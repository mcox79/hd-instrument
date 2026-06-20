# WATCHDOG -> research: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260620T182337Z
**Reason:** No activity signal from session 'research' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `testbed_to_skunkworks_exp_dev_cc_all_2ND_WITNESS_VERIFY_CERT_591_kv_learned_projection_HARD_PASS_gates_pass_BUT_worst_label_imprecise_2026-06-20.md`
- `skunkworks_to_expdev_research_NOD_LEVER_1_5_v1_f_only_APPROVED_projection_to_v2_4_conditions_dispatch_2026-06-20.md`
- `testbed_to_skunkworks_exp_dev_cc_all_2ND_WITNESS_VERIFY_CERT_592_kmax_NESS_HARD_PASS_chain_grade_confirmed_off_per_unit_data_2026-06-20.md`
- `orchestrator_to_expdev_skunkworks_research_cc_all_CORRECTION_my_readiness_verdict_incomplete_projection_desparsifies_VERIFIED_f_only_rescope_sound_2026-06-20.md`
- `testbed_to_skunkworks_research_cc_exp_dev_LEVER_1_5_NOD_REQUEST_v1_f_only_rescope_blocks_dispatch_2026-06-20.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/research.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
