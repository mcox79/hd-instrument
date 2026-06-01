"""Stringed Lambda batch launcher: bootstrap once, run N experiments, terminate once.

Per-launch overhead (boot + bootstrap) is ~5 min wall and ~$0.13 per
experiment with launch_experiment.py. For a 2-3 anchor batch, that's
10-15 min wall + $0.26-0.39 wasted on re-paying setup.

This script pays setup ONCE then runs every experiment in the batch on
the same instance sequentially. The first anchor's bootstrap leaves the
.venv + git clone in place; subsequent anchors just re-dispatch.

Division of labor (per session_architecture_v1):
  - orchestrator designs experiments (writes experiments/exp_*.py)
  - testbed batches them at dispatch time (this script)

Usage:
  python tools/cloud/launch_batch.py \\
    --batch path/to/batch.json \\
    --ssh-key-name lambda_canary \\
    --ssh-key-path ~/.ssh/lambda_canary.pem \\
    --max-cost-usd 2.00 \\
    --budget-cap-usd 5.00 \\
    --expected-wall-min 45

batch.json format (list of anchor dicts):
[
  {
    "anchor": "exp_anchor_name_v1_n4096",
    "script": "experiments/exp_anchor_name_v1_n4096.py",
    "total_cells": 15,
    "cell_regex": "(optional; defaults to substrate pattern)",
    "experiment_timeout_min": 60,
    "result_paths": [
      "data/testbed_pp8_week2/phi3_qformer_wiring_cuda.json",
      "data/testbed_pp8_week2/train_v1/*"
    ]
  },
  ...
]

result_paths (optional): list of remote glob patterns (relative to
~/hd-instrument/) to SCP back AFTER the experiment completes. Files are
mirrored under data/lambda_batch_results/<anchor>_<instance_id[:8]>/ on
local. Closes the NO_METRICS gap where script outputs at custom paths
were never preserved.

All 3 safety layers from launch_experiment.py:
  1. terminate retry with backoff + leak flag (single terminate at end
     OR on any signal mid-batch)
  2. always-verbose remote dispatch (set -ex + python -u + stdbuf + tee)
  3. pre-launch snapshot + 5xx retry + orphan reconcile (once)

Per-anchor: ProgressPoller spawned for each, runs while that anchor's
SSH dispatch is in flight, then stops before the next.

Exit codes:
  0  all experiments ran to completion (each rc=0)
  1  fatal error pre-batch (launch/ssh/bootstrap)
  2  one or more experiments returned non-zero rc; batch still cleanly
     terminated; per-anchor reports indicate which
"""

from __future__ import annotations

import argparse
import atexit
import json
import os
import re
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
    """Single terminate at batch end OR on signal. Retry w/ backoff + leak flag."""
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
            print(f"[launch_batch] cleanup attempt {attempt+1}: terminated {terminated}",
                  flush=True)
            _TERMINATE_STATE["done"] = True
            return
        except Exception as exc:
            last_exc = exc
            print(f"[launch_batch] cleanup attempt {attempt+1} failed: {exc}",
                  flush=True)
            if attempt < 5:
                print(f"  retrying in {backoff:.0f}s...", flush=True)
                try:
                    time.sleep(backoff)
                except Exception:
                    pass
                backoff *= 2
    print(f"[launch_batch] CLEANUP EXHAUSTED RETRIES: {last_exc}", flush=True)
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
    print(f"[launch_batch] signal {signum}; cleanup", flush=True)
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


def _scp_recursive_from(ip: str, key: str | None, remote: str, local: Path,
                        timeout_s: int = 300) -> tuple[bool, str]:
    """Recursively SCP a remote path (file or directory) to a local path.

    Returns (success, message). The local target's parent is created if needed.
    Uses scp -r for directories; plain scp for files.
    """
    local.parent.mkdir(parents=True, exist_ok=True)
    base = [
        "scp", "-r",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "ConnectTimeout=30",
    ]
    if key:
        base.extend(["-i", key])
    base.append(f"ubuntu@{ip}:{remote}")
    base.append(str(local))
    try:
        proc = subprocess.run(
            base, capture_output=True, text=True, timeout=timeout_s)
        if proc.returncode == 0:
            return True, "ok"
        return False, (proc.stderr or proc.stdout or f"rc={proc.returncode}")[:200]
    except subprocess.TimeoutExpired:
        return False, f"timeout after {timeout_s}s"
    except Exception as exc:
        return False, str(exc)[:200]


def _ssh_glob(ip: str, key: str | None, pattern: str) -> list[str]:
    """List remote paths matching `pattern` (relative to ~/hd-instrument/).

    Uses a shell-evaluated glob expansion on the remote so callers can pass
    patterns like `data/testbed_pp8_week2/*.json`. Returns absolute paths.
    """
    cmd = (
        f"cd ~/hd-instrument && "
        f"for f in {pattern}; do "
        f"  [ -e \"$f\" ] && echo \"$HOME/hd-instrument/$f\"; "
        f"done"
    )
    base = [
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "ConnectTimeout=30",
    ]
    if key:
        base.extend(["-i", key])
    base.extend([f"ubuntu@{ip}", cmd])
    try:
        proc = subprocess.run(
            base, capture_output=True, text=True, timeout=60)
        if proc.returncode != 0:
            return []
        return [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    except Exception:
        return []


def _scp_back_result_paths(
    ip: str, key: str | None, instance_id: str, anchor: str,
    result_paths: list[str], local_base: Path,
) -> list[dict[str, Any]]:
    """SCP-back a list of result patterns from the remote to local.

    `result_paths` is a list of patterns relative to ~/hd-instrument/ on the
    remote (e.g. "data/testbed_pp8_week2/phi3_qformer_wiring_cuda.json" or
    "data/testbed_pp8_week2/train_v1/*"). Glob expansion happens on the remote.

    Returns a list of per-path dicts {"pattern", "matches", "results": [...]}.
    Each result is {"remote": str, "local": str, "ok": bool, "msg": str}.
    """
    summary: list[dict[str, Any]] = []
    if not result_paths:
        return summary
    print(f"  [scp-back] declared result_paths ({len(result_paths)}):")
    for pattern in result_paths:
        remote_matches = _ssh_glob(ip, key, pattern)
        entry: dict[str, Any] = {
            "pattern": pattern,
            "matches": len(remote_matches),
            "results": [],
        }
        if not remote_matches:
            print(f"    {pattern}: no matches on remote")
            summary.append(entry)
            continue
        for remote in remote_matches:
            # Mirror the remote subpath under local_base, keyed by anchor +
            # instance_id so multiple anchors don't collide.
            # remote is absolute: /home/ubuntu/hd-instrument/data/...
            try:
                rel = remote.split("hd-instrument/", 1)[1]
            except IndexError:
                rel = Path(remote).name
            local_dest = local_base / f"{anchor}_{instance_id[:8]}" / rel
            ok, msg = _scp_recursive_from(ip, key, remote, local_dest)
            entry["results"].append({
                "remote": remote,
                "local": str(local_dest),
                "ok": ok,
                "msg": msg if not ok else "ok",
            })
            print(f"    {remote} -> {local_dest}: {'OK' if ok else 'FAIL: ' + msg}")
        summary.append(entry)
    return summary


class ProgressPoller(threading.Thread):
    """Same shape as launch_experiment's ProgressPoller; runs per anchor."""

    def __init__(self, ip, ssh_key_path, instance_id, anchor, stop_event,
                 poll_interval_s=_PROGRESS_POLL_INTERVAL_S):
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

    def run(self):
        if self.stop_event.wait(timeout=10):
            return
        while not self.stop_event.is_set():
            try:
                self._poll_once()
            except Exception as exc:
                print(f"[progress-poller] error (continuing): {exc}", flush=True)
            if self.stop_event.wait(timeout=self.poll_interval_s):
                break

    def _poll_once(self):
        tmp = self.local_path.with_suffix(self.local_path.suffix + ".tmp")
        if not _scp_from(self.ip, self.ssh_key_path, self.remote_path, tmp):
            return
        if not tmp.is_file():
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
        if cell is None or total is None or cell == self._last_cell:
            return
        self._last_cell = int(cell)
        pct = (cell / total * 100) if total else 0
        eta_str = f"ETA {eta}s" if eta is not None else "ETA -"
        ts = datetime.now().astimezone().strftime("%H:%M:%S")
        print(f"[progress {ts}] {self.anchor} cell {cell}/{total}  "
              f"({pct:.1f}%)  {phase}  {eta_str}", flush=True)


def _run_one_anchor(ip, ssh_key_path, anchor, script, total_cells,
                    cell_regex, instance_id, experiment_timeout_min,
                    result_paths: list[str] | None = None,
                    script_args: str = ""):
    """Dispatch one anchor on the running instance; mirror of launch_experiment's [4/4].

    result_paths: optional list of remote glob patterns (relative to
    ~/hd-instrument/) to SCP back AFTER the experiment completes. Examples:
      "data/testbed_pp8_week2/phi3_qformer_wiring_cuda.json"
      "data/testbed_pp8_week2/train_v1/*"
      "data/testbed_pp8_week2/train_v1/checkpoint_*.pt"
    Glob expansion happens on the remote (shell-evaluated). Files are mirrored
    under data/lambda_batch_results/<anchor>_<instance_id[:8]>/<remote_subpath>.
    """
    remote_anchor_dir = f"data/exp_{anchor}"
    regex_escaped = cell_regex.replace("'", "'\\''")
    script_args_escaped = script_args.replace("'", "'\\''") if script_args else ""
    target_cmd = (
        f"$PY -u tools/cloud/generic_progress_wrapper.py "
        f"--anchor {anchor} "
        f"--script {script} "
        f"--total-cells {total_cells} "
        f"--cell-regex '{regex_escaped}'"
        + (f" --script-args '{script_args_escaped}'" if script_args else "")
    )
    exp_cmd = (
        "set -e; cd ~/hd-instrument; git pull --ff-only > /dev/null 2>&1 || true; "
        "PY=$(if [ -x .venv/bin/python ]; then echo .venv/bin/python; else echo python3; fi); "
        f"REMOTE_OUT={remote_anchor_dir}; "
        f"REMOTE_LOG=$REMOTE_OUT/exp_run.log; "
        f"mkdir -p $REMOTE_OUT; "
        "echo '--- env ---'; $PY --version; free -h | head -2; "
        "echo '--- dispatch ---'; set -x; "
        f"(stdbuf -oL {target_cmd} 2>&1 | tee $REMOTE_LOG; "
        f"  echo \"EXP_EXIT=${{PIPESTATUS[0]}}\") || echo 'EXP_DISPATCH_FAIL'; "
        "set +x; echo '--- result ---'; "
        f"if [ -f $REMOTE_OUT/metrics.json ]; then echo 'METRICS_OK'; "
        f"ls -la $REMOTE_OUT/metrics.json; else echo 'NO_METRICS'; "
        f"tail -50 $REMOTE_LOG || true; fi"
    )

    stop_event = threading.Event()
    poller = ProgressPoller(ip, ssh_key_path, instance_id, anchor, stop_event)
    poller.start()
    try:
        rc, out, err = _ssh_run(ip, ssh_key_path, exp_cmd,
                                timeout_s=int(experiment_timeout_min * 60))
    finally:
        stop_event.set()
        poller.join(timeout=5)

    # Print with errors='replace' so non-ASCII chars (e.g. transformers'
    # tqdm progress-bar arrows) don't crash launch_batch on Windows cp1252
    # stdout. The full untranslated output still gets written to the local
    # log file (UTF-8) just below; only the stdout PREVIEW gets sanitized.
    _safe_out = (out[-3000:] or "").encode("ascii", errors="replace").decode("ascii")
    _safe_err = (err[-1000:] or "").encode("ascii", errors="replace").decode("ascii")
    print(f"---- {anchor} stdout tail ----")
    print(_safe_out)
    if err:
        print(f"---- {anchor} stderr ----\n{_safe_err}")
    print(f"---- {anchor} exit: {rc} ----")

    log_path = _REPO_ROOT / "data" / f"lambda_batch_{anchor}_{instance_id}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(out + "\n[stderr]\n" + err, encoding="utf-8")
    metrics_local = _REPO_ROOT / "data" / f"lambda_batch_{anchor}_metrics_{instance_id}.json"
    if _scp_from(ip, ssh_key_path,
                 f"~/hd-instrument/{remote_anchor_dir}/metrics.json",
                 metrics_local):
        print(f"  metrics: {metrics_local}")
    remote_log_local = _REPO_ROOT / "data" / f"lambda_batch_{anchor}_remote_log_{instance_id}.log"
    _scp_from(ip, ssh_key_path,
              f"~/hd-instrument/{remote_anchor_dir}/exp_run.log",
              remote_log_local)
    progress_local = _REPO_ROOT / "data" / f"lambda_batch_{anchor}_progress_final_{instance_id}.json"
    _scp_from(ip, ssh_key_path,
              f"~/hd-instrument/{remote_anchor_dir}/progress.json",
              progress_local)

    # Declared-result-paths SCP-back (closes Phase 1's NO_METRICS gap where
    # the experiment's output JSON existed on the remote but was never pulled
    # because the standard metrics.json scrape didn't match its path).
    result_paths_summary: list[dict[str, Any]] = []
    if result_paths:
        local_base = _REPO_ROOT / "data" / "lambda_batch_results"
        result_paths_summary = _scp_back_result_paths(
            ip, ssh_key_path, instance_id, anchor, result_paths, local_base,
        )
        # Persist the summary so the batch report can reference what was pulled
        summary_path = (local_base / f"{anchor}_{instance_id[:8]}"
                        / "result_paths_summary.json")
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(
            json.dumps(result_paths_summary, indent=2), encoding="utf-8")

    return rc, metrics_local


def main() -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)
        sys.stderr.reconfigure(line_buffering=True)
    except (AttributeError, OSError):
        pass

    parser = argparse.ArgumentParser(description="Stringed Lambda batch launcher")
    parser.add_argument("--batch", required=True,
                        help="Path to JSON batch config (list of anchor dicts)")
    parser.add_argument("--ssh-key-name", required=True)
    parser.add_argument("--ssh-key-path", required=True)
    parser.add_argument("--key-file", default=".env.lambda")
    parser.add_argument("--instance-type", default=None)
    parser.add_argument("--region", default=None)
    parser.add_argument("--max-cost-usd", type=float, default=5.0)
    parser.add_argument("--expected-wall-min", type=float, default=45.0)
    parser.add_argument("--budget-cap-usd", type=float, default=10.0)
    parser.add_argument("--repo-url",
                        default="https://github.com/mcox79/hd-instrument.git")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--default-experiment-timeout-min", type=float, default=60.0)
    parser.add_argument("--wait-for-capacity-max-s", type=float, default=3600.0,
                        help="Max time to poll Lambda catalog for capacity "
                             "BEFORE attempting launch_instance. Zero billable "
                             "cost during this wait. Default 3600s (1 hour).")
    parser.add_argument("--capacity-poll-interval-s", type=float, default=30.0,
                        help="Catalog poll interval during capacity-wait.")
    parser.add_argument("--stuck-booting-max-s", type=float, default=300.0,
                        help="If instance status stays `booting` for this many "
                             "seconds without progress, terminate fast-fail. "
                             "Caps wasted boot billing at "
                             "~rate * stuck_booting_max_s (e.g., $4.29/hr H100 "
                             "* 300s = $0.36 vs $1.07 at 900s default). "
                             "Default 300s (5 min).")
    args = parser.parse_args()

    batch_path = Path(args.batch)
    if not batch_path.is_absolute():
        batch_path = _REPO_ROOT / batch_path
    if not batch_path.is_file():
        print(f"[ERROR] batch config not found: {batch_path}")
        return 1
    try:
        batch = json.loads(batch_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[ERROR] batch JSON parse: {exc}")
        return 1
    if not isinstance(batch, list) or not batch:
        print(f"[ERROR] batch must be non-empty JSON list")
        return 1
    for i, b in enumerate(batch):
        for required in ("anchor", "script", "total_cells"):
            if required not in b:
                print(f"[ERROR] batch[{i}] missing '{required}'")
                return 1
        try:
            re.compile(b.get("cell_regex", _DEFAULT_CELL_REGEX))
        except re.error as exc:
            print(f"[ERROR] batch[{i}] invalid cell_regex: {exc}")
            return 1

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

    try:
        catalog = client.list_instance_types()
    except LambdaClientError as exc:
        print(f"[ERROR] catalog: {exc}")
        return 1
    with_cap = [t for t in catalog if t.regions_available]
    with_cap.sort(key=lambda t: t.price_cents_per_hour)
    if args.instance_type:
        # Explicit type: look up in FULL catalog so we can fall through to the
        # wait_for_capacity gate even when current capacity is zero. This is
        # the whole point of having the gate -- capacity often becomes
        # available within minutes; we should not error out instantly.
        target = next((t for t in catalog if t.name == args.instance_type), None)
        if not target:
            print(f"[ERROR] {args.instance_type} not in Lambda catalog at all")
            return 1
        if not target.regions_available:
            print(f"  {args.instance_type} has no current capacity; "
                  f"will poll via wait_for_capacity gate")
    else:
        if not with_cap:
            print("[ERROR] no capacity for ANY instance type")
            return 1
        target = with_cap[0]
    predicted = target.hourly_rate_usd * (args.expected_wall_min / 60.0)

    print("=" * 70)
    print(f"Batch launcher: {len(batch)} anchor(s)")
    print("=" * 70)
    for i, b in enumerate(batch):
        print(f"  [{i+1}/{len(batch)}] {b['anchor']} ({b['total_cells']} cells)")
    print(f"  Instance type:       {target.name}")
    print(f"  Region preference:   {args.region or 'ANY (first available)'}")
    print(f"  Rate:                ${target.hourly_rate_usd:.2f}/hr")
    print(f"  Expected wall:       {args.expected_wall_min:.1f} min (entire batch)")
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

    # Pre-flight capacity gate: confirm target type has regions_available
    # BEFORE we make a billable launch call. Returns the available regions
    # at the moment capacity was seen; we use the FIRST one for launch so
    # there's no stale-region-cache risk if capacity shifted during the wait.
    print(f"\n[0/3] Verifying capacity for {target.name} "
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
    # Use FRESH capacity result, not the cached target.regions_available
    # from the initial catalog query (which may have gone stale during wait).
    region = available_regions[0]
    print(f"  Selected region for launch: {region}")

    print(f"\n[1/3] Launching {target.name} in {region}...")
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
                name=f"batch-{batch[0]['anchor'][:24]}",
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
                time.sleep(backoff); backoff *= 2
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

    print(f"[wait] Waiting for active (stuck-booting fast-fail at "
          f"{args.stuck_booting_max_s:.0f}s)...")
    try:
        inst = client.wait_for_active(
            instance_id, timeout_s=args.stuck_booting_max_s)
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

    print(f"\n[2/3] Bootstrapping {instance_id} (ONCE for entire batch)...")
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
            encoding="utf-8", errors="replace", timeout=2700,
        )
        print(result.stdout)
        if result.stderr:
            print(f"---- bootstrap stderr ----\n{result.stderr[-1500:]}",
                  file=sys.stderr)
        boot_ok = (result.returncode == 0)
    except Exception as exc:
        print(f"  [ERROR] bootstrap: {exc}")
        boot_ok = False
    if not boot_ok:
        print(f"\n[ERROR] bootstrap failed; aborting")
        return 1

    print(f"\n[3/3] Dispatching {len(batch)} experiments sequentially...")
    rcs: list[tuple[str, int, Path | None]] = []
    for i, b in enumerate(batch):
        timeout = b.get("experiment_timeout_min", args.default_experiment_timeout_min)
        cell_regex = b.get("cell_regex", _DEFAULT_CELL_REGEX)
        print(f"\n=== [{i+1}/{len(batch)}] {b['anchor']} "
              f"({b['total_cells']} cells, {timeout:.0f}m timeout) ===")
        result_paths = b.get("result_paths") or []
        script_args = b.get("script_args", "")
        rc, metrics_path = _run_one_anchor(
            ip=ip, ssh_key_path=args.ssh_key_path,
            anchor=b["anchor"], script=b["script"],
            total_cells=int(b["total_cells"]),
            cell_regex=cell_regex,
            instance_id=instance_id,
            experiment_timeout_min=timeout,
            result_paths=result_paths,
            script_args=script_args,
        )
        rcs.append((b["anchor"], rc, metrics_path if metrics_path and metrics_path.is_file() else None))

    print(f"\n[terminate]")
    _force_terminate()
    terminate_ts = datetime.now(timezone.utc)
    actual_wall_s = (terminate_ts - launch_ts).total_seconds()
    actual_cost = inst.hourly_rate_usd * (actual_wall_s / 3600.0)

    print()
    print("=" * 70)
    print(f"Batch report: {len(batch)} anchor(s)")
    print("=" * 70)
    print(f"  Predicted:     ${predicted:.2f}  ({args.expected_wall_min:.1f} min)")
    print(f"  Actual wall:   {actual_wall_s/60:.1f} min")
    print(f"  Actual cost:   ${actual_cost:.2f}")
    if predicted > 0:
        rel = (actual_cost - predicted) / predicted * 100
        print(f"  Delta:         ${actual_cost - predicted:+.2f}  ({rel:+.1f}%)")
    print(f"  Bootstrap pay-once savings: ~${0.13 * (len(batch) - 1):.2f} + "
          f"~{5 * (len(batch) - 1)}m wall vs N separate launches")
    print()
    for anchor, rc, mp in rcs:
        status = "OK" if rc == 0 else f"rc={rc}"
        mpath = str(mp) if mp else "MISSING"
        print(f"  [{status:>6}] {anchor}: {mpath}")

    update_cost(current_hourly_rate_usd=0.0, active_instances=[])
    new_total = accumulate_run_cost(actual_cost)
    print(f"  Cumulative today: ${new_total:.2f}")

    report = {
        "batch_size": len(batch),
        "anchors": [a for a, _, _ in rcs],
        "instance_id": instance_id,
        "instance_type": target.name,
        "hourly_rate_usd": inst.hourly_rate_usd,
        "wall_min": round(actual_wall_s / 60, 1),
        "actual_cost_usd": round(actual_cost, 2),
        "experiment_rcs": [{"anchor": a, "rc": rc,
                            "metrics": str(mp) if mp else None}
                           for a, rc, mp in rcs],
        "launched_at": launch_ts.isoformat(),
        "terminated_at": terminate_ts.isoformat(),
    }
    rp = _REPO_ROOT / "data" / f"lambda_batch_report_{instance_id}.json"
    rp.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"  Report: {rp}")

    all_clean = all(rc == 0 for _, rc, _ in rcs)
    return 0 if all_clean else 2


if __name__ == "__main__":
    sys.exit(main())
