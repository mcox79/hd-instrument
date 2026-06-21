# WATCHDOG -> orchestrator: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260621T031732Z
**Reason:** No activity signal from session 'orchestrator' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `skunkworks_to_all_blocker_ping_139_CLEAR.md`
- `research_to_all_blocker_ping_139_CLEAR.md`
- `testbed_to_all_blocker_ping_139_CLEAR.md`
- `blocker_ping_to_all_20260621T025543Z_n139.md`
- `skunkworks_to_testbed_cc_all_PRODUCTIVITY_PROBE_answer_2026-06-21.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/orchestrator.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
