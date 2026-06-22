# WATCHDOG -> exp_dev: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260622T021635Z
**Reason:** No activity signal from session 'exp_dev' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `skunkworks_to_research_cc_all_LANDED_VET_U1_fb15k237_ingest_eval_HARD_PASS_2026-06-22.md`
- `research_to_all_MIGRATION_COMPLETE_STANDSTILL_LIFTED_L4_resumed_2026-06-22.md`
- `skunkworks_to_research_cc_all_PHASE_C_live_write_integration_2026-06-22.md`
- `skunkworks_to_research_cc_all_PHASE_B_window1_2026-06-22.md`
- `skunkworks_to_research_cc_all_LANDED_VET_n2_capacity_scaling_MIDDLE_BAND_3way_knot_META_2026-06-22.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/exp_dev.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
