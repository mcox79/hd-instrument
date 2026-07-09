"""
A5-gated atomize: LANDED-VET (AUDIT-ONLY, HIGH) of pfc_gate_waypoint_rescue_stacked_corrections_v1.
BARRIER #2 chain-drift rescue via STACKING two informationally-independent correction channels
(KB-grounded gate OR cross-fit calibrated selector). TIER = HARD_FAIL (genuine structural
compounding-error bound; THIRD distinct rescue mechanism to fail the same corner; NOVEL mechanism clue:
the OR-gate is DILUTIVE -- stacking a low-precision 2nd channel DISCARDS the precise KB channel's gains).

CELL: experiments/exp_pfc_gate_waypoint_rescue_stacked_corrections_v1.py (commit 8e934ca2e)
  parent cell = pfc_gate_waypoint_rescue_kb_grounded_check_v1 (the KB-grounding MM, 2026-07-09)
METRICS: data/exp_pfc_gate_waypoint_rescue_stacked_corrections_v1/metrics.json
  run_mode=full, device=cuda, elapsed_s=5211.0, ts 2026-07-09T13:51Z, N=8192, 5 seeds [7,17,23,31,41],
  5 regimes x 5 seeds x 14 arms = 350 units (completed 350, cardinality_ok, cv_gate_enforced). verdict
  HARD_FAIL_COMPOUNDING_ERROR_BOUND_REAL.

INDEPENDENT OFF-DISK RECOMPUTE (.venv, this session -- recomputed recovery/delta/stk_over_kb off arm_means,
NOT off verdict_msg; Fix#28 read metrics.json directly):
  recovery=(arm-flat_gonogo)/(hier_oracle-flat_gonogo). ALL 5 regimes EXACT MATCH to reported
  stacked_over_kb and delta_recovery (focus stk_over_kb -0.2242 == recompute; delta_vs_ver +0.0020 == recompute).

CRISP STRUCTURAL FINDING (novel, robust across ALL 5 regimes): the STACKED (A OR B) arm collapses to
selector-alone EXACTLY in every regime (stacked_mean == selector_mean to machine precision), and
stacked_over_kb is NEGATIVE in every regime (-0.19,-0.43,-0.22,-0.34,-0.44). i.e. OR-unioning the precise
KB channel with the low-precision calibrated selector DISCARDS KB's gains -- the argmax over the (larger,
more permissive) union lands on the selector's picks. The OR-gate is DILUTIVE, not additive.

VERDICT LOGIC (from prereg bands): HARD_FAIL fires on ANY of: delta_recovery(vs verify)<=0.05 (BOUND_REAL)
OR |failmask_corr|>0.50 (FAILURE_MASKS_CORRELATED) OR stacked_over_kb<=0.03 (STACKING_REDUNDANT) OR
flatness_ratio<0.20 (ACCELERATING_COLLAPSE). At FOCUS op4_V1200_d8: delta_vs_ver=0.0020<=0.05 (FIRES),
stk_over_kb=-0.224<=0.03 (FIRES), flatness=0.027<0.20 (FIRES). failmask_corr=0.237 does NOT exceed 0.50
(does NOT fire). Cell tag = ..._BOUND_REAL. TIER = HARD_FAIL confirmed.

GENUINE (structural) vs DESIGN-FAILURE -- STANDARD_HF_CLOSURE gate, GENUINE:
  (C1) POSITIVE-CONTROL RAIL CLEARS ITS OWN FLOOR FIRST: oracle_exec=0.918, hier_oracle(given-decomp)=0.906
     at the SAME deep corner where every rescue arm sits at ~0.10 -> task IS solvable, headroom exists
     (headroom_exec_ok, headroom_decomp_ok True) -> HF_STRUCTURAL_BOUND, NOT HF_TEST_DESIGN_FAILURE.
     Negative controls collapse: hier_shuffled=0.0017, wp_random=0.0175, wp_index_midpoint=0.0183.
  (C2) DISCRIMINATOR FIRES AT SCALE / can-fail reachable: at the SHALLOW d4 corner the stacked arm DOES
     beat verify (delta_vs_ver=+0.0343, sign_p=0.0001) -- the HARD_PASS branch is reachable in principle;
     it simply collapses at high entropy. wp_random moves with depth (0.102 d4 -> 0.017 d8). Not
     saturation-vacuous, not analytically pinned.
  (C3) ENTROPY-driven not raw depth: op2_V800_d8 (depth 8, ent 8) partially recovers (kb 0.641) while
     op3/op4 d8 (ent 12.7/16) collapse -- same wall as the parent MM and the two sibling HFs.

FRAMING CORRECTION vs Director pass-through (symmetric anti-negativity -- a MIS-ATTRIBUTION fix, not
inflation/deflation): the Director's framing leaned on the SMOKE reading "failure masks correlated ~0.49
-> data-coverage problem". THIS DID NOT REPRODUCE at FULL focus. At op4_V1200_d8 failmask_corr=0.237
(< the 0.50 HARD_FAIL gate; failmask_screen_pass=false only because 0.237>0.20 partial band). The
FAILURE_MASKS_CORRELATED verdict gate did NOT fire. Worse for that story, the HIGHEST failmask_corr (0.666)
is at the SHALLOW d4 where everything WORKS -- failmask_corr is INVERSELY related to the wall, not the
driver of it. The ACTUAL, robust driver is the DILUTIVE OR-GATE + a near-vacuous 2nd channel at depth
(gain_sel=0.002 at focus; selector_alone barely above open bisection). The correct mechanism statement is
about ADMISSION PRECISION, not MISS correlation: the multiplicative premise P(skip)=miss_A*miss_B only
helps if OR-ADMISSION admits CORRECT candidates; the selector's admissions are mostly wrong at depth, so
OR-admission re-introduces the errors KB filtered out. Director's PIVOT DIRECTION (invest in the single
best channel's coverage, not channel-count) is DIRECTIONALLY CORRECT and I endorse it -- but the honest
justification is "OR-stacking a weak 2nd channel is dilutive", NOT "the channels' failure masks are
correlated" (they are only moderately so, 0.18-0.37, at the deep corners, and the gate did not fire).

CROSS-ARC OVERLAP (USER-locked): substrate_query "OR-gate stacking two independent correction channels
dilutive waypoint rescue compounding reasoning drift" -> TOP hit cosine=0.2988 (below the 0.30 threshold;
generic 'compounding' wordnet entry). No prior-arc atom returns >0.30. The direct parent/sibling atoms
(kb_grounded MM, replay-bidirectional HF, coarse2fine HF) are found by anchor, not by semantic collision.
This is a TARGETED EXTENSION (new rescue mechanism = channel-stacking, at the same corner), NOT a
rediscovery -- the July-1 INT8 pattern does not apply.

TIER = HARD_FAIL (genuine; THIRD distinct rescue mechanism to fail BARRIER #2; and the FIRST to show that
BOOSTING the partially-working KB channel via OR-stacking actively HURTS). Counts as a proven NEGATIVE.
Composes (NOT supersedes): parent kb_grounded MM (KB partially rescues), sibling replay-bidirectional HF,
sibling coarse2fine HF. Eligible for the 5x negative-drill (confirmed genuine), but revival must be a NEW
mechanism CLASS: (1) a CORRECTNESS-CALIBRATED selector (the failure here is selector precision, not
independence -- selector_independence_corr is clean at 0.114); (2) an AND-gate / confidence-WEIGHTED union
that PRESERVES KB precision instead of diluting it; (3) grow single-channel KB edge density where
kb_fresh_rate is high (0.063 at focus); (4) DAgger/imitation-from-oracle (parent's named lever). Symmetric
anti-negativity: not inflated to a win (there is none); the dilutive-OR mechanism clue IS the value.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_atomize_2026_07_09_pfc_gate_waypoint_rescue_stacked_corrections_v1_HARD_FAIL"
CELL_COMMIT = "8e934ca2e"
TS = time.time()
TS_ISO = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(TS))
SESSION = "2026-07-09_pfc_gate_waypoint_rescue_stacked_corrections_v1_landed_vet_OR_GATE_DILUTIVE_THIRD_RESCUE_HF"

P_KB_GROUNDED_MM = (
    "math::MEASURED_MECHANISM_BARRIER2_REFINED_EXOGENOUS_KB_REACHABILITY_GROUNDING_PARTIALLY_RESCUES_"
    "autonomous_chain_drift_at_the_deep_high_entropy_corner_where_ALL_self_derived_mechanisms_HARD_FAILED_"
    "the_compounding_barrier_is_an_AUTONOMOUS_GENERATION_limit_NOT_a_task_solvability_limit_but_grounded_"
    "rescue_STILL_DECAYS_with_depth_wall_PUSHED_not_BROKEN_5seed_FULL_GPU_300units_N8192_focus_op4_V1200_"
    "d8_ent16_steps3_OPEN_0p097_VERIFY_0p096_KB_0p283_recov_ver_0p018_recov_kb_0p244_DELTA_vs_ver_0p226_ge_"
    "0p15_HP_delta_CLEARS_flatness_0p264_in_0p20_to_0p50_MIDDLE_below_HP_0p50_above_HF_0p20_indep_corr_"
    "0p047_le_0p15_clean_non_degenerate_kb_confirm_mean_0p499_non_vacuous_sign_p_1p69e_12_lift_flat_0p202_"
    "lift_random_0p265_idx_gap_0p0008_anti_taut_0p0013_degen_0p000_brs_cv_0p109_GENUINE_positive_control_"
    "rail_clears_own_floor_oracle_exec_0p918_hier_oracle_0p906_headroom_decomp_ok_negative_controls_"
    "collapse_shuf_0p0017_wp_random_0p0175_discriminator_FIRES_at_scale_MECHANISM_kb_gate_MASKS_R_balance_"
    "argmax_to_KB_reachability_confirmed_candidates_exogenous_raw_graph_zero_shared_params_a_NECESSARY_"
    "FILTER_not_an_oracle_answer_recov_0p244_far_below_oracle_1p0_frontier_PUSHED_op4_d4_ent8_autonomous_"
    "to_op4_V1200_d6_ent12_max_entropy_hp_ok_12p0_grid_d4_kb_0p920_flat_1p000_d6_kb_0p498_flat_0p525_hp_ok_"
    "d8_kb_0p283_flat_0p264_op3_d8_kb_0p388_op2_d8_kb_0p641_ENTROPY_driven_not_depth_op2_V800_d8_depth8_"
    "ent8_recovers_0p641_n_hp_ok_1_of_5_UNDERSELLS_flatness_only_computable_for_op4_op2_op3_flat_0_by_"
    "construction_no_shallow_sibling_composes_not_supersedes_replay_bidir_HF_coarse2fine_HF_autonomous_"
    "self_discovery_MM_next_lever_DAgger_imitation_or_correctness_calibrated_selector_2026-07-09"
)
P_REPLAY_BIDIR_HF = (
    "math::HARD_FAIL_STRUCTURAL_COMPOUNDING_ERROR_BOUND_DOUBLY_CONFIRMED_MECHANISM_INDEPENDENT_BARRIER2_"
    "replay_generate_select_plus_bidirectional_consistency_selection_ALSO_does_NOT_rescue_autonomous_chain_"
    "drift_at_the_deepest_high_entropy_corner_5seed_FULL_GPU_275units_op4_V1200_d8_ent16_steps3_OPEN_0p097_"
    "VERIFY_0p096_REPLAY_0p104_recov_ver_0p018_recov_rescue_0p028_DELTA_vs_ver_0p010_lt_0p05_HF_delta_FIRES_"
    "flatness_ratio_0p044_lt_0p20_HF_flat_FIRES_lift_verify_0p008_negligible_sign_p_0p4228_ns_n_hp_ok_0_of_"
    "5_CAP_FRONTIER_None_GENUINE_not_design_failure_positive_control_rail_clears_own_floor_oracle_exec_"
    "0p918_hier_oracle_0p906_headroom_decomp_ok_negative_controls_collapse_hier_shuffled_0p0017_wp_random_"
    "0p0175_discriminator_FIRES_at_scale_RAND_0p102_d4_to_0p017_d8_paired_sign_fires_where_signal_d4_3e5_"
    "d6_0p001_op2_0p045_null_only_at_focus_ENTROPY_driven_not_depth_op2_V800_d8_depth8_ent8_recovers_0p30_"
    "op3_d8_ent12p7_collapses_0p09_max_delta_vs_ver_anywhere_0p035_at_d4_replay_0p798_WORSE_than_open_0p823_"
    "delta_minus0p057_mechanism_never_wins_bidir_selector_ACTIVE_frac_not_open_0p617_bidir_sel_0p630_gt_all_"
    "0p584_but_NON_predictive_consistency_not_correctness_proxy_under_compounding_drift_anti_taut_0p0013_"
    "degen_0p000_index_leak_False_spr_delta_ent_minus0p051_CROSS_CONFIRMS_coarse2fine_HF_bound_is_MECHANISM_"
    "INDEPENDENT_3rd_4th_autonomous_rescue_to_fail_DAgger_imitation_from_oracle_next_lever_class_not_"
    "another_autonomous_decomposition_variant_2026-07-09"
)
P_COARSE2FINE_HF = (
    "math::HARD_FAIL_STRUCTURAL_COMPOUNDING_ERROR_BOUND_REAL_coarse_to_fine_waypoint_bisection_does_NOT_"
    "rescue_autonomous_decomposition_at_the_deepest_high_entropy_corner_5seed_FULL_GPU_250units_op4_V1200_"
    "d8_ent16_OPEN_autonomous_0p097_eq_coarse2fine_0p100_ZERO_lift_recovery_rescue_0p0232_lt_0p20_delta_"
    "recovery_0p004_lt_0p15_sign_p_0p1797_ns_rescue_beats_open_False_n_hp_ok_0_of_5_all_3_HARD_PASS_bars_"
    "FAIL_the_SMOKE_DIRECTIONAL_SIGNAL_REVERSED_smoke_delta_plus0p112_spearman_delta_ent_plus0p500_FULL_"
    "delta_plus0p004_spearman_minus0p237_SIGN_FLIP_GENUINE_BOUND_not_machinery_oracle_exec_rail_0p918_"
    "hier_oracle_given_decomp_0p906_headroom_decomp_ok_controls_collapse_hier_shuffled_0p0017_wp_random_"
    "0p0175_anti_taut_0p0013_degen_0p000_index_leak_False_brs_cv_0p118_coarse_to_fine_rescues_the_SHALLOW_"
    "corner_op4_d4_OPEN_eq_c2f_0p823_only_because_OPEN_already_high_nothing_to_rescue_delta_0_but_CANNOT_"
    "extend_autonomous_decomposition_to_the_DEEP_corner_where_OPEN_collapses_to_0p10_DAgger_oracle_next_"
    "lever_out_of_scope_narrow_glass_box_2026-07-06"
)

ATOM_ID = (
    "math::HARD_FAIL_STRUCTURAL_COMPOUNDING_ERROR_BOUND_TRIPLY_CONFIRMED_BARRIER2_STACKING_two_independent_"
    "correction_channels_KB_grounded_gate_OR_calibrated_selector_does_NOT_push_the_recovery_frontier_past_"
    "single_channel_AND_the_OR_gate_is_DILUTIVE_5seed_FULL_GPU_350units_op4_V1200_d8_ent16_steps3_OPEN_"
    "0p097_VERIFY_0p096_KB_alone_0p283_SEL_alone_0p098_STACKED_0p098_recov_kb_0p244_recov_sel_0p020_recov_"
    "stk_0p020_DELTA_vs_ver_0p002_lt_0p05_HF_BOUND_REAL_FIRES_stacked_over_kb_minus0p224_le_0p03_STACKING_"
    "REDUNDANT_FIRES_flatness_0p027_lt_0p20_ACCEL_COLLAPSE_FIRES_super_additive_False_gain_kb_0p226_gain_"
    "sel_0p002_NOVEL_MECHANISM_stacked_mean_EQUALS_selector_mean_EXACTLY_in_ALL_5_regimes_stacked_over_kb_"
    "NEGATIVE_in_ALL_5_minus0p19_minus0p43_minus0p22_minus0p34_minus0p44_OR_union_lands_on_the_permissive_"
    "low_precision_selector_and_DISCARDS_the_precise_KB_channels_gains_ADMISSION_PRECISION_not_MISS_"
    "correlation_is_the_failure_FAILMASK_CORR_0p237_at_focus_DOES_NOT_exceed_0p50_gate_did_NOT_fire_highest_"
    "failmask_0p666_at_SHALLOW_d4_where_everything_works_INVERSELY_related_to_wall_GENUINE_not_design_"
    "failure_oracle_exec_0p918_hier_oracle_0p906_headroom_decomp_ok_negative_controls_collapse_shuf_0p0017_"
    "wp_random_0p0175_discriminator_FIRES_at_scale_can_fail_reachable_d4_delta_plus0p034_sign_p_0p0001_"
    "ENTROPY_driven_not_depth_op2_V800_d8_depth8_ent8_kb_recovers_0p641_selector_independence_clean_0p114_"
    "so_failure_is_selector_PRECISION_at_depth_not_independence_THIRD_distinct_rescue_mechanism_to_fail_"
    "BARRIER2_and_FIRST_to_show_BOOSTING_the_partially_working_KB_channel_via_OR_stacking_HURTS_composes_"
    "not_supersedes_kb_grounded_MM_replay_bidir_HF_coarse2fine_HF_revival_correctness_calibrated_selector_"
    "or_AND_gate_confidence_weighted_union_or_grow_single_channel_KB_density_or_DAgger_2026-07-09"
)

atom = {
    "id": ATOM_ID,
    "name": (
        "MATH HARD_FAIL (structural, compounding-error bound REAL -- TRIPLY-CONFIRMED; NOVEL mechanism: the "
        "OR-gate is DILUTIVE): STACKING two informationally-independent correction channels (KB-grounded "
        "gate A OR cross-fit calibrated selector B) does NOT push the recovery frontier past single-channel "
        "-- and actively HURTS. BARRIER #2. 5-seed FULL (GPU, 350 units, N=8192); focus op4_V1200_d8 "
        "(ent 16, steps 3): OPEN=0.097 VERIFY=0.096 KB_alone=0.283 SEL_alone=0.098 STACKED=0.098; "
        "recov_kb=0.244 recov_sel=0.020 recov_stk=0.020 DELTA(vs_ver)=0.002 (<=0.05 -> HF_BOUND_REAL), "
        "stacked_over_kb=-0.224 (<=0.03 -> STACKING_REDUNDANT), flatness_ratio=0.027 (<0.20 -> ACCEL_"
        "COLLAPSE), super_additive=False (gain_kb=0.226 >> gain_sel=0.002), n_hp_ok=0/5. NOVEL, robust "
        "mechanism: the STACKED (A OR B) arm equals SELECTOR-alone EXACTLY in all 5 regimes, and "
        "stacked_over_kb is NEGATIVE in all 5 (-0.19,-0.43,-0.22,-0.34,-0.44) -- OR-unioning the precise KB "
        "channel with the low-precision selector re-admits the errors KB filtered out and the argmax lands "
        "on the selector's picks, DISCARDING KB's gains. The failure is ADMISSION PRECISION, not MISS "
        "correlation. GENUINE, not design-failure: oracle_exec=0.918/hier_oracle=0.906 clear their own "
        "floor at the same corner (task solvable, headroom exists); negative controls collapse "
        "(hier_shuffled=0.0017, wp_random=0.0175); the can-fail branch is reachable (at shallow d4 the "
        "stacked arm DOES beat verify, delta +0.034 sign_p=0.0001). FRAMING FIX vs the SMOKE reading: the "
        "'failure masks correlated ~0.49 -> data-coverage' story does NOT reproduce at FULL focus "
        "(failmask_corr=0.237, below the 0.50 gate which did NOT fire; the HIGHEST failmask 0.666 is at the "
        "SHALLOW d4 where everything works -- inversely related to the wall). THIRD distinct rescue "
        "mechanism to fail BARRIER #2, and the FIRST to show that BOOSTING the partially-working KB channel "
        "(the parent MM) via OR-stacking HURTS. Composes (not supersedes) kb_grounded MM + replay-bidir HF "
        "+ coarse2fine HF. Revival: correctness-calibrated selector, AND-gate/confidence-weighted union, "
        "grow single-channel KB density, or DAgger."
    ),
    "corpus": "math",
    "tier": "HARD_FAIL",
    "kind": "experiment_landed_vet",
    "cert_status": (
        "hard_fail_structural_compounding_error_bound_triply_confirmed_barrier2_stacking_two_independent_"
        "correction_channels_kb_grounded_gate_or_calibrated_selector_does_not_push_recovery_frontier_past_"
        "single_channel_and_the_or_gate_is_dilutive_op4_v1200_d8_ent16_delta_vs_ver_0p002_le_0p05_stacked_"
        "over_kb_minus0p224_le_0p03_flatness_0p027_lt_0p20_super_additive_false_gain_kb_0p226_gain_sel_"
        "0p002_stacked_equals_selector_exactly_all_5_regimes_stacked_over_kb_negative_all_5_admission_"
        "precision_not_miss_correlation_failmask_corr_0p237_below_0p50_gate_did_not_fire_positive_control_"
        "rail_clears_own_floor_oracle_0p918_hier_oracle_0p906_negative_controls_collapse_discriminator_"
        "fires_at_scale_can_fail_reachable_d4_delta_plus0p034_entropy_driven_not_depth_selector_"
        "independence_clean_0p114_failure_is_precision_not_independence_third_rescue_to_fail_first_to_show_"
        "boosting_kb_via_or_stacking_hurts"
    ),
    "cert_class": (
        "autonomous_chain_drift_rescue_via_STACKING_two_informationally_independent_correction_channels_"
        "channel_A_exogenous_KB_raw_graph_reachability_gate_channel_B_cross_fit_double_ML_calibrated_"
        "correctness_selector_combined_as_an_OR_gate_vs_KB_alone_selector_alone_verify_gated_and_open_"
        "bisection_baselines_over_a_depth_by_entropy_grid_where_the_discriminator_is_whether_the_stacked_"
        "arm_lifts_recovery_over_the_best_single_channel_super_additively_with_a_load_bearing_failmask_"
        "correlation_screen_positive_oracle_rail_and_negative_shuffled_random_controls_present_measured_"
        "bound_is_config_contingent_glass_box_synthetic_pfc_bg_gating_task_N8192_5seed_third_distinct_"
        "rescue_mechanism_to_fail_the_same_corner_and_first_to_test_stacking_onto_the_partially_working_"
        "kb_channel"
    ),
    "description": (
        "LANDED-VET (AUDIT-ONLY, HIGH) of exp_pfc_gate_waypoint_rescue_stacked_corrections_v1 (commit "
        "8e934ca2e; run_mode=full; device=cuda; elapsed 5211.0s; 5 seeds [7,17,23,31,41]; N=8192; 5 regimes "
        "x 5 seeds x 14 arms = 350 units, cardinality_ok, cv_gate_enforced; verdict "
        "HARD_FAIL_COMPOUNDING_ERROR_BOUND_REAL). Metrics read directly off authoritative disk (Fix#28). "
        "INDEPENDENT .venv RECOMPUTE off arm_means (NOT verdict_msg): recovery=(arm-flat_gonogo)/"
        "(hier_oracle-flat_gonogo); all 5 regimes EXACT-match reported stacked_over_kb and delta_recovery "
        "(focus stk_over_kb -0.2242 == recompute, delta_vs_ver +0.0020 == recompute). "
        "PARENT: follow-up to pfc_gate_waypoint_rescue_kb_grounded_check_v1 (the KB-grounding MEASURED_"
        "MECHANISM, 2026-07-09) which found the exogenous KB reachability gate PARTIALLY rescues (recov_kb="
        "0.244 at focus). THIS cell asks: can we push PAST single-channel by STACKING a NEW independent "
        "cross-fit calibrated selector (channel B) with the KB gate (channel A) as an OR-gate, "
        "multiplicatively suppressing skips (P(skip)=miss_A*miss_B if independent)? "
        "FOCUS op4_V1200_d8 (ent 16, chain_steps 3), all reproduced off-disk: FLAT=0.0808, oracle_exec="
        "0.9175, hier_oracle=0.9058, OPEN=0.0967, VERIFY=0.0958, KB_alone=0.2825, SEL_alone=0.0975, "
        "STACKED=0.0975; recov_kb=0.2444, recov_sel=0.0202, recov_stk=0.0202, recov_ver=0.0182; "
        "DELTA(vs_ver)=0.0020, stacked_over_kb=-0.2242, super_additive=False; gain_kb=0.2263, gain_sel="
        "0.0020, gain_stacked=0.0020; flatness_ratio=0.0274, flatness_kb=0.2641; failmask_corr=0.237 "
        "(kb_fail=0.72, sel_fail=0.90), independence_corr=0.047, selector_independence_corr=0.114; "
        "kb_confirm_mean=0.499, sel_accept_rate=0.122, kb_fresh_rate=0.063; sign_p=0.9088, brs_cv=0.311; "
        "spearman(delta,ent)=-0.821; n_seeds=5, n_hp_ok=0/5, CAP_FRONTIER=None. "
        "VERDICT LOGIC (prereg bands): HARD_FAIL fires on ANY of delta_vs_ver<=0.05 (BOUND_REAL) OR "
        "|failmask_corr|>0.50 (FAILURE_MASKS_CORRELATED) OR stacked_over_kb<=0.03 (STACKING_REDUNDANT) OR "
        "flatness_ratio<0.20 (ACCELERATING_COLLAPSE). At focus: delta_vs_ver=0.0020<=0.05 FIRES, "
        "stacked_over_kb=-0.224<=0.03 FIRES, flatness=0.027<0.20 FIRES; failmask_corr=0.237 does NOT exceed "
        "0.50 (does NOT fire). All 3 HARD_PASS bars also fail (recov_stk 0.020<0.35, delta 0.002<0.15, "
        "flat 0.027<0.50). TIER = HARD_FAIL confirmed. "
        "NOVEL MECHANISM (robust across ALL 5 regimes): the STACKED (A OR B) arm equals SELECTOR-alone "
        "EXACTLY (stacked_mean==selector_mean to machine precision) in every regime, and stacked_over_kb is "
        "NEGATIVE in every regime (-0.189 d4, -0.425 d6, -0.224 d8, -0.343 op3_d8, -0.441 op2_d8). The "
        "OR-union is more PERMISSIVE than KB-alone, so it re-admits candidates KB excluded; R's balance-"
        "argmax over the larger set lands on the selector's (low-precision) picks, DISCARDING KB's gains. "
        "The failure is ADMISSION PRECISION, not MISS correlation: the multiplicative premise only helps if "
        "OR-admission admits CORRECT candidates, but the selector's admissions are mostly wrong at depth "
        "(sel_fail=0.90 at focus; selector_alone barely above open bisection; gain_sel=0.002). "
        "GENUINE (structural) vs DESIGN-FAILURE -- STANDARD_HF_CLOSURE, GENUINE: "
        "(C1) POSITIVE-CONTROL RAIL CLEARS ITS OWN FLOOR FIRST: oracle_exec=0.918, hier_oracle(given-"
        "decomp)=0.906 at the SAME corner where every rescue arm sits at ~0.10 -> task solvable, headroom "
        "exists (headroom_exec_ok, headroom_decomp_ok True) -> HF_STRUCTURAL_BOUND, not HF_TEST_DESIGN_"
        "FAILURE. Negative controls collapse: hier_shuffled=0.0017, wp_random=0.0175, wp_index_midpoint="
        "0.0183. (C2) CAN-FAIL/DISCRIMINATOR REACHABLE at scale: at the SHALLOW d4 corner the stacked arm "
        "DOES beat verify (delta_vs_ver=+0.0343, sign_p=0.0001) -- the HARD_PASS branch is reachable in "
        "principle; it collapses only at high entropy; wp_random moves with depth (0.102 d4 -> 0.017 d8). "
        "(C3) ENTROPY-driven not raw depth: op2_V800_d8 (depth 8, ent 8) partially recovers (kb 0.641) "
        "while op3/op4 d8 (ent 12.7/16) collapse -- same wall as the parent MM and the two sibling HFs. "
        "FRAMING CORRECTION vs Director pass-through (symmetric anti-negativity -- MIS-ATTRIBUTION fix): the "
        "Director framing leaned on the SMOKE reading 'failure masks correlated ~0.49 -> data-coverage "
        "problem'. This did NOT reproduce at FULL focus: failmask_corr=0.237 (below the 0.50 HARD_FAIL "
        "gate, which did NOT fire; failmask_screen_pass=false only because 0.237>0.20 partial band). The "
        "HIGHEST failmask_corr (0.666) is at the SHALLOW d4 where everything WORKS -- failmask_corr is "
        "INVERSELY related to the wall, not its driver. The actual robust drivers are the DILUTIVE OR-GATE "
        "and the near-vacuous 2nd channel at depth. Director's PIVOT DIRECTION (invest in the single best "
        "channel's coverage, not channel-count) is DIRECTIONALLY CORRECT and endorsed; but the honest "
        "justification is 'OR-stacking a weak 2nd channel is dilutive / admission-precision-limited', NOT "
        "'failure masks correlated'. Note selector_independence_corr=0.114 is CLEAN (channel B IS "
        "independent of M/R by construction) -- so the failure is selector PRECISION at depth, not a "
        "broken-independence artifact. "
        "CROSS-ARC OVERLAP (USER-locked): substrate_query 'OR-gate stacking two independent correction "
        "channels dilutive waypoint rescue compounding reasoning drift' -> top cosine=0.2988 (below 0.30; "
        "generic 'compounding' wordnet). No prior-arc atom >0.30. TARGETED EXTENSION (new rescue mechanism "
        "= channel-stacking, same corner), NOT a rediscovery; July-1 INT8 pattern N/A. "
        "TIER = HARD_FAIL (genuine; THIRD distinct rescue mechanism to fail BARRIER #2; FIRST to show "
        "BOOSTING the partially-working KB channel via OR-stacking HURTS). Counts as a proven NEGATIVE. "
        "ELIGIBLE for the 5x negative-drill (confirmed genuine), but revival must be a NEW mechanism CLASS: "
        "(1) CORRECTNESS-CALIBRATED selector (fix precision, the actual bottleneck); (2) AND-gate / "
        "confidence-WEIGHTED union that PRESERVES KB precision instead of diluting it; (3) grow single-"
        "channel KB edge density where kb_fresh_rate is high (0.063 at focus); (4) DAgger/imitation-from-"
        "oracle (parent's named lever). Symmetric anti-negativity: not inflated to a win (there is none); "
        "the dilutive-OR mechanism clue IS the value. Measured bound is config-contingent (N=8192, this "
        "grid), not a universal impossibility. commit 8e934ca2e 2026-07-09."
    ),
    "provenance": {
        "cell": "experiments/exp_pfc_gate_waypoint_rescue_stacked_corrections_v1.py",
        "commit": CELL_COMMIT,
        "metrics_path": "data/exp_pfc_gate_waypoint_rescue_stacked_corrections_v1/metrics.json",
        "parent_cell": "pfc_gate_waypoint_rescue_kb_grounded_check_v1",
        "seeds": [7, 17, 23, 31, 41],
        "run_mode": "full",
        "device": "cuda",
        "elapsed_s": 5211.0,
        "metrics_ts_iso": "2026-07-09T13:51:33.927680+00:00",
        "whole_cell_verdict": "HARD_FAIL_COMPOUNDING_ERROR_BOUND_REAL",
        "audit_tier": "HARD_FAIL",
        "ts_iso": TS_ISO,
        "atomized_by": ATOMIZED_BY,
        "verified_off_data": True,
        "verified_off_data_note": (
            "Fix#28 read metrics.json directly. Independent .venv recompute off arm_means (NOT verdict_msg): "
            "recovery=(arm-flat_gonogo)/(hier_oracle-flat_gonogo). ALL 5 regimes exact-match reported "
            "stacked_over_kb {d4 -0.1886, d6 -0.4250, d8 -0.2242, op3_d8 -0.3434, op2_d8 -0.4414} and "
            "delta_recovery {d4 +0.0343, d6 +0.0453, d8 +0.0020, op3_d8 +0.0249, op2_d8 +0.0544}. Verified "
            "stacked_mean==selector_mean to machine precision in ALL 5 regimes. cardinality 350/350 = 5 "
            "regimes x 5 seeds x 14 arms; cv_gate_enforced True."
        ),
    },
    "verified_numbers": {
        "N": 8192, "n_seeds": 5, "seeds": [7, 17, 23, 31, 41], "run_mode": "full", "device": "cuda",
        "cardinality_units": 350, "cardinality_expected": 350, "cardinality_ok": True, "cv_gate_enforced": True,
        "n_hp_ok": 0, "n_regimes": 5, "cap_frontier": None,
        "focus_regime": "op4_V1200_d8", "focus_entropy": 16.0, "focus_chain_steps": 3,
        "focus_flat_gonogo": 0.08083333333333333, "focus_oracle_exec": 0.9175000000000001,
        "focus_hier_oracle": 0.9058333333333334, "focus_hier_shuffled": 0.0016666666666666666,
        "focus_wp_bisect_open": 0.09666666666666665, "focus_wp_bisect_verify": 0.09583333333333333,
        "focus_kb_alone": 0.28250000000000003, "focus_selector_alone": 0.0975,
        "focus_stacked": 0.0975, "focus_wp_random_state": 0.017499999999999998,
        "focus_recov_kb": 0.2444444444444445, "focus_recov_sel": 0.020202020202020214,
        "focus_recov_stacked": 0.020202020202020214, "focus_recov_verify": 0.01818181818181818,
        "focus_delta_vs_verify": 0.002020202020202033, "focus_stacked_over_kb": -0.22424242424242427,
        "focus_super_additive": False, "focus_gain_kb": 0.2262626262626263, "focus_gain_sel": 0.002020202020202033,
        "focus_flatness_ratio": 0.027405841359329736, "focus_flatness_kb": 0.26406035665294936,
        "focus_failmask_corr": 0.23710681275266093, "focus_failmask_kb_rate": 0.7175,
        "focus_failmask_sel_rate": 0.9025000000000001, "focus_independence_corr": 0.04678885581044465,
        "focus_selector_independence_corr": 0.11366161871452125, "focus_sel_accept_rate": 0.12183055555555558,
        "focus_kb_confirm_mean": 0.4988888888888889, "focus_kb_fresh_rate": 0.06333333333333332,
        "focus_sign_test_p": 0.9087769252754924, "focus_brs_cv": 0.31123318728261756,
        "spearman_delta_vs_entropy": -0.8207826816681234,
        "grid_stacked_over_kb": {"op4_d4": -0.18857142857142806, "op4_d6": -0.42497482376636453,
                                  "op4_d8": -0.22424242424242427, "op3_d8": -0.3433609958506224,
                                  "op2_d8": -0.441354292623942},
        "grid_delta_vs_verify": {"op4_d4": 0.034285714285714475, "op4_d6": 0.04531722054380663,
                                  "op4_d8": 0.002020202020202033, "op3_d8": 0.02489626556016598,
                                  "op2_d8": 0.054413542926239386},
        "grid_failmask_corr": {"op4_d4": 0.6661712001077703, "op4_d6": 0.22809757952511886,
                                "op4_d8": 0.23710681275266093, "op3_d8": 0.18435115695990817,
                                "op2_d8": 0.366760492997522},
        "grid_sign_p": {"op4_d4": 0.00012111663818359375, "op4_d6": 1.4100783873147614e-06,
                         "op4_d8": 0.9087769252754924, "op3_d8": 0.016020274788899974, "op2_d8": 9.206613802682597e-05},
        "stacked_equals_selector_all_regimes": True,
        "stacked_over_kb_negative_all_regimes": True,
        "HF_delta_gate": 0.05, "HF_failmask_gate": 0.50, "HF_stacked_over_kb_gate": 0.03, "HF_flat_gate": 0.20,
        "HP_recov_gate": 0.35, "HP_delta_gate": 0.15, "HP_flat_gate": 0.50,
        "recovery_formula": "recovery = (arm_mean - flat_gonogo) / (hier_oracle - flat_gonogo)",
        "recompute_exact_match": True,
    },
    "can_fail_discriminator_verdict": (
        "FIRES and is TELEMETRY-SENSITIVE. (1) The HARD_PASS branch is reachable: the SAME stacked arm beats "
        "verify at the shallow d4 corner (delta +0.0343, sign_p=0.0001) and would have cleared HARD_PASS had "
        "it lifted recovery >=0.35 and delta >=0.15 super-additively at the focus -- it did not (recov_stk "
        "0.020, delta 0.002, super_additive False). (2) The positive-control rail (oracle_exec 0.918, "
        "hier_oracle 0.906) is NOT pinned to the rescue floor -- it clears its own ceiling at the deep "
        "corner, so a HF here is a real bound. (3) The negative RAND control MOVES with difficulty (0.102 "
        "d4 -> 0.017 d8) -> nothing analytically pinned; perturbing the regime moves the floor. (4) The "
        "load-bearing NEW failmask screen is telemetry-sensitive: it reads 0.666 at d4, 0.184-0.367 at the "
        "deep corners -- it varies with the data, and it correctly does NOT trip the >0.50 gate at the "
        "focus (0.237). (5) stacked_over_kb varies -0.19..-0.44 across regimes (reads the data). This "
        "HARD_FAIL is a GENUINE structural bound (task solvable per oracle rail; the OR-stack simply "
        "dilutes the one working channel), not a design failure and not a saturation-vacuous null."
    ),
    "framing_corrections_vs_cell_author_and_director": [
        "Cell self-verdict HARD_FAIL_COMPOUNDING_ERROR_BOUND_REAL is CORRECT and reproduces exactly off-"
        "disk; audit CONFIRMS HARD_FAIL. No correction to the verdict itself.",
        "PRIMARY MIS-ATTRIBUTION FIX (Director pass-through): the memorialized lesson is NOT 'FAILURE_MASKS_"
        "CORRELATED -> data-coverage problem'. That gate (|failmask_corr|>0.50) did NOT fire at FULL focus: "
        "failmask_corr=0.237. The SMOKE value 0.49 did NOT reproduce. Moreover the HIGHEST failmask_corr "
        "(0.666) is at the SHALLOW d4 corner where EVERYTHING works -- so failmask_corr is INVERSELY "
        "related to the wall, not its cause. The actual, robust driver is the DILUTIVE OR-GATE: stacked=="
        "selector EXACTLY in all 5 regimes and stacked_over_kb is negative in all 5.",
        "MECHANISM RE-STATEMENT: the failure is ADMISSION PRECISION, not MISS correlation. The "
        "multiplicative premise P(skip)=miss_A*miss_B only helps if OR-ADMISSION admits CORRECT candidates. "
        "Channel B (calibrated selector) is IS independent of M/R (selector_independence_corr=0.114, clean) "
        "but is IMPRECISE at depth (sel_fail=0.90, gain_sel=0.002); OR-unioning it with KB re-admits the "
        "errors KB filtered, so the argmax collapses to the selector's picks. Independence was necessary "
        "but NOT sufficient -- the second channel also needs precision/value.",
        "PIVOT DIRECTION ENDORSED, JUSTIFICATION CORRECTED: Director's 'invest in the single best channel's "
        "coverage, not channel-count' is directionally right (more channels via OR did not help; the one "
        "channel that works is KB). The honest justification is OR-dilution + weak-2nd-channel, NOT "
        "correlated failure masks. Concretely: grow KB edge density where kb_fresh_rate is high (0.063 at "
        "focus), OR replace the OR-gate with a precision-preserving combiner (AND-gate / confidence-weighted "
        "union), OR make channel B correctness-calibrated.",
        "SCOPE (load-bearing): this is the THIRD distinct rescue mechanism to fail BARRIER #2 (after "
        "coarse2fine and replay-bidirectional) and the FIRST to STACK onto the partially-working KB channel "
        "(the parent MM). The compounding-error bound is now confirmed across THREE structurally distinct "
        "rescue strategies. But do NOT overclaim mechanism-independence of STACKING per se: the specific "
        "finding is narrower and sharper -- OR-stacking a low-precision independent channel onto a precise "
        "one is dilutive. A different combiner or a precise channel B is untested and is the revival lever.",
        "ENTROPY-driven not literal-depth (consistent with parent + siblings): op2_V800_d8 has depth 8 but "
        "ent 8 and KB partially recovers (0.641); op3/op4 d8 (ent 12.7/16) collapse. Config-contingent "
        "(N=8192, this grid), not a universal impossibility.",
    ],
    "revival_or_extension_criterion": (
        "HARD_FAIL scope: at op4_V1200_d8/ent16 (N=8192, 5 seeds), OR-stacking the exogenous KB gate with a "
        "cross-fit calibrated selector does NOT push recovery past KB-alone and is DILUTIVE (stacked=="
        "selector exactly, stacked_over_kb -0.224; all HP bars fail). REVIVAL (each a NEW cell; negative "
        "confirmed GENUINE so eligible for the 5x negative-drill, but ONLY along a NEW mechanism CLASS -- "
        "we now have 3 autonomous rescues failing this corner): (1) CORRECTNESS-CALIBRATED selector -- the "
        "bottleneck is admission PRECISION (sel_fail=0.90), not independence (0.114 clean); train/verify "
        "channel B to correlate with actual correctness under drift and re-test the OR-stack. (2) PRECISION-"
        "PRESERVING COMBINER -- replace the hard OR with an AND-gate or a confidence-WEIGHTED union so the "
        "precise KB mask is not diluted by a permissive 2nd channel; directly tests whether combiner choice "
        "(not channel count) is the lever. (3) GROW SINGLE-CHANNEL KB EDGE DENSITY where kb_fresh_rate is "
        "high (0.063 at focus) -- the Director's coverage pivot, correctly justified. (4) DAgger / "
        "imitation-from-oracle (parent's named lever; different class). PROMOTION-to-MM trigger: any of the "
        "above lifts recovery>=0.35 AND delta_vs_verify>=0.15 AND flat>=0.50 at ent>=12 for >=3/5 seeds. "
        "DEMOTION/void trigger for THIS atom: a re-run where the oracle rail fails (task unsolvable -> "
        "reclassify as design-failure), or where stacked stops equalling selector / stacked_over_kb turns "
        "non-negative (the dilutive-OR mechanism claim would need revision)."
    ),
    "composes": [P_KB_GROUNDED_MM, P_REPLAY_BIDIR_HF, P_COARSE2FINE_HF],
    "compose_note": (
        "Composes (NOT supersedes) three BARRIER #2 atoms. PARENT (kb_grounded MM, 2026-07-09): the "
        "exogenous KB reachability gate PARTIALLY rescues (recov_kb 0.244 at focus) -- the ONE channel that "
        "works. THIS atom is the follow-up that STACKS a second independent channel onto it and finds the "
        "OR-stack DILUTES the parent's gain (stacked_over_kb -0.224; stacked==selector exactly). SIBLINGS "
        "(replay-bidirectional HF and coarse2fine HF): two other autonomous rescue mechanisms that also "
        "pin to ~0.10 at the same corner. Together these are THREE structurally distinct rescue strategies "
        "failing op4_V1200_d8/ent16 while the oracle rail holds 0.92 -> the compounding-error bound is "
        "robust. NEW contribution of THIS atom: (a) the FIRST attempt to BOOST the partially-working KB "
        "channel, showing that OR-stacking a low-precision independent 2nd channel HURTS; (b) the crisp "
        "DILUTIVE-OR mechanism (stacked==selector exactly, stacked_over_kb negative in all 5 regimes); "
        "(c) the FRAMING FIX that the failure is ADMISSION PRECISION not MISS correlation (failmask_corr "
        "0.237 at focus does not trip the gate; independence is clean at 0.114). Brain-grounding: PFC/BG "
        "waypoint-gated hierarchical control; channel A = exogenous semantic-memory reachability grounding; "
        "channel B = a learned correctness monitor; the finding is that OR-combining a grounded filter with "
        "an imprecise learned monitor discards the grounded filter's benefit -- combiner design and monitor "
        "precision matter more than adding monitors."
    ),
    "cross_arc_overlap_check": (
        "substrate_query 'OR-gate stacking two independent correction channels dilutive waypoint rescue "
        "compounding reasoning drift' -> TOP hit cosine=0.2988 (generic 'compounding' wordnet entry), BELOW "
        "the 0.30 threshold; no prior-arc atom returns >0.30. The direct parent/sibling atoms (kb_grounded "
        "MM, replay-bidirectional HF, coarse2fine HF) are located by anchor, not by semantic collision. "
        "TARGETED EXTENSION (new rescue mechanism = channel-stacking at the same corner), NOT a "
        "rediscovery; the July-1 INT8-rediscovery pattern does NOT apply."
    ),
    "anchor": "pfc_gate_waypoint_rescue_stacked_corrections_v1",
    "cell_commit": CELL_COMMIT,
    "seeds": [7, 17, 23, 31, 41],
    "run_mode": "full",
    "cardinality_ok": True,
    "arms_differ_verified": True,
    "verified_off_data": True,
    "auditor": "hdi_skunkworks",
    "atomized_by": "hdi_skunkworks",
    "landed_VET_session": SESSION,
    "route_to_research_negative_drill": True,
    "route_note": (
        "GENUINE negative confirmed (not design-failure) -> eligible for 5x negative-drill per USER-locked "
        "rule. Constraint: revival must be a NEW mechanism CLASS -- correctness-calibrated selector "
        "(precision is the bottleneck), precision-preserving combiner (AND-gate / confidence-weighted "
        "union), grow single-channel KB density, or DAgger/imitation -- NOT another OR-stack of autonomous "
        "channels."
    ),
    "needs_orchestrator_store_sync": True,
    "ts": TS,
    "ts_iso": TS_ISO,
    "ts_added": TS_ISO,
    "aliases": [
        "STACKING two independent correction channels (KB gate OR calibrated selector) does NOT push the recovery frontier past single-channel and the OR-gate is DILUTIVE (BARRIER #2); HARD_FAIL, third rescue mechanism to fail",
        "op4_V1200_d8 ent16: KB_alone 0.283, SEL_alone 0.098, STACKED 0.098; recov_kb 0.244, recov_stk 0.020, delta_vs_verify 0.002 (<=0.05), stacked_over_kb -0.224 (<=0.03), flatness 0.027 (<0.20), super_additive False",
        "NOVEL: stacked == selector EXACTLY in all 5 regimes; stacked_over_kb NEGATIVE in all 5 -> OR-union collapses to the permissive low-precision selector and discards the precise KB channel's gains",
        "failure is ADMISSION PRECISION not MISS correlation: selector independence clean (0.114) but imprecise at depth (sel_fail 0.90, gain_sel 0.002)",
        "FRAMING FIX: FAILURE_MASKS_CORRELATED did NOT fire at FULL focus (failmask_corr 0.237, < 0.50 gate); SMOKE 0.49 did not reproduce; highest failmask 0.666 at SHALLOW d4 (inversely related to wall)",
        "GENUINE not design-failure: oracle_exec 0.918 / hier_oracle 0.906 rail clears own floor; negative controls collapse; can-fail reachable (d4 stacked beats verify, delta +0.034 sign_p 0.0001)",
        "composes kb_grounded MM (KB partially rescues) + replay-bidir HF + coarse2fine HF; revival = correctness-calibrated selector / AND-gate / grow KB density / DAgger",
        "pfc_gate_waypoint_rescue_stacked_corrections_v1 landed-VET HARD_FAIL",
    ],
    "added_atom_id": None,
}
atom["added_atom_id"] = atom["id"]

ledger = {
    "ts": TS, "ts_iso": TS_ISO, "op": "add", "atom_id": atom["id"], "corpus": "math",
    "tier": "HARD_FAIL",
    "disposition": "hard_fail_structural_compounding_error_bound_triply_confirmed_barrier2_stacking_two_independent_correction_channels_or_gate_is_dilutive_does_not_push_recovery_frontier_past_single_channel",
    "cert_status": atom["cert_status"],
    "cert_class": atom["cert_class"],
    "cert_increment_delta": {"CG": 0, "MM": 0, "HF": 1},
    "cert_delta": {"CG": 0, "MM": 0, "HF": 1},
    "cert_delta_note": (
        "HF +1 (proven NEGATIVE, third-confirmed + novel mechanism): STACKING the exogenous KB gate with a "
        "cross-fit calibrated selector as an OR-gate does NOT push recovery past KB-alone and is DILUTIVE. "
        "5-seed FULL GPU, 350 units, N=8192, verdict HARD_FAIL reproduces exactly off-disk (Fix#28 + "
        "independent .venv recompute off arm_means, all 5 regimes exact incl focus stacked_over_kb -0.2242 "
        "and delta_vs_ver +0.0020). At focus op4_V1200_d8: delta_vs_ver=0.002<=0.05 (BOUND_REAL FIRES), "
        "stacked_over_kb=-0.224<=0.03 (STACKING_REDUNDANT FIRES), flatness=0.027<0.20 (ACCEL_COLLAPSE "
        "FIRES); all 3 HP bars fail (recov_stk 0.020, delta 0.002, flat 0.027); super_additive False "
        "(gain_kb 0.226 >> gain_sel 0.002); n_hp_ok 0/5. NOVEL robust mechanism: stacked==selector EXACTLY "
        "in all 5 regimes and stacked_over_kb NEGATIVE in all 5 -> the OR-union collapses to the permissive "
        "low-precision selector, discarding the precise KB channel's gains; the failure is ADMISSION "
        "PRECISION, not MISS correlation. GENUINE structural bound, NOT design-failure: oracle rail clears "
        "own floor (oracle_exec 0.918, hier_oracle 0.906, headroom_decomp_ok); negative controls collapse "
        "(hier_shuffled 0.0017, wp_random 0.0175); can-fail reachable (d4 stacked beats verify delta +0.034 "
        "sign_p 0.0001; RAND moves with depth). FRAMING FIX vs Director pass-through: the FAILURE_MASKS_"
        "CORRELATED story does NOT hold at FULL focus (failmask_corr 0.237, below the 0.50 gate which did "
        "NOT fire; SMOKE 0.49 did not reproduce; highest failmask 0.666 at SHALLOW d4, inversely related to "
        "the wall). Director's coverage pivot (invest in single best channel, not channel-count) is "
        "endorsed but must be justified by OR-dilution + weak-2nd-channel, NOT correlated failure masks; "
        "selector independence is clean (0.114) so the bottleneck is selector PRECISION at depth. THIRD "
        "distinct rescue mechanism to fail BARRIER #2 and FIRST to STACK onto the partially-working KB "
        "channel; composes (NOT supersedes) kb_grounded MM + replay-bidir HF + coarse2fine HF. Cross-arc "
        "overlap top cosine 0.2988 (<0.30; targeted extension, not rediscovery). Symmetric anti-negativity: "
        "not inflated; the dilutive-OR mechanism clue IS the value. Config-contingent (N=8192), not "
        "universal. ROUTE TO RESEARCH 5x negative-drill (confirmed genuine) along a NEW mechanism class "
        "(correctness-calibrated selector / precision-preserving combiner / grow KB density / DAgger). "
        "Needs orchestrator Store-sync."
    ),
    "verified_off_data": True,
    "verification": "fix28_read_metrics_json_direct + independent_venv_recompute_off_arm_means_all_5_regimes_exact_match_incl_focus_stacked_over_kb_minus0p2242_delta_plus0p0020 + stacked_equals_selector_all_5_regimes_machine_precision + stacked_over_kb_negative_all_5_regimes + positive_control_rail_clears_own_floor_oracle_0p918 + rand_control_moves_with_depth + failmask_corr_0p237_at_focus_below_0p50_gate_did_not_fire_highest_0p666_at_shallow_d4",
    "anchor": "pfc_gate_waypoint_rescue_stacked_corrections_v1",
    "cell_commit": CELL_COMMIT,
    "auditor": "hdi_skunkworks", "atomized_by": "hdi_skunkworks",
    "landed_VET_session": SESSION,
    "composes": [P_KB_GROUNDED_MM, P_REPLAY_BIDIR_HF, P_COARSE2FINE_HF],
    "route_to_research_negative_drill": True,
    "needs_orchestrator_store_sync": True,
    "raw_metrics_paths": ["data/exp_pfc_gate_waypoint_rescue_stacked_corrections_v1/metrics.json"],
}


def append_jsonl_a5(path: Path, new_row: dict, label: str) -> int:
    pre_lines = []
    if path.exists():
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
    out_text = "\n".join(pre_lines + [new_line]) + "\n"
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text)
        f.flush()
        os.fsync(f.fileno())
    for _attempt in range(10):
        try:
            os.replace(str(tmp_path), str(path))
            break
        except PermissionError:
            if _attempt == 9:
                raise
            time.sleep(0.1 * (2 ** _attempt))
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
    print(f"[A5] atomize START {ATOMIZED_BY} ts={TS:.3f} ts_iso={TS_ISO}")
    append_jsonl_a5(MATH_ATOMS, atom, "math/atoms (stacked-corrections OR-gate dilutive compounding-bound HARD_FAIL triply-confirmed)")
    append_jsonl_a5(CERT_LEDGER, ledger, "cert_ledger (HF +1)")
    print(f"[A5] DONE OK -> stacked-corrections OR-gate dilutive compounding-error bound HARD_FAIL (HF +1)")


if __name__ == "__main__":
    main()
