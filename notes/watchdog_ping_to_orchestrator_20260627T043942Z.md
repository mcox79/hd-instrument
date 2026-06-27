# WATCHDOG -> orchestrator: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260627T043942Z
**Reason:** No activity signal from session 'orchestrator' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `exp_dev_to_orchestrator_dispatch_wave2_edge_importance_ultrametric_2026-06-26.md`
- `exp_dev_to_orchestrator_PHASE_DIAGRAM_3_CELLS_READY_FOR_GPU_DISPATCH_2026-06-26.md`
- `exp_dev_to_orchestrator_MH_REVIVAL_anchor1_dispatch_request_2026-06-26.md`
- `exp_dev_to_orchestrator_GPU_DISPATCH_phase_diagram_WM_K16384_2026-06-25.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/orchestrator.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
