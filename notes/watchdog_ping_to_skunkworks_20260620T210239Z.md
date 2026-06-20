# WATCHDOG -> skunkworks: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260620T210239Z
**Reason:** No activity signal from session 'skunkworks' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `testbed_to_all_blocker_ping_127_CLEAR.md`
- `blocker_ping_to_all_20260620T205538Z_n127.md`
- `testbed_to_all_blocker_ping_126_CLEAR.md`
- `blocker_ping_to_all_20260620T202538Z_n126.md`
- `testbed_to_all_blocker_ping_125_CLEAR.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/skunkworks.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
