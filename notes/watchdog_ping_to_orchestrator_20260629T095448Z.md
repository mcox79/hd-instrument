# WATCHDOG -> orchestrator: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260629T095448Z
**Reason:** No activity signal from session 'orchestrator' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `exp_dev_to_orchestrator_DISPATCH_REQUEST_multihop_phase_diagram_v5_3seeds_overnight_2026-06-29.md`
- `exp_dev_to_orchestrator_dispatch_wm_encoder_family_v1_2026-06-28.md`
- `exp_dev_to_orchestrator_refuse_gate_adaptivity_v1_dispatch_2026-06-28.md`
- `exp_dev_to_orchestrator_DISPATCH_REQUEST_wm_routing_family_phase_diagram_v1_3seeds_overnight_2026-06-28.md`
- `exp_dev_to_orchestrator_time_decay_v2_Pareto_AUC_remote_dispatch_2026-06-29.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/orchestrator.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
