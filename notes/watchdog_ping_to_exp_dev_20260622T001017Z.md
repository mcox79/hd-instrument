# WATCHDOG -> exp_dev: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260622T001017Z
**Reason:** No activity signal from session 'exp_dev' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `testbed_to_all_HANDOFF_SNAPSHOT_for_migration_2026-06-21.md`
- `research_to_all_blocker_ping_181_CLEAR.md`
- `blocker_ping_to_all_20260621T235537Z_n181.md`
- `research_to_all_PHASE2_pre_staging_role_subagent_defs_hybrid_arch_disciplines_state_migration_2026-06-21.md`
- `research_to_all_ACK_USER_STANDSTILL_MIGRATE_skunkworks_HYBRID_endorsed_phase2_prep_2026-06-21.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/exp_dev.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
