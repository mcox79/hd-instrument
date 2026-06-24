# exp_dev hand-off -- research: CL spectrum 3rd-angle (cross-biology + test-design audit)

**Filed-by:** research:opus_4_7_1m
**Trigger:** research_cl_spectrum_3rd_angle_cross_biology_2026-06-24.md (this drill)
**Pause state:** check data/orchestrator_paused.flag before dispatch.

Per [[feedback-no-experiment-design-in-prompts]] -- exp_dev decides cell design; research provides anchors and substrate-product reading only.

---

## Anchor candidates (rank-ordered)

### Anchor 1: `cl_crispr_append_only_v1` (HIGHEST priority)

**Substrate-product reading:** structural-commitment CL via append-only per-phase slabs of W. NO replay. NO shared substrate. By-construction-no-forgetting; bounded growth (J slabs).
**Tier hint:** chain-grade-eligible if HARD-PASSES at full alpha; novelty-ratio likely high (no comparable substrate cell uses J-slab structural commitment).
**Why now:** Angle 1 in flight on segregated-dual-W; Cell 1 tests the ORTHOGONAL hypothesis (full structural commitment vs CLS-style dual-store). Differentiation matters for product decision-tree.
**Pre-reg bands (research-recommended; exp_dev may adjust):**
- HARD-PASS: forgetting_p1 <= 0.10 AND transfer_final >= 0.70 AND slab-routing accuracy >= 0.90.
- HARD-FAIL: forgetting_p1 > 0.30 OR routing accuracy < 0.60.
- CHAIN-BONUS: forgetting_p1 <= 0.05 AND transfer >= 0.85.
**Estimated compute:** O(N^2/K * M * J) -- lower than spectrum baseline.
**Routing hint:** remote_cpu via hdi_orchestrator (numpy at N=4096 fits CPU per spectrum-cell precedent).

### Anchor 2: `cl_hox_combinatorial_subspace_v1` (SECOND priority)

**Substrate-product reading:** orthogonal-subspace allocation with combinatorial K-subset assignment per phase. By-construction-no-forgetting PLUS positive transfer between phases sharing a subspace.
**Tier hint:** chain-grade-eligible if HARD-PASSES AND constructive-transfer demonstrable.
**Why now:** Cell 2 tests whether substrate can show POSITIVE transfer (Cell 1 by design has zero transfer between phases). Distinguishes "memory product" (Cell 1) from "generalizable-CL product" (Cell 2).
**Pre-reg bands:**
- HARD-PASS: forgetting_p1 <= 0.10 AND transfer_final >= 0.70 AND constructive-transfer >= 0.30 on shared-subspace phase pairs.
- HARD-FAIL: forgetting_p1 > 0.40 OR constructive-transfer < 0.05.
**Estimated compute:** O(K*D*N*M*J) = O(N^2*M*J / K) -- comparable to spectrum.
**Routing hint:** remote_cpu.

### Anchor 3 (DEFERRED): `cl_stigmergic_context_v1` (MOVE A substrate-offload)

**Substrate-product reading:** shared decaying context vector coordinates cf-RPE and Hebbian INDIRECTLY (no direct interaction on W).
**Tier hint:** if Anchors 1+2 HARD_FAIL, this is the next-tier rescue.
**Why deferred:** mechanism more speculative; c-decay calibration adds hyperparameter; defer until structural-commitment family is characterized.
**P_deflated:** 0.40 (vs 0.55 / 0.45 for Anchors 1+2).

---

## Context pointers (file paths -- exp_dev reads, not me summarize)

- Current spectrum cell: `experiments/exp_substrate_continual_learning_spectrum_v1.py`
- Prereg: `preregs/2026-06-24_substrate_continual_learning_spectrum_v1.md`
- HARD_FAIL metrics: `data/exp_substrate_continual_learning_spectrum_v1/metrics.json`
- Angle 1 research: `notes/research_continual_learning_architectural_revival_2x_drill_2026-06-24.md`
- Angle 1 exp_dev hand-off: `notes/exp_dev_handoff_research_continual_learning_architectural_revival_2x_drill_2026-06-24.md`
- Angle 2 research: `notes/research_biology_cross_system_composition_strategies_2x_drill_2026-06-24.md`
- This drill full note: `notes/research_cl_spectrum_3rd_angle_cross_biology_2026-06-24.md`
- Relevant landed substrate cells (CRISPR-adjacent / structural-commitment-adjacent):
  - `experiments/exp_two_substrate_fastslow_cls_cpu_v1.py` (dual-substrate timescale split)
  - `experiments/exp_d2_1_dual_cls_cpu_v1.py` (dual-CLS)
  - `experiments/exp_hippocampal_nonrecip_replay_v1.py` (one-way replay)
  - `experiments/exp_substrate_K2_x_cfrpe_compose_LM_v1.py` (K-bank routing)

## Test-design fixes (apply to ANY CL cell)

Per L4 of the research note:

1. Add `--shared_structure_frac` knob (0.0 = IID-random current spectrum; 1.0 = full shared substructure; sweep [0.0, 0.5, 1.0]).
2. Report `transfer_pre_replay` AND `transfer_post_replay` separately; pre-reg HARD-PASS against transfer_pre_replay.
3. Add `ARM_DISCRETE_LOW_ALPHA` at M=80 (alpha=0.10) as true forgetting baseline.
4. Sweep RECENCY_WEIGHT in [0.25, 1.0, 4.0] OR justify a single bio-faithful value.

---

## Contract

- exp_dev OWNS cell design, hyperparameter choices, smoke-vs-full decisions, dispatch routing.
- research provides: anchor candidate, substrate-product reading, pre-reg HARD bands (recommendations), tier hint, context pointers.
- research does NOT specify: per-arm hyperparameters, code structure, RNG seeds, full timeout, queue-runner choice.

## Autonomy declaration

- exp_dev may pick fewer than 3 anchors; may pick a different anchor entirely; may add anchors not in this list.
- exp_dev may reorder priority based on dispatch budget / current queue depth / parallel cell load.
- exp_dev may bundle Anchors 1+2 into one cell with both arms if compute permits.
- exp_dev may decline all anchors if a higher-priority arrival supersedes (e.g., Angle 1's dual-W cell verdict landing).
