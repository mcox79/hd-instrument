## Exp Dev hand-off — v193 queue refill (>=3 anchors; remote CPU queue EMPTY)

**From**: Orchestrator inline cycle (2026-05-24, post-v193 cap_map commit)
**To**: Exp Dev (immediate pickup)
**Cap_map**: v193 (this cycle)
**Pause state**: ACTIVE (no pause flag)

## Why this hand-off exists

Per [[feedback-no-experiment-design-in-prompts]] — orchestrator main thread MUST NOT design experimental parameters (N, M, K, seeds, thresholds, queue, anchor names, formula details). The anchors below are pickup-ready: task SHAPE + WHY + CONTEXT POINTERS + CONTRACT + AUTONOMY DECLARATION. exp_dev decides all parameters.

Per [[feedback-pipeline-pacing]] — user reports remote CPU queue empty AND GPU queue=0 pending post-cycle. **Pipeline invariant is queue depth >= 1 at all times across runners.** This hand-off restores queue depth.

Per [[feedback-dispatch-wrappers-default]] — Agent dispatch unavailable in this runtime per orchestrator post-compaction brief Section 2; exp_dev sub-agent dispatches the next cycle. The orchestrator main thread does NOT design these inline.

## Priority order (locked by v193 cap_map state)

| # | Anchor | Priority | Default queue (exp_dev may revise per Tier A/B/C policy) | Base context |
|---|---|---|---|---|
| 1 | **R-PRIME-2 MoE M_c falsifier** | HIGH (returns to top with R-PRIME-3 killed v193) | overnight_queue (GPU; K-sweep multi-seed depth probe) | notes/research_R_PRIME_directions_2026-05-24.md (R-PRIME-2 spec); notes/orchestrator_prioritized_roadmap_2026-05-24.md (Ship 4 with R-PRIME-3 dead → Ship 1) |
| 2 | **Field-A reservoir-computing Lyapunov spectrum** | HIGH (carried from v192 Ship 2; cross-framework cadence) | remote_cpu_queue (CPU-suitable matrix-spectrum diagnostic) | notes/exp_dev_handoff_fieldA_reservoir_lyapunov_2026-05-24.md (full spec); notes/research_R_PRIME_directions_2026-05-24.md Field-A |
| 3 | **Bet D analyzer pass at K=32 / K=64** | MEDIUM (carried from v192 Ship 3; near-zero compute analyzer-only) | local_cpu_queue OR remote_cpu_queue (analyzer-only on existing checkpoints) | notes/orchestrator_prioritized_roadmap_2026-05-24.md (Ship 3); notes/research_existing_data_analyses_2026-05-24.md (R10 Gap(K) concave-saturating; 1-2 more K points enable AGS-scaling fit) |

**Optional anchors 4+ (also pickup-ready; exp_dev decides whether to ship this cycle or carry over)**:

| # | Anchor | Priority | Default queue | Base context |
|---|---|---|---|---|
| 4 | **F-6 Boolean re-ship with proper schema** | LOW (residual from v183 5-anchor hand-off; never shipped via correct schema) | remote_cpu_queue (KKL probe CPU-bound) | notes/exp_dev_handoff_5anchors_post_v183_2026-05-24.md anchor 3 |
| 5 | **MS_1ST_ORDER script-fix** (NOT a rerun) | LOW (residual from v183 anchor 6; script edit task) | local-dev (no queue) | notes/exp_dev_handoff_5anchors_post_v183_2026-05-24.md anchor 6 |
| 6 | **Bet M logarithmic-forgetting closed-form fit** (Bet M Allen-Cahn rescue R1) | LOW (carried from v192 Ship 5; zero-compute literature-anchor + closed-form fit on existing Bet B data) | local_cpu_queue (analyzer-only on existing t=1..21 data) | notes/orchestrator_prioritized_roadmap_2026-05-24.md (Ship 5); Wickelgren 1972 / Wixted-Ebbesen 1991 anchor |
| 7 | **R-PRIME-3 RESCUES** (Bet B retention rehab post-HARD-FAIL) | NEW v193 — 5 rescues filed inline at cap_map v193 | varies | cap_map v193 (R1 alt geometry metric / R2 sub-corpus geometry / R3 PAC-Bayes floor elevated / R4 cluster-structured 1-RSB basin-discrete / R5 abandon geometry) |
| 8 | **K2 mechanism-class rescues M1-M4** (K2 4-stage rehab axes exhausted) | NEW v193 — 4 rescues filed inline at cap_map v193 | varies (M1/M2/M4 likely GPU; M3 may be CPU) | cap_map v193 (M1 hierarchical replay / M2 attention-gated readout Bet X integration / M3 memory consolidation / M4 dim-scaling) |
| 9 | **K6 mechanism-class axes 2/3/4 elevated** (K6 dim-scaling axis 1 exhausted) | NEW v193 (carried from v190 4-axis list with axis 1 now consumed) | likely overnight_queue (compositional probes are seed-multi GPU) | cap_map v190 K6 4 rehab axes (axes 2 hierarchical pre-binding / 3 cleanup-iteration / 4 Bet X position-indexed) |

**Minimum ship target this cycle**: 3 anchors landed in queues (1 GPU + 1 remote CPU + 1 local/analyzer). exp_dev may ship more if smoke gates clear.

## WHY this batch

**R-PRIME-3 closure v193 reshapes priority order**: with task-pair-geometry HYPOTHESIS REJECTED, R-PRIME-2 (MoE M_c falsifier) returns to TOP priority — it was demoted to Ship 4 at v192 ONLY because R-PRIME-3 looked dominant; now that R-PRIME-3 is dead, R-PRIME-2 is the leading active R-PRIME falsifier (R-PRIME-1 PAC-Bayes floor is a Research drill not exp_dev; R-PRIME-3 dead; R-PRIME-5 SSM/HiPPO speculative; R-PRIME-6 Clifford/TN needs new diagnostic infra). R-PRIME-2 directly probes "implicit expert allocation" framing.

**Field-A reservoir Lyapunov** is the cross-framework cadence drill (per [[feedback-periodic-scope-expansion]]); v192 Ship 2 carry-over. Edge-of-chaos signature falsifies/confirms echo-state mapping with closed-form Memory-capacity payoff.

**Bet D analyzer K=32/K=64** is near-zero compute analyzer-only on existing checkpoints; extends R10 Gap(K) curve to enable AGS-scaling fit (Path 3 synergy v191).

**3 anchors + 6 optional** = clear ramp; exp_dev triages.

## CONTRACT (deliverable shape, ALL anchors)

- exp_dev decides: ALL design parameters (N, M, K, seed count, threshold bands, queue choice, ETA, anchor name).
- exp_dev decides: HARD-PASS / HARD-FAIL / MIDDLE bands per anchor; both bands MUST be falsifiable BEFORE running per [[feedback-no-smoke]].
- Pre-reg file in `preregs/` ahead of FULL run per anchor.
- Smoke first; FULL on smoke clearance.
- Multi-seed FULL minimum (>=5 seeds per anchor for which a seed-axis applies).
- Queue routing per Tier A/B/C policy in `tools/orchestrator/agents/exp_dev.md` Section 0 — exp_dev decides based on depth/compute/runtime profile NOT user-named-queue.
- Ship via `bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout>` for each anchor; queue_add.sh does its own REMOTE VERIFY (post-ship `Where-Object name -eq <NAME>` SSH check; FAIL: post-ship verification exits 5).

## AUTONOMY DECLARATION

You decide all design parameters for ALL anchors above: corpus pairs / K-grid / N / seed count / threshold bounds / queue placement / ETA / anchor name. Do NOT ship parameter grids designed in this hand-off — design them yourself. The cap_map v193 block + orchestrator_prioritized_roadmap + research_R_PRIME_directions are pointers — read them for context, do NOT copy parameter values verbatim.

## DISCIPLINE CITATIONS

- per [[feedback-no-experiment-design-in-prompts]]: this hand-off names task SHAPE not parameters
- per [[feedback-pipeline-pacing]]: fill CPU + GPU queue depth >= 1 at all times
- per [[feedback-rehabilitation-after-rejection]]: R-PRIME-3 has 5 rescues filed inline cap_map v193; K2 has 4 mechanism-class rescues M1-M4; K6 has axes 2/3/4 elevated
- per [[feedback-dont-overextend-theorems]]: R-PRIME-3 HARD-FAIL kills SPECIFIC metric NOT all geometry framings; R1 alt-metric + R2 sub-corpus preserve idea space
- per [[feedback-no-smoke]]: pre-reg both HARD-PASS + HARD-FAIL bands BEFORE running each anchor
- per [[feedback-verdict-msg-honest-reread]]: honest reread label=msg=data after FULL each anchor
- per [[feedback-ascii-only-in-scripts]] (OBSOLETED 2026-05-23): ASCII grep step no longer required; runner sets PYTHONIOENCODING=utf-8 + new scripts include `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` at top
- per [[feedback-negative-results-2x-research]]: R-PRIME-3 closure triggers 2x Research drill cadence (deferred to Research wrapper next cycle; orchestrator notes for follow-up)
- per [[feedback-lit-scan-calibration-penalty]]: Field-A reservoir-computing is uncharted regime for substrate; deflate P estimates by 0.15-0.25 in pre-reg

## Blockers

None. cap_map v193 already committed; pause flag ABSENT; runner state CPU ALIVE + remote CPU queue empty (refill target); queue_add.sh present and verified at tools/orchestrator/queue_add.sh.

---
BULK-ARCHIVED 2026-06-01: orchestrator-filed handoff to exp_dev; acted on (cap_map v312+ reflects evidence of completed work); bulk-archived per dashboard inbox-clearance Path A pattern.
