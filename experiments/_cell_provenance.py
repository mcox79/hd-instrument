"""Shared metrics-PROVENANCE fields for experiment cells (Skunkworks metrics-provenance gate, 2026-06-17).

Makes "is this metrics.json the output of the run I think, via the path/method I require?" a FIELD CHECK, not an
inference. Every cell emits the same structured block so the cert gate + the dispatch one-true-test read it programmatically
(ending the stale / wrong-method / wrong-mode remote-vs-local inference that bit the team today).

Fields (the cert-owner 4-point gate + commit bonus):
  run_mode        -- full | smoke                                  (MODE; GATE-0)
  branch_path     -- which code path executed (cell-specific str)  (PATH)
  metrics_source  -- method that produced the numbers              (METHOD; METHOD-GATE)
  run_started_utc -- iso8601 at run start                          (IDENTITY/FRESHNESS: is this file from THIS run?)
  cell_commit     -- git short hash of the running cell            (which CODE produced it)

Deterministic; no LLM. ASCII-only.
"""
from __future__ import annotations
import subprocess
from datetime import datetime, timezone
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]


def now_utc() -> str:
    """iso8601 UTC timestamp; capture at run start for run_started_utc."""
    return datetime.now(timezone.utc).isoformat()


def cell_commit() -> str:
    """Best-effort git short hash of the running cell (on the remote = the commit the runner actually pulled)."""
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(_REPO),
                              capture_output=True, text=True, timeout=5).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def provenance_fields(run_mode: str, branch_path: str, metrics_source: str, run_started_utc: str) -> dict:
    """The structured provenance block to spread into a cell's metrics dict."""
    return {"run_mode": run_mode, "branch_path": branch_path, "metrics_source": metrics_source,
            "run_started_utc": run_started_utc, "cell_commit": cell_commit()}
