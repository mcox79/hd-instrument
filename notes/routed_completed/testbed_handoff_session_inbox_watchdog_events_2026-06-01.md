# Testbed handoff: session_inbox watchdog event class (consolidates with dashboard handoff)

**From**: orchestrator
**To**: testbed
**Date**: 2026-06-01
**Source**: `notes/strategy_request_to_strategy_research_inbox_watchdog_event_2026-06-01.md` (research routing; orchestrator-accepted)
**Coordinates with**: `notes/testbed_handoff_dashboard_session_coordination_v1_2026-06-01.md` (earlier dashboard handoff this turn; SAME problem space; CONSOLIDATE)

## TL;DR

Research surfaced the auto-ping gap orchestrator already routed to dashboard handoff. Their proposal: add 3 watchdog events (`research_inbox_new`, `testbed_inbox_new`, `strategy_inbox_new`) to `heartbeat_watchdog.py` as a "session_inbox" event class. **This IS Part C of the dashboard handoff under a different framing.** Consolidate them into one work stream.

## What to build

Per research routing — 3 events in one class, ~30-50 LOC in `heartbeat_watchdog.py`:

For each of {research, testbed, strategy}:
- `<session>_inbox_new` event
- `RESEARCH_INBOX_GLOB = notes/strategy_request_to_research_*.md`
- `TESTBED_INBOX_GLOB = notes/testbed_handoff_*.md` AND `notes/exp_dev_handoff_*.md`
- `STRATEGY_INBOX_GLOB = notes/strategy_request_to_strategy_*.md` AND `notes/strategy_request_to_exp_dev_*.md`
- Per-session watermark (file or in-memory state)
- `check_<session>_inbox()` function: glob + filter mtime > watermark; return list
- Main polling loop: emit event with cooldown
- Payload: list of pending inbox files + their mtimes + total count

Plus dashboard surface (Part A of the earlier dashboard handoff):
- `tools/dashboard/poller.py`: expose per-session inbox count + recent files
- `tools/dashboard/static/index.html`: surface in For You tab + per-session panels
- Importance HIGH if count >= 1
- Clickable to view file content

## How this consolidates with the earlier dashboard handoff

The dashboard handoff (`testbed_handoff_dashboard_session_coordination_v1_2026-06-01.md`) has 4 parts:
- Part A: per-session inbox indicators ← THIS handoff supplies the watchdog-event data source
- Part B: pipeline state view ← unchanged from earlier handoff
- Part C: auto-ping + manual-ping notification mechanism ← THIS handoff IS the auto-ping piece (Layer 1)
- Part D: session-staleness indicator ← unchanged from earlier handoff

Net: this handoff REFINES Parts A + C of the earlier handoff with concrete event specs from research. Don't treat as a separate build — fold into the dashboard work.

## Engineering scope estimate (consolidated)

- Watchdog events (this handoff specifies): ~30-50 LOC heartbeat_watchdog.py + glob configs
- Dashboard surfacing (per Part A from earlier handoff): ~50-100 LOC poller.py + index.html
- Manual ping button (per Part C Layer 2 from earlier handoff): ~30 LOC frontend write to status_log
- Watermark initialization for backlog suppression: orchestrator just bulk-archived the 31-file research backlog this turn; testbed can initialize watermark = max-mtime of remaining inbox files at deploy time

Total: ~150-250 LOC, ~1-2 days work, fits within the earlier dashboard handoff's ~1-2 day estimate.

## Recommended sequencing

1. **First**: ship watchdog events + dashboard surface for `research_inbox_new` only (cheapest; matches the immediate research-surfaced problem)
2. **Second**: extend to `testbed_inbox_new` + `strategy_inbox_new` (same pattern; trivial extension)
3. **Third**: ship manual ping button (lowest-priority; the watchdog auto-event closes the main pain point)

## Importance level decision

Research recommended HIGH. Orchestrator agrees: HIGH. Inbox-staleness has been the operational pain point all session; user explicitly called it out today. HIGH ensures the For You tab surfaces inbox depth visibly.

## Acceptance criteria (per the dashboard handoff)

- When a new routing file lands matching session's inbox glob, dashboard For You feed shows it within ~30s (next watchdog tick)
- Per-session panels show inbox depth count
- Click-through to file content from dashboard

## Sequencing vs other testbed work

Deferred behind:
- Week 0 H100 result ← DONE (GO; this turn)
- PP-3 Phase 2 reframe ← APPROVED (in progress)
- **PP-8 Week 2 feasibility smoke ← TODAY's biggest new commitment** (user authorized; ~$50-150 cloud H100; 3-phase Q-Former + QLoRA + Rescue C)

Dashboard + watchdog events should slot in AFTER PP-8 Week 2 Phase 1 dispatches (a parallel local-engineering track that doesn't block the cloud H100 work).

## Files referenced

- `tools/orchestrator/heartbeat_watchdog.py` (extension target)
- `tools/dashboard/poller.py` + `tools/dashboard/static/index.html` (surface targets)
- `notes/strategy_request_to_strategy_research_inbox_watchdog_event_2026-06-01.md` (research source routing)
- `notes/testbed_handoff_dashboard_session_coordination_v1_2026-06-01.md` (earlier dashboard handoff this consolidates with)
- `notes/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` (research surfaced backlog; orchestrator bulk-archived this turn — Path A)

## Closing this routing

Move to `routed_completed/` when testbed dispatches Phase 1 of the watchdog-events build (initiate, not complete).
