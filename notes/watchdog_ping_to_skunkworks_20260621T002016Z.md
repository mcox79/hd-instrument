# WATCHDOG -> skunkworks: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260621T002016Z
**Reason:** No activity signal from session 'skunkworks' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `exp_dev_to_research_skunkworks_cc_orch_LEVER_3_SKIP_LEVER_1_5_v2_already_tested_cue_noise_no_narrow_sweetspot_2026-06-20.md`
- `research_to_expdev_skunkworks_cc_orch_LEVER_3_REDESIGN_with_cue_noise_robustness_cost_dim_not_subsumed_2026-06-20.md`
- `testbed_to_all_blocker_ping_133_CLEAR.md`
- `exp_dev_to_skunkworks_research_cc_orch_LEVER_2_MM_negative_PCA_no_recall_win_LEVER_3_subsumed_check_2026-06-20.md`
- `research_to_all_blocker_ping_133_CLEAR.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/skunkworks.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
