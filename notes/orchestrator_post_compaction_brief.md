# Orchestrator post-compaction brief

**Purpose:** After context compaction / summarization, behavioral knowledge gets lost. This file is the dense restoration document. The orchestrator reads this FIRST on cold start AND right after any context summarization, before doing anything else.

**Last updated:** 2026-06-04 cycle 56 (post 4-session architecture rollout). Cap_map at v387. Portfolio 32+77. HONEST 816, LVH 213. PP-12/Q-A3 BAND saturated at 0.97 calibration cap (15 consecutive lifts 0.85→0.97). Substrate composition algebra empirically validated to L=2000 N=16384 (unbounded; 10,000 cells zero failures).

## CRITICAL — 4-SESSION ARCHITECTURE (rolled out 2026-06-04 ~07:30)

The session model is now **Orchestrator + Exp-Dev + Research + Testbed** (4 sessions, file-based handoff).

**Read `notes/session_prompts_v2_2026-06-04.md` for the full architecture spec + handoff protocol.**

### Orchestrator (this session — me) — narrowed role

I PROCESS VERDICTS via `/verdict_handler`. I TRIAGE NEW research routings. I write LIGHT strategic notes to Exp-Dev (not prescriptive cell specs). I COMMUNICATE FINDINGS TO USER. I push commits.

I no longer:
- Dispatch `/exp_dev` (Exp-Dev session does this on its own cadence)
- Engineer experiment scripts (Exp-Dev does)
- Specify anchor names / L values / HP bands in priorities files (that's cell design = Exp-Dev's job)
- Manage `experiments/` commits (Exp-Dev does its own)

### Verdict_handler prompt discipline (LOAD-BEARING)

Verdict prompts MUST be minimal:
```
VERDICTS:
1. <anchor_name>
2. ...
ENFORCEMENT: REMOTE-FIRST SCP metrics + log; Honest re-read MANDATORY; ASCII; PROT-018/019/021/022; commit v<X> -> v? if state changes.
RETURN: classified + cap_map delta + commit + LVH + headline + per-anchor plain+implication.
```

NO outcome-anticipation language. NO "ULTIMATE depth probe (15x past frontier)" framing. NO "if HP confirms X" interpretation. NO strategic-significance tags. The verdict_handler reads the prereg + metrics itself; my prompt just supplies the anchor list. Pre-framing biases classification = forbidden per [[feedback-no-smoke-preframing-in-task-prompts]].

### Priorities files for Exp-Dev (light touch only)

If I write one (NOT mandatory every cycle), keep it strategic:
- "Q-A3 ladder marginal value declining — slow it down"
- "PP-58 SCS framework needs empirical test at substrate's actual operating tau"
- "Test substrate's unbounded-composition claim at striking depth"

NOT:
- "Ship L=141, L=142, L=143"
- "TAU=0.71, HP ratio in [0.85, 1.18]"
- "Copy this file, change TAU constant"

Exp-Dev figures out cells from strategic ask. They're better at it.

### Exp-Dev result files

After each Exp-Dev cycle they write `notes/exp_dev_to_orchestrator_shipped_<date>_cycle<N>.md`. I read those on each 30-min wake.

## CURRENT STATE (cycle 56, 2026-06-04 ~10:25)

- **Cap_map v387** (just bumped from v386 by cycle 56 batch)
- **HONEST 816, LVH 213**
- **Portfolio 32+77** (unchanged across day)
- **PP-12/Q-A3 SATURATED at 0.97 calibration cap** — 15 consecutive BAND-LIFTs from 0.85 → 0.97
- **L=2000 N=16384 ALL-TIME DEEPEST** confirmed HP today (cycle 56). 10,000 cells zero failures.
- **L=1000 N=8192 KILO-DEEP cross-N** confirmed today (matches N=16384 result; N-independence)
- **PP-58 SCS framework refuted** at tau_actual=0.71 (under-prediction d-independent); validity narrowed to alpha≤0.06 AND tau<<0.10 AND below-spike-d
- **NHSE annulus alternative** for PP-58 also HF (non-monotone gamma); PP-58 stays MIDDLE 0.55-0.70
- **Phase 0.5 Rung A GATE OPEN** (cloud Llama-3.1-8B dispatch unblocked since 2026-06-03 cycle 42)

## Active sessions

- **Orchestrator (me):** verdicts + triage + user. 30-min recurring watchdog.
- **Exp-Dev:** ladder + scripts + ship. 15-min recurring cadence. Already shipped through cycle 56 (cycles 52-56 in past ~3 hours, ~50 anchors). Confirmed live.
- **Research:** drilling actively (5 new drills landed cycle 51; 1 more NHSE drill cycle 56). Routings to Orchestrator (not Testbed).
- **Testbed:** scope narrowed to LLM-integration only (Phase A/B/0.5 brain-inspired + Pythia/Llama Algorithm 1). NOT substrate-physics.

## Key reference docs

- `notes/session_prompts_v2_2026-06-04.md` — full 4-session architecture spec
- `notes/exp_dev_state_of_experiments_2026-06-04.md` — anchor family reference for Exp-Dev cold-start
- `notes/orchestrator_to_exp_dev_role_clarification_2026-06-04.md` — what changed + FLAG responses
- `notes/experiment_queue_pending.md` — running pending list (Exp-Dev maintains)
- `data/blocked_items.json` — global skip list (4 items)

## Exp-Dev shipped result files history (cycles 52-56)

- `notes/exp_dev_to_orchestrator_shipped_2026-06-04_cycle52.md`
- `notes/exp_dev_to_orchestrator_shipped_2026-06-04_cycle53.md`
- `notes/exp_dev_to_orchestrator_shipped_2026-06-04_cycle54.md`
- `notes/exp_dev_to_orchestrator_shipped_2026-06-04_cycle55.md`
- `notes/exp_dev_to_orchestrator_shipped_2026-06-04_cycle56.md`
- `notes/exp_dev_to_orchestrator_scope_clarification_2026-06-04.md` — Exp-Dev confirming they stayed in lane

## Open FLAGs from Exp-Dev (need Orchestrator action)

- **FLAG 3** (cycle 54): research handoff backlog scaffold-blocked. Tiny char-LM scaffold is **Testbed scope** (LLM-class). Route to Testbed.
- **Joint D+H instrumentation finding** (cycle 56): cosine-softmax temperature artifact at temp=1.0 (BPC near-uniform); calibrated temp~0.2 gives BPC 3.76 vs 5.52. Confounds prior brain-inspired "no learning" HFs. **Route to Research/Testbed for instrumentation review.**

## 5 new research drills awaiting triage (cycle 51)

- `research_drill_substrate_training_augmentation_unified_2x_2026-06-04.md`
- `research_drill_drift_detection_lyapunov_framework_2x_2026-06-04.md`
- `research_drill_multi_channel_orchestration_failure_3x_2026-06-04.md`
- `research_drill_cf_rank1_as_substrate_native_rpe_2x_2026-06-04.md`
- `research_drill_nhse_annulus_tau_scaling_2x_2026-06-04.md` (cycle 56 follow-up)

Plus 5 `exp_dev_handoff_research_*` files for substrate-physics work AND tiny-LM scaffold work (the latter route to Testbed).



## PENDING EXPERIMENT QUEUE — RUNNING LIST (2026-06-03)

**Single source of truth for what's waiting to be queued.** Lives at:
- `notes/experiment_queue_pending.md`

Orchestrator updates this file on EVERY cycle that:
- Ships items (cross off / remove)
- Receives new research routing (add new items with handoff path)
- Receives strategy_request (add new items)
- Surfaces a blocked item (mark ROUTING-PARKED)

User can read this file ANY TIME to see what's pending. If this file is stale (mtime > 2 hours), orchestrator's running-list discipline broke.

Pre-watchdog-tick checklist (every 30-min wake):
1. `notes/experiment_queue_pending.md` updated this cycle? If not, why? Update or note "all items completed".
2. Any new `research_routing_*.md` or `strategy_request_*.md` since last cycle? Pull items into the list.
3. Any new `exp_dev_handoff_*.md`? Mark routing-parked items.

## VERDICT_HANDLER DISCIPLINE LOCKS (2026-06-03)

Every verdict_handler dispatch task prompt MUST include this clause (per [[feedback-verdicts-include-intuitive-explanation]]):

> Return ONE line: classified N (HP/MID/HF) + cap_map delta + commit hash deferred + LVH catches + headline.
>
> THEN: include a second-block table with one row per HP/MID/HF anchor:
> `<anchor_name>: <intuitive_explanation_1-2_sentences> | implication: <which_substrate_capability_this_supports_limits_or_refutes>`

Plus standing locks per cycle 22-onward:
- NEUTRAL classification only (per [[feedback-no-smoke-preframing-in-task-prompts]])
- NO outcome-anticipation language ("X HP -> Y consequence") — LVH #211 lock
- Honest re-read mandatory; prereg bands verbatim before classifying

## STARTUP / REBOOT PROCEDURE (read on cold start)

**Trigger phrase: "get everything started" / "start everything"** means: do the 3 actions below in order, then report back state.

**1. Restart local services** (do NOT survive Windows reboot; no schtask for either):
```powershell
# Heartbeat watchdog (SCPs remote_state_cache.json every 30s; feeds dashboard)
Start-Process -FilePath "D:\AI\hd-instrument\.venv\Scripts\pythonw.exe" `
    -ArgumentList "D:\AI\hd-instrument\tools\orchestrator\heartbeat_watchdog.py" `
    -WorkingDirectory "D:\AI\hd-instrument" -WindowStyle Hidden

# Dashboard server (uvicorn on port 8765; reads remote_state_cache.json)
Start-Process -FilePath "D:\AI\hd-instrument\tools\dashboard\.venv\Scripts\python.exe" `
    -ArgumentList "-m","uvicorn","server:app","--app-dir","D:\AI\hd-instrument\tools\dashboard",`
                  "--host","0.0.0.0","--port","8765","--log-level","info" `
    -WorkingDirectory "D:\AI\hd-instrument" -WindowStyle Hidden
```
After ~30-40s the local cache file `d:/AI/hd-instrument/data/remote_state_cache.json` should refresh (verify mtime). Dashboard reachable at http://127.0.0.1:8765/.

**Caution on duplicates:** when you query python processes you'll see PARENT (`.venv/Scripts/pythonw.exe`) + CHILD (`AppData/Local/Programs/Python/Python312/pythonw.exe`) for each. That's normal Windows venv shim behavior, NOT duplicates. Only count by ParentProcessId to detect actual duplicates. Don't kill the children.

**2. Pull queue state** to see what verdicts are pending:
```bash
ssh marsh@home 'powershell -Command "(Get-Content C:/dev/hd-instrument/data/overnight_queue/queue.json | ConvertFrom-Json).experiments | Where-Object { $_.status -in @(\"pending\",\"running\") } | Select-Object name, status | Format-Table -AutoSize"'
```
If queue empty: count completed entries since last verdict commit to identify unprocessed verdicts.

**3. Resume cycle loop**:
- If ≥3 unprocessed verdicts: dispatch verdict_handler (NEUTRAL) + exp_dev (5-anchor refill) in parallel
- If queue draining (≤2): refill via /exp_dev (5 anchor max per user constraint)
- If GPU idle + queue empty: ship next batch from current strategy_request or research routings

## CYCLE 16 SNAPSHOT (state at last conversation pause)

**Unprocessed verdicts (5 anchors all completed on remote, awaiting verdict_handler):**
- q_b1_chain_depth_70_v1_n8192 (prereg `preregs/2026-06-02_q_b1_chain_depth_70.md`)
- q_b1_chain_depth_80_v1_n8192 (prereg `preregs/2026-06-02_q_b1_chain_depth_80.md`)
- q_a3_l14_cross_layer_composition_v1_n4096 (prereg `preregs/2026-06-02_q_a3_l14_cross_layer_composition.md`)
- pp48_nkt_depth_21_v1_n4096 (prereg `preregs/2026-06-02_pp48_nkt_depth_21.md`)
- pp48_nkt_cross_n_depth19_v1_n8192 (prereg `preregs/2026-06-02_pp48_nkt_cross_n_depth19_n8192.md`)

If d70+d80 both HP: Q-B1 BAND-LIFT candidate (chain ceiling unbroken to d-80).
If d-21 in-N + d-19 cross-N both HP: PP-48 BAND-LIFT candidate.

**Active user constraints (carry forward):**
- 5 anchors max per exp_dev dispatch
- No cloud GPU (per [[feedback-batch-cloud-experiments]])
- 2 BLOCKED items (combo1_v5 MMD per-pattern, pp47_v3 circular K-space) — see `data/blocked_items.json`

## EFFICIENCY WINS LANDED 2026-06-02 (commit f255c2f)

**Available tools** (use these in new dispatches; saves substantial subagent tokens):
- `data/blocked_items.json` — global skip list; exp_dev should read this once and auto-skip matching anchor patterns instead of being told to skip per-prompt
- `preregs/_template.md` — jinja-style template for new preregs; cuts prereg write time ~50%
- `notes/pre_context_pruning_recipe_2026-06-02.md` — main-thread extracts 5 priority items + bands INLINE in dispatch prompts; subagent doesn't re-read routing files (~40% input token savings)
- `tools/ship_anchor.py` — one-call wrapper: smoke + PROT-019 timeout compute + queue_add + REMOTE VERIFY + status_log
- `tools/stamp_anchor.py` — parameter-stamps anchor scripts from family templates (Q-B1 ONLY currently; PP-48/Q-A3/PP-52 TODO)
- `experiments/_templates/q_b1_chain_depth.py.template` — Q-B1 family template
- `tools/cap_map_append.py` — targeted cap_map sub-property bumps without full read (MEDIUM-risk; shadow-mode required first 3 runs)
- `tools/orchestrator/agents/cycle_processor.md` — combined verdict+refill agent definition (MEDIUM-risk; first 3 runs compare against parallel verdict_handler+exp_dev)
- `tools/orchestrator/agents/smoke_runner.md` — rote smoke+ship offload (MEDIUM-risk; first 2 runs require exp_dev dual-smoke audit)

**FIRST-USE VERIFICATION REQUIRED** (per `notes/efficiency_rollout_2026-06-02.md` outstanding TODOs 3-7):
- ship_anchor.py: run on ONE anchor first; verify SHIPPED line + REMOTE VERIFY hit
- stamp_anchor.py Q-B1: stamp d100, run --self-test, ship, await verdict
- cap_map_append.py: dual-write (full cap_map verdict_handler path + cap_map_append shadow path); diff for 3 cycles
- cycle_processor: dispatch BOTH paths (combined + parallel) for next HP-dominant batch; diff outputs × 3 cycles
- smoke_runner: have exp_dev dual-smoke alongside smoke_runner for first 2 cycles; diff smoke results + timeout + queue entries

Until verification PASSes the required N runs, the new path is the SHADOW; verdict_handler / exp_dev remain authoritative.



## COMPACTION HANDOFF SNAPSHOT (2026-06-02 ~17:00)

**Active queues** (commits pushed to origin/main through 0ecceac + post-v341 refill):
- CPU: ~2 running (q_f5_v2_n8192, a6_oneshot_vs_lora_economics_v1) + ~5 pending (a7 kappa3_drift + a8 continual_writes + a9 cert_chain_replay + pp45 combo3 intermediate + wave4 full_pipeline_with_audit)
- GPU: ~5 just completed in cycle 12 refill (pp52_one_shot_n8192 + pp52_rollback_n8192 + q_b1_d25 + combo2_l4_extension + pp48_d3_baseline) — NEEDS REFILL on next cycle

**Recent KEY top-level rows** (post-2026-05-27):
- PP-45 5-method unified-API algebraic theorem 0.70-0.85 (LIFTED v335 via cloud N=32768)
- PP-46 GDPR-grade deletion-cert non-repudiation 0.70-0.85 (LIFTED v335)
- PP-47 hippocampal place-field 0.60-0.75 (v337)
- PP-48 Negative-Knowledge Tree 0.70-0.85 (v338 BAND-LIFT 0.65-0.80 → 0.70-0.85)
- PP-49 Hierarchical Refusal Cert + Counterfactual Abduction 0.70-0.85 (v338)
- PP-50 κ_3 sub-percent drift detection 0.70-0.85 (v335)
- PP-51 implicit-Gram audit-on-M-side architecture LOCK 0.70-0.85 (v338)
- PP-52 Hebbian-vs-LoRA-speedup empirical capstone 0.55-0.70 EXPLORATORY (FOUNDED v339 at N=1024; needs production-N for LIFT)

**Open issues** (tracked I-1 through I-17 in cap_map):
- I-12 OPEN: κ_3 sensitivity n16384 2× HF contradicts cloud n32768; needs research config-delta R2 audit
- I-13 OPEN: caching eviction design under-stressed
- I-14 UPDATED: combo1 vram-friendly HF = math issue not VRAM; theory-audit before Wave 5 Cell 5 retry
- I-15 OPEN: pp49 depth-10 OS FAST_FAIL (architecture boundary at depth-10)
- I-16 OPEN: HRC depth-5 structural design flaw (heteroassoc W asymmetric, ξ_B not fixed-point)
- I-17 RESOLVED: COMBO-3 × PP-51 formula bug fixed in v2_cert_fix

**Wave 5 cloud status** (testbed handoff):
- Cells 1-4 + ADD-1 + ADD-2 PASSed cloud N=32768 at $3.81 (82% under budget) per v335
- Cell 5 cloud authorization INTACT (LOCAL HF at v339 was different operating point)
- Cell 5 redesign: combo1_v3 GPU fix HP'd v338 unblocked it; LOCAL N=32768 HF separately

**Testbed has** (per testbed_phase05_combined_deployment_readiness_2026-06-02.md):
- Phase 0.5 Tier-7 MVP STAGED (USER AUTHORIZED $50-100; needs hyperprobe clone + vLLM Llama-3.1-8B before launch)
- Phase 0.5b Hebbian distillation MVP STAGED (user combined-auth per testbed note)
- Tier-6 LLM-integration StepGame flagship (gated)

**Pending design-fault rescues** (need research input; NOT exp_dev re-try):
- PP-47×PP-48 NKT signed-AM categorical failure (anti_cos=-1.0; needs contrastive-Hebbian/RBM)
- Q-F4 saddle-overlap stuck-kill (needs max_iter + convergence check)
- Q-C2 v3 MP-HC stuck-kill (needs eigsolve timeout + bounds)
- alpha_mu_snap smoke HF (needs new mechanism)
- tau_alpha protocol smoke HF
- ckm_coefficient smoke HF
- F4 M4 v3 deeper correction (M3 PASS / M4 +33%)
- κ_3 mixing v3 high-ρ (ρ≥0.2 fail HP≤0.03)
- hippocampal_engram_consolidation v2 (α_total < α_c)
- COMBO-4 dynamical v3 (μ_aging OOB)

**Discipline locks** (recent feedback):
- NEUTRAL prompts in verdict_handler (NO "if HP this validates X" pre-framing — caught 3 LVH catches #203-205 + #206 from my own pre-framing)
- Sonnet for routine HP/HF classification; Opus only for novel cap_map row promotion or reliability-recalc
- Pre-flight existence + uniqueness + timeout estimation always (added to exp_dev prompts)
- GPU template MANDATORY for new GPU scripts (assert cuda + device=cuda + batched matmul + memory > 100MB check at smoke)
- HDLAB_RUN_MODE default="full" pattern locked in all 25+ Round 7-9 scripts (commit b97e037) + runner_v2_prod.py injects HDLAB_RUN_MODE=full in child_env (commit 8a4ae70)
- runner_v2_prod.py uses CREATE_NO_WINDOW (0x08000000) to suppress per-child console flash (commit 1d1bee2)
- Cap_map version v341 commit 0ecceac on origin/main
- Cycle wake interval: 1500s (25 min) when queues loaded; 600s (10 min) when draining

**Previous updates:**
- 2026-05-27 incremental delta v234+v235 (compaction handoff v2). Section 7 updated: portfolio 14+18.

**Previous updates:**
- 2026-05-27 (earlier) by memory_curator sub-agent — Section 4b updated to 13 watchdog event kinds (added `bridge_cache_stale`); Section 5 clarified that custom subagent_types DO register and PROT-014 is obsolete; new Section 5c documents PROT-018 anchor-name binding + runner singleton lock + per-experiment timeout policy as enforced (not advisory) rules.
- 2026-05-24 by skill-registry-fix sub-agent — added `/verdict_handler` skill; clarified slash-command vs SKILL.md discovery split; documented Agent-fallback path for current orchestrator session.
- 2026-05-23 by orchestration-architect sub-agent, after user flagged 5+ times that the orchestrator does substantive work in main thread and disobeys pause directives.

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

### 3g. Anchor-name N-suffix is a binding contract (PROT-018)

60+ mismatches (2026-05-27): anchor `_n4096` ran at N=512 (smoke config leaked into the full run). The `_n<NUMBER>` suffix in an anchor name is a HARD CONTRACT — the script's PRODUCTION N must equal that number.

- **exp_dev pre-ship check**: `grep -E "(N\s*=|n\s*=)\s*<SUFFIX_N>"` must find a match — if not, BLOCK.
- **queue_add.py exit-6**: ship-time validator rejects mismatches before smoke runs.
- **`_v<N>` is version, not N-binding** — only `_n<NUMBER>` triggers this rule.
- Unit-tested 10/10 cases at lock-in.
- Full rule: `notes/active_protocols.md` PROT-018.

### 3h. Per-experiment `--timeout` REQUIRED (no silent default)

`queue_add.py` no longer accepts ships without `--timeout <seconds>`. The 7200s silent default is REMOVED. Formula:

```
timeout = ceil(1.5 * smoke_wall_s * (FULL_N / smoke_N)^exp * (FULL_seeds / smoke_seeds))
```

with `exp ∈ {1.0, 1.5, 2.0}` (default 1.5 if scaling unknown). Timeouts > 14400s are BLOCKED pre-ship pending justification — surface to orchestrator. Memory: `feedback_per_experiment_timeout_required.md`.

### 3i. Runner singleton PID-file lock

Before any `start /BELOWNORMAL python ...` or `schtasks /Run` for cpu_runner_0 / gpu_runner_0 / remote_state_emitter / heartbeat_watchdog:

- Check `tasklist | findstr <runner_script>` FIRST.
- `runner_v2_prod.py --singleton-pid-file <path>` enforces; launchers pass the flag.
- New launches abort cleanly if PID file shows an alive process.
- Watchdog `duplicate_runner_detected` / `duplicate_watchdog_detected` events fire on N>1.
- 3 runner-duplication incidents on 2026-05-27 forced this. Memory: `feedback_runner_singleton_check.md`.

### 3j. OOM pre-check gate (6GB ceiling)

O(N²) matrix ops at large N must pass a 6GB GPU/RAM ceiling check BEFORE ship. exp_dev computes peak memory analytically (e.g. `8 * N^2` bytes for a float64 N×N) and BLOCKS the ship if predicted peak > 6 GB without explicit `--allow-large-mem` justification. Multiple O(N²) OOM crashes on 2026-05-27 triggered this.

### 3k. Import-chain coverage in smoke

Smoke runs MUST exercise the same `from experiments.X import ...` chain that FULL will use — no smoke-only stub imports, no try/except-swallow on the import line. Several FULL runs on 2026-05-27 passed smoke and then ImportError'd in production because smoke shimmed an import. Smoke is a production-codepath audit, not just a numerical sanity check.

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
  pattern="EVENT (silent_idle|gpu_idle|cpu_idle|gpu_queue_low|cpu_queue_low|ship_unconfirmed|for_you_stale|research_overdue|verdict_landed|bridge_cache_stale|routing_ratio_low|duplicate_runner_detected|duplicate_watchdog_detected)"
)
```

**Thirteen watchdog event kinds and mandatory orchestrator response:**

| Event | Trigger condition | Cooldown | Orchestrator mandatory response |
|---|---|---|---|
| `silent_idle` | Both GPU+CPU queues = 0 AND no in-flight dispatches AND no runner running for > 120s | 600s | Dispatch exp_dev for emergency refill (GATED on pause flag — if paused, write a `for_you` status_log entry instead explaining nothing is running). |
| `gpu_idle` | overnight_queue pending=0 AND GPU runner NOT running for > 120s (CPU state irrelevant) | 600s | Dispatch exp_dev to refill the GPU lane (GATED on pause flag). Fires independently of CPU — use this to catch GPU going empty while CPU is still busy. |
| `cpu_idle` | remote_cpu_queue pending=0 AND CPU runner NOT running for > 120s (GPU state irrelevant) | 600s | Dispatch exp_dev to refill the CPU lane (GATED on pause flag). Fires independently of GPU. |
| `gpu_queue_low` | overnight_queue pending <= 1 AND GPU runner IS running (proactive: fires BEFORE idle) | 600s (LOW); 300s (SEVERELY_LOW when pending=0) | Dispatch exp_dev refill PROACTIVELY — fires while ~30-60 min of work still in flight so the lane never goes idle. Payload includes `gpu_pending`, `threshold`. GATED on pause flag. |
| `cpu_queue_low` | remote_cpu_queue pending <= 1 AND CPU runner IS running (same logic as gpu_queue_low) | 600s (LOW); 300s (SEVERELY_LOW) | Same as gpu_queue_low for the CPU lane. |
| `ship_unconfirmed` | `queue_add.sh` returned success locally but the experiment name has not appeared in any queue/verdict/log within 60s | 300s (per name) | Investigate: check `data/recent_ship_attempts.jsonl` + run `python tools/orchestrator/state_check.py` + confirm queue status via dashboard. Re-ship if the experiment genuinely did not land. |
| `for_you_stale` | No status_log entry written in the past 30 min | 1800s | (A) Write a "still working on X" status_log entry for whatever the orchestrator has been doing, OR (B) if truly nothing is happening, dispatch a research drill so there is something to report, OR (C) if paused and idle, surface stale-state to the user in chat. At minimum, write a `heartbeat` status_log entry with plain_language so the For You tab does not go dark. |
| `research_overdue` | No `research_drill_closure` or `research_delivered` event in the past 24 h | 3600s | Dispatch the research sub-agent with `suggested_field` from the payload (or any cross-domain probe if `suggested_field` is empty). Per [[feedback-periodic-scope-expansion]] and auto-probe trigger B in Section 5b above. Always allowed — research is not pause-gated. |
| `verdict_landed` | A new verdict appears in the remote_state bridge cache (ended_at > last_seen_ts) | 0s per verdict (each fires once) | Dispatch verdict_handler with the verdict name from payload `{"name": ..., "verdict": ..., "ended_at": ..., "queue": ...}`. Gated on pause flag for exp_dev refill step inside verdict_handler. **Bootstrap fix:** on first watchdog start, `last_seen_ts = max(ended_at) - 1` so the newest verdict still fires once instead of being silently skipped. |
| `bridge_cache_stale` | Local `data/remote_state_cache_local.json` mtime > 90s (3x emitter cadence) | 600s | Verify both schtasks alive (`hd_remote_state_emitter` on remote, local heartbeat_watchdog with `pull_remote_state_cache`). Restart whichever is dead per `docs/bridge_recovery.md`. Bridge staleness blinds the whole agent stack — treat as HIGH-priority. |
| `routing_ratio_low` | `routing_ratio` < 0.75 over last 20 turns AND turn count >= 8 | 900s | (a) Re-read Section 2 above. (b) Route the NEXT event through its proper wrapper. (c) Write a `routing_ratio_correction` status_log entry acknowledging the drift. |
| `duplicate_runner_detected` | >1 real Python interpreter instance found on marsh@home whose commandline matches a runner kind (cpu_runner_0, gpu_runner_0, remote_state_emitter); venv shim launchers (~4 MB) are excluded | 900s per runner kind | Dispatch a focused dedup sub-agent to identify the non-leader instance(s) and terminate them (e.g. via SSH `taskkill /PID <pid>`). Payload contains `runner_kind`, `instance_count`, `pids`. Per [[feedback-runner-singleton-check]]. |
| `duplicate_watchdog_detected` | >1 local heartbeat_watchdog.py Python instance found on THIS machine | 900s | Kill all instances except the one with the highest PID (newest). The payload `pids` list + `own_pid` field shows which to keep. |

**Monitor note:** The Monitor armed on `dispatch.py` receives verdict / routing / queue_add events (from the repo file-system poller). The Monitor armed on `heartbeat_watchdog.py` receives the thirteen structural-health events above. Both should be armed simultaneously; they share the same `EVENT <kind>` format and the orchestrator reads from whichever fires first.

---

## 5. SKILLS REGISTRY

**Updated 2026-05-24: 7 subagent types.** All 7 core patterns now have subagent type definitions at `C:\Users\marsh\.claude\agents\<name>.md`. The full contract (pause gate, self-discovery, autonomy, hard constraints, return format) lives in the subagent system prompt. Orchestrator job per dispatch: `Agent({subagent_type: "<name>", description: "<name>: <args>", prompt: "<args>"})` — ONE call, args only.

**PROT-014 OBSOLETE (clarified 2026-05-27):** Earlier guidance suggested that custom subagent_types might not register reliably. This is FALSE in the current harness. All 7 of `exp_dev`, `research`, `verdict_handler`, `strategy_scribe`, `memory_curator`, `meta_audit`, `routing_handler` are addressable via `Agent(subagent_type=...)` without session restart. The Skill tool is a discovery shortcut to the same Agent call. Prefer either; both work.

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

## 5c. ENFORCED SHIP-TIME PROTOCOLS (PROT-018 + singleton + timeout)

These three rules became **structurally enforced** on 2026-05-27 (not advisory). Each one was conversationally violated 3+ times before enforcement landed. They are documented here so the orchestrator knows what queue_add.py / runner launchers / exp_dev will reject and why.

### PROT-018 — anchor-name `_n<N>` binding contract

The `_n<NUMBER>` suffix in an anchor name (e.g. `bid_v2_n8192_5seed_FULL`) is a HARD CONTRACT — the script's PRODUCTION N must equal that number.

- **exp_dev pre-ship check:** `grep -E "(N\s*=|n\s*=)\s*<SUFFIX_N>"` against the script. If no match, BLOCK.
- **queue_add.py exit-6:** ship-time validator rejects mismatches before smoke even runs.
- **`_v<N>` is version, not N-binding** — only `_n<NUMBER>` triggers the rule.
- 60+ label-vs-honest catches accumulated on 2026-05-27 before enforcement landed; smoke configs leaked into FULL-run paths, producing unfalsifiable evidence.
- Memory: `feedback_no_label_vs_honest_anchor_names.md`.

### Runner singleton lock (PID-file)

Before any `start /BELOWNORMAL python ...` or `schtasks /Run` for cpu_runner_0 / gpu_runner_0 / remote_state_emitter / heartbeat_watchdog:

- `runner_v2_prod.py --singleton-pid-file <path>` accepts the flag; launchers pass it.
- New launches abort cleanly if PID file shows an alive process.
- Watchdog `duplicate_runner_detected` / `duplicate_watchdog_detected` events fire when N>1 instance is found.
- 3 runner-duplication incidents on 2026-05-27 forced this fix. Duplicates compete for queue items and write conflicting heartbeats.
- Memory: `feedback_runner_singleton_check.md`.

### Per-experiment `--timeout` (required, no silent default)

`queue_add.py` now REQUIRES `--timeout <seconds>` (the silent 7200s default is removed).

Formula exp_dev uses at ship time:

```
timeout = ceil(1.5 * smoke_wall_s * (FULL_N / smoke_N)^exp * (FULL_seeds / smoke_seeds))
```

with `exp ∈ {1.0, 1.5, 2.0}` (default 1.5 if scaling unknown). Timeouts > 14400s are blocked pre-ship pending review — surface to orchestrator.

Forced by multiple TIMEOUT failures on 2026-05-27 (Bet I depth_polylog v3/v4 + hysteresis variants).

Memory: `feedback_per_experiment_timeout_required.md`.

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

## 6. BRIDGE ARCHITECTURE (canonical reference)

The remote-state bridge replaced per-call SSH for state reads on 2026-05-27. SSH is now reserved for WRITES (queue_add, runner control, file deploys). State READS go through a 30s-cached JSON file.

**Components:**
- **Remote emitter**: `tools/orchestrator/remote_state_emitter.py` running on marsh@home via schtask `hd_remote_state_emitter` ONLOGON. Writes `C:/dev/hd-instrument/data/remote_state_cache.json` every 30s.
- **Local puller**: integrated into `heartbeat_watchdog.py` via `pull_remote_state_cache()` — SCP fetch every 30s into `data/remote_state_cache_local.json`.
- **API**: `tools/orchestrator/remote_state.py` — 6 functions:
  - `get_queue_state()`
  - `get_runner_state()`
  - `get_recent_verdicts()`
  - `is_stale()`
  - `snapshot_ts()`
  - `queue_pending_count()`

**Performance:** 0.5ms cache read vs 600-2000ms SSH = **1161× speedup**. Latency budget for state_check.py / dashboard / watchdog dropped from seconds to milliseconds.

**Recovery:** `docs/bridge_recovery.md` documents how to restart both sides after either machine reboots. Both ends use schtasks ONLOGON triggers so reboot survival is automatic; manual recovery only needed if a schtask is disabled or the emitter crashes mid-cycle.

**Atomic heartbeat write:** `.tmp + os.replace` semantics on the cache file; dashboard tolerates parse failure (last-good fallback) so a torn read during emitter write doesn't blank the UI.

**Dashboard runner-grouping:** venv-shim PID + interpreter PID pairs are grouped as ONE logical runner instance. Child experiments are labeled as such (not as duplicate runners) so `duplicate_runner_detected` doesn't false-fire during a normal experiment launch.

**Watchdog interaction:** `bridge_cache_stale` event (Section 4b) fires when the local cache file mtime > 90s (3× emitter cadence). Treat as HIGH priority — staleness blinds the whole agent stack.

Memory: `feedback_remote_bridge_architecture.md`.

---

## 7. CAP_MAP SNAPSHOT AT COMPACTION HANDOFF (2026-05-27 v235)

Cap_map at **v235** (commit bb0ecd9 or successor pushed). Read `notes/capability_map.md` for the full row-by-row state; this section captures the strategic shape.

**DELTA from prior brief (v233 → v235):** Portfolio 14+14 → 14+18. Spectral-graph demoted 🟢→🟡. Large-deviations CLOSED-NEGATIVE. Bet B 4-stage NEW row 🟢-smoke-only. Framework reliability specific-documented revised down 48-58% → 45-55%. 77 cumulative label-vs-honest catches (was 70+ at v233). 4 verdicts unprocessed at compaction time (see below).

### Substrate-class confirmations (today)

- **SKAH-M class CONFIRMED at v228**: substrate IS the documented gated-multistable AM / lR-phase class (P=0.48 modal). 6-cell positive-identifier battery HARD_PASS at N=8192, 5-seed. 15+ static-phase rejections preceded. Three lit threads converge:
  - Non-reciprocal Hopfield (arxiv 2501.00983)
  - Spatial-correlated DAM (arxiv 2207.05218)
  - Saddle-hierarchy DAM (arxiv 2508.19151)
  - Substrate is a hybrid match. Memory: `project_substrate_skahm_class_confirmed_2026-05-27.md`.

- **Non-equilibrium-stat-mech framework class** (v229 row): BID v2 HARD_PASS at FULL N=1024-8192, 5-seed (sigma_margin=7.54 OUTSIDE all Hopfield static bands). Surviving frameworks: Crooks, Sagawa-Ueda, drift-diffusion-BP, free-probability. Static-phase drills PARKED as class. Memory: `project_substrate_non_eq_stat_mech_class_2026-05-27.md`.

- **Plural-framework lock** (3rd independent confirmation): Saad-Solla saddle-cascade + 1-RSB hysteresis (🟡) + MoE SHIFT are INDEPENDENT phase observations. NOT unified by SVD-cascade -- that was decisively rejected at v219+v224.

### Bet states

- **Bet B retention 4-tier shift-class taxonomy FINAL LOCK** (silhouette=0.788).
- **Bet B 4-stage compositional CL: NEW 🟢-smoke-only row** (v234). retention_A=0.848 / ret_B=0.905 / ret_C=0.874 at N=1024 smoke (pre-PROT-018 ship; labeled N=8192). FIRST 4-stage compositional CL evidence. FULL N=8192 multi-seed REQUIRED. If FULL confirms ret_A >= 0.80, promotes to Tier-1 demonstrated -- product-spec advance. Memory: `project_bet_b_4stage_smoke_pass_2026-05-27.md`.
- **Bet N STRONG_PARTIAL**: atom-genericity confirmed; EN/PY gap=0.0014.
- **Bet I MoE rebuild engineering-rate-limited** at K=4/K=8: LSH gating entropy is the sole degradation source per K_perarm; cosine-dot + Hebbian-anchor learned-router rescues BOTH HARD_FAILed.
- **Saad-Solla large-N FULL still genuinely open** -- 77th label-vs-honest catch in v234 (Saad-Solla v8_n2048 still ran at N=512; 6th attempt). PROT-018 now blocks new such catches. Memory: `project_pred4_hysteresis_first_order_confirmed_2026-05-27.md` for adjacent results.
- **Path-b feasibility revised 0.45 → 0.27**: corpus-size scaling HARD_FAIL; tau-limit + PPMI saturation are the bottleneck.
- **Spectral-graph DEMOTED 🟢→🟡** (v3 single-seed corr=-0.881 disconfirmed v2 multi-seed corr=+0.615; directional sign flip on replication).
- **Large-deviations substrate CLOSED-NEGATIVE** (gc_r2=0.040 HARD_FAIL).
- **Sagawa-Ueda deletion-cert** 🟢 continues building (v2 2/2 HARD_PASS); v3 FAILED 15:41 -- unprocessed at compaction.
- **Drift-diffusion-BP** v2 damp-formulation rescue in flight; v3 completed 15:45 -- unprocessed.
- **TCFT** still MIDDLE_BAND smoke; v4 completed 15:31 -- unprocessed.
- **Cellular-automata / tropical-geometry / quantum-error-correction**: NEW 🟡 sub-framing rows added.
- **Hatano-Sasha**: probed partial-negative (smoke single-seed sigma=0).
- **SKAH-M sub-class discriminator v2 weakens** lit-thread C (spatial-correlated DAM) per honest re-read.

### Unprocessed verdicts at compaction (handle first in next session)

1. tcft_fresh_erase_v4 -- completed 15:31 (3rd TCFT iteration; trend to evaluate)
2. sagawa_ueda_deletion_cert_v3 -- FAILED 15:41 (Sagawa-Ueda v3; compare to v2 2/2 HARD_PASS)
3. drift_diffusion_bp_v3 -- completed 15:45 (follow v2 damp-formulation rescue)
4. bid_order_parameter_v3_full -- FAILED 15:50

### False-alarm cluster (watchdog cooldown artifact)

wave14_saddle_solla_v7_n4096 and multiple older anchors (bid_v1, bid_v1_nsweep, etc.) continued firing ship_unconfirmed false-alarms via watchdog restart cycle. These are completed earlier-today anchors re-triggering the 61s threshold on watchdog restart. Not genuine unconfirmed ships.

### Framework reliability (split)

- General: 65-75% (UNCHANGED from v233)
- Specific-documented: 45-55% (MODEST DOWN from 48-58%; spectral-graph demotion offsets prior upward revision)
- Product-feature: 55-70% (UNCHANGED from v233)

### Portfolio

- **14 demonstrated + 18 evidence-strength rows** (was 14+14 at v233; +4 new sub-framing rows).
- **5 killer features design-ready**: deletion certificate / compositionality audit API / per-fact retention policy / live drift detection / edit-with-impact-prediction. Memory: `project_substrate_killer_features_2026-05-26.md`.
- **3 LLM-leapfrog product narratives**: Audit+Compliance / Operational Reliability / AI-data-sovereignty. Memory: `project_llm_leapfrog_directions_2026-05-26.md`.

### Label-vs-honest catch counter

77 cumulative catches as of v235. PROT-018 enforces at ship-time for NEW anchors. Pre-PROT-018 anchors continue completing as smoke-named-as-FULL throughout the day. **Next session sweep recommended**: identify queue items shipped before 10:00 on 2026-05-27 and re-design under PROT-018-compliant names or accept smoke-only status. Memory: `feedback_no_label_vs_honest_anchor_names.md`.

### Engineering posture

- **Product engineering DEFERRED** per user until full substrate characterization (non-eq framework drills still active).
- **Plumbing/SDK/dashboard is the rate-limiter**, not physics. Weight product-engineering work HIGHER than additional theoretical confirmation when characterization completes. Window: 24-36 months. Memory: `feedback_substrate_value_framing_2026-05-26.md`, `project_substrate_strategic_inversion_48h_2026-05-26.md`.

---

## 8. TODAY'S STRUCTURAL-PROCESS ADDITIONS (2026-05-27 consolidated index)

| Addition | Status | Where enforced |
|---|---|---|
| PROT-018 anchor-name N-suffix binding | LOCKED, unit-tested 10/10 | exp_dev pre-ship grep + queue_add.py exit-6; brief Section 3g |
| PROT-015 cold-start cap 2 calls | LOCKED | Section 10 cold-start sequence below |
| PROT-014 research-must-use-general-purpose | **OBSOLETED today** | All 7 custom subagent_types confirmed registered; Section 5 |
| Runner singleton PID-file lock | LOCKED | `--singleton-pid-file` flag + watchdog `duplicate_runner_detected` event; Section 3i |
| Per-experiment `--timeout` REQUIRED + formula | LOCKED | queue_add.py rejects missing flag; >14400s blocked; Section 3h |
| OOM pre-check gate (6GB ceiling) | LOCKED | exp_dev computes peak analytically + BLOCKs without `--allow-large-mem`; Section 3j |
| Import-chain coverage in smoke | LOCKED | smoke uses same `from experiments.X import ...` as FULL; Section 3k |
| 13-event watchdog set | LOCKED | `heartbeat_watchdog.py` (5 new: gpu_idle, cpu_idle, gpu_queue_low, cpu_queue_low, duplicate_watchdog_detected; 8 carried forward); Section 4b. Memory: `feedback_watchdog_full_event_set.md`. |
| Bridge architecture (1161× SSH reduction; 30s TTL) | LOCKED | Section 6. Memory: `feedback_remote_bridge_architecture.md` |
| Heartbeat atomic write | LOCKED | `.tmp + os.replace` in emitter; Section 6 |
| Dashboard runner-grouping | LOCKED | venv-shim+interpreter pairs grouped; child experiments labeled; Section 6 |
| Memory_curator wrote 7 new memories today | DONE | 3 project + 4 feedback in `C:\Users\marsh\.claude\projects\d--AI\memory\` — see MEMORY.md index |

The 7 new memories today (slugs):
- `project_substrate_skahm_class_confirmed_2026-05-27.md`
- `project_substrate_non_eq_stat_mech_class_2026-05-27.md`
- `project_pred4_hysteresis_first_order_confirmed_2026-05-27.md`
- `feedback_no_label_vs_honest_anchor_names.md`
- `feedback_runner_singleton_check.md`
- `feedback_per_experiment_timeout_required.md`
- `feedback_remote_bridge_architecture.md`
- `feedback_watchdog_full_event_set.md`

(8 files; original count "7" reflects the major lock-ins — `feedback_watchdog_full_event_set.md` is bundled with the 13-event watchdog rollout.)

---

## 9. MEMORY FILES FOR FURTHER READING

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

## 10. WHAT TO DO RIGHT NOW (cold-start procedure, PROT-015 cap = 2 calls)

PROT-015 caps cold-start at TWO main-thread tool calls before dispatching for any further exploration. The two slots are:

1. **Call 1 — Read this brief** (the file you are reading now).
2. **Call 2 — `python tools/orchestrator/state_check.py`** (consolidates pause state + queue state + recent verdicts + runner heartbeats + cap_map version in one Bash call).

Anything else — reading active_protocols, strategy_decisions, meta_audit tails, memory files — goes through the **state-check sub-agent** or a memory_curator dispatch. No additional Reads from main thread.

**After the two cold-start calls, arm the Monitor:**

```
Monitor(
  command="python tools/orchestrator/heartbeat_watchdog.py",
  pattern="EVENT (silent_idle|gpu_idle|cpu_idle|gpu_queue_low|cpu_queue_low|ship_unconfirmed|for_you_stale|research_overdue|verdict_landed|bridge_cache_stale|routing_ratio_low|duplicate_runner_detected|duplicate_watchdog_detected)"
)
```

This arming is permitted as the 2nd-call slot's continuation (PROT-015 allows the Monitor arm as part of cold-start setup, not a separate exploratory call).

**Then surface state to user:**
- If PAUSED, first response: "Pause flag is set ([reason from flag file line 1]). Doing structural / observation work only. Run /orchestrator-resume-experiments to enable exp_dev dispatches."
- If ACTIVE, first response: "Orchestrator READY. Cap_map v<N>; <queue depths>; <recent verdict tail>; <last-strategy-bump>."
- Write a `cold_start` status_log entry with plain_language + importance=MEDIUM.

**If user then explicitly authorizes resume**, invoke the `/orchestrator-resume-experiments` skill — do NOT `rm` the flag manually from Bash. The skill wraps flag-clear + log_event in one atomic action. Manual `rm` is a [[feedback-lock-in-inefficiency-fixes]] violation.

Do NOT dispatch experiment-shipping sub-agents until call 2 confirms ACTIVE.
