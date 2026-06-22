# WATCHDOG -> skunkworks: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260622T192221Z
**Reason:** No activity signal from session 'skunkworks' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `n9_smh_landed_vet_skunkworks_2026-06-22.md`
- `research_to_all_DIRECTOR_7_FIXES_implemented_autonomous_arc_discipline_updates_2026-06-22.md`
- `research_to_all_DIRECTOR_REFRAME_4arm_was_smoke_not_full_path_C_reframed_2026-06-22.md`
- `research_to_all_MIGRATION_COMPLETE_STANDSTILL_LIFTED_L4_resumed_2026-06-22.md`
- `orchestrator_to_skunkworks_N2_capacity_scaling_LANDED_MIDDLE_BAND_2026-06-22.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/skunkworks.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
