# exp_dev -> research: MIGRATE to the shared event bus (turn OFF your heavy watcher)

**From:** exp_dev (acting on USER directive: laptop overheating from N heavy per-session watchers). Date 2026-06-12.

## Why
Each of the 4 sessions was running its OWN heavy scanner (find over ~3026 notes + grep + ssh every 5-30s; your
research_seen_v5 monitor runs `find notes ... ; sleep 5` -- the hottest one). With duplicates from Monitor restarts, ~31
loops were running at once -> laptop overheating. We consolidated to ONE shared producer.

## New architecture (one producer -> per-session logs -> cheap tails)
- A SINGLE producer `tools/event_bus.sh` (running now, PID in data/.event_bus.lock, singleton) does the heavy scan ONCE per
  30s and ROUTES events by recipient into `data/events/<session>.log`.
- Your session's events (testbed_to_*, exp_dev_to_*/handoffs to you, orchestrator_to_research_*, strategy_request_to_research_*,
  strategy_decisions_*, visibility_decisions_*) are routed to **`data/events/research.log`**.

## ACTION (please do both)
1. **HOOK IN** -- replace your watcher with a near-zero-cost tail. Use your Monitor tool, persistent:
   ```
   tail -n0 -F data/events/research.log
   ```
   (no find, no grep, no ssh -> ~0% CPU; you still get every routed event as a notification line.)
2. **TURN OFF THE OLD WATCHER** -- TaskStop your existing research monitor task (the `research_seen_v5` / `find notes ... sleep 5`
   loop) so it stops respawning. If orphaned bash loops remain, they can be killed by command-line match `research_seen_v5`.
   Do NOT start a new heavy find/grep loop -- the producer now owns scanning.

## Notes
- The producer is a singleton (data/.event_bus.lock); don't launch a second one. To restart it if ever needed:
  `rm -f data/.event_bus.lock && bash tools/event_bus.sh &`
- Routing is by filename convention; if you find an event class missing from research.log, reply and exp_dev will add the
  route in event_bus.sh.
