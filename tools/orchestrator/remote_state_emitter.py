"""Remote-side state emitter for the hd-instrument remote bridge.

Runs on marsh@home (Windows, cmd.exe environment). Snapshots queue state,
runner heartbeats, and recent verdicts into a single JSON file every 30s.

Designed to be launched once by Windows Task Scheduler (or a schtasks entry)
and run as a while-True loop. It writes:
    C:/dev/hd-instrument/data/remote_state_cache.json

The local orchestrator (heartbeat_watchdog.py patched) SCPs this file back to
D:/AI/hd-instrument/data/remote_state_cache.json every 30s, so sub-agents can
read it locally without any SSH overhead.

Usage (on remote):
    C:/dev/hd-instrument/.venv/Scripts/python.exe ^
        C:/dev/hd-instrument/tools/orchestrator/remote_state_emitter.py

Or via schtasks (see install_remote_emitter_schtask.ps1 in the same directory).
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

REPO = Path(r"C:/dev/hd-instrument")
OUTPUT = REPO / "data" / "remote_state_cache.json"
OVERNIGHT_QUEUE = REPO / "data" / "overnight_queue" / "queue.json"
CPU_QUEUE = REPO / "data" / "remote_cpu_queue" / "queue.json"

RUNNER_HEARTBEAT_PATHS = {
    "gpu_runner_0": REPO / "data" / "overnight_queue" / "heartbeat.gpu_runner_0.json",
    "cpu_runner_0": REPO / "data" / "remote_cpu_queue" / "heartbeat.cpu_runner_0.json",
}
# Also check generic heartbeat.json fallbacks
RUNNER_HEARTBEAT_FALLBACKS = {
    "gpu_runner_0": REPO / "data" / "overnight_queue" / "heartbeat.json",
    "cpu_runner_0": REPO / "data" / "remote_cpu_queue" / "heartbeat.json",
}
EVENT_OUTCOMES_DIR = REPO / "data" / "event_outcomes"
RUNNER_LOGS_DIR = REPO / "data"

POLL_INTERVAL_S = 30


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> dict | list | None:
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def _queue_entries(queue_path: Path) -> list[dict]:
    """Load a queue.json and return the experiments list."""
    doc = _load_json(queue_path)
    if not isinstance(doc, dict):
        return []
    exps = doc.get("experiments")
    if not isinstance(exps, list):
        return []
    out = []
    for e in exps:
        if not isinstance(e, dict):
            continue
        out.append({
            "name": e.get("name"),
            "status": e.get("status"),
            "queued_at": e.get("queued_at") or e.get("created_at"),
            "started_at": e.get("started_at"),
        })
    return out


def _runner_state_from_heartbeat(runner_id: str) -> dict:
    """Read runner heartbeat from the queue-local heartbeat JSON file."""
    path = RUNNER_HEARTBEAT_PATHS.get(runner_id)
    fallback = RUNNER_HEARTBEAT_FALLBACKS.get(runner_id)

    doc: dict | None = None
    for p in [path, fallback]:
        if p is not None:
            result = _load_json(p)
            if isinstance(result, dict):
                doc = result
                break

    if not isinstance(doc, dict):
        return {"alive": False, "error": "heartbeat_missing"}

    return {
        "pid": doc.get("pid"),
        "heartbeat_ts": doc.get("ts"),
        "status": doc.get("status"),
        "current": doc.get("current"),
        "alive": True,
        "runner_id": doc.get("runner_id"),
    }


def _recent_verdicts(n: int = 10) -> list[dict]:
    """Pull the most recent n verdicts from queue.json completed entries.

    Looks at both overnight_queue and remote_cpu_queue for entries with
    status in (completed, failed, killed) and an ended_at timestamp.
    Returns the n most recently-ended entries sorted newest-last.
    """
    all_entries: list[dict] = []
    for queue_name, queue_path in [
        ("overnight_queue", OVERNIGHT_QUEUE),
        ("remote_cpu_queue", CPU_QUEUE),
    ]:
        doc = _load_json(queue_path)
        if not isinstance(doc, dict):
            continue
        exps = doc.get("experiments") or []
        for e in exps:
            if not isinstance(e, dict):
                continue
            status = e.get("status")
            if status not in ("completed", "failed", "killed", "inconclusive"):
                continue
            ended_at = e.get("ended_at") or e.get("completed_at")
            all_entries.append({
                "name": e.get("name"),
                "verdict": status,
                "queue": queue_name,
                "ended_at": ended_at,
                "elapsed_s": e.get("elapsed_s"),
                "verdict_msg": e.get("verdict_msg") or e.get("notes"),
            })

    # Sort by ended_at, newest last; take last n
    def _sort_key(e: dict) -> str:
        return e.get("ended_at") or ""

    all_entries.sort(key=_sort_key)
    return all_entries[-n:]



# ---------------------------------------------------------------------------
# Core snapshot
# ---------------------------------------------------------------------------

def build_snapshot() -> dict:
    now_iso = datetime.now().isoformat(timespec="seconds")

    snapshot = {
        "snapshot_ts": now_iso,
        "queues": {
            "overnight_queue": _queue_entries(OVERNIGHT_QUEUE),
            "remote_cpu_queue": _queue_entries(CPU_QUEUE),
        },
        "runners": {
            "gpu_runner_0": _runner_state_from_heartbeat("gpu_runner_0"),
            "cpu_runner_0": _runner_state_from_heartbeat("cpu_runner_0"),
        },
        "recent_verdicts": _recent_verdicts(10),
        "recent_runner_log_tail": "",
    }

    return snapshot


def write_atomic(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    os.replace(tmp, path)


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main() -> None:
    print(
        f"[remote_state_emitter] starting; writing to {OUTPUT}; poll={POLL_INTERVAL_S}s",
        flush=True,
    )
    while True:
        try:
            snap = build_snapshot()
            write_atomic(OUTPUT, snap)
        except Exception as e:
            # Never crash — just log and keep going
            print(f"[remote_state_emitter] ERROR: {e}", flush=True)
        time.sleep(POLL_INTERVAL_S)


if __name__ == "__main__":
    main()
