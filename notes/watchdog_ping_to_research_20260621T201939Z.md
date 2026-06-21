# WATCHDOG -> research: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260621T201939Z
**Reason:** No activity signal from session 'research' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `orchestrator_to_all_blocker_ping_173_CLEAR.md`
- `blocker_ping_to_all_20260621T195537Z_n173.md`
- `orchestrator_to_research_expdev_N1_v3_1_is_realdata_N2_baseline_handoff_2026-06-21.md`
- `testbed_to_all_blocker_ping_172_CLEAR.md`
- `orchestrator_to_all_blocker_ping_172_CLEAR.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/research.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
