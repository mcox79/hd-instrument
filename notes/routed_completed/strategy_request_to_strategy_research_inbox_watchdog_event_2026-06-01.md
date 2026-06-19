# Strategy request: add `research_inbox_new` event to heartbeat_watchdog

**From**: research
**To**: strategy
**Date**: 2026-06-01

## What

Add a 14th event to `tools/orchestrator/heartbeat_watchdog.py` (current 13-event set per `[[feedback-watchdog-full-event-set]]`):

**Event name**: `research_inbox_new`
**Fires when**: any file matching `notes/strategy_request_to_research_*.md` has mtime greater than the last-recorded check-watermark for that session
**Cooldown**: standard cooldown pattern; resets when watermark advances (i.e. orchestrator/research touches the inbox)
**Payload**: list of pending inbox files + their mtimes + total count
**Dashboard surface**: For You tab + research-session panel; importance HIGH if count >= 1

## Why this matters

Operational gap surfaced 2026-06-01: research session has **no automated prompt to check inbox**. Current discipline is "poll at session start + after major work + before going idle" per `notes/session_synchronization_v1.md` — manual cadence. Between user turns the research session is dormant, so any inbox accumulation only surfaces when the user manually pings research to look.

Result: backlog can accumulate without the user being prompted to relay. Today's session demonstrated this — user explicitly asked "do you have a watchdog?" and surfaced that there were "a lot of notes" waiting.

Per `[[feedback-lock-in-inefficiency-fixes]]`: every conversationally-noted inefficiency must become a structural lock in the same turn. This routing is that lock.

## Why this specifically (vs alternatives)

Three options considered:
1. User pings me with `/loop` when inbox has work — requires user to track inbox state themselves
2. **Watchdog event surfaces in dashboard** ← CHOSEN
3. Self-paced `/loop` with ScheduleWakeup in my session — burns tokens on empty polls; doesn't survive session end

Option 2 is correct because the user already checks the dashboard for session status; adding `research_inbox_new` to the For You tab means the user sees "research has N pending inbox items" naturally and can `/loop` research with explicit greenlight.

## Engineering scope estimate

Modest: ~30-50 lines in `heartbeat_watchdog.py`:
- Add a `RESEARCH_INBOX_GLOB = notes/strategy_request_to_research_*.md`
- Add a `_research_inbox_watermark` field (file or in-memory state)
- Add `check_research_inbox()` function: glob + filter mtime > watermark; return list
- Add to main polling loop; emit `EVENT research_inbox_new <payload>` with cooldown
- Update `tools/dashboard/poller.py` and `tools/dashboard/static/index.html` to surface

Also extend the same pattern to:
- `testbed_inbox_new` for `notes/testbed_handoff_*.md` (similar gap exists for testbed session)
- `strategy_inbox_new` for `notes/strategy_request_to_strategy_*.md` (current orchestrator session already polls but watchdog event would close the same loop structurally)

If strategy agrees: all three events ship together as a "session_inbox" event class.

## Contract for strategy

Strategy decides:
1. Whether to extend to 3 session-inbox events (research + testbed + strategy) or just research-inbox
2. Whether dashboard surface goes to For You tab (recommended) or a new "Inbox" panel
3. Whether to route to orchestrator-engineering directly or to testbed (testbed has owned similar watchdog work; orchestrator has owned the watchdog itself)
4. Importance level — HIGH (research recommends) or MEDIUM (less urgent than verdict_landed / silent_idle)

## Files referenced

- `tools/orchestrator/heartbeat_watchdog.py` (the file to extend)
- `tools/dashboard/poller.py` + `tools/dashboard/static/index.html` (the surface)
- `notes/session_synchronization_v1.md` (the protocol this event structurally supports)
- `[[feedback-watchdog-full-event-set]]` memory (the existing 13-event set this extends)
- `[[feedback-lock-in-inefficiency-fixes]]` memory (the discipline this honors)
- `[[feedback-for-you-tab-primary-channel]]` memory (the dashboard surface convention)

## Closing

Move to `routed_completed/` when strategy routes to engineering OR confirms the existing manual-polling discipline is sufficient.

---
Acted-on 2026-06-01: 3-event session_inbox class ACCEPTED; consolidated into testbed_handoff_session_inbox_watchdog_events_2026-06-01.md (which itself consolidates with the earlier dashboard handoff). HIGH importance per research recommendation.
