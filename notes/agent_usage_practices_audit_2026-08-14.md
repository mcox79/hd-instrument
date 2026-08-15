# Agent-usage practices audit — 2026-08-14

Owner request: measure how agents are being used (background/parallel/efficiency/
accountability), drill best practice against measured behaviour, implement mechanism over
advice. Full transcript of session `139818eb` parsed: `C:\Users\marsh\.claude\projects\D--AI\139818eb-7f83-457e-928d-a8db02a0214d.jsonl`,
5693 lines, main-thread-only (`isSidechain:false`) records, 2026-08-12T14:49Z to
2026-08-14T23:5xZ. Parser: `scratch/measure_agent_usage.py` + `scratch/measure_agent_usage_2.py`
(promote if a durable file cites their numbers again). Raw output:
`scratch/agent_usage_measurements.json`.

**Note on `notes/active_protocols.md`:** that file's own header (2026-08-12) declares it
RETIRED — "DO NOT ACT ON ANYTHING BELOW", superseded by `CLAUDE.md` + the SessionStart hook.
No entry in it postdates the retirement. My dispatch brief assumed it is the live PROT store
and that I am its sole writer; that assumption is stale by the file's own more recent banner
(evidence-discipline rule 4: re-verify before citing, a note is a measurement with a
timestamp). I did not write to it. New rules below are instead drafted as a `CLAUDE.md`
patch (not applied — concurrent writers) plus this note.

## 1. Measured numbers

**Spawns.** 235 `Agent` tool_use calls, main thread only. `run_in_background=true` 172
(73.2%), explicitly `false` 0, unset 63 (26.8%) — CLAUDE.md says pass it explicitly on
every spawn; over a quarter don't. subagent_type mix: general-purpose 139, hdi_exp_dev 33,
hdi_skunkworks 21, hdi_research 17, hdi_testbed 9, exp_dev 7, meta_audit/memory_curator/
research/Explore/hdi_orchestrator the rest. Model: opus 95, sonnet 42, inherited/unset 98
(inheriting is explicitly endorsed by CLAUDE.md, not a violation by itself).

**Yield-after-dispatch.** Grouped assistant messages into 110 "turns" containing >=1
background dispatch (turn boundary = between two genuinely-typed user messages, tool-result
carrier records excluded). Of those, **83/110 (75.5%) show tool calls or >50 chars of text
in the SAME turn within 10s of the dispatch** — continued generation, not yield. 25/110
(22.7%) show continuation only after a >=10s gap (plausibly a legitimate
notification-triggered new turn, not a same-breath violation). **Split at the hook's install
timestamp (2026-08-13T23:07:59Z, from `data/hooks/agent_dispatch_hook.log`): BEFORE
install, immediate-violation rate 63.9% (46/72 turns); AFTER install, 97.4% (38/39).**
Compliance got measurably worse, not better, after the hook landed.

**Hook firing.** `agent_dispatch_hook.log`: 164 lines total, mode counts `agent` 80,
`probe` 78, `pre` 6, spanning 2026-08-13T23:07:59 to 2026-08-14T19:51:48 (the last two
entries are this dispatch's own env, `CLAUDE_CODE_AGENT_TYPE=team-lead` — confirms it fires
for a meta_audit-class dispatch too). The hook reliably fires and reliably injects the
reminder text; it does not enforce, and the transcript shows the reminder is not obeyed at
a rising rate.

**Idle gaps.** 261 gaps >60s between consecutive main-thread events, summing 51.5h across
the ~57h span. Classified by what closes the gap: 183 gaps (31.3h) end in a background-agent
completion notification — plausibly legitimate wait. **63 gaps (17.26h) end in a genuinely
typed user message — the Director produced nothing until the user broke the silence.** 5
end in a tool-result/other record (0.43h), 10 end in another assistant-attributed event
(1.4h, likely a parsing edge case), 1 in a local-command-caveat (1.1h). 4 gaps fall fully
inside the 2026-08-14T21:30-23:30Z usage-limit window, summing 99.5 min. The three largest
real-idle gaps (191min, 179min, 151min) all end with the user asking a status question
("what is your recommendation", "what's the update", "what are the permission issues") —
direct evidence of the "sat idle ~2h" complaint.

**Main-thread serial chains.** 19 runs of >=3 consecutive assistant messages using only
Edit/Read/Write/Bash/PowerShell/Grep/Glob with no interleaved Agent call, 219 messages
total. The largest is 93 messages (52 Edit, 34 Bash, 6 Read, 1 Write) at
2026-08-14T21:34:02-21:56:48Z — coincides exactly with the weekly usage-limit firing window
found in the transcript (21:28-21:36Z rate-limit-related timestamps) and immediately
precedes the 86.9-minute idle gap that ends with the user asking "are you idle right now?".

**Relay.** 246 background-completion notifications reached the main thread. 209 (85%) are
followed by an assistant message carrying <30 chars of text before the next action — i.e.
mostly not relayed as visible prose before something else happens.

**Parallelism.** 0/235 spawns were batched — every Agent-call-bearing message contains
exactly 1 Agent tool_use. The 5-agent budget was never exercised as true concurrent
dispatch; whatever parallelism exists is serialized across separate turns, not
single-message batching.

**False dispatch (strict signature: message text starts with
Dispatching/Spawning/Launching/"I'll dispatch" etc. AND no `Agent` tool_use in that
message).** 3 matches in the whole transcript (lines 528, 598, 3143). In all 3, the actual
Agent call appears in the very next assistant message — a claim/action ordering gap, not a
dispatch that never happened. By this signature, zero true "claimed but never dispatched"
events are present in this transcript; the owner's "at least 3x" recollection may refer to
a different session file, a Skill-tool dispatch, or a case this text-pattern signature
under-detects (e.g. free-form phrasing not matching the regex).

**Fan-out token cost.** Session-wide (2026-08-12 14:49Z to now): output_tokens 3,491,146,
cache_creation_input_tokens 27.86M, cache_read_input_tokens 644.4M, across 1563
usage-bearing assistant messages. Average ~14.9k output tokens per Agent-bearing message
(rough; not spawn-attributed cost, whole-session average).

## 2. Coordinator-supplied findings, independently verified

**Watchdog "cron" already exists and already fails.** `notes/watchdog_ping_to_<role>_<ts>.md`:
**1585 files**, 15.7% of the 10,081 `.md` files in `notes/`, spanning 2026-08-12T15:53Z to
now, produced roughly every 10 minutes across 5 roles by the Windows Scheduled Task
`hd_session_watchdog` (State=Running continuously; script `tools/hd_session_watchdog.py`).
Its own docstring says its delivery path is each session's `v5 notes_monitor.sh` — a
Phase-2, multi-session-fleet mechanism that CLAUDE.md's "Notes directory (single-session
model)" section says is dead. The one thing that actively reads `notes/`
(`tools/dashboard/server.py`) explicitly filters `watchdog_ping`/`blocker_ping` files OUT
of its scans (lines ~901, 993, 1081, 1118) rather than acting on them. **This is the direct,
evidenced answer to "should we have a cron that spurs action": we already have one, firing
reliably, and it produces zero effect because its consumer no longer exists and the one
live reader ignores it by name.** The fix is not "add a cron"; it's either retire the task
(out of my mandate — it predates this session, "only stop/kill what this session started")
or repoint its delivery at something that reads it. Separately, `Get-ScheduledTask` shows 5
currently-`Disabled` `hd_*` tasks (`hd_metrics_sync`, `hd_orchestrator_watchdog` — last run
2026-07-17, ~28 days — `hd_orch_daily_audit`, `hd_orch_daily_research_drill`,
`hd_orch_scope_expansion`): a fresh recurrence of the exact silent-disable pattern already
on record in CLAUDE.md (11 tasks / 12 days; KB ingest / 6 days).

**KB is stale right now.** `tools/director_kb_freshness_check.py` (run live during this
audit): `scan_gap=5428s index_age=3133s n_failed_ingests=4 coverage_ok=True` —
confirms the coordinator's report; queries are answering ~90-minute-old content with 4
recent failed ingest attempts.

**Literature-cache "empty means absent" defect — root cause confirmed, not disobedience.**
`python tools/literature_cache.py find --keyword conjunctive` and `--keyword perirhinal`
both returned a bare `NOT CACHED`, even though
`notes/research_context_binding_conjunctive_coding_and_replay_necessity_2026-08-11.md`
(87KB) covers exactly that. Root cause verified: `data/literature_cache/index.jsonl` holds
65 entries, **100% retrieved_utc=2026-08-13** — it is a bibliography-of-registered-papers
cache seeded once, structurally blind to anything before or after that date, not a
topic-coverage index over `notes/`. Agents used it as if it answered "has this topic been
researched" and read an empty bibliography match as "topic unresearched" — the standing
"absence claim requires enumeration" rule, in a new place. **Fixed** (see Part 3): the bare
`NOT CACHED` message now carries the caveat inline.

**research_field_advisor.py stale**, file dated May 23 (pre-pivot); not independently
re-verified for neuroscience-field coverage beyond file age (budget).

**Orphaned-fan-out spend and stopped-agent claims**: reported by the coordinator
(process-level state, 9 agents stopped, ~280k tokens on the conjunctive-coding re-scan).
Not independently verifiable by me from the transcript alone (process state is ephemeral);
taken as coordinator-reported, not self-verified. Worth a detector: "a spawning agent's own
turn ends having only dispatched further sub-agents, with no artifact written" is the
subagent-level twin of the Director's own false-dispatch signature above and should be
checked the same way (no Write/Edit tool_use anywhere in that agent's sidechain before its
final message) in a future audit with sidechain access.

## 3. Implemented this cycle

1. `tools/literature_cache.py` `find` with no match now prints the absence-caveat
   (self-test still passes: `SELF-TEST PASS: write-guard, no-clobber guard, byte-identical
   repeat, find, sha256.`).
2. `tools/clear_watchdog_pings.py` — retention tool for the 1585 dead-consumer ping files,
   same guard pattern as `clear_scratch.py` (refuses non-pattern filenames and anything
   outside `notes/`, dry-run default, no `rm`). `--self-test` passes: guard rejects
   `active_protocols.md` and a path outside `notes/`, removes only the matching aged file.
   Does not touch the scheduled task itself (out of mandate).
3. `mcp__nimbalyst-host__schedule_wakeup` armed once, 1800s delay, as a live test of the
   cron/hook question (see Part 4) — `wakeupId=wakeup-1786752333297-wr0hqf6`,
   fires 2026-08-15T00:35:33Z. Self-limiting prompt: checks for real recent user activity
   before acting, relays any unrelayed report, dispatches the next independent delegated
   item if genuinely idle, and re-arms itself — explicitly framed to the session as a
   proof-of-concept firing, not a standing cadence, pending owner confirmation.

## 4. Cron/hook question — answered with evidence, not asserted

A **hook** (SessionStart/PostToolUse/Stop) cannot solve pure elapsed-idle-time nudging: it
is event-triggered only, and 51.5h of gaps in this transcript include stretches where
literally no tool event occurs to hang a hook off. The existing PostToolUse hook proves
this directly — it fires reliably on every Agent dispatch (80/80 agent-mode log entries,
confirmed firing for this very dispatch) but cannot fire on "nothing happened for 30
minutes", because there is no tool event to trigger it.

An **OS cron** is the mechanism already tried twice and already failed twice per CLAUDE.md
(11 tasks / 12 days, KB ingest / 6 days) — and a THIRD live instance was found this cycle:
`hd_session_watchdog` fires reliably but its consumer is dead, and 5 sibling `hd_*` tasks
are currently silently Disabled.

`mcp__nimbalyst-host__schedule_wakeup` is a different primitive: host-native (survives
Nimbalyst restarts, not Windows Task Scheduler), re-invokes the SESSION directly with a
prompt rather than writing a file for something else to notice, minimum 60s, replaces any
prior pending wakeup for the session (no unbounded pile-up like the watchdog pings). This
is the right mechanism for the idle case specifically because it does not depend on
anything else choosing to read what it produces — the session IS the reader. One instance
armed as proof (Part 3); recommend the owner confirm before it becomes a standing
self-rearming cadence.

## 5. Drafted CLAUDE.md patch (NOT applied — file is DO NOT TOUCH / concurrent writers)

Add a subsection after "Main-thread conduct: never idle, and keep replies short":

```
## Idle-nudge mechanism: schedule_wakeup, not cron, not hook (2026-08-14, measured)

Hooks are event-triggered and cannot fire on pure elapsed idle time (PostToolUse/Agent
fires reliably on every dispatch -- 80/80 measured -- but has nothing to trigger on
during a silent gap). OS cron has failed silently three times now (11 hd_* tasks / 12
days; KB ingest / 6 days; hd_session_watchdog fires reliably but writes to a dead
consumer -- notes/watchdog_ping_to_*, 1585 files, 0 read by anything live).

Use `schedule_wakeup` (host-native, re-invokes THIS session with a prompt, survives
restarts, replaces any prior pending wakeup) for idle nudging. Arm it after any turn
that ends with backgrounded work in flight or nothing left to do; the prompt should (a)
check for unrelayed background-agent reports and relay them, (b) dispatch the next
independent delegated item if genuinely idle, (c) re-arm itself. Do not arm a second one
while one is pending (the tool already enforces this -- one per session).

## Yield-after-dispatch: measured non-compliance after the hook landed

The PostToolUse/Agent reminder hook (2026-08-13) does not appear to have reduced
same-turn continuation after a background dispatch: pre-install immediate-violation rate
63.9% (46/72 turns), post-install 97.4% (38/39) (notes/agent_usage_practices_audit_2026-08-14.md).
A reminder string is not enforcement. Do not treat the hook's presence as the rule being
satisfied -- check the transcript.
```

## 6. Status_log

Written via `tools/orchestrator/state.py::log_event` (see companion tool call).
