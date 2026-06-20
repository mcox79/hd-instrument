#!/usr/bin/env python3
"""Phase 1.1 Stop hook (Python rewrite; no jq dependency).

Per Director hardening proposal + Orchestrator runtime-owner spec + Skunkworks cert-integrity
input. STAGING ONLY -- not yet registered.

Purpose: prevent idle-one-by-one deaths by continuing the session when concrete work pending.

CRITICAL safety guards (load-bearing per Orchestrator + documented ~50min Stop-hook loop bug):
  GUARD 1: stop_hook_active flag honored FIRST (loop prevention; THE load-bearing safety gate)
  GUARD 2: HARD_CAP continuation counter (per-session; prevents runaway burn)
  GUARD 3: Concrete signal gate (only block on real pending work; not "always block")

Skunkworks cert-integrity invariant: this hook does NOT trigger Store-writes. Auto-continue
does NOT race the NULL-seam hazard.

Coexistence with v5 notes_monitor.sh: uses per-session `data/last_processed_<session>.timestamp`
the monitor does NOT touch -> no race.

Usage: stop_hook.py <session>
  stdin: hook input JSON (Claude Code hook protocol)
  stdout: hook decision JSON (only if blocking) OR nothing
  exit code: always 0 (per hook protocol expectation; decision is in stdout JSON)
"""
import json
import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    # Session resolution: CLAUDE_SESSION_NAME env var preferred (set per-window),
    # else positional arg. If neither -> fail-safe no-op (never block without session context).
    session = os.environ.get('CLAUDE_SESSION_NAME', '').strip()
    if not session and len(sys.argv) >= 2:
        session = sys.argv[1]
    if not session:
        return 0

    # Read stdin JSON (Claude Code hook protocol)
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            hook_input = {}
        else:
            hook_input = json.loads(raw)
    except (json.JSONDecodeError, OSError):
        hook_input = {}

    # === GUARD 1: stop_hook_active (THE load-bearing loop prevention) ===
    if bool(hook_input.get('stop_hook_active', False)):
        # Already in a Stop-hook-triggered continuation; never recurse.
        return 0

    # === GUARD 2: HARD_CAP continuation counter (runaway prevention) ===
    # Script lives in data/hooks/staging/; repo root = ../../..
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    state_dir = repo_root / 'data' / 'hook_state'
    state_dir.mkdir(parents=True, exist_ok=True)
    cont_file = state_dir / f'stop_continuations_{session}'

    hard_cap = int(os.environ.get('HD_STOP_HOOK_HARD_CAP', '10'))

    try:
        count = int(cont_file.read_text().strip()) if cont_file.exists() else 0
    except (ValueError, OSError):
        count = 0

    if count >= hard_cap:
        # Cap reached. Let session truly stop. (Counter reset on real-USER-input cycle TBD.)
        return 0

    # === GUARD 3: Concrete signal gate ===
    # 3a: Unread inbox newer than per-session last-processed timestamp
    notes_dir = repo_root / 'notes'
    ts_file = repo_root / 'data' / f'last_processed_{session}.timestamp'

    if not ts_file.exists():
        # First-run: treat all current notes as "already processed" (start fresh).
        # The first time the hook runs, write current time so existing notes don't all trigger.
        # (Defensive: avoid using touch -t which has Windows quirks; just write now.)
        try:
            ts_file.touch()
        except OSError:
            pass
        ts_mtime = 0
    else:
        try:
            ts_mtime = ts_file.stat().st_mtime
        except OSError:
            ts_mtime = 0

    have_unread = False
    have_unread_name = None
    if notes_dir.is_dir():
        # Match same filter convention as v5 notes_monitor.sh: filenames containing
        # session OR to_all OR _all_; exclude own outgoing (session prefix).
        session_lower = session.lower()
        for note in notes_dir.iterdir():
            if not note.is_file():
                continue
            if note.suffix != '.md':
                continue
            name = note.name
            name_lower = name.lower()
            # Exclude own outgoing
            if name_lower.startswith(f'{session_lower}_'):
                continue
            # Match the v5 filter
            if not (session_lower in name_lower
                    or 'to_all' in name_lower
                    or '_all_' in name_lower):
                continue
            try:
                mtime = note.stat().st_mtime
            except OSError:
                continue
            if mtime > ts_mtime:
                have_unread = True
                have_unread_name = name
                break

    if have_unread:
        # Concrete signal: increment counter + emit block decision
        try:
            cont_file.write_text(str(count + 1))
        except OSError:
            pass
        reason = (f"New inbox items pending for {session} "
                  f"(found newer than {ts_file.name}: {have_unread_name}); "
                  f"continuing triage. (continuation {count + 1}/{hard_cap})")
        decision = {"decision": "block", "reason": reason}
        print(json.dumps(decision))
        return 0

    # No concrete signal: exit (true stop). Don't increment counter.
    return 0


if __name__ == '__main__':
    sys.exit(main())
