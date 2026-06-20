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


def _derive_session_from_transcript(transcript_path: str) -> str:
    """Derive a stable per-VS-Code-window session key from the Claude transcript path.

    Transcript paths are unique per Claude conversation. We hash to get a short stable key
    that survives session restarts but distinguishes different VS Code windows. This is the
    fallback when CLAUDE_SESSION_NAME env var isn't set (e.g. session launched without the
    launcher).
    """
    import hashlib
    h = hashlib.sha256(transcript_path.encode('utf-8')).hexdigest()[:10]
    return f'auto_{h}'


def main() -> int:
    # DEBUG: prove invocation independent of all other logic (first thing; can't be missed)
    try:
        from pathlib import Path as _P
        debug_log = _P(__file__).resolve().parent.parent.parent.parent / 'data' / 'hook_state' / '_invocation_log.txt'
        debug_log.parent.mkdir(parents=True, exist_ok=True)
        import time as _t
        with debug_log.open('a', encoding='utf-8') as _df:
            _df.write(f"{_t.strftime('%Y-%m-%dT%H:%M:%SZ', _t.gmtime())} stop_hook invoked  argv={sys.argv[1:]} pid={os.getpid()}\n")
    except Exception:
        pass

    # Read stdin JSON FIRST (so we can fall back to transcript_path for session key)
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            hook_input = {}
        else:
            hook_input = json.loads(raw)
    except (json.JSONDecodeError, OSError):
        hook_input = {}

    # Session resolution priority:
    #   1. CLAUDE_SESSION_NAME env var (per-launcher; human-readable)
    #   2. Derived from transcript_path in hook input (per-VS-Code-window; auto-stable)
    #   3. Positional arg (manual override)
    #   4. None -> fail-safe no-op
    session = os.environ.get('CLAUDE_SESSION_NAME', '').strip()
    if not session:
        transcript_path = str(hook_input.get('transcript_path', '')).strip()
        if transcript_path:
            session = _derive_session_from_transcript(transcript_path)
    if not session and len(sys.argv) >= 2:
        session = sys.argv[1]
    if not session:
        return 0

    # Resolve the auto_<hash> key to a role name via data/session_key_map.json if mapped.
    # Without this, own-outgoing exclude breaks: session_lower='auto_abc...' never matches
    # the role-prefixed notes (e.g. 'orchestrator_to_...') the session itself emits ->
    # self-firing on own broadcasts. Map is owned by the launcher / user-bootstrap.
    repo_root_early = Path(__file__).resolve().parent.parent.parent.parent
    key_map_file = repo_root_early / 'data' / 'session_key_map.json'
    role_name = None
    if key_map_file.exists():
        try:
            with key_map_file.open('r', encoding='utf-8') as f:
                key_map = json.load(f)
            mapped = key_map.get(session)
            if isinstance(mapped, str) and mapped.strip():
                role_name = mapped.strip()
        except (json.JSONDecodeError, OSError):
            pass

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
        # First-run: set timestamp to NOW so existing notes don't all count as "unread".
        # Without this, the very first hook fire would see 6000+ notes as newer than the
        # (just-created) timestamp file, blocking the session repeatedly until cap.
        try:
            ts_file.touch()
        except OSError:
            pass
        # Use current time as ts_mtime so existing notes are "already processed".
        try:
            ts_mtime = ts_file.stat().st_mtime
        except OSError:
            import time as _t
            ts_mtime = _t.time()
    else:
        try:
            ts_mtime = ts_file.stat().st_mtime
        except OSError:
            ts_mtime = 0

    have_unread = False
    have_unread_name = None
    have_watchdog_ping = False
    have_watchdog_ping_name = None
    session_lower = session.lower()
    role_lower = role_name.lower() if role_name else None
    # Prefixes a note can start with that mean "I wrote this" -- exclude.
    own_prefixes = {f'{session_lower}_'}
    if role_lower:
        own_prefixes.add(f'{role_lower}_')
    # Tokens that mean "this is for me" in the v5 unread filter -- include.
    self_tokens = {session_lower}
    if role_lower:
        self_tokens.add(role_lower)
    if notes_dir.is_dir():
        # Single scandir pass for BOTH unread + watchdog-ping signals.
        # Uses os.scandir for fast DirEntry traversal (much faster than iterdir+stat on Windows
        # for ~6000+ note directories; DirEntry caches stat info from the directory entry).
        try:
            with os.scandir(notes_dir) as it:
                for entry in it:
                    if not entry.name.endswith('.md'):
                        continue
                    name_lower = entry.name.lower()
                    # Exclude own outgoing (under EITHER the hash key or the resolved role)
                    if any(name_lower.startswith(p) for p in own_prefixes):
                        continue
                    # FIX (Orchestrator finding #1, 2026-06-20): watchdog pings are filed as
                    # `watchdog_ping_to_<X>_to_all_*` -- the `to_all` substring would otherwise
                    # trip have_unread on EVERY session, not just the targeted one. Exclude
                    # other-targeted watchdog pings explicitly before the unread match.
                    if name_lower.startswith('watchdog_ping_to_'):
                        if not any(tok in name_lower for tok in self_tokens):
                            continue
                    # First: cheap watchdog-ping filter (highest signal)
                    is_watchdog = (name_lower.startswith('watchdog_ping_to_')
                                   and any(tok in name_lower for tok in self_tokens))
                    # Then: v5 unread filter
                    is_unread_match = (any(tok in name_lower for tok in self_tokens)
                                       or 'to_all' in name_lower
                                       or '_all_' in name_lower)
                    if not (is_watchdog or is_unread_match):
                        continue
                    # Only stat() if filename matched (much less stat traffic)
                    try:
                        mtime = entry.stat().st_mtime
                    except OSError:
                        continue
                    if mtime <= ts_mtime:
                        continue
                    if is_watchdog and not have_watchdog_ping:
                        have_watchdog_ping = True
                        have_watchdog_ping_name = entry.name
                    if is_unread_match and not have_unread:
                        have_unread = True
                        have_unread_name = entry.name
                    if have_unread and have_watchdog_ping:
                        break
        except OSError:
            pass

    # NOTE: removed recent-commit-activity gate -- it over-fires across sessions during
    # active commit cycles (any session's git commit triggers .git/index mtime).
    # The watchdog-ping signal is the more-targeted external wake-up trigger.

    if have_unread or have_watchdog_ping:
        # Concrete signal: increment counter + emit block decision
        try:
            cont_file.write_text(str(count + 1))
        except OSError:
            pass
        signals = []
        if have_unread:
            signals.append(f"unread inbox ({have_unread_name})")
        if have_watchdog_ping:
            signals.append(f"watchdog ping ({have_watchdog_ping_name})")
        reason = (f"Pending work for {session}: " + " + ".join(signals) +
                  f"; continuing. (continuation {count + 1}/{hard_cap})")
        decision = {"decision": "block", "reason": reason}
        print(json.dumps(decision))
        return 0

    # No concrete signal: exit (true stop). Don't increment counter.
    return 0


if __name__ == '__main__':
    sys.exit(main())
