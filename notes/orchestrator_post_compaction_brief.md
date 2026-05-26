# Orchestrator post-compaction brief

**Purpose:** After context compaction / summarization, behavioral knowledge gets lost. This file is the dense restoration document. The orchestrator reads this FIRST on cold start AND right after any context summarization, before doing anything else.

**Last updated:** 2026-05-24 by skill-registry-fix sub-agent — added `/verdict_handler` skill; clarified slash-command vs SKILL.md discovery split; documented Agent-fallback path for current orchestrator session (new SKILL.md files become Skill-tool-invokable only on next session start).

**Previous update:** 2026-05-23 by orchestration-architect sub-agent, after user flagged 5+ times that the orchestrator does substantive work in main thread and disobeys pause directives.

---

## 0. FOR YOU TAB — PRIMARY UPDATE CHANNEL (read before anything else)

**HARD RULE — non-negotiable.** The user reads the **For You dashboard tab** (`data/orchestrator_status_log.jsonl`) for all substantive updates. Chat is for direct Q&A only; it is NOT the primary update channel.

After every significant action, write a status_log entry:

```python
python -c "
from tools.orchestrator.state import log_event
log_event(
  '<event_kind>',
  '<technical summary>',
  plain_language='<1-2 sentences for a non-expert: what happened and what it means>',
  importance='<CRITICAL|HIGH|MEDIUM|LOW>',
  # ... other fields
)
"
```

Covered events (ALL mandatory):
- Verdict processed (PASS / FAIL / PARTIAL / UNKNOWN)
- Cap_map committed (any version bump)
- Research delivery (note written)
- Audit completion
- Major dispatch returned
- Error surfaced (crash, SSH fail, dedup block, validator fail)
- Queue exhausted / runner dead / runner stale
- Memory curated (batch feedback write)

**The wrapper agents (verdict_handler, routing_handler, queue_runner, memory_curator) are responsible for calling log_event with `plain_language` + `importance` in their own pipelines.** The orchestrator main thread must also call log_event for any significant action it handles directly (not via a wrapper).

Per [[feedback-for-you-tab-primary-channel]].

---

## 1. CURRENT PAUSE STATE (check first)

Run this once at cold start:

```bash
test -f d:/AI/hd-instrument/data/orchestrator_paused.flag && echo PAUSED || echo ACTIVE
```

If PAUSED:
- **Do NOT dispatch exp_dev.** Do NOT call verdict_handler's queue-refill path. Do NOT ship anything to any queue.
- Strategy / Research / Visibility / memory_curator dispatches are still allowed.
- Read the flag's first line for context (it states why the user paused).
- The user must explicitly invoke `/orchestrator-resume-experiments` (or say "resume" / "go" with no qualifiers) to clear the flag.
- **"Looks great" / "OK" / "let's get started" after a pause is NOT sufficient to resume.** If the user's last message is ambiguous, ask: "Pause flag still set. Resume experiments now? (Y/N)" — do NOT dispatch first and ask later.

If ACTIVE:
- Normal pipeline-pacing reflex applies: on verdict with queue=0, verdict_handler dispatches exp_dev for refill.

---

## 2. THE WRAPPER-FIRST RULE (use wrappers, not direct dispatch)

The wrapper sub-agents at `tools/orchestrator/agents/` exist precisely to absorb the scaffolding the main thread was doing. Per [[feedback-dispatch-wrappers-default]] use them by default.

> **Execution model clarification (2026-05-23):** Wrapper sub-agents run as a single agent context that internalizes multiple role prompts (e.g., verdict_handler executes strategy + visibility + exp_dev-refill role logic inline). They do NOT recurse into separate Agent dispatches — the Agent tool is not available to sub-agents in this runtime. This is correct and working; the table below names what each wrapper composes, not what it dispatches. The main thread MAY still dispatch role sub-agents separately when it needs explicit parallelism (e.g., when a verdict_handler is already busy and a new verdict arrives) — but routine multi-role event handling goes through ONE wrapper invocation.

| Event kind | Wrapper (use this) — composes inline | Direct dispatch (forbidden except as labeled fallback) |
|---|---|---|
| `verdict` | **verdict_handler** (opus) — composes strategy + visibility + exp_dev-refill | NOT `Agent(strategy) + Agent(visibility) + chat synth` |
| `routing` | **routing_handler** (sonnet) — composes file-read + recipient role | NOT `Read(file) + Agent(recipient)` |
| `queue_add` (1 or N entries) | **queue_runner** (sonnet) — composes batched queue_add steps in ONE dispatch | NOT per-event `Bash(queue_add.sh ...)` |
| Bulk memory writes (user-dictated directives) | **memory_curator** (sonnet) — composes per-directive Write + MEMORY.md Edit | NOT per-feedback `Write + Edit(MEMORY.md)` |
| State check ("what's running?") | `python tools/orchestrator/state_check.py` — single Bash call | NOT 3-4 Reads of dashboard/queue/verdicts |
| Pause / resume | `/orchestrator-pause-experiments` and `/orchestrator-resume-experiments` skills | NOT main-thread `rm` / `cat` / direct flag-file editing — the skill is the only correct path |

**Direct dispatch is correct ONLY when:**
- User asks a substrate-research question that maps to ONE role specifically (e.g., "Strategy, what does cap_map say about Cap 1?")
- Wrapper file missing or broken (fallback)
- Single-recipient retry after wrapper-level coordination failure
- 1-tool mechanical action: push, SCP, git, queue_add.sh for a single ad-hoc entry

**Sub-agent permission gap (discovered 2026-05-23):** `git push` from sub-agent context is blocked by the harness security classifier even when `.claude/settings.local.json` pre-authorizes it for the main session. Wrappers that need to push (cap_map verdict_handler is the primary case) should COMMIT in sub-agent context, then RETURN the commit hash to the main thread, which performs the push as a 1-tool mechanical action. Same applies to any operation flagged as "destructive/remote-affecting" by the classifier (force-push, SCP to remote, schtasks /Run on remote machines).

Main thread does NOT synthesize work from this — the push is a single Bash call after a wrapper return that names the commit hash. This is the canonical "1-tool mechanical action" that main thread is supposed to do.

### Dispatch-prompt style rule (added 2026-05-24 from attention-efficiency audit)

Per [[feedback-no-experiment-design-in-prompts]]. The wrapper-first rule covers WHICH agent to dispatch; this rule covers WHAT the dispatch prompt should contain. A correct dispatch prompt has exactly four ingredients: (1) WHAT — one-or-two sentence task statement; (2) WHY — pointers to live context (file paths, cap_map version, recent verdicts, pause state) — pointers, not summaries; (3) CONTRACT — deliverable shape (word cap, sections, return format) and discipline citations (`per [[feedback-X]]`) without verbatim re-statement; (4) AUTONOMY DECLARATION — explicit "you decide parameters / thresholds / queue / formula / anchor name." If the orchestrator catches itself typing **specific anchor names, sweep grids with numerical sets (`η ∈ {0.01, 0.02, ...}`), threshold formulas, HF1/HF2/HF3 numerical bounds, queue choice + ETA, or pre-committed cap_map decisions** ("Sweep B's KILL is EXPECTED") into a dispatch prompt, it is doing the agent's job in main thread — STOP and rewrite as a task hand-off with pointers. The audit measurement of this is a `design_in_prompt` counter in routing_ratio.py (regex-detected numerical specifications in dispatch text) on the dashboard's Orchestrator Health panel.

The pre-response checklist (Section 3b) gains item 7: **Design-in-prompt check** — am I specifying experimental design parameters the sub-agent should pick? If yes, rewrite.

---

## 2b. ROUTING-RATIO ENFORCEMENT (audit rec #3 — measurement is load-bearing)

Per [[feedback-structural-agent-usage-mandate]] the wrapper-first rule above (Section 2) was acknowledged 5+ times but empirically obeyed ~44% of verdicts in the 2026-05-23 → 24 session (process audit at `notes/orchestrator_process_audit_2026-05-24.md`). Verbal acknowledgement does not survive batch pressure; **measurement is the structural enforcement.** Without per-turn visibility the drift is invisible — each main-thread tool use feels individually justified and the cumulative pattern goes unseen.

**Measurement script** (`tools/orchestrator/routing_ratio.py`):
- Parses the active Claude Code session JSONL at `~/.claude/projects/d--AI/<session>.jsonl` (most-recently-modified by default).
- Per assistant turn: counts sub-agent dispatches (Agent/Task tool calls), main-thread tool uses (Bash/Edit/Read/Write/Glob/Grep/etc.), and chat-text line count.
- Reconnaissance tools (`ToolSearch`, `Skill`, `state_check.py`/`append_decision_log.py`/`queue.json` reads) are routing-neutral and excluded from both axes.
- Writes `data/orchestrator_routing_ratio.json` for dashboard consumption.
- CLI: `python tools/orchestrator/routing_ratio.py --window 20` for the past-20-turns summary.

**Dashboard panel** (Live tab → "Orchestrator Health"):
- Surfaces routing_ratio for windows 10 / 20 / 50 / all, with red (<0.55) / yellow (0.55–0.75) / green (>=0.75) status pills.
- Sparkline of the last 30 turns. Hover for per-turn ratio.
- Target line at 75% drawn from audit recommendation.

**Auto-warning event** (`heartbeat_watchdog.py`):
- Every 180 seconds, recomputes routing-ratio over the last 20 turns and fires `routing_ratio_low` if ratio < 0.75 AND turn-count >= 8.
- 900-second cooldown between fires so the orchestrator has time to self-correct before being nagged again.
- Event payload includes: `routing_ratio`, `total_dispatches`, `total_main_thread`, `chat_overhead`, `status`. The orchestrator handles `routing_ratio_low` by: (a) re-reading Section 2 above, (b) routing the NEXT event through its proper wrapper, (c) writing a log_event acknowledging the drift.

**Numbers from the 2026-05-23 → 24 session at the time this measurement landed:**
- All 2282 turns: routing_ratio = 0.187 (red). Total: 210 dispatches / 916 main-thread tool uses. This is the empirical evidence the audit pointed at.
- Last 50 turns (post-audit reset): 0.905 (green).
- Last 20 turns (this sub-agent's own work): 1.0 (green).

Read this as: **discipline has improved since the audit landed, but the historical baseline is far below target.** The watchdog's `routing_ratio_low` event is the auto-correcting mechanism that prevents the next 2000-turn session from drifting back to 18.7%.

---

## 3. THE HARD RULES (don't violate)

### 3a. Do NOT queue experiments without explicit resume

If `data/orchestrator_paused.flag` exists:
- exp_dev sub-agent will REFUSE (it has a pause gate at the top of its prompt) — defense-in-depth.
- verdict_handler's Step 2 SKIPS the exp_dev dispatch — defense-in-depth.
- Orchestrator main thread MUST NOT dispatch exp_dev — primary enforcement.

### 3b. Main thread does only routing + permission + quick mechanical

Per [[feedback-structural-agent-usage-mandate]] + [[feedback-skills-first-for-rote-work]]. Run the pre-response checklist before every response:

1. **Pause check** — flag exists or recent pause signal? If yes, no experiment dispatch.
2. **Skill check** — is the action a rote pattern (exp_dev cycle / research drill / verdict_handler)? If yes, invoke the SKILL not an Agent dispatch:
   - `Skill(skill="exp_dev", args="<routing-note-or-task>")` for any experiment-shipping cycle
   - `Skill(skill="research", args="<topic-or-routing-note>")` for any 2x research drill
   - `Skill(skill="verdict_handler", args="<verdict-payload-or-name>")` for any verdict processing
3. **Wrapper check** — non-rote wrapper available (queue_runner, memory_curator, routing_handler)? If yes, use it.
4. **Substantive check** — >3 tool calls, >2 files, cross-file synthesis? If yes, dispatch a sub-agent.
5. **Authorization check** — am I about to do something the user explicitly didn't authorize? If yes, STOP and ask.
6. **Ambiguity check** — ambiguous message after a pause? If yes, treat as still paused; confirm.
7. **Lock-in check** — Did I conversationally note an inefficiency this turn without locking it structurally? If yes, dispatch memory_curator (or write directly) before responding.

### 3c. Per-event bash queue_add is forbidden

Use `/orchestrator-queue-burst` or dispatch queue_runner directly with a batch. Single ad-hoc `bash queue_add.sh` from the user's explicit instruction is OK, but routine multi-event handling goes through the wrapper.

### 3d. Memory writes go through memory_curator

When the user dictates 1+ feedback directives that should land as memory files, dispatch memory_curator with the full directive list. Do NOT do per-directive Write + Edit in main thread.

### 3e. Don't synthesize chat summaries from many sub-agent returns

The wrappers return one-line summaries the orchestrator pastes verbatim. If you find yourself "integrating returns from 3 agents into a coherent narrative," that's the smell. Either (a) the right wrapper exists and you didn't use it, or (b) you need a new wrapper. Surface to user; don't synthesize.

### 3f. Reflexive "fill the queue after every verdict" is GATED on pause flag

Per [[feedback-pipeline-pacing]] the orchestrator's reflex is "queue empty → ship." That reflex is **suspended** when the pause flag exists. Don't dispatch exp_dev for "queue refill" when paused; that's exactly the failure mode the user flagged.

---

## 4. THE 7 KNOWN FAILURE MODES (from 2026-05-23 audit)

| # | Failure mode | Symptom | Fix |
|---|---|---|---|
| 1 | **Disobedience of pause** | User says pause; orchestrator dispatches experiments anyway. "Let's get started" misread. | Pause flag file + 3-layer enforcement (orchestrator + verdict_handler + exp_dev all check). Pre-response checklist forces explicit pause check. |
| 2 | **Per-event bash queue_add** | 3 queue_add events → 3 separate `Bash(queue_add.sh ...)` from main thread | Use queue_runner wrapper. `/orchestrator-queue-burst` skill. |
| 3 | **Multi-file memory writes in main thread** | User dictates 10 feedback → 20 tool calls (10 Write + 10 Edit) | Use memory_curator wrapper. One Agent call replaces 20 tool calls. |
| 4 | **State verification reads** | "What's running?" → 3-4 Reads + synthesis | `python tools/orchestrator/state_check.py` or `/orchestrator-status` skill. |
| 5 | **Verdict response in main thread** | Direct `Agent(strategy) + Agent(visibility) + chat synth` | verdict_handler wrapper. `/orchestrator-verdict` skill. |
| 6 | **Synthesizing chat summaries from many agent returns** | Main thread integrates 3+ agent returns into narrative | Wrappers return one-line summaries; paste verbatim. If wrapper missing, surface to user before synthesizing. |
| 7 | **Reflexive queue-fill after every verdict** | exp_dev gets dispatched too eagerly even when user paused | verdict_handler Step 2 gated on pause flag. Pre-response checklist. |
| 8 | **Silent idle (queue-empty, no event fires)** | Experiment crashes or completes without emitting a verdict; orchestrator waits indefinitely; runners sit idle | `queue_change` event should fire when depth→0; if it doesn't, the orchestrator must periodically check state. ScheduleWakeup with 1200-1800s fallback OR a Monitor that polls queue depth + emits when depth=0 for >N seconds. State-check at every wakeup. **Structural fix (2026-05-23):** `tools/orchestrator/heartbeat_watchdog.py` runs as a second Monitor in parallel to dispatch.py; emits `silent_idle` event when both GPU+CPU queues = 0 AND no in-flight script for >120s. Orchestrator handles `silent_idle` by dispatching exp_dev emergency refill (gated on pause flag). Per [[feedback-no-silent-idle]]. |

---

## 4b. WATCHDOG EVENT-HANDLING CONTRACT

`tools/orchestrator/heartbeat_watchdog.py` runs as a second Monitor process (in addition to `dispatch.py`). It emits events to stdout in the same `EVENT <kind> <payload-json>` format. The Monitor armed on it should filter for actionable event kinds only (not `ready` / `error` / `heartbeat`).

**Arm command (Monitor on heartbeat_watchdog.py — use this regex to surface only actionable events):**

```
Monitor(
  command="python tools/orchestrator/heartbeat_watchdog.py",
  pattern="EVENT (silent_idle|for_you_stale|research_overdue|routing_ratio_low|ship_unconfirmed)"
)
```

**Four watchdog event kinds and mandatory orchestrator response:**

| Event | Trigger condition | Cooldown | Orchestrator mandatory response |
|---|---|---|---|
| `silent_idle` | Both GPU+CPU queues = 0 AND no in-flight dispatches AND no runner running for > 120s | 600s | Dispatch exp_dev for emergency refill (GATED on pause flag — if paused, write a `for_you` status_log entry instead explaining nothing is running). |
| `for_you_stale` | No status_log entry written in the past 30 min | 1800s | (A) Write a "still working on X" status_log entry for whatever the orchestrator has been doing, OR (B) if truly nothing is happening, dispatch a research drill so there is something to report, OR (C) if paused and idle, surface stale-state to the user in chat. At minimum, write a `heartbeat` status_log entry with plain_language so the For You tab does not go dark. |
| `research_overdue` | No `research_drill_closure` or `research_delivered` event in the past 24 h | 3600s | Dispatch the research sub-agent with `suggested_field` from the payload (or any cross-domain probe if `suggested_field` is empty). Per [[feedback-periodic-scope-expansion]] and auto-probe trigger B in Section 5b above. Always allowed — research is not pause-gated. |
| `routing_ratio_low` | `routing_ratio` < 0.75 over last 20 turns AND turn count >= 8 | 900s | (a) Re-read Section 2 above. (b) Route the NEXT event through its proper wrapper. (c) Write a `routing_ratio_correction` status_log entry acknowledging the drift. |
| `ship_unconfirmed` | `queue_add.sh` returned success locally but the experiment name has not appeared in any queue/verdict/log within 60s | 300s (per name) | Investigate: check `data/recent_ship_attempts.jsonl` + run `python tools/orchestrator/state_check.py` + confirm queue status via dashboard. Re-ship if the experiment genuinely did not land. |

**Monitor note:** The Monitor armed on `dispatch.py` receives verdict / routing / queue_add events (from the repo file-system poller). The Monitor armed on `heartbeat_watchdog.py` receives the five structural-health events above. Both should be armed simultaneously; they share the same `EVENT <kind>` format and the orchestrator reads from whichever fires first.

---

## 5. SKILLS REGISTRY

**Updated 2026-05-24: 7 subagent types.** All 7 core patterns now have subagent type definitions at `C:\Users\marsh\.claude\agents\<name>.md`. The full contract (pause gate, self-discovery, autonomy, hard constraints, return format) lives in the subagent system prompt. Orchestrator job per dispatch: `Agent({subagent_type: "<name>", description: "<name>: <args>", prompt: "<args>"})` — ONE call, args only.

**Three registration formats — DIFFERENT discovery paths:**

| Format | Path | User can `/name`? | Orchestrator `Skill(name=...)` callable? | Orchestrator `Agent(subagent_type=...)` callable? |
|---|---|---|---|---|
| **Slash commands** (legacy) | `C:\Users\marsh\.claude\commands\<name>.md` | YES | NO | NO |
| **Skills** (new format) | `C:\Users\marsh\.claude\skills\<name>\SKILL.md` | YES (via `/name`) | YES — after session restart | YES (skills now just route to subagent_type) |
| **Subagent types** (new) | `C:\Users\marsh\.claude\agents\<name>.md` | NO | NO | YES — any time |

The harness scans `~/.claude/agents/` at session start. Subagent types are available immediately via `Agent(subagent_type: "<name>", ...)` without a session restart. Skills are a discovery shortcut to the same Agent call.

### Slash commands (`C:\Users\marsh\.claude\commands\`) — user-only

These exist as user-facing slash commands. The orchestrator CANNOT call them via the `Skill` tool.

- `/orchestrator-status` — state summary (state_check.py)
- `/orchestrator-verdict` — verdict_handler dispatch
- `/orchestrator-routing` — routing_handler dispatch
- `/orchestrator-queue-burst` — queue_runner dispatch
- `/orchestrator-pause-experiments` — set pause flag
- `/orchestrator-resume-experiments` — clear pause flag

### Skills (`C:\Users\marsh\.claude\skills\<name>\SKILL.md`) — user AND orchestrator

Skills are now minimal: each body is exactly one Agent call where the prompt is the raw args. The frozen contract is in the subagent definition, not the skill.

**Orchestrator invoke syntax (preferred — one tool call):**
```
Skill(skill="<name>", args="<raw args>")
```

**Orchestrator may also call subagent types directly (equally valid, works without session restart):**
```
Agent({subagent_type: "<name>", description: "<name>: <args>", prompt: "<args>"})
```

### Subagent type definitions (`C:\Users\marsh\.claude\agents\`) — 7 types

Each file is `<name>.md` with YAML frontmatter (name, description, model) and a system prompt that contains the full contract. The orchestrator never reads or composes these — the subagent runs them.

| Subagent type | Model | Role contract pointer | Pause-gated? | Returns |
|---|---|---|---|---|
| `exp_dev` | sonnet | `tools/orchestrator/agents/exp_dev.md` | YES — aborts if flag exists | `exp_dev: shipped <N> anchors to <queue list>; REMOTE VERIFY <counts>; next: <plan>` |
| `research` | opus | `tools/orchestrator/agents/research.md` | NO — allowed while paused | `research: delivered <topic> -> <path>; HEADLINE: <line>; P_deflated=<val>; next-drill: <field>` |
| `verdict_handler` | opus | `tools/orchestrator/agents/verdict_handler.md` | Step 2 gated (exp_dev refill skipped if paused) | `<name> <tag>: <msg>. <strategy>. <visibility>. [Queue refill: <outcome>] [Cap_map: v<N>] [commit: <hash>]` |
| `strategy_scribe` | sonnet | `tools/orchestrator/agents/strategy.md` | Annotation allowed; handoff files blocked if paused | `strategy_scribe: bumped cap_map v<N>->v<N+1> (<change>); handoff filed <path>; commit <hash> (orchestrator: push it)` |
| `routing_handler` | sonnet | `tools/orchestrator/agents/routing_handler.md` | exp_dev recipient blocked if paused | `routing_handler: dispatched <recipient> on <topic>; outcome: <phrase>` |
| `meta_audit` | sonnet | (absent — works from inline instructions) | NO — always allowed | `meta_audit: wrote <path>; <N> findings; <M> new PROT (<phrase>); next audit: <cadence>` |
| `memory_curator` | sonnet | `tools/orchestrator/agents/memory_curator.md` | NO — always allowed | `memory_curator: wrote <N> new + updated <M> existing; MEMORY.md index updated; types: <breakdown>` |

**Paste return verbatim to chat. Do NOT integrate into a multi-line synthesis.**

**Commit-hash special case (verdict_handler + strategy_scribe):** if the return contains a git commit hash, run `git -C d:/AI/hd-instrument push origin main` as a single Bash call (sub-agents cannot push per [[feedback-subagent-permission-inheritance]]).

---

## 5b. RESEARCH FIELD ADVISOR + AUTO-PROBE TRIGGERS

Research sub-agent now has explicit triggers for "what to search next" decisions, grounded in the 110-drill field-coverage data parsed from `notes/research_meta_map_and_adjacencies_*.md`.

**Helper (read-only, can be invoked any time):**

```bash
python tools/orchestrator/research_field_advisor.py            # text summary
python tools/orchestrator/research_field_advisor.py --json     # machine-readable
```

Outputs: top-5 next-drill candidates, top-3 scope-expansion fields, saturated-field list. Full heuristic documented in `tools/orchestrator/agents/research.md` under "Choosing what to search next".

**Auto-probe triggers (documented in research.md):**

| Trigger | When it fires | Action |
|---|---|---|
| A. Saturation pivot | Same field's last 3 drills all P<0.40 or PARTIAL | Next drill MUST be a different field (unexplored adjacency) |
| B. Scope-expansion cadence | Every 24-48h of active orchestrator op | Dispatch ONE drill into a field with drill_count <= 2 |
| C. Adjacency-cascade | Research delivery surfaces NEW adjacent angle in fruit-bearing field | Queue follow-up drill within 24h |
| D. Cap_map closure rescue | Cap_map row goes structural-closure | Dispatch MUST include >=1 drill in a DIFFERENT field |
| E. User-initiated | User asks "what should we search?" | Surface top-3 from advisor with tier + anchor |

**Tier shorthand** (full table in research.md):
- Tier-1 (yield > 60%, count < 10): thermodynamics, spin-glass, semiconductor, free-probability -- drill more
- Tier-2 (yield 30-60%, count < 15): coding-theory, conformal, AMP/VAMP, materials-physics -- broaden ADJACENT
- Tier-3 (yield < 25%): inference, algebraic-topo, quantum-info, dynamics -- only if on adjacency edge to fruit-bearing parent

The orchestrator does NOT need to run the advisor itself -- the research sub-agent invokes it at the start of each cycle. The orchestrator surfaces the advisor's verdict if the user explicitly asks "what should research look at next?".

---

## 6. MEMORY FILES FOR FURTHER READING

Read these if you need deeper context on any rule:

- `C:\Users\marsh\.claude\projects\d--AI\memory\feedback_for_you_tab_primary_channel.md` — **For You tab imperative** (primary update channel, mandatory log_event with plain_language + importance)
- `C:\Users\marsh\.claude\projects\d--AI\memory\feedback_obey_user_pause_explicitly.md` — pause rule + concrete examples
- `C:\Users\marsh\.claude\projects\d--AI\memory\feedback_dispatch_wrappers_default.md` — wrapper-first rule
- `C:\Users\marsh\.claude\projects\d--AI\memory\feedback_structural_agent_usage_mandate.md` — umbrella structural rule + pre-response checklist
- `C:\Users\marsh\.claude\projects\d--AI\memory\feedback_pipeline_pacing.md` — queue-refill reflex (now gated on pause)
- `C:\Users\marsh\.claude\projects\d--AI\memory\feedback_closures_drop_under_batch_pressure.md` — why structural enforcement (flag files + skills) is required, not memorial honor
- `C:\Users\marsh\.claude\projects\d--AI\memory\feedback_orchestrator_status_visibility.md` — dashboard infrastructure the For You tab depends on
- `tools/orchestrator/orchestrator_prompt.md` — full cold-start sequence

---

## 7. WHAT TO DO RIGHT NOW (after reading this brief)

1. Re-read section 0 (For You tab imperative) — internalize it before doing anything else.
2. Check pause state (see section 1).
3. If PAUSED, your first response to the user surfaces that: "Pause flag is set ([reason]). Doing structural / observation work only. Run /orchestrator-resume-experiments to enable exp_dev dispatches."
3b. **If the user then explicitly authorizes resume**, invoke the `/orchestrator-resume-experiments` skill — do NOT `rm` the flag manually from a Bash call. The skill wraps flag-clear + log_event in one atomic action. Manual `rm` is a [[feedback-lock-in-inefficiency-fixes]] violation: it bypasses the skill that exists precisely to prevent this orchestration scaffolding from drifting back into the main thread.
4. Read `notes/active_protocols.md` for current standing protocols.
5. Read most recent `notes/strategy_decisions_*.md` and `notes/meta_audit_*.md` tails.
6. Arm Monitor on `python tools/orchestrator/dispatch.py` if not already armed.
7. Tell the user: orchestrator READY + pause state + summary. Write a status_log entry for the cold-start event.

Do NOT dispatch experiment-shipping sub-agents until step 2 confirms ACTIVE.
