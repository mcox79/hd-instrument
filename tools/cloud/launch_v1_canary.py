"""Launch + bootstrap + V1 + verify HARD_PASS + terminate (one-shot atomic).

Single atomic experiment for the Tier 1b validation gate:

  1. Launch a fresh A10 (or specified instance type)
  2. Wait for active + SSH-reachable
  3. Bootstrap the instance (apt + clone + venv + pip install)
  4. Run V1 PIPELINE VALIDATION script over SSH:
       exp_modern_hopfield_pipeline_validation_v1_n2048_n4096.py
  5. SCP the resulting metrics.json back to local
  6. Inspect the local copy: HARD_PASS verdict + non-null metrics +
     audit-cert validity per the V1 pre-registration
  7. TERMINATE the instance in try-finally + atexit + signal handlers

This is THE validation gate per the kickoff doc + session_architecture_v1.
A green run means Tier 2 work can confidently use Lambda for real
experiments.

Note: there is no local-vs-cloud numerical comparison in this version
because we don't have a clean local HARD_PASS reference for V1 on this
checkout. Instead we use the V1 script's OWN pre-registered HARD_PASS
criteria (n_crashed_total == 0, n_non_null_total == 39, cert_all_valid
True). If a numerical reference becomes available later, the comparison
logic from tools/cloud/v1_reproducer_canary.py can be folded back in.

Usage:
  python tools/cloud/launch_v1_canary.py \\
    --ssh-key-name lambda_canary \\
    --ssh-key-path C:/Users/marsh/.ssh/lambda_canary.pem \\
    [--instance-type gpu_1x_a10] \\
    [--max-cost-usd 2.00] \\
    [--expected-wall-min 40]

Exit codes:
  0  V1 ran + HARD_PASS criteria met
  1  fatal error (launch, ssh, scp, etc.)
  2  V1 ran but HARD_PASS criteria NOT met (instrumentation issue)
"""

from __future__ import annotations

import argparse
import atexit
import json
import os
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.cloud.lambda_client import LambdaClient, LambdaClientError  # noqa: E402
from tools.cloud.cost_tracker import update_cost, accumulate_run_cost  # noqa: E402


_V1_ANCHOR = "modern_hopfield_pipeline_validation_v1_n2048_n4096"
_V1_SCRIPT = f"experiments/exp_{_V1_ANCHOR}.py"
_V1_WRAPPER = "tools/cloud/v1_progress_wrapper.py"
_REMOTE_METRICS_PATH = f"data/exp_{_V1_ANCHOR}/metrics.json"
_REMOTE_PROGRESS_PATH = f"data/exp_{_V1_ANCHOR}/progress.json"
_PROGRESS_POLL_INTERVAL_S = 30


def _load_key(key_file_arg: str) -> str | None:
    key = os.environ.get("LAMBDA_CLOUD_API_KEY", "").strip()
    if key:
        return key
    kp = Path(key_file_arg)
    if not kp.is_absolute():
        kp = _REPO_ROOT / kp
    if not kp.is_file():
        return None
    for ln in kp.read_text(encoding="utf-8").splitlines():
        if ln.startswith("LAMBDA_CLOUD_API_KEY="):
            v = ln.split("=", 1)[1].strip().strip('"').strip("'")
            return v
    return None


_TERMINATE_STATE: dict = {"client": None, "instance_ids": [], "done": False}


def _force_terminate():
    """Idempotent terminate with retry. Tolerates transient network failures.

    Cleanup MUST succeed even if local DNS / network blips at the wrong
    moment (we observed [Errno 11001] getaddrinfo failed on a real run,
    which leaked an instance until manual cleanup). Retry up to 6 times
    with exponential backoff (1s, 2s, 4s, 8s, 16s, 32s = ~63s total).

    If all retries fail the function writes a sticky file at
    data/lambda_LEAKED_instance_<id>.flag so the dashboard / next session
    sees the leak and can manually clean up.
    """
    if _TERMINATE_STATE["done"] or not _TERMINATE_STATE["client"]:
        return
    if not _TERMINATE_STATE["instance_ids"]:
        _TERMINATE_STATE["done"] = True
        return
    instance_ids = list(_TERMINATE_STATE["instance_ids"])
    backoff = 1.0
    last_exc: Exception | None = None
    for attempt in range(6):
        try:
            terminated = _TERMINATE_STATE["client"].terminate_instances(instance_ids)
            print(f"[launch_v1_canary] cleanup attempt {attempt+1}: terminated {terminated}",
                  flush=True)
            _TERMINATE_STATE["done"] = True
            return
        except Exception as exc:
            last_exc = exc
            print(f"[launch_v1_canary] cleanup attempt {attempt+1} failed: {exc}",
                  flush=True)
            if attempt < 5:
                print(f"  retrying in {backoff:.0f}s...", flush=True)
                try:
                    time.sleep(backoff)
                except Exception:
                    pass
                backoff *= 2
    # All retries exhausted -- leave a sticky flag so the leak is visible.
    print(f"[launch_v1_canary] CLEANUP EXHAUSTED RETRIES: {last_exc}", flush=True)
    print(f"  Instance ids: {instance_ids}", flush=True)
    print(f"  MANUALLY TERMINATE VIA LAMBDA WEB CONSOLE", flush=True)
    try:
        flag = _REPO_ROOT / "data" / f"lambda_LEAKED_instance_{instance_ids[0]}.flag"
        flag.parent.mkdir(parents=True, exist_ok=True)
        flag.write_text(
            json.dumps({
                "instance_ids": instance_ids,
                "leaked_at": datetime.now(timezone.utc).isoformat(),
                "last_error": str(last_exc),
            }, indent=2),
            encoding="utf-8",
        )
        print(f"  leak flag written: {flag}", flush=True)
    except Exception as exc2:
        print(f"  could not write leak flag: {exc2}", flush=True)
    _TERMINATE_STATE["done"] = True


def _signal_handler(signum, frame):
    print(f"[launch_v1_canary] signal {signum}; cleaning up", flush=True)
    _force_terminate()
    sys.exit(130)


def _ssh_run(
    ip: str,
    ssh_key_path: str | None,
    command: str,
    timeout_s: float = 60.0,
) -> tuple[int, str, str]:
    cmd = [
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "ConnectTimeout=15",
        "-o", "LogLevel=ERROR",
    ]
    if ssh_key_path:
        cmd.extend(["-i", ssh_key_path])
    cmd.append(f"ubuntu@{ip}")
    cmd.append(command)
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            timeout=timeout_s,
        )
        return (proc.returncode, proc.stdout or "", proc.stderr or "")
    except subprocess.TimeoutExpired:
        return (-1, "", f"ssh timeout after {timeout_s}s")
    except Exception as exc:
        return (-1, "", f"ssh error: {exc}")


class ProgressPoller(threading.Thread):
    """Background SCP-poller for the remote progress.json.

    Pulls ~/hd-instrument/data/exp_<anchor>/progress.json every
    poll_interval_s, mirrors it to data/lambda_progress_<id>.json, and
    prints a one-line live status (cell N/M, percent, ETA).

    Stops cleanly when stop_event is set OR the main thread exits.
    """

    def __init__(
        self,
        ip: str,
        ssh_key_path: str | None,
        instance_id: str,
        stop_event: threading.Event,
        poll_interval_s: int = _PROGRESS_POLL_INTERVAL_S,
    ):
        super().__init__(daemon=True, name="progress-poller")
        self.ip = ip
        self.ssh_key_path = ssh_key_path
        self.instance_id = instance_id
        self.stop_event = stop_event
        self.poll_interval_s = poll_interval_s
        self.local_path = (
            _REPO_ROOT / "data" / f"lambda_progress_{instance_id}.json"
        )
        self._last_cell: int | None = None

    def run(self) -> None:
        # Small initial delay so the wrapper has time to write the first
        # progress.json before we poll.
        if self.stop_event.wait(timeout=10):
            return
        while not self.stop_event.is_set():
            try:
                self._poll_once()
            except Exception as exc:
                # Poller must NEVER take down the main run.
                print(f"[progress-poller] error (continuing): {exc}", flush=True)
            if self.stop_event.wait(timeout=self.poll_interval_s):
                break

    def _poll_once(self) -> None:
        # Use a tempfile so a partial SCP write never corrupts the local
        # path we keep around as the canonical view.
        tmp = self.local_path.with_suffix(self.local_path.suffix + ".tmp")
        ok = _scp_from(
            self.ip,
            self.ssh_key_path,
            f"~/hd-instrument/{_REMOTE_PROGRESS_PATH}",
            tmp,
        )
        if not ok or not tmp.is_file():
            # Progress file might not exist yet (V1 hasn't printed first cell).
            return
        try:
            entry = json.loads(tmp.read_text(encoding="utf-8"))
        except Exception:
            tmp.unlink(missing_ok=True)
            return
        os.replace(str(tmp), str(self.local_path))
        cell = entry.get("cell")
        total = entry.get("total_cells")
        phase = entry.get("phase") or ""
        eta = entry.get("eta_sec")
        if cell is None or total is None:
            return
        # Only print when the cell count moves (no noisy duplicates).
        if cell == self._last_cell:
            return
        self._last_cell = int(cell)
        pct = (cell / total * 100) if total else 0
        eta_str = f"ETA {eta}s" if eta is not None else "ETA -"
        ts = datetime.now().astimezone().strftime("%H:%M:%S")
        print(f"[progress {ts}] cell {cell}/{total}  ({pct:.1f}%)  "
              f"{phase}  {eta_str}",
              flush=True)


def _scp_from(
    ip: str,
    ssh_key_path: str | None,
    remote_path: str,
    local_path: Path,
) -> bool:
    cmd = [
        "scp",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "ConnectTimeout=30",
    ]
    if ssh_key_path:
        cmd.extend(["-i", ssh_key_path])
    cmd.append(f"ubuntu@{ip}:{remote_path}")
    cmd.append(str(local_path))
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return proc.returncode == 0
    except Exception:
        return False


def _evaluate_v1_metrics(metrics: dict) -> tuple[bool, str, dict]:
    """Apply V1's pre-registered HARD_PASS criteria to a metrics dict.

    V1's actual metrics.json schema (confirmed from a real run):
      {
        "elapsed_s": float,
        "summary":   {...per-cell aggregates...},
        "verdict":   "PIPELINE_HARD_PASS" | "PIPELINE_HARD_FAIL" | "PIPELINE_MIDDLE_BAND",
        "verdict_msg": "PIPELINE_VALID: n_total=39 n_success=39 n_non_null=39
                        n_crashed=0 Ns=[2048, 4096] per_N={...}
                        cert_all_valid=True -- cloud-ready at N=[...]"
      }

    Earlier versions of this function looked for `verdict_label` and
    `n_*_total` at top level; neither exists. The verdict label IS at
    `verdict` and the counts are inline in `verdict_msg`. Parse both.
    """
    import re as _re
    summary: dict = {}
    label = (metrics.get("verdict") or metrics.get("verdict_label") or "").upper()
    msg = metrics.get("verdict_msg") or ""
    summary["verdict_label"] = label
    summary["verdict_msg"] = msg

    # Extract per-cell counts from verdict_msg.
    def _grab(field: str) -> int | None:
        m = _re.search(rf"{field}=(\d+)", msg)
        return int(m.group(1)) if m else None

    n_total = _grab("n_total")
    n_success = _grab("n_success")
    n_non_null = _grab("n_non_null") or n_success
    n_crashed = _grab("n_crashed")
    if n_crashed is None and n_total is not None and n_success is not None:
        n_crashed = n_total - n_success
    summary["n_total"] = n_total
    summary["n_success"] = n_success
    summary["n_non_null"] = n_non_null
    summary["n_crashed"] = n_crashed

    cert_match = _re.search(r"cert_all_valid=(\w+)", msg)
    cert_all_valid = None
    if cert_match:
        cert_all_valid = cert_match.group(1).lower() == "true"
    summary["cert_all_valid"] = cert_all_valid

    if "PIPELINE_HARD_PASS" in label or "HARD_PASS" in label:
        return True, f"verdict={label}", summary
    if (n_crashed == 0 and n_non_null is not None and n_total is not None
            and n_non_null == n_total and cert_all_valid is True):
        return True, "per-cell: 0 crashed + all non-null + certs valid", summary
    if n_crashed is not None and n_crashed > 0:
        return False, f"FAIL: {n_crashed} cells crashed", summary
    if n_total is not None and n_non_null is not None and n_non_null < n_total:
        return False, f"FAIL: {n_total - n_non_null}/{n_total} cells null", summary
    return False, "unable to determine pass/fail from metrics", summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Launch + bootstrap + V1 + terminate")
    parser.add_argument("--ssh-key-name", required=True)
    parser.add_argument("--ssh-key-path", required=True)
    parser.add_argument("--key-file", default=".env.lambda")
    parser.add_argument("--instance-type", default=None)
    parser.add_argument("--region", default=None)
    parser.add_argument("--max-cost-usd", type=float, default=2.0)
    parser.add_argument("--expected-wall-min", type=float, default=40.0,
                        help="Boot + bootstrap + V1 + scp + terminate")
    parser.add_argument("--budget-cap-usd", type=float, default=50.0)
    parser.add_argument("--repo-url",
                        default="https://github.com/mcox79/hd-instrument.git")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--v1-timeout-min", type=float, default=45.0,
                        help="SSH command timeout for the V1 dispatch")
    args = parser.parse_args()

    api_key = _load_key(args.key_file)
    if not api_key:
        print("[ERROR] no LAMBDA_CLOUD_API_KEY")
        return 1
    try:
        client = LambdaClient(api_key=api_key)
    except LambdaClientError as exc:
        print(f"[ERROR] {exc}")
        return 1
    _TERMINATE_STATE["client"] = client

    # Catalog + pick target.
    try:
        catalog = client.list_instance_types()
    except LambdaClientError as exc:
        print(f"[ERROR] catalog: {exc}")
        return 1
    with_capacity = [t for t in catalog if t.regions_available]
    if not with_capacity:
        print("[ERROR] no capacity")
        return 1
    with_capacity.sort(key=lambda t: t.price_cents_per_hour)
    if args.instance_type:
        target = next((t for t in with_capacity if t.name == args.instance_type), None)
        if not target:
            print(f"[ERROR] requested {args.instance_type} has no capacity")
            return 1
    else:
        target = with_capacity[0]
    region = args.region or target.regions_available[0]

    predicted = target.hourly_rate_usd * (args.expected_wall_min / 60.0)
    print("=" * 70)
    print("V1 reproducer canary plan")
    print("=" * 70)
    print(f"  Instance type:       {target.name}")
    print(f"  Region:              {region}")
    print(f"  Rate:                ${target.hourly_rate_usd:.2f}/hr")
    print(f"  Expected wall:       {args.expected_wall_min:.1f} min")
    print(f"  PREDICTED COST:      ${predicted:.2f}")
    print(f"  Max-cost cap:        ${args.max_cost_usd:.2f}")
    if predicted > args.max_cost_usd:
        print(f"\n[REFUSE] predicted ${predicted:.2f} > cap ${args.max_cost_usd:.2f}")
        return 1

    atexit.register(_force_terminate)
    try:
        signal.signal(signal.SIGTERM, _signal_handler)
        signal.signal(signal.SIGINT, _signal_handler)
    except (AttributeError, ValueError):
        pass

    # --- Launch (with pre-launch snapshot + 5xx retry + orphan detection) ---
    # A 502/503/504 from Lambda's API does NOT mean the launch failed --
    # the instance may have spun up but the reply got lost. Without a
    # pre-launch snapshot we'd orphan the instance because we never learn
    # its id. Pattern:
    #   1. snapshot active ids
    #   2. retry launch on 5xx
    #   3. reconcile: any new active id since snapshot is "ours" and gets
    #      registered for termination, even if the API never told us
    print(f"\n[1/5] Launching {target.name} in {region}...")
    launch_ts = datetime.now(timezone.utc)

    def _snapshot_active_ids() -> set[str]:
        try:
            return {
                i.instance_id for i in client.list_instances()
                if i.status in ("active", "booting", "terminating", "unhealthy")
            }
        except Exception:
            return set()

    pre_launch_ids = _snapshot_active_ids()
    print(f"  pre-launch active instances on account: {len(pre_launch_ids)}")

    new_ids: list[str] = []
    last_exc: Exception | None = None
    backoff = 2.0
    for attempt in range(3):
        try:
            new_ids = client.launch_instance(
                region_name=region,
                instance_type_name=target.name,
                ssh_key_names=[args.ssh_key_name],
                quantity=1,
                name="v1-reproducer-canary",
            )
            if new_ids:
                break
        except LambdaClientError as exc:
            last_exc = exc
            msg = str(exc)
            transient = any(c in msg for c in (" 502 ", " 503 ", " 504 "))
            print(f"  launch attempt {attempt+1} failed: {exc}")
            if not transient:
                # Non-transient (auth, validation, etc.): don't retry but
                # still reconcile in case Lambda created something.
                break
            if attempt < 2:
                print(f"  transient 5xx; retrying in {backoff:.0f}s...")
                time.sleep(backoff)
                backoff *= 2

    # Reconcile: did Lambda actually create instance(s) regardless of what
    # the API replied? Wait a moment for state to propagate, then diff.
    time.sleep(5)
    post_launch_ids = _snapshot_active_ids()
    orphan_ids = sorted(post_launch_ids - pre_launch_ids - set(new_ids))
    all_ours = list(set(new_ids) | set(orphan_ids))
    if orphan_ids:
        print(f"  reconciliation detected {len(orphan_ids)} orphan(s) from failed/incomplete "
              f"launches: {orphan_ids}; registering for cleanup")

    if not all_ours:
        # Nothing recorded AND nothing orphaned -> hard fail.
        print(f"[ERROR] launch produced no instance "
              f"(last_error={last_exc!r})")
        return 1

    _TERMINATE_STATE["instance_ids"] = all_ours
    # Pick the canonical "our" instance (prefer API-reported new_id; fall
    # back to orphan if launch never reported).
    instance_id = new_ids[0] if new_ids else orphan_ids[0]
    print(f"  launched: {instance_id}  (tracked total: {len(all_ours)})")

    # --- Wait active ---
    print(f"[2/5] Waiting for active...")
    try:
        inst = client.wait_for_active(instance_id, timeout_s=900.0)
    except LambdaClientError as exc:
        print(f"[ERROR] wait_for_active: {exc}")
        return 1
    print(f"  active: ip={inst.ip}")
    ip = inst.ip
    update_cost(
        current_hourly_rate_usd=inst.hourly_rate_usd,
        active_instances=[{
            "instance_id": instance_id,
            "instance_type": target.name,
            "hourly_rate_usd": inst.hourly_rate_usd,
            "started_at": launch_ts.isoformat(),
        }],
    )

    # --- Bootstrap ---
    print(f"\n[3/5] Bootstrapping {instance_id}...")
    boot_cmd = [
        sys.executable,
        str(_REPO_ROOT / "tools" / "cloud" / "bootstrap_instance.py"),
        instance_id,
        "--ssh-key-path", args.ssh_key_path,
        "--repo-url", args.repo_url,
        "--branch", args.branch,
    ]
    try:
        result = subprocess.run(
            boot_cmd, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            timeout=2700,
        )
        print(result.stdout)
        if result.stderr:
            print(f"---- bootstrap stderr ----\n{result.stderr[-2000:]}",
                  file=sys.stderr)
        boot_ok = (result.returncode == 0)
        print(f"  bootstrap rc: {result.returncode}")
    except Exception as exc:
        print(f"  [ERROR] bootstrap subprocess: {exc}")
        boot_ok = False
    if not boot_ok:
        print(f"\n[ERROR] bootstrap FAILED; aborting V1 dispatch")
        return 1

    # --- V1 dispatch ---
    # ALWAYS verbose, per [[feedback-always-verbose-remote-dispatch]]:
    #   - `set -e` exits on error, `set -x` traces every shell command
    #   - `python -u` + `stdbuf -oL` keep stdio line-buffered so partial
    #     lines survive an SSH 'Connection reset by peer'
    #   - tee'd remote log file is SCPed back below even if the dispatch
    #     fails (so we always have ground truth on what actually ran)
    # Start the progress poller BEFORE we kick off V1. Daemon thread polls
    # the remote progress.json every 30s, prints live "cell N/M (X%)"
    # status lines, mirrors latest snapshot to data/lambda_progress_<id>.json.
    progress_stop = threading.Event()
    poller = ProgressPoller(
        ip=ip,
        ssh_key_path=args.ssh_key_path,
        instance_id=instance_id,
        stop_event=progress_stop,
    )
    poller.start()
    print(f"  progress poller started (poll every {_PROGRESS_POLL_INTERVAL_S}s; "
          f"mirror at data/lambda_progress_{instance_id}.json)")

    print(f"\n[4/5] Dispatching V1 via SSH (timeout {args.v1_timeout_min:.0f} min)...")
    v1_cmd = (
        "set -e; "
        "cd ~/hd-instrument; "
        "PY=$(if [ -x .venv/bin/python ]; then echo .venv/bin/python; else echo python3; fi); "
        f"REMOTE_OUT=data/exp_{_V1_ANCHOR}; "
        f"REMOTE_LOG=$REMOTE_OUT/v1_run.log; "
        f"mkdir -p $REMOTE_OUT; "
        "echo '--- environment ---'; "
        "echo PY=$PY; $PY --version; "
        "$PY -c 'import sys; print(\"path[0]:\", sys.path[0])' || true; "
        "$PY -c 'import torch; print(\"torch:\", torch.__version__, \"cuda:\", torch.cuda.is_available())' || echo 'torch import fail'; "
        "$PY -c 'import numpy; print(\"numpy:\", numpy.__version__)' || echo 'numpy import fail'; "
        "free -h | head -2; "
        "df -h / | tail -1; "
        "echo '--- dispatch (set -x; tee to $REMOTE_LOG) ---'; "
        # Run V1 unbuffered + line-buffered, tee everything to the remote
        # log file. The outer `|| echo` captures the V1 exit code so the
        # surrounding `set -e` does not kill the script before we read
        # the metrics file.
        f"set -x; "
        # Dispatch via the progress-emitting wrapper instead of V1 directly.
        # Wrapper streams V1's stdout unchanged AND writes progress.json
        # next to metrics.json, which the local ProgressPoller thread SCPs
        # back every 30s.
        f"(stdbuf -oL $PY -u {_V1_WRAPPER} 2>&1 | tee $REMOTE_LOG; "
        f"  echo \"V1_EXIT=${{PIPESTATUS[0]}}\") || echo 'V1_DISPATCH_FAIL'; "
        f"set +x; "
        "echo '--- result ---'; "
        f"if [ -f $REMOTE_OUT/metrics.json ]; then "
        f"  echo 'METRICS_OK'; ls -la $REMOTE_OUT/metrics.json; "
        f"else "
        f"  echo 'NO_METRICS_PRODUCED'; "
        f"  echo '--- last 200 lines of remote log ---'; "
        f"  tail -200 $REMOTE_LOG || true; "
        f"fi"
    )
    rc, out, err = _ssh_run(
        ip, args.ssh_key_path, v1_cmd,
        timeout_s=int(args.v1_timeout_min * 60),
    )
    # V1 finished (one way or another); stop the progress poller cleanly.
    progress_stop.set()
    poller.join(timeout=5)
    print("---- v1 stdout tail ----")
    print(out[-3500:])
    if err:
        print(f"---- v1 stderr ----\n{err[-1000:]}")
    print(f"---- v1 exit: {rc} ----")
    log_path = _REPO_ROOT / "data" / f"lambda_v1_canary_{instance_id}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(out + "\n[stderr]\n" + err, encoding="utf-8")
    print(f"  saved local log: {log_path}")

    # Per [[feedback-always-verbose-remote-dispatch]], pull the REMOTE log
    # file back even on failure. This is independent of metrics.json --
    # the remote log captures whatever V1 printed before any crash, and
    # is often the only diagnostic data we get.
    remote_log_path = _REPO_ROOT / "data" / f"lambda_v1_canary_remote_log_{instance_id}.log"
    if _scp_from(
        ip, args.ssh_key_path,
        f"~/hd-instrument/data/exp_{_V1_ANCHOR}/v1_run.log",
        remote_log_path,
    ):
        print(f"  saved remote log: {remote_log_path}")
    else:
        print(f"  [WARN] could not SCP remote v1_run.log (instance may have crashed before tee)")

    metrics: dict | None = None
    v1_ok = False
    verdict_msg = "not_evaluated"
    summary: dict = {}

    if rc == 0 and "METRICS_OK" in out:
        # SCP metrics.json back.
        print(f"\n[5/5] SCPing metrics.json back...")
        local_metrics_path = _REPO_ROOT / "data" / f"lambda_v1_canary_metrics_{instance_id}.json"
        ok = _scp_from(
            ip, args.ssh_key_path,
            f"~/hd-instrument/{_REMOTE_METRICS_PATH}",
            local_metrics_path,
        )
        if not ok:
            print(f"  [WARN] SCP failed")
        else:
            print(f"  saved: {local_metrics_path}")
            try:
                metrics = json.loads(local_metrics_path.read_text(encoding="utf-8"))
            except Exception as exc:
                print(f"  [WARN] metrics parse: {exc}")

    if metrics is not None:
        v1_ok, verdict_msg, summary = _evaluate_v1_metrics(metrics)
        print(f"\n  V1 verdict: {'PASS' if v1_ok else 'FAIL'}  ({verdict_msg})")
        for k, v in summary.items():
            print(f"    {k}: {v}")
    else:
        v1_ok = False
        verdict_msg = "no metrics retrieved"
        print(f"\n[FAIL] V1 produced no metrics or SCP failed")

    # --- Terminate (atexit also fires; explicit here for clarity) ---
    print(f"\n[terminate] {instance_id}...")
    _force_terminate()
    terminate_ts = datetime.now(timezone.utc)

    actual_wall_s = (terminate_ts - launch_ts).total_seconds()
    actual_cost = inst.hourly_rate_usd * (actual_wall_s / 3600.0)
    print()
    print("=" * 70)
    print("V1 canary report")
    print("=" * 70)
    print(f"  Predicted:           ${predicted:.2f}  ({args.expected_wall_min:.1f} min)")
    print(f"  Actual wall:         {actual_wall_s/60:.1f} min")
    print(f"  Actual cost:         ${actual_cost:.2f}")
    if predicted > 0:
        rel = (actual_cost - predicted) / predicted * 100
        print(f"  Delta:               ${actual_cost - predicted:+.2f}  ({rel:+.1f}%)")
    print(f"  V1 verdict:          {'PASS' if v1_ok else 'FAIL'}  ({verdict_msg})")

    update_cost(current_hourly_rate_usd=0.0, active_instances=[])
    new_total = accumulate_run_cost(actual_cost)
    print(f"  Cumulative today: ${new_total:.2f}")

    report = {
        "instance_id": instance_id,
        "instance_type": target.name,
        "hourly_rate_usd": inst.hourly_rate_usd,
        "wall_min": round(actual_wall_s / 60, 1),
        "actual_cost_usd": round(actual_cost, 2),
        "v1_ok": v1_ok,
        "verdict_msg": verdict_msg,
        "v1_summary": summary,
        "launched_at": launch_ts.isoformat(),
        "terminated_at": terminate_ts.isoformat(),
    }
    rp = _REPO_ROOT / "data" / f"lambda_v1_canary_report_{instance_id}.json"
    rp.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\n  Report: {rp}")

    return 0 if v1_ok else 2


if __name__ == "__main__":
    sys.exit(main())
