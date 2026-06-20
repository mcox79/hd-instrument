# WATCHDOG -> research: ACTION REQUIRED - heartbeat-stale

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260620T175201Z
**Reason:** No activity signal from session 'research' in the stale window.

## ACTION REQUIRED (do this on receipt; takes one Bash call)

Run this exact command to mark yourself alive + stop future ping spam from the watchdog:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/research.timestamp
```

Then continue with your standing-reactive pipeline (cycle-check filesystem for any substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you. One `touch` per turn-end is enough -- the watchdog ignores you for 10 min after each touch.

## If you have substantive work pending

Process it now (e.g., reactive 2nd-witness on recent cert events, atomization checks, etc.) THEN do the heartbeat touch at the end of your turn.
