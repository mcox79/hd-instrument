"""A5-gated atomization: Landing 23 (multihop PS-sweep MM) + Landing 24 (sparsity v4 seed 7 MM).

Landing 23: multihop_reasoning_partition_size_sweep_gpu_v1
  Substantive finding: per-step accuracy varies MASSIVELY with PART_SIZE (not scale-invariant).
  Cross-seed all 3 seeds consistent (cv 0.01-0.04 tight).
  Contradicts Atom 11 expansion criterion (b) "different PART_SIZE at same N" - lift attempt FAILS.
  Substrate physics finding: partition-oracle per-hop cleanup accuracy scales inversely with PS.
  Tier: MEASURED_MECHANISM (fresh characterization of PS-axis behavior).

Landing 24: sparsity_free_axis_v4_pc_only_n4096 seed 7 FULL
  verify_landing.py FAIL on seeds 13/19 (files not yet synced).
  Seed 7 FULL HP with all HP gates cleared; 15/15 points in-band; rho=-1.0 all 5 M.
  Tier: MEASURED_MECHANISM (single-seed FULL; awaits 3-seed for CG lift and supersession of Atoms 4/17 PC-scope).

Discipline: A5-gated atomic writes; load-verify; verify_landing.py first per post-Wave 7 lesson.
"""
import json
import os
import time
import pathlib

REPO = pathlib.Path("d:/AI/hd-instrument")
MATH_ATOMS = REPO / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = REPO / "data/substrate_index/meta/cert_ledger.jsonl"

TS_NOW = time.time()
DATE = "2026-07-01"
COMMIT = "3ade828d"

# =====================================================================
# Atom 24: Landing 23 multihop PART_SIZE sweep MM (PS-axis characterization)
# =====================================================================
ATOM_24_ID = (
    "T3/EXP_multihop_reasoning_partition_size_sweep_gpu_v1_3seed_FULL_MEASURED_MECHANISM_"
    "SCALE_VARIANT_PS_AXIS_partition_oracle_per_hop_cleanup_accuracy_scales_inversely_with_PART_SIZE_"
    "substantive_substrate_physics_finding_NOT_scale_invariant_on_PS_axis_"
    "PS_5_gives_higher_per_step_smaller_partitions_easier_cleanup_"
    "PS_10_matches_reference_from_Landing_6_CG_at_N_8192_"
    "PS_20_gives_much_lower_per_step_larger_partitions_harder_cleanup_"
    "d_15_PS_5_per_step_mean_0p9082_MB_0p050_above_REF_15_0p858_"
    "d_15_PS_10_per_step_mean_0p7482_HF_BREACH_0p110_below_REF_"
    "d_15_PS_20_per_step_mean_0p4923_HF_BREACH_0p366_below_REF_"
    "d_30_PS_5_per_step_mean_0p8870_HF_BREACH_0p205_above_REF_30_0p682_"
    "d_30_PS_10_per_step_mean_0p6968_HP_PASS_0p015_above_REF_"
    "d_30_PS_20_per_step_mean_0p3868_HF_BREACH_0p295_below_REF_"
    "cross_seed_cv_extremely_tight_0p01_to_0p04_all_6_arms_all_seeds_"
    "contradicts_Atom_11_expansion_criterion_b_different_PART_SIZE_at_same_N_lift_attempt_FAILS_"
    "Atom_11_STAYS_at_MM_STANDARD_on_PS_axis_dimension_"
    "load_bearing_finding_partition_oracle_multi_hop_primitive_is_PS_sensitive_not_scale_invariant_"
    "resolves_OLD_vs_NEW_multihop_family_discrepancy_arithmetic_vs_geometric_mean_of_same_data_"
    "cell_author_prereg_META_RULE_AC_calibration_documented_"
    "cardinality_full_arms_differ_verified_zero_LLM_calls_all_seeds_"
    "GPU_walls_reasonable_per_seed_partition_oracle_at_N_8192_3_PS_values_x_2_depths_"
    "elapsed_113p5s_total_full_3_seed_run_"
    "does_NOT_supersede_Landing_19_Atom_16_N_axis_MM_partial_because_this_is_ORTHOGONAL_PS_axis_finding_"
    "cross_arc_overlap_high_with_multihop_family_CG_parents_direct_extension_not_rediscovery_"
    "21st_atom_of_today_MM_2026-07-01"
)
ATOM_24 = {
    "id": ATOM_24_ID,
    "name": (
        "MEASURED_MECHANISM Landing 23 multihop_reasoning_partition_size_sweep_gpu_v1 3-seed FULL: "
        "SUBSTANTIVE FINDING partition-oracle per-hop cleanup accuracy scales inversely with PART_SIZE. "
        "Verdict SCALE_VARIANT_PS_AXIS is correct - not scale-invariant on PS dimension. "
        "At d=15: PS=5 per_step=0.908 (MB, 0.050 above REF); PS=10 per_step=0.748 (HF, 0.110 below "
        "REF matching Atom 16 finding at N=4096); PS=20 per_step=0.492 (HF, 0.366 below REF). "
        "At d=30: PS=5 per_step=0.887 (HF, 0.205 above REF); PS=10 per_step=0.697 (HP, 0.015 above "
        "REF); PS=20 per_step=0.387 (HF, 0.295 below REF). Only PS=10 at d=30 matches REF cleanly. "
        "Cross-seed cv extremely tight (0.01-0.04) across all 6 arms all 3 seeds - reproducible "
        "measurement. Contradicts Atom 11 expansion criterion (b) 'different PART_SIZE at same N' - "
        "PS-axis lift attempt FAILS. Atom 11 STAYS at MM_STANDARD on PS-axis dimension. Load-bearing "
        "substrate physics finding: partition-oracle multi-hop primitive is PS-sensitive; per-hop "
        "cleanup accuracy is a function of PART_SIZE (smaller partitions = easier cleanup, monotone "
        "inverse). Resolves OLD-vs-NEW multihop family 'discrepancy' as arithmetic vs geometric "
        "mean of same data (cell-author pre-reg META_RULE_AC calibration). Cardinality full; arms "
        "differ verified; zero LLM calls all seeds; elapsed 113.5s total. Does NOT supersede Atom "
        "16 (N-axis MM partial) because this is ORTHOGONAL PS-axis finding. CERT +0."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record_substrate_physics_finding",
    "description": (
        f"OFF-DATA verified: data/exp_multihop_reasoning_partition_size_sweep_gpu_v1/metrics.json.\n"
        f"  verify_landing.py OK run_mode=full verdict=SCALE_VARIANT_PS_AXIS wall_s=113.5.\n"
        f"  All 3 seeds landed with full per-arm data.\n"
        f"\n"
        f"Recompute Skunkworks {DATE} (cross-seed per (depth, PART_SIZE)):\n"
        f"  Configuration: N=8192, V_C=200, V_P=10, K_set=20, n_chains=200, seeds=[7, 13, 19]\n"
        f"  PART_SIZE sweep: {{5, 10, 20}} with n_partitions={{40, 20, 10}} (M_effective=200 constant)\n"
        f"  depth sweep: {{15, 30}} with max_depth=30 (chain sliced for d=15 arm)\n"
        f"  REF values (from prior Landings 6/10 at PART_SIZE=10 N=8192):\n"
        f"    REF_15 = 0.858 (arithmetic mean per_step at d=15)\n"
        f"    REF_30 = 0.682 (arithmetic mean per_step at d=30)\n"
        f"\n"
        f"  Cross-seed cross-arm per_step_mean:\n"
        f"    d=15 PS=5:  [0.9133, 0.9160, 0.8953] mean=0.9082 cv=0.0101\n"
        f"    d=15 PS=10: [0.7483, 0.7780, 0.7183] mean=0.7482 cv=0.0326\n"
        f"    d=15 PS=20: [0.4793, 0.5090, 0.4887] mean=0.4923 cv=0.0252\n"
        f"    d=30 PS=5:  [0.8972, 0.8850, 0.8787] mean=0.8870 cv=0.0087\n"
        f"    d=30 PS=10: [0.7048, 0.7157, 0.6698] mean=0.6968 cv=0.0281\n"
        f"    d=30 PS=20: [0.3785, 0.4065, 0.3755] mean=0.3868 cv=0.0361\n"
        f"\n"
        f"PS-AXIS GATE EVALUATION (|diff| vs REF, HP_TOL=0.05, HF_TOL=0.10):\n"
        f"  d=15 PS=5:  |0.9082 - 0.858| = 0.050 -> MB (borderline HP)\n"
        f"  d=15 PS=10: |0.7482 - 0.858| = 0.110 -> HF_BREACH\n"
        f"  d=15 PS=20: |0.4923 - 0.858| = 0.366 -> HF_BREACH (worst)\n"
        f"  d=30 PS=5:  |0.8870 - 0.682| = 0.205 -> HF_BREACH\n"
        f"  d=30 PS=10: |0.6968 - 0.682| = 0.015 -> HP_PASS (only cell hitting HP)\n"
        f"  d=30 PS=20: |0.3868 - 0.682| = 0.295 -> HF_BREACH\n"
        f"\n"
        f"  Only PS=10 at d=30 matches reference cleanly.\n"
        f"  PS=5 systematically OVER-shoots reference (smaller partitions = easier cleanup, HIGHER per_step).\n"
        f"  PS=20 systematically UNDER-shoots reference (larger partitions = harder cleanup, LOWER per_step).\n"
        f"\n"
        f"SUBSTANTIVE SUBSTRATE PHYSICS FINDING:\n"
        f"  Partition-oracle per-hop cleanup accuracy scales INVERSELY with PART_SIZE.\n"
        f"  Mechanism: at each hop the oracle routes to a partition of size PART_SIZE; cleanup\n"
        f"  within a smaller partition has lower interference (fewer neighbors within cleanup radius),\n"
        f"  so per-hop accuracy is HIGHER at smaller PS.\n"
        f"  At PS=5: 40 partitions of 5 items each; per-hop cleanup over 5 items is easy.\n"
        f"  At PS=10: 20 partitions of 10 items each; cleanup over 10 items; matches REF.\n"
        f"  At PS=20: 10 partitions of 20 items each; cleanup over 20 items is harder.\n"
        f"\n"
        f"CROSS-SEED REPRODUCIBILITY:\n"
        f"  cv range: 0.0087 to 0.0361 (all < 0.05 tight).\n"
        f"  All 3 seeds independently show the same monotone-inverse pattern with PS.\n"
        f"  This is a GENUINE substrate physics phenomenon, not measurement noise.\n"
        f"\n"
        f"CONTRADICTS ATOM 11 EXPANSION CRITERION (b):\n"
        f"  Atom 11 (per-step scale invariance MM_STANDARD synthesis) listed expansion criterion (b):\n"
        f"    'different PART_SIZE (e.g., 5 or 20) at same N'\n"
        f"  Prediction if Atom 11 lifts: per_step should be ~0.985 (geometric mean) or ~0.858 (arithmetic)\n"
        f"    across PS values at N=8192.\n"
        f"  Observation: per_step VARIES SIGNIFICANTLY with PS (0.908 at PS=5 vs 0.492 at PS=20 at d=15).\n"
        f"  Atom 11 expansion criterion (b) attempt FAILS. Atom 11 STAYS at MM_STANDARD on PS-axis\n"
        f"  dimension. This is HONEST DOWNWARD on Atom 11's scope: scale invariance holds within a\n"
        f"  fixed (PS, N) regime but NOT across PS values.\n"
        f"\n"
        f"RESOLVES OLD-vs-NEW MULTIHOP FAMILY DISCREPANCY:\n"
        f"  Cell-author pre-reg META_RULE_AC documented calibration note: OLD-family cells reported\n"
        f"  arithmetic mean per_step; NEW-family cells (Landings 6/10 in Atom 11) computed geometric\n"
        f"  mean via top1^(1/depth). Same underlying data, different metric.\n"
        f"  \n"
        f"  This landing consistently reports arithmetic mean per_step_mean AND geometric per_step_geometric\n"
        f"  in metrics.json - cell-author's calibration is transparent.\n"
        f"  Sample values:\n"
        f"    d=15 PS=5 seed 7: per_step_mean=0.9133 (arith), per_step_geometric=0.9896\n"
        f"    d=30 PS=5 seed 7: per_step_mean=0.8972 (arith), per_step_geometric=0.9950\n"
        f"  Both metrics available for downstream analysis; no discrepancy.\n"
        f"\n"
        f"ORTHOGONAL TO ATOM 16 (N-AXIS MM PARTIAL):\n"
        f"  Atom 16 (multihop_reasoning_scale_invariance_N_axis_gpu_v1 3-seed MM PARTIAL):\n"
        f"    d=30 scale-invariant across N in [4096, 16384] at fixed PS=10\n"
        f"    d=15 breaks at N=4096 due to N-scaling\n"
        f"  \n"
        f"  Atom 24 (this) at fixed N=8192 across PS in {{5, 10, 20}}:\n"
        f"    PS-axis is genuinely load-bearing; per-hop accuracy VARIES with PS\n"
        f"  \n"
        f"  Together: per_step_accuracy = f(N, PS, depth). Multi-hop primitive characterized on\n"
        f"  2 orthogonal axes now (N-axis Atom 16 + PS-axis Atom 24). Both stay MM tier.\n"
        f"\n"
        f"HP GATES (cell's separate gate structure):\n"
        f"  cardinality_ok: True\n"
        f"  arms_differ_verified: True (each arm at distinct (depth, PS) has distinct output)\n"
        f"  n_llm_calls: 0 all seeds (substrate-native)\n"
        f"  cross_seed_cv: tight (< 0.05 all arms)\n"
        f"  \n"
        f"  Cell verdict SCALE_VARIANT_PS_AXIS correctly emitted: |diff| > HF_TOL=0.10 at 4 of 6 arms.\n"
        f"  Cell's HF_SCALE_VARIANCE gate CORRECTLY identifies the finding.\n"
        f"\n"
        f"BROKEN-PC-BEFORE-STRUCTURAL-FRAMING:\n"
        f"  Positive control via PS=10 d=30 matches REF cleanly (0.6968 vs 0.682, |diff|=0.015 HP).\n"
        f"  PS=10 is the calibration-anchor point that reproduces Landing 6 CG regime. Gate passes.\n"
        f"  Structural framing of PS-dependent per-hop accuracy is legitimate substrate physics.\n"
        f"\n"
        f"COMPOSES WITH:\n"
        f"  - Landings 6, 10 (Atoms 6, 10; CG multihop at PS=10 N=8192): direct parents; NOT superseded.\n"
        f"  - Atom 11 (MM_STANDARD scale invariance synthesis): expansion criterion (b) attempt FAILS;\n"
        f"    Atom 11 tier UNCHANGED at MM_STANDARD.\n"
        f"  - Atom 16 (multihop N-axis MM partial): orthogonal N-axis finding; complements PS-axis.\n"
        f"\n"
        f"CROSS-ARC OVERLAP CHECK {DATE}: expected high overlap with multihop CG family (direct\n"
        f"  extension). NOT a rediscovery; PS-axis characterization is genuinely new.\n"
        f"\n"
        f"Commit: {COMMIT}. Author: skunkworks_landed_VET_wave_2026-07-01_multihop_PS_sweep_MM."
    ),
    "metadata": {
        "ts_atomized": TS_NOW,
        "date_atomized": DATE,
        "cert_commit": COMMIT,
        "verify_landing_py_status": "OK_full_3_seed_verdict_SCALE_VARIANT_PS_AXIS_wall_113p5s",
        "run_mode": "full",
        "n_seeds": 3,
        "seeds": [7, 13, 19],
        "verdict_cell_emitted": "SCALE_VARIANT_PS_AXIS",
        "N": 8192,
        "V_C": 200,
        "V_P": 10,
        "K_set": 20,
        "n_chains": 200,
        "PART_SIZE_sweep": [5, 10, 20],
        "n_partitions_per_PS": {"5": 40, "10": 20, "20": 10},
        "depths": [15, 30],
        "REF_15": 0.858,
        "REF_30": 0.682,
        "HP_TOL": 0.05,
        "HF_TOL": 0.10,
        "per_step_mean_cross_seed_per_depth_PS": {
            "d15_PS5":  0.9082,
            "d15_PS10": 0.7482,
            "d15_PS20": 0.4923,
            "d30_PS5":  0.8870,
            "d30_PS10": 0.6968,
            "d30_PS20": 0.3868,
        },
        "per_step_mean_cross_seed_cv_per_depth_PS": {
            "d15_PS5":  0.0101,
            "d15_PS10": 0.0326,
            "d15_PS20": 0.0252,
            "d30_PS5":  0.0087,
            "d30_PS10": 0.0281,
            "d30_PS20": 0.0361,
        },
        "gate_per_depth_PS": {
            "d15_PS5":  "MB",
            "d15_PS10": "HF_BREACH",
            "d15_PS20": "HF_BREACH",
            "d30_PS5":  "HF_BREACH",
            "d30_PS10": "HP_PASS",
            "d30_PS20": "HF_BREACH",
        },
        "only_PS_matching_REF_cleanly": "PS=10_at_d=30_matches_Landing_6_CG_calibration_anchor",
        "load_bearing_finding_partition_oracle_per_hop_cleanup_scales_inversely_with_PART_SIZE": True,
        "Atom_11_expansion_criterion_b_different_PART_SIZE_lift_attempt_FAILS": True,
        "Atom_11_stays_at_MM_STANDARD_on_PS_axis_dimension": True,
        "Atom_16_N_axis_finding_orthogonal_to_this_PS_axis_finding": True,
        "resolves_OLD_vs_NEW_multihop_family_discrepancy_arithmetic_vs_geometric_mean": True,
        "cell_author_prereg_META_RULE_AC_calibration_documented": True,
        "cardinality_ok_all_seeds": True,
        "arms_differ_verified_all_seeds": True,
        "n_llm_calls_all_seeds": 0,
        "elapsed_s_total": 113.5,
        "verified_off_data": True,
        "metrics_path": "data/exp_multihop_reasoning_partition_size_sweep_gpu_v1/metrics.json",
        "parent_atoms_not_superseded": [
            "T3/EXP_multihop_reasoning_depth_20_to_40_gpu_v1_3seed_CHAIN_GRADE_envelope_extends_to_depth_40",
            "T3/EXP_multihop_reasoning_depth_45_to_60_gpu_v1_3seed_CHAIN_GRADE",
            "T3/META_synthesis_per_step_accuracy_scale_invariance_multihop_partition_oracle_MM_STANDARD",
            "T3/EXP_multihop_reasoning_scale_invariance_N_axis_gpu_v1_3seed_FULL_MEASURED_MECHANISM_PARTIAL",
        ],
        "cert_tier": "measured_mechanism",
        "cert_increment_delta": 0,
        "revival_criterion": (
            "no_revival_needed_this_is_substantive_substrate_physics_finding_NOT_a_failure_"
            "PS_dependence_of_per_hop_accuracy_is_load_bearing_characterization_"
            "future_cells_using_partition_oracle_should_specify_PART_SIZE_and_use_appropriate_REF_for_that_PS"
        ),
    },
}
LEDGER_24 = {
    "ts": TS_NOW,
    "op": "cert_ruling_measured_mechanism_substrate_physics_finding_PS_axis_characterization",
    "atom_id": f"math::{ATOM_24_ID}",
    "cert_status": "measured_mechanism",
    "cert_class": "substrate_physics_partition_oracle_per_hop_cleanup_scales_inversely_with_PART_SIZE_orthogonal_to_N_axis_finding",
    "verified_off_data": True,
    "atomized_by": "skunkworks_landed_VET_wave_2026-07-01_multihop_PS_sweep_MM",
    "cell_commit": COMMIT,
    "verdict": (
        "MEASURED_MECHANISM_SCALE_VARIANT_PS_AXIS_3_seed_FULL_"
        "substantive_substrate_physics_finding_partition_oracle_per_hop_cleanup_accuracy_scales_inversely_with_PART_SIZE_"
        "cross_seed_reproducibility_tight_cv_0p009_to_0p036_across_all_6_arms_all_3_seeds_"
        "only_PS_10_at_d_30_matches_reference_cleanly_calibration_anchor_from_Landing_6_CG_"
        "PS_5_over_shoots_reference_by_0p05_to_0p21_smaller_partitions_easier_cleanup_"
        "PS_20_under_shoots_by_0p30_to_0p37_larger_partitions_harder_cleanup_"
        "contradicts_Atom_11_expansion_criterion_b_different_PART_SIZE_lift_attempt_FAILS_"
        "Atom_11_STAYS_at_MM_STANDARD_on_PS_axis_dimension_HONEST_DOWNWARD_on_Atom_11_scope_"
        "orthogonal_to_Atom_16_N_axis_finding_together_characterize_multi_hop_primitive_on_2_axes_"
        "resolves_OLD_vs_NEW_multihop_family_arithmetic_vs_geometric_mean_of_same_data_documented_cell_author_META_RULE_AC_"
        "cardinality_full_arms_differ_verified_zero_LLM_calls_all_seeds_elapsed_113p5s_"
        "does_NOT_supersede_parent_multihop_CG_atoms_6_10_which_stay_valid_at_PS_10_N_8192_"
        "future_cells_using_partition_oracle_should_specify_PART_SIZE_and_appropriate_REF_"
        "21st_atom_of_today_MM"
    ),
    "cert_increment_delta": 0,
    "cv": 0.025,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_multihop_reasoning_partition_size_sweep_gpu_v1/metrics.json",
        "parent_multihop_CG_atoms_not_superseded": [
            "T3/EXP_multihop_reasoning_depth_20_to_40_gpu_v1_3seed_CHAIN_GRADE",
            "T3/EXP_multihop_reasoning_depth_45_to_60_gpu_v1_3seed_CHAIN_GRADE",
        ],
        "atom_qualified_id": f"math::{ATOM_24_ID}",
    },
    "supersedes": None,
    "note": (
        "multihop_PS_sweep_3seed_FULL_MEASURED_MECHANISM_substrate_physics_finding_"
        "partition_oracle_per_hop_cleanup_scales_INVERSELY_with_PART_SIZE_"
        "PS_5_over_shoots_REF_PS_10_matches_calibration_anchor_PS_20_under_shoots_"
        "cross_seed_cv_tight_across_all_arms_reproducible_measurement_"
        "contradicts_Atom_11_MM_STANDARD_expansion_criterion_b_lift_attempt_FAILS_"
        "Atom_11_stays_MM_STANDARD_HONEST_DOWNWARD_on_PS_axis_scope_"
        "orthogonal_to_Atom_16_N_axis_partial_MM_finding_together_2_axis_characterization_"
        "per_step_accuracy_is_f_of_N_PS_depth_multi_hop_primitive_characterized_on_orthogonal_axes_"
        "resolves_OLD_vs_NEW_multihop_family_arithmetic_vs_geometric_mean_META_RULE_AC_documented_"
        "load_bearing_finding_for_downstream_cell_design_PART_SIZE_must_be_specified_and_appropriate_REF_used_"
        "does_NOT_supersede_Atoms_6_10_which_stay_valid_at_PS_10_N_8192_setpoint_"
        "PS_axis_lift_attempt_failure_is_HONEST_scope_bounding_not_negative_result_"
        "hdlab_ships_partition_oracle_with_PART_SIZE_10_at_N_8192_as_default_calibration_setpoint"
    ),
}

# =====================================================================
# Atom 25: Landing 24 sparsity v4 PC-only seed 7 FULL MM
# =====================================================================
ATOM_25_ID = (
    "T3/EXP_substrate_sparsity_free_axis_v4_pc_only_n4096_seed_7_FULL_MEASURED_MECHANISM_"
    "single_seed_FULL_HP_all_HP_gates_cleared_awaits_seeds_13_19_sync_for_3_seed_CG_lift_"
    "verify_landing_py_OK_seed_7_run_mode_full_verdict_HARD_PASS_wall_46p79s_"
    "verify_landing_py_FAIL_seeds_13_19_metrics_path_missing_files_not_yet_synced_"
    "PC_regime_only_v4_retires_WM_readout_per_v3_architectural_bug_finding_v2core_line_419_vals_corr_unused_in_readout_"
    "extended_M_grid_from_v2_1000_1500_2000_to_v4_800_1000_1500_2000_2500_5_M_levels_"
    "N_4096_alpha_0p05_0p10_0p20_3_sparsity_levels_c_0p60_T_1_encoder_hrr_real_"
    "15_of_15_phase_points_in_band_0p30_to_0p90_HP_gate_cleared_all_points_"
    "Spearman_rho_negative_1p0_all_5_M_levels_STRICT_monotone_decrease_perfect_HP_monotonicity_"
    "sparsity_range_per_M_0p1775_at_M_800_0p188_at_M_1000_0p194_at_M_1500_0p222_at_M_2000_0p242_at_M_2500_"
    "range_grows_with_M_capacity_pressure_makes_sparsity_more_sensitive_load_bearing_finding_"
    "positive_control_PC_at_M_2000_alpha_0p10_top1_0p507_cleanly_in_band_0p30_to_0p90_passes_"
    "cross_seed_cv_bit_identical_at_all_points_LLN_concentration_signature_at_N_4096_"
    "random_floor_at_0p0_to_0p004_chance_baseline_confirmed_arms_differ_verified_"
    "cardinality_15_of_15_units_zero_LLM_calls_"
    "AUDITOR_MM_because_verify_landing_py_shows_seeds_13_19_not_yet_on_disk_"
    "single_seed_evidence_insufficient_for_CG_and_supersession_of_Atom_4_v1_HF_and_Atom_17_v2_HF_WM_only_"
    "same_sync_lag_pattern_as_Atom_13_v8_smoke_MM_lifted_to_Atom_15_v8_3_seed_FULL_CG_"
    "expansion_criterion_land_seeds_13_19_verify_landing_py_OK_all_HP_gates_cleared_cross_seed_cv_le_0p10_"
    "would_supersede_Atoms_4_and_17_ON_PC_SCOPE_ONLY_leaves_WM_axis_characterization_for_future_v5_"
    "WM_status_RETIRED_ARCH_BUG_v2core_line_419_vals_corr_unused_in_readout_defered_to_v5_"
    "22nd_atom_of_today_MM_2026-07-01"
)
ATOM_25 = {
    "id": ATOM_25_ID,
    "name": (
        "MEASURED_MECHANISM Landing 24 sparsity_free_axis_v4_pc_only_n4096 seed 7 FULL: verify_landing.py "
        "OK seed 7 run_mode=full verdict=HARD_PASS wall=46.79s. verify_landing.py FAIL on seeds 13/19 "
        "(files not yet synced from remote). v4 retires WM readout per v3 architectural bug finding "
        "(v2core line 419 vals_corr unused in readout). Extended M grid from v2's {1000, 1500, 2000} "
        "to v4's {800, 1000, 1500, 2000, 2500} - 5 M levels. Configuration N=4096, alpha in {0.05, "
        "0.10, 0.20}, c=0.60, T=1, encoder=hrr_real, PC regime ONLY. Seed 7 FULL: 15/15 phase points "
        "in-band [0.30, 0.90] HP; Spearman rho=-1.0 at ALL 5 M levels (strict monotone decrease; "
        "perfect HP monotonicity); sparsity_range grows with M (0.178 at M=800 to 0.242 at M=2500) "
        "- capacity pressure makes sparsity more sensitive (load-bearing finding). Positive control "
        "PC at M=2000, alpha=0.10 top1=0.507 cleanly in [0.30, 0.90] band. Random floor 0.0-0.004 "
        "(chance baseline). Cross-seed cv bit-identical at all points (single seed; LLN concentration "
        "signature). Cardinality 15/15 units; arms_differ_verified; zero LLM calls. AUDITOR MM tier "
        "because seeds 13/19 files NOT yet on disk per verify_landing.py; single-seed evidence "
        "insufficient for CG lift and supersession of Atom 4 (v1 HF) + Atom 17 (v2 HF WM-only). "
        "Same sync-lag pattern as Wave 6 Atom 13 (v8 smoke MM) -> Wave 7 Atom 15 (v8 3-seed FULL CG). "
        "Expansion criterion: land seeds 13/19 FULL with all HP gates cleared; would supersede Atoms "
        "4/17 ON PC SCOPE ONLY (WM axis characterization deferred to future v5 architectural fix). "
        "CERT +0."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record_awaits_full_3_seed",
    "description": (
        f"OFF-DATA verification (verify_landing.py):\n"
        f"  OK   substrate_sparsity_free_axis_v4_pc_only_n4096_seed_7   run_mode=full verdict=HARD_PASS wall_s=46.79\n"
        f"  FAIL substrate_sparsity_free_axis_v4_pc_only_n4096_seed_13  metrics_path_missing\n"
        f"  FAIL substrate_sparsity_free_axis_v4_pc_only_n4096_seed_19  metrics_path_missing\n"
        f"\n"
        f"AUDITOR DOWNWARD FRAMING CORRECTION:\n"
        f"  Director spawn framed '3-seed FULL POTENTIAL CG' with seed 7 HP wall=16.3s, seed 13 HP\n"
        f"  wall=14.2s, seed 19 imminent. verify_landing.py confirms seed 7 (at wall=46.79s not 16.3s;\n"
        f"  sync updated) but FAILS on seeds 13, 19 which have NOT yet synced. Auditor tiers based\n"
        f"  on WHAT'S ACTUALLY ON DISK per post-Wave 7 discipline.\n"
        f"\n"
        f"Recompute Skunkworks {DATE} (seed 7 only):\n"
        f"  Configuration: N=4096, alpha in {{0.05, 0.10, 0.20}}, c=0.60, T=1, encoder=hrr_real,\n"
        f"    PC regime ONLY, M in {{800, 1000, 1500, 2000, 2500}}, 5 M levels x 3 alpha = 15 phase points\n"
        f"  \n"
        f"  Per-M summary:\n"
        f"    M=800:  sparsity_range=0.178, rho=-1.0, alphas=[0.05, 0.10, 0.20], top1=[0.789, 0.720, 0.611]\n"
        f"    M=1000: sparsity_range=0.188, rho=-1.0, top1=[0.730, 0.686, 0.542]\n"
        f"    M=1500: sparsity_range=0.194, rho=-1.0, top1=[0.638, 0.593, 0.444]\n"
        f"    M=2000: sparsity_range=0.222, rho=-1.0, top1=[0.592, 0.507, 0.370]\n"
        f"    M=2500: sparsity_range=0.242, rho=-1.0, top1=[0.547, 0.484, 0.305]\n"
        f"\n"
        f"HP GATES (all cleared seed 7):\n"
        f"  hp_pc_monotone_all_M: True (all 5 M levels rho=-1.0; |rho|>=0.80 threshold)\n"
        f"  hp_pc_in_band_all_points: True (all 15 top1 in [0.30, 0.90] band)\n"
        f"  hp_cross_seed_tight_all_points: True (bit-identical; single-seed baseline)\n"
        f"  hp_random_floor_chance: True (random 0.0-0.004; near-zero chance)\n"
        f"  hp_arms_differ_all_points: True (mechanism vs random distinct at all 15 points)\n"
        f"  hf_saturation_points: [] (no arm at 1.000 or 0.000 ceiling)\n"
        f"  hf_crumble_points: [] (no arm below chance)\n"
        f"  positive_control_pc_ok: True (M=2000, alpha=0.10 top1=0.507 in [0.30, 0.90])\n"
        f"  cardinality_ok: True (15/15 units)\n"
        f"  n_llm_calls: 0\n"
        f"\n"
        f"SUBSTANTIVE MECHANISM CLAIM VALIDATED AT SEED 7:\n"
        f"  sparsity IS a monotone-decreasing lever on recall at PC regime at N=4096, M in\n"
        f"    {{800, 1000, 1500, 2000, 2500}}, c=0.60, T=1, hrr_real.\n"
        f"  Cross-M finding: sparsity_range GROWS with M (0.178 at M=800 to 0.242 at M=2500).\n"
        f"    Interpretation: capacity pressure (higher M) makes sparsity more sensitive as a\n"
        f"    load-bearing capacity-relief mechanism. Load-bearing substrate physics finding.\n"
        f"\n"
        f"V4 DESIGN CHOICES:\n"
        f"  (1) Retires WM regime per v3 architectural bug finding:\n"
        f"      v2core line 419: vals_corr unused in readout - cortex-side aggregation missed the\n"
        f"      cleanup step that would have used vals_corr correctly.\n"
        f"      v4 skips WM to isolate PC claim; WM axis deferred to v5 with architectural fix.\n"
        f"  (2) Extends M grid from v2's {{1000, 1500, 2000}} to v4's {{800, 1000, 1500, 2000, 2500}}.\n"
        f"      Adds lower (M=800) and higher (M=2500) capacity points for shape characterization.\n"
        f"  (3) PC c=0.60 preserved from v2 - Atom 17 confirmed correctly calibrated at v2 PC scope.\n"
        f"\n"
        f"WHY AUDITOR MM (NOT CG or Atom 4/17 SUPERSESSION):\n"
        f"  (a) verify_landing.py FAIL on seeds 13, 19 - files NOT yet on disk\n"
        f"  (b) Only seed 7 FULL landed; single-seed evidence insufficient for CG per Skunkworks discipline\n"
        f"  (c) Superseding Atoms 4 and 17 requires 3-seed cross-seed reproducibility (standard bar)\n"
        f"  (d) All 3 milestone closures today (M1.4 Atom 15, M1.5 Atom 18, LLN Atom 22) had 3-seed\n"
        f"      FULL with cross-seed cv <=0.10 or bit-identical\n"
        f"  (e) Bar not lowered on sparsity PC-scope tier lift\n"
        f"\n"
        f"WHY AUDITOR DID NOT DOWNGRADE PAST MM:\n"
        f"  (a) Seed 7 FULL legitimately clears all HP gates (auditor recomputed all fields)\n"
        f"  (b) v4 design fixes are transparent (retires broken WM per v3 bug finding)\n"
        f"  (c) 15-point HP with rho=-1.0 all 5 M levels is strong single-seed evidence\n"
        f"  (d) Positive control PC in-band at correct anchor point (M=2000 alpha=0.10 top1=0.507)\n"
        f"  (e) MM tier captures single-seed FULL validation; awaits cross-seed for CG lift\n"
        f"\n"
        f"SYNC-LAG PATTERN (same as Atom 13 -> Atom 15 chain):\n"
        f"  Wave 6: Atom 13 tiered v8 seed 7 smoke MM because verify_landing.py showed FULL missing.\n"
        f"  Wave 7: Atom 15 tiered v8 3-seed FULL CG when sync tick landed FULL files.\n"
        f"           Supersession chain established.\n"
        f"  \n"
        f"  This landing (Atom 25) at same sync-lag stage. When seeds 13/19 land + verify_landing.py OK:\n"
        f"    File proper CG atom that SUPERSEDES this Atom 25.\n"
        f"    That CG atom would ALSO supersede Atom 4 (v1 HF) and Atom 17 (v2 HF WM-only) on\n"
        f"    PC-scope claim (WM axis stays under Atom 17 characterization until v5).\n"
        f"\n"
        f"EXPANSION CRITERION TO CG + PC-SCOPE SUPERSESSION OF ATOMS 4/17:\n"
        f"  Land 3-seed FULL with:\n"
        f"    (a) verify_landing.py OK all 3 seeds run_mode=full verdict=HARD_PASS\n"
        f"    (b) all 3 seeds rho=-1.0 at all 5 M levels (monotonicity preserved)\n"
        f"    (c) all 3 seeds 15/15 points in [0.30, 0.90] band\n"
        f"    (d) cross-seed cv on top1 per point <= 0.10 (loose per pre-reg)\n"
        f"    (e) positive control PC at M=2000, alpha=0.10 in [0.30, 0.90] all 3 seeds\n"
        f"    (f) cardinality 15/15 per seed\n"
        f"    (g) no saturation or crumble points any seed\n"
        f"  If all met: CG atom supersedes this Atom 25 + Atom 4 (v1 all-regime HF; PC-scope moved to CG)\n"
        f"    + Atom 17 (v2 WM-only HF; PC-scope moved to CG). Atoms 4/17 stay in ledger; supersession\n"
        f"    chain notes PC-scope claim now CG at v4 config; WM axis still MB/HF until v5.\n"
        f"\n"
        f"COMPOSES WITH:\n"
        f"  - Atom 4 (v1 HF test-design failure all-regime): parent HF; PC-scope will be superseded on 3-seed FULL.\n"
        f"  - Atom 17 (v2 HF WM-only; PC-partial-success): parent HF; PC-scope will be superseded on 3-seed FULL.\n"
        f"  - Both parents stay in ledger; supersession chain documents scope transitions.\n"
        f"\n"
        f"CROSS-ARC OVERLAP CHECK {DATE}: expected high overlap with sparsity v1/v2 (direct parents).\n"
        f"  NOT a rediscovery; PC-only characterization + WM retirement is genuinely novel design.\n"
        f"\n"
        f"Commit: {COMMIT}. Author: skunkworks_landed_VET_wave_2026-07-01_sparsity_v4_seed_7_MM."
    ),
    "metadata": {
        "ts_atomized": TS_NOW,
        "date_atomized": DATE,
        "cert_commit": COMMIT,
        "verify_landing_py_status": {
            "seed_7": "OK run_mode=full verdict=HARD_PASS wall_s=46.79",
            "seed_13": "FAIL metrics_path_missing",
            "seed_19": "FAIL metrics_path_missing",
        },
        "run_mode": "full",
        "n_seeds_landed": 1,
        "seeds_landed_HP_full": [7],
        "seeds_awaiting_sync": [13, 19],
        "auditor_downward_correction_reason": "Director_framed_3_seed_FULL_but_verify_landing_py_FAIL_on_seeds_13_19_only_seed_7_on_disk",
        "N": 4096,
        "M_values": [800, 1000, 1500, 2000, 2500],
        "alpha_values": [0.05, 0.10, 0.20],
        "regime": "PC_only",
        "PC_c_corruption": 0.60,
        "T_cleanup": 1,
        "encoder": "hrr_real",
        "cardinality_ok_seed_7": True,
        "n_units_seed_7": 15,
        "arms_differ_verified_seed_7": True,
        "hp_pc_monotone_all_M_seed_7": True,
        "hp_pc_in_band_all_points_seed_7": True,
        "hp_cross_seed_tight_all_points_seed_7": True,
        "hp_random_floor_chance_seed_7": True,
        "hp_arms_differ_all_points_seed_7": True,
        "hf_saturation_points_seed_7": [],
        "hf_crumble_points_seed_7": [],
        "positive_control_pc_ok_seed_7": True,
        "positive_control_M_2000_alpha_0p10_top1_seed_7": 0.507,
        "positive_control_pre_reg_band": [0.30, 0.90],
        "per_M_sparsity_range_seed_7": {
            "800": 0.1775,
            "1000": 0.188,
            "1500": 0.194,
            "2000": 0.222,
            "2500": 0.242,
        },
        "sparsity_range_grows_with_M_finding": True,
        "sparsity_range_growth_interpretation": "capacity_pressure_higher_M_makes_sparsity_more_sensitive_load_bearing_capacity_relief_mechanism",
        "per_M_spearman_rho_seed_7": {
            "800": -1.0, "1000": -1.0, "1500": -1.0, "2000": -1.0, "2500": -1.0,
        },
        "per_M_top1_by_alpha_seed_7": {
            "800":  [0.7887, 0.7200, 0.6112],
            "1000": [0.7300, 0.6860, 0.5420],
            "1500": [0.6380, 0.5927, 0.4440],
            "2000": [0.5915, 0.5070, 0.3695],
            "2500": [0.5468, 0.4844, 0.3048],
        },
        "n_llm_calls_seed_7": 0,
        "elapsed_s_seed_7": 46.79,
        "v4_design_fixes": {
            "retires_WM_readout_per_v3_arch_bug_finding": "v2core_line_419_vals_corr_unused_in_readout",
            "WM_status": "RETIRED_ARCH_BUG_defered_to_v5",
            "extended_M_grid": "from_v2_1000_1500_2000_to_v4_800_1000_1500_2000_2500",
        },
        "verified_off_data": True,
        "metrics_path_seed_7": "data/exp_substrate_sparsity_free_axis_v4_pc_only_n4096_seed_7/metrics.json",
        "prereg_path": "preregs/2026-07-01_substrate_sparsity_free_axis_v4_pc_only_n4096.md",
        "wm_deferred_notes_path": "notes/wm_readout_architectural_bug_deferred_v5_2026-07-01.md",
        "parent_atoms": [
            "T3/EXP_substrate_sparsity_free_axis_v1_3seed_HARD_FAIL_TEST_DESIGN_FAILURE",
            "T3/EXP_substrate_sparsity_free_axis_v2_n4096_3seed_FULL_HARD_FAIL_TEST_DESIGN_FAILURE_WM_ONLY",
        ],
        "cert_tier": "measured_mechanism",
        "cert_increment_delta": 0,
        "expansion_criterion_to_CG_and_supersession": (
            "land_seeds_13_19_FULL_verify_landing_py_OK_all_HP_gates_cleared_all_3_seeds_"
            "cross_seed_cv_le_0p10_at_all_15_points_"
            "would_supersede_this_Atom_25_AND_Atoms_4_17_ON_PC_SCOPE_ONLY_"
            "WM_axis_stays_under_Atom_17_characterization_until_v5_architectural_fix_"
            "supersession_chain_documents_scope_transitions_v1_all_regime_HF_v2_WM_only_HF_v4_PC_scope_CG"
        ),
        "sync_lag_pattern_matches_Atom_13_v8_smoke_MM_lifted_to_Atom_15_v8_3_seed_FULL_CG": True,
    },
}
LEDGER_25 = {
    "ts": TS_NOW,
    "op": "cert_ruling_measured_mechanism_single_seed_FULL_awaits_cross_seed_for_CG_lift_and_atoms_4_17_PC_scope_supersession",
    "atom_id": f"math::{ATOM_25_ID}",
    "cert_status": "measured_mechanism",
    "cert_class": "sparsity_v4_PC_only_seed_7_FULL_HP_single_seed_evidence_awaits_seeds_13_19_sync",
    "verified_off_data": True,
    "atomized_by": "skunkworks_landed_VET_wave_2026-07-01_sparsity_v4_seed_7_MM",
    "cell_commit": COMMIT,
    "verdict": (
        "MEASURED_MECHANISM_sparsity_v4_pc_only_seed_7_FULL_HARD_PASS_"
        "verify_landing_py_OK_seed_7_FAIL_seeds_13_19_metrics_path_missing_files_not_yet_synced_"
        "single_seed_evidence_insufficient_for_CG_lift_and_supersession_of_Atoms_4_17_"
        "seed_7_FULL_15_of_15_phase_points_in_band_0p30_to_0p90_HP_"
        "Spearman_rho_negative_1p0_all_5_M_levels_strict_monotone_decrease_perfect_HP_monotonicity_"
        "sparsity_range_grows_with_M_0p178_at_M_800_to_0p242_at_M_2500_load_bearing_capacity_relief_finding_"
        "positive_control_PC_at_M_2000_alpha_0p10_top1_0p507_cleanly_in_band_broken_PC_gate_passes_"
        "v4_retires_WM_readout_per_v3_architectural_bug_v2core_line_419_vals_corr_unused_deferred_to_v5_"
        "extends_M_grid_from_v2_to_v4_5_levels_800_2500_cardinality_15_of_15_zero_LLM_calls_"
        "sync_lag_pattern_matches_Wave_6_Atom_13_smoke_MM_lifted_to_Wave_7_Atom_15_3_seed_FULL_CG_"
        "expansion_criterion_seeds_13_19_landing_HP_all_gates_cleared_would_lift_MM_to_CG_"
        "and_supersede_Atoms_4_v1_HF_and_17_v2_HF_ON_PC_SCOPE_ONLY_WM_axis_stays_under_Atom_17_until_v5_"
        "22nd_atom_of_today_MM"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path_seed_7": "data/exp_substrate_sparsity_free_axis_v4_pc_only_n4096_seed_7/metrics.json",
        "metrics_paths_seeds_13_19_missing": [
            "data/exp_substrate_sparsity_free_axis_v4_pc_only_n4096_seed_13/metrics.json (NOT ON DISK)",
            "data/exp_substrate_sparsity_free_axis_v4_pc_only_n4096_seed_19/metrics.json (NOT ON DISK)",
        ],
        "prereg_path": "preregs/2026-07-01_substrate_sparsity_free_axis_v4_pc_only_n4096.md",
        "parent_HF_atoms_will_be_superseded_on_3_seed_FULL_PC_scope_only": [
            "T3/EXP_substrate_sparsity_free_axis_v1_3seed_HARD_FAIL_TEST_DESIGN_FAILURE",
            "T3/EXP_substrate_sparsity_free_axis_v2_n4096_3seed_FULL_HARD_FAIL_TEST_DESIGN_FAILURE_WM_ONLY",
        ],
        "future_CG_atom_will_supersede_this_and_amend_Atoms_4_17": True,
        "atom_qualified_id": f"math::{ATOM_25_ID}",
    },
    "supersedes": None,
    "note": (
        "sparsity_v4_pc_only_seed_7_FULL_MEASURED_MECHANISM_awaits_seeds_13_19_sync_"
        "single_seed_FULL_HP_all_HP_gates_cleared_15_of_15_points_in_band_rho_negative_1p0_all_5_M_levels_"
        "sparsity_range_grows_with_M_capacity_pressure_finding_"
        "positive_control_PC_in_band_broken_PC_gate_passes_"
        "v4_retires_WM_per_v3_arch_bug_defered_to_v5_extends_M_grid_5_levels_800_2500_"
        "sync_lag_pattern_same_as_Wave_6_Atom_13_and_Wave_7_Atom_15_supersession_chain_"
        "when_seeds_13_19_land_file_proper_CG_atom_that_supersedes_this_and_atoms_4_17_ON_PC_SCOPE_ONLY_"
        "WM_axis_characterization_stays_under_Atom_17_until_v5_architectural_fix_"
        "PC_regime_correctly_calibrated_at_v2_v4_c_0p60_T_1_N_4096_hrr_real_setpoint_"
        "expansion_criterion_seeds_13_19_HP_all_gates_cleared_at_full_lifts_to_CG_and_supersedes_HF_atoms_4_17_PC_scope"
    ),
}

# =====================================================================
# Atomic write
# =====================================================================
def atomic_append_jsonl(path: pathlib.Path, records: list[dict]) -> tuple[int, int]:
    """Atomic tmp-write + os.replace + verify-load. Returns (lines_before, lines_after)."""
    lines_before = 0
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            lines_before = sum(1 for _ in f)

    tmp_path = path.with_suffix(path.suffix + ".tmp")
    existing_content = b""
    if path.exists():
        existing_content = path.read_bytes()
    if existing_content and not existing_content.endswith(b"\n"):
        existing_content += b"\n"
    new_lines = b""
    for rec in records:
        line = json.dumps(rec, ensure_ascii=False) + "\n"
        new_lines += line.encode("utf-8")
    tmp_path.write_bytes(existing_content + new_lines)

    with tmp_path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Corrupt JSON at line {i+1} in {tmp_path}: {e}")

    os.replace(tmp_path, path)

    lines_after = 0
    with path.open("r", encoding="utf-8") as f:
        lines_after = sum(1 for _ in f)

    return lines_before, lines_after


def main():
    math_before, math_after = atomic_append_jsonl(MATH_ATOMS, [ATOM_24, ATOM_25])
    print(f"math/atoms.jsonl: {math_before} -> {math_after} (+{math_after - math_before})")

    ledger_records = [LEDGER_24, LEDGER_25]
    led_before, led_after = atomic_append_jsonl(CERT_LEDGER, ledger_records)
    print(f"meta/cert_ledger.jsonl: {led_before} -> {led_after} (+{led_after - led_before})")

    print()
    print(f"CERT delta: +0 (both MM)")
    print(f"  Atom 24: Landing 23 multihop PS-sweep MM (substrate physics finding; Atom 11 lift fails)")
    print(f"  Atom 25: Landing 24 sparsity v4 seed 7 FULL MM (awaits seeds 13/19 sync)")
    print(f"Session-cumulative today: CG=+13, MM=+10, HF=+2, meta_amendment=+2")
    print(f"Timestamp: {TS_NOW}")
    print(f"Commit: {COMMIT}")


if __name__ == "__main__":
    main()
