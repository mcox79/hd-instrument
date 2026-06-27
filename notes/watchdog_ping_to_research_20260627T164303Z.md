# WATCHDOG -> research: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260627T164303Z
**Reason:** No activity signal from session 'research' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `skunkworks_to_research_FLAGBACK_batch7_4cell_phantom_no_full_landings_2026-06-27.md`
- `exp_dev_to_research_cortex_E_tensor_v2_SMOKE_HARD_FAIL_Fix_B_wrong_shaped_2026-06-26.md`
- `exp_dev_predispatch_hold_n6_optimal_V_C_sweep_v1_routes_to_research_2026-06-26.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/research.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
