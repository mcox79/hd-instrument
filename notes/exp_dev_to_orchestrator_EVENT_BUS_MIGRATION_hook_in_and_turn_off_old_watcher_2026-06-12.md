# exp_dev -> orchestrator: MIGRATE to the shared event bus (turn OFF your heavy watcher)

**From:** exp_dev (acting on USER directive: laptop overheating from N heavy per-session watchers). Date 2026-06-12.

## Why
4 sessions each ran a heavy scanner; with Monitor-restart duplicates ~31 loops ran at once (incl. ~5 copies of
watch_for_orchestrator.py) -> laptop overheating. Consolidated to ONE shared producer.

## New architecture (one producer -> per-session logs -> cheap tails)
- SINGLE producer `tools/event_bus.sh` (running now, singleton via data/.event_bus.lock) scans queues + notes ONCE per 30s and
  ROUTES events by recipient into `data/events/<session>.log`.
- Your events (*_to_orchestrator_*, *_to_all_*, research_decisions_*, strategy_decisions_*, visibility_decisions_*,
  orchestrator_to_{research,exp_dev,testbed}_* echoes) are routed to **`data/events/orchestrator.log`**.

## ACTION (please do both)
1. **HOOK IN** -- replace watch_for_orchestrator.py with a tail. Your Monitor tool, persistent:
   ```
   tail -n0 -F data/events/orchestrator.log
   ```
2. **TURN OFF THE OLD WATCHER(S)** -- TaskStop your watch_for_orchestrator.py Monitor task(s). There were ~5 copies respawning;
   ensure none remain (kill by command-line match `watch_for_orchestrator`). Do NOT relaunch the python watcher.

## Notes
- Producer is a singleton (data/.event_bus.lock). Restart if ever needed:
  `rm -f data/.event_bus.lock && bash tools/event_bus.sh &`
- The producer routing is in tools/event_bus.sh; orchestrator may want to OWN/relocate the producer to a session that stays up
  longest (currently launched from the exp_dev session as a detached background process -- it dies if that shell exits). A
  Windows Scheduled Task or a dedicated always-on session would be more robust. exp_dev's recommendation: orchestrator owns it.
- If an event class is missing from orchestrator.log, reply and exp_dev adds the route.
