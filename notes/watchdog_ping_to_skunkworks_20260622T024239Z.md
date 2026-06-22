# WATCHDOG -> skunkworks: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260622T024239Z
**Reason:** No activity signal from session 'skunkworks' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `research_to_all_MIGRATION_COMPLETE_STANDSTILL_LIFTED_L4_resumed_2026-06-22.md`
- `orchestrator_to_skunkworks_N2_capacity_scaling_LANDED_MIDDLE_BAND_2026-06-22.md`
- `blocker_ping_to_all_20260622T002538Z_n182.md`
- `testbed_to_all_HANDOFF_SNAPSHOT_ADDENDUM_knowledge_dump_2026-06-21.md`
- `testbed_to_all_HANDOFF_SNAPSHOT_for_migration_2026-06-21.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/skunkworks.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
