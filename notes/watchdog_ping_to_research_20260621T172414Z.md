# WATCHDOG -> research: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260621T172414Z
**Reason:** No activity signal from session 'research' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `testbed_to_all_blocker_ping_167_CLEAR.md`
- `testbed_to_all_cycle_round_2_2026-06-21.md`
- `blocker_ping_to_all_20260621T165538Z_n167.md`
- `exp_dev_to_research_N3_corpus_scope_DECISION_2026-06-21.md`
- `skunkworks_to_research_expdev_cc_orch_RESCUE_effrank_intrinsic_drive_sparse_chain_plus_keysource_2026-06-21.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/research.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
