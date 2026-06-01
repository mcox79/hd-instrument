"""Generic atomic launch+bootstrap+experiment+terminate for Lambda.

Same shape as launch_v1_canary.py but takes the experiment script + anchor
folder as args instead of hard-coding V1. Used for the cheap-Lambda batch:

  python tools/cloud/launch_experiment.py \\
    --anchor path_d_24n_32n_envelope_v1_n4096 \\
    --script experiments/exp_path_d_24n_32n_envelope_v1_n4096.py \\
    --ssh-key-name lambda_canary \\
    --ssh-key-path C:/Users/marsh/.ssh/lambda_canary.pem \\
    --max-cost-usd 1.50

All 3 safety layers active:
  1. terminate retry-with-backoff + leak flag
  2. always-verbose remote dispatch + always-SCP remote log
  3. pre-launch snapshot + 5xx retry + orphan reconcile

Does NOT evaluate the experiment's verdict (each experiment has its own
metrics schema). Caller examines SCPed metrics.json + remote log and files
the appropriate routing file for orchestrator.

Exit codes:
  0  experiment ran to completion (V1_EXIT=0); metrics.json SCPed back
  1  fatal error pre-experiment (launch / ssh / bootstrap / scp)
  2  experiment ran with non-zero exit code
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


_TERMINATE_STATE: dict = {"client": None, "instance_ids": [], "done": False}
_PROGRESS_POLL_INTERVAL_S = 30
_DEFAULT_CELL_REGEX = (
    r"^\s+(?:M=\d+\s+d=\d+\s+)?seed=\d+\s+(?:ok=|acc=|FAILED:)"
)


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


def _force_terminate():
    """Layer 1 safety: terminate retry with exp backoff + leak flag."""
    if _TERMINATE_STATE["done"] or not _TERMINATE_STATE["client"]:
        return
    if not _TERMINATE_STATE["instance_ids"]:
        _TERMINATE_STATE["done"] = True
        return
    ids = list(_TERMINATE_STATE["instance_ids"])
    backoff = 1.0
    last_exc = None
    for attempt in range(6):
        try:
            terminated = _TERMINATE_STATE["client"].terminate_instances(ids)
            print(f"[launch_experiment] cleanup attempt {attempt+1}: terminated {terminated}",
                  flush=True)
            _TERMINATE_STATE["done"] = True
            return
        except Exception as exc:
            last_exc = exc
            print(f"[launch_experiment] cleanup attempt {attempt+1} failed: {exc}",
                  flush=True)
            if attempt < 5:
                print(f"  retrying in {backoff:.0f}s...", flush=True)
                try:
                    time.sleep(backoff)
                except Exception:
                    pass
                backoff *= 2
    print(f"[launch_experiment] CLEANUP EXHAUSTED RETRIES: {last_exc}", flush=True)
    print(f"  Instance ids: {ids}; MANUALLY TERMINATE", flush=True)
    try:
        flag = _REPO_ROOT / "data" / f"lambda_LEAKED_instance_{ids[0]}.flag"
        flag.parent.mkdir(parents=True, exist_ok=True)
        flag.write_text(
            json.dumps({"instance_ids": ids,
                        "leaked_at": datetime.now(timezone.utc).isoformat(),
                        "last_error": str(last_exc)}, indent=2),
            encoding="utf-8")
        print(f"  leak flag: {flag}", flush=True)
    except Exception:
        pass
    _TERMINATE_STATE["done"] = True


def _signal_handler(signum, frame):
    print(f"[launch_experiment] signal {signum}; cleanup", flush=True)
    _force_terminate()
    sys.exit(130)


def _ssh_run(ip: str, key: str | None, cmd: str, timeout_s: float) -> tuple[int, str, str]:
    base = [
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "ConnectTimeout=15",
        "-o", "LogLevel=ERROR",
    ]
    if key:
        base.extend(["-i", key])
    base.append(f"ubuntu@{ip}")
    base.append(cmd)
    try:
        proc = subprocess.run(
            base, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout_s,
        )
        return (proc.returncode, proc.stdout or "", proc.stderr or "")
    except subprocess.TimeoutExpired:
        return (-1, "", f"timeout {timeout_s}s")
    except Exception as exc:
        return (-1, "", str(exc))


def _scp_from(ip: str, key: str | None, remote: str, local: Path) -> bool:
    base = [
        "scp",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "ConnectTimeout=30",
    ]
    if key:
        base.extend(["-i", key])
    base.append(f"ubuntu@{ip}:{remote}")
    base.append(str(local))
    try:
        proc = subprocess.run(base, capture_output=True, text=True, timeout=120)
        return proc.returncode == 0
    except Exception:
        return False


class ProgressPoller(threading.Thread):
    """Background SCP-poller for the remote progress.json.

    Pulls ~/hd-instrument/data/exp_<anchor>/progress.json every
    poll_interval_s, mirrors it to data/lambda_progress_<anchor>_<id>.json,
    and prints a one-line live status (cell N/M, percent, ETA).

    Stops cleanly when stop_event is set OR the main thread exits.
    """

    def __init__(
        self,
        ip: str,
        ssh_key_path: str | None,
        instance_id: str,
        anchor: str,
        stop_event: threading.Event,
        poll_interval_s: int = _PROGRESS_POLL_INTERVAL_S,
    ):
        super().__init__(daemon=True, name=f"progress-poller-{anchor}")
        self.ip = ip
        self.ssh_key_path = ssh_key_path
        self.instance_id = instance_id
        self.anchor = anchor
        self.stop_event = stop_event
        self.poll_interval_s = poll_interval_s
        self.remote_path = f"~/hd-instrument/data/exp_{anchor}/progress.json"
        self.local_path = (
            _REPO_ROOT / "data" / f"lambda_progress_{anchor}_{instance_id}.json"
        )
        self._last_cell: int | None = None

    def run(self) -> None:
        if self.stop_event.wait(timeout=10):
            return
        while not self.stop_event.is_set():
            try:
                self._poll_once()
            except Exception as exc:
                print(f"[progress-poller] error (continuing): {exc}", flush=True)
            if self.stop_event.wait(timeout=self.poll_interval_s):
                break

    def _poll_once(self) -> None:
        tmp = self.local_path.with_suffix(self.local_path.suffix + ".tmp")
        ok = _scp_from(self.ip, self.ssh_key_path, self.remote_path, tmp)
        if not ok or not tmp.is_file():
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
        if cell == self._last_cell:
            return
        self._last_cell = int(cell)
        pct = (cell / total * 100) if total else 0
        eta_str = f"ETA {eta}s" if eta is not None else "ETA -"
        ts = datetime.now().astimezone().strftime("%H:%M:%S")
        print(f"[progress {ts}] {self.anchor} cell {cell}/{total}  "
              f"({pct:.1f}%)  {phase}  {eta_str}", flush=True)


def main() -> int:
    # Line-buffer stdout so launcher prints flush per line even when the
    # parent harness captures stdout to a file (Python defaults to fully
    # buffered in that case, so progress prints stay hidden until exit).
    try:
        sys.stdout.reconfigure(line_buffering=True)
        sys.stderr.reconfigure(line_buffering=True)
    except (AttributeError, OSError):
        pass

    parser = argparse.ArgumentParser(description="Generic Lambda experiment launcher")
    parser.add_argument("--anchor", required=True,
                        help="Experiment anchor name (folder under data/exp_X)")
    parser.add_argument("--script", required=True,
                        help="Path to experiment script (relative to repo root)")
    parser.add_argument("--ssh-key-name", required=True)
    parser.add_argument("--ssh-key-path", required=True)
    parser.add_argument("--key-file", default=".env.lambda")
    parser.add_argument("--instance-type", default=None)
    parser.add_argument("--region", default=None)
    parser.add_argument("--max-cost-usd", type=float, default=2.0)
    parser.add_argument("--expected-wall-min", type=float, default=45.0)
    parser.add_argument("--budget-cap-usd", type=float, default=50.0)
    parser.add_argument("--repo-url",
                        default="https://github.com/mcox79/hd-instrument.git")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--experiment-timeout-min", type=float, default=60.0)
    parser.add_argument("--total-cells", type=int, default=0,
                        help="Expected cell-completion lines (>0 enables "
                             "ProgressPoller; 0 disables progress tracking)")
    parser.add_argument("--cell-regex", default=_DEFAULT_CELL_REGEX,
                        help="Regex matching one cell-completion stdout "
                             "line; default fits substrate experiments")
    parser.add_argument("--wait-for-capacity-max-s", type=float, default=3600.0,
                        help="Max time to poll catalog for capacity before "
                             "launching (zero billable cost; default 3600s)")
    parser.add_argument("--capacity-poll-interval-s", type=float, default=30.0)
    parser.add_argument("--stuck-booting-max-s", type=float, default=300.0,
                        help="Terminate fast-fail if instance status stays "
                             "booting > this many seconds; caps wasted boot "
                             "billing. Default 300s.")
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

    # Catalog + target
    try:
        catalog = client.list_instance_types()
    except LambdaClientError as exc:
        print(f"[ERROR] catalog: {exc}")
        return 1
    with_cap = [t for t in catalog if t.regions_available]
    if not with_cap:
        print("[ERROR] no capacity")
        return 1
    with_cap.sort(key=lambda t: t.price_cents_per_hour)
    if args.instance_type:
        target = next((t for t in with_cap if t.name == args.instance_type), None)
        if not target:
            print(f"[ERROR] {args.instance_type} no capacity")
            return 1
    else:
        target = with_cap[0]
    predicted = target.hourly_rate_usd * (args.expected_wall_min / 60.0)

    print("=" * 70)
    print(f"Experiment launcher: {args.anchor}")
    print("=" * 70)
    print(f"  Script:              {args.script}")
    print(f"  Instance type:       {target.name}")
    print(f"  Region preference:   {args.region or 'ANY (first available)'}")
    print(f"  Rate:                ${target.hourly_rate_usd:.2f}/hr")
    print(f"  Expected wall:       {args.expected_wall_min:.1f} min")
    print(f"  PREDICTED COST:      ${predicted:.2f}")
    print(f"  Max-cost cap:        ${args.max_cost_usd:.2f}")
    if predicted > args.max_cost_usd:
        print(f"\n[REFUSE] ${predicted:.2f} > cap ${args.max_cost_usd:.2f}")
        return 1

    atexit.register(_force_terminate)
    try:
        signal.signal(signal.SIGTERM, _signal_handler)
        signal.signal(signal.SIGINT, _signal_handler)
    except (AttributeError, ValueError):
        pass

    # Pre-flight capacity gate: returns FRESH available_regions list at the
    # moment capacity was seen; we use the first one for launch so no stale-
    # region-cache risk.
    print(f"\n[0/4] Verifying capacity for {target.name} "
          f"(region preference={args.region or 'ANY'}; "
          f"max wait {args.wait_for_capacity_max_s:.0f}s; zero billable cost)...")
    try:
        available_regions = client.wait_for_capacity(
            instance_type_name=target.name,
            regions=[args.region] if args.region else None,
            max_wait_s=args.wait_for_capacity_max_s,
            poll_interval_s=args.capacity_poll_interval_s,
            verbose=True,
        )
    except LambdaClientError as exc:
        print(f"[ERROR] capacity gate: {exc}")
        return 1
    region = available_regions[0]
    print(f"  Selected region for launch: {region}")

    # Launch (layer 3 safety: snapshot + 5xx retry + reconcile)
    print(f"\n[1/4] Launching {target.name} in {region}...")
    launch_ts = datetime.now(timezone.utc)

    def _snapshot() -> set[str]:
        try:
            return {i.instance_id for i in client.list_instances()
                    if i.status in ("active", "booting", "terminating", "unhealthy")}
        except Exception:
            return set()

    pre_ids = _snapshot()
    print(f"  pre-launch active on account: {len(pre_ids)}")
    new_ids: list[str] = []
    last_exc = None
    backoff = 2.0
    for attempt in range(3):
        try:
            new_ids = client.launch_instance(
                region_name=region,
                instance_type_name=target.name,
                ssh_key_names=[args.ssh_key_name],
                quantity=1,
                name=f"exp-{args.anchor[:32]}",
            )
            if new_ids:
                break
        except LambdaClientError as exc:
            last_exc = exc
            transient = any(c in str(exc) for c in (" 502 ", " 503 ", " 504 "))
            print(f"  attempt {attempt+1} failed: {exc}")
            if not transient:
                break
            if attempt < 2:
                print(f"  transient 5xx; retry in {backoff:.0f}s...")
                time.sleep(backoff)
                backoff *= 2
    time.sleep(5)
    post_ids = _snapshot()
    orphan_ids = sorted(post_ids - pre_ids - set(new_ids))
    all_ours = list(set(new_ids) | set(orphan_ids))
    if orphan_ids:
        print(f"  reconciled {len(orphan_ids)} orphan(s): {orphan_ids}")
    if not all_ours:
        print(f"[ERROR] no instance (last_error={last_exc!r})")
        return 1
    _TERMINATE_STATE["instance_ids"] = all_ours
    instance_id = new_ids[0] if new_ids else orphan_ids[0]
    print(f"  launched: {instance_id} (tracked: {len(all_ours)})")

    # Wait active (with stuck-booting fast-fail per args.stuck_booting_max_s)
    print(f"[2/4] Waiting for active (stuck-booting fast-fail at "
          f"{args.stuck_booting_max_s:.0f}s)...")
    try:
        inst = client.wait_for_active(instance_id, timeout_s=args.stuck_booting_max_s)
    except LambdaClientError as exc:
        print(f"[ERROR] {exc}")
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

    # Bootstrap (via existing bootstrap_instance.py subprocess)
    print(f"\n[3/4] Bootstrapping {instance_id}...")
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
            print(f"---- bootstrap stderr ----\n{result.stderr[-1500:]}",
                  file=sys.stderr)
        boot_ok = (result.returncode == 0)
        print(f"  bootstrap rc: {result.returncode}")
    except Exception as exc:
        print(f"  [ERROR] bootstrap: {exc}")
        boot_ok = False
    if not boot_ok:
        print(f"\n[ERROR] bootstrap failed; aborting")
        return 1

    # Dispatch experiment (layer 2 safety: verbose tracing + tee remote log)
    print(f"\n[4/4] Dispatching experiment ({args.experiment_timeout_min:.0f}m timeout)...")
    remote_anchor_dir = f"data/exp_{args.anchor}"
    progress_enabled = args.total_cells > 0
    if progress_enabled:
        # Wrap target script in generic_progress_wrapper for per-cell ETA emission.
        # Escape single quotes in regex by using a heredoc-friendly shell pattern.
        regex_escaped = args.cell_regex.replace("'", "'\\''")
        target_cmd = (
            f"$PY -u tools/cloud/generic_progress_wrapper.py "
            f"--anchor {args.anchor} "
            f"--script {args.script} "
            f"--total-cells {args.total_cells} "
            f"--cell-regex '{regex_escaped}'"
        )
        print(f"  progress tracking ON (total_cells={args.total_cells})")
    else:
        target_cmd = f"$PY -u {args.script}"
        print(f"  progress tracking OFF (--total-cells=0)")
    exp_cmd = (
        "set -e; "
        "cd ~/hd-instrument; "
        "PY=$(if [ -x .venv/bin/python ]; then echo .venv/bin/python; else echo python3; fi); "
        f"REMOTE_OUT={remote_anchor_dir}; "
        f"REMOTE_LOG=$REMOTE_OUT/exp_run.log; "
        f"mkdir -p $REMOTE_OUT; "
        "echo '--- env ---'; "
        "$PY --version; "
        "$PY -c 'import torch, numpy; print(\"torch:\", torch.__version__, \"cuda:\", torch.cuda.is_available(), \"numpy:\", numpy.__version__)' || true; "
        "free -h | head -2; df -h / | tail -1; "
        "echo '--- dispatch ---'; "
        "set -x; "
        f"(stdbuf -oL {target_cmd} 2>&1 | tee $REMOTE_LOG; "
        f"  echo \"EXP_EXIT=${{PIPESTATUS[0]}}\") || echo 'EXP_DISPATCH_FAIL'; "
        "set +x; "
        "echo '--- result ---'; "
        f"if [ -f $REMOTE_OUT/metrics.json ]; then echo 'METRICS_OK'; ls -la $REMOTE_OUT/metrics.json; "
        f"else echo 'NO_METRICS'; tail -100 $REMOTE_LOG || true; fi"
    )

    # Spawn ProgressPoller BEFORE the blocking SSH dispatch so live cell
    # updates print to stdout while the experiment runs. Stops on _ssh_run
    # return or signal.
    progress_stop = threading.Event()
    progress_poller: ProgressPoller | None = None
    if progress_enabled:
        progress_poller = ProgressPoller(
            ip=ip, ssh_key_path=args.ssh_key_path,
            instance_id=instance_id, anchor=args.anchor,
            stop_event=progress_stop,
        )
        progress_poller.start()

    try:
        rc, out, err = _ssh_run(ip, args.ssh_key_path, exp_cmd,
                                 timeout_s=int(args.experiment_timeout_min * 60))
    finally:
        if progress_poller is not None:
            progress_stop.set()
            progress_poller.join(timeout=5)
    print("---- experiment stdout tail ----")
    print(out[-4000:])
    if err:
        print(f"---- experiment stderr ----\n{err[-1500:]}")
    print(f"---- exit: {rc} ----")
    log_path = _REPO_ROOT / "data" / f"lambda_exp_{args.anchor}_{instance_id}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(out + "\n[stderr]\n" + err, encoding="utf-8")
    print(f"  local log: {log_path}")

    # SCP results (metrics.json + remote log) regardless of rc
    metrics_local = _REPO_ROOT / "data" / f"lambda_exp_{args.anchor}_metrics_{instance_id}.json"
    if _scp_from(ip, args.ssh_key_path,
                 f"~/hd-instrument/{remote_anchor_dir}/metrics.json",
                 metrics_local):
        print(f"  metrics: {metrics_local}")
    else:
        print(f"  [WARN] no metrics.json on remote")
    remote_log_local = _REPO_ROOT / "data" / f"lambda_exp_{args.anchor}_remote_log_{instance_id}.log"
    if _scp_from(ip, args.ssh_key_path,
                 f"~/hd-instrument/{remote_anchor_dir}/exp_run.log",
                 remote_log_local):
        print(f"  remote log: {remote_log_local}")
    progress_local = _REPO_ROOT / "data" / f"lambda_exp_{args.anchor}_progress_final_{instance_id}.json"
    if progress_enabled and _scp_from(
            ip, args.ssh_key_path,
            f"~/hd-instrument/{remote_anchor_dir}/progress.json",
            progress_local):
        print(f"  progress (final): {progress_local}")

    # Terminate (layer 1 safety: retry+leak flag via _force_terminate)
    print(f"\n[terminate]")
    _force_terminate()
    terminate_ts = datetime.now(timezone.utc)
    actual_wall_s = (terminate_ts - launch_ts).total_seconds()
    actual_cost = inst.hourly_rate_usd * (actual_wall_s / 3600.0)
    print()
    print("=" * 70)
    print(f"Experiment report: {args.anchor}")
    print("=" * 70)
    print(f"  Predicted:     ${predicted:.2f}  ({args.expected_wall_min:.1f} min)")
    print(f"  Actual wall:   {actual_wall_s/60:.1f} min")
    print(f"  Actual cost:   ${actual_cost:.2f}")
    if predicted > 0:
        rel = (actual_cost - predicted) / predicted * 100
        print(f"  Delta:         ${actual_cost - predicted:+.2f}  ({rel:+.1f}%)")
    print(f"  Experiment rc: {rc}")
    print(f"  Metrics:       {metrics_local if metrics_local.is_file() else 'NOT PRODUCED'}")

    update_cost(current_hourly_rate_usd=0.0, active_instances=[])
    new_total = accumulate_run_cost(actual_cost)
    print(f"  Cumulative today: ${new_total:.2f}")

    report = {
        "anchor": args.anchor,
        "script": args.script,
        "instance_id": instance_id,
        "instance_type": target.name,
        "hourly_rate_usd": inst.hourly_rate_usd,
        "wall_min": round(actual_wall_s / 60, 1),
        "actual_cost_usd": round(actual_cost, 2),
        "experiment_rc": rc,
        "launched_at": launch_ts.isoformat(),
        "terminated_at": terminate_ts.isoformat(),
        "metrics_path": str(metrics_local) if metrics_local.is_file() else None,
        "remote_log_path": str(remote_log_local) if remote_log_local.is_file() else None,
        "local_log_path": str(log_path),
    }
    rp = _REPO_ROOT / "data" / f"lambda_exp_{args.anchor}_report_{instance_id}.json"
    rp.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"  Report:        {rp}")
    return 0 if rc == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
