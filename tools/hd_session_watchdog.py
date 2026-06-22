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
import re
import sys
import time
from pathlib import Path
from typing import Optional


SESSIONS = ('testbed', 'research', 'exp_dev', 'orchestrator', 'skunkworks')

DEFAULT_POLL_SEC = 60       # check cadence
DEFAULT_STALE_THRESHOLD_SEC = 1200  # 20 min stale -> ping (2026-06-20: bumped 10->20min)
DEFAULT_DEAD_THRESHOLD_SEC = 3000  # 50 min stale -> mark dead + alert
PING_COOLDOWN_SEC = 600     # don't re-ping the same session more often than every 10 min

# Inbox-seed filtering (Testbed infra-fix 2026-06-22; per USER no-inter-session-routing rule).
# `_recent_inbox_for` used to surface stale 3-day-old ferry/dashboard/landed-vet notes as
# "pending work" -- noise under the no-ferry rule (feedback memory
# feedback_no_inter_session_routing_notes_deprecate_ferry_mechanism_USER_2026-06-22).
# Filter applies to the inbox-seed block ONLY; the heartbeat-stale ping itself still fires
# (the genuinely-silent signal is load-bearing per session-hardening Phase 1+2).
INBOX_MAX_AGE_SEC = 24 * 3600   # drop notes older than 24h
INBOX_DEPRECATED_PATTERNS = (
    re.compile(r'_to_[a-z_]+_ferry_', re.I),       # _to_<session>_ferry_* (deprecated routing)
    re.compile(r'^ferry_request_', re.I),           # ferry_request_* (deprecated mechanism)
    re.compile(r'_landed_vet_', re.I),              # LANDED_VET cert-trail (not action)
    re.compile(r'_dashboard_', re.I),               # DASHBOARD historical (not action)
    re.compile(r'_blocker_ping_\d+_clear', re.I),   # blocker_ping_<N>_CLEAR (already resolved)
    re.compile(r'_resolved_', re.I),                # explicit resolution marker
    re.compile(r'_processed_', re.I),               # explicit processed marker
)

# Per-session stale-threshold overrides (P2 streamline; 2026-06-21).
# Skunkworks requested 60min: legit-reactive cert-owner waits multi-hour on cell-lands;
# default 20min mis-fires + wastes pings. They have active Monitor + Stop hook = alive.
# Testbed: also 60min self-stale-pings were wasteful when actively cycling but between events.
PER_SESSION_STALE_THRESHOLD_SEC = {
    'skunkworks': 3600,  # 60 min (Skunkworks request 2026-06-21; reactive cert-owner)
    'testbed':    3600,  # 60 min (audit role; always Monitor-armed; was burning self-pings)
}

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


def _recent_inbox_for(session: str, max_items: int = 5,
                      max_age_sec: int = INBOX_MAX_AGE_SEC,
                      now: Optional[float] = None) -> list:
    """Return up to max_items recent note filenames addressed to this session.

    Match criteria: filename contains '_to_<session>_' OR contains '_to_all_' / '_cc_all_'
    broadcast tokens (excluding own outgoing). Used to seed the ping body with concrete
    pending work so the session has something specific to do on wake.

    Filters (Testbed 2026-06-22):
      1. Drop notes older than max_age_sec (default 24h) -- if unprocessed in 24h+,
         the note has aged out of "actionable inbox" definitionally.
      2. Drop notes matching INBOX_DEPRECATED_PATTERNS (ferry/LANDED_VET/DASHBOARD/etc.)
         per the no-inter-session-routing rule
         (feedback_no_inter_session_routing_notes_deprecate_ferry_mechanism_USER_2026-06-22).
      3. Drop the loose '_<session>_' substring-match (was catching legacy multi-target
         notes like `testbed_to_research_skunkworks_*` for ALL three sessions); narrow
         to explicit `_to_<session>_` or broadcast tokens.
    """
    candidates = []
    sess_lower = session.lower()
    own_prefix = f'{sess_lower}_'
    now_ts = time.time() if now is None else now
    age_floor = now_ts - max_age_sec
    try:
        with os.scandir(NOTES_DIR) as it:
            for entry in it:
                if not entry.name.endswith('.md'):
                    continue
                name_lower = entry.name.lower()
                if name_lower.startswith(own_prefix):
                    continue
                # Skip watchdog own-broadcasts to keep the list signal-y
                if name_lower.startswith('watchdog_ping_to_'):
                    continue
                # Drop deprecated patterns (ferry/LANDED_VET/DASHBOARD/resolved/processed).
                if any(p.search(name_lower) for p in INBOX_DEPRECATED_PATTERNS):
                    continue
                # Narrow addressed-match: explicit _to_<session>_ or broadcast token only.
                # The prior loose `_{sess_lower}_` substring caught multi-target legacy
                # notes for every named session simultaneously.
                addressed = (f'_to_{sess_lower}_' in name_lower
                             or '_to_all_' in name_lower
                             or '_cc_all_' in name_lower)
                if not addressed:
                    continue
                try:
                    mtime = entry.stat().st_mtime
                except OSError:
                    continue
                # Drop notes older than the 24h freshness floor.
                if mtime < age_floor:
                    continue
                candidates.append((mtime, entry.name))
    except OSError:
        return []
    candidates.sort(reverse=True)
    return [name for (_, name) in candidates[:max_items]]


def write_ping_note(session: str, dry_run: bool = False) -> Optional[Path]:
    """Write a high-visibility ping note that the session's monitor will pick up.

    Filename includes session name + to_all + watchdog tag so the v5 filter matches it.
    Body includes the concrete recent-inbox snapshot so the session, on wake, has specific
    work to act on instead of just running the heartbeat-touch.
    """
    import os as _os  # local import for scandir
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    # Filename is TARGETED (no `_to_all_` infix): v5 notes_monitor.sh delivers it ONLY to
    # the session whose name is in the filename, NOT to every session's monitor via the
    # `to_all` token. Kills the N-1-wasted-wake-ups-per-ping cross-session monitor churn
    # Orchestrator observed 2026-06-20. Visibility of fleet staleness is preserved via
    # data/watchdog/state.json (the dashboard reads that, not ping-filenames).
    fname = f'watchdog_ping_to_{session}_{ts}.md'
    note_path = NOTES_DIR / fname

    # Seed the body with the session's actual recent inbox so they have CONCRETE
    # pending work to address on wake, not just the ack ritual.
    recent = _recent_inbox_for(session, max_items=5)
    if recent:
        inbox_block = (
            "## Your recent inbox (5 newest notes likely addressed to you)\n\n"
            + "\n".join(f"- `{n}`" for n in recent)
            + "\n\nProcess any of these you haven't yet; reply per their protocol.\n\n"
        )
    else:
        inbox_block = "## Your recent inbox\n\n(none detected matching your name in the last scan)\n\n"

    body = (
        f"# WATCHDOG -> {session}: heartbeat-stale + concrete inbox snapshot\n\n"
        f"**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)\n"
        f"**Date:** {ts}\n"
        f"**Reason:** No activity signal from session '{session}' in the stale window.\n\n"
        + inbox_block +
        "## ACTION (do on wake; takes one Bash call)\n\n"
        f"After processing the inbox above (if anything new), run:\n\n"
        "```bash\n"
        f"mkdir -p data/heartbeats && touch data/heartbeats/{session}.timestamp\n"
        "```\n\n"
        "Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).\n\n"
        "## Why this matters\n\n"
        "Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.\n"
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

        # Per-session stale threshold override (P2 streamline 2026-06-21)
        effective_stale_sec = PER_SESSION_STALE_THRESHOLD_SEC.get(sess, stale_sec)
        if age < effective_stale_sec:
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
