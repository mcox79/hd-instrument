# Orchestrator context-reset readiness audit — 2026-05-23

**Auditor**: system-audit sub-agent (Opus 4.7, 1M context)
**Scope**: Verify the orchestrator's structural setup will survive a context compaction and continue to operate efficiently for research + experimentation.

---

## HEADLINE — MOSTLY READY

Survival readiness: **mostly-ready**. The structural wiring is in place: pause flag exists and is read by 3 layers, all 4 wrappers exist and are documented with "when to use" criteria, all 6 skills are present and well-described, the post-compaction brief restates the rules tersely, and the cold-start sequence has been updated to read the brief FIRST (STEP 0). However, three real gaps remain that would either degrade behavior after compaction or quietly block research throughput.

### 3 critical gaps

1. **The post-compaction brief is reachable ONLY via `orchestrator_prompt.md` STEP 0.** It is NOT referenced from `MEMORY.md`'s index, and not listed in `active_protocols.md`. If compaction summarizes the prompt and drops the STEP 0 reference, the brief becomes orphaned. The memory files DO point to it (in body text), but a compactor pulling from MEMORY.md's index wouldn't see it.

2. ~~**`queue_clean.py` does NOT exist**~~ **FALSE NEGATIVE — CORRECTED 2026-05-23**: `queue_clean.py` exists at `tools/queue_clean.py` (not `tools/orchestrator/queue_clean.py` as the audit assumed). The file is fully implemented with subcommands `--list`, `--list-failed`, `--reset`, `--remove`, `--dry-run`; uses `QueueLock`; supports SSH for remote queues (overnight_queue, remote_cpu_queue). `python tools/queue_clean.py --help` returns exit 0. No action required.

3. **Periodic cadences are documented in memory but have NO scheduled enforcement.** The 24h research drill / 24h historical audit / 24-48h scope expansion are guidance in memory files only. There is no cron, no `/loop`, no Monitor-fired event for them. After compaction these will be forgotten until the user prompts. Compare to PROT-005 which DID set up `/loop` for Exp Dev — that pattern was abandoned in migration but the replacement (orchestrator self-dispatching cadences) was never wired.

---

## Per-acceptance-criterion checklist

| # | Criterion | Wired? | Survivable? | Notes |
|---|---|---|---|---|
| 1 | Read post-compaction brief BEFORE any other action | YES — STEP 0 of cold start | **partial** | Reachable only via `orchestrator_prompt.md` STEP 0 + 2 memory body refs. NOT in MEMORY.md index. Brief itself is well-written and dense (~9 KB, 7 sections, restates rules + failure modes). |
| 2 | Detect pause flag; refuse exp dispatch until explicit resume | YES — 3-layer defense | **YES** | Checked in: orchestrator_prompt.md cold-start STEP 1, post_compaction_brief §1, verdict_handler.md Step 2, exp_dev.md PAUSE GATE, all 3 wrapper-related skills (verdict / routing / queue-burst). |
| 3 | Use wrappers (verdict_handler / queue_runner / routing_handler / memory_curator) | YES | **YES** | Event-handling table in prompt is wrapper-first. Direct dispatch labeled as fallback with explicit conditions. Pre-response checklist makes wrapper-check #2. |
| 4 | Parallel dispatch in one message, not serially | DOCUMENTED | **partial** | The structural-mandate memory has explicit "Parallel dispatch is the default — NOT serialized" section with examples. But this is memory-only enforcement; no structural test. The wrappers internalize fan-out so the orchestrator main thread mostly issues 1 wrapper call per event — parallelism is now within the wrappers, which is correct. |
| 5 | Push status updates with plain_language + importance | YES | **YES** | `state.py log_event()` accepts both fields. verdict_handler Step 3 + visibility agent both require them. Skills (pause/resume) demonstrate the pattern. |
| 6 | Use state_check.py for quick state queries | YES | **YES** | `state_check.py` exists, is documented in brief, the prompt, and the `/orchestrator-status` skill. Outputs one line. |
| 7 | GPU-first / remote-CPU-second / local-CPU-only-for-trivial routing | YES | **YES** | exp_dev.md "Queue routing decision" section has 4 rules with explicit precedence + worked examples. Includes the "GPU-first when idle" precedence override (rule 0). |
| 8 | Periodic cadences (~24h research, ~24h audit, ~24-48h scope expansion) | **NO** | **NO** | Documented in memory only. No cron, no `/loop`, no event-driven trigger. Will silently drift after compaction. |

---

## Throughput audit

### Tool-call counts per main-thread event

| Event type | Expected tool calls | Actual (current setup) | Verdict |
|---|---|---|---|
| **Verdict event** | ≤3 | **2-3** | PASS. Flow: (a) optional Bash `test -f paused.flag` if not already known [1 call], (b) dispatch verdict_handler via Agent [1 call], (c) paste return + optional log_event from main thread [0-1 calls]. With `/orchestrator-verdict` skill the pause-check + Read are inlined; ≤3 main-thread calls. |
| **3-experiment queue refill** | ≤2 | **2** | PASS. Flow: (a) dispatch queue_runner with batch=[3 entries] [1 call], (b) paste return [0 calls]. The `/orchestrator-queue-burst` skill bundles the pause-check into the skill body so it doesn't add a main-thread call. |
| **User asks "status"** | ≤2 | **2** | PASS. Flow: (a) `python tools/orchestrator/state_check.py` via Bash [1 call], (b) paste result [0 calls]. Pause-flag prepend + open-Q count are inside the `/orchestrator-status` skill body (skill itself executes a 2-3 step script but those are not main-thread Claude tool calls). |
| **Routing event** | ≤3 | **2** | PASS. Flow: (a) dispatch routing_handler via Agent [1 call], (b) paste return [0 calls]. Pause-check is in skill body. |
| **User dictates 10 feedback memories** | ≤2 | **2** | PASS. Flow: (a) dispatch memory_curator with 10 directives [1 call], (b) paste return [0 calls]. Was 20 calls before the wrapper. |
| **Negative verdict triggering 2x research** | ≤3 | **2-3** | PASS (assuming flow). verdict_handler dispatches strategy which files a research request; orchestrator on next event picks up the routing_handler dispatch. Two events = two wrapper calls. The 2x-research-on-negative reflex is in strategy.md (PROT-004/006) — wired but pull-based, not push-based. |

### Wrapper-gap watchlist (flows that may still exceed 5 main-thread calls)

- **User asks "what does the cap_map say about Cap 1?"** → orchestrator does direct `Agent(strategy)`. That's 1 call. OK.
- **User dictates a single feedback memory in chat** (not a 10-feedback burst) → main thread reflex is "Write feedback file + Edit MEMORY.md" = 2 calls. Brief says memory_curator is for "1+ feedback directives" so the wrapper is justified even for N=1; the cost asymmetry (2 main-thread vs 1 Agent dispatch) is debatable. Documented as acceptable but could be a per-event waste.
- **User asks the orchestrator to set up a new cron / loop / scheduled task** → no wrapper. Likely OK (rare event), but worth knowing it's manual.
- **Negative verdict with no rehab path** → strategy sub-agent handles rehab (PROT-004/006). Orchestrator stays out of it. OK.
- **3 routing files arrive in the same Monitor batch** → orchestrator should dispatch 3 routing_handlers in parallel (one message, 3 Agent calls). The prompt's "Parallel sub-agents" section says exactly this. PASS structurally but no test.

### Orphan / contradiction scan

- `feedback_ascii_only_in_scripts.md` is marked OBSOLETED 2026-05-23 in multiple agent files (exp_dev, visibility, queue_health, research, strategy, queue_runner) — encoding is now structural. But the memory file index entry still describes the original rule. Not a contradiction in behavior (the agents all reflect obsoletion), but the index line is stale.
- `feedback_two_experiments_per_cycle.md` and `feedback_pipeline_pacing.md` overlap heavily; the former is referenced as the "queue depth ≥ 1" anchor; pipeline_pacing adds the CPU-vs-GPU role split. No contradiction; they compose.
- `project_orchestrator_migration.md` says migration is in progress (2026-05-23 quiet window, 24-48h verification). The prompt's "Migration phase" section says the same. Consistent. After the verification window passes (likely 2026-05-24 or 25), this section becomes stale and should be archived.
- `project_runner_race.md` ("ssh -f runners survive sessions and duplicate-pick queue items") — no acknowledgment in any wrapper or in queue_runner.md. If revived CPU runners exhibit this race, queue_runner has no defense. Worth adding to queue_runner.md or queue_health.md as a known mode.
- `project_cpu_resource_underutilized.md` (cpu_runner_0 dead since 2026-05-21) — exp_dev.md correctly comments that the runner may be dead. No contradiction.

---

## Top 3 fixes to ship NOW (before another compaction)

### Fix 1: Add post_compaction_brief to MEMORY.md index AND to active_protocols.md

The brief is currently reachable only via `orchestrator_prompt.md` STEP 0 and via body-text references in two memory files. If compaction summarizes the prompt and drops the STEP 0 sentence, the brief becomes orphaned. Add an explicit index entry to MEMORY.md and a PROT-010 stub to `active_protocols.md` that says "READ `notes/orchestrator_post_compaction_brief.md` FIRST after any context summarization." Cost: 2 small edits. Survivability gain: high — the brief becomes triple-redundant.

### Fix 2: Wire the 3 periodic cadences (research drill, historical audit, scope expansion)

Create three `CronCreate` entries or `/loop` schedules:
- `/loop 12h /research-standing-drill` (or similar)
- `/loop 24h /historical-audit`
- `/loop 36h /scope-expansion`

Each cron fires a slash command that dispatches the appropriate sub-agent with a fresh prompt. Without this, the cadences will silently die after compaction. The memory files describe WHAT to do; the cron/loop is the structural enforcement that they HAPPEN. Pattern: same as the now-retired META cron.

If `/loop` is undesirable (because the orchestrator session may not be live continuously), make it a CronCreate-based `RemoteTrigger` or write a status-log event that the orchestrator checks on every wake-up tick and dispatches if overdue.

### Fix 3: Confirm `queue_clean.py` status — RESOLVED 2026-05-23

~~Task description listed `queue_clean.py` as a current tool but the file does not exist at `d:/AI/hd-instrument/tools/orchestrator/queue_clean.py`.~~

**Corrected**: `queue_clean.py` exists at `d:/AI/hd-instrument/tools/queue_clean.py`. The audit checked the wrong path. Verified working: `python tools/queue_clean.py --help` returns clean output. Subcommands `--list`, `--list-failed`, `--reset`, `--remove`, `--dry-run` all implemented with `QueueLock` + SSH remote support. No action required.

---

## Top 3 longer-term improvements (NOT blocking compaction survival)

### Improvement A: Self-test for parallel-dispatch behavior

The "parallel dispatch is the default" rule is memory-only. A simple test: log each Agent tool invocation with its message_id; later, count message_ids with N>=2 Agent calls. If the orchestrator is silently serializing, the test will catch it. The cost is a 30-line log analyzer; the gain is automated regression detection on the most-violated structural rule.

### Improvement B: Archive the orchestrator migration phase + retire stale memory entries

After the 24-48h verification window passes (likely 2026-05-24), the "Migration phase" section in `orchestrator_prompt.md` becomes stale. Also: `feedback_ascii_only_in_scripts.md` is OBSOLETED across all agents; the memory index should reflect this. Schedule a 30-min pass to clean these up so compaction doesn't restore stale guidance.

### Improvement C: Wrapper coverage for two more event classes

Two patterns are still done in main thread that could be wrappers:
- **Single-feedback memory write** (N=1) — currently main-thread Write + Edit. Could go through memory_curator with batch=[1] for consistency, but adds an Agent call where 2 tool calls would do. Marginal; document the choice.
- **User asks for substrate-research synthesis ad-hoc** — currently the prompt says "direct Agent(strategy)". A "research_handler" wrapper that picks between strategy / research / visibility based on question type would centralize the routing. Probably not worth it for 1-2 events/day, but flag for future consideration.

---

## Pre-compaction sanity checks (run these once before the next compaction)

1. `test -f notes/orchestrator_post_compaction_brief.md && echo OK || echo FAIL`
2. `test -f data/orchestrator_paused.flag && echo PAUSED || echo ACTIVE` (currently PAUSED, expected)
3. `ls tools/orchestrator/agents/*.md | wc -l` (expect 9)
4. `ls C:/Users/marsh/.claude/commands/orchestrator-*.md | wc -l` (expect 6)
5. `python tools/orchestrator/state_check.py` (expect one line; nonzero exit acceptable but should not crash)
6. Grep `orchestrator_paused.flag` in all wrapper agents (expect: exp_dev, verdict_handler at minimum)
7. `grep -l post_compaction_brief tools/orchestrator/*.md notes/active_protocols.md MEMORY.md` (currently: only orchestrator_prompt.md — Fix 1 should make this 3+)

---

## One-sentence honest expectation

After this audit my honest expectation is: the orchestrator will survive a context compaction and continue to honor the pause flag + wrapper-first dispatch, and the throughput targets (≤3 tool calls per verdict, ≤2 per queue refill, ≤2 per status) are structurally achieved; the biggest risk is silent drift of the periodic research / audit / scope-expansion cadences which have no cron-based enforcement and will only fire when the user prompts.
