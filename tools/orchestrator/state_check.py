"""Orchestrator state-check helper — one-shot state summary.

Replaces the main-thread pattern of:
  - Read data/local_dashboard_snapshot.json
  - Grep queue_pending_count + runner heartbeats
  - Read notes/substrate_capability_map.md head for cap_map version
  - Synthesize a chat-friendly state line

Usage::

    python tools/orchestrator/state_check.py

Prints one line to stdout:

    [HH:MM] cap_map v157 | gpu_q:1 cpu_q:0 local_q:2 | gpu:RUN cpu:DEAD local:IDLE | last_verdict 4m ago: <name>

Queue depths and runner states are read from data/remote_state_cache.json
(populated by heartbeat_watchdog's SCP pull every 30s) when that cache is
fresh (< 120s old).  Falls back to local_dashboard_snapshot.json when the
bridge cache is stale or missing.  This eliminates SSH calls for reads.

Exits 0 always (orchestrator parses the output line; even DEGRADED state should not break the orchestrator's flow).
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DASHBOARD = REPO / "data" / "local_dashboard_snapshot.json"
CAP_MAP = REPO / "notes" / "substrate_capability_map.md"
STATUS_LOG = REPO / "data" / "orchestrator_status_log.jsonl"

# Remote-bridge consumer API — prefer over direct SSH for reads
try:
    import importlib.util as _ilu
    _rs_spec = _ilu.spec_from_file_location(
        "remote_state",
        Path(__file__).parent / "remote_state.py",
    )
    _rs_mod = _ilu.module_from_spec(_rs_spec)  # type: ignore[arg-type]
    _rs_spec.loader.exec_module(_rs_mod)  # type: ignore[union-attr]
    _rs_get_queue_state = _rs_mod.get_queue_state
    _rs_get_runner_state = _rs_mod.get_runner_state
    _rs_is_stale = _rs_mod.is_stale
    _REMOTE_STATE_AVAILABLE = True
except Exception:
    _REMOTE_STATE_AVAILABLE = False


def _safe_read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _minutes_ago(iso: str | None) -> float | None:
    if not iso:
        return None
    try:
        ts = datetime.fromisoformat(iso.replace("Z", ""))
        if ts.tzinfo is not None:
            ts = ts.replace(tzinfo=None)
        return (datetime.now() - ts).total_seconds() / 60.0
    except Exception:
        return None


def _runner_state(runner: dict, stale_min: float = 5.0) -> str:
    """Return one-token runner state: RUN | IDLE | DEAD | STALE."""
    if not runner:
        return "DEAD"
    hb = runner.get("heartbeat") or {}
    status = hb.get("status") or runner.get("status")
    mins = _minutes_ago(hb.get("ts"))
    if status == "running":
        if mins is not None and mins > stale_min:
            return "STALE"
        return "RUN"
    if status in ("idle", "waiting"):
        return "IDLE"
    if mins is None or mins > 60:
        return "DEAD"
    return (status or "?").upper()


def _cap_map_version() -> str:
    """Find the latest `## v<N> update` header in cap_map (file is ~600 KB).

    Strategy: read the file once, scan for all `## v<N> update` markers, take max.
    Falls back to `v?` if no markers are found.
    """
    try:
        text = CAP_MAP.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "v?"
    # Match three cap_map header formats:
    #   1. Older: "## v<N> update"
    #   2. Cycle format: "## Cycle <N> ... -- v<M>"
    #   3. Current (2026-05-24+): "## v<N> - (date) ..." e.g. "## v194 - (2026-05-24) ..."
    versions: list[int] = []
    versions += [int(m.group(1)) for m in re.finditer(r"^##\s+v(\d+)\s+update", text, flags=re.MULTILINE)]
    versions += [int(m.group(1)) for m in re.finditer(r"^##\s+Cycle\s+\d+.*?--\s+v(\d+)\s*$", text, flags=re.MULTILINE)]
    versions += [int(m.group(1)) for m in re.finditer(r"^##\s+v(\d+)\s+[-–—]+\s+", text, flags=re.MULTILINE)]
    if not versions:
        versions = [int(m.group(1)) for m in re.finditer(r"\bv(\d+)\b", text)]
    return f"v{max(versions)}" if versions else "v?"


def _last_verdict() -> tuple[str, float | None]:
    """Read tail of status log; find newest verdict line; return (name, mins_ago)."""
    if not STATUS_LOG.exists():
        return ("?", None)
    try:
        lines = STATUS_LOG.read_text(encoding="utf-8", errors="replace").strip().splitlines()
    except OSError:
        return ("?", None)
    for line in reversed(lines):
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        if o.get("event_kind") != "verdict":
            continue
        summary = (o.get("summary") or "").split(":")[0].split(" — ")[0].strip()
        mins = _minutes_ago(o.get("ts"))
        return (summary or "?", mins)
    return ("?", None)


def _queue_depths(d: dict) -> dict[str, int | None]:
    # Prefer remote_state bridge (local file, no SSH) when cache is fresh
    if _REMOTE_STATE_AVAILABLE and not _rs_is_stale():
        gpu_entries = _rs_get_queue_state("overnight_queue")
        cpu_entries = _rs_get_queue_state("remote_cpu_queue")
        gpu_count = sum(1 for e in gpu_entries if e.get("status") in ("pending", "running"))
        cpu_count = sum(1 for e in cpu_entries if e.get("status") in ("pending", "running"))
        # local_cpu_queue is not in the remote bridge (it is local); read from snapshot
        local = d.get("local_cpu") or d.get("cpu_local") or {}
        return {
            "gpu": gpu_count,
            "cpu": cpu_count,
            "local": local.get("queue_pending_count"),
            "_source": "remote_bridge",
        }
    # Fallback: read from local dashboard snapshot
    gpu = d.get("gpu") or {}
    cpu = d.get("cpu") or {}
    local = d.get("local_cpu") or d.get("cpu_local") or {}
    return {
        "gpu": gpu.get("queue_pending_count"),
        "cpu": cpu.get("queue_pending_count"),
        "local": local.get("queue_pending_count"),
        "_source": "snapshot_fallback",
    }


def _runner_state_from_bridge(runner_id: str) -> str | None:
    """Return runner state token from remote_state cache, or None if unavailable."""
    if not _REMOTE_STATE_AVAILABLE or _rs_is_stale():
        return None
    r = _rs_get_runner_state(runner_id)
    if not r:
        return None
    status = (r.get("status") or "").lower()
    hb_ts = r.get("heartbeat_ts")
    alive = r.get("alive", False)
    if not alive:
        return "DEAD"
    if status == "running":
        # Check heartbeat age for STALE
        if hb_ts:
            try:
                dt = datetime.fromisoformat(hb_ts)
                if dt.tzinfo is not None:
                    dt = dt.replace(tzinfo=None)
                mins = (datetime.now() - dt).total_seconds() / 60.0
                if mins > 5.0:
                    return "STALE"
            except Exception:
                pass
        return "RUN"
    if status in ("idle", "waiting"):
        return "IDLE"
    return (status or "?").upper()


def main() -> int:
    d = _safe_read_json(DASHBOARD)
    ts = datetime.now().strftime("%H:%M")

    cap_v = _cap_map_version()
    depths = _queue_depths(d)

    # Prefer remote bridge for runner states; fall back to snapshot
    gpu_state = _runner_state_from_bridge("gpu_runner_0") or _runner_state(d.get("gpu") or {})
    cpu_state = _runner_state_from_bridge("cpu_runner_0") or _runner_state(d.get("cpu") or {})
    local_state = _runner_state(d.get("local_cpu") or d.get("cpu_local") or {})

    name, mins_ago = _last_verdict()
    verdict_seg = (
        f"last_verdict {mins_ago:.0f}m ago: {name}"
        if mins_ago is not None
        else "last_verdict ?"
    )

    def _fmt(v: int | None) -> str:
        return "?" if v is None else str(v)

    source_tag = depths.get("_source", "snapshot_fallback")
    src_label = "" if source_tag == "remote_bridge" else " [snap]"

    line = (
        f"[{ts}] cap_map {cap_v} | "
        f"gpu_q:{_fmt(depths['gpu'])} cpu_q:{_fmt(depths['cpu'])} local_q:{_fmt(depths['local'])}{src_label} | "
        f"gpu:{gpu_state} cpu:{cpu_state} local:{local_state} | "
        f"{verdict_seg}"
    )
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
