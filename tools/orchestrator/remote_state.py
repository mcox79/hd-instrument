"""Local consumer API for the hd-instrument remote-bridge cache.

Sub-agents and orchestrator tools read remote queue / runner / verdict state
from a local JSON file (data/remote_state_cache.json) that heartbeat_watchdog
refreshes via SCP every 30s.  This eliminates per-call SSH overhead for reads.

Usage::

    from tools.orchestrator.remote_state import (
        get_queue_state,
        get_runner_state,
        get_recent_verdicts,
        is_stale,
    )

    # Check freshness before trusting the data
    if is_stale():
        # fall back to direct SSH or raise a warning
        ...

    pending = [e for e in get_queue_state("overnight_queue") if e["status"] == "pending"]
    runner  = get_runner_state("gpu_runner_0")
    verdicts = get_recent_verdicts(n=5)

Fallback contract
-----------------
Every function returns an empty / falsy value ([], {}, True for is_stale) when
the cache file is missing, unreadable, or malformed.  Callers that care about
freshness should check is_stale() first and fall back to direct SSH if True.
"""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_REPO = Path(__file__).resolve().parents[2]
CACHE_PATH = _REPO / "data" / "remote_state_cache.json"

# Age thresholds
WARN_AGE_S: float = 120.0   # is_stale() returns True above this
HARD_AGE_S: float = 300.0   # cache is definitely broken above this


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_cache() -> dict[str, Any]:
    """Read and parse the cache file. Returns {} on any failure."""
    try:
        return json.loads(CACHE_PATH.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}


def _cache_age_s() -> float | None:
    """Return age in seconds of the cache snapshot_ts field.

    Returns None if the file is missing or the timestamp is unparseable.
    """
    doc = _load_cache()
    ts_str = doc.get("snapshot_ts")
    if not ts_str:
        return None
    try:
        ts = datetime.fromisoformat(ts_str)
        # Make offset-naive for comparison
        if ts.tzinfo is not None:
            ts = ts.replace(tzinfo=None)
        return (datetime.now() - ts).total_seconds()
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_queue_state(queue_name: str) -> list[dict[str, Any]]:
    """Return queue entries for the named queue.

    Args:
        queue_name: one of "overnight_queue" or "remote_cpu_queue".

    Returns:
        List of dicts with keys: name, status, queued_at, started_at.
        Empty list if cache is missing, malformed, or queue not found.
    """
    doc = _load_cache()
    queues = doc.get("queues")
    if not isinstance(queues, dict):
        return []
    q = queues.get(queue_name)
    if not isinstance(q, list):
        return []
    return q


def get_runner_state(runner_name: str) -> dict[str, Any]:
    """Return runner state dict for the named runner.

    Args:
        runner_name: e.g. "gpu_runner_0" or "cpu_runner_0".

    Returns:
        Dict with keys: pid, heartbeat_ts, status, current, alive.
        Empty dict if cache is missing, malformed, or runner not found.
    """
    doc = _load_cache()
    runners = doc.get("runners")
    if not isinstance(runners, dict):
        return {}
    r = runners.get(runner_name)
    if not isinstance(r, dict):
        return {}
    return r


def get_recent_verdicts(n: int = 10) -> list[dict[str, Any]]:
    """Return the most recent n verdicts from the cache.

    Args:
        n: maximum number of verdicts to return (default 10).

    Returns:
        List of verdict dicts, newest last.
        Empty list if cache is missing or malformed.
    """
    doc = _load_cache()
    rv = doc.get("recent_verdicts")
    if not isinstance(rv, list):
        return []
    return rv[-n:]


def is_stale(max_age_s: float = WARN_AGE_S) -> bool:
    """Return True if the cache is older than max_age_s seconds.

    Also returns True if the cache file is missing or its timestamp is
    unparseable — callers should fall back to direct SSH in those cases.

    Args:
        max_age_s: staleness threshold in seconds (default 120s).
    """
    age = _cache_age_s()
    if age is None:
        return True  # missing or broken
    return age > max_age_s


def snapshot_ts() -> str | None:
    """Return the ISO timestamp of the current cache snapshot, or None."""
    doc = _load_cache()
    return doc.get("snapshot_ts")


def queue_pending_count(queue_name: str) -> int:
    """Convenience: count pending entries in a queue."""
    return sum(
        1 for e in get_queue_state(queue_name)
        if e.get("status") in ("pending", "running")
    )


def any_runner_active() -> bool:
    """Return True if any runner has status == 'running' in the cache."""
    doc = _load_cache()
    runners = doc.get("runners") or {}
    for r in runners.values():
        if isinstance(r, dict) and r.get("status") == "running":
            return True
    return False


# ---------------------------------------------------------------------------
# CLI self-test (python -m tools.orchestrator.remote_state)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    age = _cache_age_s()
    stale = is_stale()
    snap_ts = snapshot_ts()

    print(f"cache path : {CACHE_PATH}")
    print(f"exists     : {CACHE_PATH.exists()}")
    print(f"snapshot_ts: {snap_ts}")
    print(f"age_s      : {age:.1f}" if age is not None else "age_s      : N/A")
    print(f"is_stale   : {stale}  (threshold={WARN_AGE_S}s)")
    print()

    for q in ("overnight_queue", "remote_cpu_queue"):
        entries = get_queue_state(q)
        pending = [e for e in entries if e.get("status") in ("pending", "running")]
        print(f"{q}: {len(entries)} entries, {len(pending)} pending/running")

    print()
    for r in ("gpu_runner_0", "cpu_runner_0"):
        rs = get_runner_state(r)
        print(f"{r}: status={rs.get('status')} current={rs.get('current')} alive={rs.get('alive')}")

    print()
    verdicts = get_recent_verdicts(5)
    print(f"recent_verdicts (last 5): {len(verdicts)} entries")
    for v in verdicts:
        print(f"  {v.get('name')} -> {v.get('verdict')}")
