"""Production runner v2 — multi-runner-safe, drop-in replacement for run_overnight_queue.py.

Feature parity with the live runner PLUS:
  * safe_queue atomic claim/mark_outcome (lock-safe for concurrent runners)
  * per-runner ID + heartbeat (heartbeat.<id>.json)
  * tolerates older single-runner clients (defaults --id to 'runner_0',
    writes heartbeat.runner_0.json AND legacy heartbeat.json)
  * OMP/MKL env vars are respected (already set in os.environ by launcher)
  * CPU usage cap: on Windows, child experiment processes are spawned at
    BELOW_NORMAL priority so the desktop stays usable during runs.
    The runner process itself should be launched at BELOWNORMAL via the
    launcher .bat (start /BELOWNORMAL). No per-ship opt-in needed.

CLI (preserves run_overnight_queue.py positional arg):
  python runner_v2_prod.py                          # uses overnight_queue, id=runner_0
  python runner_v2_prod.py remote_cpu_queue         # uses remote_cpu_queue, id=runner_0
  python runner_v2_prod.py --queue-dir <dir> --id <id>  # explicit
  python runner_v2_prod.py overnight_queue --id gpu_runner_0
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

from safe_queue import claim_next_pending, mark_outcome, QueueLock, lock_backend_name  # noqa: E402


# ---------- Constants (feature-parity with live runner) ----------
POLL_INTERVAL_S = 5
IDLE_EXIT_S = 3600  # 1 hour idle -> exit
HEARTBEAT_INTERVAL_S = 30
DEFAULT_TIMEOUT_S = 14400  # 4 hours
METRICS_MIN_BYTES = 100  # below this -> mark inconclusive even if exit=0

# Cascade recovery
CASCADE_THRESHOLD = 3
CASCADE_SLEEP_S = 300


# ---------- Module-level state ----------
_HB_STATE = {"status": "starting", "current": None, "stop": False, "runner_id": "runner_0"}
_CASCADE = {"consecutive_fails": 0, "last_exit": None}
_PATHS: dict = {}  # populated in main()


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def log(msg: str) -> None:
    line = f"[{_now_iso()}] [{_HB_STATE['runner_id']}] {msg}"
    print(line, flush=True)
    try:
        with _PATHS["global_log"].open("a", encoding="utf-8") as f:
            f.write(line + "\n")
        with _PATHS["runner_log"].open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except (OSError, KeyError):
        pass


# ---------- Heartbeat ----------

def _write_heartbeat() -> None:
    payload = {
        "ts": _now_iso(),
        "runner_id": _HB_STATE["runner_id"],
        "pid": str(os.getpid()),
        "status": _HB_STATE["status"],
        "current": _HB_STATE["current"],
    }
    try:
        _PATHS["heartbeat_runner"].write_text(json.dumps(payload, indent=2), encoding="utf-8")
        # Also update legacy heartbeat.json so existing dashboard panels keep working
        _PATHS["heartbeat_legacy"].write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except OSError:
        pass


def heartbeat(status: str, current: str | None = None) -> None:
    _HB_STATE["status"] = status
    _HB_STATE["current"] = current
    _write_heartbeat()


def _heartbeat_loop() -> None:
    while not _HB_STATE["stop"]:
        _write_heartbeat()
        time.sleep(HEARTBEAT_INTERVAL_S)


# ---------- Cascade recovery ----------

def record_outcome(exit_code: int) -> None:
    if exit_code == 0:
        _CASCADE["consecutive_fails"] = 0
        _CASCADE["last_exit"] = None
        return
    if exit_code == _CASCADE["last_exit"]:
        _CASCADE["consecutive_fails"] += 1
    else:
        _CASCADE["consecutive_fails"] = 1
        _CASCADE["last_exit"] = exit_code
    if _CASCADE["consecutive_fails"] >= CASCADE_THRESHOLD:
        log(f"CASCADE detected: {_CASCADE['consecutive_fails']} consecutive failures "
            f"exit={exit_code}. Sleeping {CASCADE_SLEEP_S}s for OS recovery.")
        heartbeat("cascade_recovery", current=f"exit={exit_code}")
        time.sleep(CASCADE_SLEEP_S)
        _CASCADE["consecutive_fails"] = 0
        _CASCADE["last_exit"] = None
        log("Cascade recovery sleep done; resuming.")


# ---------- Metrics schema validation ----------

_METRICS_REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


def _validate_metrics_schema(path: Path) -> str | None:
    """Return None if valid, else a short error string. Never raises."""
    if not path.exists():
        return "missing"
    if path.stat().st_size < METRICS_MIN_BYTES:
        return f"too_small ({path.stat().st_size}B)"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return f"invalid_json: {e}"
    if not isinstance(data, dict):
        return f"not_an_object: {type(data).__name__}"
    missing = [f for f in _METRICS_REQUIRED_FIELDS if f not in data]
    if missing:
        return f"missing_fields: {missing}"
    if not data.get("verdict") or not isinstance(data["verdict"], str):
        return "empty_verdict"
    if not data.get("verdict_msg") or not isinstance(data["verdict_msg"], str):
        return "empty_verdict_msg"
    return None


# ---------- Run a single experiment ----------

def run_one(entry: dict) -> str:
    name = entry["name"]
    script = entry["script"]
    script_path = REPO / script
    queue_path = _PATHS["queue_file"]
    queue_dir = _PATHS["queue_dir"]

    if not script_path.exists():
        log(f"SKIP {name}: script not found at {script_path}")
        mark_outcome(queue_path, name, "skipped",
                     error="script_not_found",
                     completed_by=_HB_STATE["runner_id"],
                     completed_at=_now_iso())
        return "skipped"

    log_path = queue_dir / f"{name}.log"
    log(f"START {name} -> {script_path}")
    heartbeat("running", name)

    # Pass HDLAB_EXP_NAME so the experiment writes to data/exp_{name}/
    # regardless of how its own __file__ path resolves. Fixes the silent-fail
    # mode where queue-renamed entries (e.g. *_v2) wrote to the un-suffixed
    # directory and the runner couldn't find metrics.
    #
    # PYTHONIOENCODING=utf-8 forces the child's stdout/stderr to UTF-8, so
    # print() of emoji / em-dash / unicode does NOT crash on Windows cp1252
    # default codepage. This eliminates the structural reason for the
    # ASCII-only-in-scripts rule (feedback_ascii_only_in_scripts) — scripts
    # may now use unicode freely in print() / verdict_msg.
    child_env = {**os.environ, "HDLAB_EXP_NAME": name, "PYTHONIOENCODING": "utf-8"}

    # On Windows: spawn child at BELOW_NORMAL priority so the desktop stays
    # usable during long CPU-bound runs. This is DEFAULT-ON for all remote_cpu
    # experiments; no per-ship flag needed. On non-Windows the flag is 0 (no-op).
    _below_normal_flag = getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0)

    t0 = time.perf_counter()
    try:
        with log_path.open("w", encoding="utf-8") as logf:
            result = subprocess.run(
                [sys.executable, "-u", str(script_path)],
                cwd=str(REPO),
                env=child_env,
                stdout=logf,
                stderr=subprocess.STDOUT,
                timeout=entry.get("timeout_s", DEFAULT_TIMEOUT_S),
                creationflags=_below_normal_flag,
            )
        dt = time.perf_counter() - t0

        if result.returncode == 0:
            # Validate metrics.json: exists, non-trivial, has required fields.
            metrics_path = REPO / "data" / f"exp_{name}" / "metrics.json"
            schema_err = _validate_metrics_schema(metrics_path)
            if schema_err is not None:
                log(f"FAIL {name}: exit=0 but metrics invalid: {schema_err}")
                mark_outcome(queue_path, name, "failed",
                             ended_at=_now_iso(), wall_s=dt,
                             error=f"metrics_invalid: {schema_err}",
                             completed_by=_HB_STATE["runner_id"],
                             failed_at=_now_iso())
                record_outcome(0)
                return "failed"
            log(f"DONE {name} in {dt:.1f}s (exit 0)")
            mark_outcome(queue_path, name, "completed",
                         ended_at=_now_iso(), wall_s=dt,
                         completed_by=_HB_STATE["runner_id"],
                         completed_at=_now_iso())
            record_outcome(0)
            return "completed"
        else:
            log(f"FAIL {name} exit={result.returncode} after {dt:.1f}s")
            mark_outcome(queue_path, name, "failed",
                         ended_at=_now_iso(), wall_s=dt,
                         exit_code=result.returncode,
                         completed_by=_HB_STATE["runner_id"],
                         failed_at=_now_iso())
            record_outcome(result.returncode)
            return "failed"

    except subprocess.TimeoutExpired:
        dt = time.perf_counter() - t0
        log(f"TIMEOUT {name} after {dt:.1f}s")
        mark_outcome(queue_path, name, "failed",
                     ended_at=_now_iso(), wall_s=dt,
                     error="timeout",
                     completed_by=_HB_STATE["runner_id"],
                     failed_at=_now_iso())
        record_outcome(124)  # bash timeout convention
        return "failed"

    except Exception as e:
        dt = time.perf_counter() - t0
        log(f"ERROR {name}: {e}")
        mark_outcome(queue_path, name, "failed",
                     ended_at=_now_iso(), wall_s=dt,
                     error=str(e),
                     completed_by=_HB_STATE["runner_id"],
                     failed_at=_now_iso())
        record_outcome(1)
        return "failed"


# ---------- Main loop ----------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("positional_queue", nargs="?", default=None,
                    help="Queue dir name under data/ (legacy positional arg)")
    ap.add_argument("--queue-dir", default=None,
                    help="Path to queue dir (full path, overrides positional)")
    ap.add_argument("--id", default=None,
                    help="Runner ID (default: $RUNNER_ID env or 'runner_0')")
    ap.add_argument("--idle-exit-minutes", type=int, default=60,
                    help="Exit after this many minutes of empty queue (default: 60)")
    args = ap.parse_args()

    # Resolve queue dir
    if args.queue_dir:
        queue_dir = Path(args.queue_dir).resolve()
    else:
        name = args.positional_queue or "overnight_queue"
        queue_dir = REPO / "data" / name

    queue_dir.mkdir(parents=True, exist_ok=True)
    queue_file = queue_dir / "queue.json"

    # Resolve runner ID
    runner_id = args.id or os.environ.get("RUNNER_ID") or "runner_0"
    _HB_STATE["runner_id"] = runner_id

    # Populate paths
    _PATHS["queue_dir"] = queue_dir
    _PATHS["queue_file"] = queue_file
    _PATHS["global_log"] = queue_dir / "queue.log"
    _PATHS["runner_log"] = queue_dir / f"queue.{runner_id}.log"
    _PATHS["heartbeat_runner"] = queue_dir / f"heartbeat.{runner_id}.json"
    _PATHS["heartbeat_legacy"] = queue_dir / "heartbeat.json"

    # Initial queue.json (if missing)
    if not queue_file.exists():
        queue_file.write_text(json.dumps({"experiments": []}, indent=2), encoding="utf-8")

    log("============================================")
    log(f"Runner v2 started: id={runner_id} pid={os.getpid()}")
    log(f"Repo:      {REPO}")
    log(f"Queue:     {queue_file}")
    log(f"Python:    {sys.executable}")
    log(f"OMP_NUM_THREADS: {os.environ.get('OMP_NUM_THREADS', '(unset)')}")
    log(f"Lock backend:    {lock_backend_name()}")
    _bnf = getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0)
    log(f"CPU cap:         child experiments launched at {'BELOW_NORMAL priority (Windows)' if _bnf else 'default priority (non-Windows)'}")
    heartbeat("idle")

    threading.Thread(target=_heartbeat_loop, daemon=True).start()

    idle_exit_s = args.idle_exit_minutes * 60
    consecutive_empty = 0
    pause_file = queue_dir / "PAUSED"
    try:
        while True:
            # Honor PAUSED flag: idle without claiming, don't count toward idle exit.
            if pause_file.exists():
                heartbeat("paused")
                consecutive_empty = 0
                time.sleep(POLL_INTERVAL_S)
                continue
            entry = claim_next_pending(queue_file, runner_id, _now_iso())
            if entry is None:
                consecutive_empty += 1
                heartbeat("idle")
                if consecutive_empty * POLL_INTERVAL_S >= idle_exit_s:
                    log(f"Queue empty for {args.idle_exit_minutes} min; exiting")
                    heartbeat("stopped")
                    return 0
                time.sleep(POLL_INTERVAL_S)
                continue
            consecutive_empty = 0
            run_one(entry)
    finally:
        _HB_STATE["stop"] = True
        heartbeat("exited")
        log(f"Runner {runner_id} exiting")


if __name__ == "__main__":
    sys.exit(main())
