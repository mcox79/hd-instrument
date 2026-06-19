"""Orchestrator state layer: in-flight dispatch tracking + structured status logging.

This module is the single owner of:
  - data/orchestrator_in_flight.json   (what sub-agents are running right now)
  - data/orchestrator_status_log.jsonl (append-only event log, dashboard reads this)

All writes are atomic (.tmp + os.replace) for NTFS safety.

Quick usage::

    from tools.orchestrator.state import (
        log_event,
        dispatch_with_log,
        clear_dispatch_with_log,
        log_dashboard_event,
        # in-flight primitives (backward compat)
        record_dispatch,
        clear_dispatch,
        clear_all_dispatches,
        list_dispatches,
    )

    # Structured dispatch (preferred — auto-logs dispatched + returned)
    dispatch_id = dispatch_with_log(
        role="research",
        model="claude-sonnet-4-6",
        summary="Sagawa-Ueda drill on reservoir computing",
        expected_minutes=20,
    )
    # ... agent runs ...
    clear_dispatch_with_log(dispatch_id, outcome="delivered", decision_file="notes/research_sagawa_2026-05-23.md")

    # Ad-hoc event (verdict, audit, etc.)
    log_event("verdict", "CROOKS_PASS FULL — 3/3 noisy cells pass", substrate_product="Cap 1 SLA widens")
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import uuid
import warnings
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).parents[2]
_DATA_DIR = _REPO_ROOT / "data"
_IN_FLIGHT_FILE = _DATA_DIR / "orchestrator_in_flight.json"
_STATUS_LOG_FILE = _DATA_DIR / "orchestrator_status_log.jsonl"


# ---------------------------------------------------------------------------
# Internal helpers — atomic file I/O
# ---------------------------------------------------------------------------

def _atomic_write(dest: Path, text: str) -> None:
    """Write *text* to *dest* atomically via a sibling .tmp file + os.replace."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".tmp")
    try:
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, dest)
    except OSError:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def _atomic_append_jsonl(dest: Path, obj: dict) -> None:
    """Append one JSON line to *dest* atomically.

    Strategy: read existing content + append new line + write whole file.
    This is safe on NTFS where O_APPEND is not reliably atomic for concurrent
    writers; the read-modify-write under os.replace gives us the same
    last-writer-wins guarantee as the in-flight JSON file.

    For the status log (low-frequency writes, never concurrent), this is fine.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n"
    try:
        existing = dest.read_text(encoding="utf-8") if dest.exists() else ""
    except OSError:
        existing = ""
    _atomic_write(dest, existing + line)


# ---------------------------------------------------------------------------
# In-flight dispatch tracking (originally in in_flight.py)
# ---------------------------------------------------------------------------

def _read_in_flight() -> dict:
    try:
        text = _IN_FLIGHT_FILE.read_text(encoding="utf-8")
        d = json.loads(text)
        if not isinstance(d, dict):
            return {"dispatches": []}
        d.setdefault("dispatches", [])
        return d
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {"dispatches": []}


def _write_in_flight(data: dict) -> None:
    _atomic_write(_IN_FLIGHT_FILE, json.dumps(data, indent=2, ensure_ascii=False))


def record_dispatch(
    role: str,
    model: str,
    summary: str,
    expected_minutes: float = 15.0,
) -> str:
    """Add a new in-flight dispatch entry. Returns the dispatch id (uuid4)."""
    dispatch_id = str(uuid.uuid4())
    now = datetime.now().astimezone()
    expected_done = now + timedelta(minutes=expected_minutes)
    entry = {
        "id": dispatch_id,
        "started_at": now.isoformat(timespec="seconds"),
        "role": role,
        "model": model,
        "summary": summary,
        "expected_done_at": expected_done.isoformat(timespec="seconds"),
    }
    data = _read_in_flight()
    data["dispatches"].append(entry)
    _write_in_flight(data)
    return dispatch_id


def clear_dispatch(dispatch_id: str) -> bool:
    """Remove a dispatch entry by id. Returns True if found and removed."""
    data = _read_in_flight()
    before = len(data["dispatches"])
    data["dispatches"] = [d for d in data["dispatches"] if d.get("id") != dispatch_id]
    if len(data["dispatches"]) < before:
        _write_in_flight(data)
        return True
    return False


def clear_all_dispatches() -> int:
    """Clear all in-flight entries (e.g. at orchestrator startup). Returns count removed."""
    data = _read_in_flight()
    count = len(data["dispatches"])
    data["dispatches"] = []
    _write_in_flight(data)
    return count


def list_dispatches() -> list[dict]:
    """Return current in-flight dispatch list (copy)."""
    return list(_read_in_flight().get("dispatches", []))


# ---------------------------------------------------------------------------
# Status log — log_event and friends
# ---------------------------------------------------------------------------

def log_event(event_kind: str, summary: str, **fields: Any) -> None:
    """Append a single JSONL entry to data/orchestrator_status_log.jsonl.

    Standard fields auto-populated:
      ts          ISO-8601 local timestamp (always set)
      event_kind  the event category string
      summary     terse human-readable description

    Optional keyword fields you can pass:
      sub_agents      list[str]  e.g. ["strategy:opus", "visibility:haiku"]
      outcome         str        one-line result summary
      substrate_product str      capability impact
      decision_file   str        path to the authoritative note for this event
      closure_flag    bool       True when a capability is being closed
      mechanism       str        research mechanism name
      p_estimate      float      probability estimate
      recommendation  str        action recommendation
      report          str        path to a report file
      dispatch_id     str        uuid of the associated sub-agent dispatch
      role            str        sub-agent role
      model           str        model ID used
      plain_language  str        1-2 sentence non-expert explanation of what this event means
      importance      str        one of: CRITICAL / HIGH / MEDIUM / LOW

    All other keyword args are passed through verbatim.
    """
    entry: dict[str, Any] = {
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "event_kind": event_kind,
        "summary": summary,
    }
    entry.update(fields)
    _atomic_append_jsonl(_STATUS_LOG_FILE, entry)


def dispatch_with_log(
    role: str,
    model: str,
    summary: str,
    expected_minutes: int = 15,
) -> str:
    """Record an in-flight dispatch AND write a sub_agent_dispatched status log entry.

    This is the preferred way to start a sub-agent from the orchestrator.
    Pair with clear_dispatch_with_log() when the agent returns.

    Returns the dispatch id (uuid4).
    """
    dispatch_id = record_dispatch(
        role=role,
        model=model,
        summary=summary,
        expected_minutes=float(expected_minutes),
    )
    log_event(
        "sub_agent_dispatched",
        summary,
        dispatch_id=dispatch_id,
        role=role,
        model=model,
        expected_minutes=expected_minutes,
    )
    return dispatch_id


def clear_dispatch_with_log(
    dispatch_id: str,
    outcome: str = "",
    decision_file: str = "",
) -> None:
    """Clear an in-flight dispatch AND write a sub_agent_returned status log entry.

    Args:
        dispatch_id:   The uuid returned by dispatch_with_log / record_dispatch.
        outcome:       One-line summary of what the agent produced/decided.
        decision_file: Path to the canonical note where the agent's full output lives.
    """
    clear_dispatch(dispatch_id)
    fields: dict[str, Any] = {"dispatch_id": dispatch_id}
    if outcome:
        fields["outcome"] = outcome
    if decision_file:
        fields["decision_file"] = decision_file
    log_event(
        "sub_agent_returned",
        outcome or f"dispatch {dispatch_id[:8]} returned",
        **fields,
    )


def log_dashboard_event(event_kind: str, **fields: Any) -> None:
    """Convenience wrapper for common orchestrator surface events.

    Accepted event_kind values (soft convention, not enforced):
      verdict       — experiment hypothesis accepted/rejected
      routing       — orchestrator made a routing decision
      queue_add     — experiment added to queue
      queue_change  — queue item status changed
      error         — orchestrator error or unexpected condition
      heartbeat     — periodic alive signal (no notable activity)
      meta_audit    — periodic self-audit completed
      audit_overdue — self-audit is late

    Optional enrichment kwargs (passed through to log_event):
      plain_language  str  1-2 sentence non-expert explanation of what this event means
      importance      str  one of: CRITICAL / HIGH / MEDIUM / LOW

    All kwargs forwarded to log_event.  'summary' is required as a kwarg
    or will default to the event_kind string.
    """
    summary = fields.pop("summary", event_kind)
    log_event(event_kind, summary, **fields)
