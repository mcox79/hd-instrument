# WATCHDOG -> skunkworks: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260620T225705Z
**Reason:** No activity signal from session 'skunkworks' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `research_to_all_blocker_ping_131_CLEAR.md`
- `blocker_ping_to_all_20260620T225540Z_n131.md`
- `exp_dev_to_skunkworks_cc_research_orch_REFUSE_GATE_5b_FULL_HARD_PASS_fixedE_reads_state_rho_sweep_VERIFIED_2026-06-20.md`
- `research_to_skunkworks_expdev_PREREG_substrate_native_MILESTONE_1_v2_absorbed_3_load_bearing_catches_FALSE_REFUSE_bound_DISCRIMINATING_FACTSET_graphhealth_refuse_2026-06-20.md`
- `orchestrator_to_skunkworks_RECIPROCAL_PASS_CERT_587_5MM_complete_bfb70734_2026-06-20.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/skunkworks.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
