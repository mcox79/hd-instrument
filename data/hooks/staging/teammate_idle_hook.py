"""TeammateIdle hook — built-in auto-wake mechanism for Agent Teams.

Anthropic Claude Code fires this hook when a teammate is about to go idle.
Exit code 2 = send feedback to keep the teammate working (auto-pulse).
Exit code 0 = let the teammate go idle (normal end-of-work).

This replaces our hand-rolled keepalive cycle (USER 2026-06-21 migration). The hook
decides whether to keep the teammate active based on:
- Pending tasks in the shared task list assigned to this teammate
- Open routings in notes/ addressed to this teammate
- Recent inbox events not yet processed

If anything is pending, exit 2 with a brief hint. If nothing pending, exit 0
to let teammate idle (will auto-wake on next TaskCreated or SendMessage).
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

REPO = Path(r"D:\AI\hd-instrument")
NOTES = REPO / "notes"

# Stdin = hook input JSON per Anthropic spec
try:
    payload = json.load(sys.stdin)
except json.JSONDecodeError:
    sys.exit(0)

teammate_name = payload.get("teammate_name") or payload.get("agent_name") or ""
if not teammate_name:
    sys.exit(0)

role = teammate_name.lower()
# Map teammate names to role keys (e.g., "skunkworks-1" -> "skunkworks")
for known in ("research", "skunkworks", "exp_dev", "orchestrator", "testbed"):
    if known in role:
        role = known
        break
else:
    sys.exit(0)


def addressed_notes_count(role: str, since_min: int = 30) -> int:
    """Count notes addressed to this role filed in the last N min."""
    if not NOTES.is_dir():
        return 0
    cutoff = time.time() - since_min * 60
    count = 0
    try:
        with os.scandir(NOTES) as it:
            for entry in it:
                if not entry.name.endswith(".md"):
                    continue
                # Skip own outgoing
                if entry.name.startswith(f"{role}_"):
                    continue
                # Match addressed-to-role or broadcast
                name_lower = entry.name.lower()
                if (f"_to_{role}_" in name_lower) or ("_to_all_" in name_lower) or ("_cc_all_" in name_lower):
                    try:
                        if entry.stat().st_mtime > cutoff:
                            count += 1
                    except OSError:
                        pass
    except OSError:
        pass
    return count


pending = addressed_notes_count(role, since_min=60)
if pending > 0:
    msg = f"Pending inbox: {pending} addressed note(s) in last 60min. Process them + continue your in-flight work."
    print(msg, file=sys.stderr)
    sys.exit(2)  # Keep teammate working

# Nothing pending — let teammate go idle.
sys.exit(0)
