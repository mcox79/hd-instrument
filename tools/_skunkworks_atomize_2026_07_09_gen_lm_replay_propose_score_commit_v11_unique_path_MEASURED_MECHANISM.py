"""
A5-gated atomize: LANDED-VET (AUDIT-ONLY, HIGH) of substrate_gen_lm_replay_propose_score_commit_v11_unique_path.
BARRIER2 (recurrent noise-compounding) -- GENERATION-DOMAIN instance. TIER = MEASURED_MECHANISM (proven boundary).

CELL: experiments/exp_substrate_gen_lm_replay_propose_score_commit_v11_unique_path_n8192_gpu.py (commit 3793f9d94)
METRICS: data/exp_substrate_gen_lm_replay_propose_score_commit_v11_unique_path_n8192_gpu/metrics.json
  run_mode=full, 3 seeds 7/17/23, N=8192, L_grid [4,8,14], headline L=14, chance=0.125, verdict MIDDLE_BAND_PARTIAL.

INDEPENDENT OFF-DISK RECOMPUTE (.venv, this session -- aggregated per_seed[] arm x L, all 3 seeds):
  ALL headline numbers reproduce EXACTLY. Recomputed intra_decline / body_token_acc / goal_reach curves per arm:
    intra_decline   L4      L8      L14
      REPLAY        0.000   0.000   0.000   (all 3 seeds identically 0.000; body cv=0.000, stdev=0.000)
      ACCUMULATE    0.283   0.138   0.262   (NON-monotonic in L)
      RANDOM        0.271   0.149   0.084
    body_token_acc  L4      L8      L14
      REPLAY        1.000   1.000   1.000   (== ORACLE == PROPOSE_ONLY exactly)
      ACCUMULATE    0.826   0.927   0.867
      RANDOM        0.138   0.065   0.039
    goal_reach @L14: REPLAY 1.000, ACCUM 0.392, RANDOM 0.000 -> REP-ACCUM=+0.608, REP-RANDOM=+1.000 (reproduce).
  SATURATION / DIGEST-IDENTITY (the load-bearing audit finding): arm_digests ORACLE == REPLAY == REPLAY_PROPOSE_ONLY
    all = f05d802280db... (byte-identical committed output). sel_value(body @L14) = REPLAY - PROPOSE_ONLY = +0.000.
    This is BY DESIGN (cell docstring): v11 uses a UNIQUE-PATH graph, so REPLAY scored-by-goal-reach recovers THE one
    goal-reaching route -> identical to ORACLE; and the goal-directed propose step already saturates, so uniform
    (PROPOSE_ONLY) vs scored selection land on the same route -> the SCORE/COMMIT stage is PROVABLY INERT here.
  ACCUM body_drift(L4->L14) = 0.826 - 0.867 = -0.041 (body IMPROVES slightly with depth) -> the "body gap grows with L"
    HARD_PASS leg (D1 depth-scaling) FAILS; the compounding ACCUM shows is WITHIN-body (intra_decline fires 0.14-0.28),
    not depth-scaling.

WHY MIDDLE_BAND_PARTIAL (verified off-disk, missed HARD_PASS legs):
  (a) sel_value > 0 FAILS (=+0.000; scoring inert -- saturation-vacuous scoring discriminator).
  (b) "REPLAY-ACCUM body gap GROWS with L" FAILS (ACCUM body_drift = -0.041, not >0).
  (c) REPLAY flatness is at SATURATION (body 1.000, cv 0.000) and partly BY CONSTRUCTION (unique-route recovery).
  The legs that PASS cleanly: D1c REPLAY body >= ceiling + flat (intra_decline 0.000 <= 0.05); D2 REPLAY beats
  RANDOM (goal_reach +1.000 >= 0.15); REPLAY beats ACCUM (goal_reach +0.608 >= 0.20); D3 ORACLE body >= 0.90;
  discriminator FIRES at N=8192 (ACCUM goal_reach 0.39 and RANDOM ~0 both genuinely fail at scale, NOT vacuous).

FIVE ADVERSARIAL CHECKS:
  P1 DISCRIMINATOR FIRES AT SCALE, PER-SEED: at N=8192 the must-underperform controls genuinely fail -- ACCUM
     goal_reach 0.51/0.45/0.46 (s7/17/23) @L4 down to 0.40/0.46/0.31 @L14; RANDOM goal_reach ~0 at all L. Non-vacuous.
  P2 SATURATION OF THE SCORING DISCRIMINATOR (the reason scoring-value is NOT shown): ORACLE==REPLAY==PROPOSE_ONLY
     byte-identical digest; sel_value=+0.000. On a unique-path graph the goal-directed propose step saturates, so
     score/commit has nothing to correct. v10 (multi-path) DID show sel_value=+0.073 but had a body_token_acc confound
     -- the two versions TRADE OFF; no single version shows BOTH drift-free-body AND scoring-earns-keep.
  P3 ACCUM COMPOUNDING IS WITHIN-BODY, NOT DEPTH-SCALING: intra_decline fires (0.14-0.28, late positions worse:
     e.g. seed7 L14 per_position 1.0...1.0->0.956->0.9->0.79->0.556->0.4) BUT is non-monotonic in L (L4 0.283 > L8
     0.138) and ACCUM body_drift(L4->L14) is NEGATIVE (-0.041). The "compounds MORE with depth" story is NOT clean.
  P4 TELEMETRY: REPLAY/ORACLE/PROPOSE_ONLY pinned at 1.000 (saturated); ACCUM + RANDOM move with seed
     (ACCUM goal_reach @L14 0.40/0.46/0.31; RANDOM body @L4 0.123/0.142/0.148) -> the FAILING arms are data-driven,
     not analytically pinned. cardinality: 5 arms x 3 L, arm_digests distinct across the 3 mechanism families
     (ORACLE/REPLAY/PROPOSE f05d..., ACCUM 0371.., RANDOM 361b..) -- REPLAY vs ACCUM vs RANDOM genuinely differ.
  P5 HONEST SCOPE: certifies REPLAY-generation body/goal DOMINANCE over ACCUMULATE + RANDOM on a UNIQUE-PATH
     synthetic generation graph (drift-free BY CONSTRUCTION of unique-route recovery); does NOT certify (i) scoring
     earns its keep (inert here), (ii) depth-scaling of compounding, (iii) any real-language generation. Synthetic.

CROSS-ARC OVERLAP (USER-locked check): substrate_query "replay propose score commit drift-free depth-invariant
  generation accumulate error compounding" -> top cosine 0.2607 (all NOTES: 'Composition cost (noise accumulation)',
  long-form-generation handoff, NOISE-COMPOUNDING backup-doc principle), NONE a landed cell at cosine>0.30. BUT the
  cert_ledger reveals TWO structurally-adjacent LANDED atoms in the same BARRIER2 arc: the community_routed_glassbox
  MM (2026-07-08, ARM_C fresh-flat slope 0.001 vs compound slope 0.098, explicitly flagged flat "BY CONSTRUCTION")
  and the replay_generate_select HF (2026-07-09, replay+select does NOT rescue AUTONOMOUS chain drift at the deep
  high-entropy corner). REDISCOVERY-ADJACENCY CALL: v11 re-instantiates the SAME non-compounding-by-construction
  CONTRAST law, so it CANNOT be CG -- but it is a GENUINELY NEW TASK DOMAIN (autoregressive token-body generation vs
  retrieval-reasoning) with NEW ablations (propose-only scoring ablation + random-restart null) and it usefully
  SCOPES the replay mechanism: replay WINS when there is a unique goal-reaching route to recover (v11, low-entropy),
  and (per BARRIER2 HF) replay+select does NOT rescue drift in the HARD multi-branch high-entropy regime. Valid
  additional MM instance, not a byte-rediscovery.

TIER = MEASURED_MECHANISM (proven boundary): the generation-domain instance of the recurrent noise-compounding law is
  real, reproduces exactly, discriminator fires non-vacuously at scale -- but (i) the certified content is the
  CONTRAST (REPLAY drift-free-by-construction dominates ACCUMULATE within-body compounding + RANDOM null), NOT a
  stressed capacity or scoring-value result; (ii) scoring is PROVABLY INERT at this saturated regime; (iii) depth-
  scaling of compounding is not clean. Symmetric anti-negativity: NOT deflated to MB/HF (contrast clean, reproduces,
  cv=0.000, discriminator fires); NOT inflated to CG (flat-by-construction, scoring inert, synthetic, re-instantiates
  an established law). Counts toward CERT N as a proven boundary. Composes the community_routed_glassbox MM (same
  contrast structure) and the BARRIER2 compounding-error HF (the bound cross-confirmed + the regime scope).
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_atomize_2026_07_09_gen_lm_replay_propose_score_commit_v11_unique_path_MEASURED_MECHANISM"
CELL_COMMIT = "3793f9d94"
TS = time.time()
TS_ISO = "2026-07-09T00:00:00Z"
SESSION = "2026-07-09_gen_lm_replay_propose_score_commit_v11_unique_path_landed_vet_BARRIER2_GENERATION_INSTANCE_MM"

P_SIBLING = (
    "math::MEASURED_MECHANISM_community_routed_glassbox_reasoning_scale_v1_BARRIER2_CROSSCONFIRM_a_community_routed_"
    "glass_box_reasoning_chain_stays_FLAT_routed_succ_1p000_rel_deg_0p000_over_a_V_sweep_580_2900_12000_30000_N8192_"
    "3seed_7_17_23_depth_2to8_WHILE_a_FLAT_whole_store_chain_COLLAPSES_flat_succ_0p440_to_0p000_by_V2900_perseed_rel_"
    "deg_1p000_discriminator_FIRES_glass_box_audit_INTACT_at_scale_replay_merkle_tamper_routing_causal_flip_tamper_"
    "all_1p000_at_every_V_incl_V30000_route_acc_1p000_modularityQ_min_0p698_real_structure_reproduces_EXACT_off_disk_"
    "all_hashes_PROVEN_BOUNDARY_NOT_CG_because_i_the_scale_invariance_headline_RE_DEMONSTRATES_community_bounded_"
    "retrieval_scale_invariance_v1_MM_same_Vsweep_design_same_seeds_same_route_acc_1p000_and_ii_the_ROUTED_arm_is_at_"
    "CEILING_routed_succ_1p000_zero_headroom_comm_size_24_to_173_ALL_below_the_apprx580_flat_collapse_knee_and_"
    "apprx630_within_community_Plate_cliff_so_flat_is_total_V_invariance_WITHIN_the_community_capacity_envelope_NOT_"
    "unbounded_and_iii_glass_box_multihop_at_scale_is_ALREADY_CG_via_glass_box_micro_loop_conceptnet_multihop_SCALE_"
    "v1_which_is_NON_CEILING_accB_0p933_and_REAL_ConceptNet_topology_strictly_stronger_ARM_B_ROUTED_WITHIN_eq_ARM_"
    "ORACLE_ROUTE_byte_identical_hash_every_seed_V_because_route_acc_1p000_so_oracle_ceiling_gate_adds_no_independent_"
    "info_THE_GENUINE_NEW_INCREMENT_is_the_independent_channel_NON_COMPOUNDING_cross_confirm_of_BARRIER2_ARM_C_FRESH_"
    "slope_0p00101_flat_per_hop_hazard_apprx0p14_across_8_hops_vs_ARM_C_COMPOUND_slope_0p09756_rises_0p14_0p38_0p55_"
    "0p74_SAME_V12000_Q256_SAME_3seed_PAIRED_the_fresh_flat_slope_is_largely_BY_CONSTRUCTION_independent_channel_"
    "cannot_compound_the_load_bearing_content_is_the_CONTRAST_proving_compounding_is_the_collapse_driver_cross_"
    "confirming_the_compounding_error_bound_HARD_FAIL_and_the_3rd_instance_recurrent_noise_compounding_bound_from_the_"
    "OTHER_direction_an_independent_fresh_channel_ESCAPES_the_bound_compound_tail_noisy_at_risk_768_to_1_last_hazard_"
    "1p000_from_one_sample_but_rise_decisive_over_hops_1to4_SCOPE_synthetic_community_structured_KB_not_real_ingested_"
    "topology_EXTENDS_community_bounded_retrieval_scale_invariance_v1_MM_2026-07-08"
)

P_BOUND = (
    "math::HARD_FAIL_STRUCTURAL_COMPOUNDING_ERROR_BOUND_DOUBLY_CONFIRMED_MECHANISM_INDEPENDENT_BARRIER2_replay_"
    "generate_select_plus_bidirectional_consistency_selection_ALSO_does_NOT_rescue_autonomous_chain_drift_at_the_"
    "deepest_high_entropy_corner_5seed_FULL_GPU_275units_op4_V1200_d8_ent16_steps3_OPEN_0p097_VERIFY_0p096_REPLAY_"
    "0p104_recov_ver_0p018_recov_rescue_0p028_DELTA_vs_ver_0p010_lt_0p05_HF_delta_FIRES_flatness_ratio_0p044_lt_0p20_"
    "HF_flat_FIRES_lift_verify_0p008_negligible_sign_p_0p4228_ns_n_hp_ok_0_of_5_CAP_FRONTIER_None_GENUINE_not_design_"
    "failure_positive_control_rail_clears_own_floor_oracle_exec_0p918_hier_oracle_0p906_headroom_decomp_ok_negative_"
    "controls_collapse_hier_shuffled_0p0017_wp_random_0p0175_discriminator_FIRES_at_scale_RAND_0p102_d4_to_0p017_d8_"
    "paired_sign_fires_where_signal_d4_3e5_d6_0p001_op2_0p045_null_only_at_focus_ENTROPY_driven_not_depth_op2_V800_d8_"
    "depth8_ent8_recovers_0p30_op3_d8_ent12p7_collapses_0p09_max_delta_vs_ver_anywhere_0p035_at_d4_replay_0p798_WORSE_"
    "than_open_0p823_delta_minus0p057_mechanism_never_wins_bidir_selector_ACTIVE_frac_not_open_0p617_bidir_sel_0p630_"
    "gt_all_0p584_but_NON_predictive_consistency_not_correctness_proxy_under_compounding_drift_anti_taut_0p0013_degen_"
    "0p000_index_leak_False_spr_delta_ent_minus0p051_CROSS_CONFIRMS_coarse2fine_HF_bound_is_MECHANISM_INDEPENDENT_3rd_"
    "4th_autonomous_rescue_to_fail_DAgger_imitation_from_oracle_next_lever_class_not_another_autonomous_decomposition_"
    "variant_2026-07-09"
)

ATOM_ID = (
    "math::MEASURED_MECHANISM_gen_lm_replay_propose_score_commit_v11_unique_path_GENERATION_DOMAIN_INSTANCE_of_the_"
    "recurrent_NOISE_COMPOUNDING_law_BARRIER2_on_a_UNIQUE_PATH_synthetic_generation_graph_N8192_3seed_7_17_23_Lgrid_"
    "4_8_14_chance_0p125_a_REPLAY_propose_score_commit_generator_recovers_the_one_goal_reaching_route_with_ZERO_"
    "within_body_decline_intra_decline_0p000_body_token_acc_1p000_FLAT_across_L4_L8_L14_all_3_seeds_cv_0p000_and_"
    "DOMINATES_both_an_ACCUMULATE_generator_navigating_by_a_growing_leaky_bundle_lambda_0p65_which_shows_GENUINE_"
    "WITHIN_BODY_compounding_intra_decline_0p283_0p138_0p262_body_0p826_0p927_0p867_goal_reach_0p481_0p435_0p392_and_"
    "a_RANDOM_RESTART_null_body_0p138_0p065_0p039_goal_reach_apprx0_at_L14_REP_minus_ACCUM_goal_reach_plus_0p608_REP_"
    "minus_RANDOM_plus_1p000_body_plus_0p961_discriminator_FIRES_at_N8192_both_controls_genuinely_fail_at_scale_NON_"
    "vacuous_reproduces_EXACT_off_disk_PROVEN_BOUNDARY_NOT_CG_because_i_the_certified_content_is_the_CONTRAST_REPLAY_"
    "is_drift_free_BY_CONSTRUCTION_unique_route_recovery_arm_digest_ORACLE_eq_REPLAY_eq_PROPOSE_ONLY_byte_identical_"
    "f05d802280db_saturated_1p000_cv_0p000_ii_the_SCORE_COMMIT_stage_is_PROVABLY_INERT_here_sel_value_plus_0p000_"
    "PROPOSE_ONLY_uniform_selection_lands_on_the_SAME_route_because_the_goal_directed_propose_step_saturates_on_a_"
    "unique_path_graph_scoring_earns_its_keep_is_NOT_shown_saturation_vacuous_v10_multi_path_DID_show_sel_value_plus_"
    "0p073_but_had_a_body_confound_the_two_versions_TRADE_OFF_no_single_version_shows_BOTH_and_iii_ACCUM_compounding_"
    "is_WITHIN_body_not_depth_scaling_intra_decline_NON_monotonic_in_L_and_ACCUM_body_drift_L4_to_L14_is_NEGATIVE_"
    "minus_0p041_body_gap_grows_with_L_HARD_PASS_leg_FAILS_SCOPE_synthetic_unique_path_generation_graph_NOT_real_"
    "language_certifies_replay_vs_accumulate_vs_random_body_goal_dominance_does_NOT_certify_scoring_value_or_depth_"
    "scaling_of_compounding_re_instantiates_the_non_compounding_by_construction_contrast_law_in_a_NEW_task_domain_"
    "autoregressive_token_body_generation_scopes_replay_wins_when_a_unique_goal_route_exists_low_entropy_while_"
    "BARRIER2_HF_shows_replay_plus_select_does_NOT_rescue_autonomous_drift_in_the_hard_multi_branch_high_entropy_"
    "regime_composes_community_routed_glassbox_MM_and_compounding_error_HF_commit_3793f9d94_2026-07-09"
)

atom = {
    "id": ATOM_ID,
    "name": (
        "MEASURED_MECHANISM (proven boundary): substrate REPLAY-propose-score-commit generation is the GENERATION-"
        "DOMAIN instance of the recurrent noise-compounding law (BARRIER2). On a UNIQUE-PATH synthetic generation "
        "graph (N=8192, 3 seeds 7/17/23, L_grid [4,8,14], chance 0.125), REPLAY recovers the one goal-reaching route "
        "with ZERO within-body decline (intra_decline 0.000, body_token_acc 1.000, FLAT across all L, cv 0.000) and "
        "DOMINATES both (a) an ACCUMULATE generator (growing leaky bundle, lambda 0.65) that shows GENUINE within-"
        "body compounding (intra_decline 0.28/0.14/0.26; goal_reach 0.48/0.44/0.39) and (b) a RANDOM_RESTART null "
        "(goal_reach ~0). @L14 REP-ACCUM goal_reach +0.608, REP-RANDOM +1.000 / body +0.961. Discriminator FIRES at "
        "N=8192 (both controls genuinely fail at scale). BOUNDARY (why MM not CG): (i) REPLAY drift-free is BY "
        "CONSTRUCTION of unique-route recovery -- arm_digest ORACLE == REPLAY == PROPOSE_ONLY byte-identical "
        "(f05d802280db), saturated at 1.000 cv 0.000; (ii) the SCORE/COMMIT stage is PROVABLY INERT here (sel_value "
        "+0.000; uniform-select PROPOSE_ONLY lands on the same route because goal-directed proposal saturates on a "
        "unique-path graph) -- 'scoring earns its keep' is NOT shown (saturation-vacuous); v10's multi-path did show "
        "sel_value +0.073 but had a body confound, the two versions trade off; (iii) ACCUM compounding is WITHIN-body "
        "not depth-scaling (intra_decline non-monotonic in L; ACCUM body_drift L4->L14 = -0.041, i.e. body does NOT "
        "grow-worse with depth). SCOPE: synthetic unique-path graph, NOT real language; certifies the REPLAY-vs-"
        "ACCUMULATE-vs-RANDOM body/goal contrast, NOT scoring value or depth-scaling. Re-instantiates the non-"
        "compounding-by-construction contrast in a NEW task domain (autoregressive token-body generation); scopes "
        "replay: it WINS when a unique goal route exists (low-entropy), while the BARRIER2 HF shows replay+select "
        "does NOT rescue autonomous drift in the hard high-entropy multi-branch regime."
    ),
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet",
    "cert_status": (
        "mm_gen_lm_replay_propose_score_commit_v11_unique_path_generation_domain_instance_of_recurrent_noise_"
        "compounding_law_barrier2_replay_drift_free_intra_decline_0p000_body_1p000_flat_all_L_cv0p000_dominates_"
        "accumulate_within_body_compounding_intra_decline_0p14_to_0p28_goal_reach_0p39_to_0p48_and_random_null_"
        "goal_reach_apprx0_rep_minus_accum_gr_plus0p608_rep_minus_random_gr_plus1p000_discriminator_fires_at_n8192_"
        "reproduces_exact_off_disk_PROVEN_BOUNDARY_replay_flat_by_construction_unique_route_recovery_digest_oracle_"
        "eq_replay_eq_propose_only_byte_identical_score_commit_stage_provably_inert_sel_value_plus0p000_saturation_"
        "vacuous_scoring_discriminator_accum_compounding_within_body_not_depth_scaling_accum_body_drift_L4_L14_"
        "negative_minus0p041_synthetic_unique_path_graph_not_real_language"
    ),
    "cert_class": (
        "within_sequence_non_compounding_of_a_replay_propose_score_commit_autoregressive_generator_that_recovers_a_"
        "unique_goal_reaching_route_vs_a_growing_leaky_bundle_accumulate_generator_and_a_random_restart_null_on_a_"
        "unique_path_synthetic_generation_graph_where_the_load_bearing_signal_is_the_intra_decline_and_goal_reach_"
        "CONTRAST_replay_flat_accumulate_within_body_compounds_random_floor_measured_across_a_depth_sweep_L4_L8_L14_"
        "N8192_random_bipolar_codes_peel_sic_readout_scoring_value_and_depth_scaling_of_compounding_untested_"
        "saturated_replay_arm_synthetic_not_real_language"
    ),
    "description": (
        "LANDED-VET (AUDIT-ONLY, HIGH) of exp_substrate_gen_lm_replay_propose_score_commit_v11_unique_path_n8192_gpu "
        "(commit 3793f9d94; run_mode=full; 3 seeds 7/17/23; N=8192; L_grid [4,8,14]; headline L=14; chance 0.125; "
        "cell verdict MIDDLE_BAND_PARTIAL). Verified off-disk by independent .venv recompute -- aggregated per_seed[] "
        "over arm x L for all 3 seeds; ALL headline numbers reproduce EXACTLY. "
        "RECOMPUTED CURVES (mean 3 seeds): intra_decline REPLAY 0.000/0.000/0.000 (every seed identically 0.000, cv "
        "0.000), ACCUMULATE 0.283/0.138/0.262 (NON-monotonic in L), RANDOM 0.271/0.149/0.084; body_token_acc REPLAY "
        "1.000/1.000/1.000 (== ORACLE == PROPOSE_ONLY exactly), ACCUM 0.826/0.927/0.867, RANDOM 0.138/0.065/0.039; "
        "goal_reach @L14 REPLAY 1.000 ACCUM 0.392 RANDOM 0.000 -> REP-ACCUM +0.608, REP-RANDOM +1.000 (body +0.961). "
        "MECHANISM: BARRIER2 (recurrent noise-compounding) in the GENERATION domain. v11 uses a UNIQUE-PATH graph so "
        "the exact laid-down route is a clean ~1.0 body ceiling. REPLAY = propose R whole-route candidates by gain-x-"
        "need, score by goal-reach, commit the goal-reacher; on a unique-path graph this recovers THE one goal-route "
        "-> identical to ORACLE. ACCUMULATE = navigate by a growing leaky bundle c_{l+1}=0.65*c+... whose crosstalk "
        "grows -> decodes a WRONG current node -> within-body accuracy declines. RANDOM_RESTART = compute-matched "
        "uniform-out-edge walks (null). REPLAY_PROPOSE_ONLY = gain-x-need proposal but UNIFORM (ungated) selection "
        "(scoring ablation). "
        "FIVE ADVERSARIAL CHECKS (all off per_seed[], not verdict_msg): "
        "(P1) DISCRIMINATOR FIRES AT SCALE, PER-SEED: at N=8192 ACCUM goal_reach 0.51/0.45/0.46 (s7/17/23) @L4 -> "
        "0.40/0.46/0.31 @L14; RANDOM goal_reach ~0 all L. Both must-underperform controls genuinely fail at scale -- "
        "non-vacuous contrast. "
        "(P2) SATURATION OF THE SCORING DISCRIMINATOR (why scoring-value is NOT shown): arm_digests ORACLE == REPLAY "
        "== REPLAY_PROPOSE_ONLY are byte-identical (f05d802280db); sel_value(body @L14) = REPLAY - PROPOSE_ONLY = "
        "+0.000. On a unique-path graph the goal-directed propose step saturates, so uniform vs scored selection land "
        "on the same route -> the SCORE/COMMIT stage is PROVABLY INERT here. v10 (multi-path) DID measure sel_value "
        "+0.073 but had a body_token_acc confound (multiple valid paths). The two versions TRADE OFF: v11 cleaned the "
        "body confound at the cost of saturating scoring; no single version shows BOTH drift-free-body AND scoring-"
        "earns-keep. "
        "(P3) ACCUM COMPOUNDING IS WITHIN-BODY, NOT DEPTH-SCALING: intra_decline fires (late body positions worse -- "
        "e.g. seed7 L14 per_position 1.0...1.0->0.956->0.9->0.79->0.556->0.4) BUT is non-monotonic in L (L4 0.283 > "
        "L8 0.138) and ACCUM body_drift(L4->L14) = 0.826-0.867 = -0.041 (body slightly IMPROVES with depth). The "
        "'REPLAY-ACCUM body gap GROWS with L' HARD_PASS leg FAILS; the compounding is within-sequence, not depth-"
        "scaling. "
        "(P4) TELEMETRY + CARDINALITY: REPLAY/ORACLE/PROPOSE_ONLY are pinned at 1.000 (saturated); the FAILING arms "
        "move with seed (ACCUM goal_reach @L14 0.40/0.46/0.31; RANDOM body @L4 0.123/0.142/0.148) -> data-driven, "
        "not analytically pinned. cardinality 5 arms x 3 L x 3 seeds; arm_digests distinct across the 3 mechanism "
        "families (ORACLE/REPLAY/PROPOSE f05d.., ACCUM 0371.., RANDOM 361b..) -- REPLAY vs ACCUM vs RANDOM genuinely "
        "differ. "
        "(P5) HONEST SCOPE: certifies REPLAY-generation body/goal DOMINANCE over ACCUMULATE + RANDOM on a UNIQUE-PATH "
        "synthetic generation graph (REPLAY drift-free BY CONSTRUCTION of unique-route recovery); does NOT certify "
        "(i) scoring earns its keep (inert here), (ii) depth-scaling of compounding, (iii) any real-language "
        "generation. "
        "CROSS-ARC OVERLAP (USER-locked): substrate_query top cosine 0.2607 (all NOTES; NONE a landed cell >0.30). "
        "BUT the cert_ledger has TWO structurally-adjacent LANDED atoms in the same BARRIER2 arc: community_routed_"
        "glassbox MM (2026-07-08; ARM_C fresh-flat slope 0.001 vs compound slope 0.098, itself flagged flat 'BY "
        "CONSTRUCTION') and the replay_generate_select HF (2026-07-09; replay+select does NOT rescue AUTONOMOUS drift "
        "at the deep high-entropy corner). REDISCOVERY-ADJACENCY CALL: v11 re-instantiates the SAME non-compounding-"
        "by-construction CONTRAST law so it CANNOT be CG -- but it is a GENUINELY NEW TASK DOMAIN (autoregressive "
        "token-body generation vs retrieval-reasoning) with NEW ablations (propose-only + random-restart) and it "
        "usefully SCOPES replay (wins on unique-route/low-entropy; the HF shows it does NOT rescue drift in the hard "
        "high-entropy multi-branch regime). Valid additional MM instance, not a byte-rediscovery. "
        "TIER = MEASURED_MECHANISM (proven boundary): the generation-domain instance of the compounding law is real, "
        "reproduces exactly, discriminator fires non-vacuously at scale -- but the certified content is the CONTRAST "
        "(REPLAY drift-free-by-construction dominates ACCUM within-body compounding + RANDOM null), NOT a stressed "
        "capacity, NOT scoring-value (provably inert), NOT depth-scaling of compounding. Symmetric anti-negativity: "
        "not deflated to MB/HF (contrast clean, cv 0.000, discriminator fires); not inflated to CG (flat-by-"
        "construction, scoring inert, synthetic, re-instantiates an established law). Composes the community_routed_"
        "glassbox MM (same contrast structure) and the BARRIER2 compounding-error HF (bound cross-confirmed + regime "
        "scope). commit 3793f9d94 2026-07-09."
    ),
    "provenance": {
        "cell": "experiments/exp_substrate_gen_lm_replay_propose_score_commit_v11_unique_path_n8192_gpu.py",
        "commit": CELL_COMMIT,
        "metrics_path": "data/exp_substrate_gen_lm_replay_propose_score_commit_v11_unique_path_n8192_gpu/metrics.json",
        "prereg": None,
        "seeds": [7, 17, 23],
        "run_mode": "full",
        "whole_cell_verdict": "MIDDLE_BAND",
        "whole_cell_verdict_msg": "MIDDLE_BAND[REPLAY]_PARTIAL",
        "audit_tier": "MEASURED_MECHANISM",
        "ts_iso": TS_ISO,
        "atomized_by": ATOMIZED_BY,
        "verified_off_data": True,
        "verified_off_data_note": (
            "Independent .venv recompute aggregated per_seed[] over arm x L for all 3 seeds: ALL headline numbers "
            "reproduce EXACTLY. intra_decline REPLAY 0.000 (all 9 seed*L, stdev 0.000) / ACCUM 0.283,0.138,0.262 / "
            "RANDOM 0.271,0.149,0.084. body_token_acc REPLAY 1.000==ORACLE==PROPOSE_ONLY / ACCUM 0.826,0.927,0.867 / "
            "RANDOM 0.138,0.065,0.039. goal_reach @L14 REPLAY 1.000 ACCUM 0.392 RANDOM 0.000 -> REP-ACCUM +0.608, "
            "REP-RANDOM +1.000. sel_value(body @L14)=REPLAY-PROPOSE_ONLY=+0.000 (scoring inert). arm_digest ORACLE=="
            "REPLAY==PROPOSE_ONLY=f05d802280db (byte-identical, saturated); ACCUM=0371e64c, RANDOM=361b02cb. ACCUM "
            "body_drift(L4->L14)=-0.041 (body improves with depth -> depth-scaling leg fails)."
        ),
    },
    "verified_numbers": {
        "N": 8192, "L_grid": [4, 8, 14], "headline_L": 14, "n_seeds": 3, "seeds": [7, 17, 23], "chance": 0.125,
        "intra_decline_REPLAY": {"L4": 0.0, "L8": 0.0, "L14": 0.0},
        "intra_decline_ACCUMULATE": {"L4": 0.28333, "L8": 0.1382, "L14": 0.26213},
        "intra_decline_RANDOM_RESTART": {"L4": 0.27083, "L8": 0.1493, "L14": 0.084},
        "body_token_acc_REPLAY": {"L4": 1.0, "L8": 1.0, "L14": 1.0},
        "body_token_acc_ACCUMULATE": {"L4": 0.82639, "L8": 0.92679, "L14": 0.86699},
        "body_token_acc_RANDOM_RESTART": {"L4": 0.1375, "L8": 0.06548, "L14": 0.03878},
        "goal_reach_L14": {"REPLAY": 1.0, "ACCUMULATE": 0.39167, "RANDOM_RESTART": 0.0},
        "REP_minus_ACCUM_goal_reach_L14": 0.60833, "REP_minus_RANDOM_goal_reach_L14": 1.0,
        "REP_minus_RANDOM_body_L14": 0.96122,
        "sel_value_body_L14": 0.0, "sel_value_goal_reach_L14": 0.0,
        "arm_digest_ORACLE": "f05d802280db67b4351a5809043579bbff49fdc52ed0f750cee5c25fe674cd6f",
        "arm_digest_REPLAY": "f05d802280db67b4351a5809043579bbff49fdc52ed0f750cee5c25fe674cd6f",
        "arm_digest_REPLAY_PROPOSE_ONLY": "f05d802280db67b4351a5809043579bbff49fdc52ed0f750cee5c25fe674cd6f",
        "arm_digest_ACCUMULATE": "0371e64c0befb228dff3c78e0dcc6268d60a3fd596c800b42452c9c7da76225a",
        "arm_digest_RANDOM_RESTART": "361b02cb0615ed5ef185e7e57b30c16556944022d9bc8aac9587329ac84e8c47",
        "replay_body_cv_across_seeds": 0.0, "replay_body_stdev": 0.0,
        "accum_body_drift_L4_to_L14": -0.0406, "accum_intra_decline_monotonic_in_L": False,
        "oracle_body_L14": 1.0, "cardinality_arms": 5, "cardinality_L": 3, "cardinality_ok": True,
        "arms_differ_verified": True, "discriminator_fires_at_scale": True, "all_headline_reproduce_exact": True,
    },
    "can_fail_discriminator_verdict": (
        "PARTIALLY FIRES + telemetry-sensitive on the arms that matter, but the SCORING sub-discriminator is "
        "SATURATION-VACUOUS. (1) The REPLAY-vs-baselines discriminator FIRES at N=8192: ACCUMULATE (must-underperform "
        "compounding baseline) genuinely declines within-body (intra_decline 0.14-0.28, goal_reach collapses to "
        "0.39-0.48) and RANDOM_RESTART (null) sits at goal_reach ~0 / body 0.04-0.14 -- the HARD_FAIL 'win is "
        "redundancy' branch was reachable (REPLAY-RANDOM > NO_RECOMB_BAND) and did not fire; both controls fail per-"
        "seed at scale. (2) Seed perturbation moves the FAILING arms (ACCUM/RANDOM goal_reach + body vary across "
        "7/17/23) -> not analytically pinned. (3) BUT the sel_value>0 gate (does score/commit beat propose-only) is "
        "SATURATION-VACUOUS here: on a unique-path graph the goal-directed proposal already saturates, so PROPOSE_"
        "ONLY produces the byte-identical route (digest f05d.. == REPLAY == ORACLE), sel_value=+0.000 -> the scoring "
        "stage CANNOT be shown load-bearing. (4) The 'ACCUM body gap grows with L' (depth-scaling) leg is NOT "
        "supported: ACCUM body_drift(L4->L14)=-0.041 and intra_decline is non-monotonic in L. So the cell CAN and "
        "DOES fire the compounding-vs-bounded CONTRAST, but CANNOT fire the scoring-value or depth-scaling claims at "
        "this saturated unique-path regime -- precisely why this is a PROVEN BOUNDARY (MM), not a HARD_PASS."
    ),
    "framing_corrections_vs_cell_author_and_director": [
        "MISFRAMING to CORRECT (verdict_msg): 'scoring earns its keep (sel_value=+0.000)' is INTERNALLY CONTRADICTORY. "
        "sel_value=+0.000 with arm_digest REPLAY == REPLAY_PROPOSE_ONLY (byte-identical) PROVES the score/commit stage "
        "is INERT at this regime, NOT that it earns its keep. This resolves the distinction Director asked for: "
        "drift-free IS demonstrated (REPLAY body 1.000, cv 0.000) BUT scoring-value is NOT demonstrated (saturation-"
        "vacuous) -- the FIRST of Director's two cases.",
        "REPLAY drift-free is largely BY CONSTRUCTION, not a stressed capacity result: on the v11 unique-path graph, "
        "scoring-by-goal-reach recovers THE one goal-reaching route, so REPLAY output is byte-identical to the ORACLE "
        "(same digest f05d..). Bake this into any downstream framing: the certified content is the CONTRAST (REPLAY "
        "drift-free vs ACCUMULATE within-body compounding vs RANDOM null), NOT an unstressed 'depth-invariant "
        "generation' capacity claim. This mirrors the sibling community_routed MM, which explicitly flags its flat "
        "arm as flat 'BY CONSTRUCTION'.",
        "ACCUMULATE 'compounds error WITH DEPTH' is only PARTIALLY shown: it compounds WITHIN body (intra_decline "
        "0.14-0.28 fires; late positions worse) but does NOT scale with depth -- intra_decline is non-monotonic in L "
        "(L4 0.283 > L8 0.138) and ACCUM body_token_acc actually IMPROVES slightly L4->L14 (drift -0.041). The "
        "verdict_msg note 'ACCUM body_drift(L4->L14)=-0.041 (>0=compounds)' is self-refuting: -0.041 is NOT >0.",
        "SYMMETRIC anti-negativity: do NOT deflate this to MB/HF -- the compounding-vs-bounded contrast is clean, "
        "reproduces exactly off-disk with cv=0.000, and the discriminator fires non-vacuously at N=8192 (both "
        "controls genuinely fail at scale). Equally, do NOT inflate to a drift-free-generation CG -- REPLAY is flat "
        "by construction + saturated, scoring is inert, and this re-instantiates an already-established compounding "
        "law (community_routed MM 07-08; BARRIER2 HF 07-09) rather than proving a new mechanism.",
        "REDISCOVERY-ADJACENCY (USER-locked cross-arc check): substrate_query returned only NOTES <0.30, but the "
        "cert_ledger shows the non-compounding-by-construction CONTRAST is already MM'd (community_routed_glassbox). "
        "v11 is NOT a byte-rediscovery -- it is a new TASK DOMAIN (autoregressive token-body generation) with new "
        "ablations -- but that adjacency is the reason it lands MM (additional instance), not CG.",
        "SCOPE the replay mechanism honestly against the BARRIER2 HF: replay WINS here because a UNIQUE goal-reaching "
        "route exists to recover (low-entropy); the replay_generate_select HF (07-09) proves replay+select does NOT "
        "rescue AUTONOMOUS chain drift in the HARD high-entropy multi-branch regime. This atom must not be read as "
        "'replay solves generation drift' -- it solves it only where a recoverable unique route exists.",
    ],
    "revival_or_extension_criterion": (
        "MM scope: certifies the REPLAY-vs-ACCUMULATE-vs-RANDOM body/goal CONTRAST (REPLAY drift-free by unique-route "
        "recovery, ACCUM within-body compounding, RANDOM null) on a synthetic unique-path generation graph, N=8192, "
        "L up to 14, 3 seeds. PROMOTE-toward-CG / EXTENSIONS (each a NEW cell, composes NOT supersedes): (1) SHOW "
        "SCORING EARNS ITS KEEP WITHOUT A BODY CONFOUND -- a regime where the goal-directed propose step does NOT "
        "saturate (e.g. multiple goal-reaching routes of differing body-fidelity, or a NOISY proposal) so score/"
        "commit measurably beats propose-only (sel_value>0) on a metric that also stays clean; this is the axis v10 "
        "and v11 each got half of. (2) DEPTH-SCALING OF COMPOUNDING -- design so ACCUM's within-body decline "
        "MONOTONICALLY grows with L (the current graph's per-L difficulty is not depth-monotone); demonstrate REPLAY-"
        "ACCUM body gap grows with L. (3) STRESS REPLAY OFF ITS CEILING -- a graph where the unique route is NOT "
        "trivially recoverable (noisy codes, longer routes, larger width) so REPLAY body < 1.000 with headroom; does "
        "it stay bounded when it is NOT saturated. (4) REAL-LANGUAGE / NON-UNIQUE-PATH generation. DEMOTION trigger: "
        "a re-run where ACCUMULATE does NOT compound within-body (intra_decline < DECLINE_MIN at all L) or RANDOM "
        "does not fail (the discriminator goes inert), or REPLAY drops below its body ceiling on the unique path."
    ),
    "composes": [P_SIBLING, P_BOUND],
    "compose_note": (
        "Composes (1) the community_routed_glassbox_reasoning_scale_v1 MM (2026-07-08): SAME contrast structure -- a "
        "non-compounding channel stays FLAT by construction while a compounding channel degrades; that atom already "
        "flags its flat arm as flat 'BY CONSTRUCTION' and that 'the load-bearing content is the CONTRAST proving "
        "compounding is the collapse driver'. This v11 atom is the GENERATION-DOMAIN counterpart of that retrieval-"
        "reasoning cross-confirm. And (2) the HARD_FAIL_STRUCTURAL_COMPOUNDING_ERROR_BOUND (BARRIER2 replay_generate_"
        "select HF, 2026-07-09): the compounding-error bound this cross-confirms from the generation angle, AND the "
        "regime scope -- replay+select does NOT rescue drift in the hard high-entropy autonomous regime, so v11's "
        "replay win is scoped to the low-entropy unique-route regime where a recoverable route exists. Brain-"
        "grounding: replay / hippocampal trajectory recovery vs raw leaky-integrator drift (bounded per-step re-clean "
        "vs unbounded accumulation)."
    ),
    "cross_arc_overlap_check": (
        "substrate_query 'replay propose score commit drift-free depth-invariant generation accumulate error "
        "compounding' -> top cosine 0.2607 (NOTES only: 'Composition cost (noise accumulation)' 0.2607, long-form-"
        "generation handoff 0.2588, NOISE-COMPOUNDING backup-doc principle 0.252), NONE a landed cell at cosine>0.30. "
        "Cert_ledger audit reveals two structurally-adjacent LANDED atoms (community_routed_glassbox MM 07-08; "
        "replay_generate_select HF 07-09) -- the non-compounding-by-construction contrast is already MM'd. v11 is a "
        "GENUINELY NEW TASK DOMAIN (autoregressive token-body generation vs retrieval-reasoning) with new ablations "
        "(propose-only scoring ablation + random-restart null), NOT a byte-rediscovery; that adjacency is precisely "
        "why it lands MM (additional instance), not CG. The July-1 INT8-rediscovery failure mode is FLAGGED and "
        "handled (composed, not re-certified as novel CG)."
    ),
    "anchor": "substrate_gen_lm_replay_propose_score_commit_v11_unique_path_n8192_gpu",
    "cell_commit": CELL_COMMIT,
    "seeds": [7, 17, 23],
    "run_mode": "full",
    "cardinality_ok": True,
    "arms_differ_verified": True,
    "verified_off_data": True,
    "auditor": "hdi_skunkworks",
    "atomized_by": "hdi_skunkworks",
    "landed_VET_session": SESSION,
    "needs_orchestrator_store_sync": True,
    "ts": TS,
    "ts_iso": TS_ISO,
    "ts_added": TS_ISO,
    "aliases": [
        "substrate REPLAY-propose-score-commit generation is the generation-domain instance of the recurrent noise-compounding law (BARRIER2); MEASURED_MECHANISM proven boundary",
        "on a unique-path generation graph REPLAY recovers the goal route drift-free (intra_decline 0.000 body 1.000 flat all L cv 0.000) and dominates ACCUMULATE within-body compounding and RANDOM null",
        "REP-ACCUM goal_reach +0.608, REP-RANDOM +1.000 body +0.961 at L14; discriminator fires at N=8192 (both controls genuinely fail at scale)",
        "BOUNDARY: REPLAY flat BY CONSTRUCTION (arm_digest ORACLE==REPLAY==PROPOSE_ONLY byte-identical f05d..); score/commit stage PROVABLY INERT sel_value=+0.000 (saturation-vacuous scoring discriminator)",
        "verdict_msg 'scoring earns its keep (sel_value=+0.000)' is a misframing: +0.000 with digest-identity proves scoring is inert, drift-free demonstrated but scoring-value NOT demonstrated",
        "ACCUM compounds WITHIN body (intra_decline 0.14-0.28) but NOT with depth (non-monotonic in L; body_drift L4->L14 = -0.041); depth-scaling HARD_PASS leg fails",
        "SCOPE: synthetic unique-path graph not real language; re-instantiates the non-compounding-by-construction contrast in a new task domain; replay wins only where a unique goal route exists (low-entropy)",
        "gen_lm_replay_propose_score_commit_v11_unique_path landed-VET MEASURED_MECHANISM",
    ],
    "added_atom_id": None,
}
atom["added_atom_id"] = atom["id"]

ledger = {
    "ts": TS, "ts_iso": TS_ISO, "op": "add", "atom_id": atom["id"], "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "disposition": "measured_mechanism_proven_boundary_gen_lm_replay_propose_score_commit_v11_unique_path_generation_domain_instance_of_recurrent_noise_compounding_law_barrier2",
    "cert_status": atom["cert_status"],
    "cert_class": atom["cert_class"],
    "cert_increment_delta": {"CG": 0, "MM": 1, "HF": 0},
    "cert_delta": {"CG": 0, "MM": 1, "HF": 0},
    "cert_delta_note": (
        "MM +1 (proven boundary): substrate REPLAY-propose-score-commit generation is the GENERATION-DOMAIN instance "
        "of the recurrent noise-compounding law (BARRIER2). On a UNIQUE-PATH synthetic generation graph (N=8192, 3 "
        "seeds 7/17/23, L_grid [4,8,14], chance 0.125) REPLAY recovers the one goal-reaching route with ZERO within-"
        "body decline (intra_decline 0.000, body 1.000, FLAT across L, cv 0.000) and DOMINATES both an ACCUMULATE "
        "generator (growing leaky bundle, within-body compounding intra_decline 0.28/0.14/0.26, goal_reach "
        "0.48/0.44/0.39) and a RANDOM_RESTART null (goal_reach ~0). @L14 REP-ACCUM goal_reach +0.608, REP-RANDOM "
        "+1.000 (body +0.961). Discriminator FIRES at N=8192 (both controls genuinely fail at scale). Verified off-"
        "disk by independent .venv recompute -- all headline curves reproduce EXACTLY. WHY MM NOT CG: (i) REPLAY "
        "drift-free is BY CONSTRUCTION -- arm_digest ORACLE==REPLAY==PROPOSE_ONLY byte-identical (f05d802280db), "
        "saturated 1.000 cv 0.000; (ii) the SCORE/COMMIT stage is PROVABLY INERT (sel_value +0.000; uniform-select "
        "PROPOSE_ONLY lands on the same route because goal-directed proposal saturates on a unique-path graph) -- "
        "'scoring earns its keep' is NOT shown (saturation-vacuous; v10 multi-path showed +0.073 but had a body "
        "confound, the two versions trade off); (iii) ACCUM compounding is WITHIN-body not depth-scaling (intra_"
        "decline non-monotonic in L; ACCUM body_drift L4->L14 = -0.041). FRAMING CORRECTION: verdict_msg 'scoring "
        "earns its keep (sel_value=+0.000)' is self-contradictory; +0.000 with digest-identity proves scoring inert "
        "-- drift-free demonstrated, scoring-value NOT demonstrated (Director's first case). SCOPE: synthetic unique-"
        "path graph, NOT real language; certifies the REPLAY/ACCUMULATE/RANDOM contrast, not scoring value or depth-"
        "scaling. Cross-arc: re-instantiates the non-compounding-by-construction contrast already MM'd (community_"
        "routed_glassbox 07-08), in a NEW task domain (autoregressive token-body generation) -- valid additional "
        "instance not byte-rediscovery, hence MM not CG. Scopes replay via BARRIER2 HF (replay+select does NOT rescue "
        "autonomous drift in the hard high-entropy regime; v11 replay wins only where a unique route exists). "
        "Symmetric anti-negativity: not deflated (contrast clean, cv 0.000, discriminator fires), not inflated (flat-"
        "by-construction, scoring inert, synthetic). Composes community_routed_glassbox MM + BARRIER2 compounding-"
        "error HF. Needs orchestrator Store-sync (skunkworks atoms do not auto-persist)."
    ),
    "verified_off_data": True,
    "verification": "recomputed_intra_decline_body_token_acc_goal_reach_curves_per_arm_all_3seed_exact_match + arm_digest_identity_ORACLE_eq_REPLAY_eq_PROPOSE_ONLY_confirms_scoring_inert + accum_body_drift_L4_L14_negative_depth_scaling_leg_fails + cross_arc_ledger_audit_finds_sibling_community_routed_MM_and_BARRIER2_HF",
    "anchor": "substrate_gen_lm_replay_propose_score_commit_v11_unique_path_n8192_gpu",
    "cell_commit": CELL_COMMIT,
    "auditor": "hdi_skunkworks", "atomized_by": "hdi_skunkworks",
    "landed_VET_session": SESSION,
    "composes": [P_SIBLING, P_BOUND],
    "needs_orchestrator_store_sync": True,
    "raw_metrics_paths": ["data/exp_substrate_gen_lm_replay_propose_score_commit_v11_unique_path_n8192_gpu/metrics.json"],
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
    append_jsonl_a5(MATH_ATOMS, atom, "math/atoms (gen_lm replay v11 unique-path BARRIER2 generation-instance MEASURED_MECHANISM)")
    append_jsonl_a5(CERT_LEDGER, ledger, "cert_ledger (MM +1)")
    print(f"[A5] DONE OK -> gen_lm replay-propose-score-commit v11 unique-path BARRIER2 generation-domain MEASURED_MECHANISM (MM +1)")


if __name__ == "__main__":
    main()
