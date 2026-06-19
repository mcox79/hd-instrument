"""Append-only JSONL event log for cross-session context recovery.

Usage:
    from hdlab.session_log import log_event
    log_event("experiment_started", name="r10_K128", queue="overnight_queue")
    log_event("observation", msg="R10 K=256 gap = +0.193")

Each call appends one JSON line to data/session_events.jsonl (relative to repo
root). Writes that fail are reported on stderr but never raise — event logging
must not break the calling experiment.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


_REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PATH = Path(os.environ.get(
    "HDLAB_SESSION_EVENTS",
    str(_REPO_ROOT / "data" / "session_events.jsonl"),
))


def log_event(event_type: str, *, path: Path | str | None = None, **fields: Any) -> dict:
    """Append one event to the session log. Returns the event dict (also on write failure)."""
    p = Path(path) if path else DEFAULT_PATH
    event = {
        "ts": fields.pop("ts", None) or datetime.now().isoformat(timespec="seconds"),
        "type": event_type,
        **fields,
    }
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(event, ensure_ascii=False)
        with open(p, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        print(f"[session_log] write failed ({type(e).__name__}: {e})", file=sys.stderr)
    return event
