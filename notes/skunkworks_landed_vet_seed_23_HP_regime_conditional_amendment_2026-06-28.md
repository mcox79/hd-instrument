# Skunkworks landed-VET: 4-item HIGH-priority batch 2026-06-28 evening

ROLE: AUDIT-ONLY (Skunkworks sub-agent spawned by Research / Director).
DISCIPLINE: verify-OFF-DATA via fresh .venv python on metrics.json directly;
            NEVER from verdict-report alone. Honest-downward default classification.

## ITEM (1) TASK_VECTOR v1 FULL 3-seed atomization

VERDICT: MEASURED_MECHANISM (UNCHANGED). cert_delta = 0.
ATOMIZATION STATUS: ALREADY-ATOMIZED. Independent off-disk recompute MATCHES
prior atom exactly (avg_arms_diff: 0.246 / 0.276 / 0.216 per seed = cell-claimed values).

Prior atom (no new write required):
  math::T3/EXP_substrate_task_vector_K_cliff_phase_diagram_v1_FULL_CROSS_SEED_AGG_3_of_3_MEASURED_MECHANISM_K_cliff_CHARACTERIZED_in_V10_overlap_under_0p3_regime_ONLY_...

Off-disk verification (Skunkworks .venv python, 3 seeds, 63 phase-points each = 1890 obs):
  - cardinality 1890/1890 per seed (META_RULE_H pass)
  - cell-reported K_cliff_min=1 at (V=10, ov=0.6) is METRIC ARTIFACT:
    At (V=10, ov=0.6): K=1 TV=0.0 (all 3 seeds); K=3 TV=0.30/0.70/0.70 RECOVERS upward
    Non-monotonic; cliff metric collapsed low-K floor into "cliff"
  - REAL cliff characterized only in V<=10 / ov<=0.3 regime (monotonic K-cliff)
  - V>=200 / ov>=0.6: BIT-IDENTICAL ZERO across 3 seeds (substrate capacity ceiling)
  - arms-must-differ: TV > RV in 31-40 of 63 points; TV = RV in 22-32 of 63 (floor ties)

DISPOSITION: Prior HONEST_DOWNWARD MM classification is CORRECT. No revision needed.
NO NEW ATOM (would duplicate the existing MM atom).

## ITEM (2) PC v2p2 GPU dense cliff grid 3-seed chain-grade

VERDICT: chain-grade (UNCHANGED). cert_delta = 0 (already counted prior).
ATOMIZATION STATUS: ALREADY-ATOMIZED. Per-seed HP atoms + cross-seed AGG chain-grade
phase-characterization atom exist; covered in prior 4batch landed-VET.

Prior atoms (no new writes required):
  math::T3/EXP_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_{7,13,19}_GPU_HARD_PASS_LOCALIZED_CLIFF_180_of_180_...
  math::T3/EXP_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_CROSS_SEED_AGG_3_of_3_GPU_HARD_PASS_PHASE_CHARACTERIZATION_chain_grade_...

Off-disk verification (Skunkworks .venv python, sampled bracketing the cliff at N=2048):
  - cardinality 180/180 per seed (META_RULE_H pass)
  - real cliff bracketed at N=2048: TV at corruption=0.43-0.45 saturates at 1.0,
    drops to 0.132 at 0.48, 0.066 at 0.485, 0.01 at 0.49 (genuine cliff)
  - cliff_locator migrates with N: 0.47 -> 0.48 -> 0.485 -> 0.49 (N=2048->16384)
  - matches CRLB prediction: 0.461, 0.4725, 0.4805, 0.4862 (theoretically bounded)
  - arms_differ: substrate_hash vs random_hash distinct; random ~1/M=0.002 floor
  - backend=torch.cuda; device=cuda; gpu_util_estimate=0.95; gpu_mem peak 285.6MB
  - 3 seeds bit-stable on cliff_locator (zero variance on the cliff edge)

DISPOSITION: chain-grade phase-characterization STANDS. No revision.

## ITEM (3) exp_cortex_hippo_handoff_FULL_seed_23 SUB-AUDIT

VERDICT: REVISE-TO-REGIME-CONDITIONAL (high-stakes regime audit).
The CLS_handoff CLOSED-negative is NOT REOPENED.

ATOMIZATION STATUS: NEW ATOMS WRITTEN today:
  math::T3/EXP_cortex_hippo_handoff_FULL_seed_23_HARD_PASS_replay_consolidates_singleseed_MM_sub_capacity_regime_M_200_N_h_512_2026-06-28
  meta::T_methodology/META_RULE_cortex_hippo_handoff_CLS_capacity_floor_REGIME_CONDITIONAL_amendment_chain_grade_M_8192_HF_AND_sub_capacity_M_200_HP_jointly_characterize_Willshaw_sparse_DG_capacity_bound_2026-06-28

Off-disk verification + regime comparison:
                            | M=8192 chain-grade CLOSED-neg | M=200 FULL seed_23 (HP today)
  N_h                       | 4096                          | 512
  N_c                       | 8192                          | 8192
  M (items stored)          | 8192                          | 200
  alpha_simple = M/N_c      | 1.000                         | 0.024   (41x less)
  M / Willshaw_cap (sparse) | 227x OVER                     | 5.6x over (40x less)
  FULL recall_cortex        | 0.013-0.015 (3 seeds HF)      | 1.000 (HP)
  NO_REPLAY recall_cortex   | 0.000122                      | 0.005 (~1/200 floor)
  DIRECT recall_cortex      | 0.308-0.327 (also bounded)    | 1.000 (saturated)
  CAPACITY_WARN in metric   | n/a (chain-grade by design)   | EXPLICIT: alpha=0.024 < 0.05

THE KEY FINDING: regimes are RADICALLY different. seed_23 cell verdict_msg itself
contains "CAPACITY_WARN: alpha=0.024 < 0.05 -- consider raising M for chain-grade".
The HP at sub-capacity is EXPECTED per the capacity-floor mechanism the CLOSED-
negative characterized: substrate WORKS sub-capacity, FAILS over-capacity. This is
what a real capacity bound LOOKS like; not a contradiction.

WHY MM not chain-grade for seed_23: META_RULE_Q saturation_guard fires
(FULL=DIRECT=1.000 saturation; arm_dist_FULL_vs_DIRECT=0.000). At sub-capacity,
both arms saturate at ORACLE so FULL vs DIRECT collapses — but this is SATURATION-
ARTIFACT not the v1 W_hippo-bypass bug. v2 selftests passed remotely; NO_REPLAY=
0.005 distinct from 0.000 also rules out v1 bug. Cert capped at MM per by-
construction-saturation principle.

WHY NOT REOPENING the CLOSED-negative: the CLOSED-negative atom is correctly
scoped to "M=8192 with sparsity=0.10 N_h=4096". Its claim is precise at its
declared regime. The atom itself stands. The REVISION is to the JOINT M3-
JUSTIFICATION META-rule's narrative phrasing ("substrate cannot CONSOLIDATE...
at chain-grade M") which could be misread as protocol-wide. AMENDMENT makes
regime-conditionality explicit.

M3 ARCHITECTURAL CONCLUSION: UNCHANGED. Chain-grade scale requires high M;
external cortex layer remains load-bearing at chain-grade scale per
project_M3_architecture_needs_cortex_layer_above_substrate_USER_2026-06-28.

REVIVAL FLAGS for chain-grade demonstration (cert-owner FLAG only; not direction):
  (a) raise Willshaw cap: N_h=16384 + sparsity=0.05 -> cap~580; M=500 fits at alpha_W=0.86
  (b) M-staged consolidation protocol per CLOSED-negative redesign route (d)
  (c) iterative cleanup during replay per CLOSED-negative redesign route (c)
  (d) richer protocol (LLM cortex bridge per M3 phase-1 plan)

## ITEM (4) 3x HARD_FAIL_GPU_MANDATE_BREACH atomization

VERDICT: cert_ruling_dispatch_infra_failure (UNCHANGED). cert_delta = 0.
ATOMIZATION STATUS: ALREADY-ATOMIZED. Per-seed + cross-seed AGG infra-failure
atoms exist in math corpus.

Prior atoms (no new writes required):
  math::T3/EXP_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_{7,13,19}_DISPATCH_INFRA_FAILURE_HDLAB_QUEUE_env_var_unset_gpu_mandate_refusal_no_substrate_sweep_executed_elapsed_0p01s_2026-06-28
  math::T3/EXP_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_CROSS_SEED_AGG_3_of_3_DISPATCH_INFRA_FAILURE_NOT_substrate_hypothesis_test_outcome_v2p1_MM_stands_v2p3_recommended_with_HDLAB_QUEUE_set_2026-06-28

Off-disk verification: all 3 v2_rerun_2026-06-28 cells exited at phase=gpu_mandate_check
with elapsed_s=0.02, backend=torch.cpu, routed_queue='' (HDLAB_QUEUE env var not set
by runner). No substrate sweep ran. Pre-reg lines 129-137 explicitly required
HDLAB_QUEUE=local_cpu_queue dispensation; runner did not provide. Cell-author intent
matches gate behavior exactly. NOT a substrate negative result.

NOTE: the v2_rerun_2026-06-28 cells are DIFFERENT directory paths from the legitimate
_GPU evidence cells (item 2). Item 4 dir is `_v2_rerun_2026-06-28` (infra-fail); item 2
dir is `_GPU` (chain-grade HP evidence). Both atomized prior.

## SUMMARY

| Item | Disposition | CERT delta | Atomization status |
|------|-------------|-----------:|---------------------|
| (1) TASK_VECTOR v1 FULL 3-seed | MEASURED_MECHANISM (UNCHANGED) | 0 | ALREADY-ATOMIZED; off-disk recompute matches prior |
| (2) PC v2p2 GPU 3-seed         | chain-grade (UNCHANGED)        | 0 | ALREADY-ATOMIZED; per-seed + AGG exist |
| (3) cortex_hippo seed_23 FULL  | MM single-seed HP + REVISE-TO-REGIME-CONDITIONAL | 0 | NEW: 1 math atom + 1 meta META-rule amendment |
| (4) PC v2p2 v2_rerun 3x INFRA  | dispatch_infra_failure (UNCHANGED) | 0 | ALREADY-ATOMIZED; per-seed + AGG exist |

Total CERT delta this batch: 0.
CLS_handoff CLOSED-negative status: REVISED-to-regime-conditional (NOT reopened).
M3 architecture conclusion: UNCHANGED (external cortex layer load-bearing at chain-grade scale).

Verified off-disk: 9 metrics.json files; 4 prior atoms via grep on atoms.jsonl.

## Files written this turn (absolute paths)

NEW:
  d:/AI/hd-instrument/tools/atomize_cortex_hippo_handoff_FULL_seed_23_HP_regime_conditional_amendment_2026-06-28.py
  d:/AI/hd-instrument/notes/skunkworks_landed_vet_seed_23_HP_regime_conditional_amendment_2026-06-28.md (this file)

MODIFIED (via A5-gated atomic write + verify-load + integrity-check):
  d:/AI/hd-instrument/data/substrate_index/math/atoms.jsonl  (28722 -> 28723 lines)
  d:/AI/hd-instrument/data/substrate_index/meta/atoms.jsonl  (254   -> 255   lines)
  d:/AI/hd-instrument/data/substrate_index/meta/cert_ledger.jsonl (964 -> 966 lines)
