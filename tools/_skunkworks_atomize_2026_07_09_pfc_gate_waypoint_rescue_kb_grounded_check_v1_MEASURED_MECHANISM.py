"""
A5-gated atomize: LANDED-VET (AUDIT-ONLY, HIGH) of pfc_gate_waypoint_rescue_kb_grounded_check_v1.
BARRIER #2 exogenous-KB-grounding check (GPU). TIER = MEASURED_MECHANISM (proven bound): an EXOGENOUS
KB-reachability grounding channel PARTIALLY rescues autonomous chain-drift at the deep high-entropy
corner where ALL self-derived rescue mechanisms HARD_FAILED -> the compounding barrier is an
AUTONOMOUS-GENERATION limit, not a task-solvability limit. But the grounded rescue itself DECAYS with
depth (flatness 0.264 at ent16), so the wall is PUSHED (frontier entropy 8 -> 12), NOT BROKEN.

CELL: experiments/exp_pfc_gate_waypoint_rescue_kb_grounded_check_v1.py (commit 4f566616b)
  parent cell = pfc_gate_waypoint_rescue_replay_bidirectional_v1 (the replay+bidir BARRIER2 HF, 2026-07-09)
METRICS: data/exp_pfc_gate_waypoint_rescue_kb_grounded_check_v1/metrics.json
  run_mode=full, device=cuda, elapsed_s=5104.3, ts 2026-07-09T06:24:46Z, N=8192, 5 seeds [7,17,23,31,41],
  5 regimes x 5 seeds x 12 arms; completed 300/300 units, cardinality_ok. verdict
  MIDDLE_BAND_FLATNESS_BELOW_50.

INDEPENDENT OFF-DISK RECOMPUTE (.venv this session, off arm_means NOT verdict_msg; Fix#28):
  recovery = (arm_mean - flat_gonogo)/(hier_oracle - flat_gonogo); flatness = recov_rescue(d8)/recov_rescue(d4 sibling).
  ALL EXACT MATCH to 5 decimals. focus delta_recovery recompute 0.22626 == disk 0.22626;
  flatness recompute 0.26406 == disk 0.26406.

FOCUS op4_V1200_d8 (ent=16.0, chain_steps=3), reproduced:
  FLAT=0.0808 oracle_exec=0.9175 hier_oracle=0.9058 | OPEN=0.0967 VERIFY=0.0958 KB=0.2825
  recov_ver=0.0182 recov_kb=0.2444 DELTA(vs_ver)=0.2263 (>=0.15 HP_delta CLEARS) DELTA(vs_open)=0.2253
  flatness_ratio=0.2641 (in [0.20,0.50) -> MIDDLE: below HP 0.50, above HF 0.20)
  indep|corr|=0.0468 (<=0.15 clean, non-degenerate) kb_confirm_mean=0.499 (0.05<m<0.95 non-vacuous)
  lift_flat=0.2017 lift_random=0.2650 | idx_gap=0.0008 anti_taut=0.0013 degen=0.000 sign_p=1.69e-12 brs_cv=0.109
  n_seeds=5 n_hp_ok=1/5 CAP_FRONTIER=op4_V1200_d6 max_entropy_hp_ok=12.0 spr(delta,ent)=-0.205

VERDICT LOGIC (config gates): HARD_PASS needs recov>=0.20 AND delta>=0.15 AND flat>=0.50 AND |indep|<=0.15;
HARD_FAIL if delta<=0.05 OR |indep|>0.40 OR flat<0.20. Focus: delta_vs_ver=0.226>=0.15 (PASS-level),
|indep|=0.047<=0.15 (clean), recov_kb=0.244>=0.20 (PASS-level) BUT flat=0.264 in [0.20,0.50) -> neither
HP nor HF fires on flatness -> MIDDLE_BAND_FLATNESS_BELOW_50. Independent audit CONFIRMS the verdict.

SUB-AUDIT of the MIDDLE_BAND -> MEASURED_MECHANISM (proven bound), NOT HARD_PASS, NOT HARD_FAIL:
  - NOT HARD_PASS: flatness 0.264 < 0.50 -> the exogenous-grounded rescue DECAYS with depth (recov_kb
    0.926@d4 ent8 -> 0.486@d6 ent12 -> 0.244@d8 ent16). The wall is PUSHED to a new frontier (entropy 12,
    op4_d6 hp_ok=True), NOT removed. Also: the mechanism is EXOGENOUS-GROUNDING-ASSISTED, not autonomous
    problem-solving -> it does not warrant an autonomous-capability CG.
  - NOT HARD_FAIL: delta_vs_ver=0.226 >> HF_delta 0.05, sign_p=1.69e-12 (highly significant), recov_kb
    reaches 0.244 at the SAME corner where every self-derived mechanism (coarse2fine, replay, bidirectional,
    cerebellar rollout) sat at ~0.028 recovery. There IS material, clean lift -> the barrier is NOT
    depth-fundamental for the task.
  - PROVEN BOUND (MM): the exogenous-grounded rescue frontier is entropy 12; at entropy 16 grounded rescue
    still decays (flatness 0.264). This REFINES BARRIER #2: the compounding barrier is specific to
    AUTONOMOUS (self-derived) waypoint generation -- an exogenous reachability channel partially escapes it,
    but a residual depth cost remains even with grounding.

GENUINE-SIGNAL vs ARTIFACT adjudication -- all clean:
  (A1) Positive-control rail clears its own floor at the deep corner: oracle_exec=0.9175, hier_oracle
    (given-decomp)=0.9058, headroom_decomp_ok -> task solvable; a rescue COULD reach it. Negative controls
    collapse: hier_shuffled=0.0017, wp_random=0.0175, wp_index_midpoint=0.0183.
  (A2) Discriminator FIRES at scale, non-vacuous: arms separate cleanly (KB 0.283 vs verify 0.096 vs random
    0.017 at FOCUS); wp_random moves with depth (0.102@d4 -> 0.017@d8); paired sign test 1.69e-12.
  (A3) NOT a tautology / index-leak / oracle-answer leak: index_artifact_gap=0.0008 (index_leak False),
    anti_tautology_corr=0.0013, degenerate_rate=0.000. MECHANISM AUDIT (read code): wp_kb_grounded_gate
    MASKS the substrate's OWN R-balance argmax to KB-reachability-confirmed candidates (exogenous raw-graph
    reach_cum, ZERO shared params with R); it is a NECESSARY-condition FILTER, not the answer -- the drifting
    R-balance still chooses among confirmed candidates, so recovery is only 0.244 (far below oracle 1.0).
    NOT an oracle leak.
  (A4) INDEPENDENCE screen is the load-bearing honesty check and it is CLEAN AND non-degenerate:
    corr(kb_confirm_signal, m_error) = 0.047 at FOCUS (|corr|<=0.15), varies across regimes (-0.363@d4 to
    +0.214@op2_d8) so non-degenerate; independence_degenerate=False. The KB channel is informationally
    INDEPENDENT of the substrate's own error -> the lift is genuinely exogenous information, not re-use of
    R's own signal. kb_confirm_mean=0.499 (non-vacuous), kb_confirm_std=0.500, kb_fresh_rate=0.063,
    kb_fallback_rate=0.000.
  (A5) cross-seed cv gate: brs_cv=0.109 < 0.15; cardinality 300/300; cv_gate_enforced=True.

ENTROPY-driven, not literal depth (cross-confirms parent): op2_V800_d8 has DEPTH 8 but ENTROPY 8 and
recovers KB=0.641 (recov 0.591, delta_vs_ver 0.496); op4_V1200_d8 (depth 8, ent 16) KB=0.283. Same depth,
different entropy -> different outcome. NOTE the n_hp_ok=1/5 UNDERSELLS the capability: flatness_ratio is
only computable for op4 regimes (needs the chain_steps==1 d4 sibling); op2_d8 and op3_d8 get flatness=0 BY
CONSTRUCTION (no shallow sibling), so they cannot be hp_ok even though op2_d8 shows the STRONGEST grounded
recovery in the grid. So hp_ok=1/5 is a metric-coverage artifact, not evidence of a weak effect.

CROSS-ARC OVERLAP (USER-locked): substrate_query 'waypoint rescue depth wall barrier compounding autonomous
bisect KB grounding' -> TOP hit cosine=0.3584 is the autonomous-waypoint deep-corner compounding-error rescue
research note (SAME arc); the barrier-2 HF atoms sit in the same cluster. This is a TARGETED EXTENSION (a NEW
mechanism CLASS -- exogenous grounding -- at the same corner), NOT a rediscovery. The novelty is precisely
the exogenous-grounding partial-rescue that isolates the barrier as autonomous-generation-specific plus the
frontier-push measurement (entropy 8 -> 12) -- none of which the parent HF atoms carry.

TIER = MEASURED_MECHANISM (MM +1). A proven POSITIVE BOUNDARY that refines the barrier-#2 negative. Composes
(does NOT supersede) the replay-bidirectional HF (parent), the coarse2fine HF, and the autonomous
self-discovery MM. Symmetric anti-negativity: this is NOT inflated to a barrier-BREAK (flatness 0.264 says the
wall is pushed, not broken) and NOT deflated to a null (delta 0.226 is a real, clean, exogenous lift).
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_atomize_2026_07_09_pfc_gate_waypoint_rescue_kb_grounded_check_v1_MEASURED_MECHANISM"
CELL_COMMIT = "4f566616b"
TS = time.time()
TS_ISO = "2026-07-09T00:00:00Z"
SESSION = "2026-07-09_pfc_gate_waypoint_rescue_kb_grounded_check_v1_landed_vet_BARRIER2_EXOGENOUS_GROUNDING_PARTIAL_RESCUE_MM"

# parent cell atom (the replay+bidirectional BARRIER2 doubly-confirmed HARD_FAIL, 2026-07-09)
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
    "INDEPENDENT_3rd_4th_autonomous_rescue_to_fail_DAgger_imitation_from_oracle_next_lever_class_not_another_"
    "autonomous_decomposition_variant_2026-07-09"
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
P_AUTONOMOUS_SELF_DISCOVERY_MM = (
    "math::MEASURED_MECHANISM_CONTROL_autonomous_waypoint_SELF_DISCOVERY_is_a_REAL_DEPTH_ENTROPY_BOUNDED_"
    "capability_the_substrate_self_discovers_useful_bisection_waypoint_decompositions_at_LOW_MID_entropy_"
    "that_BEAT_flat_gonogo_AND_random_state_5seed_FULL_GPU_405units_3of9_regimes_CLEAR_pre_registered_HP_"
    "bands_op2_d6_ent6_lift_flat_plus0p188_op3_d4_ent6p3_plus0p118_op4_d4_ent8_plus0p284_all_sign_p_0p0000_"
    "recovery_ratio_0p48_to_0p69_lift_over_random_plus0p68_to_plus0p74_capability_FRONTIER_op4_d4_max_"
    "entropy_8p0_clean_guards_degenerate_0_anti_tautology_le0p018_index_leak_False_bwp_cv_le0p032_DOMAIN_"
    "FIT_bisection_BEATS_spectral_by_0p61_to_0p65_and_cluster_by_0p58_to_0p62_at_all_hp_ok_regimes_BUT_"
    "COLLAPSES_at_HIGH_entropy_ties_or_LOSES_to_flat_op4_d6_ent12_lift_minus0p003_op3_d8_ent12p7_minus0p023_"
    "op4_d8_ent16_FOCUS_minus0p012_spearman_recovery_vs_entropy_minus0p7615_monotone_decline_the_cell_own_"
    "verdict_HARD_FAIL_is_the_FOCUS_deepest_corner_gate_only_the_GRID_reveals_a_bounded_POSITIVE_capability_"
    "GENUINE_bound_not_machinery_oracle_exec_0p92_to_0p97_and_hier_oracle_given_decomp_0p92_to_0p96_at_"
    "EVERY_regime_headroom_decomp_ok_at_deep_corners_so_task_solvable_discovery_specifically_fails_deep_"
    "pairs_with_coarse2fine_rescue_HARD_FAIL_and_given_decomposition_control_MM_DAgger_oracle_next_lever_"
    "narrow_glass_box_2026-07-06"
)

ATOM_ID = (
    "math::MEASURED_MECHANISM_BARRIER2_REFINED_EXOGENOUS_KB_REACHABILITY_GROUNDING_PARTIALLY_RESCUES_"
    "autonomous_chain_drift_at_the_deep_high_entropy_corner_where_ALL_self_derived_mechanisms_HARD_FAILED_"
    "the_compounding_barrier_is_an_AUTONOMOUS_GENERATION_limit_NOT_a_task_solvability_limit_but_grounded_"
    "rescue_STILL_DECAYS_with_depth_wall_PUSHED_not_BROKEN_5seed_FULL_GPU_300units_N8192_focus_op4_V1200_d8_"
    "ent16_steps3_OPEN_0p097_VERIFY_0p096_KB_0p283_recov_ver_0p018_recov_kb_0p244_DELTA_vs_ver_0p226_ge_"
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

atom = {
    "id": ATOM_ID,
    "name": (
        "MATH MEASURED_MECHANISM (proven bound; BARRIER #2 REFINED): an EXOGENOUS KB-reachability grounding "
        "channel PARTIALLY rescues autonomous chain-drift at the deep high-entropy corner where ALL "
        "self-derived rescue mechanisms (coarse2fine, replay, bidirectional, cerebellar rollout) HARD_FAILED "
        "-> the compounding barrier is an AUTONOMOUS-GENERATION limit, NOT a task-solvability limit. But the "
        "grounded rescue STILL DECAYS with depth (flatness 0.264 at ent16) -> the wall is PUSHED (frontier "
        "entropy 8 -> 12), NOT BROKEN. 5-seed FULL (GPU, 300 units, N=8192); focus op4_V1200_d8 (ent 16, "
        "steps 3): OPEN=0.097 VERIFY=0.096 KB=0.283; recov_ver=0.018 recov_kb=0.244 DELTA(vs_ver)=0.226 "
        "(>=0.15, HP_delta clears), flatness_ratio=0.264 (in [0.20,0.50) -> MIDDLE: below HP 0.50, above HF "
        "0.20), |indep_corr|=0.047 (<=0.15, clean, non-degenerate), kb_confirm_mean=0.499 (non-vacuous), "
        "sign_p=1.69e-12, lift_flat=0.202, lift_random=0.265, n_hp_ok=1/5, CAP_FRONTIER=op4_V1200_d6, "
        "max_entropy_hp_ok=12.0. GENUINE: the positive-control rail clears its own floor at the same corner "
        "(oracle_exec=0.918, hier_oracle=0.906, headroom_decomp_ok); negative controls collapse (shuffled "
        "0.0017, random 0.0175); discriminator fires at scale. NOT an oracle-answer leak (mechanism audit): "
        "the KB gate MASKS the substrate's own R-balance argmax to KB-reachability-confirmed candidates "
        "(exogenous raw-graph reach_cum, ZERO shared params) -- a necessary-condition filter, not the answer, "
        "so recovery is only 0.244 (far below oracle 1.0). The independence screen is the load-bearing "
        "honesty check: corr(kb_confirm, m_error)=0.047 (independent, non-degenerate: -0.363@d4 to +0.214@"
        "op2) -> the lift is genuinely exogenous information. ENTROPY-driven not depth: op2_V800_d8 (depth 8, "
        "ent 8) recovers KB=0.641; op4_d8 (depth 8, ent 16) KB=0.283. n_hp_ok=1/5 UNDERSELLS -- flatness is "
        "only computable for op4 regimes (needs the d4 sibling); op2/op3 get flatness=0 by construction. "
        "REFINES BARRIER #2: an exogenous reachability channel partially escapes it, but a residual depth "
        "cost remains even with grounding. Next lever: DAgger/imitation-from-oracle or a "
        "correctness-calibrated selector."
    ),
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet",
    "cert_status": (
        "measured_mechanism_barrier2_refined_exogenous_kb_reachability_grounding_partially_rescues_autonomous_"
        "chain_drift_deep_high_entropy_corner_op4_v1200_d8_ent16_delta_vs_ver_0p226_ge_0p15_flatness_0p264_"
        "middle_below_0p50_above_0p20_recov_kb_0p244_indep_corr_0p047_clean_non_degenerate_kb_confirm_0p499_"
        "non_vacuous_sign_p_1p69e_12_lift_flat_0p202_lift_random_0p265_idx_gap_0p0008_anti_taut_0p0013_degen_"
        "0p000_brs_cv_0p109_positive_control_rail_clears_own_floor_oracle_0p918_hier_oracle_0p906_negative_"
        "controls_collapse_discriminator_fires_kb_gate_is_necessary_filter_not_oracle_answer_recov_far_below_"
        "oracle_frontier_pushed_entropy_8_to_12_barrier_is_autonomous_generation_specific_not_task_"
        "solvability_wall_pushed_not_broken_grounded_rescue_still_decays_with_depth"
    ),
    "cert_class": (
        "autonomous_chain_drift_rescue_via_an_exogenous_kb_reachability_grounding_channel_that_masks_the_"
        "substrates_own_R_balance_argmax_to_candidates_confirmed_reachable_in_the_raw_graph_zero_shared_"
        "params_with_R_vs_verify_gated_bisection_and_open_bisection_baselines_over_a_depth_by_entropy_grid_"
        "where_the_discriminator_is_whether_the_exogenously_grounded_arm_lifts_recovery_over_plain_verify_at_"
        "the_deep_high_entropy_corner_AND_whether_the_kb_confirm_signal_is_informationally_independent_of_the_"
        "substrates_own_error_positive_oracle_rail_and_negative_shuffled_random_controls_present_measured_"
        "bound_is_config_contingent_glass_box_synthetic_pfc_bg_gating_task_N8192_5seed_first_mechanism_to_"
        "materially_lift_the_deep_corner_after_four_autonomous_rescues_failed"
    ),
    "description": (
        "LANDED-VET (AUDIT-ONLY, HIGH) of exp_pfc_gate_waypoint_rescue_kb_grounded_check_v1 (commit 4f566616b; "
        "run_mode=full; device=cuda; elapsed 5104.3s; 5 seeds [7,17,23,31,41]; N=8192; 5 regimes x 5 seeds x "
        "12 arms; completed 300/300 units, cardinality_ok; cv_gate_enforced; verdict "
        "MIDDLE_BAND_FLATNESS_BELOW_50). Metrics read directly off authoritative disk (Fix#28). INDEPENDENT "
        ".venv RECOMPUTE off arm_means (NOT verdict_msg): recovery=(arm-flat_gonogo)/(hier_oracle-flat_gonogo), "
        "flatness=recov_rescue(d8)/recov_rescue(d4 sibling); focus delta_recovery recompute 0.22626 == disk "
        "0.22626, flatness recompute 0.26406 == disk 0.26406 (EXACT). "
        "PARENT: follow-up to pfc_gate_waypoint_rescue_replay_bidirectional_v1 (BARRIER2 doubly-confirmed HF, "
        "2026-07-09). All prior rescues were AUTONOMOUS (self-derived): coarse2fine+verify (HF 07-06), "
        "replay-generate-select + bidirectional-consistency (HF 07-09), cerebellar anticipatory rollout + "
        "lookahead bisection (synthesis 07-07). THIS cell tests a NEW mechanism CLASS: an EXOGENOUS "
        "KB-reachability grounding channel (kinetic-proofreading checkpoint). "
        "MECHANISM (read from code, lines 1046-1113): wp_kb_grounded_gate performs the same sequential "
        "bisection as wp_bisect_open but MASKS the R-balance argmax to only KB-reachability-CONFIRMED "
        "candidates (left leg reachable within seg_len of the anchor AND goal reachable within the remainder), "
        "using the raw-graph reachability tensor reach_cum -- an exogenous channel with ZERO shared params "
        "with the SR estimator R. Empty-confirmed rows RESET FRESH re-anchored at the immutable START; "
        "still-empty rows fall back to the open argmax (counted, kb_fallback_rate). This is a NECESSARY-"
        "condition FILTER, not the oracle answer: the drifting R-balance still chooses among confirmed "
        "candidates, so recovery reaches only 0.244 -- far below the given-decomposition oracle (1.0 by "
        "construction; hier_oracle absolute 0.906). "
        "FOCUS op4_V1200_d8 (ent 16, chain_steps 3), all reproduced off-disk: FLAT=0.0808, oracle_exec=0.9175, "
        "hier_oracle=0.9058, OPEN=0.0967, VERIFY=0.0958, KB=0.2825; recov_open=0.0192, recov_ver=0.0182, "
        "recov_kb=0.2444, DELTA(vs_ver)=0.2263 (>=0.15 HP_delta clears), DELTA(vs_open)=0.2253; "
        "flatness_ratio=0.2641 (in [0.20,0.50) -> MIDDLE); lift_flat=0.2017, lift_random=0.2650; "
        "|indep_corr|=0.0468, kb_confirm_mean=0.499, kb_confirm_std=0.500, kb_fresh_rate=0.063, "
        "kb_fallback_rate=0.000; index_artifact_gap=0.0008, anti_taut=0.0013, degen=0.000, sign_p=1.69e-12, "
        "brs_cv=0.109; n_seeds=5, n_hp_ok=1/5, CAP_FRONTIER=op4_V1200_d6, max_entropy_hp_ok=12.0, "
        "spr(delta,ent)=-0.205. "
        "VERDICT LOGIC (config gates): HARD_PASS needs recov>=0.20 AND delta>=0.15 AND flat>=0.50 AND "
        "|indep|<=0.15; HARD_FAIL if delta<=0.05 OR |indep|>0.40 OR flat<0.20. Focus: delta 0.226>=0.15 "
        "(PASS-level), |indep| 0.047<=0.15 (clean), recov 0.244>=0.20 (PASS-level), BUT flat 0.264 in "
        "[0.20,0.50) -> neither HP nor HF fires -> MIDDLE_BAND_FLATNESS_BELOW_50. Audit CONFIRMS. "
        "SUB-AUDIT -> MEASURED_MECHANISM (proven bound): NOT HARD_PASS (flatness 0.264<0.50: grounded rescue "
        "DECAYS with depth, recov_kb 0.926@d4 -> 0.486@d6 -> 0.244@d8; and the mechanism is grounding-ASSISTED "
        "not autonomous). NOT HARD_FAIL (delta 0.226>>0.05, sign_p 1.69e-12; recov 0.244 where every "
        "self-derived rescue sat at 0.028 -> the barrier is not depth-fundamental for the task). PROVEN BOUND: "
        "the exogenous-grounded rescue frontier is entropy 12; the barrier is autonomous-generation-specific; "
        "a residual depth cost persists even with grounding. "
        "GENUINE-SIGNAL adjudication -- all clean: (A1) positive-control rail clears its own floor at the deep "
        "corner (oracle_exec 0.918, hier_oracle 0.906, headroom_decomp_ok; negatives collapse hier_shuffled "
        "0.0017, wp_random 0.0175, wp_index_midpoint 0.0183). (A2) discriminator fires at scale (KB 0.283 vs "
        "verify 0.096 vs random 0.017; wp_random moves 0.102@d4 -> 0.017@d8; paired sign 1.69e-12). (A3) not a "
        "tautology/index-leak/oracle-answer-leak (index_artifact_gap 0.0008 -> index_leak False, anti_taut "
        "0.0013, degen 0.000; mechanism is a necessary-condition reachability filter, recov 0.244<<1.0). (A4) "
        "INDEPENDENCE screen clean and non-degenerate: corr(kb_confirm, m_error)=0.047 (|corr|<=0.15), varies "
        "-0.363@d4 to +0.214@op2 -> independence_degenerate False; kb_confirm_mean 0.499 non-vacuous -> the "
        "KB channel is informationally independent of R's own error, so the lift is genuinely exogenous. (A5) "
        "brs_cv 0.109<0.15, cardinality 300/300. "
        "ENTROPY-driven not literal depth (cross-confirms parent): op2_V800_d8 (DEPTH 8, ENTROPY 8) recovers "
        "KB=0.641 (recov 0.591, delta_vs_ver 0.496); op4_d8 (depth 8, ent 16) KB=0.283. n_hp_ok=1/5 "
        "UNDERSELLS: flatness_ratio is only computable for op4 regimes (needs the chain_steps==1 d4 sibling); "
        "op2_d8/op3_d8 get flatness=0 BY CONSTRUCTION (no shallow sibling) and cannot be hp_ok even though "
        "op2_d8 shows the STRONGEST grounded recovery. So hp_ok=1/5 is a metric-coverage artifact, not a weak "
        "effect. "
        "GRID (KB / recov_kb / delta_vs_ver / flatness / indep_corr / hp_ok): op4_d4 ent8: 0.920/0.926/0.223/"
        "1.000/-0.363/False; op4_d6 ent12: 0.498/0.486/0.470/0.525/0.069/True; op4_d8 ent16 FOCUS: 0.283/"
        "0.244/0.226/0.264/0.047/False; op3_d8 ent12.7: 0.388/0.341/0.368/0.000/0.117/False; op2_d8 ent8: "
        "0.641/0.591/0.496/0.000/0.214/False. "
        "CROSS-ARC OVERLAP (USER-locked): substrate_query 'waypoint rescue depth wall barrier compounding "
        "autonomous bisect KB grounding' -> TOP hit cosine=0.3584 is the autonomous-waypoint deep-corner "
        "compounding-error rescue research note (SAME arc). TARGETED EXTENSION (new mechanism class -- "
        "exogenous grounding -- at the same corner), NOT a rediscovery. Novelty: the exogenous-grounding "
        "partial-rescue isolating the barrier as autonomous-generation-specific + the frontier-push (entropy "
        "8 -> 12). TIER = MEASURED_MECHANISM (proven positive boundary refining barrier #2). Symmetric "
        "anti-negativity: NOT inflated to a barrier-BREAK (flatness 0.264 -> pushed not broken) and NOT "
        "deflated to a null (delta 0.226 is a real, clean, exogenous lift). Config-contingent bound (N=8192, "
        "this grid). commit 4f566616b 2026-07-09."
    ),
    "provenance": {
        "cell": "experiments/exp_pfc_gate_waypoint_rescue_kb_grounded_check_v1.py",
        "commit": CELL_COMMIT,
        "metrics_path": "data/exp_pfc_gate_waypoint_rescue_kb_grounded_check_v1/metrics.json",
        "parent_cell": "pfc_gate_waypoint_rescue_replay_bidirectional_v1",
        "seeds": [7, 17, 23, 31, 41],
        "run_mode": "full",
        "device": "cuda",
        "elapsed_s": 5104.3,
        "metrics_ts_iso": "2026-07-09T06:24:46.171338+00:00",
        "whole_cell_verdict": "MIDDLE_BAND_FLATNESS_BELOW_50",
        "audit_tier": "MEASURED_MECHANISM",
        "ts_iso": TS_ISO,
        "atomized_by": ATOMIZED_BY,
        "verified_off_data": True,
        "verified_off_data_note": (
            "Fix#28 read metrics.json directly. Independent .venv recompute off arm_means (NOT verdict_msg): "
            "recovery=(arm-flat_gonogo)/(hier_oracle-flat_gonogo); flatness=recov_rescue(d8)/recov_rescue(d4). "
            "focus delta_recovery recompute 0.22626 == disk 0.22626; flatness recompute 0.26406 == disk "
            "0.26406; full-grid recompute matched recov/delta for all 5 regimes. wp_random moves 0.102(d4) -> "
            "0.017(d8) confirms discriminator fires at scale. Mechanism audited from source lines 1046-1113: "
            "kb gate masks R-balance argmax to raw-graph-reachability-confirmed candidates (exogenous, zero "
            "shared params), necessary-condition filter not oracle answer (recov 0.244 << oracle 1.0). "
            "cardinality 300/300 = 5 regimes x 5 seeds x 12 arms."
        ),
    },
    "verified_numbers": {
        "N": 8192, "n_seeds": 5, "seeds": [7, 17, 23, 31, 41], "run_mode": "full", "device": "cuda",
        "cardinality_units": 300, "cardinality_expected": 300, "cardinality_ok": True, "cv_gate_enforced": True,
        "n_hp_ok": 1, "n_regimes": 5, "cap_frontier": "op4_V1200_d6", "max_entropy_hp_ok": 12.0,
        "focus_regime": "op4_V1200_d8", "focus_entropy": 16.0, "focus_chain_steps": 3,
        "focus_flat_gonogo": 0.08083333333333333, "focus_oracle_exec": 0.9175000000000001,
        "focus_hier_oracle": 0.9058333333333334, "focus_hier_shuffled": 0.0016666666666666666,
        "focus_wp_bisect_open": 0.09666666666666665, "focus_wp_bisect_verify": 0.09583333333333333,
        "focus_wp_kb_grounded_gate": 0.28250000000000003, "focus_wp_random_state": 0.017499999999999998,
        "focus_wp_index_midpoint": 0.018333333333333333,
        "focus_recov_open": 0.01919191919191918, "focus_recov_verify": 0.01818181818181818,
        "focus_recov_rescue": 0.2444444444444445, "focus_delta_vs_verify": 0.2262626262626263,
        "focus_delta_vs_open": 0.22525252525252532, "focus_flatness_ratio": 0.26406035665294936,
        "focus_lift_flat": 0.20166666666666672, "focus_lift_random": 0.265,
        "focus_index_artifact_gap": 0.0008333333333333352, "focus_anti_tautology_corr": 0.0012920684175128394,
        "focus_degenerate_rate": 0.0, "focus_index_leak": False, "focus_sign_test_p": 1.6888357965245234e-12,
        "focus_brs_cv": 0.10854495276090913, "focus_abs_independence_corr": 0.04678885581044465,
        "focus_kb_confirm_mean": 0.4988888888888889, "focus_kb_confirm_std": 0.4998294420475208,
        "focus_kb_fresh_rate": 0.06333333333333332, "focus_kb_fallback_rate": 0.0,
        "focus_independence_degenerate": False, "focus_kb_vacuous": False,
        "spearman_delta_vs_entropy": -0.20519567041703085,
        "grid_kb_grounded_gate": {"op4_d4_e8": 0.9200, "op4_d6_e12": 0.4983, "op4_d8_e16": 0.2825,
                                   "op3_d8_e12p7": 0.3875, "op2_d8_e8": 0.6408},
        "grid_recov_kb": {"op4_d4": 0.9257, "op4_d6": 0.4864, "op4_d8": 0.2444, "op3_d8": 0.3413, "op2_d8": 0.5913},
        "grid_delta_vs_verify": {"op4_d4": 0.2229, "op4_d6": 0.4703, "op4_d8": 0.2263, "op3_d8": 0.3683, "op2_d8": 0.4958},
        "grid_flatness": {"op4_d4": 1.000, "op4_d6": 0.525, "op4_d8": 0.264, "op3_d8": 0.000, "op2_d8": 0.000},
        "grid_indep_corr": {"op4_d4": -0.3628, "op4_d6": 0.0695, "op4_d8": 0.0468, "op3_d8": 0.1172, "op2_d8": 0.2142},
        "grid_hp_ok": {"op4_d4": False, "op4_d6": True, "op4_d8": False, "op3_d8": False, "op2_d8": False},
        "grid_rand_control": {"op4_d4": 0.1017, "op4_d6": 0.0208, "op4_d8": 0.0175, "op3_d8": 0.0125, "op2_d8": 0.0308},
        "flatness_undefined_for_non_op4": "op2_d8/op3_d8 have no chain_steps==1 sibling -> flatness=0 by construction -> cannot be hp_ok; hp_ok=1/5 undersells",
        "HF_delta_gate": 0.05, "HF_flat_gate": 0.20, "HF_indep_gate": 0.40,
        "HP_recov_gate": 0.20, "HP_delta_gate": 0.15, "HP_flat_gate": 0.50, "HP_indep_gate": 0.15,
        "recovery_formula": "recovery = (arm_mean - flat_gonogo) / (hier_oracle - flat_gonogo)",
        "flatness_formula": "flatness_ratio = recov_rescue(FOCUS d8) / recov_rescue(op4 d4 chain_steps==1 sibling)",
        "recompute_exact_match": True,
    },
    "can_fail_discriminator_verdict": (
        "FIRES and is TELEMETRY-SENSITIVE. (1) Both non-MIDDLE branches were reachable: the HARD_FAIL branch "
        "would have fired had delta<=0.05 or flat<0.20 (the three prior autonomous rescues DID land HARD_FAIL "
        "on exactly these gates -- delta 0.004-0.010, flat 0.044); the HARD_PASS branch would have fired had "
        "flat>=0.50 (op4_d6 DOES clear all four HP gates -> hp_ok=True). This cell lands MIDDLE precisely "
        "because delta+recov+indep pass but flatness sits at 0.264. (2) The independence screen is a genuine "
        "can-fail honesty gate: |corr| moves across regimes (-0.363 to +0.214) and would have fired HF had it "
        "exceeded 0.40 -- a leak would have shown high |corr|; it did not. (3) The positive-control rail is "
        "not pinned to the rescue floor (oracle 0.918 vs KB 0.283), and the RAND control moves with difficulty "
        "(0.102 -> 0.017) -> nothing analytically pinned. (4) The paired sign test reads the data (1.69e-12 "
        "where signal exists). (5) The mechanism is a necessary-condition filter, not the oracle answer "
        "(recov 0.244 << 1.0), so a MIDDLE here reflects genuine partial exogenous information, not a leak."
    ),
    "framing_corrections_vs_cell_author_and_director": [
        "Cell self-verdict MIDDLE_BAND_FLATNESS_BELOW_50 is CORRECT and reproduces exactly off-disk; audit "
        "CONFIRMS MIDDLE and sub-audits it to MEASURED_MECHANISM (proven positive boundary). No correction to "
        "the verdict itself.",
        "BARRIER #2 FRAMING (adjudicated against the Director's decision frame): the answer is PUSHED, not "
        "BROKEN, and not DEPTH-FUNDAMENTAL. HARD_PASS (barrier BROKEN) would need flatness>=0.50; it is 0.264, "
        "so grounded rescue still decays with depth. HARD_FAIL (depth-fundamental) would need delta<=0.05; it "
        "is 0.226 with sign_p 1.69e-12, so there IS material clean lift. The honest claim: exogenous "
        "KB-reachability grounding EXTENDS the rescue frontier from entropy 8 (the autonomous self-discovery "
        "frontier, op4_d4) to entropy 12 (op4_d6, hp_ok), and even at entropy 16 lifts recovery to 0.244 "
        "where every autonomous mechanism sat at 0.028 -- but the wall re-forms at a deeper frontier rather "
        "than dissolving.",
        "LOAD-BEARING SCOPING: this is EXOGENOUS-GROUNDING-ASSISTED, NOT autonomous problem-solving. The KB "
        "reachability channel is external ground-truth graph structure consulted at decision time. Do NOT "
        "narrate this as 'the substrate learned to cross the barrier' -- it is 'with an exogenous reachability "
        "check, the deep corner becomes partially rescuable'. This ISOLATES the barrier: the substrate cannot "
        "SELF-DERIVE reliable waypoints at high entropy, but the task is not intrinsically unrescuable -- the "
        "limit is in autonomous generation, not solvability.",
        "n_hp_ok=1/5 UNDERSELLS the capability and must not be quoted as '1/5 regimes worked'. flatness_ratio "
        "is only computable for the op4 regimes (they alone have a chain_steps==1 d4 sibling); op2_d8 and "
        "op3_d8 get flatness=0 BY CONSTRUCTION and therefore cannot be hp_ok, even though op2_d8 shows the "
        "STRONGEST grounded recovery in the whole grid (KB=0.641, delta_vs_ver 0.496). The correct read is "
        "'grounded rescue lifts recovery materially and cleanly at 5/5 regimes; it clears the strict "
        "flatness-normalized frontier through entropy 12'.",
        "ENTROPY-driven not depth-driven (consistent with parent): op2_V800_d8 has DEPTH 8 but ENTROPY 8 and "
        "recovers KB=0.641; op4_d8 (depth 8, ent 16) reaches 0.283. Frame any downstream capability as an "
        "entropy-per-step frontier, not a 'depth-8 result'. Config-contingent (N=8192, this grid).",
        "NOT an oracle-answer leak (pre-empting an over-claim in the other direction): the KB gate is a "
        "necessary-condition reachability FILTER on the substrate's own R-balance argmax, not the oracle "
        "waypoint. Recovery reaches only 0.244 (the given-decomposition oracle is 1.0). Symmetric "
        "anti-negativity applies both ways: neither a barrier-break nor an oracle triviality.",
    ],
    "revival_or_extension_criterion": (
        "MEASURED-BOUND scope: at op4_V1200_d8/ent16 (N=8192, 5 seeds) an exogenous KB-reachability grounding "
        "channel lifts recovery to 0.244 (delta_vs_ver 0.226, clean, sign_p 1.69e-12) where all four "
        "autonomous rescues sat at ~0.028, but grounded rescue still decays with depth (flatness 0.264); the "
        "flatness-normalized frontier is entropy 12 (op4_d6, hp_ok). EXTENSIONS (each a NEW cell): (1) "
        "PROMOTION-to-CG trigger: a mechanism (grounded or otherwise) that lifts recovery_rescue>=0.20 AND "
        "delta>=0.15 AND flatness>=0.50 AND |indep|<=0.15 at ent>=16 for >=4/5 seeds -> would upgrade the "
        "grounded rescue from a pushed-frontier bound to a depth-flat capability. (2) MEASURE THE GROUNDED "
        "FRONTIER precisely: sweep entropy 8->20 at fixed depth to locate where grounded flatness crosses 0.50 "
        "and 0.20 -- turns this MM into a measured grounded-recovery frontier curve. (3) DECOMPOSE the residual "
        "depth cost: since the KB filter is a necessary-not-sufficient condition and the drifting R-balance "
        "still chooses among confirmed candidates, test whether replacing the R-balance tiebreak with a "
        "correctness-calibrated scorer (the parent's non-predictive-consistency clue) closes the flatness gap. "
        "(4) DAgger / imitation-from-oracle as the AUTONOMOUS analogue: learn the decomposition policy from "
        "oracle traces (the named next lever for the HF chain) and compare its frontier to this exogenous "
        "grounded frontier -- does a learned policy match what exogenous grounding buys? DEMOTION/void trigger "
        "for THIS atom: a re-run where the independence screen degenerates (|corr|>0.40 -> the KB channel is "
        "not actually independent, lift would be a leak), or where the oracle rail fails (task unsolvable), or "
        "where kb_confirm goes vacuous (mean outside 0.05-0.95 -> filter contaminated)."
    ),
    "composes": [P_REPLAY_BIDIR_HF, P_COARSE2FINE_HF, P_AUTONOMOUS_SELF_DISCOVERY_MM],
    "compose_note": (
        "REFINES and complements the BARRIER #2 chain -- does NOT supersede any of it. The three composed "
        "atoms establish that AUTONOMOUS (self-derived) waypoint rescue HARD_FAILS at op4_V1200_d8/ent16: "
        "coarse2fine+verify (HF 07-06), replay-generate-select + bidirectional-consistency (HF 07-09; the "
        "direct parent cell), and the autonomous self-discovery MM (07-06; frontier entropy 8). THIS atom adds "
        "the ORTHOGONAL result: an EXOGENOUS reachability grounding channel PARTIALLY rescues the SAME corner "
        "(delta_vs_ver 0.226, recov 0.244 vs autonomous ~0.028), which REFRAMES the whole barrier -- it is an "
        "AUTONOMOUS-GENERATION limit, not a task-solvability limit. NEW contribution of THIS atom: (a) the "
        "autonomous-vs-exogenous dissociation (isolates WHERE the barrier lives), (b) the frontier PUSH "
        "(autonomous entropy-8 frontier -> grounded entropy-12 frontier), (c) the wall-pushed-not-broken "
        "measurement (grounded flatness still 0.264 at ent16), and (d) the mechanism audit that the grounding "
        "is a necessary-condition FILTER (recov 0.244 << oracle 1.0), not an answer leak, with a clean "
        "independence screen (corr 0.047). Brain-grounding: PFC/BG waypoint-gated hierarchical control with an "
        "exogenous grounding channel = a kinetic-proofreading / external-reference checkpoint; the finding is "
        "that consulting an independent ground-truth reachability signal partially substitutes for the "
        "supervised/oracle decomposition the substrate cannot self-generate at high entropy, but does not "
        "fully close the depth gap."
    ),
    "cross_arc_overlap_check": (
        "substrate_query 'waypoint rescue depth wall barrier compounding autonomous bisect KB grounding' -> "
        "TOP hit cosine=0.3584 = autonomous-waypoint deep-corner compounding-error rescue research note (SAME "
        "arc; rank-1/2); 'compounding' concept 0.338; 'grounding' concept 0.329. All in-arc. This is a "
        "TARGETED EXTENSION (a NEW mechanism CLASS -- exogenous KB-reachability grounding -- at the same deep "
        "corner the autonomous mechanisms failed), NOT a full rediscovery; the July-1 INT8-rediscovery pattern "
        "does NOT apply. Novelty carried by THIS atom and none of the prior arc atoms: the exogenous partial "
        "rescue, the autonomous-generation-vs-solvability dissociation, and the frontier push entropy 8 -> 12."
    ),
    "anchor": "pfc_gate_waypoint_rescue_kb_grounded_check_v1",
    "cell_commit": CELL_COMMIT,
    "seeds": [7, 17, 23, 31, 41],
    "run_mode": "full",
    "cardinality_ok": True,
    "arms_differ_verified": True,
    "verified_off_data": True,
    "auditor": "hdi_skunkworks",
    "atomized_by": "hdi_skunkworks",
    "landed_VET_session": SESSION,
    "route_to_research_extension": True,
    "route_note": (
        "PROVEN positive boundary (barrier PUSHED not broken). Route to research for the frontier-measurement "
        "and correctness-calibrated-selector extensions, and to compare against DAgger/imitation-from-oracle "
        "(the autonomous analogue named as the HF chain's next lever). Not a negative -> not a 5x negative "
        "drill; it is a positive result whose extension is to close the residual flatness gap."
    ),
    "needs_orchestrator_store_sync": True,
    "ts": TS,
    "ts_iso": TS_ISO,
    "ts_added": TS_ISO,
    "aliases": [
        "exogenous KB-reachability grounding PARTIALLY rescues autonomous chain drift where all self-derived mechanisms HARD_FAILED (BARRIER #2 REFINED); MEASURED_MECHANISM proven bound",
        "op4_V1200_d8 ent16: OPEN 0.097 VERIFY 0.096 KB 0.283, delta_vs_verify 0.226 (>=0.15), flatness 0.264 (in [0.20,0.50) MIDDLE), indep_corr 0.047 clean, sign_p 1.69e-12",
        "barrier is an AUTONOMOUS-GENERATION limit not a task-solvability limit; wall PUSHED (frontier entropy 8 -> 12) not BROKEN; grounded rescue still decays with depth",
        "mechanism = KB-reachability-confirmed mask on R-balance argmax (exogenous raw graph, zero shared params); NECESSARY FILTER not oracle answer (recov 0.244 << oracle 1.0)",
        "n_hp_ok 1/5 UNDERSELLS: flatness only computable for op4 (needs d4 sibling); op2_d8 depth8 ent8 has STRONGEST grounded recovery KB 0.641 but flatness=0 by construction",
        "ENTROPY-driven not depth: op2_V800_d8 (depth 8 ent 8) recovers 0.641; op4_d8 (depth 8 ent 16) 0.283",
        "pfc_gate_waypoint_rescue_kb_grounded_check_v1 landed-VET MEASURED_MECHANISM",
    ],
    "added_atom_id": None,
}
atom["added_atom_id"] = atom["id"]

ledger = {
    "ts": TS, "ts_iso": TS_ISO, "op": "add", "atom_id": atom["id"], "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "disposition": "measured_mechanism_barrier2_refined_exogenous_kb_reachability_grounding_partially_rescues_autonomous_chain_drift_deep_high_entropy_corner_wall_pushed_frontier_entropy_8_to_12_not_broken_barrier_is_autonomous_generation_specific_not_task_solvability",
    "cert_status": atom["cert_status"],
    "cert_class": atom["cert_class"],
    "cert_increment_delta": {"CG": 0, "MM": 1, "HF": 0},
    "cert_delta": {"CG": 0, "MM": 1, "HF": 0},
    "cert_delta_note": (
        "MM +1 (proven positive boundary refining BARRIER #2): an EXOGENOUS KB-reachability grounding channel "
        "PARTIALLY rescues autonomous chain-drift at op4_V1200_d8/ent16 where all four self-derived rescues "
        "(coarse2fine, replay, bidirectional, cerebellar rollout) HARD_FAILED. 5-seed FULL GPU, 300/300 units, "
        "N=8192, verdict MIDDLE_BAND_FLATNESS_BELOW_50 reproduces exactly off-disk (Fix#28 + independent .venv "
        "recompute off arm_means: focus delta 0.22626 EXACT, flatness 0.26406 EXACT). FOCUS: delta_vs_ver "
        "0.226>=0.15 (HP_delta clears), recov_kb 0.244>=0.20 (HP_recov clears), |indep_corr| 0.047<=0.15 "
        "(clean, non-degenerate), BUT flatness 0.264 in [0.20,0.50) -> neither HP nor HF fires -> MIDDLE, "
        "sub-audited to MM. GENUINE: positive-control rail clears own floor (oracle_exec 0.918, hier_oracle "
        "0.906, headroom_decomp_ok); negatives collapse (shuffled 0.0017, random 0.0175); discriminator fires "
        "at scale (KB 0.283 vs verify 0.096 vs random 0.017; wp_random moves 0.102 d4 -> 0.017 d8; sign_p "
        "1.69e-12). NOT an oracle-answer leak (mechanism audit): kb gate masks R-balance argmax to "
        "KB-reachability-confirmed candidates (exogenous raw graph, zero shared params) -- a necessary-"
        "condition filter, recov 0.244 far below oracle 1.0. Independence screen clean/non-degenerate "
        "(corr -0.363@d4 to +0.214@op2). BARRIER #2 framing: PUSHED not BROKEN -- frontier extended from the "
        "autonomous entropy-8 frontier to entropy 12 (op4_d6 hp_ok=True, max_entropy_hp_ok=12.0); grounded "
        "rescue still decays with depth (recov_kb 0.926 d4 -> 0.486 d6 -> 0.244 d8). ENTROPY-driven not depth "
        "(op2_V800_d8 depth8 ent8 recovers 0.641). n_hp_ok 1/5 UNDERSELLS: flatness only computable for op4 "
        "(op2/op3 flatness=0 by construction). Composes (NOT supersedes) the replay-bidir HF (parent), "
        "coarse2fine HF, and autonomous self-discovery MM -- REFRAMES the barrier as an autonomous-generation "
        "limit, not a task-solvability limit. Cross-arc overlap: top cosine 0.3584 = in-arc rescue note "
        "(targeted extension, new mechanism class, not rediscovery). Symmetric anti-negativity: NOT inflated "
        "to a barrier-break (flatness 0.264) and NOT deflated to a null (delta 0.226 clean, sign_p 1.69e-12). "
        "Grounding-ASSISTED, not autonomous problem-solving. Config-contingent (N=8192, this grid). Next "
        "levers: measure grounded frontier finely; correctness-calibrated selector; DAgger/imitation as the "
        "autonomous analogue. Needs orchestrator Store-sync."
    ),
    "verified_off_data": True,
    "verification": "fix28_read_metrics_json_direct + independent_venv_recompute_off_arm_means_all_5_regimes_exact_match_focus_delta_0p22626_flatness_0p26406 + positive_control_rail_clears_own_floor + rand_control_moves_with_depth_discriminator_fires + independence_screen_clean_nondegenerate_corr_0p047 + mechanism_audit_kb_gate_is_necessary_filter_not_oracle_answer_recov_0p244_below_oracle_1p0 + entropy_vs_depth_decoupling_op2_d8",
    "anchor": "pfc_gate_waypoint_rescue_kb_grounded_check_v1",
    "cell_commit": CELL_COMMIT,
    "auditor": "hdi_skunkworks", "atomized_by": "hdi_skunkworks",
    "landed_VET_session": SESSION,
    "composes": [P_REPLAY_BIDIR_HF, P_COARSE2FINE_HF, P_AUTONOMOUS_SELF_DISCOVERY_MM],
    "route_to_research_extension": True,
    "needs_orchestrator_store_sync": True,
    "raw_metrics_paths": ["data/exp_pfc_gate_waypoint_rescue_kb_grounded_check_v1/metrics.json"],
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
    print(f"[A5] atomize START {ATOMIZED_BY} ts={TS:.3f}")
    append_jsonl_a5(MATH_ATOMS, atom, "math/atoms (kb-grounded partial-rescue BARRIER2-refined MEASURED_MECHANISM)")
    append_jsonl_a5(CERT_LEDGER, ledger, "cert_ledger (MM +1)")
    print(f"[A5] DONE OK -> exogenous-KB-grounding partial-rescue BARRIER2-refined MEASURED_MECHANISM (MM +1)")


if __name__ == "__main__":
    main()
