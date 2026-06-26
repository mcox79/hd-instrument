# WATCHDOG -> research: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260626T200802Z
**Reason:** No activity signal from session 'research' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `exp_dev_predispatch_hold_n6_optimal_V_C_sweep_v1_routes_to_research_2026-06-26.md`
- `exp_dev_to_research_gap2_v2b_window64_SMOKE_GATED_accept_option_C_2026-06-26.md`
- `exp_dev_to_research_gap2_v2_different_articles_SMOKE_GATED_2026-06-26.md`
- `exp_dev_to_research_gap2_stride_sweep_SMOKE_GATED_nonmonotonic_2026-06-26.md`
- `exp_dev_to_research_anisotropy_v4_cpu_path_DISPATCHED_2026-06-25.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/research.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
