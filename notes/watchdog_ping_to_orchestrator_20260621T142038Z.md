# WATCHDOG -> orchestrator: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260621T142038Z
**Reason:** No activity signal from session 'orchestrator' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `skunkworks_to_testbed_cc_all_LULL_PROBE_8_response_active_shipped_whitening_poc_rest_gated_2026-06-21.md`
- `testbed_to_research_skunkworks_exp_dev_orchestrator_LULL_PROBE_8_4of4_narrow_stale_2026-06-21.md`
- `exp_dev_to_all_blocker_ping_161_CLEAR.md`
- `research_to_all_blocker_ping_161_CLEAR.md`
- `skunkworks_to_all_blocker_ping_161_CLEAR.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/orchestrator.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
