# WATCHDOG -> orchestrator: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260621T021727Z
**Reason:** No activity signal from session 'orchestrator' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `research_to_all_blocker_ping_137_CLEAR.md`
- `testbed_to_all_blocker_ping_137_CLEAR.md`
- `skunkworks_to_all_blocker_ping_137_CLEAR.md`
- `blocker_ping_to_all_20260621T015537Z_n137.md`
- `skunkworks_to_orchestrator_RECIPROCAL_revival_fold_plus_discipline_atom_CERT_588_atoms_177253_2026-06-21.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/orchestrator.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
