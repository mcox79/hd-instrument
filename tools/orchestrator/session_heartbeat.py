"""Per-session heartbeat writer.

Each long-running Claude Code session (orchestrator, research, testbed, cloud)
calls update_heartbeat() periodically to advertise that it is alive and what
it is currently doing. The dashboard reads these files via the poller and
renders per-session activity indicators.

File convention:
  data/session_heartbeat_<session>.json

Schema:
  {
    "session":        "testbed",        # session name
    "ts":             "2026-05-31T...", # last update (local ISO-8601)
    "current_focus":  "Tier 1a dashboard expansion",  # 1-line activity
    "last_event_ts":  "...",            # last status_log entry by this session
    "stale_after_s":  3600              # dashboard marks stale after this many sec
  }

Atomic writes via .tmp + os.replace so the dashboard never reads a partial file.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional


_REPO_ROOT = Path(__file__).parents[2]
_DATA_DIR = _REPO_ROOT / "data"

# Valid session names; dashboard expects exactly these four.
_VALID_SESSIONS = {"orchestrator", "research", "testbed", "cloud"}

# Default freshness window: dashboard marks a heartbeat "stale" if its ts is
# older than now - stale_after_s. 1 hour is generous for Claude Code sessions
# that may pause between user turns; cron-style runners would use a tighter
# window (e.g., 120s).
_DEFAULT_STALE_AFTER_S = 3600


def _heartbeat_path(session: str) -> Path:
    return _DATA_DIR / f"session_heartbeat_{session}.json"


def update_heartbeat(
    session: str,
    current_focus: str,
    last_event_ts: Optional[str] = None,
    stale_after_s: int = _DEFAULT_STALE_AFTER_S,
) -> None:
    """Write a fresh heartbeat for *session*.

    Args:
        session: One of "orchestrator", "research", "testbed", "cloud".
        current_focus: 1-line description of what this session is doing now.
        last_event_ts: ISO timestamp of the most recent status_log entry by
            this session (optional; used by dashboard to gauge productive work
            vs idle heartbeat).
        stale_after_s: How many seconds the dashboard should wait before
            marking this session stale. Default 3600 (1 hour); shorter for
            cron-style runners.
    """
    if session not in _VALID_SESSIONS:
        raise ValueError(
            f"session must be one of {sorted(_VALID_SESSIONS)}; got {session!r}"
        )
    if not current_focus or not isinstance(current_focus, str):
        raise ValueError("current_focus must be a non-empty string")

    entry = {
        "session": session,
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "current_focus": current_focus.strip()[:240],
        "last_event_ts": last_event_ts,
        "stale_after_s": int(stale_after_s),
    }

    path = _heartbeat_path(session)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        dir=str(path.parent), prefix=path.name + ".", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(entry, f, indent=2)
        os.replace(tmp_path, str(path))
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def read_heartbeat(session: str) -> Optional[dict]:
    """Read the most recent heartbeat for *session*, or None if missing.

    Used by the dashboard poller; not typically called by the session itself.
    """
    if session not in _VALID_SESSIONS:
        raise ValueError(
            f"session must be one of {sorted(_VALID_SESSIONS)}; got {session!r}"
        )
    path = _heartbeat_path(session)
    if not path.is_file():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        # Mid-write or corrupt; dashboard treats as missing this poll.
        return None


def read_all_heartbeats() -> dict[str, dict]:
    """Read every session heartbeat that exists. Returns {session: entry}."""
    out: dict[str, dict] = {}
    for s in _VALID_SESSIONS:
        entry = read_heartbeat(s)
        if entry is not None:
            out[s] = entry
    return out
