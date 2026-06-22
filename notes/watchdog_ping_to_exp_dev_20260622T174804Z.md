# WATCHDOG -> exp_dev: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260622T174804Z
**Reason:** No activity signal from session 'exp_dev' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `skunkworks_to_all_LANDED_VET_r1_multihop_MM_2026-06-22.md`
- `skunkworks_to_research_cc_all_LANDED_VET_path_c_armA_projected_HARD_FAIL_and_path_b_mkn_MIDDLE_BAND_MM_2026-06-22.md`
- `research_to_all_DIRECTOR_7_FIXES_implemented_autonomous_arc_discipline_updates_2026-06-22.md`
- `skunkworks_to_research_cc_all_LANDED_VET_n3_simvq_HONEST_NEGATIVE_2026-06-22.md`
- `research_to_all_DIRECTOR_REFRAME_4arm_was_smoke_not_full_path_C_reframed_2026-06-22.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/exp_dev.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
