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
import time
from pathlib import Path


def _testbed_waiting_cycle_hint(repo_root: Path) -> str:
    """For testbed role only: if > 60min since last waiting-on-cycle round was fired,
    return '[WAITING-CYCLE-DUE: file next round per USER hourly protocol]'.
    Best-effort silent on errors. Cooldown via data/hook_state/waiting_cycle_last_fired_ts."""
    cooldown_file = repo_root / 'data' / 'hook_state' / 'waiting_cycle_last_fired_ts'
    try:
        if cooldown_file.exists():
            last_fired = float(cooldown_file.read_text().strip())
            if (time.time() - last_fired) < 3000:  # 50 min suppress
                return ''
    except (OSError, ValueError):
        pass
    return '[WAITING-CYCLE-DUE: file next waiting-on cycle round per USER hourly protocol]'


def _testbed_active_pulse(repo_root: Path) -> str:
    """For the testbed role only: run an active dashboard pulse on EVERY Stop fire
    and embed rich state in the block reason. Replaces the prior 'hint only when
    triggered' pattern -- the data is ALWAYS surfaced so I can't drift into
    standing-without-checking. Cooldown only suppresses the recommend-to-fire
    action, not the pulse data itself.

    Returns a single line like:
      [FLEET: agg=WARN | research(22m) exp_dev(35m STALE) skunkworks(active) orchestrator(active) | drift: 0 RED | ACTION: fire probe R12 narrowed to research+exp_dev]

    Silent only on dashboard-unreachable (no false-alarm).
    """
    import urllib.request
    import urllib.error
    try:
        with urllib.request.urlopen('http://localhost:8765/api/dashboard/v2/health', timeout=3) as r:
            data = json.loads(r.read().decode('utf-8'))
    except (urllib.error.URLError, OSError, json.JSONDecodeError, ValueError):
        return '[PULSE-DASHBOARD-DOWN]'  # not silent -- I should know if dashboard is down

    agg = (data.get('aggregate') or {}).get('status', '?')
    fleet = (data.get('project_health') or {}).get('fleet') or {}
    red_drifts = [d.get('name', '?') for d in data.get('drift_detectors', []) if d.get('status') == 'RED']

    # Per-session age summary; mark stale (>15m)
    fleet_summary = []
    stale = []
    for role in ('research', 'exp_dev', 'skunkworks', 'orchestrator'):
        s = fleet.get(role, {})
        age = s.get('latest_substantive_note_age_s')
        if not isinstance(age, (int, float)):
            fleet_summary.append(f'{role}(?)')
            continue
        m = int(age / 60)
        if m > 15:
            fleet_summary.append(f'{role}({m}m STALE)')
            stale.append((role, m))
        else:
            fleet_summary.append(f'{role}({m}m)')

    # Cooldown check for lull-probe action recommendation
    lull_cd = repo_root / 'data' / 'hook_state' / 'lull_probe_last_fired_ts'
    lull_action_due = False
    if len(stale) >= 2:
        try:
            if lull_cd.exists():
                last = float(lull_cd.read_text().strip())
                if (time.time() - last) >= 2700:  # 45 min
                    lull_action_due = True
            else:
                lull_action_due = True
        except (OSError, ValueError):
            lull_action_due = True

    # Cycle-due check
    cycle_cd = repo_root / 'data' / 'hook_state' / 'waiting_cycle_last_fired_ts'
    cycle_action_due = False
    try:
        if cycle_cd.exists():
            last = float(cycle_cd.read_text().strip())
            if (time.time() - last) >= 3000:  # 50 min
                cycle_action_due = True
        else:
            cycle_action_due = True
    except (OSError, ValueError):
        cycle_action_due = True

    actions = []
    if lull_action_due and len(stale) >= 2:
        narrow = sorted(stale, key=lambda x: -x[1])
        narrow_desc = '+'.join(r for r, _ in narrow[:4])
        actions.append(f'fire LULL probe (narrow_to_{narrow_desc})')
    if cycle_action_due:
        if stale:
            narrow = sorted(stale, key=lambda x: -x[1])
            narrow_desc = '+'.join(r for r, _ in narrow[:4])
            actions.append(f'fire CYCLE round (narrow_to_{narrow_desc})')
        else:
            actions.append('fire CYCLE round (4/4 active; broad ok)')
    if red_drifts:
        actions.append(f'investigate RED drift: {",".join(red_drifts)}')

    action_str = ' | '.join(actions) if actions else 'pulse-only (no action due)'
    red_str = f'{len(red_drifts)} RED ({",".join(red_drifts)})' if red_drifts else '0 RED'
    return f"[FLEET: agg={agg} | {' '.join(fleet_summary)} | drift: {red_str} | ACTION: {action_str}]"


def _testbed_lull_check_hint(repo_root: Path) -> str:
    """DEPRECATED: kept for compatibility; replaced by _testbed_active_pulse.
    Returns '' always; _testbed_active_pulse now embeds lull state + action
    recommendation directly into the hook's block reason."""
    return ''


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

    # Heartbeat-on-every-turn-end: if we can resolve a role, touch its heartbeat file so
    # the watchdog has a current liveness signal without needing to ping (eliminates the
    # self-stale-ping loop that wastes a turn just to touch a file). Done early + tolerant
    # of failures (the hook's decision logic continues regardless).
    repo_root_hb = Path(__file__).resolve().parent.parent.parent.parent
    key_map_file_hb = repo_root_hb / 'data' / 'session_key_map.json'
    role_for_hb = None
    if key_map_file_hb.exists():
        try:
            with key_map_file_hb.open('r', encoding='utf-8') as f:
                km_hb = json.load(f)
            v = km_hb.get(session)
            if isinstance(v, str) and v.strip():
                role_for_hb = v.strip()
        except (json.JSONDecodeError, OSError):
            pass
    if role_for_hb:
        try:
            hb_dir = repo_root_hb / 'data' / 'heartbeats'
            hb_dir.mkdir(parents=True, exist_ok=True)
            hb_file = hb_dir / f'{role_for_hb}.timestamp'
            hb_file.touch()
        except OSError:
            pass

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
        # Advance last_processed to NOW so subsequent Stop fires don't re-block on the
        # SAME notes (the block itself surfaces them to the session as Stop hook feedback;
        # the session's continuation turn IS the response). Without this, the hook
        # re-blocks on the same unread note every cycle until cap, even though the
        # session already saw it.
        try:
            ts_file.touch()
        except OSError:
            pass
        signals = []
        if have_unread:
            signals.append(f"unread inbox ({have_unread_name})")
        if have_watchdog_ping:
            signals.append(f"watchdog ping ({have_watchdog_ping_name})")
        reason = (f"Pending work for {session}: " + " + ".join(signals) +
                  f"; continuing. (continuation {count + 1}/{hard_cap})")
        # Layer 1 of the lull-breaker enforcement (per USER 2026-06-21 + my own
        # protocol commit). For the testbed (audit) role only: query the dashboard
        # health endpoint + check if >= 2 OTHER sessions have substantive-note age
        # > 15 min. If so AND no probe was fired in the last 90 min, INJECT a
        # "LULL DETECTED" hint into the block reason. The hint becomes Stop hook
        # feedback text in the next turn -- mechanical, not memory-dependent.
        if role_for_hb == 'testbed':
            # Auto-execute pulse (replaces both prior hint helpers; ALWAYS runs +
            # embeds rich fleet data + action recommendation -- no reliance on me
            # remembering to check). Per USER 2026-06-21 #1 improvement.
            try:
                pulse = _testbed_active_pulse(repo_root_hb)
                if pulse:
                    reason = reason + " " + pulse
                # Self-test (#4): log success to debug file so any silent failure
                # of the helpers is visible within minutes (the lull-hint NameError
                # bug went undetected for hours because no self-test ran).
                try:
                    st_log = repo_root_hb / 'data' / 'hook_state' / '_hint_selftest.log'
                    st_log.parent.mkdir(parents=True, exist_ok=True)
                    with st_log.open('a', encoding='utf-8') as f:
                        f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} OK pulse_len={len(pulse)}\n")
                except OSError:
                    pass
            except Exception as e:
                # Self-test (#4): record the failure so it's visible
                try:
                    st_log = repo_root_hb / 'data' / 'hook_state' / '_hint_selftest.log'
                    st_log.parent.mkdir(parents=True, exist_ok=True)
                    with st_log.open('a', encoding='utf-8') as f:
                        f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} FAIL {type(e).__name__}: {str(e)[:100]}\n")
                except OSError:
                    pass
        decision = {"decision": "block", "reason": reason}
        print(json.dumps(decision))
        return 0

    # No concrete signal: exit (true stop). Also RESET the continuation counter to 0 -- a
    # clean stop is the natural cycle boundary (equivalent to "session caught up + handed
    # back to USER"); the counter should fresh-start the next time work shows up. Without
    # this, the counter accumulates across DIFFERENT pings/notes during a long reactive
    # session and eventually hits cap on unrelated notes. (Written as "0" rather than
    # unlinked so the dry-run tests' count_after read remains valid.)
    try:
        if count != 0:
            cont_file.write_text('0')
    except OSError:
        pass
    return 0


if __name__ == '__main__':
    sys.exit(main())
