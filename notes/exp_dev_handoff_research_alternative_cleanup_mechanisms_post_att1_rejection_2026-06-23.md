# exp_dev hand-off — research: alternative cleanup mechanisms post att1 rejection

**Filed-by:** Research (Opus 4.7)
**Date:** 2026-06-23
**Trigger:** research note `d:/AI/hd-instrument/notes/research_alternative_cleanup_mechanisms_post_att1_rejection_2026-06-23.md`
**Pause state:** check `d:/AI/hd-instrument/data/orchestrator_paused.flag` before dispatch

Per [[feedback-no-experiment-design-in-prompts]]: this file points exp_dev at anchor candidates and contracts; exp_dev autonomously designs the cell.

---

## Anchor candidates (rank-ordered)

### Anchor 1: att1_v3_omp_sparse_coding_cleanup_v1 (PRIORITY)

- **Anchor pointer:** see research note section "CHEAP DECISIVE TEST (top candidate: OMP / sparse-coding cleanup)"
- **Substrate-product reading:** OMP gives substrate a structurally-different cleanup operator (residual-shrinkage vs argmax-similarity); if it works it unblocks n4/n9/n10/p1 across the board, gives k-sparse compositional decode for polysemous cues, gives explicit residual-norm as "phase margin" observable.
- **Tier hint:** smoke first; if smoke HARD_PASS (lift >= +0.05 at sigma=1.50 across all seeds), promote to full-3-seed; MEASURED_MECHANISM if full passes; chain-grade requires capacity sweep.
- **Why-now:** att1 v1+v2 rejected the iterative-attractor family; OMP is the structurally-orthogonal next mechanism to test. ~1hr total budget. Cleanup is a load-bearing META atom; cannot leave the substrate without a candidate path forward.
- **Pre-reg pointer:** thresholds in research note (HARD_PASS=+0.05 lift; HARD_FAIL=-0.005 lift OR conv frac<0.8; MIDDLE_BAND=(-0.005,+0.05))
- **Queue routing:** `local_cpu_queue` (N=512, M=200 sub-second per seed; pure matmul + LS-solve)

### Anchor 2: att1_v3_multi_bump_can_ensemble_cleanup_v1 (PARALLEL or IF #1 MIDDLE)

- **Anchor pointer:** see research note candidate #2 "Multi-bump CAN ensemble cleanup"
- **Substrate-product reading:** ensemble-over-K-init-conditions reduces noise-drift per multi-bump CAN literature (PLOS 2022; Frontiers 2025); reuses existing `hdlab/iterative_attractor.py` 90%; if works gives modest lift composable with #1.
- **Tier hint:** smoke + 3-seed full; HARD_PASS = lift >= +0.04 at sigma=1.50; HARD_FAIL = lift <= 0.000.
- **Why-now:** structurally complementary to #1; if #1 HARD_FAILS, #2 provides a different attack axis; if #1 HARD_PASSES, #2 is candidate-stacking experiment for ensemble lift over single-OMP.
- **Pre-reg pointer:** K_bump in {1, 4, 8}, sigma_init in {0.1, 0.3, 0.5}, sigmas=[1.0, 1.5, 2.0], seeds=[7,17,23]
- **Queue routing:** `local_cpu_queue`

### Anchor 3 (RESERVE; only if #1+#2 both HARD_FAIL): att1_v3_sdm_radius_readout_cleanup_v1

- **Substrate-product reading:** Kanerva radius-readout averages atoms in cosine-radius; substrate already has n11 RI ternary indices so partial composability.
- **Pre-reg pointer:** radius r in {0.6, 0.7, 0.75, 0.8}, sigmas=[1.0, 1.5, 2.0], 3 seeds
- **Tier hint:** P_deflated=0.35; expect MIDDLE_BAND or HARD_FAIL given averaging-destroys-signal risk at high noise.

---

## Context pointers (file paths; do not summarize)

- Research note: `d:/AI/hd-instrument/notes/research_alternative_cleanup_mechanisms_post_att1_rejection_2026-06-23.md`
- Prior att1 v1 (HARD_FAIL): `d:/AI/hd-instrument/data/exp_att1_iterative_attractor_cleanup_v1_smoke/metrics.json`
- Prior att1 v2 Krotov (HARD_FAIL): `d:/AI/hd-instrument/data/exp_att1_iterative_attractor_v2_low_storage_ratio_krotov_v1/metrics.json`
- Existing primitive (to deprecate-annotate, not delete): `d:/AI/hd-instrument/hdlab/iterative_attractor.py`
- Parent 2x revival drill: `d:/AI/hd-instrument/notes/research_2x_revival_overnight_negatives_2026-06-23.md`
- Brain-mechanism broad drill (mech 5 CAN family origin): `d:/AI/hd-instrument/notes/research_brain_mechanism_x_HD_broad_exploration_drill_2026-06-22.md`
- META atom (cleanup is load-bearing): `meta::META_codebook_NN_cleanup_is_load_bearing_for_substrate_*`

---

## Contract

- **Pre-flight gate:** sanity check `OMP_K1 ~ argmax` within +/- 0.01 (NOT mechanism rejection if violated -- implementation bug). Per [[feedback-verify-the-referent]].
- **Honest scope:** report best lift, all per-arm metrics (per [[feedback-fix28-verify-per-arm-metrics]]), per-seed CV.
- **Pre-reg fields:** HARD_PASS / HARD_FAIL / MIDDLE_BAND bands MUST be in the prereg file BEFORE dispatch per envelope-fail-bands.
- **Pause-gate:** check `data/orchestrator_paused.flag` before queue_add.
- **Cell-author smoke:** required before full dispatch (Fix #17).
- **Status_log entry:** required on cell-author dispatch.

## Autonomy declaration

exp_dev autonomously decides:
- Cell file name and exact implementation
- Arm parameter sweep details (within the ranges given in research note)
- Whether to ship #1 first, #1+#2 in parallel, or #1 then #2 sequentially based on queue capacity
- Whether to extract `omp_cleanup` to `hdlab/` as new primitive immediately or after HARD_PASS

Research does NOT prescribe code; only the mechanism class, pre-reg bands, and substrate-product reading.
