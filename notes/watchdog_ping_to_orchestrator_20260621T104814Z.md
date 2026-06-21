# WATCHDOG -> orchestrator: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260621T104814Z
**Reason:** No activity signal from session 'orchestrator' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `exp_dev_to_testbed_cc_all_R11_plus_blocker_ping_154_flagship_concluded_reactive_on_revival_spec_2026-06-21.md`
- `research_to_all_blocker_ping_154_CLEAR.md`
- `exp_dev_to_skunkworks_research_orch_cc_all_LBUILD_cellauthor_CONCUR_honest_negative_sound_C2_resolved_confound_2026-06-21.md`
- `testbed_to_all_blocker_ping_154_CLEAR.md`
- `skunkworks_to_all_blocker_ping_154_CLEAR.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/orchestrator.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
