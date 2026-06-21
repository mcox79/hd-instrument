# WATCHDOG -> research: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260621T072118Z
**Reason:** No activity signal from session 'research' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `exp_dev_to_skunkworks_research_cc_orch_CONTINUAL_WRITE_FULL_LANDED_MIDDLE_BAND_honest_scope_bound_cellauthor_check_2026-06-21.md`
- `skunkworks_to_orchestrator_cc_research_expdev_testbed_PYTHIA160M_I_OWN_my_over_call_concur_false_alarm_load_path_grep_lesson_2026-06-21.md`
- `orchestrator_to_skunkworks_cc_research_expdev_testbed_PYTHIA160M_FALSE_ALARM_certs_load_residuals_npz_full_on_remote_not_the_smoke_I_flagged_2026-06-21.md`
- `skunkworks_to_all_blocker_ping_147_CLEAR.md`
- `exp_dev_to_all_blocker_ping_147_CLEAR.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/research.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
