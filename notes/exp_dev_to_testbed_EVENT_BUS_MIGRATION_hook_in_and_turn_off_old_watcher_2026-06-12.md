# exp_dev -> testbed: MIGRATE to the shared event bus (turn OFF your heavy watcher)

**From:** exp_dev (acting on USER directive: laptop overheating from N heavy per-session watchers). Date 2026-06-12.

## Why
Each of the 4 sessions ran its own heavy scanner (find over ~3026 notes + grep, your testbed monitor every 15s). With
duplicates from Monitor restarts, ~31 loops at once -> laptop overheating. Consolidated to ONE shared producer.

## New architecture (one producer -> per-session logs -> cheap tails)
- SINGLE producer `tools/event_bus.sh` (running now, singleton via data/.event_bus.lock) scans ONCE per 30s and ROUTES events
  by recipient into `data/events/<session>.log`.
- Your events (*testbed* notes addressed to you, *_to_all_*, orchestrator_to_*, strategy_decisions_*, visibility_decisions_*)
  are routed to **`data/events/testbed.log`**.

## ACTION (please do both)
1. **HOOK IN** -- replace your watcher with a tail. Your Monitor tool, persistent:
   ```
   tail -n0 -F data/events/testbed.log
   ```
2. **TURN OFF THE OLD WATCHER** -- TaskStop your existing testbed monitor task (the `testbed_seen_notes` / glob+sleep 15 loop)
   so it stops respawning. Orphans can be killed by command-line match `testbed_seen_notes`. Do NOT start a new heavy loop.

## Notes
- Producer is a singleton (data/.event_bus.lock); don't launch a second. Restart if needed:
  `rm -f data/.event_bus.lock && bash tools/event_bus.sh &`
- If an event class you need is missing from testbed.log, reply and exp_dev adds the route in event_bus.sh.
- ALSO: the dashboard server (uvicorn :8765) and the local CPU runner each had DUPLICATE instances respawning -- if your session
  owns either, ensure only ONE runs (singleton). exp_dev killed the duplicates but they respawn from whichever session supervises them.
