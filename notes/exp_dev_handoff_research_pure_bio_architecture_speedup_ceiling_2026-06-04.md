# exp_dev hand-off -- research: pure biology architecture speedup ceiling 3x drill

**Filed-by:** research sub-agent
**Trigger:** d:/AI/hd-instrument/notes/research_drill_substrate_pure_biology_architecture_speedup_ceiling_3x_2026-06-04.md
**Date:** 2026-06-04

**Pause state block:** Check data/orchestrator_paused.flag before dispatching. If paused, hold.

Per [[feedback-no-experiment-design-in-prompts]]: this file provides TASK + WHY + CONTRACT + AUTONOMY only. exp_dev resolves anchor names, sweep grids, pre-reg thresholds, queue routing, and ETA independently.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (HIGHEST PRIORITY)
**Pointer:** One-shot Hebbian write vs gradient-descent baseline at matched retrieval accuracy
**Substrate-product reading:** The research note shows a ~10^5-10^7x per-pattern speedup algebraically (O(N^2) one-shot write vs O(T_gd * L * K * D^2) gradient descent). This is the foundational claim for the pure-bio mode product narrative. It must be empirically confirmed at N=2048 before any of the compound claims are taken seriously.
**Tier hint:** Tier 1 (CPU smoke; N=2048; compare Hebbian write vs small MLP gradient descent at matched M=50-200 patterns; 5 seeds; ~60s CPU per seed)
**Why-now:** This is the cheapest possible test of the most fundamental claim. A HARD-FAIL here (< 10^3x per-pattern speedup) would refute the entire bio-primitive composition premise.

Hard-pass band: per-pattern speedup > 10^5x at matched 90% retrieval accuracy over M=50-200 patterns.
Hard-fail band: per-pattern speedup < 10^3x.

### Anchor 2
**Pointer:** DG-class sparsity (f=0.005 + 20x expansion) vs dense baseline efficiency comparison
**Substrate-product reading:** Sub-question (2) predicts ~190x compound efficiency gain (sparse matmul + Tsodyks-Feigelman capacity gain, offset by expansion overhead). At f=0.005, retrieval quality must be maintained. This validates whether the Willshaw-Buckingham formula applies at substrate-class N.
**Tier hint:** Tier 1-2 (CPU; N=2048 native, expand to N_exp=40960; threshold to f=0.005; compare per-operation FLOPs and retrieval accuracy vs dense N=2048; 5 seeds)
**Why-now:** The DG sparse layer is the highest-complexity-per-gain primitive in the compound stack. If it fails (< 20x efficiency), the upper-bound compound estimate collapses by 2 orders of magnitude.

Hard-pass band: compound efficiency gain (accuracy / FLOPs) > 100x vs dense baseline.
Hard-fail band: < 20x.

### Anchor 3
**Pointer:** cf-RPE active gating -- write only on high-prediction-error samples, track accuracy at 10% coverage
**Substrate-product reading:** Sub-question (4) predicts 10-100x data efficiency from RPE-gated writes (write only when ||v - W*q||_F > tau_90th_percentile). The substrate already computes a residual as a byproduct of retrieval. Implementing the gate requires only a threshold check. If 10% data coverage reaches > 85% of full-training accuracy, the 10x data efficiency claim is confirmed.
**Tier hint:** Tier 1 (CPU; N=2048; gate writes at 90th percentile of residual distribution; 5 seeds; ~60s)
**Why-now:** This is a 5-20 line code change on the existing substrate. Extremely cheap to test; if it passes, it immediately becomes a production feature (online learning with surprise-gated writes).

Hard-pass band: gated-10% training reaches > 85% of full-training accuracy at matched M.
Hard-fail band: < 70% accuracy (gating throws away too much signal).

### Anchor 4 (COMPOUND VALIDATION)
**Pointer:** All three primitives combined: DG sparse + cf-RPE + 5-column ensemble vs dense single-column baseline
**Substrate-product reading:** Sub-question (7) predicts > 10^6x compound speedup when all primitives compose multiplicatively. This anchor tests the composition itself at small scale (5 columns, f=0.005, gating). If compound speedup is in the 10^3-10^6x range, the composition is partially multiplicative as predicted.
**Tier hint:** Tier 2 (CPU; N=2048; 5 columns parallel; DG sparse; RPE gate; 5 seeds; ~5 min total)
**Why-now:** Compound test is the decisive test for the product narrative. Per the research note, HARD-FAIL at < 100x compound speedup would indicate primitive interactions are mostly additive, which would reduce the product claim substantially.

Hard-pass band: compound speedup > 1000x vs dense single-column at matched accuracy.
Hard-fail band: < 100x (indicates additive not multiplicative composition).

---

## Context pointers

- Research note (full analysis, 27 citations): d:/AI/hd-instrument/notes/research_drill_substrate_pure_biology_architecture_speedup_ceiling_3x_2026-06-04.md
- Prior training-speed 2x drill (LLM-hybrid baseline 24x): d:/AI/hd-instrument/notes/research_drill_training_speed_hierarchical_architecture_2x_2026-06-04.md
- cf-RPE rank-1 substrate drill (RPE mechanism): d:/AI/hd-instrument/notes/exp_dev_handoff_research_cf_rank1_substrate_rpe_2x_2026-06-04.md
- REM replay consolidation handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_rem_replay_consolidation_2026-06-04.md
- Cap_map (one-shot learning / sparse coding rows): d:/AI/hd-instrument/data/cap_map.md

---

## Contract

exp_dev owns: anchor naming, sweep grid design, pre-reg threshold values, queue assignment, timeout formula, smoke/full sequencing.
Research note owns: algebraic prediction, hard-pass/hard-fail bands, lit citations, P_deflated values.
Orchestrator owns: cap_map updates post-verdict.

## Autonomy declaration

exp_dev has full autonomy to design the anchors from the algebraic predictions above. Do NOT copy numerical thresholds verbatim from this file into the experiment scripts -- re-derive from the formula (or use as a starting point and justify any deviation). Self-test formulas per [[feedback-strategy-spec-formula-selftests]] before coding. Prioritize CPU-only smoke designs; these are all Tier-1 or Tier-2 and should NOT require GPU or cloud resources.
