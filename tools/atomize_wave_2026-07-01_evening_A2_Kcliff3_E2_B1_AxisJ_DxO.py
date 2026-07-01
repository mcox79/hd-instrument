"""
A5-gated atomize wave: 2026-07-01 evening landings

INDEPENDENT OFF-DATA RECOMPUTE via .venv python on all 6 batches.

============================================================
BATCH A_v2 pc_sparsity_x_encoder_crossproduct_v2_n8192 3-seed HP -> CHAIN_GRADE
============================================================
Capacity-lift 2x-drill of Batch A v1 MM (2026-07-01 morning; ledger commit 7cef91b3).
V1 had 10/16 SAT (62.5%); v2 reduces to 7/16 SAT (43.75%) via lower N or higher M.

Off-data recompute (all 3 seeds):
  run_mode=full all 3; cardinality 16/16 all; positive control PASS all (0.732/0.742/0.733
    within [0.10, 0.95] non-sat band).
  tier_counts identical: SAT=7 HP=0 MB=5-6 FLOOR=0 HF=3-4 (3 HF cells = non-viable configs; honest floor).
  interaction_pairs_visible=4/6 all seeds.
  n_discriminating=5-6 all seeds.
  encoder_pair_distinct=6/6 all seeds.

Cross-seed CV of per_encoder_sparsity_range (the discriminator):
  binary_bipolar: [0.802, 0.812, 0.797] cv=0.0095
  hrr_real:       [0.320, 0.363, 0.338] cv=0.0638
  fhrr:           [0.227, 0.235, 0.218] cv=0.0368
  sparse_bipolar: [0.800, 0.815, 0.808] cv=0.0093
  ALL 4 ENCODERS cv << 0.15 CG threshold. 4/4 encoders with range >=0.15 (v1 had 1/4).

TIER: CHAIN_GRADE (pre_reg_pass).
  Per-cell verdict HP all 3 seeds; cross-seed cv on all 4 encoder axes < 0.10;
  positive control PASS non-saturated; sat_frac 43.75% (below 60% META_RULE_Q threshold);
  cardinality and distinctness clean.
  2x-drill of v1 MM successfully lifts to CG by reducing SAT-dominance.
  CERT +1.

============================================================
BATCH Kcliff_v3 extended-range 3-seed MB -> MEASURED_MECHANISM
============================================================
2x-drill of K-cliff v2 (2026-07-01 morning MM). v2 was SAT-dominant 60%;
v3 extends K range and escapes SAT to 12% but shifts axis into FLOOR-dominant 60%.

Off-data recompute (all 3 seeds):
  run_mode=full; cardinality 72/72 records + observed all seeds; elapsed 148-232s.
  tier_counts: n_SAT=[9,9,8] cv=0.067; n_MB=[7,8,8] cv=0.075; n_FLOOR=[42,43,43] cv=0.014;
    n_TRANSITION=[14,12,13] cv=0.077.
  K_cliffs=12/12 fire all seeds.
  avg_arms_diff cross-seed: [0.2365, 0.2361, 0.2361] cv=0.00102 (extraordinary).
  K_cliffs_per_combo exact-match 11/12 (1 disagreement: N16384_Q4 seed_7=1000, seed_13=1000,
    seed_19=500 -- boundary region).
  Phase-point all-3 same band: 66/72 (92%).

TIER: MEASURED_MECHANISM.
  Per-cell verdict MB all 3 seeds (author criterion; FLOOR-dominant now).
  Cross-seed cliff-location reproducibility is CG-quality (11/12 exact match; cv=0.001
  on avg_arms_diff) BUT per-cell verdict remains MB, and axis has now flipped from
  SAT-dominant to FLOOR-dominant -- still not free-discrimination regime.
  Complements Kcliff v2 MM: v2 characterized SAT-dominant regime; v3 characterizes
  FLOOR-dominant regime; the K-cliff mechanism itself is proven cross-seed to 11/12
  exact locations. CERT +0.

============================================================
BATCH E_v2 bytes_per_fact_pareto v2 3-seed HP -> MEASURED_MECHANISM
============================================================
V2 fixes sparse-CPU routing over v1. Author verdict HP all 3 seeds.

Off-data recompute (all 3 seeds):
  run_mode=full; cardinality 28/28 units all seeds; elapsed 78-79s.
  positive_control PASS all seeds (FP32 recall 1.0 all seeds).
  bfloat16_not_collapsed=True all seeds; int4_valid_tier=True all seeds.
  pareto_2x_separation_ok=True all seeds; monotone_decay_ok=True all seeds.
  monotone_ok_per_arm: all 7 arms True all seeds.
  mechanism_hashes_distinct=True all seeds.

Per-arm cross-seed identity check:
  20/28 cells identical across seeds (recall_mean bit-for-bit same); 8/28 differ.
  The 20 identical cells are at recall=1.0 ceiling (META_RULE_Q trip).
  The 8 differing cells are legitimate capacity-boundary variance:
    - FP16_DENSE at M in {1000, 4000, 10000, 20000}: recall=0.0 all seeds (BROKEN ARM;
      not measured; likely FP16 quantization failure at encoding level).
    - SPARSE_BIPOLAR_0p05 at M=4000: [0.805, 0.827, 0.822] cv=0.014 (real seed variance).
    - BINARY_DENSE M=20000: [0.9995, 0.9995, 0.9990] (near ceiling; seed-3 tiny drop).

TIER: MEASURED_MECHANISM.
  BFLOAT16 not-collapsed and INT4 valid_tier are REAL proven bounds. BINARY_DENSE
  works at low M. Pareto separations are true.
  BUT: 20/28 cells at recall=1.0 (71% saturation) trips META_RULE_Q; FP16_DENSE arm
  is broken (recall=0.0 across all M all seeds; not a Pareto point but noise from
  a broken quantization path). Cross-seed identity at ceiling is not chain-grade-
  quality free-discrimination; the discriminating cells are at capacity edge.
  The proven sub-mechanism: BFLOAT16 works at M=4000 (recall=1.0); INT4 works
  at M=4000 (recall=1.0); BINARY_DENSE degrades gracefully to 0.9995 at M=20000.
  CERT +0. Auditor over-rides author HP -> MM per META_RULE_Q + broken-arm.
  2x-DRILL RECOMMENDATION: fix FP16_DENSE encoding; re-run at M=20000-40000
  where BFLOAT16 + INT4 discriminate (recall < 1.0).

============================================================
BATCH B_v1 seqbind N_dim scaling law v1 3-seed HARD_FAIL (Gate D)
============================================================
Off-data (all 3 seeds):
  run_mode=full; elapsed 37s all; cardinality_ok=True all.
  All 3 seeds HARD_FAIL_POSITIVE_CONTROL_REGRESSION (Gate D):
    at N=8192, K_cliff observed = 500 (log2 = 8.966);
    CG-predicted center at N=8192 = 1000 (log2 = 9.966);
    |delta| = 1.000 vs tol 0.5 -> GATE D FAIL.

Per-seed substrate scaling fits:
  seed_7:  slope=0.83, r2=0.90 -- fit_ok=True
  seed_13: slope=1.13, r2=0.86 -- fit_ok=True
  seed_19: slope=0.70, r2=0.89 -- fit_ok=True
K_cliff by N (seed 7): {2048:200, 4096:200, 8192:500, 16384:1000}
K_cliff by N (seed 19): {2048:200, 4096:500, 8192:500, 16384:1000}
K_cliff by N (seed 13): {2048:200, 4096:200, 8192:500, 16384:2000}

TIER: HARD_FAIL (honest_negative CG-predicted-N-dim-scaling-invalid).
  Gate D fires clean all 3 seeds. RANDOM arm returns 0 at all N (positive control
  degenerate). The N-dim scaling relationship the pre-reg predicted is NOT
  observed at N=8192; K_cliff sits 1 log2 unit below the predicted center.
  Substrate scaling slope varies 0.70-1.13 across seeds (r2 ~0.86-0.90).
  CERT +0. Prior K_cliff atoms not superseded.
  2x-DRILL: revise CG-prediction formula OR test N grid outside 2048-16384.

============================================================
BATCH Axis J order_binding_family v1 (2/3 seed HF; seed_7 STILL RUNNING)
============================================================
seed_7 elapsed_s=0.15 (started but not completed; likely runner hang per infra note)
seed_13 + seed_19 both HARD_FAIL_ORDER_BINDING_INVARIANT:
  all 3 ops (CYCLIC_SHIFT / RANDOM_PERMUTATION / PHASE_ROTATION) have identical
  K* = 500 at N=8192; log10_sep_pairs all 0.000; n_ops_distinct_from_baseline=0.
  Mechanistic distinctness holds (3/3 bundle pairs distinct; 3/3 positions pairs
  distinct; mech hashes distinct) -- arms are genuinely different mechanisms
  but ALL PRODUCE IDENTICAL K*.
  positive_control PASS both seeds (CYCLIC_SHIFT K=50 top1=1.0 above 0.8 floor).
  tier_counts: SAT=3 MB=3 FLOOR=2 TRANSITION=1 (both seeds identical).
  max_cv per op: seed_13 0.7014 / seed_19 0.6961 (structural saturation noise).

TIER: HARD_FAIL (honest_negative order_binding_family_capability_invariant_at_WM_regime).
  Substantive substrate finding: 3 order-binding operations produce identical
  K* = 500 -- axis is capability-family-invariant at WM regime.
  2-seed replication with clean control + identical results = HF confirmed;
  seed_7 not needed to overturn (2/2 identical -> strong prior).
  CERT +0.
  NOTE: seed_7 marked RUNNING (elapsed 0.15s) -- possible runner hang per
  Testbed a57b9f19 note. Atom records 2-seed evidence; if seed_7 completes with
  divergent result, will supersede.

============================================================
BATCH DxO binding_op_x_capacity v1 seed_7 HARD_FAIL (single-seed)
============================================================
seed_7 FULL HF: HARD_FAIL_BINDING_OP_CAPACITY_INVARIANT.
  All 3 binding ops (HADAMARD_BIND / CIRCULAR_CONV_HRR / FHRR_COMPLEX_MUL)
  produce K_cliff=750 at alpha=0.5 -- identical.
  K_cliff_shift_from_ref = 0.0 for all 3 ops.
  BUT top1 at alpha=0.5 differs: HADAMARD 0.267, CIRCULAR 0.367, FHRR 0.867.
  Positive control PASS (HADAMARD alpha=0.1 M=150 top1=1.0 above 0.8 floor).
  Mechanistic distinctness: 3/3 pairs distinct; op_mech_hashes distinct.
  tier_counts: SAT=3 MB=2 FLOOR=1 TRANSITION=3.
  max_cv per op: HADAMARD 0.858 / CIRCULAR 0.695 / FHRR 0.366.

TIER: HARD_FAIL (honest_negative binding_op_capacity_axis_null_but_top1_differs).
  Composes with Axis J (order_binding_family HF): both binding-family axes
  are capability-family-invariant at WM regime (K_cliff / K* location does
  not depend on op choice). But: DxO shows top1 does differ meaningfully
  across ops (HAD 0.27 / CIR 0.37 / FHRR 0.87 at alpha=0.5) even though
  K_cliff is identical.
  This is a strong substantive finding: binding-op axis affects RECALL LEVEL
  but not CAPACITY LOCATION at WM regime. Single-seed atom for now; cross-seed
  replication recommended before promoting to MM.
  CERT +0.

============================================================
CUMULATIVE TIER TALLY THIS WAVE:
  1 CHAIN_GRADE (A_v2)           -> CERT +1
  2 MEASURED_MECHANISM (Kcliff_v3, E_v2) -> CERT +0
  3 HARD_FAIL (B_v1, Axis J, DxO)         -> CERT +0
  Total CERT delta = +1
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_landed_VET_wave_2026-07-01_evening"
ATOMIZED_DATE = "2026-07-01"

# ============================================================================
# BATCH A_v2: CHAIN_GRADE (CERT +1)
# ============================================================================
atom_A_v2_CG = {
    "id": (
        "T3/EXP_substrate_pc_sparsity_x_encoder_crossproduct_v2_n8192_3seed_CHAIN_GRADE_"
        "capacity_lift_2x_drill_of_v1_MM_SAT_frac_62p5_to_43p75_pct_all_4_encoders_range_"
        "ge_0p15_cv_binary_0p009_sparse_0p009_hrr_0p064_fhrr_0p037_2026-07-01"
    ),
    "name": (
        "CHAIN-GRADE PC sparsity x encoder crossproduct v2 N=8192 3-seed FULL: capacity-lift "
        "2x-drill of v1 MM lifts to CG. SAT_frac reduced 62.5%->43.75% (below META_RULE_Q "
        "threshold). All 4 encoders discriminate with per_encoder_sparsity_range >= 0.15 (v1 had "
        "only fhrr). Cross-seed CV extraordinarily tight: binary=0.009 / sparse=0.009 / fhrr=0.037 "
        "/ hrr=0.064 (all << 0.15 CG threshold). Positive control PASS non-saturated all 3 seeds "
        "(0.732/0.742/0.733 within [0.1, 0.95]). encoder_pair_distinct=6/6 all; cardinality 16/16 "
        "all; interaction_pairs_visible=4/6 all. Per-cell HP all 3 seeds. CERT +1."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "3-seed FULL PC sparsity x encoder crossproduct v2 at N=8192 with capacity-lift. "
        "OFF-DATA recompute (skunkworks 2026-07-01 evening): "
        "run_mode=full all 3; cardinality 16/16 all; tier_counts identical (SAT=7 HP=0 MB=5-6 "
        "FLOOR=0 HF=3-4; 3 HF cells are non-viable configs = honest floor); "
        "positive control PASS all seeds (target binary_bipolar s=0.25 top1_band [0.1, 0.95]; "
        "measured 0.732/0.742/0.733); interaction_pairs_visible=4/6 all seeds; "
        "n_discriminating=5-6 all seeds; encoder_pair_distinct=6/6 all seeds. "
        "Per_encoder_sparsity_range cross-seed: "
        "binary_bipolar [0.802, 0.812, 0.797] cv=0.0095; "
        "hrr_real [0.320, 0.363, 0.338] cv=0.0638; "
        "fhrr [0.227, 0.235, 0.218] cv=0.0368; "
        "sparse_bipolar [0.800, 0.815, 0.808] cv=0.0093. "
        "All 4 encoders with range >=0.15 (v1 had 1/4). SAT_frac=43.75% cross-seed identical "
        "(below META_RULE_Q 60% threshold). 2x-drill of v1 MM (2026-07-01 morning atom in "
        "commit 7cef91b3) successfully lifts to CG by escaping SAT-dominance. CERT +1."
    ),
    "metadata": {
        "provenance_quality": "CERT_CHAIN_GRADE",
        "verdict": "HARD_PASS",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python on 3 seeds metrics.json (remote pulled via SSH): "
            "run_mode=full all 3; cardinality 16/16 all; positive_control PASS non-sat all seeds "
            "(0.73-0.74); sat_frac=43.75% cross-seed identical; per_encoder_sparsity_range cv "
            "binary=0.009 sparse=0.009 hrr=0.064 fhrr=0.037 (all << 0.15 CG threshold); "
            "4/4 encoders with range >=0.15; encoder_pair_distinct=6/6 all seeds"
        ),
        "regime": {"N": 8192, "encoders": ["binary_bipolar","hrr_real","fhrr","sparse_bipolar"],
                   "sparsity_grid": [0.01, 0.05, 0.10, 0.25]},
        "per_seed_metrics_paths": {
            "seed_7":  "data/exp_substrate_pc_sparsity_x_encoder_crossproduct_v2_n8192_seed_7/metrics.json (remote pulled)",
            "seed_13": "data/exp_substrate_pc_sparsity_x_encoder_crossproduct_v2_n8192_seed_13/metrics.json (remote pulled)",
            "seed_19": "data/exp_substrate_pc_sparsity_x_encoder_crossproduct_v2_n8192_seed_19/metrics.json (remote pulled)",
        },
        "per_encoder_sparsity_range_cross_seed": {
            "binary_bipolar":  {"vals": [0.8017, 0.8117, 0.7967], "mean": 0.8034, "cv": 0.0095},
            "hrr_real":        {"vals": [0.3200, 0.3633, 0.3383], "mean": 0.3405, "cv": 0.0638},
            "fhrr":            {"vals": [0.2266, 0.2350, 0.2183], "mean": 0.2266, "cv": 0.0368},
            "sparse_bipolar":  {"vals": [0.8000, 0.8150, 0.8083], "mean": 0.8078, "cv": 0.0093},
        },
        "sat_frac_cross_seed": 0.4375,
        "sat_frac_v1_baseline": 0.625,
        "capacity_lift_confirmed": True,
        "supersedes_v1_MM_atom_prefix": "T3/EXP_substrate_pc_sparsity_x_encoder_crossproduct_v1_n8192_3seed_MM_",
        "cert_increment_delta": 1,
        "discipline_tags": [
            "META_RULE_Q_below_threshold_43p75pct_sat_frac",
            "META_RULE_H_cardinality_ok_16_of_16_all_seeds",
            "META_RULE_AV_interaction_pairs_visible_4_of_6",
            "DISCRIMINATOR_MUST_SURVIVE_SCALE_confirmed_at_N_8192_full",
            "2x_drill_capacity_lift_v1_MM_to_v2_CG",
            "Fix_28_per_arm_metrics_verified",
            "stage_3_compositional_understanding_USER_2026-06-26",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

# ============================================================================
# BATCH Kcliff_v3: MEASURED_MECHANISM (CERT +0)
# ============================================================================
atom_Kcliff_v3_MM = {
    "id": (
        "T3/EXP_substrate_sequence_binding_K_cliff_phase_diagram_v3_extended_range_3seed_MM_"
        "SAT_escape_60_to_12_pct_now_FLOOR_dominant_60_pct_11of12_K_cliffs_exact_match_"
        "66of72_band_agree_avg_arms_diff_cv_0p00102_2026-07-01"
    ),
    "name": (
        "MEASURED-MECHANISM K-cliff phase-diagram v3 extended-range 3-seed FULL: 2x-drill of "
        "v2 MM. SAT-escape confirmed (60%->12%) but axis shifted into FLOOR-dominant regime "
        "(60% FLOOR). K_cliffs=12/12 fire all seeds; 11/12 K_cliff locations exact-match "
        "cross-seed (v2 had 10/12); 66/72 phase points same band all-3 (v2 had 61/72); "
        "avg_arms_diff cv=0.00102 (v2 was 0.00162; even tighter). Per-cell MB all 3 seeds; "
        "cliff-location reproducibility CG-quality but per-cell verdict prevents CG promotion. "
        "Complements v2: v2 characterized SAT-dominant regime; v3 characterizes FLOOR-dominant. "
        "CERT +0."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "3-seed FULL K-cliff phase-diagram v3 extended K range. OFF-DATA recompute: "
        "run_mode=full all 3; cardinality 72/72 records + 21600/21600 all seeds; elapsed 148-232s. "
        "tier_counts: n_SAT=[9,9,8] cv=0.067; n_MB=[7,8,8] cv=0.075; n_FLOOR=[42,43,43] cv=0.014; "
        "n_TRANSITION=[14,12,13] cv=0.077. "
        "K_cliffs_per_combo exact-match 11/12 (only N16384_Q4 disagrees: [1000, 1000, 500]). "
        "avg_arms_diff cross-seed [0.2365, 0.2361, 0.2361] cv=0.00102. "
        "Phase-point all-3 same band: 66/72 (92%). K_cliffs=12/12 fire all seeds. "
        "SAT-escape confirmed vs v2: v2 was 42-43/72 SAT (60%); v3 is 8-9/72 SAT (12%). "
        "BUT axis flipped into FLOOR-dominant: v3 is 42-43/72 FLOOR (60%). Neither v2 nor v3 "
        "hits the free-discrimination regime; both characterize their respective saturation "
        "boundaries. "
        "TIER: MM. Cliff-location reproducibility is CG-quality (11/12 exact; cv 0.001 on "
        "avg_arms_diff) but per-cell MB verdict + FLOOR-dominant regime = MM. Complements v2 "
        "MM: pair characterizes both edges of the phase diagram. CERT +0."
    ),
    "metadata": {
        "provenance_quality": "MEASURED_MECHANISM",
        "verdict": "MEASURED_MECHANISM",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python on 3 seeds metrics.json (remote pulled): "
            "run_mode=full all 3; cardinality 72/72 all seeds; K_cliffs=12/12 fire all seeds; "
            "K_cliffs exact-match 11/12 combos; avg_arms_diff cv=0.00102; "
            "n_SAT cv=0.067; n_MB cv=0.075; n_FLOOR cv=0.014; n_TRAN cv=0.077; "
            "66/72 phase points same band all-3 seeds; SAT_frac 12% (vs v2 60%)"
        ),
        "regime": {"N_grid":[2048,4096,8192,16384], "Q_grid":[1,2,4], "K_extended_range": True},
        "per_seed_metrics_paths": {
            "seed_7":  "data/exp_substrate_sequence_binding_K_cliff_phase_diagram_v3_extended_range_seed_7/metrics.json (remote pulled)",
            "seed_13": "data/exp_substrate_sequence_binding_K_cliff_phase_diagram_v3_extended_range_seed_13/metrics.json (remote pulled)",
            "seed_19": "data/exp_substrate_sequence_binding_K_cliff_phase_diagram_v3_extended_range_seed_19/metrics.json (remote pulled)",
        },
        "K_cliff_exact_match_cross_seed": "11 of 12 combos",
        "K_cliff_disagreements": ["N16384_Q4 [1000, 1000, 500]"],
        "avg_arms_diff_cross_seed": {"vals": [0.2365, 0.2361, 0.2361], "cv": 0.00102},
        "phase_point_all_3_same_band": "66 of 72 (92%)",
        "sat_frac_v3": 0.12,
        "sat_frac_v2_baseline": 0.60,
        "floor_frac_v3": 0.60,
        "sat_escape_confirmed_but_floor_dominant_now": True,
        "complements_v2_MM_at_opposite_regime_boundary": True,
        "cert_increment_delta": 0,
        "discipline_tags": [
            "META_RULE_Q_escaped_SAT_dominance_but_now_FLOOR_dominant",
            "META_RULE_H_cardinality_ok_72_of_72_all_seeds",
            "META_RULE_AF_cross_seed_reproducibility_at_ceiling_11of12_K_cliffs_exact_match",
            "2x_drill_v2_SAT_regime_lifted_to_v3_FLOOR_regime",
            "Fix_28_per_arm_metrics_verified",
            "stage_3_compositional_understanding_USER_2026-06-26",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

# ============================================================================
# BATCH E_v2: MEASURED_MECHANISM (CERT +0; auditor over-rides author HP -> MM)
# ============================================================================
atom_E_v2_MM = {
    "id": (
        "T3/EXP_substrate_bytes_per_fact_pareto_v2_3seed_MM_auditor_override_HP_to_MM_"
        "META_RULE_Q_71pct_sat_20of28_at_recall_1p0_FP16_DENSE_broken_arm_recall_0p0_"
        "all_M_all_seeds_BFLOAT16_INT4_BINARY_valid_pareto_2026-07-01"
    ),
    "name": (
        "MEASURED-MECHANISM bytes_per_fact_pareto v2 3-seed FULL: author verdict HP; auditor "
        "over-rides to MM per META_RULE_Q (20/28 cells at recall=1.0 ceiling = 71% saturation) + "
        "FP16_DENSE broken arm (recall=0.0 all M all seeds; not a Pareto point but broken quant). "
        "Real bounds: BFLOAT16 not-collapsed at M=4000 (recall=1.0); INT4 valid_tier at M=4000; "
        "BINARY_DENSE degrades gracefully to 0.9995 at M=20000; SPARSE_BIPOLAR_0p05 shows real "
        "seed variance at M=4000 [0.805, 0.827, 0.822] cv=0.014. Pareto separations true all seeds; "
        "monotone_decay all 7 arms all seeds; mechanism_hashes_distinct=True. CERT +0. "
        "2x-drill: fix FP16_DENSE + test M=20000-40000 where BFLOAT16 + INT4 discriminate."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "3-seed FULL bytes_per_fact_pareto v2 with sparse-CPU routing fix. Author verdict HP "
        "all 3 seeds. OFF-DATA recompute: run_mode=full all 3; elapsed 78-79s all; "
        "cardinality 28/28 units all seeds; positive_control PASS (FP32 recall=1.0 all); "
        "bfloat16_not_collapsed=True all; int4_valid_tier=True all; pareto_2x_separation_ok=True "
        "all; monotone_decay_ok=True all; monotone_ok_per_arm all 7 arms True all seeds; "
        "mechanism_hashes_distinct=True all. "
        "PER-ARM CROSS-SEED IDENTITY CHECK: 20/28 cells identical bit-for-bit across seeds "
        "(all at recall=1.0 ceiling = META_RULE_Q trip); 8/28 cells differ. "
        "The 8 differing cells: (a) FP16_DENSE at all M in {1000,4000,10000,20000}: recall=0.0 "
        "all seeds -- BROKEN ARM, not a measured Pareto point; likely FP16 quantization failure "
        "at encoding level. (b) SPARSE_BIPOLAR_0p05 at M=4000: [0.805, 0.827, 0.822] cv=0.014 "
        "-- real seed variance. (c) BINARY_DENSE at M=20000: [0.9995, 0.9995, 0.9990] -- near "
        "ceiling; seed_19 tiny drop. "
        "AUDITOR TIER: MM (over-rides author HP). Rationale: cross-seed identity at recall=1.0 "
        "ceiling is not free-discrimination; META_RULE_Q trips at 71% ceiling-saturation. "
        "FP16_DENSE broken arm should not be counted as a Pareto point. The proven bounds: "
        "BFLOAT16 works at M<=4000; INT4 works at M=4000; BINARY_DENSE graceful degradation "
        "to M=20000; SPARSE_BIPOLAR shows real seed variance at capacity edge. "
        "2X-DRILL: (a) fix FP16_DENSE encoding path; (b) re-run at M=20000-40000 where "
        "BFLOAT16 + INT4 discriminate (recall < 1.0); CG-eligible for BFLOAT16/INT4 sub-claim "
        "if those specific arms discriminate cleanly across seeds without saturation. CERT +0."
    ),
    "metadata": {
        "provenance_quality": "MEASURED_MECHANISM",
        "verdict": "MEASURED_MECHANISM",
        "author_verdict_overridden": "HARD_PASS -> MEASURED_MECHANISM per META_RULE_Q + broken_arm_FP16",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python on 3 seeds metrics.json (remote pulled): "
            "run_mode=full all 3; cardinality 28/28 all seeds; positive_control PASS all; "
            "20/28 cells at recall=1.0 identical cross-seed (META_RULE_Q trip); "
            "FP16_DENSE recall=0.0 all M all seeds (broken arm); "
            "SPARSE_BIPOLAR_0p05 M=4000 [0.805, 0.827, 0.822] shows real seed variance; "
            "BINARY_DENSE M=20000 [0.9995, 0.9995, 0.9990] near-ceiling variance"
        ),
        "regime": {"arms": ["FP32_DENSE","BFLOAT16_DENSE","FP16_DENSE","INT8_DENSE",
                            "INT4_QUANTIZED","BINARY_DENSE","SPARSE_BIPOLAR_0p05"],
                   "M_grid": [1000, 4000, 10000, 20000], "n_units_per_seed": 28},
        "per_seed_metrics_paths": {
            "seed_7":  "data/exp_substrate_bytes_per_fact_pareto_v2_seed_7/metrics.json (remote pulled)",
            "seed_13": "data/exp_substrate_bytes_per_fact_pareto_v2_seed_13/metrics.json (remote pulled)",
            "seed_19": "data/exp_substrate_bytes_per_fact_pareto_v2_seed_19/metrics.json (remote pulled)",
        },
        "sat_ceiling_20_of_28_at_recall_1p0": True,
        "broken_arm_FP16_DENSE_recall_0p0_all_M_all_seeds": True,
        "real_seed_variance_at_capacity_edge": {
            "SPARSE_BIPOLAR_M4000": [0.805, 0.827, 0.822],
            "BINARY_DENSE_M20000":  [0.9995, 0.9995, 0.9990],
        },
        "proven_bounds": {
            "BFLOAT16_not_collapsed_at_M_le_4000": True,
            "INT4_valid_tier_at_M_4000": True,
            "BINARY_DENSE_graceful_degradation_to_M_20000": True,
        },
        "cert_increment_delta": 0,
        "discipline_tags": [
            "META_RULE_Q_SUSPECT_1p000_20_of_28_at_ceiling",
            "META_RULE_H_cardinality_ok_28_of_28_all_seeds",
            "broken_arm_FP16_DENSE_not_a_pareto_point",
            "Fix_28_per_arm_metrics_verified_reveals_ceiling_identity",
            "auditor_override_HP_to_MM_per_META_RULE_Q_and_broken_arm",
            "stage_3_compositional_understanding_USER_2026-06-26",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

# ============================================================================
# BATCH B_v1: HARD_FAIL (CERT +0; Gate D fail)
# ============================================================================
atom_B_v1_HF = {
    "id": (
        "T3/EXP_substrate_seqbind_N_dim_scaling_law_v1_3seed_HARD_FAIL_Gate_D_positive_control_"
        "regression_K_cliff_1_log2_unit_below_CG_predicted_center_at_N_8192_delta_1p0_tol_0p5_"
        "substrate_scaling_slope_0p70_to_1p13_r2_0p86_to_0p90_2026-07-01"
    ),
    "name": (
        "HARD_FAIL seqbind N_dim scaling law v1 3-seed FULL Gate D fail: at N=8192 K_cliff=500 "
        "(log2=8.966); CG-predicted center=1000 (log2=9.966); |delta|=1.0 vs tol 0.5. All 3 seeds "
        "identical HF. Substrate scaling fits: seed_7 slope=0.83 r2=0.90, seed_13 slope=1.13 r2=0.86, "
        "seed_19 slope=0.70 r2=0.89. K_cliff per seed at N=16384: 1000/2000/1000. RANDOM arm returns "
        "0 at all N. Substantive negative: CG-predicted N-dim scaling relationship NOT observed at "
        "N=8192; K_cliff sits 1 log2 unit below prediction. CERT +0. 2x-drill: revise formula OR "
        "test N grid outside 2048-16384."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "3-seed FULL seqbind N_dim scaling law v1. OFF-DATA recompute: run_mode=full all 3; "
        "elapsed 37s all; cardinality_ok=True all. All 3 HARD_FAIL_POSITIVE_CONTROL_REGRESSION "
        "at Gate D: N=8192 K_cliff observed=500 (log2=8.966); CG-predicted center=1000 "
        "(log2=9.966); |delta|=1.000 vs tol 0.5 -> FAIL. Per-seed substrate scaling fits "
        "(fit_ok=True all): seed_7 slope=0.829, intercept=-1.805, r2=0.899; seed_13 slope=1.129, "
        "intercept=-5.305, r2=0.862; seed_19 slope=0.697, intercept=0.178, r2=0.891. "
        "K_cliff per N per seed: seed_7 {2048:200, 4096:200, 8192:500, 16384:1000}; "
        "seed_13 {2048:200, 4096:200, 8192:500, 16384:2000}; seed_19 {2048:200, 4096:500, "
        "8192:500, 16384:1000}. RANDOM arm K_cliff=0 all N all seeds (positive control degenerate; "
        "correct behavior). "
        "Substantive negative: the CG-predicted scaling formula fails Gate D across all 3 seeds "
        "with identical delta=1.000 log2 unit below prediction. This is a clean honest-negative "
        "on the scaling-law hypothesis. CERT +0. "
        "2x-DRILL: revise CG-prediction formula (the log2(1000) center may be over-optimistic) "
        "OR test N grid outside 2048-16384 (may hit floor or need larger N to see the predicted "
        "scaling)."
    ),
    "metadata": {
        "provenance_quality": "HARD_FAIL",
        "verdict": "HARD_FAIL",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python on 3 seeds metrics.json (remote pulled): "
            "all 3 HARD_FAIL_POSITIVE_CONTROL_REGRESSION Gate D at N=8192 with identical delta=1.000 "
            "log2 vs tol 0.5; substrate scaling fits all fit_ok=True with slopes 0.70-1.13 r2 0.86-0.90; "
            "K_cliff by N per seed shows monotone increase; RANDOM K_cliff=0 all N all seeds"
        ),
        "regime": {"N_grid": [2048, 4096, 8192, 16384], "arms": ["SUBSTRATE","RANDOM"]},
        "per_seed_metrics_paths": {
            "seed_7":  "data/exp_substrate_seqbind_N_dim_scaling_law_v1_seed_7/metrics.json (remote pulled)",
            "seed_13": "data/exp_substrate_seqbind_N_dim_scaling_law_v1_seed_13/metrics.json (remote pulled)",
            "seed_19": "data/exp_substrate_seqbind_N_dim_scaling_law_v1_seed_19/metrics.json (remote pulled)",
        },
        "gate_D_fail_reason": "K_cliff at N=8192 is 500 (log2=8.966); CG-predicted center is log2(1000)=9.966; |delta|=1.000 exceeds tol 0.5",
        "substrate_scaling_fits": {
            "seed_7":  {"slope": 0.8288, "intercept": -1.8048, "r2": 0.8992, "fit_ok": True},
            "seed_13": {"slope": 1.1288, "intercept": -5.3048, "r2": 0.8619, "fit_ok": True},
            "seed_19": {"slope": 0.6966, "intercept": 0.1781, "r2": 0.8914, "fit_ok": True},
        },
        "K_cliff_by_N_per_seed": {
            "seed_7":  {"2048": 200, "4096": 200, "8192": 500, "16384": 1000},
            "seed_13": {"2048": 200, "4096": 200, "8192": 500, "16384": 2000},
            "seed_19": {"2048": 200, "4096": 500, "8192": 500, "16384": 1000},
        },
        "cert_increment_delta": 0,
        "discipline_tags": [
            "Gate_D_positive_control_regression_all_3_seeds_identical_delta_1p0",
            "META_RULE_H_cardinality_ok_all_3_seeds",
            "Fix_28_per_arm_metrics_verified",
            "honest_negative_CG_prediction_formula_revision_needed_OR_N_grid_extension",
            "stage_3_compositional_understanding_USER_2026-06-26",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

# ============================================================================
# BATCH Axis J: HARD_FAIL 2-seed (seed_7 still RUNNING; CERT +0)
# ============================================================================
atom_axis_J_HF_2seed = {
    "id": (
        "T3/EXP_substrate_order_binding_family_v1_2seed_HARD_FAIL_order_binding_capability_family_"
        "invariant_at_WM_regime_all_3_ops_K_star_500_identical_max_sep_0p0_log10_"
        "mech_hashes_distinct_arms_genuinely_different_but_all_K_star_same_seed_7_STILL_RUNNING_2026-07-01"
    ),
    "name": (
        "HARD_FAIL Axis J order_binding_family v1 2-seed FULL (seed_7 still RUNNING per runner "
        "hang; 2/2 completed seeds identical HF): all 3 order-binding operations "
        "(CYCLIC_SHIFT / RANDOM_PERMUTATION / PHASE_ROTATION) produce K*=500 at N=8192 with "
        "max_log10_sep=0.000. n_ops_distinct_from_baseline=0. Mechanistic distinctness holds "
        "(3/3 bundle pairs distinct; 3/3 positions pairs distinct; mech hashes all differ) -- "
        "arms are genuinely different mechanisms but ALL PRODUCE IDENTICAL K*. Positive control "
        "PASS both seeds. Substantive substrate finding: order-binding axis is "
        "CAPABILITY-FAMILY-INVARIANT at WM regime. Composes with DxO seed_7 finding. CERT +0."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Axis J order_binding_family v1 3-seed FULL dispatched; seed_7 STILL RUNNING (elapsed_s "
        "= 0.15 stuck; likely runner hang per Testbed a57b9f19 infra note). Atom records 2-seed "
        "evidence from seed_13 + seed_19; will supersede if seed_7 diverges. "
        "OFF-DATA recompute (seed_13 + seed_19): run_mode=full both; elapsed 62-76s both; "
        "cardinality 9/9 both; verdict HARD_FAIL_ORDER_BINDING_INVARIANT both. "
        "K_star_per_op identical across ops within each seed AND across seeds: "
        "  seed_13: CYCLIC_SHIFT=500 RANDOM_PERMUTATION=500 PHASE_ROTATION=500 (all K*=500). "
        "  seed_19: CYCLIC_SHIFT=500 RANDOM_PERMUTATION=500 PHASE_ROTATION=500 (all K*=500). "
        "K_star_log10_sep_pairs = 0.000 all 3 pairs both seeds. "
        "n_ops_distinct_from_baseline=0 both seeds. "
        "Mechanistic distinctness PASS: 3/3 op_pair_bundle_distinctness True; 3/3 "
        "op_pair_positions_distinctness True; op_bundle_hashes all 3 distinct; "
        "op_positions_hashes all 3 distinct. Arms are genuinely different mechanisms but all "
        "produce identical K*=500. "
        "Positive control PASS both seeds (CYCLIC_SHIFT K=50 top1=1.0 above 0.8 floor). "
        "tier_counts identical both seeds: SAT=3 MB=3 FLOOR=2 TRANSITION=1. "
        "max_cv per op high (0.59-0.70) = structural saturation noise. "
        "Substantive substrate finding: order-binding operation choice does NOT shift capacity "
        "location K* at N=8192 WM regime. The 3 operations are capability-family-invariant. "
        "COMPOSES WITH DxO seed_7 finding: DxO shows binding-op (Hadamard/CircularConv/FHRR) "
        "also produces identical K_cliff=750 at alpha=0.5. Two orthogonal binding axes both "
        "capability-invariant. CERT +0."
    ),
    "metadata": {
        "provenance_quality": "HARD_FAIL",
        "verdict": "HARD_FAIL",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python on 2 completed seeds (seed_7 still RUNNING per "
            "runner hang): both HARD_FAIL_ORDER_BINDING_INVARIANT with identical K*=500 all 3 ops; "
            "mechanistic distinctness holds 3/3 pairs; positive_control PASS both; "
            "K_star_log10_sep_pairs all 0.000"
        ),
        "regime": {"N": 8192, "ops": ["CYCLIC_SHIFT","RANDOM_PERMUTATION","PHASE_ROTATION"]},
        "per_seed_metrics_paths": {
            "seed_7":  "data/exp_substrate_order_binding_family_v1_seed_7/metrics.json (STILL RUNNING)",
            "seed_13": "data/exp_substrate_order_binding_family_v1_seed_13/metrics.json",
            "seed_19": "data/exp_substrate_order_binding_family_v1_seed_19/metrics.json",
        },
        "K_star_per_op_cross_seed": {
            "seed_13": {"CYCLIC_SHIFT": 500, "RANDOM_PERMUTATION": 500, "PHASE_ROTATION": 500},
            "seed_19": {"CYCLIC_SHIFT": 500, "RANDOM_PERMUTATION": 500, "PHASE_ROTATION": 500},
        },
        "log10_sep_pairs_all_0p0_both_seeds": True,
        "mechanistic_distinctness_pass_both_seeds": True,
        "positive_control_pass_both_seeds": True,
        "seed_7_still_running_will_supersede_if_diverges": True,
        "composes_with_axis_D_x_O_seed_7_binding_op_capacity_invariant": True,
        "cert_increment_delta": 0,
        "discipline_tags": [
            "honest_negative_order_binding_capability_family_invariant_at_WM_regime",
            "META_RULE_AX_distinctness_pass_arms_mechanistically_different_but_K_star_identical",
            "META_RULE_H_cardinality_ok_both_completed_seeds",
            "composes_with_axis_D_x_O_binding_op_axis_null_at_capacity_location",
            "seed_7_still_running_2_of_3_seed_atom_provisional",
            "stage_3_compositional_understanding_USER_2026-06-26",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

# ============================================================================
# BATCH DxO: HARD_FAIL single-seed (CERT +0)
# ============================================================================
atom_axis_DxO_HF = {
    "id": (
        "T3/EXP_substrate_binding_op_x_capacity_v1_seed_7_single_seed_HARD_FAIL_binding_op_axis_"
        "capacity_invariant_at_WM_regime_all_3_ops_K_cliff_750_at_alpha_0p5_identical_"
        "top1_differs_HAD_0p27_CIR_0p37_FHRR_0p87_2026-07-01"
    ),
    "name": (
        "HARD_FAIL Axis DxO binding_op_x_capacity v1 seed_7 single-seed FULL: all 3 binding "
        "operations (HADAMARD_BIND / CIRCULAR_CONV_HRR / FHRR_COMPLEX_MUL) produce K_cliff=750 "
        "at alpha=0.5 with K_cliff_shift_from_ref=0.0 all 3 ops. Mechanistic distinctness holds "
        "(3/3 pairs distinct; op_mech_hashes distinct). Interesting sub-finding: top1 at alpha=0.5 "
        "DIFFERS meaningfully across ops (HAD 0.267 / CIR 0.367 / FHRR 0.867) even though "
        "K_cliff location is identical. Substantive substrate finding: binding-op axis affects "
        "RECALL LEVEL but not CAPACITY LOCATION at WM regime. Composes with Axis J HF. "
        "Single-seed; cross-seed replication recommended. CERT +0."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Axis DxO binding_op_x_capacity v1 seed_7 single-seed FULL. OFF-DATA recompute: "
        "run_mode=full; elapsed_s=186.4; cardinality 9/9. verdict HARD_FAIL_BINDING_OP_"
        "CAPACITY_INVARIANT. All 3 binding ops (HADAMARD_BIND, CIRCULAR_CONV_HRR, "
        "FHRR_COMPLEX_MUL) produce K_cliff=750 at alpha=0.5; K_cliff_shift_from_ref=0.0 all "
        "3 ops; n_ops_shifted_ge_15pct=0. "
        "SUB-FINDING: top1 at alpha=0.5 DIFFERS across ops meaningfully: HADAMARD 0.267, "
        "CIRCULAR 0.367, FHRR 0.867 -- 3.2x range. So binding-op affects recall LEVEL but not "
        "capacity LOCATION. This is a substantive finding: capacity axis is invariant to "
        "binding-op family choice, but performance axis is NOT invariant. "
        "Mechanistic distinctness: 3/3 pairs distinct; op_mech_hashes all differ; arms are "
        "genuinely different mechanisms. "
        "Positive control PASS (HADAMARD alpha=0.1 M=150 top1=1.0 above 0.8 floor). "
        "tier_counts: SAT=3 MB=2 FLOOR=1 TRANSITION=3. max_cv per op: HADAMARD 0.858 / "
        "CIRCULAR 0.695 / FHRR 0.366 (structural saturation noise). "
        "COMPOSES WITH Axis J HF: both binding-family axes (order + binding-op) show identical "
        "K*/K_cliff across mechanistically-distinct family members. Substrate WM capacity "
        "location is INVARIANT to binding-family choice within each axis. "
        "CERT +0. Single-seed atom; recommend cross-seed replication before promoting to MM."
    ),
    "metadata": {
        "provenance_quality": "HARD_FAIL",
        "verdict": "HARD_FAIL",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python on seed_7 metrics.json: "
            "run_mode=full; cardinality 9/9; verdict HARD_FAIL_BINDING_OP_CAPACITY_INVARIANT; "
            "K_cliff=750 all 3 ops; K_cliff_shift=0.0 all 3 ops; mechanistic distinctness 3/3; "
            "top1 at alpha=0.5 differs meaningfully (HAD 0.27 / CIR 0.37 / FHRR 0.87)"
        ),
        "regime": {"N": 8192, "B_banks": 16, "ops": ["HADAMARD_BIND","CIRCULAR_CONV_HRR","FHRR_COMPLEX_MUL"],
                   "alpha_grid": "sweep_including_0p1_and_0p5"},
        "metrics_path": "data/exp_substrate_binding_op_x_capacity_v1_seed_7/metrics.json",
        "K_cliff_per_op_at_alpha_0p5": {"HADAMARD_BIND": 750, "CIRCULAR_CONV_HRR": 750, "FHRR_COMPLEX_MUL": 750},
        "top1_at_alpha_0p5_differs": {"HADAMARD_BIND": 0.267, "CIRCULAR_CONV_HRR": 0.367, "FHRR_COMPLEX_MUL": 0.867},
        "capacity_axis_invariant_to_binding_op_family": True,
        "performance_axis_NOT_invariant_binding_op_matters_for_recall": True,
        "composes_with_axis_J_order_binding_family_HF": True,
        "single_seed_atom_cross_seed_replication_recommended": True,
        "cert_increment_delta": 0,
        "discipline_tags": [
            "honest_negative_binding_op_axis_capacity_invariant_at_WM_regime",
            "sub_finding_top1_level_differs_across_binding_ops_3x_range",
            "META_RULE_AX_distinctness_pass_arms_mechanistically_different_but_K_cliff_identical",
            "META_RULE_H_cardinality_ok_9_of_9",
            "composes_with_axis_J_order_binding_family_HF_two_orthogonal_binding_axes_capability_invariant",
            "single_seed_recommend_cross_seed_before_MM_promotion",
            "stage_3_compositional_understanding_USER_2026-06-26",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

# ============================================================================
# CERT LEDGER ROWS
# ============================================================================
_t0 = time.time()

ledger_A_v2_CG = {
    "ts": _t0,
    "op": "cert_ruling",
    "atom_id": f"math::{atom_A_v2_CG['id']}",
    "cert_status": "chain_grade",
    "cert_class": "pre_reg_pass",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": None,
    "verdict": (
        "CHAIN_GRADE_3seed_HP_per_cell_capacity_lift_2x_drill_v1_MM_to_v2_CG_sat_frac_"
        "62p5_to_43p75_pct_all_4_encoders_range_ge_0p15_cv_binary_0p009_sparse_0p009_"
        "fhrr_0p037_hrr_0p064_positive_control_non_sat_pass_all_seeds"
    ),
    "cert_increment_delta": 1,
    "cv": 0.0095,  # min cv (binary_bipolar); all 4 << 0.15
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_substrate_pc_sparsity_x_encoder_crossproduct_v2_n8192_seed_{7,13,19}/metrics.json (remote)",
        "atom_qualified_id": f"math::{atom_A_v2_CG['id']}",
    },
    "supersedes": None,  # amends v1 MM atom, but does not delete
    "note": (
        "A_v2_pc_sparsity_capacity_lift_2x_drill_lifts_v1_MM_to_CG_"
        "sat_frac_reduced_62p5_to_43p75_pct_all_4_encoders_discriminate_range_ge_0p15_"
        "cross_seed_cv_all_under_0p07_positive_control_pass_non_sat_META_RULE_Q_below_threshold_"
        "cardinality_16_of_16_all_seeds_encoder_pair_distinct_6_of_6_all_seeds_"
        "13th_CG_promotion_of_recent_arc"
    ),
}

ledger_Kcliff_v3_MM = {
    "ts": _t0 + 0.001,
    "op": "cert_ruling",
    "atom_id": f"math::{atom_Kcliff_v3_MM['id']}",
    "cert_status": "measured_mechanism",
    "cert_class": "mechanism_characterization",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": None,
    "verdict": (
        "MM_3seed_MB_per_cell_extended_range_SAT_escape_60_to_12_pct_now_FLOOR_dominant_60pct_"
        "11of12_K_cliffs_exact_match_66of72_band_agree_avg_arms_diff_cv_0p00102_"
        "complements_v2_MM_at_opposite_regime_boundary"
    ),
    "cert_increment_delta": 0,
    "cv": 0.00102,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_substrate_sequence_binding_K_cliff_phase_diagram_v3_extended_range_seed_{7,13,19}/metrics.json (remote)",
        "atom_qualified_id": f"math::{atom_Kcliff_v3_MM['id']}",
    },
    "supersedes": None,
    "note": (
        "Kcliff_v3_extended_range_3seed_MM_SAT_escape_confirmed_but_FLOOR_dominant_now_"
        "cliff_locations_reproducible_11of12_exact_match_cross_seed_"
        "complements_v2_MM_which_characterized_SAT_dominant_regime"
    ),
}

ledger_E_v2_MM = {
    "ts": _t0 + 0.002,
    "op": "cert_ruling",
    "atom_id": f"math::{atom_E_v2_MM['id']}",
    "cert_status": "measured_mechanism",
    "cert_class": "mechanism_characterization_auditor_override_HP_to_MM",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": None,
    "verdict": (
        "MM_auditor_override_HP_to_MM_META_RULE_Q_71pct_20of28_at_recall_1p0_"
        "FP16_DENSE_broken_arm_recall_0p0_all_M_all_seeds_"
        "proven_bounds_BFLOAT16_not_collapsed_INT4_valid_tier_BINARY_graceful_"
        "SPARSE_BIPOLAR_real_seed_variance_at_M_4000"
    ),
    "cert_increment_delta": 0,
    "cv": 0.014,  # SPARSE_BIPOLAR M=4000 cross-seed cv (the discriminating cell)
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_substrate_bytes_per_fact_pareto_v2_seed_{7,13,19}/metrics.json (remote)",
        "atom_qualified_id": f"math::{atom_E_v2_MM['id']}",
    },
    "supersedes": None,
    "note": (
        "E_v2_bytes_per_fact_pareto_3seed_auditor_override_HP_to_MM_"
        "META_RULE_Q_trip_20of28_cells_at_recall_1p0_ceiling_"
        "FP16_DENSE_broken_arm_recall_0p0_all_M_all_seeds_not_a_pareto_point_"
        "BFLOAT16_INT4_BINARY_pareto_arms_valid_2x_drill_fix_FP16_and_test_M_20k_to_40k"
    ),
}

ledger_B_v1_HF = {
    "ts": _t0 + 0.003,
    "op": "cert_ruling",
    "atom_id": f"math::{atom_B_v1_HF['id']}",
    "cert_status": "hard_fail",
    "cert_class": "honest_negative_gate_D_positive_control_regression",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": None,
    "verdict": (
        "HARD_FAIL_3seed_Gate_D_positive_control_regression_K_cliff_1_log2_unit_below_"
        "CG_predicted_center_at_N_8192_delta_1p0_tol_0p5_scaling_slope_0p70_to_1p13_"
        "r2_0p86_to_0p90_RANDOM_arm_degenerate_2x_drill_revise_formula_OR_N_grid"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_substrate_seqbind_N_dim_scaling_law_v1_seed_{7,13,19}/metrics.json (remote)",
        "atom_qualified_id": f"math::{atom_B_v1_HF['id']}",
    },
    "supersedes": None,
    "note": (
        "B_v1_seqbind_N_dim_scaling_law_3seed_HARD_FAIL_Gate_D_identical_delta_1p0_all_seeds_"
        "CG_predicted_formula_fails_at_N_8192_K_cliff_500_vs_predicted_1000_"
        "substrate_scaling_slope_varies_0p70_to_1p13_r2_0p86_to_0p90_"
        "2x_drill_revise_prediction_formula_OR_extend_N_grid_outside_2048_16384"
    ),
}

ledger_axis_J_HF_2seed = {
    "ts": _t0 + 0.004,
    "op": "cert_ruling",
    "atom_id": f"math::{atom_axis_J_HF_2seed['id']}",
    "cert_status": "hard_fail",
    "cert_class": "honest_negative_capability_family_invariant_2seed_seed_7_running",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": None,
    "verdict": (
        "HARD_FAIL_2seed_seed_13_and_19_identical_K_star_500_all_3_ops_log10_sep_0p0_"
        "order_binding_capability_family_invariant_at_WM_regime_mech_distinctness_pass_"
        "arms_genuinely_different_but_all_K_star_same_positive_control_pass_both_seeds_"
        "seed_7_STILL_RUNNING_provisional_will_supersede_if_diverges"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_substrate_order_binding_family_v1_seed_{7=RUNNING,13,19}/metrics.json",
        "atom_qualified_id": f"math::{atom_axis_J_HF_2seed['id']}",
    },
    "supersedes": None,
    "note": (
        "Axis_J_order_binding_family_2seed_HF_provisional_"
        "seed_7_still_running_per_runner_hang_note_2_of_3_completed_identical_HF_"
        "order_binding_capability_family_invariant_at_WM_regime_"
        "composes_with_axis_D_x_O_binding_op_capacity_invariant"
    ),
}

ledger_axis_DxO_HF = {
    "ts": _t0 + 0.005,
    "op": "cert_ruling",
    "atom_id": f"math::{atom_axis_DxO_HF['id']}",
    "cert_status": "hard_fail",
    "cert_class": "honest_negative_binding_op_capacity_invariant_single_seed",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": None,
    "verdict": (
        "HARD_FAIL_seed_7_single_seed_binding_op_axis_capacity_invariant_at_WM_regime_"
        "K_cliff_750_all_3_ops_at_alpha_0p5_shift_0p0_all_top1_differs_HAD_0p27_CIR_0p37_FHRR_0p87_"
        "3p2x_range_capacity_invariant_but_performance_NOT_invariant"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_substrate_binding_op_x_capacity_v1_seed_7/metrics.json",
        "atom_qualified_id": f"math::{atom_axis_DxO_HF['id']}",
    },
    "supersedes": None,
    "note": (
        "Axis_D_x_O_binding_op_x_capacity_seed_7_single_seed_HF_"
        "capacity_axis_invariant_to_binding_op_family_at_WM_regime_"
        "sub_finding_top1_level_differs_across_ops_HAD_CIR_FHRR_3p2x_range_"
        "composes_with_axis_J_order_binding_family_HF_two_orthogonal_binding_axes_capability_invariant_"
        "single_seed_recommend_cross_seed_before_MM_promotion"
    ),
}


# ============================================================================
# A5 write protocol with Windows os.replace retry
# ============================================================================
def append_jsonl_a5(path: Path, new_row: dict, label: str):
    print(f"[A5] {label}: path={path}")
    assert path.exists(), f"target does not exist: {path}"

    with open(path, "r", encoding="utf-8") as f:
        pre_lines = f.read().splitlines()
    pre_count = len(pre_lines)
    print(f"[A5] {label}: pre_count={pre_count}")

    for i, ln in enumerate(pre_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"PRE integrity fail line {i+1}: {e}")

    new_line = json.dumps(new_row, ensure_ascii=True)
    parsed_back = json.loads(new_line)
    if "id" in new_row:
        assert parsed_back.get("id") == new_row.get("id")
    if "atom_id" in new_row:
        assert parsed_back.get("atom_id") == new_row.get("atom_id")

    out_lines = pre_lines + [new_line]
    out_text = "\n".join(out_lines) + "\n"

    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text)
        f.flush()
        os.fsync(f.fileno())
    import time as _time
    for _attempt in range(10):
        try:
            os.replace(str(tmp_path), str(path))
            break
        except PermissionError:
            if _attempt == 9:
                raise
            _time.sleep(0.1 * (2 ** _attempt))

    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    print(f"[A5] {label}: post_count={post_count}")
    assert post_count == pre_count + 1

    tail = json.loads(post_lines[-1])
    if "id" in new_row:
        assert tail["id"] == new_row["id"]
    if "atom_id" in new_row:
        assert tail["atom_id"] == new_row["atom_id"]

    for i, ln in enumerate(post_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"POST integrity fail line {i+1}: {e}")

    print(f"[A5] {label}: OK")
    return post_count


def main():
    print(f"[A5] atomize START {ATOMIZED_BY} ts={time.time():.3f}")
    print(f"[A5] Wave atoms:")
    print(f"       A_v2 CG           = math::{atom_A_v2_CG['id'][:120]}...")
    print(f"       Kcliff_v3 MM      = math::{atom_Kcliff_v3_MM['id'][:120]}...")
    print(f"       E_v2 MM           = math::{atom_E_v2_MM['id'][:120]}...")
    print(f"       B_v1 HF           = math::{atom_B_v1_HF['id'][:120]}...")
    print(f"       Axis J HF 2-seed  = math::{atom_axis_J_HF_2seed['id'][:120]}...")
    print(f"       DxO HF seed_7     = math::{atom_axis_DxO_HF['id'][:120]}...")
    print()

    append_jsonl_a5(MATH_ATOMS, atom_A_v2_CG,          "math/atoms (A_v2 CG)")
    append_jsonl_a5(MATH_ATOMS, atom_Kcliff_v3_MM,     "math/atoms (Kcliff_v3 MM)")
    append_jsonl_a5(MATH_ATOMS, atom_E_v2_MM,          "math/atoms (E_v2 MM)")
    append_jsonl_a5(MATH_ATOMS, atom_B_v1_HF,          "math/atoms (B_v1 HF)")
    append_jsonl_a5(MATH_ATOMS, atom_axis_J_HF_2seed,  "math/atoms (Axis J HF 2seed)")
    append_jsonl_a5(MATH_ATOMS, atom_axis_DxO_HF,      "math/atoms (DxO HF)")
    append_jsonl_a5(CERT_LEDGER, ledger_A_v2_CG,       "cert_ledger (A_v2 CG +1)")
    append_jsonl_a5(CERT_LEDGER, ledger_Kcliff_v3_MM,  "cert_ledger (Kcliff_v3 MM)")
    append_jsonl_a5(CERT_LEDGER, ledger_E_v2_MM,       "cert_ledger (E_v2 MM)")
    append_jsonl_a5(CERT_LEDGER, ledger_B_v1_HF,       "cert_ledger (B_v1 HF)")
    append_jsonl_a5(CERT_LEDGER, ledger_axis_J_HF_2seed, "cert_ledger (Axis J HF 2seed)")
    append_jsonl_a5(CERT_LEDGER, ledger_axis_DxO_HF,   "cert_ledger (DxO HF)")

    print()
    print(f"[A5] DONE OK")
    print(f"[A5] Wave summary:")
    print(f"       1 CHAIN_GRADE (A_v2 capacity-lift 2x-drill lifts v1 MM to CG)")
    print(f"       2 MEASURED_MECHANISM (Kcliff_v3 FLOOR-regime; E_v2 override META_RULE_Q)")
    print(f"       3 HARD_FAIL (B_v1 Gate_D; Axis J 2-seed capability-invariant; DxO capacity-invariant)")
    print(f"[A5] CERT delta = +1 (A_v2 chain-grade)")


if __name__ == "__main__":
    main()
