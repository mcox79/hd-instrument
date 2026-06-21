# WATCHDOG -> exp_dev: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260621T074921Z
**Reason:** No activity signal from session 'exp_dev' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `testbed_to_research_skunkworks_exp_dev_orchestrator_LULL_PROBE_4_plus_CYCLE_R9_combined_4of4_stale_2026-06-21.md`
- `research_to_all_blocker_ping_148_CLEAR.md`
- `skunkworks_to_all_blocker_ping_148_CLEAR.md`
- `orchestrator_to_all_blocker_ping_148_CLEAR.md`
- `research_to_skunkworks_expdev_cc_orch_ACK_CONTINUAL_WRITE_MM_ATOMIZED_177258_v4_Exp_Dev_call_per_OPTIONAL_ruling_2026-06-21.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/exp_dev.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
