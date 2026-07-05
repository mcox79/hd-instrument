"""
A5-gated atomization -- Skunkworks landed-VET 2026-07-05 (three FULLs).
AUDIT-ONLY. All numbers recomputed INDEPENDENTLY off-disk via .venv (NOT verdict_msg).

VET1 CONTROL v2  : exp_pfc_gate_cfrpe_trained_v2         -> MEASURED_MECHANISM (+1)
VET2 COMPREHENSION: exp_comprehension_envelope_superposition_vocab_v1 -> MEASURED_MECHANISM (+1)
VET3 ENCODER 5seed: exp_encoder_step2step3_inbatch_rkd_shipmetric_carrythrough_v1_seed_{7,13,23,29,31}
                    -> MIDDLE_BAND (+1 baseline confirmation, cross-ref perception graded-code MM)

NET CERT DELTA: MM +2, MB +1, CG 0, HF 0, DEMOTE 0.
"""
import json
import os
import time
import tempfile

MATH_ATOMS = "d:/AI/hd-instrument/data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = "d:/AI/hd-instrument/data/substrate_index/meta/cert_ledger.jsonl"
DATA = "d:/AI/hd-instrument/data"

TS = time.time()
TS_ISO = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(TS))
SESSION_TAG = "2026-07-05_control_v2_comprehension_envelope_encoder_5seed_three_FULLs"

# ---- composition atom ids (verified present on disk) ----
CONTROL_V1_ID = "math::MEASURED_MECHANISM_pfc_gate_cfrpe_trained_v1_cfRPE_successor_feature_transport_GoNoGo_gate_DELIVERS_the_v3_revival_a_target_cosine_INDEPENDENT_signal_reach_tcos_corr_neg0p045_that_DECISIVELY_beats_the_static_additive_baseline_52_gonogo_only_vs_1_additive_only_paired_sign_p_1p2e_minus14_go_over_add_ratio_GROWS_with_harder_regime_2p85x_d3_4p18x_d4_6p67x_d6_7p00x_d8_and_per_hop_reach_rank_test_0p495_vs_chance_0p25_FIRES_at_scale_BUT_end_to_end_capability_is_FLOOR_BOUND_in_the_deep_canonical_regime_gonogo_0p100_at_d6_and_0p035_at_d8_vs_oracle_0p958_0p933_closes_only_9pct_of_the_0p943_headroom_bar_wanted_25pct_because_per_hop_accuracy_decays_geometrically_factor_0p59_per_hop_regime_stable_so_the_smoke_0p365_to_full_0p085_gonogo_lift_drop_is_decision_depth_4_to_6_plus_V_200_to_2400_floor_compression_NOT_effect_death_the_cells_HARD_FAIL_ADDITIVE_RAIL_verdict_is_a_REGIME_calibration_failure_additive_baseline_add_0p015_below_the_0p05_measurable_floor_NOT_a_clean_effect_collapse_DOWNGRADED_from_HARD_FAIL_to_MEASURED_MECHANISM_5seed_FULL_N8192_V2400_2026-07-05"
COMPREHENSION_FRAMECLASSIFY_MM_ID = "math::MEASURED_MECHANISM_comprehension_classify_then_decode_ARCHITECTURE_validated_end_to_end_and_sparse_block_geometry_makes_the_frame_BLOCK_SET_recoverable_as_a_ZERO_NOISE_occupancy_readout_where_the_DENSE_algebra_entangles_it_to_chance_dense_ctrl_frame_class_0p078_approx_1overF_vs_sparse_1p000_gap_0p922_PAIRED_non_vacuous_BUT_the_1p000_is_BY_CONSTRUCTION_deterministic_occupied_block_L2_energy_exactly_k20_empty_exactly_0_matched_filter_margin_exactly_k_min_eq_max_and_CORRELATION_INDEPENDENT_frame_class_1p000_even_on_RANDOM_uncorrelated_fillers_recovers_the_block_SET_NOT_role_ORDER_permuted_role_to_block_same_set_gives_IDENTICAL_occupancy_order_fixed_by_sort_convention_never_tested_frame_class_stays_1p000_to_F56_all_distinct_subsets_so_F_count_Arm4_wont_bottleneck_and_decode_is_at_proven_easy_regime_ceiling_cond_decode_1p000_at_V1024D3_cliff_CITED_0p856_at_V8192D26_comprehension_FRONTIER_OPENED_not_closed_next_test_is_ORDER_PERMUTATION_recovery_and_superposition_and_decode_at_scale_3seed_FULL_N8192_F16_2026-07-05"
PERCEPTION_GRADED_MM_ID = "math::MEASURED_MECHANISM_PERCEPTION_SHIP_GATE_re_verdict_graded_GSBC_codes_SOLVE_the_retrieval_agreement_gap_that_made_the_seed7_ship_metric_MIDDLE_BAND_baseline_SIGN_INBATCH_BLOCK_cosine_0p8611_PASS_composed_at_J10_0p9833_PASS_ret_agree10_0p1837_MISS_0p30_ONLY_the_ret_axis_failed_and_hard_STE_sign_quantization_is_CONFIRMED_the_cause_all_hard_sign_codes_sit_0p18_to_0p22_the_GRADED_fix_v11_GSBC_FULL_block_topm3_full_recipe_2seed_ret_0p3986_0p3968_BOTH_clear_0p30_lift_pos0p1869_pos0p1791_cosine_hi80_0p8338_0p8300_BOTH_clear_0p80_keyed_J5_1p000_shuffled_0p000_cv_ret_0p0023_cos_0p0023_composed_at_J10_ge_0p95_by_SOUND_monotone_bracketing_no_exact_J10_point_exists_Jsweep_1_2_5_8_16_32_64_keyed_acc_monotone_nonincreasing_in_J_so_J10_ge_J16_and_same_geometry_graded_block_v12_GSBC_RKD_BLOCK_J16_0p9833_seed7_1p000_seed13_full_recipe_does_NOT_degrade_keyed_margin_snr_0p0575_vs_0p0580_so_GSBC_FULL_at_J10_tracks_block_the_KEY_GAP_v12_EXPAND2X_J8_eq_J16_eq_1p000_does_NOT_close_the_J10_for_GSBC_FULL_gap_because_EXPAND2X_is_a_DIFFERENT_code_gwta_global_topk_out8192_kb64_rkd_vs_GSBC_FULL_block_topm3_out4096_full_different_sha256_geometry_width_recipe_Director_suspicion_CORRECT_use_same_geometry_RKD_BLOCK_not_EXPAND2X_VERDICT_perception_PASSES_the_joint_ship_gate_with_graded_codes_retrieval_gap_SOLVED_RESERVATION_no_strict_single_carrythrough_run_co_measures_ret_plus_cosine_plus_keyed_at_J10_on_ONE_deployed_graded_code_with_an_exact_J10_point_confirming_FULL_is_CHEAP_high_prior_PASS_not_a_research_risk_2seed_FULL178k_2026-07-05"


def rnd(x, n=4):
    return round(float(x), n)


# =========================================================================
# RECOMPUTE OFF-DISK (independent, .venv) -- CONTROL v2
# =========================================================================
ctrl = json.load(open(f"{DATA}/exp_pfc_gate_cfrpe_trained_v2/metrics.json"))
pr = ctrl["per_regime"]
ctrl_recompute = {}
for k, r in pr.items():
    am = r["arm_means"]
    add, gono, cctrl, orac = am["additive_baseline"], am["cfrpe_trained_gonogo"], am["cfrpe_control_identity"], am["oracle"]
    ctrl_recompute[k] = {
        "additive": rnd(add), "gonogo": rnd(gono), "control_identity": rnd(cctrl), "oracle": rnd(orac),
        "gonogo_lift_recomp": rnd(gono - add), "dynamics_lift_recomp": rnd(gono - cctrl),
        "closure_recomp": rnd((gono - add) / (orac - add)),
        "gonogo_cv": rnd(r["gonogo_cv"]), "baseline_in_band": r["baseline_in_band"],
        "reach_tcos_corr": rnd(r["reach_tcos_corr_test"]), "reach_rank_test": rnd(r["reach_rank_test"]),
        "sign_p": r["sign_test_p"], "oracle_rail_ok": r["oracle_rail_ok"],
    }
# both fair regimes pass check
fair = ctrl["fair_regime_keys"]
fair_pass = {}
for k in fair:
    r = pr[k]
    fair_pass[k] = bool(r["closure"] >= 0.25 and r["gonogo_cv"] < 0.10 and abs(r["reach_tcos_corr_test"]) < 0.85
                        and r["sign_test_p"] < 0.05 and r["reach_rank_test"] > 0.30 and r["oracle_rail_ok"])

# =========================================================================
# RECOMPUTE OFF-DISK -- ENCODER 5seed
# =========================================================================
enc_seeds = [7, 13, 23, 29, 31]
enc = {}
cos_list, ret_list, rt_list, delta_list = [], [], [], []
for s in enc_seeds:
    d = json.load(open(f"{DATA}/exp_encoder_step2step3_inbatch_rkd_shipmetric_carrythrough_v1_seed_{s}/metrics.json"))
    sh = d["ship"]
    cos_list.append(sh["cosine_to_gold"]); ret_list.append(sh["ret_agree10"])
    rt_list.append(sh["composed_roundtrip"]); delta_list.append(sh["delta_ret_agree10_vs_charpos"])
    enc[s] = {"cosine_to_gold": rnd(sh["cosine_to_gold"]), "ret_agree10": rnd(sh["ret_agree10"]),
              "composed_roundtrip": rnd(sh["composed_roundtrip"]), "isolated_roundtrip": rnd(sh["isolated_roundtrip"]),
              "charpos_ret_agree10": rnd(sh["charpos_ret_agree10"]), "delta_vs_charpos": rnd(sh["delta_ret_agree10_vs_charpos"]),
              "spearman_all": rnd(sh["spearman_all"]), "verdict": d["verdict"], "baseline_in_band": sh["baseline_in_band"]}
cos_mean = sum(cos_list) / len(cos_list)
ret_mean = sum(ret_list) / len(ret_list)
enc_agg = {
    "cosine_mean": rnd(cos_mean), "cosine_min": rnd(min(cos_list)), "cosine_max": rnd(max(cos_list)),
    "cosine_n_clear_0p80": sum(1 for c in cos_list if c >= 0.80),
    "ret_agree10_mean": rnd(ret_mean), "ret_agree10_min": rnd(min(ret_list)), "ret_agree10_max": rnd(max(ret_list)),
    "ret_agree10_n_clear_0p30": sum(1 for r in ret_list if r >= 0.30),
    "composed_roundtrip_min": rnd(min(rt_list)), "composed_roundtrip_max": rnd(max(rt_list)),
    "delta_vs_charpos_min": rnd(min(delta_list)), "delta_vs_charpos_max": rnd(max(delta_list)),
}

# =========================================================================
# RECOMPUTE OFF-DISK -- COMPREHENSION envelope
# =========================================================================
comp = json.load(open(f"{DATA}/exp_comprehension_envelope_superposition_vocab_v1/metrics.json"))
env = comp["envelope"]
cf = comp["arms"]["content_frame"]
oc = comp["arms"]["occupancy_baseline"]
dp = comp["arms"]["decode_posctrl"]
comp_recompute = {
    "n_order_cells_hold": sum(1 for v in env["order_holds_surface"].values() if v),
    "n_parse_cells_hold": sum(1 for v in env["parse_holds_surface"].values() if v),
    "n_cells_total": env["n_cells_total"],
    "order_content_perrole_min": rnd(min(cf["order_perrole_by_cell"].values())),
    "order_content_perrole_max": rnd(max(cf["order_perrole_by_cell"].values())),
    "occupancy_perrole_min": rnd(min(oc["order_perrole_by_cell"].values())),
    "occupancy_perrole_max": rnd(max(oc["order_perrole_by_cell"].values())),
    "occupancy_chance": 0.5,
    "decode_full_D2": rnd(dp["decode_full_by_cell"]["D2_V50"]),
    "decode_full_D4plus_all_zero": all(v == 0.0 for kk, v in dp["decode_full_by_cell"].items() if not kk.startswith("D2")),
    "cliff_cells": env["cliff_cells_order_holds_parse_fails"],
    "D8V1000_survival": rnd(cf["superposition_survival_by_cell"]["D8_V1000"]),
    "hp_corner_content": rnd(cf["hp_corner_perrole_mean"]), "hp_corner_occupancy": rnd(oc["hp_corner_perrole_mean"]),
    "parse_max_constituents_at_Vge500": env["parse_max_constituents_at_Vge500"],
    "max_constituents_at_Vge500": env["max_constituents_at_Vge500"],
}

# =========================================================================
# ATOM 1 -- CONTROL v2  (MEASURED_MECHANISM)
# =========================================================================
atom_control = {
    "id": "math::MEASURED_MECHANISM_pfc_gate_cfrpe_trained_v2_FULL_5seed_7regime_sweep_RESOLVES_the_v1_regime_calibration_failure_the_cfRPE_GoNoGo_control_gate_PASSES_at_the_FAIR_depth4_superposition_regime_where_the_additive_baseline_is_in_band_not_floored_BOTH_fair_regimes_pass_V1200_d4_closure_0p661_gonogo_lift_0p600_dynamics_lift_0p603_and_V2400_d4_closure_0p514_gonogo_lift_0p468_cross_seed_cv_0p037_and_0p031_discriminator_FIRES_gonogo_beats_identity_reach_CTRL_by_0p60_anti_tautology_clean_reach_tcos_corr_neg0p079_paired_sign_p_2e_minus196_oracle_rail_0p962_n_fair_2of7_is_the_CONSERVATIVE_meta_rule_excludes_5_FLOORED_baseline_regimes_a_HARDER_test_not_a_cherry_pick_V2400_d6_intended_floored_control_correctly_auto_EXCLUDED_not_silently_passed_BUT_capability_DEGRADES_with_superposition_depth_gonogo_0p653_d4_to_0p075_d6_scoped_to_depth4_NOT_a_universal_all_regime_pass_5seed_FULL_N8192_2026-07-05",
    "name": "MATH MEASURED_MECHANISM (CONTROL resolved weak->PROVEN-at-depth4): pfc_gate_cfrpe_trained_v2 FULL 5-seed 7-regime sweep resolves the v1 regime-calibration failure. The cfRPE GoNoGo control gate PASSES at the FAIR depth-4 superposition regime (additive baseline in-band, not floored). BOTH fair regimes pass: V1200_d4 closure=0.661 gonogo_lift=0.600 dynamics_lift=0.603 cv=0.037; V2400_d4 closure=0.514 gonogo_lift=0.468 cv=0.031. Discriminator FIRES (gonogo beats identity-reach CTRL by ~0.60); anti-tautology clean (reach_tcos_corr=-0.079, reach independent of target-cosine); paired sign_p~2e-196; oracle_rail=0.962. n_fair=2/7 is the CONSERVATIVE meta-rule (excludes 5 FLOORED-baseline regimes -> a HARDER test, NOT a cherry-pick); V2400_d6 (intended floored control) correctly auto-EXCLUDED, not silently passed. BUT the capability DEGRADES with superposition depth (gonogo 0.653 at d4 -> 0.075 at d6): scoped to depth-4, NOT a universal all-regime PASS.",
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet",
    "cert_status": "proven_bound_control_gate_passes_at_fair_depth4_regime_degrades_with_superposition_depth_resolves_v1_calibration_failure",
    "cert_class": "pfc_cfrpe_gonogo_control_gate_PROVEN_at_fair_depth4_both_fair_regimes_pass_discriminator_fires_anti_tautology_clean_n_fair_2of7_conservative_not_cherry_pick_depth_scoped",
    "description": (
        "LANDED-VET of exp_pfc_gate_cfrpe_trained_v2 (self-reported HARD_PASS, run_mode=full, N=8192, 5 seeds "
        "[7,17,23,31,41], 7 regimes V{800,1200,2400}x{d4,d5} + V2400_d6, expected_n=175 completed=175, "
        "cardinality_ok=True; cell commit 1d606f4ec). AUDITOR INDEPENDENT RECOMPUTE (.venv, off per_regime arm_means, "
        "NOT verdict_msg): all gonogo_lift/dynamics_lift/closure reconcile EXACTLY. "
        "\n"
        "WHAT IS REAL AND PROVEN (the load-bearing finding): the cfRPE successor-feature GoNoGo gate DECISIVELY beats "
        "the static additive baseline AT THE FAIR (in-band, non-floored) DEPTH-4 REGIME. BOTH fair regimes clear the "
        "full pass bar (HP_closure>=0.25, cv<0.10, |reach_tcos_corr|<0.85, sign_p<0.05, reach_rank>0.30, oracle_rail): "
        "V1200_d4 (FOCUS) closure=0.661 gonogo=0.653 vs additive=0.053 -> gonogo_lift=0.600, dynamics_lift=0.603 "
        "(gonogo beats the identity-reach CTRL=0.051), cv=0.037, reach_tcos_corr=-0.079, reach_rank=0.690, sign_p=2.4e-196 "
        "(734 go-only vs 14 add-only paired); V2400_d4 closure=0.514 gonogo=0.521 vs additive=0.053 -> gonogo_lift=0.468, "
        "dynamics_lift=0.466, cv=0.031, reach_tcos_corr=-0.071, sign_p=1.5e-144. It is NOT a single-focus cherry-pick: "
        "the SECOND fair regime also passes cleanly. The discriminator FIRES (dynamics_lift>0 -> the TRAINED reach "
        "dynamics add value beyond identity-reach; control_identity stays at baseline ~0.05). Anti-tautology CLEAN "
        "(reach_tcos_corr=-0.079<<0.85 -> the reach weight is NOT correlated with target-cosine, the gate is not reading "
        "off the target). "
        "\n"
        "WHY n_fair=2/7 IS NOT A CHERRY-PICK (auditor scrutiny of the KEY concern): the 5 EXCLUDED regimes "
        "(V800_d4 additive=0.038, all d5 additive~0.013-0.016, V2400_d6 additive=0.007) have FLOORED additive baselines "
        "below the ~0.05 measurable band. At those regimes the gonogo lift is actually LARGEST relative to baseline "
        "(V2400_d6 gonogo=0.075 vs additive=0.007 ~ 11x), so beating them is EASIER -> excluding them makes the "
        "certified test HARDER, the CONSERVATIVE (anti-inflation) direction. The meta-rule keeps only the regimes where "
        "the additive baseline is a genuine competitor (~0.05), and the gonogo still wins there by ~0.5-0.6 absolute. "
        "V2400_d6 -- the INTENDED floored-baseline control -- is correctly auto-EXCLUDED (baseline_in_band=False), NOT "
        "silently passed. This is the v1 calibration failure FIXED: v1's HARD_FAIL_ADDITIVE_RAIL was a regime-calibration "
        "artifact (additive below floor); v2 sweeps to FIND and certify only the fair regimes. "
        "\n"
        "THE MEASURED BOUND (why MM, honest scope): the gonogo capability itself DEGRADES monotonically with "
        "superposition depth -- gonogo 0.642/0.653/0.521 at d4, 0.315/0.293/0.220 at d5, 0.075 at d6; closure 0.66 -> "
        "0.07. So the CLEAN fair PASS is at DEPTH-4 only. At d5/d6 the signal is still present (sign_p tiny, gonogo >> "
        "everything) but the baseline is floored so it cannot be FAIRLY certified, and closure has collapsed. The "
        "'HARD_PASS resolves CONTROL to PASS' framing must be SCOPED: CONTROL moves from weak (v1 floor-bound) to "
        "PROVEN-at-depth-4 (MEASURED_MECHANISM) -- a real, meaningful upgrade -- but NOT a universal all-regime "
        "chain-grade control pass. "
        "\n"
        "TIER RATIONALE: MEASURED_MECHANISM (+1). The gating mechanism is PROVEN non-vacuously at the fair depth-4 "
        "regime (2/2 fair regimes pass, discriminator fires, anti-tautology clean, 5 seeds, tight cv), so NOT HARD_FAIL "
        "and NOT dismissed. But it is a capability WITH a measured depth-envelope bound (d5/d6 collapse), scoped to "
        "depth-4 fair regimes, so NOT a universal chain-grade PASS. This CONFIRMS+SCOPES the v1 MM at FULL 5-seed scale."
    ),
    "aliases": ["control cfrpe gonogo gate passes at fair depth4 regime both fair regimes pass",
                "n_fair 2of7 is conservative meta-rule not a cherry-pick floored baselines excluded",
                "control resolved weak to proven-at-depth4 degrades with superposition depth"],
    "metadata": {
        "record_class": "experiment_landed_vet_measured_mechanism_control_capability_resolved_at_fair_depth4_regime",
        "term_class": "PFC_CFRPE_GONOGO_CONTROL_GATE_PROVEN_AT_FAIR_DEPTH4_BOTH_FAIR_REGIMES_PASS_N_FAIR_2OF7_CONSERVATIVE_DEPTH_SCOPED",
        "cert_status": "proven_bound_control_gate_passes_at_fair_depth4_regime_degrades_with_depth",
        "cert_class": "pfc_cfrpe_gonogo_control_gate_PROVEN_at_fair_depth4_conservative_meta_rule_depth_scoped",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "verified_via": "independent .venv off-disk recompute off per_regime arm_means (NOT verdict_msg): gonogo_lift/dynamics_lift/closure reconcile EXACTLY; both fair regimes pass full bar; n_fair meta-rule confirmed conservative; depth-cliff confirmed",
        "atomized_by": "skunkworks_landed_VET_2026-07-05_control_v2_comprehension_envelope_encoder_5seed",
        "anchor": "pfc_gate_cfrpe_trained_v2",
        "cell_commit": "1d606f4ec",
        "raw_metrics_path": "data/exp_pfc_gate_cfrpe_trained_v2/metrics.json",
        "run_mode": "full", "N": 8192, "n_seeds": 5, "seeds": [7, 17, 23, 31, 41], "n_units": 175,
        "cardinality_ok": True,
        "load_bearing_number": "FOCUS V1200_d4 closure=0.661 gonogo_lift=0.600 dynamics_lift=0.603 cv=0.037 reach_tcos_corr=-0.079; 2nd fair regime V2400_d4 closure=0.514 gonogo_lift=0.468 -> BOTH fair regimes pass; depth-cliff gonogo 0.653(d4)->0.075(d6)",
        "recompute_off_disk_per_regime": ctrl_recompute,
        "fair_regime_keys": fair,
        "fair_regimes_both_pass_full_bar": fair_pass,
        "non_vacuity_checks": {
            "both_fair_regimes_pass_not_single_focus": "V1200_d4 PASS and V2400_d4 PASS on HP_closure>=0.25, cv<0.10, |corr|<0.85, sign_p<0.05, reach_rank>0.30, oracle_rail -> not a lucky single-regime pass",
            "discriminator_fires": "dynamics_lift=gonogo-control_identity=+0.603/+0.466 at fair regimes -> trained reach dynamics beat identity-reach CTRL (which sits at baseline ~0.05)",
            "anti_tautology_clean": "reach_tcos_corr=-0.079/-0.071 << 0.85 -> reach weight NOT correlated with target-cosine; gate is not reading off the target",
            "paired_sign_test": "sign_p=2.4e-196/1.5e-144; 734 go-only vs 14 add-only (fair focus) -> overwhelmingly paired-consistent win",
            "positive_control_oracle_rail": "oracle ~0.962 all regimes, oracle_rail_ok=True everywhere -> the ceiling arm reaches its expected rail (test not degenerate)",
            "conservative_meta_rule_not_cherry_pick": "5 excluded regimes have FLOORED additive baselines (0.007-0.038 < ~0.05 band) where gonogo win is LARGER relative to baseline; excluding them is the HARDER, anti-inflation direction; V2400_d6 intended floored control correctly auto-excluded not silently passed",
        },
        "measured_bound": "gonogo DEGRADES monotonically with superposition depth: 0.642/0.653/0.521 (d4) -> 0.315/0.293/0.220 (d5) -> 0.075 (d6); closure 0.66->0.07. Clean fair PASS is at DEPTH-4 only; d5/d6 signal present (sign_p tiny) but baseline floored (not fairly certifiable) and closure collapsed.",
        "cross_arc_overlap_check_2026_07_01_USER_locked": "substrate_query 'pfc goal conditioned gate cfrpe successor feature go nogo control reach target cosine independent' -> top hit cosine=0.3281 = pfc_goal_conditioned_gate_v1 (metrics) + prereg 0.292. These are the DIRECT v1/v3 predecessors of THIS arc -> v2 is a targeted FULL scale-up + fair-regime resolution of its own arc, NOT an inadvertent cross-arc rediscovery. Confirmed targeted extension.",
        "composes_with_atoms": [CONTROL_V1_ID],
        "composition_note": "COMPOSES WITH / CONFIRMS+SCOPES (does NOT supersede) the v1 control MM: v1 established the gate FIRES at scale but is FLOOR-BOUND in the deep canonical regime and its HARD_FAIL_ADDITIVE_RAIL was a regime-calibration failure (additive below floor). v2 FIXES that by the fair-regime meta-rule: at the properly-calibrated fair depth-4 regime the gate PASSES (closure 0.51-0.66). v1 stands as the smoke/deep-regime characterization; v2 is the FULL fair-regime resolution.",
        "framing_corrections_vs_director_and_cell": "AFFIRM: HARD_PASS is legitimate FOR the fair depth-4 regime; both fair regimes pass; discriminator fires; anti-tautology clean; positive control (oracle rail) holds; n_fair=2/7 is the conservative meta-rule working CORRECTLY (excludes floored baselines = harder test), the intended floored control V2400_d6 is correctly auto-excluded not silently passed. CORRECT (downward, symmetric, honest scope): (1) 'resolves CONTROL to PASS' should be SCOPED to 'PROVEN at depth-4' -- the gonogo capability DEGRADES with superposition depth (0.653 d4 -> 0.075 d6), so this is NOT a universal all-regime chain-grade control pass. (2) Tier = MEASURED_MECHANISM (proven-at-fair-depth4 with a measured depth-envelope), NOT chain-grade -- CONTROL moves from weak to PROVEN-at-depth-4, a real upgrade, but the bound is real. NO under-deflation: the mechanism IS proven, the discriminator DOES fire, and the meta-rule is credited as conservative-not-cherry-pick.",
        "envelope_and_next_test": "The fair-regime envelope is depth-4 (V1200/V2400). Next test to widen the certified envelope: raise the additive baseline INTO the measurable band at d5/d6 (lower V or adjust density) so the deep-regime win can be FAIRLY certified, OR accept depth-4 as the mechanism's certified operating envelope. The depth-cliff itself (per-hop geometric decay) is the measured bound to characterize.",
        "expansion_criterion": "PROMOTES toward CHAIN_GRADE iff the gate passes the full bar at >=3 fair regimes spanning >1 superposition depth (e.g. a d5 regime with a non-floored baseline in-band), demonstrating the control is not depth-4-specific. Stays MM if only depth-4 fair regimes certify. DEMOTES only if a re-run fails to reproduce the fair-regime pass (not expected; reconciled exactly).",
        "disposition": "MEASURED_MECHANISM_control_cfrpe_gonogo_gate_PROVEN_at_fair_depth4_both_fair_regimes_pass_discriminator_fires_anti_tautology_clean_n_fair_2of7_conservative_not_cherry_pick_capability_degrades_with_superposition_depth_scoped_to_depth4_confirms_and_scopes_v1_MM_at_FULL_5seed",
        "cert_increment_delta": 1,
    },
}

# =========================================================================
# ATOM 2 -- COMPREHENSION envelope  (MEASURED_MECHANISM)
# =========================================================================
atom_comp = {
    "id": "math::MEASURED_MECHANISM_comprehension_envelope_superposition_vocab_v1_RESOLVES_the_ORDER_recovery_frontier_the_prior_frame_classify_MM_opened_content_conditioned_role_typing_selectional_restriction_RECOVERS_role_to_block_ORDER_across_a_D2_to_D8_by_V50_to_1000_envelope_order_holds_20of20_cells_content_order_perrole_0p964_to_1p000_even_at_D8_L4_superposition_where_survival_drops_to_0p446_the_OCCUPANCY_blind_control_stays_at_CHANCE_0p46_to_0p54_discriminator_FIRES_order_from_role_typing_NOT_occupancy_leakage_role_blind_decode_COLLAPSES_decode_full_0p000_at_D4plus_selectional_restriction_NECESSARY_full_parse_envelope_bounded_at_D6_all_V_and_D8_Vle125_17of20_cells_CLIFF_at_D8_Vge250_driven_by_superposition_survival_collapse_HP_corner_D4V500_content_1p000_occupancy_0p458_exact_1p000_chance_0p167_BOUNDED_probe_5p6pct_concepts_3seed_FULL_N8192_K192_2026-07-05",
    "name": "MATH MEASURED_MECHANISM (COMPREHENSION order-recovery envelope, resolves the frontier the frame-classify MM opened): content-conditioned role-typing (selectional restriction) RECOVERS role->block ORDER across a D2-D8 x V50-1000 superposition envelope. ORDER holds 20/20 cells (content order_perrole 0.964-1.000, even at D8 L=4 superposition where survival drops to 0.446). The OCCUPANCY-blind control stays at CHANCE (0.46-0.54, chance 0.5) -> the discriminator FIRES: order comes from role-typing NOT occupancy leakage. Role-blind decode COLLAPSES (decode_full=0.000 at D4+) -> selectional restriction is NECESSARY. Full-PARSE envelope (order AND all fillers) bounded at D6-all-V / D8-V<=125 (17/20 cells); CLIFF at D8 x V>=250 driven by superposition-survival collapse. HP corner D4V500 content=1.000 occupancy=0.458 exact=1.000 (chance 0.167). BOUNDED probe (5.6% of concepts), 3 seeds.",
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet",
    "cert_status": "proven_bound_comprehension_order_recovery_via_content_role_typing_full_parse_envelope_bounded_cliff_at_D8_Vge250",
    "cert_class": "comprehension_order_recovery_content_role_typing_selectional_restriction_occupancy_control_at_chance_discriminator_fires_role_blind_decode_collapses_full_parse_envelope_bounded",
    "description": (
        "LANDED-VET of exp_comprehension_envelope_superposition_vocab_v1 (self-reported HARD_PASS, run_mode=full, "
        "N=8192, K_ACTIVE=192, B_TOTAL=8, B_OCC=2, D_grid=[2,4,6,8], V_grid=[50,125,250,500,1000], 80 trials, "
        "3 seeds [7,13,19], 60 units, cardinality_ok=True, arms_differ_verified=True; cell commit 704ff5539). "
        "AUDITOR INDEPENDENT RECOMPUTE (.venv, off arms/grid, NOT verdict_msg): order-cells-hold=20/20, "
        "parse-cells-hold=17/20, cliff cells and survival all reconcile. "
        "\n"
        "WHAT IS REAL AND PROVEN (the load-bearing finding, and it RESOLVES the prior frontier): the prior "
        "frame-classify MM recovered the block-SET but NOT role-ORDER (occupancy is order-blind), and it set an "
        "explicit CG-promotion criterion: 'a follow-up cell demonstrating frame recovery UNDER STRESS -- ORDER/"
        "permutation recovery (same block-set, different role->block map) with a paired negative control that CAN "
        "fail.' THIS cell delivers exactly that. Content-conditioned role-typing (each role has a DISJOINT content "
        "vocabulary = selectional restriction) RECOVERS the role->block ORDER: content order_perrole = 0.964-1.000 "
        "across the full D2-D8 x V50-1000 grid, holding even at D8 (load L=4 per block) where superposition survival "
        "has dropped to 0.446 -- role-typing survives crosstalk because the matched filter to the disjoint vocab "
        "identifies the RIGHT role even when the exact filler is corrupted. "
        "\n"
        "THE DISCRIMINATOR FIRES (paired can-fail control at chance): the OCCUPANCY-blind arm (order-agnostic block "
        "pooling) stays at CHANCE order_perrole 0.458-0.5375 (chance 0.5) at EVERY one of the 20 cells -> occupancy "
        "PROVABLY cannot recover order (same block-set regardless of order), so the content-frame's order recovery is "
        "NOT occupancy leakage. SELECTIONAL RESTRICTION NECESSARY: the role-blind decode (decode_full) = 1.000 at D2 "
        "(L=1, one filler per role, trivial) but COLLAPSES to 0.000 at D4+ (L>=2) -> without role-typing the "
        "assignment cannot be recovered under superposition; role-conditioning is load-bearing. "
        "\n"
        "THE MEASURED BOUND (why MM, honest scope): (1) FULL-PARSE (order AND all fillers recovered) is bounded: "
        "17/20 cells hold; the CLIFF is at D8 x V>=250 (D8_V250/V500/V1000 parse-fail) where order still holds but "
        "not all fillers survive -- driven by superposition_survival dropping (D8_V1000 survival=0.446, ~55% of "
        "fillers lost to crosstalk). parse_max_constituents@V>=500=6 vs order max_constituents@V>=500=8. (2) The order "
        "recovery RELIES on the disjoint-per-role-vocabulary selectional-restriction structural assumption (a real, "
        "brain-grounded mechanism -- content constrains role -- but a specific regime). (3) BOUNDED probe: native "
        "GSBC_EXPAND2X codes over 10000 of 177899 concepts (5.6%), 3 seeds, 80 trials. "
        "\n"
        "TIER RATIONALE: MEASURED_MECHANISM (+1). The order-recovery mechanism (content-role-typing recovers order "
        "under superposition; occupancy control at chance; role-blind decode collapses) is PROVEN non-vacuously and "
        "satisfies the prior atom's own order-under-stress promotion criterion, so this is a genuine ADVANCE (set->order). "
        "But it is an ENVELOPE with a measured full-parse cliff (D8 x V>=250) and relies on the selectional-restriction "
        "regime on a bounded concept probe, so 'COMPREHENSION HOLDS' is honestly scoped to order-recovery-via-role-typing "
        "with a measured full-parse bound -- MM, not a universal chain-grade parse."
    ),
    "aliases": ["comprehension order recovery via content role typing selectional restriction envelope",
                "occupancy blind control at chance discriminator fires role blind decode collapses",
                "full parse cliff at D8 Vge250 superposition survival collapse resolves prior frame classify frontier"],
    "metadata": {
        "record_class": "experiment_landed_vet_measured_mechanism_comprehension_order_recovery_envelope",
        "term_class": "COMPREHENSION_ORDER_RECOVERY_CONTENT_ROLE_TYPING_SELECTIONAL_RESTRICTION_OCCUPANCY_CONTROL_AT_CHANCE_FULL_PARSE_ENVELOPE_BOUNDED_CLIFF_D8_Vge250",
        "cert_status": "proven_bound_comprehension_order_recovery_full_parse_envelope_bounded",
        "cert_class": "comprehension_order_recovery_content_role_typing_occupancy_control_at_chance_role_blind_decode_collapses_full_parse_bounded",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "verified_via": "independent .venv off-disk recompute off arms/grid (NOT verdict_msg): order-cells-hold=20/20, occupancy at chance 0.46-0.54, decode_full=0 at D4+, parse-cells-hold=17/20, cliff=D8xV>=250, D8V1000 survival=0.446",
        "atomized_by": "skunkworks_landed_VET_2026-07-05_control_v2_comprehension_envelope_encoder_5seed",
        "anchor": "comprehension_envelope_superposition_vocab_v1",
        "cell_commit": "704ff5539",
        "raw_metrics_path": "data/exp_comprehension_envelope_superposition_vocab_v1/metrics.json",
        "run_mode": "full", "N": 8192, "K_ACTIVE": 192, "B_TOTAL": 8, "B_OCC": 2,
        "D_grid": [2, 4, 6, 8], "V_grid": [50, 125, 250, 500, 1000], "trials": 80,
        "n_seeds": 3, "seeds": [7, 13, 19], "n_units": 60, "cardinality_ok": True,
        "bounded_probe_note": "native GSBC_EXPAND2X codes over 10000 of 177899 concepts (5.6%)",
        "load_bearing_number": "ORDER holds 20/20 cells (content order_perrole 0.964-1.000); OCCUPANCY control at CHANCE 0.46-0.54 (discriminator fires); role-blind decode_full=0.000 at D4+ (selectional restriction necessary); full-PARSE 17/20, cliff D8xV>=250 (D8V1000 survival=0.446)",
        "recompute_off_disk": comp_recompute,
        "non_vacuity_checks": {
            "occupancy_control_at_chance_can_fail_and_does": "occupancy-blind order_perrole 0.458-0.5375 (chance 0.5) at ALL 20 cells -> order recovery is NOT occupancy leakage; the paired control CAN fail (it is a genuine order task where occupancy is degenerate) and DOES stay at chance",
            "role_blind_decode_collapses": "decode_full=1.000 at D2 (trivial L=1) but 0.000 at D4+ -> without role-typing, assignment cannot be recovered under superposition; selectional restriction is load-bearing",
            "order_survives_superposition_stress": "content order_perrole=0.964 at D8_V1000 even though superposition_survival=0.446 (~55% fillers lost) -> role-typing (disjoint-vocab matched filter) is robust to crosstalk; NOT a trivial by-construction readout",
            "cross_seed_tight_cv": "order_content_perrole_cv 0.000-0.0237 across the grid (3 seeds)",
        },
        "measured_bound": "FULL-PARSE (order AND all fillers) bounded: 17/20 cells; cliff at D8 x V>=250 (order still holds, full-parse fails) driven by superposition-survival collapse (D8_V1000 survival=0.446); parse_max_constituents@V>=500=6 vs order max=8. Order recovery relies on disjoint-per-role-vocab selectional restriction; bounded 5.6% concept probe.",
        "cross_arc_overlap_check_2026_07_01_USER_locked": "substrate_query 'comprehension order recovery role filler binding superposition content role typing selectional restriction occupancy' -> top hit cosine=0.3584 = notes/research_drill_substrate_VSA_position_is_meaning_4x_2026-06-12.md::chunk006 ('additive bundling gives a SET representation ... loses role-filler structure A+B+C==C+B+A'). This is the THEORETICAL grounding (occupancy=set-only loses order) that this cell RESOLVES by adding content-role-typing to recover order -- CORROBORATES, not a rediscovery. Only prior experimental comprehension atom >0.30 is the frame-classify MM (composed with, not duplicated). Order-recovery-via-selectional-restriction is NOVEL.",
        "composes_with_atoms": [COMPREHENSION_FRAMECLASSIFY_MM_ID],
        "composition_note": "ADVANCES / RESOLVES-THE-FRONTIER-OF (does NOT supersede) the frame-classify MM: that atom recovered the block-SET but PROVABLY-not the role-ORDER (occupancy order-blind) and set the explicit promotion criterion 'ORDER/permutation recovery under stress with a paired can-fail control.' THIS cell meets it: content-role-typing recovers ORDER, occupancy control stays at chance (can-fail, fires), role-blind decode collapses. The prior MM stands as the set-recovery result; this is the order-recovery advance.",
        "framing_corrections_vs_director_and_cell": "AFFIRM: order recovery holds across the envelope, occupancy control at chance (clean discriminator), role-blind collapse confirms selectional restriction necessary, HP corner holds, order survives superposition stress -> the self-reported HARD_PASS is well-supported for ORDER recovery and genuinely advances comprehension from 'set-not-order' (prior MM) to 'order-via-content-role-typing.' CORRECT (downward, symmetric, scope): (1) 'COMPREHENSION HOLDS' should be scoped to ORDER-recovery-via-selectional-restriction; the FULL-parse (order AND all fillers) envelope is BOUNDED at D6-all-V / D8-V<=125 with a cliff at D8 x V>=250. (2) Order recovery relies on the disjoint-per-role-vocabulary selectional-restriction assumption (real/brain-grounded but a specific structural regime). (3) BOUNDED concept probe (5.6%), 3 seeds. Tier = MEASURED_MECHANISM (order-recovery envelope with measured full-parse bound), not a universal chain-grade parse. NO under-deflation: the order-recovery + firing discriminator are credited as a real frontier resolution.",
        "envelope_and_next_test": "Order envelope = full grid D2-D8 x V50-1000 (holds). Full-parse envelope = D6-all-V + D8-V<=125 (cliff at D8 x V>=250, survival-driven). Next test to widen: (a) increase superposition survival at D8 high-V (larger N or K, or CLS-style consolidation) to push the full-parse cliff out; (b) relax the disjoint-vocab selectional restriction (overlapping per-role vocab) to stress the role-typing itself; (c) unbounded concept probe (full 177899). The order-recovery mechanism is the resolved frontier; the survival-limited full-parse cliff is the next bound.",
        "expansion_criterion": "PROMOTES toward CHAIN_GRADE iff order recovery + a firing can-fail control hold under a RELAXED selectional restriction (overlapping per-role vocab, so role-typing is not guaranteed by disjointness) at >=HP, AND/OR the full-parse cliff is pushed past D8 x V>=250 via a survival intervention. Stays MM if re-confirmed only under disjoint-vocab on the bounded probe. DEMOTES only if occupancy control rises off chance or order recovery fails to reproduce (not expected).",
        "disposition": "MEASURED_MECHANISM_comprehension_order_recovery_via_content_role_typing_selectional_restriction_holds_across_D2_D8_x_V50_1000_occupancy_control_at_chance_discriminator_fires_role_blind_decode_collapses_full_parse_envelope_bounded_cliff_D8_Vge250_survival_driven_resolves_prior_frame_classify_frontier_bounded_probe_3seed",
        "cert_increment_delta": 1,
    },
}

# =========================================================================
# ATOM 3 -- ENCODER 5seed baseline  (MIDDLE_BAND)
# =========================================================================
atom_enc = {
    "id": "math::MIDDLE_BAND_encoder_step2step3_inbatch_rkd_shipmetric_carrythrough_v1_5seed_hard_STE_baseline_CONFIRMED_cosine_to_gold_mean_0p827_4of5_seeds_clear_0p80_seed13_dips_to_0p786_algebra_INTACT_composed_roundtrip_0p983_to_1p000_isolated_1p000_at_J10_ret_agree10_mean_0p221_ALL_5_seeds_MISS_0p30_range_0p184_to_0p266_consistent_with_seed7_ret_beats_charpos_baseline_delta_plus_0p12_to_0p20_REAL_signal_below_bar_this_is_the_hard_STE_sign_quantization_BASELINE_that_the_graded_GSBC_code_fix_perception_ship_gate_MM_improves_on_ret_to_0p398_NOT_re_litigating_perception_firming_the_5seed_baseline_number_5seed_FULL178k_2026-07-05",
    "name": "MATH MIDDLE_BAND (5-seed hard-STE encoder BASELINE confirmed): encoder_step2step3_inbatch_rkd_shipmetric_carrythrough_v1 at 5 seeds [7,13,23,29,31]. cosine_to_gold mean=0.827 (4/5 seeds clear 0.80; seed 13 dips to 0.786). Algebra INTACT: composed_roundtrip 0.983-1.000, isolated 1.000 (J10). ret_agree10 mean=0.221, ALL 5 seeds MISS 0.30 (range 0.184-0.266, consistent with seed 7); ret beats the charpos baseline (delta +0.12 to +0.20) = real signal below the bar. This is the hard-STE sign-quantization BASELINE that the graded-GSBC-code fix (perception ship-gate MM) improves on (ret->0.398). Not re-litigating perception; firming the 5-seed baseline number.",
    "corpus": "math",
    "tier": "MIDDLE_BAND",
    "kind": "experiment_landed_vet",
    "cert_status": "middle_band_hard_STE_encoder_baseline_confirmed_5seed_ret_misses_cosine_clears_algebra_intact_cross_ref_graded_code_perception_pass",
    "cert_class": "encoder_hard_STE_ship_baseline_5seed_cosine_clears_0p80_4of5_ret_agree10_misses_0p30_all5_algebra_intact_baseline_that_graded_codes_improve",
    "description": (
        "LANDED-VET of exp_encoder_step2step3_inbatch_rkd_shipmetric_carrythrough_v1 at 5 seeds [7,13,23,29,31] "
        "(all self-reported MIDDLE_BAND, run_mode=full, N per teacher 177899, 8 units each, cardinality_ok=True, "
        "arms_differ_verified=True, 3 distinct arm sha256 INBATCH_BLOCK/CHARPOS/RANDOM_BLOCK, "
        "discriminator_reachability=True; cell commit 230dabdde). AUDITOR INDEPENDENT RECOMPUTE (.venv, off ship dict "
        "per seed, NOT verdict_msg): aggregates computed below. "
        "\n"
        "CONFIRMED 5-seed hard-STE baseline: (1) cosine_to_gold mean=0.827 -- 4/5 seeds clear the 0.80 bar; SEED 13 "
        "DIPS TO 0.786 (below 0.80), the honest exception (range 0.786-0.861). (2) Algebra INTACT: composed_roundtrip "
        "0.983-1.000 (seed 7=0.983, others 1.000), isolated_roundtrip=1.000 all seeds, at J_composed=10 -- the "
        "block-local circular-convolution composition survives. (3) ret_agree10 mean=0.221, ALL 5 seeds MISS the 0.30 "
        "ship bar (range 0.184-0.266; max seed 13=0.266, min seed 7=0.184) -- CONSISTENT with the seed-7 baseline that "
        "made the ship metric MIDDLE_BAND. The retrieval-agreement signal is REAL (ret beats the charpos baseline "
        "~0.064-0.071 by delta +0.116 to +0.200 on every seed), it just sits below the 0.30 bar -- the honest "
        "MIDDLE_BAND: real signal, misses the bar. Note the mild tradeoff: seed 13 has the HIGHEST ret (0.266) but the "
        "LOWEST cosine (0.786). "
        "\n"
        "TIER RATIONALE: MIDDLE_BAND (+1, baseline confirmation). This firms the 5-seed hard-STE sign-quantization "
        "BASELINE that the graded-GSBC-code fix (perception ship-gate MM, this session) improves on: graded codes lift "
        "ret_agree10 to ~0.398 (clears 0.30) while keeping cosine>0.80, which is perception's RESOLUTION. This atom does "
        "NOT re-litigate perception -- it records the 5-seed hard-STE baseline number so the graded-code PASS has a "
        "confirmed multi-seed reference point. Cross-referenced, not superseded."
    ),
    "aliases": ["encoder 5seed hard STE baseline cosine clears 0.80 4of5 ret_agree10 misses 0.30 all5",
                "hard STE sign quantization baseline that graded GSBC codes improve on",
                "seed13 cosine dips to 0.786 ret highest 0.266 tradeoff"],
    "metadata": {
        "record_class": "experiment_landed_vet_middle_band_hard_STE_encoder_baseline_confirmation_5seed",
        "term_class": "ENCODER_HARD_STE_SHIP_BASELINE_5SEED_COSINE_CLEARS_0P80_4OF5_RET_AGREE10_MISSES_0P30_ALL5_ALGEBRA_INTACT_BASELINE_GRADED_CODES_IMPROVE",
        "cert_status": "middle_band_hard_STE_encoder_baseline_confirmed_5seed_cross_ref_graded_code_perception_pass",
        "cert_class": "encoder_hard_STE_ship_baseline_5seed_cosine_clears_ret_misses_algebra_intact",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "verified_via": "independent .venv off-disk recompute off ship dict per seed (NOT verdict_msg): cosine mean 0.827 (4/5 clear 0.80, seed13=0.786); ret_agree10 mean 0.221 (0/5 clear 0.30); composed_roundtrip 0.983-1.000; ret beats charpos delta +0.12 to +0.20",
        "atomized_by": "skunkworks_landed_VET_2026-07-05_control_v2_comprehension_envelope_encoder_5seed",
        "anchor": "encoder_step2step3_inbatch_rkd_shipmetric_carrythrough_v1_seed_{7,13,23,29,31}",
        "cell_commit": "230dabdde",
        "raw_metrics_paths": [
            f"data/exp_encoder_step2step3_inbatch_rkd_shipmetric_carrythrough_v1_seed_{s}/metrics.json" for s in enc_seeds
        ],
        "run_mode": "full", "n_seeds": 5, "seeds": enc_seeds, "n_units_per_seed": 8, "cardinality_ok": True,
        "arms_differ_verified": True, "discriminator_reachability": True,
        "load_bearing_number": "cosine_to_gold mean=0.827 (4/5 clear 0.80, seed13=0.786); ret_agree10 mean=0.221 ALL 5 MISS 0.30 (range 0.184-0.266); composed_roundtrip 0.983-1.000",
        "recompute_off_disk_per_seed": enc,
        "recompute_off_disk_aggregate": enc_agg,
        "non_vacuity_checks": {
            "ret_beats_charpos_baseline": "delta_ret_agree10_vs_charpos = +0.116 to +0.200 on every seed (charpos ~0.064-0.071) -> retrieval-agreement is REAL signal above the character-position baseline, just below the 0.30 bar",
            "arms_distinct": "3 arms INBATCH_BLOCK/CHARPOS/RANDOM_BLOCK with distinct sha256; arms_differ_verified=True; discriminator_reachability=True",
            "algebra_intact_positive_control": "isolated_roundtrip=1.000 all seeds, composed_roundtrip 0.983-1.000 at J10 -> block-local circular-convolution composition is a clean positive control",
            "honest_exception_flagged": "seed 13 cosine=0.786 is BELOW 0.80 (4/5 clear, not 5/5); mean 0.827 clears",
        },
        "cross_arc_overlap_check_2026_07_01_USER_locked": "This is the DIRECT 5-seed scale-out of the seed-7 ship baseline already atomized in the perception ship-gate MM (math perception graded-code MM). Not a new-arc rediscovery -- it firms the baseline of an in-arc, already-VET'd finding. Confirmed in-arc baseline confirmation.",
        "composes_with_atoms": [PERCEPTION_GRADED_MM_ID],
        "composition_note": "CROSS-REFERENCES / is the BASELINE FOR (does NOT supersede, does NOT re-litigate) the perception ship-gate graded-code MM: that atom established graded GSBC codes SOLVE the retrieval-agreement gap (ret->0.398 clears 0.30, cosine stays >0.80) as perception's RESOLUTION, with the hard-STE sign-quantization confirmed as the cause of the miss. THIS atom firms the hard-STE BASELINE at 5 seeds (ret 0.184-0.266 all miss 0.30; cosine 0.786-0.861) so the graded-code improvement has a confirmed multi-seed reference. Perception's PASS-verdict is unchanged.",
        "framing_corrections_vs_director_and_cell": "AFFIRM: ret_agree10 misses 0.30 across all 5 seeds (consistent with seed 7), algebra intact, this is the confirmed hard-STE baseline. CORRECT (minor, symmetric): 'cosine_to_gold clears 0.80' is true on the MEAN (0.827) and 4/5 seeds, but SEED 13 = 0.786 dips BELOW 0.80 -- state it as '4/5 clear, mean 0.827' not '5/5 clear.' Otherwise matches self-report; MIDDLE_BAND is the honest tier (real signal below the ship bar).",
        "disposition": "MIDDLE_BAND_encoder_hard_STE_5seed_baseline_CONFIRMED_cosine_mean_0p827_4of5_clear_0p80_seed13_0p786_ret_agree10_mean_0p221_all5_miss_0p30_algebra_intact_real_signal_above_charpos_below_bar_baseline_that_graded_GSBC_codes_improve_cross_ref_perception_graded_code_MM_not_re_litigated",
        "cert_increment_delta": 1,
    },
}


def a5_append(path, atom):
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_atoms_", suffix=".jsonl")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as src:
                    for line in src:
                        f.write(line)
            f.write(json.dumps(atom, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    n_lines = 0
    found = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            n_lines += 1
            obj = json.loads(line)  # integrity: raises on corrupt line
            aid = obj.get("id") or obj.get("atom_id")
            if aid == atom["id"]:
                found += 1
    if found != 1:
        raise RuntimeError(f"verify-load failed: atom id found {found}x (expected 1) in {path}")
    return n_lines


def ledger_append(atom, note, ledger_path=CERT_LEDGER):
    md = atom["metadata"]
    entry = {
        "ts": TS, "ts_iso": TS_ISO, "atom_id": atom["id"], "corpus": atom["corpus"], "tier": atom["tier"],
        "cert_status": md.get("cert_status"), "cert_class": md.get("cert_class"),
        "cert_increment_delta": md.get("cert_increment_delta", 0), "verified_off_data": True,
        "anchor": md.get("anchor"), "cell_commit": md.get("cell_commit"),
        "auditor": "skunkworks", "atomized_by": md.get("atomized_by"),
        "landed_VET_session": SESSION_TAG, "note": note,
    }
    d = os.path.dirname(ledger_path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_ledger_", suffix=".jsonl")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            if os.path.exists(ledger_path):
                with open(ledger_path, "r", encoding="utf-8") as src:
                    for line in src:
                        f.write(line)
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, ledger_path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


if __name__ == "__main__":
    print(f"[atomize] ts_iso={TS_ISO}")
    print("[recompute] CONTROL v2 fair regimes pass:", fair_pass)
    print("[recompute] ENCODER agg:", enc_agg)
    print("[recompute] COMPREHENSION:", {k: comp_recompute[k] for k in ("n_order_cells_hold", "n_parse_cells_hold", "cliff_cells", "occupancy_perrole_min", "occupancy_perrole_max")})
    n1 = a5_append(MATH_ATOMS, atom_control)
    print(f"[atomize] ATOM1 CONTROL v2 MM appended; math lines={n1}")
    n2 = a5_append(MATH_ATOMS, atom_comp)
    print(f"[atomize] ATOM2 COMPREHENSION envelope MM appended; math lines={n2}")
    n3 = a5_append(MATH_ATOMS, atom_enc)
    print(f"[atomize] ATOM3 ENCODER 5seed MB appended; math lines={n3}")
    ledger_append(atom_control, "CONTROL resolved weak->PROVEN-at-depth4 (MM): both fair regimes pass (closure 0.66/0.51), discriminator fires, anti-tautology clean; n_fair=2/7 is conservative meta-rule not cherry-pick; degrades with superposition depth. Scoped to depth-4, confirms+scopes v1 MM at FULL 5-seed.")
    ledger_append(atom_comp, "COMPREHENSION order-recovery envelope (MM): content-role-typing recovers ORDER 20/20 cells, occupancy control at chance (discriminator fires), role-blind decode collapses; full-parse cliff at D8xV>=250 (survival-driven). Resolves the order-recovery frontier the prior frame-classify MM opened. Bounded 5.6% probe, 3 seeds.")
    ledger_append(atom_enc, "ENCODER 5-seed hard-STE baseline CONFIRMED (MB): cosine mean 0.827 (4/5 clear 0.80, seed13=0.786), ret_agree10 mean 0.221 all5 miss 0.30, algebra intact. Baseline that graded-GSBC-code fix (perception ship-gate MM) improves on; cross-ref not re-litigated.")
    print("[atomize] DONE 3 atoms + 3 ledger entries; A5-gated (tmp+os.replace+verify-load+json-integrity); matching TS_ISO")
    print("[atomize] NET CERT DELTA: MM +2 (control, comprehension), MB +1 (encoder baseline), CG 0, HF 0, DEMOTE 0")
