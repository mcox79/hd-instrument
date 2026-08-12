"""
A5-gated atomize: LANDED-VET (AUDIT-ONLY, XHIGH) of community_routed_glassbox_reasoning_scale_v1.
CORRECTED TIER = MEASURED_MECHANISM (proven-bound + barrier-#2 cross-confirm). NOT the cell's HARD_PASS
chain-grade: the scale-invariance headline RE-DEMONSTRATES an existing MM boundary and the routed arm is
at ceiling (never stressed to its own cliff). The genuine new increment is the independent-channel
NON-COMPOUNDING cross-confirmation of barrier #2.

CELL metrics: data/exp_community_routed_glassbox_reasoning_scale_v1/metrics.json (run_mode=full, N=8192,
  3 seeds 7/17/23, V_grid [580,2900,12000,30000], depth [2,3,4,5,6,8], verdict HARD_PASS, 15/15 units).

INDEPENDENT OFF-DISK RECOMPUTE (.venv, this session; off per_seed[] raw counts, NOT verdict_msg):
  - flat_succ cross-seed mean: V580=0.44010 (0.515625/0.375/0.4296875, cv 0.132), V2900=V12000=V30000=0.0.
    flat rel_deg = (0.44010-0)/0.44010 = 1.000. EXACT match.
  - routed_succ = oracle_succ = 1.000 at EVERY V/seed; routed rel_deg = 0.000; cv 0.000.
  - fresh_hazard rebuilt from raw sum(fail)/sum(at_risk) over 3 seeds: [0.14323,0.12918,0.13787,0.15789,
    0.15144,0.14731,0.14618,0.14008] -> EXACT match reported. fresh_slope (polyfit) = 0.00101 EXACT.
  - compound_hazard rebuilt: [0.14323,0.37994,0.55147,0.74317,0.74468,0.58333,0.8,1.0] -> EXACT match.
    compound_slope = 0.09756 EXACT. compound aggregate at_risk 768->1 (last hazard 1.0 from ONE sample).
  - modularity per-seed true-min = 0.6975 at V30000 (reported 'min' 0.7027 = min-over-V of seed-MEAN);
    both >> 0.30. n_comm*comm_size approx V exactly (600/2916/12100/30102) -> real store built at each V.
  - fresh vs compound: SAME V=12000, Q=256, SAME 3 seeds, both start at_risk 256 -> PAIRED, clean.

FOUR AUDIT VERDICTS:
  (1) DISCRIMINATOR TELEMETRY-SENSITIVE / NOT SATURATION-VACUOUS: the must-fail FLAT control GENUINELY
      collapses at scale (0.440 -> 0.0 by V=2900, per-seed) -> the harness CAN produce failure; the
      routed 1.000 is measured off genuinely-different per-seed data (routed_hash DIFFERS across seeds
      7/17/23 while succ=1.000) -> not analytically pinned. Scale genuinely exercised: 15/15 units, V=30000
      present all 3 seeds with distinct hashes, comm_size grows 24->173. elapsed 58s is fine (N=8192 GPU).
  (2) WHY MM NOT CG -- REDISCOVERY of an existing MM boundary: the "routing keeps chain success flat as V
      scales while flat collapses" claim is the SAME mechanism as community_bounded_retrieval_scale_
      invariance_v1 (cc804bfc1, MM) -- same V-sweep design, same seeds 7/17/23, same route_acc=1.000, same
      flat-collapse. And the routed arm is at CEILING (routed_succ=1.000, zero headroom) with comm_size
      24->173, ALL below the ~580 flat-collapse knee / the ~630 within-community Plate cliff that v1
      independently measured (comm 630->0.680). SAME within-envelope boundary -> total-V invariance within
      the community-capacity envelope, NOT unbounded. Cross-arc check catches the July-1 rediscovery pattern.
  (3) GLASS-BOX-AT-SCALE already CG-covered: replay/merkle/tamper/routing_causal_flip/tamper=1.000 at every
      V incl V=30000 is telemetry-sensitive and intact, BUT glass-box multihop reasoning at scale is ALREADY
      chain-grade via glass_box_micro_loop_conceptnet_multihop_SCALE_v1 (de7385271), which is STRICTLY
      STRONGER: NON-CEILING (accB 0.933 <= 0.95, graded) AND real ConceptNet topology. This synthetic-KB
      ceiling-saturated version cannot claim a fresh glass-box CG. Also: ARM_B_ROUTED_WITHIN == ARM_ORACLE_
      ROUTE byte-identical (same hash every seed/V) because route_acc=1.000 collapses them -> the oracle
      "within-community ceiling" gate adds NO independent information here.
  (4) THE GENUINE NEW INCREMENT (why atomize, MM): independent-channel NON-COMPOUNDING cross-confirm of
      barrier #2. fresh_slope=0.00101 (flat, per-hop hazard ~0.14 across 8 hops) vs compound_slope=0.09756
      (rises 0.14->0.38->0.55->0.74). The fresh arm's flat slope is largely BY-CONSTRUCTION (an independent
      fresh channel each hop cannot compound); the load-bearing content is the CONTRAST proving compounding
      is the collapse driver -- cross-confirming the compounding-error bound (HARD_FAIL_STRUCTURAL_
      COMPOUNDING_ERROR_BOUND_REAL) and the 3rd-instance recurrent-noise-compounding-bound MM_SYNTHESIS from
      the OTHER direction (an independent channel escapes the bound). Caveat: compound tail is noisy
      (at_risk 768->1; last hazard 1.0 from one sample), but the rise is decisive over hops 1-4.

TIER = MEASURED_MECHANISM: mechanism real, reproduces EXACT off-disk, discriminator telemetry-sensitive,
  scale genuinely exercised -- BUT (a) the scale-invariance headline re-demonstrates the v1 MM boundary,
  (b) routed arm at ceiling never stressed to own cliff (comm_size 173 << ~630), (c) glass-box-at-scale CG
  is already held by a stronger real-topology non-ceiling version. Symmetric anti-negativity: NOT deflated
  to MB/HF (all gates genuine, numbers exact); NOT inflated to a fresh HARD_PASS CG (rediscovery + ceiling).
  CERT delta: MM +1 (proven-boundary extension + barrier-#2 cross-confirm), CG +0, HF +0, no demotion.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_atomize_2026_07_08_community_routed_glassbox_reasoning_scale_v1_MEASURED_MECHANISM"
CELL_COMMIT = "unknown_no_commit_field_in_metrics_verified_off_metrics_json_mtime_2026-07-08T22:37"
TS = time.time()
TS_ISO = "2026-07-08T00:00:00Z"
SESSION = "2026-07-08_community_routed_glassbox_reasoning_scale_v1_landed_vet_CORRECTED_MM_barrier2_crossconfirm"

# Parent 1: the v1 community-bounded scale-invariance MM (the boundary this RE-DEMONSTRATES / extends).
P_V1_COMMUNITY = (
    "math::MEASURED_MECHANISM_community_bounded_two_stage_retrieval_DECOUPLES_CROSSTALK_from_TOTAL_store_size_"
    "BARRIER3_the_additive_store_crosstalk_wall_M_lt_N_over_2lnV_makes_a_dense_GLOBAL_bundle_COLLAPSE_as_total_"
    "V_grows_but_a_TWO_STAGE_hippocampal_index_plus_community_route_stage1_argmax_over_a_sqrtV_near_orthogonal_"
    "gist_codebook_then_stage2_unbind_plus_peel_sic_fine_decode_WITHIN_the_selected_community_only_converts_the_"
    "crosstalk_relevant_codebook_from_total_V_to_active_community_size_sqrtV_over_a_100x_V_sweep_580_2900_29000_"
    "58000_N8192_3seed_7_17_23_CONTROL_dense_additive_fid_0p789_to_0p023_to_0p000_to_0p000_rel_deg_1p000_PER_"
    "SEED_ZERO_at_both_V29000_and_V58000_discriminator_FIRES_at_scale_non_vacuous_WHILE_TREATMENT_fid_1p000_"
    "FLAT_rel_deg_0p000_cv_0p000_route_acc_1p000_at_n_comm_241_all_seeds_the_load_bearing_scale_invariance_"
    "evidence_routing_does_not_degrade_with_V_min_Newman_Q_0p510_at_V58000_real_community_structure_not_toy_"
    "store_gist_decoupled_abs_cos_0p009_near_orthogonal_correlation_hurts_store_telemetry_sensitive_seed_"
    "perturb_moves_control_fid_0p023_to_0p039_0p047_nothing_pinned_reproduces_BIT_EXACT_off_disk_all_hashes_"
    "PROVEN_BOUNDARY_NOT_CG_the_treatment_is_NEVER_stressed_to_its_OWN_ceiling_community_size_241_well_below_"
    "the_within_community_Plate_cliff_630_MEASURED_independently_comm64_1p000_comm241_0p992_comm630_0p680_"
    "comm1000_0p313_comm2000_0p094_so_flat_is_TOTAL_V_invariance_WITHIN_the_community_capacity_envelope_NOT_"
    "unlimited_capacity_SCOPE_synthetic_community_structured_KB_not_real_ingested_topology_certifies_total_V_"
    "decoupling_does_NOT_certify_within_community_capacity_v2_community_of_communities_2nd_tier_plus_higher_"
    "per_community_load_composes_FHRR_bundle_capacity_CG_commit_cc804bfc1_2026-07-08"
)
# Parent 2: the compounding-error-bound HARD_FAIL (barrier #2 the fresh-vs-compound contrast cross-confirms).
P_COMPOUND_HF = (
    "math::HARD_FAIL_STRUCTURAL_COMPOUNDING_ERROR_BOUND_REAL_coarse_to_fine_waypoint_bisection_does_NOT_rescue_"
    "autonomous_decomposition_at_the_deepest_high_entropy_corner_5seed_FULL_GPU_250units_op4_V1200_d8_ent16_OPEN_"
    "autonomous_0p097_eq_coarse2fine_0p100_ZERO_lift_recovery_rescue_0p0232_lt_0p20_delta_recovery_0p004_lt_0p15_"
    "sign_p_0p1797_ns_rescue_beats_open_False_n_hp_ok_0_of_5_all_3_HARD_PASS_bars_FAIL_the_SMOKE_DIRECTIONAL_"
    "SIGNAL_REVERSED_smoke_delta_plus0p112_spearman_delta_ent_plus0p500_FULL_delta_plus0p004_spearman_minus0p237_"
    "SIGN_FLIP_GENUINE_BOUND_not_machinery_oracle_exec_rail_0p918_hier_oracle_given_decomp_0p906_headroom_decomp_"
    "ok_controls_collapse_hier_shuffled_0p0017_wp_random_0p0175_anti_taut_0p0013_degen_0p000_index_leak_False_"
    "brs_cv_0p118_coarse_to_fine_rescues_the_SHALLOW_corner_op4_d4_OPEN_eq_c2f_0p823_only_because_OPEN_already_"
    "high_nothing_to_rescue_delta_0_but_CANNOT_extend_autonomous_decomposition_to_the_DEEP_corner_where_OPEN_"
    "collapses_to_0p10_DAgger_oracle_next_lever_out_of_scope_narrow_glass_box_2026-07-06"
)
# Parent 3: the 3rd-instance recurrent-noise-compounding-bound MM_SYNTHESIS (cross-mechanism law).
P_COMPOUND_SYNTH = (
    "math::MEASURED_MECHANISM_SYNTHESIS_depth6_goal_conditioned_control_gating_CLOSED_BOTH_rescue_levers_FAILED_"
    "cerebellar_anticipatory_rollout_recovered_frac_minus1p40_this_cell_AND_prior_lookahead_waypoint_bisection_"
    "autonomous_decomp_compounding_error_HARD_FAIL_incumbent_one_step_SR_reach_remains_BEST_d6_lift_0p097_"
    "MECHANISM_CLUE_multi_step_lookahead_COMPOUNDS_cleanup_noise_3RD_INSTANCE_recurrent_noise_compounding_bound_"
    "composing_resonator_basin_proliferation_MM_and_autonomous_decomp_compounding_error_HF_MM_TENTATIVE_cross_"
    "mechanism_law_2026-07-07"
)

ATOM_ID = (
    "math::MEASURED_MECHANISM_community_routed_glassbox_reasoning_scale_v1_BARRIER2_CROSSCONFIRM_a_community_"
    "routed_glass_box_reasoning_chain_stays_FLAT_routed_succ_1p000_rel_deg_0p000_over_a_V_sweep_580_2900_12000_"
    "30000_N8192_3seed_7_17_23_depth_2to8_WHILE_a_FLAT_whole_store_chain_COLLAPSES_flat_succ_0p440_to_0p000_by_"
    "V2900_perseed_rel_deg_1p000_discriminator_FIRES_glass_box_audit_INTACT_at_scale_replay_merkle_tamper_"
    "routing_causal_flip_tamper_all_1p000_at_every_V_incl_V30000_route_acc_1p000_modularityQ_min_0p698_real_"
    "structure_reproduces_EXACT_off_disk_all_hashes_PROVEN_BOUNDARY_NOT_CG_because_i_the_scale_invariance_"
    "headline_RE_DEMONSTRATES_community_bounded_retrieval_scale_invariance_v1_MM_same_Vsweep_design_same_seeds_"
    "same_route_acc_1p000_and_ii_the_ROUTED_arm_is_at_CEILING_routed_succ_1p000_zero_headroom_comm_size_24_to_"
    "173_ALL_below_the_apprx580_flat_collapse_knee_and_apprx630_within_community_Plate_cliff_so_flat_is_total_V_"
    "invariance_WITHIN_the_community_capacity_envelope_NOT_unbounded_and_iii_glass_box_multihop_at_scale_is_"
    "ALREADY_CG_via_glass_box_micro_loop_conceptnet_multihop_SCALE_v1_which_is_NON_CEILING_accB_0p933_and_REAL_"
    "ConceptNet_topology_strictly_stronger_ARM_B_ROUTED_WITHIN_eq_ARM_ORACLE_ROUTE_byte_identical_hash_every_"
    "seed_V_because_route_acc_1p000_so_oracle_ceiling_gate_adds_no_independent_info_THE_GENUINE_NEW_INCREMENT_"
    "is_the_independent_channel_NON_COMPOUNDING_cross_confirm_of_BARRIER2_ARM_C_FRESH_slope_0p00101_flat_per_hop_"
    "hazard_apprx0p14_across_8_hops_vs_ARM_C_COMPOUND_slope_0p09756_rises_0p14_0p38_0p55_0p74_SAME_V12000_Q256_"
    "SAME_3seed_PAIRED_the_fresh_flat_slope_is_largely_BY_CONSTRUCTION_independent_channel_cannot_compound_the_"
    "load_bearing_content_is_the_CONTRAST_proving_compounding_is_the_collapse_driver_cross_confirming_the_"
    "compounding_error_bound_HARD_FAIL_and_the_3rd_instance_recurrent_noise_compounding_bound_from_the_OTHER_"
    "direction_an_independent_fresh_channel_ESCAPES_the_bound_compound_tail_noisy_at_risk_768_to_1_last_hazard_"
    "1p000_from_one_sample_but_rise_decisive_over_hops_1to4_SCOPE_synthetic_community_structured_KB_not_real_"
    "ingested_topology_EXTENDS_community_bounded_retrieval_scale_invariance_v1_MM_2026-07-08"
)

atom = {
    "id": ATOM_ID,
    "name": (
        "MEASURED_MECHANISM (proven boundary + barrier-#2 cross-confirm): community-routed GLASS-BOX reasoning "
        "chain stays FLAT (routed_succ 1.000, rel_deg 0.000) over a V-sweep [580,2900,12000,30000] N=8192 3seed "
        "depth 2-8 WHILE a FLAT whole-store chain COLLAPSES (flat_succ 0.440->0.000 by V=2900, per-seed, rel_deg "
        "1.000 -> discriminator fires). Glass-box audit INTACT at scale (replay/merkle/tamper/routing_causal_"
        "flip/tamper all 1.000 at every V incl V=30000); route_acc 1.000; min Newman Q~0.698 (real structure). "
        "CORRECTED TIER = MM not the cell's HARD_PASS CG because (i) the scale-invariance headline RE-"
        "DEMONSTRATES community_bounded_retrieval_scale_invariance_v1 (MM; same V-sweep design, same seeds, same "
        "route_acc=1.000), (ii) the ROUTED arm is at CEILING (routed_succ 1.000, zero headroom; comm_size 24->173 "
        "ALL below the ~580 flat-collapse knee / ~630 within-community Plate cliff) -> total-V invariance WITHIN "
        "the community-capacity envelope, NOT unbounded, and (iii) glass-box-multihop-at-scale is already CG via "
        "glass_box_micro_loop_conceptnet_multihop_SCALE_v1 (NON-CEILING accB 0.933, REAL ConceptNet topology -- "
        "strictly stronger). ARM_B_ROUTED_WITHIN == ARM_ORACLE_ROUTE byte-identical (route_acc=1.000) -> oracle "
        "'ceiling' gate adds no independent info. THE GENUINE NEW INCREMENT: independent-channel NON-COMPOUNDING "
        "cross-confirm of BARRIER #2 -- ARM_C_FRESH slope=0.00101 flat (per-hop hazard ~0.14 across 8 hops) vs "
        "ARM_C_COMPOUND slope=0.09756 rising (0.14->0.38->0.55->0.74), SAME V=12000/Q=256/3 seeds (paired). The "
        "fresh-flat is largely by-construction (independent channel cannot compound); the load-bearing content is "
        "the CONTRAST proving compounding is the collapse driver -- cross-confirming the compounding-error bound "
        "(HARD_FAIL) and the 3rd-instance recurrent-noise compounding-bound from the OTHER direction (a fresh "
        "channel escapes it). SCOPE: synthetic community-structured KB, not real ingested topology. EXTENDS v1 MM."
    ),
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet",
    "cert_status": (
        "mm_community_routed_glassbox_reasoning_scale_routed_chain_flat_succ_1p000_rel_deg_0p000_over_Vsweep_580_"
        "2900_12000_30000_while_flat_whole_store_chain_collapses_0p440_to_0p000_perseed_rel_deg_1p000_"
        "discriminator_fires_glass_box_replay_merkle_tamper_causal_flip_1p000_at_every_V_incl_30000_route_acc_"
        "1p000_modQ_min_0p698_reproduces_exact_off_disk_PROVEN_BOUNDARY_scale_invariance_redemonstrates_v1_"
        "community_bounded_MM_routed_at_ceiling_comm_size_24_to_173_below_580_knee_630_cliff_total_v_invariance_"
        "within_envelope_not_unbounded_glassbox_at_scale_already_CG_via_conceptnet_nonceiling_realtopology_armB_"
        "eq_armOracle_byte_identical_route_acc_1p000_GENUINE_INCREMENT_barrier2_crossconfirm_fresh_slope_0p00101_"
        "flat_vs_compound_slope_0p09756_rising_paired_same_V12000_Q256_3seed_fresh_flat_by_construction_contrast_"
        "proves_compounding_is_collapse_driver_independent_channel_escapes_compounding_bound_synthetic_kb"
    ),
    "cert_class": (
        "total_V_scale_invariance_of_a_community_routed_glass_box_multi_hop_reasoning_chain_route_to_community_"
        "then_reason_within_it_vs_a_flat_whole_store_chain_control_over_a_V_sweep_where_the_slope_contrast_flat_"
        "collapses_routed_flat_is_the_discriminator_with_a_per_hop_merkle_tamper_and_causal_hand_edit_glass_box_"
        "audit_intact_at_every_scale_PLUS_an_independent_channel_non_compounding_probe_fresh_channel_bounded_"
        "per_hop_hazard_flat_slope_vs_a_compound_channel_rising_hazard_paired_same_V_Q_seeds_the_routed_effective_"
        "store_is_the_active_community_size_held_below_the_within_community_bundle_capacity_cliff_store_codes_"
        "near_orthogonal_guarded_by_measured_newman_modularity_synthetic_community_structured_kb_routed_own_"
        "capacity_ceiling_untested_glass_box_capability_frontier_already_certified_by_a_stronger_real_topology_"
        "non_ceiling_conceptnet_cell"
    ),
    "description": (
        "LANDED-VET (AUDIT-ONLY, XHIGH) of exp_community_routed_glassbox_reasoning_scale_v1 (run_mode=full; 3 "
        "seeds 7/17/23; N=8192; V_grid [580,2900,12000,30000]; depth [2,3,4,5,6,8]; V_compound=12000, Qc=256; "
        "verdict HARD_PASS; 15/15 units card_ok; elapsed 58.3s). Verified off-disk by independent .venv recompute "
        "from per_seed[] raw counts (NOT verdict_msg): flat_succ cross-seed V580=0.44010 (0.515625/0.375/"
        "0.4296875, cv 0.132), V2900=V12000=V30000=0.0 -> flat rel_deg 1.000 EXACT; routed_succ=oracle_succ=1.000 "
        "every V/seed -> routed rel_deg 0.000, cv 0.000; fresh_hazard rebuilt from sum(fail)/sum(at_risk) over 3 "
        "seeds = [0.14323,0.12918,0.13787,0.15789,0.15144,0.14731,0.14618,0.14008] EXACT, fresh_slope polyfit "
        "0.00101 EXACT; compound_hazard = [0.14323,0.37994,0.55147,0.74317,0.74468,0.58333,0.8,1.0] EXACT, "
        "compound_slope 0.09756 EXACT; modularity per-seed true-min 0.6975@V30000 (reported 'min' 0.7027 = min-"
        "over-V of the seed-MEAN), both >> 0.30; n_comm*comm_size approx V EXACT (600/2916/12100/30102) -> real "
        "store built at each V. FOUR AUDIT VERDICTS (all off per_seed[]): "
        "(1) DISCRIMINATOR TELEMETRY-SENSITIVE / NOT SATURATION-VACUOUS: the must-fail FLAT control GENUINELY "
        "collapses (0.440->0.0 by V=2900, per-seed) -> the harness CAN produce failure; routed 1.000 is measured "
        "off genuinely-different per-seed data (routed_hash DIFFERS across seeds 7/17/23 while succ=1.000) -> not "
        "analytically pinned. Scale genuinely exercised: 15/15 units, V=30000 present all 3 seeds with distinct "
        "hashes, comm_size grows 24->173; elapsed 58s is consistent with N=8192 GPU (not a smoke shortcut). "
        "(2) WHY MM NOT CG -- REDISCOVERY of an existing MM boundary: the 'routing keeps chain success flat as V "
        "scales while flat collapses' claim is the SAME mechanism as community_bounded_retrieval_scale_invariance"
        "_v1 (cc804bfc1, MM) -- same V-sweep design, same seeds 7/17/23, same route_acc=1.000, same flat-collapse. "
        "And the routed arm is at CEILING (routed_succ 1.000, zero headroom) with comm_size 24->173, ALL below "
        "the ~580 flat-collapse knee (flat@580=0.44) and the ~630 within-community Plate cliff that v1 measured "
        "independently (comm 630->0.680). SAME within-envelope boundary -> total-V invariance within the "
        "community-capacity envelope, NOT unbounded. Cross-arc overlap check caught the July-1 rediscovery "
        "pattern. "
        "(3) GLASS-BOX-AT-SCALE already CG-covered: replay/merkle/tamper/routing_causal_flip/tamper=1.000 at "
        "every V incl V=30000 is telemetry-sensitive (causal_flip requires a hand-edit to change downstream; "
        "tamper_detect requires merkle to catch edits) and genuinely intact -- BUT glass-box multihop reasoning "
        "at scale is ALREADY chain-grade via glass_box_micro_loop_conceptnet_multihop_SCALE_v1 (de7385271), which "
        "is STRICTLY STRONGER: NON-CEILING (accB 0.933 <= 0.95, graded decay 0.927->0.848) AND real ConceptNet "
        "topology. This synthetic-KB ceiling-saturated (routed 1.000) version cannot claim a fresh glass-box CG. "
        "Also: ARM_B_ROUTED_WITHIN == ARM_ORACLE_ROUTE byte-identical (same hash every seed/V) because route_acc="
        "1.000 collapses them -> the oracle 'within-community ceiling' (Gate D) adds NO independent information "
        "here. "
        "(4) THE GENUINE NEW INCREMENT (why atomize, and why MM not a bare note): independent-channel NON-"
        "COMPOUNDING cross-confirm of barrier #2. ARM_C_FRESH slope=0.00101 (flat; per-hop hazard ~0.14 across "
        "8 hops, span 0.129-0.158) vs ARM_C_COMPOUND slope=0.09756 (rises 0.14->0.38->0.55->0.74->...->1.0), "
        "SAME V=12000/Q=256/3 seeds, both start at_risk 256 (PAIRED, clean). The fresh-flat slope is largely BY-"
        "CONSTRUCTION (an independent fresh channel each hop cannot compound); the load-bearing content is the "
        "CONTRAST proving compounding is the collapse driver -- cross-confirming the compounding-error bound "
        "(HARD_FAIL_STRUCTURAL_COMPOUNDING_ERROR_BOUND_REAL) and the 3rd-instance recurrent-noise compounding-"
        "bound MM_SYNTHESIS from the OTHER direction (an independent channel ESCAPES the bound; routing is one "
        "such escape). Caveat: the compound tail is noisy (aggregate at_risk 768->1; last hazard 1.0 from ONE "
        "sample), but the rise is decisive over hops 1-4. "
        "TIER = MEASURED_MECHANISM: mechanism real, reproduces EXACT off-disk, discriminator telemetry-sensitive, "
        "scale genuinely exercised -- BUT the scale-invariance headline re-demonstrates the v1 MM, the routed arm "
        "is at ceiling never stressed to its own cliff (comm_size 173 << ~630), and glass-box-at-scale CG is "
        "already held by a stronger real-topology non-ceiling cell. Symmetric anti-negativity: NOT deflated to "
        "MB/HF (all gates genuine, numbers exact, glass-box intact); NOT inflated to a fresh HARD_PASS CG "
        "(rediscovery + ceiling). EXTENDS community_bounded_retrieval_scale_invariance_v1 MM (both stay live; v1 "
        "= single-retrieval total-V axis, this = multi-hop chain + glass-box + barrier-2 cross-confirm). Composes "
        "the compounding-error-bound HARD_FAIL and the 3rd-instance recurrent-noise compounding-bound. SCOPE: "
        "synthetic community-structured KB, not real ingested topology. commit (no field in metrics; verified off "
        "metrics.json mtime 2026-07-08T22:37) 2026-07-08."
    ),
    "provenance": {
        "cell": "experiments/exp_community_routed_glassbox_reasoning_scale_v1.py",
        "commit": CELL_COMMIT,
        "metrics_path": "data/exp_community_routed_glassbox_reasoning_scale_v1/metrics.json",
        "seeds": [7, 17, 23],
        "run_mode": "full",
        "whole_cell_verdict": "HARD_PASS",
        "audit_tier": "MEASURED_MECHANISM",
        "ts_iso": TS_ISO,
        "atomized_by": ATOMIZED_BY,
        "verified_off_data": True,
        "verified_off_data_note": (
            "Independent .venv recompute off per_seed[] raw counts: flat cross-seed V580=0.44010 "
            "(0.515625/0.375/0.4296875, cv 0.132), V2900/12000/30000=0.0 -> flat rel_deg 1.000; routed=oracle="
            "1.000 all V/seed, routed rel_deg 0.000 cv 0.000; fresh_hazard rebuilt sum(fail)/sum(at_risk) 3seed "
            "EXACT [0.14323..0.14008], fresh_slope 0.00101; compound_hazard EXACT [0.14323..1.0], compound_slope "
            "0.09756; compound aggregate at_risk 768->658->408->183->47->12->5->1 (last hazard 1.0 from 1 "
            "sample); modularity per-seed true-min 0.6975@V30000 (reported 'min' 0.7027 = min-over-V of seed-"
            "mean); n_comm*comm_size approx V EXACT (600/2916/12100/30102); ARM_B routed_hash == ARM_ORACLE "
            "oracle_hash byte-identical every seed/V (route_acc=1.000); fresh vs compound SAME V=12000 Q=256 3 "
            "seeds paired; 15/15 units card_ok."
        ),
    },
    "verified_numbers": {
        "N": 8192, "V_grid": [580, 2900, 12000, 30000], "V_compound": 12000, "Qc": 256,
        "depth_grid": [2, 3, 4, 5, 6, 8], "n_seeds": 3, "seeds": [7, 17, 23],
        "flat_succ_curve": {"580": 0.4401041666666667, "2900": 0.0, "12000": 0.0, "30000": 0.0},
        "flat_succ_perseed_V580": [0.515625, 0.375, 0.4296875], "flat_cv_V580": 0.132,
        "flat_rel_deg": 1.0, "flat_collapse_rd_floor": 0.30,
        "routed_succ_curve": {"580": 1.0, "2900": 1.0, "12000": 1.0, "30000": 1.0},
        "routed_rel_deg": 0.0, "routed_flat_rd_ceiling": 0.10, "routed_cv": 0.0,
        "oracle_succ_curve": {"580": 1.0, "2900": 1.0, "12000": 1.0, "30000": 1.0},
        "armB_routed_eq_armOracle_hash": True,
        "route_acc_curve": {"580": 1.0, "2900": 1.0, "12000": 1.0, "30000": 1.0}, "route_acc_Vmax": 1.0,
        "comm_size_curve": {"580": 24, "2900": 54, "12000": 110, "30000": 173},
        "n_comm_curve": {"580": 25, "2900": 54, "12000": 110, "30000": 174},
        "modularity_Q_seedmean_curve": {"580": 0.9509642924, "2900": 0.9811609137, "12000": 0.9525436575, "30000": 0.7026689615},
        "modularity_Q_perseed_true_min": 0.6975449462648089, "modularity_floor": 0.30,
        "glassbox_replay_min": 1.0, "glassbox_merkle_verify_min": 1.0, "glassbox_tamper_detect_min": 1.0,
        "glassbox_routing_causal_flip_min": 1.0, "glassbox_routing_causal_tamper_min": 1.0, "n_causal": 128,
        "fresh_hazard": [0.14322916666666666, 0.12917933130699089, 0.13787085514834205, 0.15789473684210525,
                         0.15144230769230768, 0.14730878186968838, 0.1461794019933555, 0.14007782101167315],
        "fresh_slope": 0.0010095510102513087, "fresh_slope_ceiling": 0.02, "fresh_slope_recompute_exact": True,
        "compound_hazard": [0.14322916666666666, 0.3799392097264438, 0.5514705882352942, 0.7431693989071039,
                            0.7446808510638298, 0.5833333333333334, 0.8, 1.0],
        "compound_slope": 0.0975571365732376, "compound_slope_recompute_exact": True,
        "compound_aggregate_at_risk": [768, 658, 408, 183, 47, 12, 5, 1],
        "compound_tail_last_hazard_from_n_samples": 1,
        "n_comm_times_comm_size_approx_V": {"580": 600, "2900": 2916, "12000": 12100, "30000": 30102},
        "within_community_plate_cliff_approx_from_v1": 630, "flat_collapse_knee_approx": 580,
        "top_scale_comm_size": 173, "elapsed_s": 58.257, "cardinality_units": 15, "cardinality_expected": 15,
        "cardinality_ok": True, "all_recompute_exact_match": True,
    },
    "can_fail_discriminator_verdict": (
        "FIRES and is TELEMETRY-SENSITIVE. (1) The FLAT whole-store chain was the must-fail guard: it GENUINELY "
        "collapses 0.440->0.0 by V=2900 per-seed (rel_deg 1.000 >= 0.30 floor) -> the crosstalk-in-chain regime "
        "is exercised, the discriminator-inert branch was reachable and did NOT fire. (2) routed_succ=1.000 is "
        "measured off per-seed data whose routed_hash DIFFERS across seeds 7/17/23 -> not analytically pinned "
        "(different random draws all succeed because effective store = comm_size 24-173 stays below the ~580 knee/"
        "~630 cliff). (3) modularity guard reachable (Q<0.30 -> no-structure fail); per-seed min 0.698 clears it. "
        "(4) glass-box gates are can-fail: routing_causal_flip requires a logged hand-edit to actually change "
        "the downstream root (would read <1 if the routing were causally inert); tamper_detect requires merkle "
        "to catch edits (would read <1 if the hash chain were decorative); both read 1.000 at every scale incl "
        "V=30000. (5) fresh_slope<=0.02 is a real gate that the COMPOUND arm (same primitives, compounding) fails "
        "at 0.0976 -> the flat-slope reads genuine per-hop hazard, not a pinned zero. BOUNDARY-AWARE: routed CAN "
        "fail (v1 independently measured the SAME fine-decode collapsing once community exceeds ~630); it is "
        "simply never pushed there here (comm_size 173). That is why this is a PROVEN BOUNDARY (MM), not a "
        "fresh unbounded CG."
    ),
    "framing_corrections_vs_cell_author_and_director": [
        "DIRECTOR FRAMED THIS AS A 'strong-cert CANDIDATE / HARD_PASS'; the cell's self-verdict HARD_PASS is "
        "CORRECT for its pre-registered joint gate (routed flat AND flat collapse AND route>=0.90 AND Q>=0.30 "
        "AND glass-box=1 AND fresh_slope<=0.02) and ALL structured gate claims reproduce EXACT off disk. But the "
        "AUDIT tier is MEASURED_MECHANISM, not a fresh chain-grade. HONEST DOWNWARD CORRECTION (symmetric anti-"
        "negativity): the scale-invariance headline is a RE-DEMONSTRATION of community_bounded_retrieval_scale_"
        "invariance_v1 (MM) -- same V-sweep design, same seeds 7/17/23, same route_acc=1.000, same flat-collapse "
        "-- so it inherits the SAME within-envelope boundary, it is not a new CG. Do NOT deflate it either: the "
        "cell is clean and adds genuine value (glass-box on routed chains + the barrier-2 cross-confirm).",
        "THE ROUTED ARM IS AT A CEILING (routed_succ=1.000, zero headroom). comm_size grows 24->173 but ALL of "
        "it stays below the ~580 flat-collapse knee (flat@580=0.44, the point where the whole-store chain is "
        "already half-collapsed) and the ~630 within-community Plate cliff that v1 measured independently. So "
        "'scale-invariant' means total-V invariance WITHIN the community-capacity envelope; it does NOT establish "
        "unbounded reasoning-at-scale. Push per-community reasoning load toward/over ~630 (or add a 2nd routing "
        "tier) to stress the routed arm's own axis -- that is the promote-toward-CG lever.",
        "GLASS-BOX-AT-SCALE IS ALREADY CHAIN-GRADE via glass_box_micro_loop_conceptnet_multihop_SCALE_v1 "
        "(de7385271), which is STRICTLY STRONGER on both axes: NON-CEILING (accB 0.933 <= 0.95, graded decay) and "
        "REAL ConceptNet topology. This cell's glass-box gates (replay/merkle/tamper/causal-flip=1.000 at every "
        "V incl V=30000) are genuine and telemetry-sensitive, but on a SYNTHETIC KB with a SATURATED routed arm "
        "-- so they add confirmation, not a new glass-box capability frontier.",
        "ARM_B_ROUTED_WITHIN and ARM_ORACLE_ROUTE are BYTE-IDENTICAL (same hash every seed/V) because "
        "route_acc=1.000 collapses them. The 'oracle within-community ceiling' (Gate D) therefore adds NO "
        "independent information in this run -- routed IS oracle. Not a flaw, but the report should not cite "
        "oracle as an independent witness of the routed result.",
        "THE LOAD-BEARING NEW CONTRIBUTION IS THE BARRIER-#2 CROSS-CONFIRM, not the scale-invariance. fresh_slope="
        "0.00101 (flat) vs compound_slope=0.09756 (rising), paired same V/Q/seeds, cross-confirms that the "
        "compounding-error bound (HARD_FAIL_STRUCTURAL_COMPOUNDING_ERROR_BOUND_REAL, 3rd-instance recurrent-noise "
        "compounding-bound) is REAL and that an independent/fresh channel escapes it. NOTE the fresh-flat is "
        "largely BY-CONSTRUCTION (an independent channel cannot compound); frame the value as CONFIRMING the "
        "compounding mechanism from the other direction, NOT as a surprising discovery. Compound tail is noisy "
        "(at_risk 768->1; last hazard 1.0 from one sample) -- rely on hops 1-4 for the rise.",
        "SYNTHETIC KB caveat (SUBSTRATE-KNOWS-NOTHING): the community structure is generated (near-orthogonal "
        "codes + separate gist routing space), not real ingested graph topology; n_comm*comm_size approx V "
        "confirms a real store was built at each V, but the routing/reasoning is over synthetic structure.",
    ],
    "revival_or_extension_criterion": (
        "MM scope: certifies TOTAL-V scale-invariance of a community-routed glass-box reasoning CHAIN (routed "
        "effective store = active community size, held below the ~630 within-community cliff) vs a collapsing "
        "flat whole-store chain, at N=8192, V up to 30000, depth 2-8, synthetic community-structured KB, 3 "
        "seeds; PLUS an independent-channel non-compounding cross-confirm of barrier #2. PROMOTE-toward-CG / "
        "EXTENSIONS (each a NEW cell, composes NOT supersedes): (1) STRESS THE ROUTED ARM'S OWN AXIS -- push "
        "per-community reasoning load toward/over the ~630 within-community cliff (and/or add a community-of-"
        "communities 2nd routing tier) so the routed chain is graded, not saturated at 1.000; a NON-CEILING "
        "routed-flat contrast on a stressed within-community load would be CG-worthy. (2) REAL INGESTED TOPOLOGY "
        "-- run on real graph communities where store codes carry semantic correlation (correlation-hurts-store). "
        "(3) MEASURE THE FRESH-CHANNEL HAZARD FLOOR at higher V and deeper chains to bound the per-hop escape "
        "rate quantitatively. DEMOTION trigger: if a re-run shows FLAT fails to collapse (rd<0.30, discriminator "
        "inert), OR route_acc<0.90 with V, OR modularity Q<0.30, OR any glass-box gate (replay/merkle/tamper/"
        "causal_flip) drops below its floor, OR fresh_slope exceeds 0.02 (fresh channel starts compounding)."
    ),
    "composes": [P_V1_COMMUNITY, P_COMPOUND_HF, P_COMPOUND_SYNTH],
    "compose_note": (
        "EXTENDS community_bounded_retrieval_scale_invariance_v1 (MM): v1 = single-retrieval total-V decoupling; "
        "this = multi-hop reasoning CHAIN + glass-box audit + the barrier-2 cross-confirm, over the SAME "
        "community-routing mechanism and the SAME within-envelope boundary (routed effective store = community "
        "size, held below the ~630 within-community Plate cliff). Both stay live (different axes). CROSS-CONFIRMS "
        "barrier #2: the fresh (bounded slope 0.00101) vs compound (rising slope 0.09756) contrast confirms the "
        "compounding-error bound HARD_FAIL_STRUCTURAL_COMPOUNDING_ERROR_BOUND_REAL and the 3rd-instance "
        "recurrent-noise compounding-bound MM_SYNTHESIS from the OTHER direction -- routing/independent-channel "
        "is the escape from compounding. Glass-box-multihop-at-scale is already CG via glass_box_micro_loop_"
        "conceptnet_multihop_SCALE_v1 (de7385271, NON-CEILING, real ConceptNet) -- this synthetic-KB ceiling-"
        "saturated version confirms but does not extend that CG frontier."
    ),
    "cross_arc_overlap_check": (
        "substrate_query 'community routing scale-invariant chain reasoning modular store' -> top cosine 0.3252 "
        "(REASONING_ROUTING_PASS note), 0.3105 (PP-371 reasoning_routing concept), both >0.30. Direct atom "
        "inspection: community_bounded_retrieval_scale_invariance_v1 (cc804bfc1, MM) is a NEAR-DUPLICATE of the "
        "scale-invariance headline (same V-sweep design, same seeds, same route_acc=1.000, same flat-collapse, "
        "same routed-unstressed caveat), and glass_box_micro_loop_conceptnet_multihop_SCALE_v1 (de7385271, CG) "
        "already holds the glass-box-multihop-at-scale frontier NON-CEILING on real ConceptNet. So the July-1 "
        "INT8-rediscovery pattern DOES partially apply here: the scale-invariance + glass-box components are "
        "re-demonstrations, which is exactly why the tier is MM (targeted extension via the barrier-2 cross-"
        "confirm) and NOT a fresh HARD_PASS CG. The genuinely-new element (independent-channel non-compounding "
        "cross-confirm of barrier #2) is a targeted extension, not a rediscovery."
    ),
    "anchor": "community_routed_glassbox_reasoning_scale_v1",
    "cell_commit": CELL_COMMIT,
    "seeds": [7, 17, 23],
    "run_mode": "full",
    "cardinality_ok": True,
    "arms_differ_verified": True,
    "arms_differ_note": "ARM_A_FLAT distinct (collapses); ARM_B_ROUTED_WITHIN == ARM_ORACLE_ROUTE byte-identical (route_acc=1.000); ARM_C_FRESH vs ARM_C_COMPOUND distinct hashes, paired.",
    "verified_off_data": True,
    "auditor": "hdi_skunkworks",
    "atomized_by": "hdi_skunkworks",
    "landed_VET_session": SESSION,
    "needs_orchestrator_store_sync": True,
    "ts": TS,
    "ts_iso": TS_ISO,
    "ts_added": TS_ISO,
    "aliases": [
        "community-routed glass-box reasoning chain stays flat over V-sweep while flat whole-store chain collapses; MEASURED_MECHANISM proven boundary (re-demonstrates v1)",
        "routed_succ 1.000 rel_deg 0.000 (ceiling, comm_size 24->173 below ~630 cliff) vs flat_succ 0.440->0.000 rel_deg 1.000 over V [580,2900,12000,30000] N=8192 3seed depth 2-8",
        "glass-box audit intact at scale replay/merkle/tamper/routing_causal_flip=1.000 at every V incl V=30000 (telemetry-sensitive; already CG via ConceptNet non-ceiling cell)",
        "barrier-2 cross-confirm: ARM_C_FRESH slope 0.00101 flat vs ARM_C_COMPOUND slope 0.09756 rising, paired same V=12000 Q=256 3seed -- independent channel escapes the compounding-error bound",
        "ARM_B_ROUTED_WITHIN == ARM_ORACLE_ROUTE byte-identical because route_acc=1.000 (oracle ceiling gate adds no independent info)",
        "community_routed_glassbox_reasoning_scale_v1 landed-VET MEASURED_MECHANISM corrected-from-HARD_PASS",
    ],
    "added_atom_id": None,
}
atom["added_atom_id"] = atom["id"]

ledger = {
    "ts": TS, "ts_iso": TS_ISO, "op": "add", "atom_id": atom["id"], "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "disposition": "measured_mechanism_proven_boundary_community_routed_glassbox_reasoning_scale_redemonstrates_v1_plus_barrier2_crossconfirm_CORRECTED_from_cell_HARD_PASS",
    "cert_status": atom["cert_status"],
    "cert_class": atom["cert_class"],
    "cert_increment_delta": {"CG": 0, "MM": 1, "HF": 0},
    "cert_delta": {"CG": 0, "MM": 1, "HF": 0},
    "cert_delta_note": (
        "MM +1 (proven-boundary extension + barrier-2 cross-confirm), CORRECTED DOWN from the cell's HARD_PASS "
        "self-verdict. A community-routed glass-box reasoning CHAIN stays flat (routed_succ 1.000, rel_deg 0.000) "
        "over a V-sweep [580,2900,12000,30000] N=8192 3seed depth 2-8 while a FLAT whole-store chain collapses "
        "(0.440->0.000 by V=2900, per-seed, rel_deg 1.000 -> discriminator fires); glass-box audit intact at "
        "scale (replay/merkle/tamper/routing_causal_flip/tamper=1.000 at every V incl V=30000); route_acc 1.000; "
        "min Newman Q~0.698. ALL numbers reproduce EXACT off-disk by independent .venv recompute from per_seed[] "
        "raw counts (fresh_slope 0.00101, compound_slope 0.09756, flat/routed rel_deg, hazards all EXACT). WHY MM "
        "NOT CG: (i) the scale-invariance headline RE-DEMONSTRATES community_bounded_retrieval_scale_invariance_v1 "
        "(cc804bfc1, MM) -- same V-sweep design, same seeds, same route_acc=1.000; (ii) the ROUTED arm is at "
        "CEILING (routed_succ 1.000, zero headroom; comm_size 24->173 all below the ~580 flat-collapse knee / "
        "~630 within-community Plate cliff) -> total-V invariance WITHIN the community-capacity envelope, NOT "
        "unbounded; (iii) glass-box-multihop-at-scale is ALREADY CG via glass_box_micro_loop_conceptnet_multihop_"
        "SCALE_v1 (de7385271, NON-CEILING accB 0.933, REAL ConceptNet -- strictly stronger). ARM_B_ROUTED_WITHIN "
        "== ARM_ORACLE_ROUTE byte-identical (route_acc=1.000) -> oracle ceiling gate adds no independent info. "
        "THE GENUINE NEW INCREMENT: independent-channel NON-COMPOUNDING cross-confirm of barrier #2 -- fresh_slope "
        "0.00101 flat vs compound_slope 0.09756 rising, paired same V=12000/Q=256/3seed; the fresh-flat is "
        "largely by-construction (independent channel cannot compound), the load-bearing content is the CONTRAST "
        "confirming compounding is the collapse driver, cross-confirming HARD_FAIL_STRUCTURAL_COMPOUNDING_ERROR_"
        "BOUND_REAL and the 3rd-instance recurrent-noise compounding-bound from the other direction. Discriminator "
        "telemetry-sensitive (flat control genuinely fails; routed_hash differs across seeds while succ=1.000; "
        "seed perturb moves flat). Scale genuinely exercised (15/15 units, V=30000 all 3 seeds distinct hashes, "
        "comm_size 24->173, n_comm*comm_size approx V). SCOPE: synthetic community-structured KB, not real "
        "ingested topology. Symmetric anti-negativity: NOT deflated to MB/HF (all gates genuine, numbers exact, "
        "glass-box intact); NOT inflated to a fresh CG (rediscovery + ceiling). EXTENDS v1 MM; composes the "
        "compounding-error-bound HF + 3rd-instance MM_SYNTHESIS. Needs orchestrator Store-sync (skunkworks atoms "
        "do not auto-persist)."
    ),
    "verified_off_data": True,
    "verification": "recomputed_off_per_seed_raw_counts_all_EXACT: flat_rel_deg_1p000 routed_rel_deg_0p000 fresh_hazard+slope_0p00101 compound_hazard+slope_0p09756 modularity_perseed_min_0p698 n_comm_x_comm_size_approx_V armB_eq_armOracle_hash cardinality_15of15 + cross_arc_overlap_found_v1_MM_near_dup_and_conceptnet_CG_stronger",
    "anchor": "community_routed_glassbox_reasoning_scale_v1",
    "cell_commit": CELL_COMMIT,
    "auditor": "hdi_skunkworks", "atomized_by": "hdi_skunkworks",
    "landed_VET_session": SESSION,
    "composes": [P_V1_COMMUNITY, P_COMPOUND_HF, P_COMPOUND_SYNTH],
    "needs_orchestrator_store_sync": True,
    "raw_metrics_paths": ["data/exp_community_routed_glassbox_reasoning_scale_v1/metrics.json"],
    "corrected_from_cell_verdict": "HARD_PASS -> MEASURED_MECHANISM (rediscovery of v1 MM + routed at ceiling + glass-box already CG via stronger cell)",
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
    append_jsonl_a5(MATH_ATOMS, atom, "math/atoms (community-routed glass-box reasoning scale MEASURED_MECHANISM)")
    append_jsonl_a5(CERT_LEDGER, ledger, "cert_ledger (MM +1, corrected from HARD_PASS)")
    print(f"[A5] DONE OK -> community-routed glass-box reasoning scale MEASURED_MECHANISM (MM +1, corrected)")


if __name__ == "__main__":
    main()
