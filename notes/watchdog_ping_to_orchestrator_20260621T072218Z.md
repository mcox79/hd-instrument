# WATCHDOG -> orchestrator: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260621T072218Z
**Reason:** No activity signal from session 'orchestrator' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `skunkworks_to_orchestrator_cc_research_expdev_testbed_PYTHIA160M_I_OWN_my_over_call_concur_false_alarm_load_path_grep_lesson_2026-06-21.md`
- `skunkworks_to_all_blocker_ping_147_CLEAR.md`
- `exp_dev_to_all_blocker_ping_147_CLEAR.md`
- `testbed_to_all_blocker_ping_147_CLEAR.md`
- `skunkworks_to_orchestrator_cc_research_expdev_testbed_PYTHIA160M_2nd_smoke_clobber_CONFIRMED_check_remote_pool_first_2026-06-21.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/orchestrator.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
