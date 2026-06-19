"""Overnight autonomous experiment queue runner.

Reads queue.json from data/overnight_queue/. Runs each pending experiment
as a subprocess. Marks completed/failed/skipped. Continues on failure.
Logs everything to per-experiment log files PLUS a global queue.log.

Watchdog property: this script runs as a long-lived OS process on the
remote GPU. Even if Claude is not connected, the queue continues.

To extend the queue while it's running, edit queue.json (add new entries).
The runner re-reads queue.json after each experiment, so new items get
picked up automatically.

queue.json format:
  {
    "experiments": [
      {"name": "exp_name", "script": "experiments/foo.py", "status": "pending"},
      ...
    ]
  }

status values: pending, running, completed, failed, skipped
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime


REPO = Path(__file__).resolve().parent.parent
# Queue dir can be overridden via command-line arg (for parallel local CPU queue).
# Default = data/overnight_queue (the remote GPU queue).
QUEUE_DIR_NAME = sys.argv[1] if len(sys.argv) > 1 else "overnight_queue"
QUEUE_DIR = REPO / "data" / QUEUE_DIR_NAME
QUEUE_FILE = QUEUE_DIR / "queue.json"
GLOBAL_LOG = QUEUE_DIR / "queue.log"
HEARTBEAT_FILE = QUEUE_DIR / "heartbeat.json"
POLL_INTERVAL = 5  # seconds between checks when queue is empty


def log(msg: str) -> None:
    ts = datetime.now().isoformat(timespec="seconds")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with GLOBAL_LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def heartbeat(status: str, current: str | None = None) -> None:
    """Write a heartbeat file so external observers can verify the runner is alive."""
    HEARTBEAT_FILE.write_text(json.dumps({
        "ts": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "current": current,
        "pid": str(__import__("os").getpid()),
    }, indent=2))


_CASCADE_STATE = {"consecutive_fails": 0, "last_exit": None}
CASCADE_THRESHOLD = 3
CASCADE_SLEEP_S = 300


def record_outcome(exit_code: int) -> None:
    """Track consecutive failures with same exit code. Sleep if cascade detected."""
    if exit_code == 0:
        _CASCADE_STATE["consecutive_fails"] = 0
        _CASCADE_STATE["last_exit"] = None
        return
    if exit_code == _CASCADE_STATE["last_exit"]:
        _CASCADE_STATE["consecutive_fails"] += 1
    else:
        _CASCADE_STATE["consecutive_fails"] = 1
        _CASCADE_STATE["last_exit"] = exit_code
    if _CASCADE_STATE["consecutive_fails"] >= CASCADE_THRESHOLD:
        log(f"CASCADE detected: {_CASCADE_STATE['consecutive_fails']} consecutive failures with exit={exit_code}. Sleeping {CASCADE_SLEEP_S}s for OS recovery.")
        heartbeat("cascade_recovery", current=f"exit={exit_code}")
        time.sleep(CASCADE_SLEEP_S)
        _CASCADE_STATE["consecutive_fails"] = 0
        _CASCADE_STATE["last_exit"] = None
        log("Cascade recovery sleep done; resuming.")


def read_queue() -> dict:
    if not QUEUE_FILE.exists():
        return {"experiments": []}
    for attempt in range(8):
        try:
            return json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            log(f"Queue file unreadable ({e}); waiting for next poll")
            return {"experiments": []}
        except PermissionError:
            time.sleep(0.25 * (attempt + 1))
    log("Queue file locked after 8 retries; treating as empty for this poll")
    return {"experiments": []}


def write_queue(q: dict) -> None:
    for attempt in range(8):
        try:
            QUEUE_FILE.write_text(json.dumps(q, indent=2))
            return
        except PermissionError:
            time.sleep(0.25 * (attempt + 1))
    log("Queue file locked for write after 8 retries; skipping update this cycle")


def update_entry(name: str, **kwargs) -> None:
    """Update a queue entry's fields by name. Re-reads queue to avoid race
    with manual edits."""
    q = read_queue()
    for e in q["experiments"]:
        if e["name"] == name:
            e.update(kwargs)
            break
    write_queue(q)


def run_one(entry: dict) -> str:
    """Run a single experiment. Returns final status."""
    name = entry["name"]
    script = entry["script"]
    script_path = REPO / script
    if not script_path.exists():
        log(f"SKIP {name}: script not found at {script_path}")
        update_entry(name, status="skipped", error="script_not_found")
        return "skipped"

    log_path = QUEUE_DIR / f"{name}.log"
    log(f"START {name} -> {script_path}")
    update_entry(name, status="running", started_at=datetime.now().isoformat(timespec="seconds"))
    heartbeat("running", name)

    t0 = time.perf_counter()
    try:
        with log_path.open("w", encoding="utf-8") as logf:
            result = subprocess.run(
                [sys.executable, "-u", str(script_path)],
                cwd=str(REPO),
                stdout=logf,
                stderr=subprocess.STDOUT,
                timeout=entry.get("timeout_s", 14400),  # default 4 hours per experiment
            )
        dt = time.perf_counter() - t0
        if result.returncode == 0:
            log(f"DONE {name} in {dt:.1f}s (exit 0)")
        record_outcome(0)
            update_entry(name, status="completed",
                        ended_at=datetime.now().isoformat(timespec="seconds"),
                        wall_s=dt)
            return "completed"
        else:
            log(f"FAIL {name} exit={result.returncode} after {dt:.1f}s")
        record_outcome(result.returncode)
            update_entry(name, status="failed",
                        ended_at=datetime.now().isoformat(timespec="seconds"),
                        wall_s=dt, exit_code=result.returncode)
            return "failed"
    except subprocess.TimeoutExpired:
        dt = time.perf_counter() - t0
        log(f"TIMEOUT {name} after {dt:.1f}s")
        update_entry(name, status="failed",
                    ended_at=datetime.now().isoformat(timespec="seconds"),
                    wall_s=dt, error="timeout")
        return "failed"
    except Exception as e:
        dt = time.perf_counter() - t0
        log(f"ERROR {name}: {e}")
        update_entry(name, status="failed",
                    ended_at=datetime.now().isoformat(timespec="seconds"),
                    wall_s=dt, error=str(e))
        return "failed"


def main():
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    log("============================================")
    log("Overnight queue runner started")
    log(f"Repo: {REPO}")
    log(f"Queue file: {QUEUE_FILE}")
    log(f"Python: {sys.executable}")
    heartbeat("idle")

    consecutive_empty = 0
    while True:
        q = read_queue()
        # Find next pending
        next_entry = None
        for e in q["experiments"]:
            if e.get("status") == "pending":
                next_entry = e
                break
        if next_entry is None:
            consecutive_empty += 1
            heartbeat("idle")
            # Stop after long idle (1 hour) so the runner doesn't burn CPU forever
            if consecutive_empty * POLL_INTERVAL >= 3600:
                log("Queue empty for 1 hour; exiting")
                heartbeat("stopped")
                return
            time.sleep(POLL_INTERVAL)
            continue
        consecutive_empty = 0
        run_one(next_entry)


if __name__ == "__main__":
    main()
