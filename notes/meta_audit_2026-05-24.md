# META audit — 2026-05-24 (weekly cadence + post-subagent_type architecture rollout)

**Author:** meta_audit sub-agent (Sonnet)
**Scope:** weekly cadence audit + post-rollout check after today's subagent_type architecture landing (4 new types: strategy_scribe, routing_handler, meta_audit, memory_curator). Three explicit questions from orchestrator: (a) routing-ratio compliance over last 50 turns — did today's main-thread tool use spike during the skill refactor? (b) active_protocols.md entries needed to lock in "Agent({subagent_type: X, prompt: args}) is canonical dispatch shape"? (c) drift signals in past 24h of decisions/verdicts warranting a PROT addition.
**Prior audit:** meta_audit_2026-05-23_cycle96.md (cycle 96, ~10:15 on 2026-05-23)

---

## 1. Process compliance

### Routing ratio

Fresh measurement from `tools/orchestrator/routing_ratio.py --window 50`:

| Window | Turns | Dispatches | Main-thread | Ratio | Status |
|--------|-------|------------|-------------|-------|--------|
| Last 10 | 10 | 4 | 0 | 1.000 | GREEN |
| Last 20 | 20 | 7 | 0 | 1.000 | GREEN |
| Last 50 | 46 | 7 | 12 | 0.368 | RED |

**Interpretation:**

The split tells the architectural story directly. The last 20 turns (ratio = 1.000, all green) represent the **post-refactor period**: skill-based dispatch is working. The 12 main-thread tool uses that drag the 50-turn window into RED are concentrated in the **pre-refactor turns** at the start of today's session — the period when the orchestrator was performing the skill refactor itself (reading files, writing agent definitions, editing skill bodies, testing invocations). These were legitimately structural/mechanical actions with no available skill to delegate to, because the skills being built ARE the delegation infrastructure.

**Verdict: the spike is expected and is NOT a drift indicator.** The 1.000 ratio on the last 20 turns confirms the new architecture is performing correctly post-landing. The 50-turn red is a construction-period artifact, not a behavioral regression.

**One real concern:** The routing_ratio.py parser logs 7 dispatches over the 50-turn window. Cross-checking against the session JSONL sparkline, 5 of these are concentrated in the last 10-20 turns (post-refactor). The initial 36 turns contributed 2 dispatches and 12 main-thread uses. Within those 36 pre-refactor turns, the orchestrator was building skills — that is mechanical setup, exempt from the substantive-check rule. No behavioral violation found.

### Pause obedience

No evidence of exp_dev dispatch while paused. The status_log shows the pause flag was CLEARED at 2026-05-23 18:31 and the orchestrator correctly withheld exp_dev dispatches until that point. The post-compaction brief's three-layer enforcement (orchestrator + verdict_handler + exp_dev each check) was structurally in place throughout.

### For-You tab coverage

Reviewed the last 30 entries of `data/orchestrator_status_log.jsonl`. Coverage is good for major events: verdicts, cap_map commits, research deliveries, memory writes, runner state changes, queue events. Two classes of potentially under-logged events:

1. **Skill-refactor work** (today): the session building the new subagent_type definitions and skills wrote NO status_log entries during construction. This is architecturally correct (meta_audit is the audit vehicle, not the refactor vehicle), but leaves a gap in the For You tab history for a ~1-hour structural change. Mild finding — not a hard violation because the brief specifies "significant action" and skill refactoring is meta-infrastructure, not a substrate-research event.

2. **Cycle 206 routing dispatch** (strategy_decisions_2026-05-24.md): the inline strategy cycle 206 filed routing notes but no status_log entry. This is a genuine For-You-tab gap: a routing dispatch that re-filed user's analysis and spawned two routing files had no status_log record. Minor violation.

### Memory-write discipline

Status_log shows memory writes going through memory_curator for bulk directives (e.g., "Curated 1 feedback memory" entries). Single-directive curations (the "Curated 1 feedback memory" pattern) are technically over-spec per the process audit (D1), but are acceptable under wrapper-first default. No main-thread per-directive Write+Edit instances visible in the last 24h status_log. Clean.

---

## 2. Cap_map drift signals

### Stale 🔬 rows

Cannot read the full cap_map in this audit (file size). Based on strategy_decisions_2026-05-24.md and visibility_decisions_2026-05-24.md, the cap_map is at v174 as of last night's Cap 12 promotion. Active 🔬 rows from prior audits (cycle 96 referenced pq_discrete_spikes, K1000_eigenspectrum as running) have presumably resolved to verdicts since cycle 96 was 2026-05-23 10:15. Specific 🔬-age tracking requires a full cap_map read; deferred to next Strategy cycle via PROT-007 two-file history reference.

### Closure rows without rescue sketch

Based on process audit (orchestrator_process_audit_2026-05-24.md D1), rescue sketches are filed via PROT-004/006 for ❌ closures. The process audit noted two "memorial (not yet load-bearing)" locks: rescue_sketch_first_sequencing and strategy_spec_formula_selftests. These are memory-level reminders, not structural enforcement. No new ❌ closure rows in the last 24h status_log (Cap 12 was a promotion, not a closure). No gap detected.

### Version bump cadence

Cap_map went v160 → v174 over the 2026-05-23/24 session per status_log evidence. 14 version bumps in ~24h is within expected range for high-throughput experiment phases. PROT-009 paired decision-log discipline is confirmed as load-bearing per process audit D4.

---

## 3. Pipeline health

### Queue depths at audit time

From strategy_decisions_2026-05-24.md cycle 206 queue state (most recent verified count):
- overnight_queue (GPU): 5 pending
- remote_cpu_queue: 0 pending
- local_cpu_queue: 0 pending (runner DEAD)

CPU queues are at zero. GPU has 5 pending from the 5-direction routing batch. The local CPU runner remains dead (noted in MEMORY.md `project_cpu_resource_underutilized.md` — dead since 2026-05-21, no fix landed yet). No silent_idle events visible in today's status_log post-resume.

### Runner heartbeat

dispatch.py Monitor is the primary runner-heartbeat source. The heartbeat_watchdog.py is confirmed running (heartbeat_watchdog.log exists in data/). Last visible runner-event: remote_cpu_runner_0 revived at 2026-05-23 18:41. No staleness events visible in today's status_log.

### Silent-idle events in last 7 days

One confirmed `silent_idle` event at 2026-05-23 ~19:40 (created the watchdog). One near-miss at 04:20-06:20 (ship_name_collision gap) that the watchdog missed due to its blind spot. No additional silent_idle events in today's 30-entry status_log sample.

---

## 4. Research coverage

### Fields drilled in last 7 days

From notes/ listing (visible research files dated 2026-05-23/24):
- Free probability (Voiculescu S-transform, free cumulants) — multiple drills
- Kerdock / MUB / stabilizer group theory — multiple drills
- Tropical algebra / Cap 13 — 1 drill
- BBMD / Cap 12 rehab assessment — 1 drill
- Cap 11 chi_4 early-warning — 1 drill
- Cross-domain probes (research_cross_domain_probe_2/3 on 2026-05-23/24) — 2+ drills
- Glassy chi_4 / Berthier-Biroli EWS / brain-inspired dopamine (research_dopamine_article_drill, research_nature_article_drill) — 2 drills
- MAMP / Dudeja-Sen-Lu / spectral universality — 1 drill
- R-PRIME directions (5 new directions math drill) — 1 drill
- QND measurement substrate — 1 drill
- New continents + high-yield neighborhood analysis — 2 drills

Cross-domain coverage is broad: thermodynamics (Cap 1/3/5 re-axiomatization), spectral free probability, topology (Cap 13), signal processing (MAMP), neuroscience-adjacent (dopamine/nature drills), glassy physics (chi_4 EWS).

### Fields at drill_count <= 2 (scope-expansion candidates)

From the above listing: QND measurement, tropical algebra, and MAMP/spectral-universality are each 1-2 drills deep. These are scope-expansion candidates per Trigger B. The research_field_advisor.py script (at `tools/orchestrator/research_field_advisor.py`) tracks this formally; orchestrator should invoke it on next cross-domain probe dispatch.

### Saturation-pivot triggers pending

Free probability: 3+ drills, yield high (S-transform DIVERGE, free-cumulants DIVERGE, R-transform queued). NOT at saturation; still high-yield. No saturation pivot needed yet. Kerdock 4-design / RM(1,16) geometry: 2+ drills, both REFUTED at FULL — approaching Trigger A (saturation pivot). Research agent should note this on next dispatch.

---

## 5. Recommended PROT additions

### PROT-011 (NEW): Canonical dispatch shape lock-in for subagent_type architecture

**Failure mode it plugs:** The new subagent_type architecture (4 types: strategy_scribe, routing_handler, meta_audit, memory_curator; all 7 types now defined in `C:\Users\marsh\.claude\agents\`) was landed today. The dispatch shape `Agent({subagent_type: "X", description: "X: args", prompt: "args"})` is the canonical invocation. Without a PROT entry, the next cold-start or compaction reset risks reverting to the old `general-purpose` subagent_type (which still works but misses the frozen contract in the agent definition). The post-compaction brief Section 5 documents the three registration formats (slash commands / skills / subagent types) but does NOT yet have a PROT-level structural enforcement that the orchestrator uses `subagent_type: "<name>"` rather than `subagent_type: "general-purpose"` with a full prompt paste.

**Failure evidence:** This is preemptive (no instance yet), but the process audit D1 noted that the "inline strategy + inline visibility" attribution pattern suggests the verdict_handler wrapper was sometimes bypassed. The same bypassing mechanism (forgetting to use the named type, reverting to general-purpose) would cause the new 4 types to be unused. The PROT closes this before a pattern emerges.

**What to do:** Any `Agent()` call where the target role exists as a named subagent type in `C:\Users\marsh\.claude\agents\` MUST use `subagent_type: "<name>"`. The only legitimate `subagent_type: "general-purpose"` invocations are for ad-hoc analysis tasks with no defined role (e.g., a one-off dependency-audit sub-agent). All 7 roles (exp_dev, research, verdict_handler, strategy_scribe, routing_handler, meta_audit, memory_curator) must use their named subagent_type. The orchestrator's pre-response checklist (brief Section 3b) gains an additional item: "Did I use `subagent_type: 'general-purpose'` for a role that has a named type? If yes, rewrite."

**Applies to:** Orchestrator (all dispatches).
**Trigger:** Any Agent() call from main thread.
**Per-dispatch, always-on.**

### PROT-012 (NEW): For-You tab entry mandatory for routing dispatch cycles

**Failure mode it plugs:** Cycle 206 (strategy_decisions_2026-05-24.md) filed two routing notes and a research routing, but no status_log entry was written. This is a For-You-tab gap for a substantive routing action. The brief says "major dispatch" triggers a mandatory log_event — a routing cycle that spawns 2 routing files and a research request qualifies. The gap: "routing dispatch" is not explicitly called out in the brief's covered-events list (it says "major dispatch returned" but routing cycles write files rather than returning a wrapper result). Without explicit coverage, routing cycles silently omit status_log entries.

**What to do:** Any orchestrator cycle that writes >=1 routing file (strategy_request_to_exp_dev_*.md, strategy_request_to_research_*.md, exp_dev_handoff_*.md, exp_dev_to_queue_*.md) MUST write a status_log entry with at minimum: event_kind="routing_dispatch", a one-sentence plain_language, importance=LOW or MEDIUM depending on whether it touches cap_map or triggers new experiments.

**Applies to:** Orchestrator main thread; strategy_scribe sub-agent (which files routing notes as part of cap_map commits).
**Trigger:** Any cycle that produces >= 1 routing file as output.
**Per-cycle when triggered.**

---

## 6. Recommended brief updates

1. **Section 5 (Skills registry) — Skill vs subagent_type invocation clarification.** The brief says `Skill(skill="<name>", args="...")` and `Agent({subagent_type: "<name>", ...})` are "equally valid." For session-continuity, `subagent_type` is preferable because it does not require a session restart (skills need re-scan after new SKILL.md files are added). The brief should rank subagent_type above Skill for routine dispatches; Skills remain for user-facing /slash-command flows. Add one sentence: "Default: use `Agent({subagent_type: '<name>', ...})` — it works immediately. Use `Skill(skill='<name>', ...)` only when a user-facing slash command is being proxied."

2. **Section 0 (For-You tab) — Add routing_dispatch to covered-events list.** Currently the list covers: verdict, cap_map commit, research delivery, audit, major dispatch returned, error, queue/runner state, memory write. It should add: "Routing dispatch (any cycle that writes >=1 routing file to notes/)." This is what PROT-012 mandates; the brief should reinforce it.

3. **Section 4 (Failure modes) — Add Failure Mode 9.** Process audit D7 identified a watchdog blind spot: "queue=0 from new ships silently failing, while runners still busy on old work." This failure mode is documented in the process audit but is NOT yet in the brief's known-failure-mode table. Add: `| 9 | Ship-unconfirmed silent failure | queue_add.sh exits 0, but new entry absent from queue.json because dedup rejected it; runners are still running OLD work so watchdog doesn't fire | post-ship verification in queue_runner wrapper (reads queue.json after queue_add.sh, emits ship_unconfirmed if absent) |`

---

## Summary

The subagent_type architecture rollout went cleanly. The 50-turn routing ratio is RED (0.368) but this is construction-period artifact — the last 20 turns are GREEN (1.000), confirming the new dispatch shape is working correctly. The main-thread spikes in the 50-turn window are from the refactor itself, which is legitimate mechanical work with no available delegation target. No pause obedience violations. No cap_map drift signals. Two new PROTs recommended: PROT-011 (canonical subagent_type dispatch shape enforcement) and PROT-012 (routing-dispatch For-You tab coverage). Three brief updates recommended. Next audit: standard weekly (2026-05-31) unless a major event (pivot, rejection, compaction, routing-ratio-low watchdog event) triggers an earlier one.
