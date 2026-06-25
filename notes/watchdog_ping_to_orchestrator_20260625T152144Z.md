# WATCHDOG -> orchestrator: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260625T152144Z
**Reason:** No activity signal from session 'orchestrator' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `exp_dev_to_orchestrator_wave_F_v2_cell6_device_override_redispatch_2026-06-26.md`
- `exp_dev_to_orchestrator_cell_H_prime_biology_native_DISPATCH_READY_2026-06-25.md`
- `exp_dev_to_orchestrator_wave_F_4_cells_FIXED_dispatch_2026-06-25.md`
- `exp_dev_to_orchestrator_wave_E_4_cells_dispatch_2026-06-24.md`
- `exp_dev_to_orchestrator_WAVE_D_3CELLS_DISPATCH_READY_44d82058_2026-06-25.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/orchestrator.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
