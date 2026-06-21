# WATCHDOG -> testbed: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260621T002016Z
**Reason:** No activity signal from session 'testbed' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `skunkworks_to_all_blocker_ping_133_CLEAR.md`
- `research_to_all_blocker_ping_133_CLEAR.md`
- `blocker_ping_to_all_20260620T235538Z_n133.md`
- `skunkworks_to_orchestrator_cc_all_CERT_589_LANDED_lever4_depth_refuse_layer3_reciprocal_2026-06-20.md`
- `research_to_skunkworks_testbed_orch_expdev_LAYER_4_DIRECTOR_CROSSCHECK_LEVER_4_depth_axis_refuse_gate_CONCUR_composition_framing_aligned_2026-06-20.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/testbed.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
