"""Cadence-signal emitter for the hd-instrument orchestrator.

Called by Windows Task Scheduler tasks (hd_orch_daily_research_drill,
hd_orch_daily_audit, hd_orch_scope_expansion) to write a signal line to
data/orchestrator_cadence_signal.jsonl.

dispatch.py polls this file and emits EVENT cadence_signal {kind, ts}
whenever a new line appears.  The orchestrator's event-handling table
routes cadence_signal to the appropriate sub-agent (research or audit).

Usage
-----
    python tools/orchestrator/emit_cadence_signal.py <signal_kind>

    signal_kind must be one of:
        research_drill_due
        audit_due
        scope_expansion_due

This script does NOT dispatch experiments.  The pause flag still gates
all exp_dev dispatches.  This is a routing-decision trigger only.

The script is idempotent — if the signal file already has a line with the
same kind written within the last 2 hours, it skips the write to prevent
duplicate signals from schtasks retry logic.
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SIGNAL_FILE = REPO / "data" / "orchestrator_cadence_signal.jsonl"
VALID_KINDS = frozenset({"research_drill_due", "audit_due", "scope_expansion_due"})
# Dedup window: skip write if same kind was written within this many seconds.
DEDUP_WINDOW_S = 7200  # 2 hours


def _load_recent(kind: str) -> float | None:
    """Return the timestamp (epoch seconds) of the most recent line with this
    kind, or None if no such line exists."""
    if not SIGNAL_FILE.exists():
        return None
    try:
        text = SIGNAL_FILE.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    latest: float | None = None
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("signal") == kind:
            ts_str = obj.get("ts", "")
            try:
                t = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                epoch = t.timestamp()
                if latest is None or epoch > latest:
                    latest = epoch
            except (ValueError, AttributeError):
                pass
    return latest


def main() -> int:
    if len(sys.argv) != 2:
        print(
            f"Usage: {sys.argv[0]} <signal_kind>",
            file=sys.stderr,
        )
        print(f"  Valid kinds: {sorted(VALID_KINDS)}", file=sys.stderr)
        return 2

    kind = sys.argv[1].strip()
    if kind not in VALID_KINDS:
        print(
            f"ERROR: unknown signal kind '{kind}'. "
            f"Must be one of: {sorted(VALID_KINDS)}",
            file=sys.stderr,
        )
        return 1

    # Dedup check.
    last_ts = _load_recent(kind)
    if last_ts is not None:
        age_s = time.time() - last_ts
        if age_s < DEDUP_WINDOW_S:
            print(
                f"[cadence] SKIP: signal '{kind}' already written "
                f"{age_s / 3600:.1f}h ago (dedup window {DEDUP_WINDOW_S / 3600:.0f}h)."
            )
            return 0

    # Ensure data directory exists.
    SIGNAL_FILE.parent.mkdir(parents=True, exist_ok=True)

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    record = {"signal": kind, "ts": now_iso}
    line = json.dumps(record, separators=(",", ":"))

    # Atomic append: write to .tmp then append by reopening (jsonl is append-only;
    # true atomic rename is not safe for append-only files on Windows).
    try:
        with open(SIGNAL_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
            f.flush()
    except OSError as e:
        print(f"[cadence] ERROR writing signal file: {e}", file=sys.stderr)
        return 1

    print(f"[cadence] OK: wrote signal '{kind}' at {now_iso} to {SIGNAL_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
