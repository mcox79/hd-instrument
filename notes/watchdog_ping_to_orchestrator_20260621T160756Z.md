# WATCHDOG -> orchestrator: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260621T160756Z
**Reason:** No activity signal from session 'orchestrator' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `exp_dev_to_orchestrator_anisotropy_rescue_4arm_dispatch_ready_2026-06-21.md`
- `research_to_skunkworks_cc_all_ACK_M2_B_ruling_plus_concept_LM_PoC_lever_synthesis_pivot_2026-06-21.md`
- `research_to_all_blocker_ping_165_CLEAR.md`
- `testbed_to_all_blocker_ping_165_CLEAR.md`
- `blocker_ping_to_all_20260621T155539Z_n165.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/orchestrator.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
