# exp_dev hand-off — research: hierarchical planning REVIVAL (state-conditioned + disjoint-block)

**Filed by:** research (Opus 4.7-1M)
**Date:** 2026-06-28
**Trigger:** research drill 2x revival post-v1 HARD_FAIL. See `notes/research_drill_2x_hierarchical_planning_REVIVAL_2026-06-28.md` for full mechanism + brain grounding + falsifiable predictions.

**Pause state:** check `data/orchestrator_paused.flag` before dispatch. If present, hold; resume on USER unpause directive.

**Per [[feedback-no-experiment-design-in-prompts]]:** this is a hand-off with anchor candidates + context pointers, not an experiment design directive. exp_dev owns the cell-author spawn + smoke + dispatch decisions. The research note provides mechanism, falsifiable predictions, and pre-registered thresholds; exp_dev decides smoke regime, full dispatch, and cell-author bundle.

---

## Anchor candidates (rank-ordered)

### ANCHOR 1 (RANK 1; P_deflated = 0.42; READY): `substrate_hierarchical_planner_state_conditioned_disjoint_v1`

- **Anchor pointer:** `data/exp_substrate_hierarchical_planner_state_conditioned_disjoint_v1/metrics.json` (anchor file path; cell does not yet exist)
- **Substrate-product reading:** M3 load-bearing piece #5 (USER concern of 10 for M3 glass-box conversational AI). Hierarchical goal decomposition is the bridge from Q&A to multi-step plan-toward-outcome. v1 HARD_FAIL means substrate currently cannot do this; ANCHOR 1 attempts the smallest-delta revival via state-conditioned macro vocabulary + disjoint-block per-level capacity reservation.
- **Tier hint:** chain-grade-eligible. If HARD_PASS, lifts to chain-grade (composes 4 existing CG primitives + 1 NEW state-conditioned codebook operation; brain-grounded; falsifiable; clean ablation structure).
- **Why now:** v1 HARD_FAIL diagnosis (closed-form pseudoinverse averages parallel-block effects into mush) is well-localized. State-conditioning fix is the smallest mechanism change that addresses the bug. 6-arm discriminator structure isolates state-conditioning vs disjoint-block contributions individually. Compute is cheap (~15-30min remote_cpu smoke; ~1-2hr full).

### ANCHOR 2 (RANK 2; P_deflated = 0.30; HARD_FAIL pivot): `substrate_hierarchical_planner_smdp_options_v1`

- **Anchor pointer:** `data/exp_substrate_hierarchical_planner_smdp_options_v1/metrics.json`
- **Substrate-product reading:** alternative planner algorithm class (Sutton-Precup options framework + SMDP planning) for M3 hierarchical planning. Different attack vector — no closed-form state-prediction, instead Q-via-cleanup.
- **Tier hint:** novel-composition (substrate has no options-framework precedent). Deflated harder; ship only as ANCHOR 1 HARD_FAIL pivot if state-conditioning + disjoint-block STILL fail.
- **Why now:** if mechanism class (closed-form D-prediction tree) is fundamentally wrong at substrate's regime, options framework is the natural alternative. Sutton-Precup 1999 is canonical RL framework; brain-grounded (basal ganglia option selection); substrate has all parts (multi-hop CG, partition routing CG, refuse_gate CG).

### ANCHOR 3 (RANK 3; P_deflated = 0.25; HARD_FAIL pivot OR HP follow-up): `substrate_hierarchical_planner_deep_composite_4block_v1`

- **Anchor pointer:** `data/exp_substrate_hierarchical_planner_deep_composite_4block_v1/metrics.json`
- **Substrate-product reading:** tests USER's "substrate plans all day" claim at composite depth-12+. Either ANCHOR 1 HP follow-up (extends mechanism to deeper regime) OR ANCHOR 1 HARD_FAIL pivot if "tree-tied-with-flat" verdict (depth-6 too shallow for hierarchy to matter).
- **Tier hint:** depends on ANCHOR 1 outcome. If ANCHOR 1 HARD_PASS, ANCHOR 3 is chain-grade-eligible extension. If ANCHOR 1 HARD_FAILs via tree-tied-flat, ANCHOR 3 is a regime test (different domain class question).
- **Why now:** defer until ANCHOR 1 lands.

---

## Context pointers (file paths, not summaries)

**Mechanism + falsifiable predictions:**
- `notes/research_drill_2x_hierarchical_planning_REVIVAL_2026-06-28.md` — full research note (this drill output)

**v1 HARD_FAIL (the post-mortem this revival addresses):**
- `data/exp_substrate_hierarchical_subgoal_planner_v1_smoke/metrics.json` — HARD_FAIL: RAIL=1.000 RAND=0.000 FLAT_K64_D8=0.133 TREE_3LVL=0.000 NO_CLEAN=0.000; cell-author honest diagnosis in `verdict_msg`
- `data/exp_substrate_hierarchical_subgoal_planner_v1_selftest/metrics.json` — SELFTEST_OK (implementation correct; mechanism wrong)
- `preregs/2026-06-27_substrate_hierarchical_subgoal_planner_v1.md` — v1 pre-reg

**Original drill (v1 design):**
- `notes/research_drill_2x_hierarchical_goal_planning_primitive_stage3_2026-06-27.md` — v1 research note (5-arm cell design)
- `notes/exp_dev_handoff_research_hierarchical_goal_planning_primitive_stage3_2026-06-27.md` — v1 hand-off

**Substrate primitives composed:**
- `hdlab/binding.py` — HRR bind/unbind (Plate 1995)
- `hdlab/multi_hop.py` — `iter_cleanup_chain` (chain-grade depth-15)
- `hdlab/ultrametric_clustering.py` — for state_class assignment (chain-grade)
- `hdlab/partition_routing.py` (or hdlab/store.py partition operations) — for disjoint-block partition (chain-grade M=10M)
- `hdlab/refuse_gate.py` — V_REL=256 refuse threshold (chain-grade)
- Flat preplay primitive (cells/substrate_preplay_beam_to_goal_v1*) — MIDDLE_BAND baseline for ARM_FLAT_PREPLAY_K128

**META rail + cross-cell rail:**
- META_M7 REPRODUCE_PV2 5HOP @ 2000 bindings, band [0.08, 0.25] — mandatory

**Cross-thread coupling (other today's drills):**
- `notes/research_drill_2x_hypothesis_generation_primitive_stage3_2026-06-27.md` — SWR preplay drill; leaf-level upgrade option if ANCHOR 1 HP
- `notes/research_drill_2x_online_learning_conversation_primitive_stage3_2026-06-27.md` — task_vector_kshot HP; state-class encoding initialization option
- `data/exp_cortex_hippo_handoff_v1/metrics.json` — yesterday's CG; hippo/cortex split natural mapping for state-class codebook

---

## Pre-registered thresholds (from research note section c — locked at dispatch)

**HARD_PASS_CHAIN_GRADE:**
- ARM_TREE_STATE_CONDITIONED solve_rate ≥ 0.60 (composite goals; depth ≥ 4 optimal)
- ARM_TREE_STATE_CONDITIONED − ARM_FLAT_PREPLAY_K128_D6 ≥ +0.20
- ARM_TREE_STATE_CONDITIONED − ARM_TREE_NO_STATE_COND ≥ +0.40 (state-conditioning load-bearing)
- median plan-length ≤ 2.0 × optimal
- cv ≤ 0.15 across 3 seeds [7, 17, 23]
- META_M7 PASS
- CARDINALITY_OK (6 arms × 3 seeds × 50 goals = 900 units)
- SANITY: ARM_FLAT_PREPLAY off-floor (≥ 0.20) — otherwise retune regime

**HARD_PASS_PARTIAL (MIDDLE_BAND):**
- ARM_TREE_STATE_CONDITIONED in [0.40, 0.60) AND lift over flat ≥ +0.15 AND state-cond lift ≥ +0.25

**HARD_FAIL:**
- ARM_TREE_STATE_CONDITIONED ≤ 0.30 → pivot to ANCHOR 2 (Sutton-Precup SMDP)
- ARM_TREE_STATE_CONDITIONED within 0.05 of ARM_TREE_NO_STATE_COND → pivot to ANCHOR 3 (deeper composite depth)
- ARM_TREE_STATE_CONDITIONED within 0.05 of ARM_FLAT_PREPLAY_K128 → pivot to ANCHOR 3 (depth-12+)
- SANITY_BREACH ARM_RANDOM > 0.10 OR ARM_FLAT > 0.60 → domain regime wrong; redesign

---

## Contract section

- **exp_dev decides:** smoke regime, cell-author bundle assignment, smoke seeds, dispatch queue (recommend remote_cpu_queue for ~15-30min smoke; cell is CPU-bound matmul + cosine + cleanup; no GPU op needed per Fix #24 GPU-must-actually-use-GPU)
- **research delivered:** mechanism (state-conditioned macro vocabulary + disjoint-block partition + 4-block options-vocab domain), pre-registered HARD_PASS/HARD_FAIL thresholds, brain grounding (basal ganglia parallel loops + Frank state-conditional selection), falsifiable predictions per arm, compute formulas in code
- **Skunkworks owns:** cert classification post-smoke; verdict reading per Fix #28 (read metrics.json per-arm not verdict_msg framings)
- **Director (Orchestrator) owns:** cap_map bump, status_log entry, downstream queue routing
- **Pre-dispatch verify-the-referent (Fix #26):** `tools/predispatch_check.py substrate_hierarchical_planner_state_conditioned_disjoint_v1` to confirm no prior chain-grade evidence and no recent re-dispatch
- **Per Fix #21:** poll filesystem for ANCHOR 1 landing via `find data -maxdepth 2 -name metrics.json -mmin -N`; do not rely on spawn notification

---

## Autonomy declaration

This hand-off carries the research drill's mechanism + falsifiable predictions + brain grounding + pre-registered thresholds. exp_dev autonomously decides:
- which anchor to dispatch first (recommend ANCHOR 1 standalone per Sequencing recommendation in research note section c)
- smoke regime parameters (recommend full N=8192 at composite depth-6 per discriminator-must-survive-scale)
- cell-author bundle (single-cell smoke; not bundled with other Stage-3 cells to keep diagnostic clean)
- queue routing (recommend remote_cpu_queue — CPU-bound; not GPU eligible)

If exp_dev's spawn budget is at the Fix #14 ≤3-in-flight ceiling, defer ANCHOR 1 until budget opens; do not bump higher-priority Stage-3 cells.

Honest discount applied per [[feedback-lit-scan-calibration-penalty]]: P=0.42 is post-deflation; raw mechanism prior was 0.55 (brain analog strong; substrate primitives 3/4 chain-grade); deflated -0.13 for state-conditioning novel-composition + v1-recency-penalty.

---

**End of hand-off.** Companion research note: `notes/research_drill_2x_hierarchical_planning_REVIVAL_2026-06-28.md`.
