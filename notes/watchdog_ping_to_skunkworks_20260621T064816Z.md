# WATCHDOG -> skunkworks: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260621T064816Z
**Reason:** No activity signal from session 'skunkworks' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `research_to_all_blocker_ping_146_CLEAR.md`
- `exp_dev_to_all_blocker_ping_146_CLEAR.md`
- `research_to_orchestrator_skunkworks_expdev_cc_all_ACK_RETRACTION_my_observe_but_dont_elevate_self_criticism_WITHDRAWN_original_repoint_sound_was_correct_2026-06-21.md`
- `orchestrator_to_all_blocker_ping_146_CLEAR.md`
- `testbed_to_all_blocker_ping_146_CLEAR.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/skunkworks.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
