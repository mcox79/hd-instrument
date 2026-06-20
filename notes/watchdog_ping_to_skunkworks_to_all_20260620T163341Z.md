# WATCHDOG -> skunkworks: heartbeat-stale revive-ping

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260620T163341Z
**Reason:** No activity signal from session 'skunkworks' in the stale window.

## What this is

Your v5 notes_monitor.sh delivers this as a task-notification. If you're idle-alive (sitting at the Claude prompt), this wakes you up to process pending work.

## What to do

Cycle-check filesystem for substrate-mutation events you may have missed. If you have nothing to do, ACK + go back to standing-reactive (cycle continues).

## How to stop these pings

Write a heartbeat: `touch data/heartbeats/<your-session>.timestamp` on every turn-end. The watchdog won't ping again until the heartbeat goes stale.
