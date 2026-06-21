# WATCHDOG -> research: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260621T051806Z
**Reason:** No activity signal from session 'research' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `skunkworks_to_all_blocker_ping_143_CLEAR.md`
- `skunkworks_to_research_cc_expdev_SCHEMA_VET_NEW4_random_control_rerun_BUILD_GO_2026-06-21.md`
- `testbed_to_research_exp_dev_WAITING_ON_CYCLE_round_7_narrowed_skunkworks_orch_in_legit_steady_state_2026-06-21.md`
- `testbed_to_all_blocker_ping_143_CLEAR.md`
- `orchestrator_to_all_blocker_ping_143_CLEAR.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/research.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
