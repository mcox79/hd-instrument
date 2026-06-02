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
  * PROT-018 post-run N-suffix enforcement: if an anchor name contains
    _n<N>, the runner parses the script's emitted metrics.json after a
    nominally-successful run and refuses to mark it 'completed' unless the
    recorded production N matches the suffix. Mismatch -> failed with
    error=n_mismatch. Belt-and-suspenders with queue_add.py exit-6.

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
import re
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
    payload_text = json.dumps(payload, indent=2)
    try:
        # Atomic write: write to .tmp then rename so readers never see partial JSON.
        p_runner = _PATHS["heartbeat_runner"]
        tmp_runner = p_runner.with_suffix(".tmp")
        tmp_runner.write_text(payload_text, encoding="utf-8")
        os.replace(tmp_runner, p_runner)
        # Also update legacy heartbeat.json so existing dashboard panels keep working
        p_legacy = _PATHS["heartbeat_legacy"]
        tmp_legacy = p_legacy.with_suffix(".tmp")
        tmp_legacy.write_text(payload_text, encoding="utf-8")
        os.replace(tmp_legacy, p_legacy)
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

# Required scalar fields the verdict relay actually consumes downstream.
# - verdict_msg and elapsed_s are TRULY required (verdict_handler reads them).
# - The verdict label may be carried under EITHER `verdict` OR `verdict_tag`
#   (legacy + KF/PB/MoE scripts emit `verdict_tag`; T1/saad/bid scripts emit
#   `verdict`). Both shapes are HARD_PASS-valid; the gate must accept either.
# - `summary` was historically gated here but the runner does NOT read it for
#   any control flow -- scripts variously emit `summary`, `cells`, `all_cells`,
#   or `config` instead. Requiring it caused 30+ false-failed verdicts on
#   legitimate HARD_PASS runs (KF1/KF2/PB2/T1/MoE/bid/anchor_battery families).
#   verdict_msg + elapsed_s + a verdict label is sufficient for the relay.
_METRICS_REQUIRED_FIELDS = ("verdict_msg", "elapsed_s")
_METRICS_VERDICT_FIELDS = ("verdict", "verdict_tag")


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
    # Verdict label may be carried as either `verdict` or `verdict_tag`.
    verdict_val = data.get("verdict") or data.get("verdict_tag")
    if not verdict_val or not isinstance(verdict_val, str):
        return "empty_verdict"
    if not data.get("verdict_msg") or not isinstance(data["verdict_msg"], str):
        return "empty_verdict_msg"
    return None


# ---------- PROT-018: anchor-name _n<N> vs metrics-N validator ----------

# Extracts the LAST _n<digits> token from an anchor name. The trailing boundary
# is end-of-string or underscore so we do not match _n inside words like
# 'next', 'noise', 'norm'. Mirrors tools/queue_add.py check_n_suffix_binding.
_ANCHOR_N_SUFFIX_RE = re.compile(r"_n(\d+)(?:_|$)")


def _extract_anchor_n(anchor_name: str) -> int | None:
    """Return the integer N from an anchor name's _n<N> suffix, or None."""
    m = _ANCHOR_N_SUFFIX_RE.search(anchor_name)
    if m is None:
        return None
    try:
        return int(m.group(1))
    except (TypeError, ValueError):
        return None


def _extract_metrics_n(metrics: dict) -> int | None:
    """Return the production N recorded in a metrics dict.

    Schema is per-script: scripts variously place N at metrics["summary"]["N"],
    metrics["config"]["N"], or metrics["detail"]["N"]. We probe in that order
    and return the first integer found. None if no recognisable N field.
    """
    if not isinstance(metrics, dict):
        return None
    for key in ("summary", "config", "detail"):
        sub = metrics.get(key)
        if isinstance(sub, dict):
            val = sub.get("N")
            if val is None:
                # Some scripts use 'N_run' to record the actually-used N and
                # 'N_production' to record the intended one. The runner cares
                # what ran -> prefer N_run when present.
                val = sub.get("N_run")
            if isinstance(val, bool):  # avoid True/False being treated as 1/0
                continue
            try:
                return int(val)
            except (TypeError, ValueError):
                continue
    return None


def validate_n_suffix_binding(anchor_name: str, metrics_path: Path) -> str | None:
    """PROT-018 post-run check: anchor _n<N> must match recorded production N.

    Returns None on PASS (suffix matches metrics, or anchor has no _n suffix,
    or metrics file unreadable -- the schema validator above catches missing
    metrics separately so we do not double-fail on that).

    Returns a short error string on REJECT (mismatch) -- caller marks the
    queue entry failed with this string in 'error' and logs a HIGH-importance
    status_log entry.

    The check is a no-op when:
      - anchor_name has no _n<digits> suffix (rule does not apply)
      - metrics file is missing or unparseable (schema validator handles it)
      - metrics has no recognised N field (cannot reject; surface elsewhere)
    """
    suffix_n = _extract_anchor_n(anchor_name)
    if suffix_n is None:
        return None  # no suffix -> rule does not apply
    if not metrics_path.exists():
        return None  # schema validator already failed; don't double-flag
    try:
        metrics = json.loads(metrics_path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return None  # schema validator handles unreadable / invalid JSON

    metrics_n = _extract_metrics_n(metrics)
    if metrics_n is None:
        # No recognisable N in metrics. We do NOT reject here -- some legitimate
        # scripts (e.g. N-sweeps reporting a list under summary.N_sweep) have
        # no scalar production-N. Surface as a warning string via stderr only.
        return None

    if metrics_n == suffix_n:
        return None  # PASS

    # Detect mode if recorded so the error message names smoke explicitly.
    mode = None
    for key in ("config", "detail"):
        sub = metrics.get(key)
        if isinstance(sub, dict) and "mode" in sub:
            mode = str(sub["mode"]).lower()
            break

    mode_tag = f" mode={mode}" if mode else ""
    return (
        f"n_mismatch: anchor _n{suffix_n} but metrics recorded N={metrics_n}{mode_tag} "
        f"(PROT-018: anchor-name _n<N> suffix is a binding contract; this run is "
        f"NOT acceptable as the FULL N={suffix_n} result the anchor name promises)"
    )


def _log_n_mismatch_status_event(name: str, error_msg: str, metrics_path: Path) -> None:
    """Append an importance=HIGH status_log entry for a PROT-018 N-mismatch.

    Failures are silent if state.log_event is unavailable -- the queue
    mark_outcome above still records the n_mismatch error, so this is a
    visibility extra, not the primary record.
    """
    try:
        sys.path.insert(0, str(REPO / "tools"))
        from orchestrator.state import log_event  # type: ignore
        suffix_n = _extract_anchor_n(name)
        actual_n = None
        try:
            metrics = json.loads(metrics_path.read_text(encoding="utf-8", errors="replace"))
            actual_n = _extract_metrics_n(metrics)
        except Exception:
            pass
        log_event(
            "n_mismatch_runner_reject",
            f"PROT-018 runner reject: {name} anchor _n{suffix_n} vs metrics N={actual_n}",
            plain_language=(
                f"The runner refused to mark '{name}' completed because the experiment "
                f"recorded N={actual_n} but the anchor name promised N={suffix_n}. "
                f"This is the smoke-vs-FULL label drift PROT-018 was created to block."
            ),
            importance="HIGH",
            anchor=name,
            anchor_suffix_n=suffix_n,
            metrics_n=actual_n,
            error_msg=error_msg,
        )
    except Exception:
        # Best-effort; do not crash the runner over a logging side-effect.
        pass


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
    # HDLAB_RUN_MODE=full: production scripts default to full scope when runner
    # picks them up. Scripts that use os.environ.get("HDLAB_RUN_MODE", ...) will
    # now always see "full" regardless of their fallback default. Belt-and-suspenders
    # for the class of bug where default="smoke" caused silent smoke-scope runs on
    # the production runner (Round 6 batch 2026-06-01, anchors E/F/J/K).
    child_env = {**os.environ, "HDLAB_EXP_NAME": name, "PYTHONIOENCODING": "utf-8",
                 "HDLAB_RUN_MODE": "full"}

    # On Windows: spawn child at BELOW_NORMAL priority so the desktop stays
    # usable during long CPU-bound runs. This is DEFAULT-ON for all remote_cpu
    # experiments; no per-ship flag needed. On non-Windows the flag is 0 (no-op).
    # CREATE_NO_WINDOW (0x08000000) suppresses the console flash that fires every
    # time the runner spawns a new child experiment on Windows. Without this flag,
    # every child experiment briefly opens a console window visible to the user.
    _below_normal_flag = getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0)
    _no_window_flag = 0x08000000 if os.name == "nt" else 0
    _spawn_flags = _below_normal_flag | _no_window_flag

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
                creationflags=_spawn_flags,
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
            # PROT-018 post-run check: anchor _n<N> must match recorded
            # production N. Belt-and-suspenders with queue_add.py exit-6.
            # Fires when (a) a pre-PROT-018 backlog entry runs through, OR
            # (b) someone bypasses queue_add (--allow-duplicate / rerun-as),
            # OR (c) a script ran SMOKE mode despite no --smoke flag.
            n_err = validate_n_suffix_binding(name, metrics_path)
            if n_err is not None:
                log(f"FAIL {name}: exit=0 but PROT-018 N-suffix REJECT: {n_err}")
                _log_n_mismatch_status_event(name, n_err, metrics_path)
                mark_outcome(queue_path, name, "failed",
                             ended_at=_now_iso(), wall_s=dt,
                             error=n_err,
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
    ap.add_argument("--singleton-pid-file", default=None,
                    help="Path to PID file for singleton lock. If the recorded PID is "
                         "alive, this invocation exits immediately (no duplicate runner).")
    args = ap.parse_args()

    # --- Singleton PID-file guard ---
    # Prevents schtasks /Run from spawning parallel instances when the task is
    # already running (e.g. repeated revive_cpu_runner_via_schtasks.ps1 calls).
    if args.singleton_pid_file:
        pid_path = Path(args.singleton_pid_file)
        pid_path.parent.mkdir(parents=True, exist_ok=True)
        my_pid = os.getpid()
        if pid_path.exists():
            try:
                existing_pid = int(pid_path.read_text(encoding="ascii").strip())
                # Check if that PID is still a live python.exe
                import ctypes
                PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
                h = ctypes.windll.kernel32.OpenProcess(
                    PROCESS_QUERY_LIMITED_INFORMATION, False, existing_pid)
                if h:
                    ctypes.windll.kernel32.CloseHandle(h)
                    # PID alive — we are the duplicate; abort cleanly
                    msg = (f"[{datetime.now().isoformat(timespec='seconds')}] "
                           f"SINGLETON ABORT: runner already running as PID "
                           f"{existing_pid}; this instance (PID {my_pid}) exiting.")
                    print(msg, flush=True)
                    try:
                        # Append to runner log if paths not yet set up
                        log_dir = Path(args.singleton_pid_file).parent
                        fallback_log = log_dir / f"{Path(args.singleton_pid_file).stem}_singleton.log"
                        with fallback_log.open("a", encoding="utf-8") as f:
                            f.write(msg + "\n")
                    except Exception:
                        pass
                    return 0
                # PID dead (OpenProcess returned NULL) — stale file; overwrite below
            except (ValueError, OSError, AttributeError):
                pass  # Malformed file or non-Windows; proceed to overwrite
        # Write our own PID
        try:
            pid_path.write_text(str(my_pid), encoding="ascii")
        except OSError:
            pass  # Non-fatal; singleton guard best-effort only

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
        # Clean up singleton PID file so the next launch starts cleanly
        if args.singleton_pid_file:
            try:
                Path(args.singleton_pid_file).unlink(missing_ok=True)
            except OSError:
                pass


if __name__ == "__main__":
    sys.exit(main())
