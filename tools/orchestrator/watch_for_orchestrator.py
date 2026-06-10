"""Stream new experiment completions + new notes-to-orchestrator as stdout events.

Designed to be wrapped by Claude Code's Monitor tool. Each new event emits one
line; the Monitor surfaces each line as a notification, including while the
agent is in the middle of another tool call.

Sources watched:
- Dashboard /api/snapshot recent_verdicts (home's GPU + CPU runners on the desktop)
- Dashboard /api/snapshot inbox_routings.recent_24h (notes addressed to orchestrator)
- Local FrameworkMPC queue.json (data/local_cpu_queue) for completed experiments here

Polls every POLL_INTERVAL_S, prints one line per new event, line-buffered.

Usage:
    python tools/orchestrator/watch_for_orchestrator.py
"""

from __future__ import annotations

import json
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LOCAL_QUEUE = ROOT / "data" / "local_cpu_queue" / "queue.json"
DASHBOARD_URL = "http://127.0.0.1:8765/api/snapshot"

POLL_INTERVAL_S = 15.0


def _now() -> str:
    return datetime.now().strftime("%H:%M:%S")


def _emit(line: str) -> None:
    sys.stdout.write(line + "\n")
    sys.stdout.flush()


def _fetch_snapshot() -> dict | None:
    try:
        with urllib.request.urlopen(DASHBOARD_URL, timeout=10.0) as r:
            return json.loads(r.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, OSError):
        return None


def _completed_from_verdicts(snap: dict | None) -> set[tuple[str, str]]:
    if not isinstance(snap, dict):
        return set()
    verdicts = snap.get("recent_verdicts")
    if not isinstance(verdicts, list):
        return set()
    out: set[tuple[str, str]] = set()
    for v in verdicts:
        if not isinstance(v, dict):
            continue
        name = v.get("name")
        outcome_at = v.get("outcome_at") or ""
        if isinstance(name, str) and name:
            out.add((name, outcome_at))
    return out


def _notes_from_inbox(snap: dict | None) -> dict[str, float]:
    if not isinstance(snap, dict):
        return {}
    inbox = snap.get("inbox_routings")
    if not isinstance(inbox, dict):
        return {}
    recent = inbox.get("recent_24h")
    if not isinstance(recent, list):
        return {}
    out: dict[str, float] = {}
    for entry in recent:
        if not isinstance(entry, dict):
            continue
        fn = entry.get("filename")
        mtime = entry.get("mtime") or 0.0
        if isinstance(fn, str) and fn:
            out[fn] = float(mtime)
    return out


def _local_queue_completed() -> set[tuple[str, str]]:
    if not LOCAL_QUEUE.is_file():
        return set()
    try:
        q = json.loads(LOCAL_QUEUE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return set()
    out: set[tuple[str, str]] = set()
    for e in q.get("experiments", []):
        if not isinstance(e, dict):
            continue
        if e.get("status") != "completed":
            continue
        name = e.get("name")
        ended = e.get("ended_at") or ""
        if isinstance(name, str) and name:
            out.add((name, ended))
    return out


def main() -> int:
    snap = _fetch_snapshot()
    seen_verdicts = _completed_from_verdicts(snap)
    seen_notes = _notes_from_inbox(snap)
    seen_local = _local_queue_completed()

    _emit(
        f"[{_now()}] WATCHER STARTED. baseline: "
        f"recent_verdicts={len(seen_verdicts)} "
        f"inbox_notes={len(seen_notes)} "
        f"local_cpu_completed={len(seen_local)}"
    )

    while True:
        try:
            time.sleep(POLL_INTERVAL_S)
            snap = _fetch_snapshot()

            if snap is None:
                _emit(f"[{_now()}] WARN: dashboard /api/snapshot unavailable")
            else:
                # Remote completions (home GPU + CPU)
                current_verdicts = _completed_from_verdicts(snap)
                new_verdicts = current_verdicts - seen_verdicts
                for name, ts in sorted(new_verdicts, key=lambda x: x[1]):
                    _emit(f"[{_now()}] NEW COMPLETION (home): {name}  at={ts}")
                seen_verdicts = current_verdicts

                # New notes
                current_notes = _notes_from_inbox(snap)
                for fn, mtime in current_notes.items():
                    if fn not in seen_notes:
                        _emit(f"[{_now()}] NEW NOTE: {fn}")
                    elif mtime > seen_notes[fn]:
                        _emit(f"[{_now()}] NOTE MODIFIED: {fn}")
                seen_notes = current_notes

            # Local FrameworkMPC completions
            current_local = _local_queue_completed()
            new_local = current_local - seen_local
            for name, ended in sorted(new_local, key=lambda x: x[1]):
                _emit(f"[{_now()}] NEW COMPLETION (local_cpu): {name}  ended={ended}")
            seen_local = current_local

        except KeyboardInterrupt:
            _emit(f"[{_now()}] WATCHER STOPPED")
            return 0
        except Exception as exc:
            _emit(f"[{_now()}] WATCHER ERROR: {type(exc).__name__}: {exc}")
            time.sleep(5.0)


if __name__ == "__main__":
    raise SystemExit(main())
