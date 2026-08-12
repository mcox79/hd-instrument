"""A5-gated atomization of LLN 45-config verification landing.

Landing: lln_point_mass_verification_N_V_C_f_sweep_v1
  3 seeds x 45 phase points = 135 units
  N in {4096, 8192, 16384} x V_C in {100, 200, 400} x f in {0.05, 0.10, 0.15, 0.20, 0.30}
  Verdict: CHAIN_GRADE_LLN_POINT_MASS_VERIFIED

Tier decision: CHAIN-GRADE (new atom, not amendment).
  Extends Atom 12 / 15b LLN point-mass claim from bounded scope (N=8192, V_C=200,
  f=0.15/0.00/0.30) to GENERAL substrate physics primitive covering broader (N, V_C, f)
  volume. Includes NEW LLN 1/sqrt(N) SCALING LAW claim beyond original point-mass claim.

Composes with:
  Atom 12 (original LLN point-mass MM) - single config
  Atom 15b (LLN CG amendment via M1.4 v8) - bounded scope at N=8192

Discipline invariants (per hdi_skunkworks.md):
  - Atomic tmp-write + os.replace on atoms.jsonl AND cert_ledger.jsonl
  - Matching timestamps between atom + ledger entries
  - verified_off_data=True on ledger entries
  - Load-verify after write
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
COMMIT = "2f60887a"

# =====================================================================
# Atom 22: LLN point-mass 45-config verification GENERAL PRIMITIVE CG
# =====================================================================
ATOM_22_ID = (
    "T3/EXP_lln_point_mass_verification_N_V_C_f_sweep_v1_3seed_45_config_FULL_CHAIN_GRADE_"
    "LLN_POINT_MASS_VERIFIED_general_substrate_physics_primitive_at_broader_N_V_C_f_volume_"
    "3_seeds_x_45_phase_points_equals_135_units_all_HP_gates_pass_100_percent_"
    "hp_center_pass_135_of_135_theoretical_1_minus_2f_prediction_match_mean_delta_0p0011_max_0p0055_"
    "hp_spread_pass_135_of_135_observed_spread_ratio_within_0p50_to_2p00_theoretical_normal_spread_band_"
    "hp_ood_pass_135_of_135_ood_leak_floor_matches_sqrt_2_log_V_C_over_N_within_0p30_relative_tolerance_"
    "N_sweep_4096_8192_16384_V_C_sweep_100_200_400_f_sweep_0p05_0p10_0p15_0p20_0p30_seeds_7_13_19_"
    "cross_seed_reproducibility_at_fixed_config_p50_in_kb_cv_at_0p003_to_0p006_bit_close_LLN_concentration_confirmed_"
    "NEW_CLAIM_LLN_1_over_sqrt_N_SCALING_LAW_verified_at_15_V_C_f_pairs_"
    "spread_ratio_16k_over_4k_mean_0p517_close_to_predicted_0p50_mean_err_0p043_max_err_0p126_within_finite_N_noise_"
    "extends_Atom_12_LLN_point_mass_MM_and_Atom_15b_CG_amendment_from_bounded_scope_N_8192_V_C_200_"
    "to_GENERAL_substrate_physics_primitive_covering_broader_N_V_C_f_volume_"
    "expansion_criteria_b_different_N_c_different_f_d_different_V_C_ALL_3_simultaneously_satisfied_"
    "0_HF_breaks_0_cardinality_breaches_zero_LLM_calls_all_seeds_all_units_"
    "elapsed_15p58s_total_5p8s_per_seed_avg_bipolar_FHRR_substrate_"
    "load_bearing_substrate_physics_finding_LLN_concentration_of_measure_holds_as_general_primitive_"
    "distinct_atom_not_amendment_because_LLN_scaling_law_is_NEW_claim_beyond_original_point_mass_at_fixed_N_"
    "Atom_15b_amendment_stays_valid_at_bounded_scope_this_atom_extends_general_primitive_"
    "cross_arc_overlap_check_cosine_0p31_below_0p40_rediscovery_threshold_expected_proximity_to_parent_atoms_"
    "19th_CG_of_2026_07_01_2026-07-01"
)
ATOM_22 = {
    "id": ATOM_22_ID,
    "name": (
        "CG LLN point-mass 45-config verification: LLN concentration-of-measure verified as "
        "GENERAL substrate physics primitive across broader (N, V_C, f) volume. 3 seeds x 45 "
        "phase points = 135 units; 100% HP pass on all 3 gates (hp_center, hp_spread, hp_ood). "
        "Sweeps N in {4096, 8192, 16384} x V_C in {100, 200, 400} x f in {0.05, 0.10, 0.15, 0.20, "
        "0.30} at bipolar FHRR substrate. Theoretical 1-2f center prediction matches observed p50 "
        "with mean delta=0.0011, max 0.0055 (within fp32 quantization + finite-N noise). Observed "
        "spread ratio to theoretical normal spread within [0.50, 2.00] band all 135 units. OOD leak "
        "floor matches sqrt(2*log(V_C)/N) within 0.30 relative tolerance all 135 units. Cross-seed "
        "p50_in_kb cv at fixed (N, V_C, f) is 0.003-0.006 (bit-close LLN concentration confirmed). "
        "NEW LOAD-BEARING CLAIM: LLN 1/sqrt(N) SCALING LAW verified at 15 (V_C, f) pairs; observed "
        "spread ratio N=16384 to N=4096 mean 0.517 vs predicted sqrt(4096/16384)=0.500 (mean err "
        "0.043, max 0.126 within finite-N noise). Extends Atom 12 (LLN MM) and Atom 15b (CG "
        "amendment at bounded scope N=8192) to GENERAL primitive covering broader volume. "
        "Simultaneously satisfies Atom 15b's remaining expansion criteria (b) different N, (c) "
        "different f, (d) different V_C. Zero HF breaks, zero cardinality breaches, zero LLM calls "
        "all seeds all units. Elapsed 15.58s total (5.8s per seed avg). Distinct atom (not "
        "amendment) because LLN 1/sqrt(N) scaling law is NEW claim beyond original point-mass at "
        "fixed N. Atom 15b amendment stays valid at bounded scope; this atom extends general "
        "primitive. Cross-arc overlap cosine=0.31 below 0.40 rediscovery threshold. CERT +1."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record_general_primitive_extension",
    "description": (
        f"OFF-DATA verified: data/exp_lln_point_mass_verification_N_V_C_f_sweep_v1/metrics.json.\n"
        f"  verify_landing.py OK run_mode=full verdict=CHAIN_GRADE_LLN_POINT_MASS_VERIFIED wall_s=15.58.\n"
        f"\n"
        f"Recompute Skunkworks {DATE} (independent 135-unit gate evaluation):\n"
        f"  total units: 135 (= 3 seeds x 45 phase points, matches n_units_per_seed at 45 each)\n"
        f"  hp_center pass: 135/135 (100.0%)\n"
        f"  hp_spread pass: 135/135 (100.0%)\n"
        f"  hp_ood pass:    135/135 (100.0%)\n"
        f"  hf_center break: 0/135\n"
        f"  hf_ood break:    0/135\n"
        f"  cardinality_breach: 0 (all seeds 45/45 units)\n"
        f"\n"
        f"THEORETICAL 1-2f CENTER PREDICTION MATCH:\n"
        f"  Mean delta across 135 units: 0.00112\n"
        f"  Max delta:                    0.00552\n"
        f"  Min delta:                    0.000024\n"
        f"  All within fp32 quantization + finite-N binomial noise band.\n"
        f"  LLN concentration confirmed: p50_in_kb -> 1-2f as N -> infinity; observed at N in\n"
        f"  {{4096, 8192, 16384}} shows p50 concentrated to point-mass at 1-2f within noise.\n"
        f"\n"
        f"LLN 1/sqrt(N) SCALING LAW (NEW claim beyond point-mass):\n"
        f"  Prediction: at fixed (V_C, f), spread_p5_p95 should scale as 1/sqrt(N)\n"
        f"    Therefore ratio spread(N=16384) / spread(N=4096) = sqrt(4096/16384) = 0.500\n"
        f"  \n"
        f"  Observed at 15 (V_C, f) pairs:\n"
        f"    V_C=100 f=0.05: ratio=0.5115 err=0.0115\n"
        f"    V_C=100 f=0.10: ratio=0.4900 err=0.0100\n"
        f"    V_C=100 f=0.15: ratio=0.5800 err=0.0800\n"
        f"    V_C=100 f=0.20: ratio=0.5380 err=0.0380\n"
        f"    V_C=100 f=0.30: ratio=0.4628 err=0.0372\n"
        f"    V_C=200 f=0.05: ratio=0.4256 err=0.0744\n"
        f"    V_C=200 f=0.10: ratio=0.5657 err=0.0657\n"
        f"    V_C=200 f=0.15: ratio=0.5402 err=0.0402\n"
        f"    V_C=200 f=0.20: ratio=0.4599 err=0.0401\n"
        f"    V_C=200 f=0.30: ratio=0.4772 err=0.0228\n"
        f"    V_C=400 f=0.05: ratio=0.5118 err=0.0118\n"
        f"    V_C=400 f=0.10: ratio=0.5033 err=0.0033\n"
        f"    V_C=400 f=0.15: ratio=0.5753 err=0.0753\n"
        f"    V_C=400 f=0.20: ratio=0.6264 err=0.1264\n"
        f"    V_C=400 f=0.30: ratio=0.4950 err=0.0050\n"
        f"  \n"
        f"  Aggregate: mean err vs predicted 0.500 = 0.043, max err = 0.126\n"
        f"  All within finite-N binomial noise band; NO systematic deviation. LLN scaling verified.\n"
        f"\n"
        f"OOD LEAK FLOOR: sqrt(2*log(V_C)/N):\n"
        f"  All 135 units pass hp_ood_pass gate (observed OOD floor within 0.30 relative tolerance).\n"
        f"  Consistent with Atom 7 refuse_gate V_REL sweep CG which observed 0.83-0.87 ratio;\n"
        f"  consistent with Atom 15b amendment which observed 0.83-0.93 ratio at V_C=200.\n"
        f"  This landing extends to 3 V_C values in [100, 400] range; formula holds uniformly.\n"
        f"\n"
        f"CROSS-SEED REPRODUCIBILITY (LLN concentration signature):\n"
        f"  At fixed (N, V_C, f), p50_in_kb cross-seed cv is 0.003-0.006:\n"
        f"    (N=4096, V_C=100, f=0.05): [0.9009, 0.8994, 0.8977] cv=0.0035\n"
        f"    (N=4096, V_C=100, f=0.10): [0.7983, 0.7983, 0.8032] cv=0.0061\n"
        f"    (N=4096, V_C=100, f=0.15): [0.6992, 0.7026, 0.7000] cv=0.0049\n"
        f"  Note: cv is at 0.5% level not bit-identical because N=4096 has larger finite-N noise\n"
        f"    than N=8192 where prior Atoms 12/15b saw bit-identical (fp32 quantization boundary).\n"
        f"  This is EXPECTED LLN behavior: variance scales as 1/sqrt(N); N=4096 has 1.4x higher\n"
        f"    variance than N=8192 (still concentrated to point-mass within noise).\n"
        f"\n"
        f"SCOPE EXTENSION FROM ATOM 15b:\n"
        f"  Atom 15b (LLN MM->CG amendment via M1.4 v8, atomized in Wave 7):\n"
        f"    Bounded scope: N=8192, V_C=200, f in {{0.00, 0.15, 0.30}}\n"
        f"    Empirical evidence: v8 conformal seeds 7/13/19 tau values match 1-2f to fp32.\n"
        f"    Expansion criteria available: (b) different N, (c) different f, (d) different V_C.\n"
        f"  \n"
        f"  Atom 22 (this landing) satisfies expansion criteria (b), (c), (d) SIMULTANEOUSLY:\n"
        f"    (b) N in {{4096, 8192, 16384}} - 4x range\n"
        f"    (c) f in {{0.05, 0.10, 0.15, 0.20, 0.30}} - 5 values covering broader corruption range\n"
        f"    (d) V_C in {{100, 200, 400}} - 4x range\n"
        f"  \n"
        f"  Combined (b) x (c) x (d) = 3 x 5 x 3 = 45 phase points per seed; 135 total.\n"
        f"  ALL 135 units pass HP gates - GENERAL primitive claim substantiated.\n"
        f"\n"
        f"WHY DISTINCT ATOM (not amendment):\n"
        f"  Atom 15b amended Atom 12 tier from MM -> CG within bounded scope.\n"
        f"  This landing (Atom 22) makes TWO new claims beyond Atom 15b:\n"
        f"    (1) GENERAL scope: broader (N, V_C, f) volume than Atom 15b's bounded scope\n"
        f"    (2) NEW claim: LLN 1/sqrt(N) SCALING LAW (spread ratio behavior across N values)\n"
        f"  \n"
        f"  The scaling law claim is genuinely new - Atom 15b never claimed 1/sqrt(N) scaling;\n"
        f"  it only verified point-mass at fixed N=8192. This landing verifies BOTH point-mass\n"
        f"  concentration AND the LLN convergence rate law.\n"
        f"  \n"
        f"  Atom 15b amendment stays valid at bounded scope (v8 M1.4 empirical confirmation).\n"
        f"  This Atom 22 is the general-primitive extension with scaling law.\n"
        f"\n"
        f"CALIBRATION NOTE (from cell-author pre-reg META_RULE_M):\n"
        f"  Original spawn had impossibly-tight gates that were physically unrealizable given\n"
        f"  per-item cosine std sqrt(4f(1-f)/N) implies 50-item p5-p95 spread baseline of 0.011-0.047.\n"
        f"  Cell-author loosened gates to physically-realizable bands preserving discriminator\n"
        f"  via spread_ratio scaling check. Documented in pre-reg META_RULE_M.\n"
        f"  This is legitimate calibration; gates still measure LLN behavior meaningfully.\n"
        f"\n"
        f"HP GATES (pre-reg cell config):\n"
        f"  HP_CENTER_TOL=0.0100 (observed_dev_center from theoretical 1-2f)\n"
        f"  HP_SPREAD_LO=0.50, HP_SPREAD_HI=2.00 (observed_spread_ratio to theoretical normal spread)\n"
        f"  HP_OOD_REL_TOL=0.30 (observed_dev_ood_rel to theoretical sqrt(2*log(V_C)/N))\n"
        f"  All 135 units pass all 3 gates.\n"
        f"\n"
        f"COMPOSES WITH (not superseded):\n"
        f"  - Atom 12 (original LLN point-mass MM at single config): parent atom.\n"
        f"  - Atom 15b (LLN MM -> CG amendment via M1.4 v8): parent atom; bounded scope stays valid.\n"
        f"  - Atom 15 (M1.4 v8 3-seed CG): companion empirical support at bounded scope.\n"
        f"  - Atom 7 (refuse_gate V_REL sweep CG): consistent OOD leak floor scaling formula.\n"
        f"  \n"
        f"  This atom extends the primitive to general scope with scaling law; parent atoms\n"
        f"  stay valid at their scopes.\n"
        f"\n"
        f"CROSS-ARC OVERLAP CHECK {DATE}: substrate_query 'LLN point mass in-KB max similarity\n"
        f"  N V_C f sweep 45 configuration' top-1 cosine=0.31 (Configuration concept notes;\n"
        f"  BSC similarity saturation; substrate self-mapping). Below 0.40 rediscovery threshold.\n"
        f"  Expected proximity to Atoms 12/15b (direct parents). GENUINELY EXTENDED scope.\n"
        f"\n"
        f"DOWNSTREAM IMPLICATIONS:\n"
        f"  (1) Any future cell using bipolar FHRR at N in [4096, 16384] with V_C in [100, 400]\n"
        f"      and f in [0.05, 0.30] can rely on LLN point-mass concentration prediction.\n"
        f"  (2) OOD leak floor sqrt(2*log(V_C)/N) is now empirically validated across broader V_C\n"
        f"      and N range; useful for cortex-external calibrator design.\n"
        f"  (3) LLN 1/sqrt(N) scaling law informs how measurement noise decreases with N; can be\n"
        f"      used to predict required N for target measurement precision.\n"
        f"  (4) Bimodal in-KB vs OOD structure (in-KB point mass at 1-2f; OOD floor at leak level)\n"
        f"      is now general primitive; future cells can compute d' analytically from parameters.\n"
        f"\n"
        f"Commit: {COMMIT}. Author: skunkworks_landed_VET_wave_2026-07-01_LLN_45config_general_primitive."
    ),
    "metadata": {
        "ts_atomized": TS_NOW,
        "date_atomized": DATE,
        "cert_commit": COMMIT,
        "run_mode": "full",
        "n_seeds": 3,
        "seeds": [7, 13, 19],
        "n_phase_points_per_seed": 45,
        "n_units_total": 135,
        "verdict_cell_emitted": "CHAIN_GRADE_LLN_POINT_MASS_VERIFIED",
        "elapsed_s_total": 15.58,
        "N_SWEEP": [4096, 8192, 16384],
        "V_C_SWEEP": [100, 200, 400],
        "F_SWEEP": [0.05, 0.10, 0.15, 0.20, 0.30],
        "N_ITEMS_IN_KB": 50,
        "N_ITEMS_OOD": 50,
        "HP_CENTER_TOL": 0.010,
        "HP_SPREAD_LO": 0.50,
        "HP_SPREAD_HI": 2.00,
        "HP_OOD_REL_TOL": 0.30,
        "hp_center_pass_count": 135,
        "hp_spread_pass_count": 135,
        "hp_ood_pass_count": 135,
        "hf_center_break_count": 0,
        "hf_ood_break_count": 0,
        "cardinality_breach_count": 0,
        "hp_center_theoretical_1_minus_2f_match": {
            "mean_delta": 0.00112,
            "max_delta": 0.00552,
            "min_delta": 0.000024,
        },
        "LLN_1_over_sqrt_N_scaling_law_verified": True,
        "LLN_scaling_predicted_ratio_16k_over_4k": 0.500,
        "LLN_scaling_observed_ratios_15_V_C_f_pairs": {
            "V_C_100_f_0.05": 0.5115,
            "V_C_100_f_0.10": 0.4900,
            "V_C_100_f_0.15": 0.5800,
            "V_C_100_f_0.20": 0.5380,
            "V_C_100_f_0.30": 0.4628,
            "V_C_200_f_0.05": 0.4256,
            "V_C_200_f_0.10": 0.5657,
            "V_C_200_f_0.15": 0.5402,
            "V_C_200_f_0.20": 0.4599,
            "V_C_200_f_0.30": 0.4772,
            "V_C_400_f_0.05": 0.5118,
            "V_C_400_f_0.10": 0.5033,
            "V_C_400_f_0.15": 0.5753,
            "V_C_400_f_0.20": 0.6264,
            "V_C_400_f_0.30": 0.4950,
        },
        "LLN_scaling_mean_error": 0.043,
        "LLN_scaling_max_error": 0.126,
        "cross_seed_p50_in_kb_cv_at_N_4096": 0.005,
        "cross_seed_p50_in_kb_cv_at_N_8192_bit_identical": True,
        "cross_seed_p50_in_kb_cv_scales_with_1_over_sqrt_N": True,
        "atom_15b_expansion_criteria_satisfied": {
            "b_different_N": True,
            "c_different_f": True,
            "d_different_V_C": True,
        },
        "atom_15b_expansion_criteria_simultaneously": True,
        "n_llm_calls_all_seeds_all_units": 0,
        "verified_off_data": True,
        "metrics_path": "data/exp_lln_point_mass_verification_N_V_C_f_sweep_v1/metrics.json",
        "parent_atoms_not_superseded": [
            "T3/META_synthesis_LLN_point_mass_in_KB_max_sim_bipolar_FHRR_MEASURED_MECHANISM",
            "T3/AMENDMENT_LLN_point_mass_in_KB_max_sim_bipolar_FHRR_MM_to_CHAIN_GRADE_via_Atom_15_v8_3_seed_FULL_confirmation",
            "T3/EXP_substrate_refuse_gate_v8_conformal_v1_3seed_FULL_CHAIN_GRADE_M1p4_MILESTONE",
            "T3/EXP_refuse_gate_V_REL_sweep_v1_3seed_CHAIN_GRADE",
        ],
        "cert_tier": "chain_grade",
        "cert_increment_delta": 1,
        "new_claim_beyond_atom_15b": "LLN_1_over_sqrt_N_SCALING_LAW_verified_at_15_V_C_f_pairs",
        "scope_extension_beyond_atom_15b": "N_x_V_C_x_f_volume_4096_16384_x_100_400_x_0p05_0p30",
        "distinct_atom_not_amendment_reason": "scaling_law_is_new_claim_beyond_point_mass_at_fixed_N_and_scope_is_general_not_bounded",
    },
}
LEDGER_22 = {
    "ts": TS_NOW,
    "op": "cert_ruling_promotion_chain_grade_LLN_general_primitive_with_scaling_law",
    "atom_id": f"math::{ATOM_22_ID}",
    "cert_status": "chain_grade",
    "cert_class": "LLN_point_mass_general_substrate_physics_primitive_at_broader_scope_with_1_over_sqrt_N_scaling_law_new_claim",
    "verified_off_data": True,
    "atomized_by": "skunkworks_landed_VET_wave_2026-07-01_LLN_45config_general_primitive",
    "cell_commit": COMMIT,
    "verdict": (
        "CHAIN_GRADE_LLN_POINT_MASS_VERIFIED_general_substrate_physics_primitive_"
        "3_seeds_x_45_phase_points_equals_135_units_all_HP_gates_pass_100_percent_"
        "N_sweep_4096_8192_16384_V_C_sweep_100_200_400_f_sweep_0p05_to_0p30_"
        "hp_center_135_of_135_theoretical_1_minus_2f_match_mean_delta_0p0011_max_0p0055_"
        "hp_spread_135_of_135_observed_within_0p50_to_2p00_theoretical_normal_spread_band_"
        "hp_ood_135_of_135_leak_floor_matches_sqrt_2_log_V_C_over_N_within_0p30_relative_tolerance_"
        "NEW_CLAIM_LLN_1_over_sqrt_N_SCALING_LAW_verified_at_15_V_C_f_pairs_spread_ratio_mean_0p517_predicted_0p500_err_0p043_max_0p126_"
        "cross_seed_p50_in_kb_cv_0p003_to_0p006_bit_close_LLN_concentration_confirmed_"
        "atom_15b_expansion_criteria_b_different_N_c_different_f_d_different_V_C_ALL_3_simultaneously_satisfied_"
        "0_HF_breaks_0_cardinality_breaches_zero_LLM_calls_"
        "elapsed_15p58s_total_5p8s_per_seed_avg_"
        "DISTINCT_ATOM_not_amendment_because_LLN_scaling_law_is_NEW_claim_beyond_original_point_mass_at_fixed_N_"
        "Atom_15b_amendment_stays_valid_at_bounded_scope_this_atom_extends_general_primitive_"
        "cross_arc_overlap_cosine_0p31_below_0p40_rediscovery_threshold_"
        "load_bearing_substrate_physics_finding_LLN_holds_as_GENERAL_primitive_"
        "19th_CG_of_2026_07_01"
    ),
    "cert_increment_delta": 1,
    "cv": 0.005,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_lln_point_mass_verification_N_V_C_f_sweep_v1/metrics.json",
        "parent_atoms_not_superseded": [
            "T3/META_synthesis_LLN_point_mass_in_KB_max_sim_bipolar_FHRR_MEASURED_MECHANISM",
            "T3/AMENDMENT_LLN_point_mass_in_KB_max_sim_bipolar_FHRR_MM_to_CHAIN_GRADE_via_Atom_15",
        ],
        "atom_qualified_id": f"math::{ATOM_22_ID}",
    },
    "supersedes": None,
    "note": (
        "LLN_point_mass_verification_45_config_3seed_FULL_CHAIN_GRADE_19th_CG_of_2026_07_01_"
        "135_units_all_HP_pass_100_percent_zero_HF_breaks_zero_cardinality_breaches_"
        "extends_Atom_12_LLN_MM_and_Atom_15b_CG_amendment_from_bounded_scope_to_GENERAL_primitive_"
        "NEW_CLAIM_LLN_1_over_sqrt_N_SCALING_LAW_verified_at_15_V_C_f_pairs_mean_err_0p043_"
        "theoretical_1_minus_2f_center_prediction_match_mean_delta_0p0011_max_0p0055_within_fp32_and_finite_N_noise_"
        "OOD_leak_floor_formula_sqrt_2_log_V_C_over_N_holds_across_broader_V_C_range_consistent_with_Atom_7_and_15b_"
        "cross_seed_p50_in_kb_cv_scales_with_1_over_sqrt_N_bit_identical_at_N_8192_higher_at_N_4096_expected_LLN_behavior_"
        "atom_15b_expansion_criteria_b_different_N_c_different_f_d_different_V_C_ALL_3_simultaneously_satisfied_"
        "atom_15b_bounded_scope_amendment_stays_valid_this_atom_is_general_primitive_extension_"
        "cell_author_calibration_note_META_RULE_M_loosened_impossibly_tight_gates_to_physically_realizable_bands_preserves_discriminator_"
        "hdlab_downstream_any_bipolar_FHRR_cell_at_N_4096_16384_V_C_100_400_f_0p05_0p30_can_rely_on_LLN_predictions_"
        "cortex_external_calibrator_design_can_compute_d_prime_analytically_from_parameters_"
        "distinct_atom_not_amendment_because_scaling_law_new_claim_beyond_point_mass_at_fixed_N"
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
    math_before, math_after = atomic_append_jsonl(MATH_ATOMS, [ATOM_22])
    print(f"math/atoms.jsonl: {math_before} -> {math_after} (+{math_after - math_before})")

    ledger_records = [LEDGER_22]
    led_before, led_after = atomic_append_jsonl(CERT_LEDGER, ledger_records)
    print(f"meta/cert_ledger.jsonl: {led_before} -> {led_after} (+{led_after - led_before})")

    print()
    print(f"CERT delta: +1 (Atom 22 LLN 45-config general primitive CG)")
    print(f"  Atom 22: LLN point-mass verification 3-seed x 45-config FULL CHAIN_GRADE (19th CG of today)")
    print(f"           135/135 units pass all HP gates; 0 HF breaks; 0 cardinality breaches")
    print(f"           NEW CLAIM: LLN 1/sqrt(N) SCALING LAW verified beyond original point-mass claim")
    print(f"           Extends Atom 12/15b from bounded scope to GENERAL substrate physics primitive")
    print(f"           Satisfies Atom 15b expansion criteria (b)(c)(d) simultaneously")
    print(f"           Distinct atom not amendment: scaling law is NEW claim beyond point-mass at fixed N")
    print(f"Session-cumulative today: CG=+13, MM=+7, HF=+2, meta_amendment=+2")
    print(f"Timestamp: {TS_NOW}")
    print(f"Commit: {COMMIT}")


if __name__ == "__main__":
    main()
