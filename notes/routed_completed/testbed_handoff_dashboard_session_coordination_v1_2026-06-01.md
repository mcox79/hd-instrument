# Testbed handoff: Dashboard session-coordination tab (user-requested 2026-06-01)

**From**: orchestrator
**To**: testbed
**Date**: 2026-06-01
**Priority**: MEDIUM (deprioritize behind Week 0 H100 result + PP-3 Phase 2)
**Estimated cost**: ~1-2 days engineering

## Why now

User feedback during today's verdict-cascade session: "I have a hard time understanding the larger picture here between the 3 sessions. Also — each session doesn't seem to check for messages that often — I have to ping them myself."

Two distinct problems:
1. **Visibility gap**: no single view of cross-session work-in-flight (experiments planned, in design, in flight, verdict-pending; per-session attribution)
2. **Notification gap**: sessions don't auto-check for routings; the user is the manual ping

## What to build

### Part A — Cross-session messaging tab

New dashboard tab (or extension of existing For-You feed) showing:

- **Per-session inbox depth indicator**: count of unread routing files for each of {research, testbed, orchestrator}. Reads from `notes/strategy_request_to_<session>_*.md` + `notes/testbed_handoff_*.md` + `notes/exp_dev_handoff_*.md` + `notes/cloud_handoff_*.md`. "Unread" = file exists in `notes/` (not yet moved to `routed_completed/`).
- **Recent inter-session messages timeline**: chronological list of routings filed in last 24h, with from-session / to-session / type / summary / status (open/closed). Click-through to file content.
- **Session-pair message stats**: heatmap or compact table showing flow counts e.g. "research → orchestrator: 3 routings open; orchestrator → testbed: 5 routings open".

### Part B — Pipeline state view

Extension to existing experiment views OR new tab showing experiment lifecycle:

- **Planned**: routing files requesting experiments (`strategy_request_to_exp_dev_*`) that haven't been scaffolded yet
- **In design**: scaffolded scripts pre-queue (exists in `experiments/` but not in any queue.json yet) — small expected count
- **In flight**: from `data/remote_state_cache.json` queue.running + queue.pending
- **Awaiting verdict**: status=completed/failed in queue.json but not yet processed by verdict_handler (heuristic: check verdict_last_seen_ts in heartbeat_watchdog_state.json vs queue ended_at)
- **Done**: verdict_handler-processed (cap_map version-stamped)

Plus: attribution to source session (research-requested vs testbed-requested vs orchestrator-direct).

### Part C — Notification mechanism

Two layers:

1. **Auto-ping on new inbox entry** — heartbeat_watchdog detects new file matching session's inbox pattern; emits status_log entry with importance=HIGH (so it surfaces in For-You feed). This already exists for some inbox patterns per `feedback_watchdog_full_event_set` memory; extend to cover all routing-file types comprehensively.

2. **Manual ping button** — clickable in the new tab that writes a status_log entry `{event_kind: 'user_ping', source: 'user', target_session: '<research|testbed|orchestrator>', importance: 'HIGH'}`. The target session sees this on their next dashboard read.

Optional v2: an `[ack]` button next to each routing file that, when clicked, writes a status_log entry indicating the user has READ the routing (but not necessarily acted on it). Useful for the user to clear "I've seen this" state without triggering session work.

### Part D — Session staleness indicator

When a session hasn't written a status_log entry or commit in >N hours, the dashboard shows a "stale" badge. Helps the user identify "session went quiet; might need ping" without manually checking commit logs.

Suggested N = 2 hours for active work hours; 8 hours otherwise. Heartbeat_watchdog can derive.

## Scoping recommendations

- **Part A is the highest-leverage** (closes the visibility gap; estimated ~4-6h)
- **Part B is the second-highest** (closes the larger-picture gap; estimated ~6-8h; depends on pipeline-state derivation logic which may need a few helper queries)
- **Part C layer 1 (auto-ping) is mostly free** (extend existing heartbeat_watchdog event set; ~1-2h)
- **Part C layer 2 (manual ping button) is small** (status_log write from frontend; ~1-2h)
- **Part D is a nice-to-have** (~2-3h; could be deferred to v2)

Total: ~13-20h = ~1-2 days engineering for full scope; could be staged.

## Sequence recommendation

- **Day 1**: Part A + Part C layer 1 + Part D (the closure-of-visibility-gap items)
- **Day 2**: Part B + Part C layer 2 (the larger-picture + manual-ping items)

If only Day 1 ships before bigger priorities preempt, the user's main pain point ("sessions don't check messages often") is substantially addressed.

## Sequencing vs other testbed work

- **Defer behind Week 0 H100 result** (gates Week 1 GO/NO-GO; the strategic decision dwarfs this)
- **Defer behind PP-3 Phase 2 design start** (compliance-first reframe; user-approved this turn; ~6-9 days)
- **Pre-empt other smaller items**: this could ship before D7 implementation, before PP-12 audit API engineering, before any cosmetic fixes — it directly addresses a user-stated pain point

## Files of interest

- `tools/dashboard/poller.py` (existing dashboard data feed)
- `tools/dashboard/static/index.html` (existing UI)
- `tools/orchestrator/heartbeat_watchdog.py` (existing event emitter; extend for auto-ping)
- `data/orchestrator_status_log.jsonl` (existing event store; surfaces in For-You)
- `data/heartbeat_watchdog_state.json` (existing watchdog state)
- `notes/session_synchronization_v1.md` (session model + cadence patterns)
- `notes/active_protocols.md` (PROT-013 watchdog full-event-set; reference for Part C)
- Memory: `feedback_orchestrator_status_visibility`, `feedback_for_you_tab_primary_channel`, `feedback_watchdog_full_event_set`

## Acceptance criteria

- Part A: I can see at-a-glance which session has unread routings + how many
- Part B: I can see what experiments are at each lifecycle stage with source-session attribution
- Part C layer 1: When a new routing file lands in a session's inbox, the dashboard's For-You feed shows it within ~30s (next watchdog tick)
- Part C layer 2: I can click a button to send a "ping" to a specific session that surfaces in their dashboard view on next read

## Closing this routing

Move to `routed_completed/` when testbed dispatches the build (not when complete).
