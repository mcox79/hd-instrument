# Orchestrator efficiency audit + sub-agent expansion — 2026-05-23

**Author**: orchestration-architect sub-agent (deep-analysis pass)
**Brief**: User flagged 4+ times today that orchestrator main thread does too much Bash/Read/Edit volume that should be delegated to sub-agents (per `feedback_structural_agent_usage_mandate.md`). This audit measures the patterns + ships the 4 highest-ROI wrapper sub-agents.

## (a) HEADLINE — implemented + expected gain

| Pattern | Before (per occurrence) | After (per occurrence) | Implemented? |
|---|---|---|---|
| Verdict event | 2 Agent calls (strategy+visibility) + 1-2 Reads (dashboard) + 1 chat-synthesis | **1** Agent call (verdict_handler) | ✅ |
| Queue_add burst (3 entries) | 3 Bash calls + 1 Read | **1** Agent call (queue_runner) | ✅ |
| Routing event | 1-2 Reads (route file + map to recipient) + 1 Agent call | **1** Agent call (routing_handler) | ✅ |
| Memory-write batch (e.g. 5 feedback files) | 5 Writes + 5 Edits to MEMORY.md (= 10 tool calls) | **1** Agent call (memory_curator) | ✅ |
| State check (queues + runners + last verdict) | 3-4 Reads | 1 helper script invocation `python tools/orchestrator/state_check.py` | ✅ |

**Net main-thread tool-use reduction**: estimated ~75% drop on event-handling turns (typical turn dropped from ~6 tool calls to ~1-2 Agent dispatches), at the cost of one-time +5 agent-spec files (~600 LOC total).

---

## (b) Per-pattern measured cost (from today's session)

### P1 — Per-event bash queue_add
- **Fire rate today**: 8 queue_add events surfaced; clustered into 4 bursts of 1-3 entries.
- **Main-thread cost per burst of 3**: 3 separate `Bash(bash tools/orchestrator/queue_add.sh ...)` calls — orchestrator must re-state args each time, output is interleaved, error handling is per-call.
- **Hidden cost**: when SCP+SSH path fails, orchestrator does Bash retry + Read of remote log + chat-synthesize for user. ~5 tool calls in the worst case.
- **Ideal**: one queue_runner agent dispatch with the burst's payload; it batches the entries, runs queue_add.sh per entry inside its own context, returns one consolidated outcome.

### P2 — Per-verdict strategy+visibility dispatch + chat synthesis
- **Fire rate today**: 7 verdicts in status_log; user-perceived flow is closer to 10+ when counting routing-driven verdicts that bypass dashboard.
- **Main-thread cost per verdict**: 2 parallel Agent calls (strategy:opus + visibility:haiku) — same prompt scaffolding pasted from `orchestrator_prompt.md` each time. Plus 1 chat-synthesis turn assembling their returns into a 1-3-sentence user update. Plus often 1 Read of the dashboard to confirm current state.
- **Cost per verdict**: 2 Agent + 1 Read + 1 chat-synth ≈ 4 main-thread tool-equivalents.
- **Ideal**: a single verdict_handler (Opus) call that internally fans out strategy+visibility (parallel) and returns ONE consolidated update line that the orchestrator can paste to chat verbatim. Internal complexity hides inside the agent's context, not main thread's.

### P3 — Routing event scaffolding
- **Fire rate today**: at least 5 routing-file events (strategy_request_to_research_*, exp_dev_to_strategy_*, etc.).
- **Main-thread cost per routing**: 1 Read of the routing file to confirm recipient + 1 Agent dispatch with the correct sub-agent prompt + the routing file path. Often a second Read to pick the right context fragment.
- **Cost per routing**: 1-2 Reads + 1 Agent call.
- **Ideal**: routing_handler (Sonnet) takes the event payload, reads the routing file itself, dispatches the correct recipient. Orchestrator just calls routing_handler once.

### P4 — Memory-curator pattern (today's feedback writes)
- **Fire rate today**: ~10 feedback files written (per user count in the brief).
- **Main-thread cost per feedback**: 1 Write of the new feedback_*.md + 1 Edit of MEMORY.md index ≈ 2 tool calls each. Cumulative: ~20 tool calls.
- **Ideal**: memory_curator (Sonnet) takes a list of user-dictated directives, writes all the files atomically, updates MEMORY.md index once at the end. One Agent call replaces 20 tool calls.

### P5 — State check (queue depth + runner heartbeats + last verdict)
- **Fire rate today**: at least 6 times (user "queue empty?" / "what's running?" interrupts).
- **Main-thread cost**: 1 Read of dashboard snapshot + 1 grep for queue depth + 1 Read of recent_verdicts + 1 chat-synth ≈ 3-4 tool calls.
- **Ideal**: `python tools/orchestrator/state_check.py` — single subprocess that prints a one-line summary. Orchestrator runs 1 Bash call, pastes the line to chat. Saves 3 reads.

---

## (c) ROI ranking

| Rank | Pattern | LOC to build | Tool calls saved per fire | ROI (saved-per-LOC) |
|---|---|---|---|---|
| 1 | P4 memory_curator | ~120 | ~18 (writes 10 files instead of 20 calls) | very high |
| 2 | P2 verdict_handler  | ~100 | ~3 per verdict × 7+ verdicts/day | very high |
| 3 | P1 queue_runner     | ~80 | ~2-4 per burst (3-entry case) | high |
| 4 | P5 state_check.py   | ~80 | ~3 per fire × 6+ fires/day | high |
| 5 | P3 routing_handler  | ~100 | ~1-2 per routing × 5+/day | medium |

All 5 implemented in this pass.

---

## (d) Files written this pass

### New sub-agent definitions
- `tools/orchestrator/agents/queue_runner.md` — Sonnet, batches queue_add events
- `tools/orchestrator/agents/verdict_handler.md` — Opus, end-to-end verdict handling (fans out strategy+visibility)
- `tools/orchestrator/agents/routing_handler.md` — Sonnet, dispatches recipient role
- `tools/orchestrator/agents/memory_curator.md` — Sonnet, batches feedback memory writes + MEMORY.md index updates

### New helper
- `tools/orchestrator/state_check.py` — one-line state summary (queue × 3 + runners + last verdict + cap_map version)

### Updates
- `tools/orchestrator/orchestrator_prompt.md` — event-handling table rewritten to route through wrappers; old direct-dispatch rows preserved as fallback

---

## (e) What was NOT implemented and why

- **dispatch.py routing-burst batching window** (500 ms): out of scope; queue_runner agent already absorbs the burst; further work is dispatch-side optimization that's a separate refactor.
- **dispatch.py mtime-gate on dashboard re-read**: same — orthogonal perf fix, not user-flagged-as-painful.
- **Replacing existing 5 agent files**: deliberately additive. New wrappers compose existing agents; original specs remain callable for back-compat / direct invocation when needed.
- **Push helper agent**: orchestrator already has push permission in settings.local.json; a 1-Bash `git push origin main` is a routing decision, not analysis. Doesn't warrant an agent.
- **User_summarizer agent**: low marginal value — the wrapper agents (verdict_handler, queue_runner, routing_handler) already return one-line summaries the orchestrator pastes verbatim. A separate summarizer would just add another hop.

---

## (f) Usage pattern after this pass

For a typical verdict event:

```
BEFORE:
  Agent(strategy:opus, prompt:<verdict + scaffolding>)
  Agent(visibility:haiku, prompt:<verdict + scaffolding>)
  Read(data/local_dashboard_snapshot.json)
  <chat: "v158 landed — Cap 1 SLA widens; visibility logged at HH:MM">

AFTER:
  Agent(verdict_handler:opus, prompt:<verdict payload>)
  <chat: paste verdict_handler's one-line return>
```

For a queue_add burst of 3:

```
BEFORE:
  Bash(bash queue_add.sh overnight_queue exp_A ...)
  Bash(bash queue_add.sh overnight_queue exp_B ...)
  Bash(bash queue_add.sh local_cpu_queue exp_C ...)
  <chat: "3 queued (2 overnight + 1 local_cpu)">

AFTER:
  Agent(queue_runner:sonnet, prompt:<batch of 3 entries>)
  <chat: paste queue_runner's consolidated return>
```

For a memory-write batch:

```
BEFORE:
  Write(feedback_X.md) + Edit(MEMORY.md, add X line)
  Write(feedback_Y.md) + Edit(MEMORY.md, add Y line)
  ... × N
  <chat: "wrote N feedback files">

AFTER:
  Agent(memory_curator:sonnet, prompt:<list of directives>)
  <chat: paste memory_curator's return>
```

For a state-check interrupt:

```
BEFORE:
  Read(data/local_dashboard_snapshot.json)
  Grep(queue_pending_count, ...)
  Read(notes/queue_health_log.md)
  <chat: "queue at 1, gpu running wave14_X, last verdict 4 min ago">

AFTER:
  Bash(python tools/orchestrator/state_check.py)
  <chat: paste state_check's one-line summary>
```

---

## (g) Verification

Each wrapper agent is additive — existing direct-dispatch paths still work. Rollback: drop the wrapper rows from `orchestrator_prompt.md`, revert to original event table. No live experiments / cap_map state affected.

`state_check.py` is read-only; it cannot corrupt any orchestrator state.

`queue_runner` shells out to the existing `queue_add.sh`; queue_add.sh's behavior unchanged.

`memory_curator` writes feedback memory files under `C:\Users\marsh\.claude\projects\d--AI\memory\` and edits the index. Atomic .tmp+rename per [[feedback-cap-map-update-protocol]].
