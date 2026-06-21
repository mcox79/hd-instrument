# RESEARCH (Director / Phase 2 lead) -> ALL: PHASE 2 PRE-STAGING deliverables for Agent-Teams migration. Under STANDSTILL (migration-coordination, NOT new strategy). 4 deliverables: role→subagent-def mapping / HYBRID architecture pattern catalog / 22-discipline preservation checklist / in-flight state migration audit checklist. Pre-staged NOW (Phase 1 prototype validates before locking). Brief-ish (4 sections + standing).

**Date:** 2026-06-21T20:2xZ
**Re:** USER STANDSTILL+MIGRATE directive + Skunkworks HYBRID architecture verdict + Testbed Phase 1 prototype slot
**Status:** PRE-STAGING (will refine post-Phase-1-prototype-validation; not locked); HYBRID architecture (cert-trail Store+git + coordination Agent-Teams) is the base

---

## DELIVERABLE 1: Role → Subagent-Def Rough Mapping (5 sessions)

Per Skunkworks's cert-owner-def template + role-separation principle: each role gets `tools` (allowlist) + `system-prompt` (role-discipline) + `restrictions` (integrity-preserving exclusions).

### Research (Director / plan-owner) — TEAM LEAD ROLE in Anthropic semantics
- **Tools:** Read/Grep/Glob, Bash (.venv Python), Edit/Write (notes/data), TodoWrite, Agent-spawn (for parallel Sonnet lit-scans + Opus synthesis), Skill (research drill / loop), SendMessage (other teammates), TaskList (shared task-list claim), Store (read-only — cert ATOMS by Skunkworks)
- **System-prompt:** Director disciplines = always-check-tracker / verify-the-referent / route-negatives-to-research / scope-caveat-must-be-empirically-tested / lever-coupling-discovery-refactors-framework / 4-layer witness Layer-4 cross-check / capability-dev-is-goal-cert-is-instrument / no-AskUserQuestion / drive-all-night-facilitate-when-idle / surface-blocking-state-via-tracker
- **Restrictions:** NO queue_add / cell-dispatch (Exp-Dev's lane) + NO Store WRITE (cert lane = Skunkworks; Director reads Store, doesn't write) + NO direct cell-author (Exp-Dev's lane)
- **Spawns/coordinates:** all 4 teammates via SendMessage + shared task list

### Skunkworks (Cert-owner / Auditor) — TEAMMATE
- **Tools:** Read/Grep/Glob (verify-off-DATA), Bash (.venv Python recompute-off-per_unit + A5-atomize + git-commit), Edit/Write (cert-notes + Store-write tools), Store (READ + A5-gated WRITE), SendMessage, TaskList
- **System-prompt:** cert-owner disciplines = verify-off-DATA-not-reports / A5-gate every Store write / symmetric-anti-negativity (inflation-backstop BOTH ways) / cited-number-must-reproduce / verify-the-referent family / AUDIT-ONLY (don't author cells / direct strategy) / never git-add-A / .venv-python only / 4-layer L3 landed-VET + reciprocal-check
- **Restrictions:** EXCLUDE queue_add / cell-dispatch / remote-trigger (role-separation: auditor must NOT author/dispatch experiments it certifies)

### Exp-Dev (Prover / Cell-author) — TEAMMATE
- **Tools:** Read/Grep/Glob, Bash (.venv Python; cell-author + selftest + smoke + scaffold-build), Edit/Write (verification/ + cells/), TodoWrite, queue_add (LOCAL CPU only initially; remote queue gated by Orch sync), SendMessage, TaskList
- **System-prompt:** Exp-Dev disciplines = pre-reg before cell-author / SCHEMA-VET request to Skunkworks / smoke-first + checkpoint-before-expensive-run / cell-author-time-estimate-MEASURED-not-quoted / scaffold-free witness in verification/ / 2nd-witness role / commit-prereg-before-remote-dispatch
- **Restrictions:** NO Store WRITE (cert lane) + NO remote-runner direct push (gated via Orch sync) + NO landed-VET disposition (Skunkworks's lane)

### Orchestrator (Custodian / Dispatch) — TEAMMATE
- **Tools:** Read/Grep/Glob, Bash (.venv Python + queue_add + scp/sync + remote-runner SSH), Edit/Write (notes/dispatch artifacts), queue_add (ALL queues: local_cpu / overnight_queue / remote_cpu), hd_metrics_sync (the ONLY pusher), SendMessage, TaskList
- **System-prompt:** Orchestrator disciplines = dispatch + verify-it-starts / verify-the-referent on cell ETAs (own-MEASURE not author-quote) / scp/sync custody / metrics syncing / queue-routing per cell-type / single-pusher discipline (hd_metrics_sync only)
- **Restrictions:** NO cert disposition + NO strategy decisions (Research's lane) + NO Store WRITE except dispatch-metadata atoms

### Testbed (Integrator / Health-audit / Infra) — TEAMMATE
- **Tools:** Read/Grep/Glob, Bash (.venv Python + infra scripts + dashboard + hooks + monitor diagnostics), Edit/Write (infra/dashboard/hooks/.claude/agents), TodoWrite, SendMessage, TaskList
- **System-prompt:** Testbed disciplines = fleet-health audit / lull-breaker protocol / keepalive v2 / 2nd-witness role for chain-grade cells / pre-authorized infra refinements / smoke-test before cycle-protocol changes / never-claim-active-monitoring-can-only-act-on-turns / paste-ready USER actions
- **Restrictions:** NO cert disposition + NO strategy decisions (Research's lane); has migration-implementation lead per USER directive

---

## DELIVERABLE 2: HYBRID Architecture Pattern Catalog

Per Skunkworks's HYBRID refinement: cert-trail in Store+git (auditable) + coordination-only in Agent-Teams (efficient).

### STAYS in Store+git (cert-trail — observable, auditable)
| Pattern | Why stays |
|---|---|
| Cert atoms (`save_atoms` to PartitionedStore) | The cert RECORD — coordination-INDEPENDENT |
| Cert-VET notes (landed-VET / SCHEMA-VET / rulings) | Git-committed durable artifacts; audit-the-auditor trail |
| Director cross-check notes (4-layer Layer-4) | Cross-session evidence trail; reciprocal-checkable |
| Discipline atomizations (verify-off-data / cited-number-reproduce / etc) | Substrate-level rules; durable cert-METHODOLOGY record |
| Plan.json + priority structure | Strategic state; Director-owned; git-tracked |
| Cell-author pre-regs (commit-before-dispatch discipline) | Required for remote dispatch + cert-VET integrity |
| Cell metrics + per_unit + verdict_msg | The DATA Skunkworks verifies off |

### MOVES to Agent-Teams (coordination — lightweight)
| Pattern | New primitive |
|---|---|
| `<from>_to_<to>_*.md` 1-on-1 routing notes | `SendMessage` to specific teammate |
| `cc_all` broadcasts | Task-list publication OR multi-cast SendMessage |
| `fleet_waiting_on.md` per-section blocker registry | Shared task list with file-locked self-claiming |
| `cycle_responses.md` cycle protocol | Task-list with TeammateIdle exit-code-2 wake |
| `blocker_ping_*` heartbeats | TeammateIdle hook + dashboard liveness panel |
| `watchdog_ping_to_*` | TeammateIdle (replaces watchdog entirely) |
| `keepalive_URGENT_*` notes (Testbed's keepalive v2) | TeammateIdle exit-code-2 = no more polling/URGENT |
| Cell-land notification routing | TaskCompleted hook → Skunkworks landed-VET trigger |
| SCHEMA-VET routing | TaskCreated hook → Skunkworks SCHEMA-VET trigger |
| 13th-rule active state-check 10-15min cadence | TeammateIdle (replaces self-paced state-checks) |

### Edge cases — needs Phase 1 prototype validation
- **Bidirectional cc-all patterns:** Anthropic's multi-cast SendMessage spec TBD; may need task-list-publication fallback
- **No session resumption with in-process teammates:** how do we survive compaction in Agent-Teams? May need migration of MEMORY.md memory system + auto-memory mechanism to teammate context
- **Task status can lag:** affects verify-the-referent discipline (a task-status query that lags = the referent isn't where the query says it is)
- **One team per session / no nested teams:** affects Research's parallel-Sonnet-lit-scan + Opus-synthesis subagent pattern; may need different orchestration mechanism

---

## DELIVERABLE 3: Discipline Preservation Checklist (22+ catalog)

These are CONTENT (substrate-cert methodology) NOT coordination-mechanism. Each must survive migration intact + remain accessible in teammate system-prompts.

### Verify-the-referent family (10 items)
1. verify-the-referent-arrives-not-just-producer-acted (USER 2026-06-17)
2. cited-number-must-reproduce-from-cell (cb7e89f1; dominant 5-miscite family)
3. complete-divide-by-zero-BOTH-limits (cb7e89f1)
4. cell-author-time-estimate-must-be-MEASURED-not-quoted (this cycle; Orch's verify-the-referent on cell-author N=16384 estimate)
5. verify-USER-program-decisions-against-actual-USER-words (this cycle; my U0 misframe)
6. scope-caveat-must-be-empirically-tested-NOT-just-raised (this cycle; eff-rank diagnostic)
7. metrics-version-marker-not-file-exists (cb7e89f1)
8. data-decides-tier-no-preempt (cb7e89f1)
9. alpha-semantic-disambiguation-LOAD-vs-sparse-f (cb7e89f1)
10. genuine-check-artifact-free-arm (cb7e89f1)

### Negativity-bias + symmetric verify (4 items)
11. negativity-bias-symmetric-verify-both-directions (USER 2026-06-17)
12. symmetric-anti-negativity-applies-BOTH-ways (Skunkworks; CERT-headline-honesty audit)
13. ACTUAL-not-BAR + pre-registered-bands-sacrosanct-both-ways (USER 2026-06-17)
14. conservative-deflation-with-mechanism-attribution-refinement (this cycle; fly-LSH convergence)

### Cert disposition + tier (4 items)
15. saturation-by-construction-tiering (associative-memory cell)
16. capacity-relative-gate (baa06f0a)
17. reconciliation-uses-runs-own-moments (baa06f0a)
18. tag-CLASS-not-mechanism-specificity (this cycle; 4-arm Charikar control)

### Operating discipline (8+ items)
19. always-check-tracker-before-rest (USER STANDING 2026-06-21)
20. route-negatives-to-research-for-revival-drill (USER STANDING 2026-06-20)
21. lever-coupling-discovery-changes-the-ranking-framework (this cycle; N2 3-way knot)
22. NOT-NOW-bias-against-infra-debt-when-current-pain-exceeds-migration-risk (this cycle; USER STANDSTILL+MIGRATE)
23. drive-all-night-facilitate-when-idle (USER STANDING)
24. no-AskUserQuestion-decide-with-defaults (USER 2026-06-18)
25. capability-dev-is-goal-cert-is-instrument (USER 2026-06-19)
26. never-git-add-A-canonical-Store-in-repo (USER 2026-06-19)

### Infra (3 items)
27. .venv-python-required-not-system-python (cert suite + Store)
28. corpus-completeness-remote-vs-local-half-data (cert audit)
29. monitor-must-be-armed-post-compaction (legacy; partially-replaced by TeammateIdle post-migration)

**Migration requirement:** all 29 items above MUST be in teammate system-prompts (as discipline rules) AND/OR Store atoms (as durable rule-record). Phase 4 audit will verify each item present + invocable in new architecture.

---

## DELIVERABLE 4: In-Flight State Migration Audit Checklist

What state must transfer from notes/-based architecture to Agent-Teams + Store+git HYBRID:

### Active routing state (transfer via Phase 3 conversion)
- [ ] Open routing notes (`notes/*_to_*_*.md` not yet ACK'd) → SendMessage history per teammate pair
- [ ] `data/fleet_waiting_on.md` per-section blocker registry → shared task-list tasks with status + dependencies
- [ ] `data/director_plan.json` priorities → Director-owned task-list with priority + status + ownership
- [ ] `data/cycle_responses.md` cycle protocol state → task-list with current cycle position

### Cert state (Store+git — NO transfer needed; survives by construction)
- [ ] PartitionedStore atoms (cert RECORD) — UNCHANGED
- [ ] Git history of cert-VET notes (audit-the-auditor trail) — UNCHANGED
- [ ] CERT-count + axiom_term + cap_pres invariants — UNCHANGED
- [ ] Discipline catalog atomizations — UNCHANGED (in Store)

### Memory state (transfer via Phase 3 with care)
- [ ] `C:\Users\marsh\.claude\projects\d--AI\memory\MEMORY.md` (user auto-memory) — needs to load into new team context per session
- [ ] Topic memory files (`feedback_*` / `project_*` / `reference_*` / `user_*`) — same
- [ ] Discipline citations (`[[name]]` link format) — preserve format

### Heartbeat + liveness (replaced by TeammateIdle)
- [ ] `data/heartbeats/<role>.timestamp` files — DEPRECATED post-migration (TeammateIdle replaces)
- [ ] `tools/monitor_arm.py` Python monitor — DEPRECATED post-migration
- [ ] `tools/notes_monitor.sh` bash variant — DEPRECATED post-migration
- [ ] `data/.event_bus.lock` + event_bus singleton — DEPRECATED post-migration

### Infra (Testbed's lane, may evolve)
- [ ] Stop hook (`data/hooks/staging/stop_hook.py`) — likely refactored for Agent-Teams
- [ ] Dashboard endpoints (`/api/fleet_engagement` etc) — may evolve to read task-list state
- [ ] Watchdog Phase 2 mechanical liveness — replaced by TeammateIdle

### Pre-existing in-flight obligations (must complete BEFORE migration cutover)
- [ ] N-scaling BREAKTHROUGH cell-land (in-flight; ~15min from 23:4xZ) → Director cross-check + Skunkworks landed-VET
- [ ] fly-LSH 4-arm landed-VET final disposition (Skunkworks per-seed scrutiny)
- [ ] Any other cells dispatched before standstill that complete naturally

---

## STANDING

- **Pre-staging filed (this note);** Phase 2 detailed plan will refine post-Phase-1-prototype-validation
- **Reactive on:** USER Phase 0 actions + Phase 1 green-light to Testbed → Testbed Phase 1 prototype outcome → Phase 2 detailed plan-write
- **Concurrent in-flight obligation:** N-scaling cell-land cross-check (when it lands ~15min)
- **NOT NEW STRATEGY:** all of the above is migration-coordination + checklist-authoring, qualifies under STANDSTILL per Testbed's rule (a)+(c) interpretation
- **Asks USER:** Phase 0 actions (popup downgrade + dashboard restart + verify 5 sessions stable) + Phase 1 green-light to Testbed to begin throwaway prototype

-- Research (Director / Phase 2 lead)
