# Orchestrator

Single-session dispatch model for the hd-instrument multi-agent system. Replaces
the 7-session-with-independent-timers architecture with one orchestrator that
spawns role-specific sub-agents on file-system events.

## Layout

```
tools/orchestrator/
  README.md                  # this file
  orchestrator_prompt.md     # cold-start bootstrap prompt for the orchestrator session
  dispatch.py                # file-system event detector; emits one EVENT line per change
  agents/
    queue_health.md          # Phase 1 sub-agent
    visibility.md            # Phase 2 (planned)
    research.md              # Phase 3 (planned)
    exp_dev.md               # Phase 4 (planned)
    strategy.md              # Phase 5 (planned)
```

## How it runs

1. Open a Claude Code session pointed at `d:\AI\hd-instrument`.
2. Paste the contents of `orchestrator_prompt.md` as the first message.
3. The session reads `notes/orchestrator_migration_status.md`, arms `Monitor`
   running `python tools/orchestrator/dispatch.py`, and waits.
4. When dispatch.py emits an EVENT line (verdict landed, routing file written,
   queue depth changed), the Monitor notification wakes the orchestrator. The
   orchestrator parses the event and spawns the matching sub-agent.

## Event line format

```
EVENT <kind> <payload-json>
```

| Kind | Payload | Trigger |
|---|---|---|
| `ready`         | `{"watching": "<repo>"}` | dispatch.py startup |
| `verdict`       | `{"name", "verdict", "verdict_msg", "mtime_iso"}` | new entry in `data/local_dashboard_snapshot.json` `recent_verdicts[]` |
| `routing`       | `{"file", "from", "to"}` | new `notes/*_request_to_<role>_*.md` file |
| `queue_change`  | `{"pending", "previous"}` | `gpu.queue_pending_count` changed |
| `stale_runner`  | `{"runner_id", "minutes_since_beat"}` | gpu/cpu runner heartbeat >5 min old |
| `stopped`       | `{}` | dispatch.py shutting down (Ctrl-C) |

## Phase 0 scope (this commit)

- Dispatch script watches `recent_verdicts`, routing files, queue depth, runner heartbeats.
- Queue Health sub-agent defined (Phase 1 target).
- No experiment scripts modified (event_outcomes direct-write deferred until Phase 2).
- No live sessions stopped yet; only META cron will be deleted to start.

## Phase 1 target

Orchestrator dispatches `queue_health` sub-agent on `queue_change` and `stale_runner`
events for 24 hours with no regressions. When verified, Queue Health live session
is closed.
