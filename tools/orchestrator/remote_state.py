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
import re
import subprocess
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


# ---------------------------------------------------------------------------
# Remote-first metrics.json fetch (verdict_handler N-mismatch ceiling-fix)
# ---------------------------------------------------------------------------
#
# Local data/exp_<name>/metrics.json is frequently STALE relative to the
# production run that landed on marsh@home. Concrete pattern (2026-05-27,
# wave14_saddle_cascade_plateau_v6_n4096_gpu): local recorded N=512 SMOKE
# 2.64s on cpu, remote recorded N=4096 FULL 6821s on cuda HARD_PASS 5/5.
# Verdict_handler trusted local and emitted 78+ false label-vs-honest
# catches in a single day.
#
# Fix: every metrics read goes through get_metrics(name) which fetches from
# marsh@home first via SSH and only falls back to local on remote failure.
# A 'source' field is injected at the top of the returned dict so the
# caller can distinguish remote (authoritative) from local (last-resort).
# See notes/verdict_handler_remote_metrics_fix_2026-05-27.md.

# Whitelist of characters allowed in an experiment anchor name. Mirrors the
# queue_add.py convention. Prevents shell-meta injection into the SSH command.
_NAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")

# ssh marsh@home is configured in the user's ~/.ssh/config and is the same
# alias used by tools/audit_n_mismatch.py and tools/queue_add.py.
_SSH_TARGET = "marsh@home"
_REMOTE_METRICS_PATH_TPL = r"C:\dev\hd-instrument\data\exp_{name}\metrics.json"


def _ssh_type_remote_metrics(name: str, timeout_s: float = 12.0) -> str | None:
    """Run `ssh marsh@home type <remote metrics path>` and return raw stdout.

    Returns None on any failure (timeout, non-zero exit, parse error, missing
    file). Callers fall back to local on None.

    SH-4 note: remote runner may write to data/exp_exp_<name>/ when the queue
    entry name begins with 'exp_' (see _seed_checkpoint.get_output_dir).
    Handled here by trying canonical first, then double-prefix. Testbed
    2026-07-03 fleet audit.
    """
    if not _NAME_RE.match(name):
        return None
    remote_paths = [
        _REMOTE_METRICS_PATH_TPL.format(name=name),
        _REMOTE_METRICS_PATH_TPL.format(name="exp_" + name),
    ]
    for candidate in remote_paths:
        raw = _ssh_type_remote_metrics_one(candidate, timeout_s)
        if raw is not None:
            return raw
    return None


def _ssh_type_remote_metrics_one(remote_path: str, timeout_s: float) -> str | None:
    """Single-path SSH type; returns raw JSON body or None."""
    # ssh -T disables pseudo-tty (popup-fix per testbed 2026-06-28: prevents
    # remote conhost.exe allocation per call; daemon polls frequently).
    cmd = ["ssh", "-T", _SSH_TARGET, f"type {remote_path}"]
    # CREATE_NO_WINDOW prevents ssh from popping a console window per call
    # (USER 2026-06-28 popup-audit: any daemon calling this would flash a window)
    _no_window = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
    try:
        out = subprocess.check_output(
            cmd,
            stderr=subprocess.DEVNULL,
            timeout=timeout_s,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=_no_window,
        )
    except Exception:
        return None
    # Strip any SSH banner / pq-warning lines that come before the JSON body.
    # The JSON object starts at the first '{' on a line by itself or inline.
    idx = out.find("{")
    if idx < 0:
        return None
    return out[idx:]


def get_remote_metrics(name: str) -> dict[str, Any] | None:
    """Fetch data/exp_<name>/metrics.json from marsh@home over SSH.

    Returns parsed JSON dict on success, None on any failure. The returned
    dict has '_source': 'remote' injected so the caller can confirm the
    read crossed the wire (vs. quietly falling back to a stale local copy).
    """
    raw = _ssh_type_remote_metrics(name)
    if not raw:
        return None
    try:
        doc = json.loads(raw)
    except Exception:
        return None
    if not isinstance(doc, dict):
        return None
    doc["_source"] = "remote"
    return doc


def get_local_metrics(name: str) -> dict[str, Any] | None:
    """Read data/exp_<name>/metrics.json from the local repo. Returns None
    if the file is missing, unreadable, or not a JSON object.

    SH-4 fallback: also tries data/exp_exp_<name>/metrics.json when canonical
    is missing (root cause: _seed_checkpoint.get_output_dir when queue entry
    begins with 'exp_'). Testbed 2026-07-03 fleet audit."""
    if not _NAME_RE.match(name):
        return None
    candidates = [
        _REPO / "data" / f"exp_{name}" / "metrics.json",
        _REPO / "data" / f"exp_exp_{name}" / "metrics.json",
    ]
    for path in candidates:
        try:
            doc = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        if not isinstance(doc, dict):
            continue
        doc["_source"] = "local"
        return doc
    return None


def get_metrics(name: str, *, prefer_remote: bool = True) -> dict[str, Any] | None:
    """Remote-first metrics.json fetch for verdict_handler / strategy / audit.

    Args:
        name: experiment anchor (e.g. 'wave14_saddle_cascade_plateau_v6_n4096_gpu').
              Must match `_NAME_RE` -- alnum, dot, underscore, dash only.
        prefer_remote: if True (default) try SSH first, fall back to local on
                       failure. If False, read local directly (legacy path).

    Returns:
        Parsed metrics dict with '_source' field set to 'remote' or 'local';
        None if both reads fail or name is invalid.

    Notes:
        Remote fetch uses `ssh marsh@home type <C:\\dev\\hd-instrument\\data\\
        exp_<name>\\metrics.json>` with a 12s timeout. Local fallback reads
        d:/AI/hd-instrument/data/exp_<name>/metrics.json directly.
    """
    if prefer_remote:
        doc = get_remote_metrics(name)
        if doc is not None:
            return doc
    return get_local_metrics(name)


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

    # Optional: test the remote-first metrics fetch on a CLI-supplied anchor.
    import sys as _sys
    if len(_sys.argv) > 1:
        anchor = _sys.argv[1]
        print()
        print(f"=== get_metrics({anchor!r}) ===")
        m = get_metrics(anchor)
        if m is None:
            print("  result: None (both remote and local reads failed)")
        else:
            cfg = m.get("config") or {}
            summ = m.get("summary") or {}
            print(f"  _source        : {m.get('_source')}")
            print(f"  verdict        : {m.get('verdict')}")
            print(f"  config.mode    : {cfg.get('mode')}")
            print(f"  config.N       : {cfg.get('N')}")
            print(f"  config.device  : {cfg.get('device')}")
            print(f"  summary.N      : {summ.get('N')}")
            print(f"  summary.seeds  : {summ.get('seeds')}")
            print(f"  elapsed_s      : {m.get('elapsed_s')}")
