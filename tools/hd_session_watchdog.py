"""Phase 2 watchdog (per Director GO; per Orchestrator runtime-owner spec).

Monitors per-session heartbeat files and surfaces stale-session alerts. Cannot directly
"revive" a VS Code-embedded Claude session (no IPC into the extension), but does the next
best thing: files a HIGH-VISIBILITY ping note that the target session's v5 notes_monitor.sh
picks up + delivers as a task-notification. If the target session is idle-alive (sitting at
the Claude prompt with the v5 monitor still feeding events), the new ping wakes it. If the
target session process is fully-dead, the watchdog logs the death for USER to see.

LIMITS (honest):
  - Cannot revive a dead VS Code window (separate process; no programmatic restart of the
    embedded Claude extension session). Logs death for USER review.
  - "Stale" detection assumes each session writes `data/heartbeats/<session>.timestamp` on
    every turn-end. Without that session-side integration, watchdog has no signal -> falls
    back to commit-activity-by-author heuristic (per-session-prefix on note filenames).
  - Skunkworks invariant preserved: watchdog does NOT trigger Store-writes; pure read +
    notes/ filesystem write (notes are NOT Store atoms).

Coexistence with existing infra:
  - notes_monitor.sh v5: watchdog writes notes/ files which the per-session monitor picks up
  - event_bus.sh: untouched
  - hd_blocker_ping (30-min): complementary; this watchdog is finer-grained (5-min poll)
  - hd_metrics_sync: untouched

Args: optional --dry-run (no notes written; just log to stdout); --once (single poll then exit).

Usage:
  python tools/hd_session_watchdog.py            # daemon mode (poll every WATCHDOG_POLL_SEC)
  python tools/hd_session_watchdog.py --once     # single poll
  python tools/hd_session_watchdog.py --dry-run  # log only; no notes written
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional


SESSIONS = ('testbed', 'research', 'exp_dev', 'orchestrator', 'skunkworks')

DEFAULT_POLL_SEC = 60       # check cadence
DEFAULT_STALE_THRESHOLD_SEC = 600  # 10 min stale -> ping (more conservative than original 5min to avoid noisy revival)
DEFAULT_DEAD_THRESHOLD_SEC = 1800  # 30 min stale -> mark dead + alert
PING_COOLDOWN_SEC = 600     # don't re-ping the same session more often than every 10 min

REPO_ROOT = Path(__file__).resolve().parent.parent
HEARTBEAT_DIR = REPO_ROOT / 'data' / 'heartbeats'
WATCHDOG_LOG = REPO_ROOT / 'data' / 'watchdog' / 'watchdog.log'
WATCHDOG_STATE = REPO_ROOT / 'data' / 'watchdog' / 'state.json'
NOTES_DIR = REPO_ROOT / 'notes'


def log(msg: str) -> None:
    """Log to stdout + append to watchdog log file (best-effort)."""
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}  {msg}"
    print(line, flush=True)
    try:
        WATCHDOG_LOG.parent.mkdir(parents=True, exist_ok=True)
        with WATCHDOG_LOG.open('a', encoding='utf-8') as f:
            f.write(line + '\n')
    except OSError:
        pass


def load_state() -> dict:
    if not WATCHDOG_STATE.exists():
        return {}
    try:
        return json.loads(WATCHDOG_STATE.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return {}


def save_state(state: dict) -> None:
    try:
        WATCHDOG_STATE.parent.mkdir(parents=True, exist_ok=True)
        WATCHDOG_STATE.write_text(json.dumps(state, indent=2), encoding='utf-8')
    except OSError:
        pass


def session_last_activity(session: str) -> Optional[float]:
    """Return mtime of most recent activity-signal for session, or None if no signal.

    Signal priority:
      1. data/heartbeats/<session>.timestamp (requires session-side integration to write)
      2. fallback: most recent notes/ file with session-prefix (session_*.md)
    """
    hb_file = HEARTBEAT_DIR / f'{session}.timestamp'
    if hb_file.exists():
        try:
            return hb_file.stat().st_mtime
        except OSError:
            pass

    # Fallback: scan notes/ for files prefixed by session name (outgoing notes from session)
    latest = 0.0
    try:
        for note in NOTES_DIR.iterdir():
            if not note.is_file() or note.suffix != '.md':
                continue
            if note.name.startswith(f'{session}_'):
                try:
                    m = note.stat().st_mtime
                    if m > latest:
                        latest = m
                except OSError:
                    continue
    except OSError:
        pass
    return latest if latest > 0 else None


def write_ping_note(session: str, dry_run: bool = False) -> Optional[Path]:
    """Write a high-visibility ping note that the session's monitor will pick up.

    Filename includes session name + to_all + watchdog tag so the v5 filter matches it.
    """
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    fname = f'watchdog_ping_to_{session}_to_all_{ts}.md'
    note_path = NOTES_DIR / fname
    body = (
        f"# WATCHDOG -> {session}: ACTION REQUIRED - heartbeat-stale\n\n"
        f"**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)\n"
        f"**Date:** {ts}\n"
        f"**Reason:** No activity signal from session '{session}' in the stale window.\n\n"
        "## ACTION REQUIRED (do this on receipt; takes one Bash call)\n\n"
        f"Run this exact command to mark yourself alive + stop future ping spam from the watchdog:\n\n"
        "```bash\n"
        f"mkdir -p data/heartbeats && touch data/heartbeats/{session}.timestamp\n"
        "```\n\n"
        "Then continue with your standing-reactive pipeline (cycle-check filesystem for any substrate-mutation events you may have missed since last cycle).\n\n"
        "## Why this matters\n\n"
        "Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you. One `touch` per turn-end is enough -- the watchdog ignores you for 10 min after each touch.\n\n"
        "## If you have substantive work pending\n\n"
        "Process it now (e.g., reactive 2nd-witness on recent cert events, atomization checks, etc.) THEN do the heartbeat touch at the end of your turn.\n"
    )
    if dry_run:
        log(f"DRY-RUN: would write ping note: {fname}")
        return None
    try:
        note_path.write_text(body, encoding='utf-8')
        log(f"PING: filed {fname}")
        return note_path
    except OSError as e:
        log(f"ERROR writing ping note for {session}: {e}")
        return None


def poll_once(dry_run: bool = False,
              stale_sec: int = DEFAULT_STALE_THRESHOLD_SEC,
              dead_sec: int = DEFAULT_DEAD_THRESHOLD_SEC,
              ping_cooldown_sec: int = PING_COOLDOWN_SEC) -> dict:
    """Poll all sessions; return status dict."""
    now = time.time()
    state = load_state()
    if 'last_ping' not in state:
        state['last_ping'] = {}
    status = {}

    for sess in SESSIONS:
        last_active = session_last_activity(sess)
        if last_active is None:
            status[sess] = {'state': 'no_signal', 'age_sec': None}
            continue
        age = now - last_active
        last_ping = state['last_ping'].get(sess, 0)
        ping_age = now - last_ping

        if age < stale_sec:
            status[sess] = {'state': 'alive', 'age_sec': int(age)}
        elif age < dead_sec:
            status[sess] = {'state': 'stale', 'age_sec': int(age)}
            if ping_age >= ping_cooldown_sec:
                if write_ping_note(sess, dry_run=dry_run):
                    state['last_ping'][sess] = now
                    status[sess]['ping_filed'] = True
                else:
                    status[sess]['ping_filed'] = False
            else:
                status[sess]['ping_filed'] = False
                status[sess]['ping_cooldown_remaining_sec'] = int(ping_cooldown_sec - ping_age)
        else:
            status[sess] = {'state': 'dead', 'age_sec': int(age)}
            if ping_age >= ping_cooldown_sec:
                if write_ping_note(sess, dry_run=dry_run):
                    state['last_ping'][sess] = now
                    status[sess]['ping_filed'] = True
                # also write a USER-visible alert? for now log it
                log(f"DEAD ALERT: session '{sess}' has had no activity for {int(age)}s "
                    f"(threshold {dead_sec}s). USER inspection recommended.")

    save_state(state)
    return status


def daemon(poll_sec: int = DEFAULT_POLL_SEC, dry_run: bool = False) -> int:
    """Run as daemon; poll at fixed cadence."""
    log(f"hd_session_watchdog starting (poll={poll_sec}s; dry_run={dry_run})")
    while True:
        try:
            status = poll_once(dry_run=dry_run)
            alive = sum(1 for s in status.values() if s.get('state') == 'alive')
            stale = sum(1 for s in status.values() if s.get('state') == 'stale')
            dead = sum(1 for s in status.values() if s.get('state') == 'dead')
            no_sig = sum(1 for s in status.values() if s.get('state') == 'no_signal')
            log(f"poll: alive={alive} stale={stale} dead={dead} no_signal={no_sig}")
        except Exception as e:
            log(f"poll error: {e!r}")
        time.sleep(poll_sec)


def main() -> int:
    ap = argparse.ArgumentParser(description='HD session watchdog')
    ap.add_argument('--dry-run', action='store_true', help='No notes written; log only')
    ap.add_argument('--once', action='store_true', help='Single poll then exit')
    ap.add_argument('--poll-sec', type=int, default=DEFAULT_POLL_SEC)
    args = ap.parse_args()

    if args.once:
        status = poll_once(dry_run=args.dry_run)
        print(json.dumps(status, indent=2))
        return 0
    return daemon(poll_sec=args.poll_sec, dry_run=args.dry_run)


if __name__ == '__main__':
    sys.exit(main())
