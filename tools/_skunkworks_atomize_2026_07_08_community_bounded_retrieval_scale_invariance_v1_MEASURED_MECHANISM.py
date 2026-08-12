"""
A5-gated atomize: LANDED-VET (AUDIT-ONLY, HIGH) of community_bounded_retrieval_scale_invariance_v1.
BARRIER #3 (store crowding at massive scale). TIER = MEASURED_MECHANISM (proven-bound).

CELL: experiments/exp_community_bounded_retrieval_scale_invariance_v1.py (commit cc804bfc1)
METRICS: data/exp_community_bounded_retrieval_scale_invariance_v1/metrics.json (run_mode=full,
  3 seeds 7/17/23, N=8192, V_grid [580,2900,29000,58000], SCP-recovered local; verdict HARD_PASS).

INDEPENDENT OFF-DISK RECOMPUTE (.venv, this session -- re-ran run_one_V for all 3 seeds x 4 V):
  ALL EXACT MATCH on ctrl_fid, treat_fid, route_acc, comm_size, n_comm, and BOTH pred SHA256 hashes.
  metrics.json is genuine + deterministic (not stale/fabricated).

FIVE ADVERSARIAL PROBES (each off per_seed[], not verdict_msg):
  P1 DISCRIMINATOR FIRES AT SCALE, PER-SEED: CONTROL ctrl_fid = 0.0 at V=29000 AND V=58000 for ALL
     3 seeds (0.789->0.023->0.0->0.0 aggregate; per-seed collapse confirmed). Non-vacuous contrast at
     the TOP scales. Control_rd=1.000. PASS.
  P2 THE KEY CAVEAT (load-bearing, the reason this is MM not CG): TREATMENT treat_fid=1.000 flat is
     GENUINE total-V decoupling BUT is NOT stressed to its own ceiling. Independent stress probe
     (re-ran the treatment fine-decode in isolation at inflated community sizes, N=8192):
       comm_size  64 -> 1.000 | 241 -> 0.992 | 630 -> 0.680 | 1000 -> 0.313 | 2000 -> 0.094
     The ACTUAL top-scale community size is 241 (=round(sqrt(58000))), which sits WELL BELOW the
     within-community Plate cliff ~630 (N/(2 ln comm)). So treatment is flat across the tested range
     ONLY because effective load (comm_size 24->241) stays deep inside its own capacity envelope. The
     honest claim is "community-routing decouples crosstalk from TOTAL-V (total-size no longer crowds)",
     NOT "unlimited capacity". route_acc=1.000 at n_comm=241 all seeds IS the load-bearing scale-
     invariance evidence (routing codebook grows as sqrt(V) and does not degrade within range) -- but
     n_comm=241 is likewise well under the routing codebook's own cliff, so routing is also unstressed.
  P3 MODULARITY GUARD: min Newman Q = 0.510 at V=58000 (0.951/0.981/0.708/0.510 across V), all >>0.30
     and non-degenerate. Community structure is real; treatment-flat is NOT measured on a trivially-
     separable toy. Reproduced per-seed. PASS.
  P4 TELEMETRY + COMPOSITION: perturbing the seed MOVES control fid (V=2900: canonical 0.023 vs
     seed999 0.039, seed1234 0.047) -> nothing analytically pinned; the collapse reads the data.
     treat stays 1.000 (saturated within capacity, per P2). peel_sic_readout(n_items=1) is used
     CORRECTLY as the within-community/whole-V DECODE (confidence-ordered argmax), NOT as a retrieval-
     agreement fix -- the treatment advantage comes entirely from the SMALLER (community) codebook, not
     from peel/SIC; consistent with the prior finding that peel/SIC does not help single-cue NN. Store
     decoupled from routing gist: |cos|~0.009 (near-orthogonal), matching the correlation-hurts-store
     design. PASS.
  P5 HONEST SCOPE (baked into atom): certifies TOTAL-V scale-invariance of community-bounded two-stage
     retrieval (effective-V = active-community size, decoupled from total store size); does NOT certify
     within-community capacity (separate axis; community-of-communities 2nd tier + higher per-community
     load is the named v2). Synthetic community-structured KB, NOT real ingested topology.

CROSS-ARC OVERLAP: substrate_query "community-bounded two-stage retrieval hippocampal index routing
  scale invariance crosstalk total store size decouple effective V" -> top cosine 0.2588 (all NOTES:
  design/orchestrator summaries), NONE a landed cell at cosine>0.30. Consistent with prereg's own check
  (0.2705 hippocampal_index.py design note). GENUINELY NOVEL two-stage coarse-route + fine-decode cell.

TIER = MEASURED_MECHANISM: the decoupling mechanism is real, correctly implemented, reproduces bit-exact,
  discriminator fires non-vacuously per-seed, telemetry-sensitive, modularity real -- BUT the treatment
  arm is never stressed to its own ceiling (community size 241 << measured cliff ~630), so the claim is
  the PROVEN BOUNDARY "crosstalk decoupled from TOTAL-V", not a full capacity proof. Counts toward CERT N
  as a proven boundary. Symmetric anti-negativity: NOT deflated to MB/HF (mechanism clean); NOT inflated
  to CG (treatment unstressed).
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_atomize_2026_07_08_community_bounded_retrieval_scale_invariance_v1_MEASURED_MECHANISM"
CELL_COMMIT = "cc804bfc1"
TS = time.time()
TS_ISO = "2026-07-08T00:00:00Z"
SESSION = "2026-07-08_community_bounded_retrieval_scale_invariance_v1_landed_vet_TOTAL_V_DECOUPLING_MM"

# compose parents: the FHRR bundle-capacity CG (the Plate/order-statistic boundary that bounds BOTH
# the CONTROL collapse at total-V AND the treatment within-community decode cliff ~630 at N=8192).
P_CAPACITY = (
    "math::CHAIN_GRADE_SELF_REASONING_the_substrate_predicts_its_OWN_FHRR_bundle_cleanup_capacity_K_crit_"
    "EXACTLY_via_a_PARAMETER_FREE_order_statistic_bundle_geometry_adaptation_of_the_RNS_exact_prefactor_"
    "family_E_Phi_x_over_sqrt_NK2_pow_Vminus1_x_N_mean_var_N_Km1_over_2_gauss_hermite_64pt_NO_fitted_"
    "constants_5SEED_FULL_7_13_19_23_29_K_crit_cross_seed_stability_CONFIRMED_cv_max_0p0154_1p54pct_within_"
    "5pct_bar_cv_per_N_0p0015_to_0p0154_per_seed_K_crit_tightly_clustered_exact_arm_dev_le_1p22pct_at_ALL_5_"
    "N_1024_to_16384_vs_the_MEAN_of_5_seeds_max_0p0122_clears_5pct_while_the_loose_Plate_N_over_2lnN_"
    "asymptotic_stays_10_to_35pct_off_exact_is_LOAD_BEARING_rel_improve_up_to_114x_pointwise_cleanup_recall_"
    "CLIFF_predicted_exactly_RMS_0p0013_controls_FIRE_wrong_scaling_coherent_crosstalk_SEPARATED_89_to_97pct_"
    "degenerate_rank1_book_collapses_to_chance_1_over_V_genuine_parameter_free_derivation_NOT_a_fudge_"
    "PROMOTED_MM_to_CG_the_single_seed_axis_that_held_it_at_MM_is_RESOLVED_matching_the_5seed_RNS_v2_CG_"
    "precedent_SUPERSEDES_the_single_seed_MM_atom_same_anchor_EXTENDS_rns_subblock_margin_exact_prefactor_v2_"
    "new_codebook_family_2nd_self_reasoning_CG_does_NOT_auto_promote_the_3_landed_bundle_capacity_MIDDLE_BAND_"
    "cells_which_still_need_a_separate_re_VET_off_their_own_metrics_MONITOR_not_control_predicts_own_capacity_"
    "never_modifies_config_NOT_self_improvement_full_2026-07-06"
)

ATOM_ID = (
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

atom = {
    "id": ATOM_ID,
    "name": (
        "MEASURED_MECHANISM (proven boundary): community-bounded two-stage retrieval DECOUPLES crosstalk "
        "from TOTAL store size. BARRIER #3. Over a 100x total-V sweep (580->58000, N=8192, 3 seeds), a "
        "dense-additive GLOBAL-bundle CONTROL collapses (fid 0.789->0.000, rel_deg 1.000, per-seed ZERO at "
        "both V=29000 and V=58000 -> discriminator fires at scale) while a hippocampal-index + community-"
        "route TREATMENT (stage-1 argmax over a ~sqrt(V) near-orthogonal gist codebook, stage-2 unbind + "
        "peel/SIC fine-decode WITHIN the selected community only) stays FLAT (fid 1.000, rel_deg 0.000, "
        "cv 0.000). route_acc=1.000 at n_comm=241 all seeds is the load-bearing scale-invariance evidence "
        "(routing does not degrade with V). min Newman Q=0.510 (real community structure). BOUNDARY (why MM "
        "not CG): treatment is NEVER stressed to its own ceiling -- community size 241 sits well below the "
        "within-community Plate cliff ~630 (independently MEASURED: comm 630->0.680, 1000->0.313, 2000->"
        "0.094). So flat = TOTAL-V invariance WITHIN the community-capacity envelope, NOT unlimited capacity. "
        "SCOPE: synthetic community-structured KB (not real ingested topology); certifies total-V decoupling, "
        "does NOT certify within-community capacity (v2: community-of-communities 2nd tier + higher load)."
    ),
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet",
    "cert_status": (
        "mm_community_bounded_two_stage_retrieval_decouples_crosstalk_from_total_store_size_control_dense_"
        "additive_collapses_perseed_zero_at_v29000_and_v58000_discriminator_fires_at_scale_treatment_flat_"
        "fid_1p000_cv0p000_route_acc_1p000_at_n_comm_241_load_bearing_min_newmanQ_0p510_real_structure_gist_"
        "decoupled_abs_cos_0p009_telemetry_sensitive_reproduces_bit_exact_off_disk_PROVEN_BOUNDARY_treatment_"
        "unstressed_community_size_241_below_measured_within_community_plate_cliff_630_total_v_invariance_"
        "within_capacity_envelope_not_unlimited_synthetic_kb_not_real_topology"
    ),
    "cert_class": (
        "total_store_size_scale_invariance_of_a_two_stage_coarse_community_route_then_community_scoped_fine_"
        "decode_retrieval_vs_a_dense_additive_global_bundle_control_over_a_100x_V_sweep_where_the_slope_"
        "contrast_control_collapses_treatment_flat_is_the_discriminator_effective_V_equals_active_community_"
        "size_sqrtV_decoupled_from_total_V_store_codes_near_orthogonal_random_decoupled_from_a_separate_"
        "community_gist_routing_space_guarded_by_measured_newman_modularity_synthetic_community_structured_"
        "kb_random_bipolar_codes_within_community_capacity_bound_untested"
    ),
    "description": (
        "LANDED-VET (AUDIT-ONLY, HIGH) of exp_community_bounded_retrieval_scale_invariance_v1 (commit "
        "cc804bfc1; run_mode=full; 3 seeds 7/17/23; N=8192; V_grid [580,2900,29000,58000]; verdict "
        "HARD_PASS). Metrics SCP-recovered local; verified off-disk by independent .venv recompute -- "
        "re-ran run_one_V for all 3 seeds x 4 V and got ALL EXACT MATCH on ctrl_fid, treat_fid, route_acc, "
        "comm_size, n_comm, and BOTH prediction SHA256 hashes (deterministic, not stale/fabricated). "
        "MECHANISM: BARRIER #3 = the additive-store crosstalk wall M < N/(2 ln V) makes a flat/dense store "
        "collapse as total store V grows. CONTROL (dense-additive, must-collapse guard): one GLOBAL bound "
        "bundle over all V pairs; unbind a key, clean up value against the WHOLE V codebook (additive load "
        "V, argmax over V). TREATMENT (index + community, two-stage): per-community bound bundles; stage-1 "
        "coarse route = argmax over the ~sqrt(V) near-orthogonal community-gist codebook; stage-2 fine "
        "decode = unbind + peel_sic_readout(n_items=1) within the selected community's ~sqrt(V) items only. "
        "Effective crosstalk-relevant codebook = active-community size (~sqrt(V)), decoupled from total-V. "
        "FIVE ADVERSARIAL PROBES (all off per_seed[], not verdict_msg): "
        "(P1) DISCRIMINATOR FIRES AT SCALE, PER-SEED: CONTROL ctrl_fid = 0.0 at V=29000 AND V=58000 for ALL "
        "3 seeds (aggregate 0.789->0.023->0.0->0.0, rel_deg 1.000). The contrast is NON-vacuous at the top "
        "scales, not just at V_min. "
        "(P2) THE KEY CAVEAT (the reason this is MM not CG): TREATMENT flat (fid 1.000, cv 0.000) is GENUINE "
        "total-V decoupling but is NOT stressed to its own ceiling. Independent stress re-run of the "
        "treatment fine-decode in isolation at inflated community sizes (N=8192): comm 64->1.000, 241->"
        "0.992, 630->0.680, 1000->0.313, 2000->0.094. The ACTUAL top-scale community size is 241 "
        "(=round(sqrt(58000))), well BELOW the within-community Plate cliff ~630 (N/(2 ln comm)). Treatment "
        "is flat across the tested range ONLY because effective load (comm 24->241, ~10x) stays deep inside "
        "its own capacity envelope. Honest claim: community-routing decouples crosstalk from TOTAL-V (total "
        "size no longer crowds), NOT unlimited capacity. route_acc=1.000 at n_comm=241 all seeds IS the "
        "load-bearing scale-invariance evidence (routing codebook grows as sqrt(V) and does NOT degrade "
        "within range) -- but n_comm=241 is likewise under the routing codebook's own cliff, so routing is "
        "also unstressed. "
        "(P3) MODULARITY GUARD: min Newman Q = 0.510 at V=58000 (0.951/0.981/0.708/0.510 across V), all >> "
        "0.30 and non-degenerate; reproduced per-seed. Treatment-flat is measured on REAL community "
        "structure, not a trivially-separable toy. "
        "(P4) TELEMETRY + CORRECT COMPOSITION: perturbing the seed MOVES control fid (V=2900: canonical "
        "0.023 vs seed999 0.039, seed1234 0.047) -> nothing analytically pinned; the collapse reads the "
        "data. treat stays 1.000 (saturated within capacity). peel_sic_readout(n_items=1) used CORRECTLY as "
        "the within-community/whole-V DECODE (confidence-ordered argmax), NOT as a retrieval-agreement fix "
        "-- the treatment advantage is entirely from the SMALLER (community) codebook, consistent with the "
        "prior finding that peel/SIC does not help single-cue NN. Store decoupled from routing gist: "
        "|cos|~0.009 (near-orthogonal), matching the correlation-hurts-store design. "
        "(P5) HONEST SCOPE: certifies TOTAL-V scale-invariance of community-bounded two-stage retrieval "
        "(effective-V = active-community size, decoupled from total store size); does NOT certify within-"
        "community capacity (separate axis; community-of-communities 2nd tier + higher per-community load is "
        "the named v2). Synthetic community-structured KB (random bipolar codes), NOT real ingested "
        "topology. CROSS-ARC OVERLAP: substrate_query top cosine 0.2588 (all NOTES; NONE a landed cell at "
        ">0.30) -- genuinely novel two-stage coarse-route + fine-decode cell. TIER = MEASURED_MECHANISM: "
        "the decoupling mechanism is real, correctly implemented, reproduces bit-exact, discriminator fires "
        "non-vacuously per-seed, telemetry-sensitive, modularity real -- BUT the treatment arm is never "
        "stressed to its own ceiling (community size 241 << measured cliff ~630), so the certified claim is "
        "the PROVEN BOUNDARY 'crosstalk decoupled from TOTAL-V', not a full capacity proof. Symmetric "
        "anti-negativity: not deflated to MB/HF (mechanism clean); not inflated to CG (treatment "
        "unstressed). Composes the FHRR bundle-capacity CG (the Plate/order-statistic boundary that bounds "
        "both the CONTROL collapse at total-V and the treatment within-community cliff). commit cc804bfc1 "
        "2026-07-08."
    ),
    "provenance": {
        "cell": "experiments/exp_community_bounded_retrieval_scale_invariance_v1.py",
        "commit": CELL_COMMIT,
        "metrics_path": "data/exp_community_bounded_retrieval_scale_invariance_v1/metrics.json",
        "prereg": "preregs/2026-07-08_community_bounded_retrieval_scale_invariance_v1.md",
        "seeds": [7, 17, 23],
        "run_mode": "full",
        "whole_cell_verdict": "HARD_PASS",
        "audit_tier": "MEASURED_MECHANISM",
        "ts_iso": TS_ISO,
        "atomized_by": ATOMIZED_BY,
        "verified_off_data": True,
        "verified_off_data_note": (
            "Independent .venv recompute re-ran run_one_V for all 3 seeds x 4 V: ALL EXACT MATCH on ctrl_fid, "
            "treat_fid, route_acc, comm_size, n_comm and BOTH pred SHA256 hashes. ctrl_fid per-seed at "
            "V=29000 [0,0,0] and V=58000 [0,0,0]; treat_fid [1,1,1] and route_acc [1,1,1] at every V; "
            "modularity_Q reproduced (Q_min 0.510 at V=58000). Telemetry: seed999/seed1234 at V=2900 give "
            "ctrl 0.039/0.047 vs canonical 0.023 (moves). Treatment stress re-run (fine-decode isolation, "
            "N=8192): comm 64->1.000, 241->0.992, 630->0.680, 1000->0.313, 2000->0.094 -> within-community "
            "Plate cliff ~630; the tested top community size is 241 (unstressed). decouple |cos|~0.009."
        ),
    },
    "verified_numbers": {
        "N": 8192, "V_grid": [580, 2900, 29000, 58000], "n_seeds": 3, "seeds": [7, 17, 23],
        "ctrl_fid_curve": {"580": 0.7890625, "2900": 0.0234375, "29000": 0.0, "58000": 0.0},
        "ctrl_fid_perseed_V29000": [0.0, 0.0, 0.0], "ctrl_fid_perseed_V58000": [0.0, 0.0, 0.0],
        "ctrl_rel_deg": 1.0, "control_collapse_rd_floor": 0.30,
        "treat_fid_curve": {"580": 1.0, "2900": 1.0, "29000": 1.0, "58000": 1.0},
        "treat_rel_deg": 0.0, "treat_flat_rd_ceiling": 0.10, "treat_cv_across_seeds": 0.0,
        "route_acc_curve": {"580": 1.0, "2900": 1.0, "29000": 1.0, "58000": 1.0},
        "route_acc_Vmax": 1.0, "route_acc_floor": 0.90,
        "n_comm_curve": {"580": 25, "2900": 54, "29000": 171, "58000": 241},
        "comm_size_curve": {"580": 24, "2900": 54, "29000": 170, "58000": 241},
        "modularity_Q_curve": {"580": 0.9509, "2900": 0.9810, "29000": 0.7081, "58000": 0.5097},
        "modularity_Q_min": 0.5097400443597488, "modularity_floor": 0.30,
        "decouple_abs_cos_approx": 0.009,
        "telemetry_ctrl_V2900_canonical": 0.0234375, "telemetry_ctrl_V2900_seed999": 0.0390625,
        "telemetry_ctrl_V2900_seed1234": 0.046875,
        "treatment_stress_fine_decode_N8192": {"64": 1.0, "241": 0.9922, "630": 0.6797, "1000": 0.3125, "2000": 0.0938},
        "within_community_plate_cliff_approx": 630, "top_scale_community_size": 241,
        "cardinality_units": 24, "cardinality_expected": 24, "cardinality_ok": True,
        "all_recompute_exact_match": True,
    },
    "can_fail_discriminator_verdict": (
        "FIRES and is TELEMETRY-SENSITIVE. (1) The dense-additive CONTROL was the saturation-vacuous guard: "
        "it GENUINELY collapses to 0.000 per-seed at both V=29000 and V=58000 (rel_deg 1.000 >= 0.30 floor) "
        "-> the crosstalk regime is exercised at the top scales, the HARD_FAIL_DISCRIMINATOR_INERT branch "
        "was reachable and did NOT fire. (2) Seed perturbation moves control fid (0.023 -> 0.039/0.047 at "
        "V=2900) -> not analytically pinned. (3) The modularity guard (Q<0.30 -> HARD_FAIL_GENERATOR_NO_"
        "STRUCTURE) was reachable; min Q=0.510 clears it (real structure). (4) TREATMENT could have degraded "
        "with total-V if the routing leaked (route_acc<0.90) or the community bundles crosstalked with total-"
        "V; neither happened (route 1.000, treat 1.000). BOUNDARY-AWARE: the treatment-flat is NOT a pinned "
        "1.000 either -- the independent stress re-run shows the SAME fine-decode collapses (0.680/0.313/"
        "0.094) once community size exceeds ~630, so treatment CAN fail; it simply is not pushed there in the "
        "tested range. That is precisely why this is a PROVEN BOUNDARY (MM), not an unlimited-capacity CG."
    ),
    "framing_corrections_vs_cell_author_and_director": [
        "HARD_PASS (cell verdict) is CORRECT for its pre-registered joint gate (treat flat AND control "
        "collapse AND route>=0.90 AND Q>=0.30 AND card_ok) and all 5 structured gate claims reproduce off "
        "disk. But the AUDIT tier is MEASURED_MECHANISM, not chain-grade, because the pre-reg gate certifies "
        "the CONTRAST, not the treatment's own capacity. Symmetric anti-negativity: the mechanism is genuine "
        "and cleanly reproduced -- do NOT deflate it to MB/HF; equally do NOT inflate 'scale-invariance' to "
        "'unlimited capacity'.",
        "THE HEADLINE MUST BE SCOPED TO TOTAL-V (load-bearing, bake into any downstream framing): community-"
        "routing decouples crosstalk from the TOTAL store size (total-V no longer crowds the decode). It "
        "does NOT remove the within-community capacity limit. Independently MEASURED: the same fine-decode "
        "collapses (comm 630->0.680, 1000->0.313, 2000->0.094) once a community exceeds ~630 items at "
        "N=8192; the tested top community is only 241, so treatment's own ceiling is NEVER approached.",
        "route_acc=1.000 is the RIGHT load-bearing evidence for the total-V claim (the routing codebook "
        "grows as sqrt(V) to n_comm=241 and stays perfect), but note it is ALSO unstressed (241 near-"
        "orthogonal gists in N=8192 is trivially separable). The v2 that stresses BOTH tiers (community-of-"
        "communities routing at larger n_comm + higher per-community load) is what would promote this toward "
        "a fuller capacity claim.",
        "peel_sic_readout(n_items=1) is used correctly as the DECODE primitive (confidence-ordered argmax), "
        "NOT as a retrieval-agreement fix; it is not load-bearing for the win (the win is the smaller "
        "codebook). This is consistent with -- not contradicted by -- the prior finding that peel/SIC does "
        "not help single-cue NN retrieval.",
        "SYNTHETIC KB caveat (consistent with SUBSTRATE-KNOWS-NOTHING): the community structure is generated "
        "(near-orthogonal random store codes + a separate structured gist space), not real ingested graph "
        "topology. Certifies the two-stage retrieval MECHANISM over synthetic community structure; real-"
        "topology ingestion is a separate axis.",
    ],
    "revival_or_extension_criterion": (
        "MM scope: certifies TOTAL-V scale-invariance (effective-V = active-community size, decoupled from "
        "total store size) of community-bounded two-stage retrieval at N=8192, V up to 58000, community size "
        "up to 241 (well within the ~630 within-community cliff), synthetic community-structured KB, 3 seeds. "
        "PROMOTE-toward-CG / EXTENSIONS (each a NEW cell, composes NOT supersedes): (1) STRESS THE TREATMENT'S "
        "OWN AXIS -- push per-community load toward/over the within-community Plate cliff (~630 at N=8192) and "
        "add a community-of-communities 2nd routing tier (n_comm large); does the two-stage structure keep "
        "effective-V bounded when BOTH tiers are stressed (the named v2). (2) REAL INGESTED TOPOLOGY -- run "
        "on real graph communities (not synthetic near-orthogonal), where store codes may carry semantic "
        "correlation (correlation-hurts-store predicts store pressure). (3) NOISY / MULTI-ITEM readout -- "
        "n_items>1 answer sets and noisy cues at the fine-decode stage. (4) ROUTING UNDER STRESS -- push "
        "n_comm toward the routing codebook's own cliff to find where coarse-route starts leaking. DEMOTION "
        "trigger: if a re-run shows CONTROL fails to collapse (rd<0.30, discriminator inert), OR route_acc "
        "drops below 0.90 with V, OR modularity Q<0.30 (generator void), OR treatment degrades with total-V "
        "at fixed community size."
    ),
    "composes": [P_CAPACITY],
    "compose_note": (
        "Composes the FHRR bundle-capacity CG (the parameter-free order-statistic / Plate N/(2 ln V) "
        "capacity law). That law is the SHARED boundary that governs BOTH arms here: it makes the CONTROL "
        "collapse (decode load = total-V > cliff) AND it is exactly the within-community cliff (~630 at "
        "N=8192) that the TREATMENT stays below (community size 241). The novel contribution of THIS atom is "
        "the DECOUPLING claim: a two-stage coarse-community-route + community-scoped fine-decode converts the "
        "crosstalk-relevant codebook from total-V to active-community size (~sqrt(V)), so the capacity law is "
        "evaluated at community size, not total store size. Design also depends on the certified correlation-"
        "hurts-store law (store codes near-orthogonal random, decoupled from the separate routing gist space; "
        "measured |cos|~0.009). Brain-grounding: hippocampal indexing (store pointers, near-orthogonal, "
        "decoupled from content) + community/small-world routing (route to community first, then resolve "
        "within it)."
    ),
    "cross_arc_overlap_check": (
        "substrate_query 'community-bounded two-stage retrieval hippocampal index routing scale invariance "
        "crosstalk total store size decouple effective V' -> top cosine 0.2588 (all NOTES: '(D) Adaptive "
        "retrieval with complexity routing' 0.2588, 'Path 5 Hippocampal schema retrieval' 0.2529, "
        "hippocampal_index.py design note 0.249), NONE a landed cell at cosine>0.30. Consistent with the "
        "prereg's own check (top hit hippocampal_index.py 0.2705, below 0.30). No prior arc cell builds a "
        "two-stage coarse-community-select then fine-decode retrieval. GENUINELY NOVEL (the July-1 INT8-"
        "rediscovery pattern does NOT apply)."
    ),
    "anchor": "community_bounded_retrieval_scale_invariance_v1",
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
        "community-bounded two-stage retrieval decouples crosstalk from TOTAL store size (BARRIER #3); MEASURED_MECHANISM proven boundary",
        "dense-additive control collapses per-seed to 0.0 at V=29000 and V=58000 (rel_deg 1.0) while community-route treatment stays flat fid 1.0 over 100x V sweep",
        "route_acc=1.0 at n_comm=241 all seeds is the load-bearing scale-invariance evidence; min Newman Q=0.510 (real community structure)",
        "BOUNDARY: treatment flat because community size 241 << measured within-community Plate cliff ~630 (comm 630->0.680, 1000->0.313, 2000->0.094); total-V invariance within capacity envelope NOT unlimited",
        "SCOPE: synthetic community-structured KB not real topology; certifies total-V decoupling not within-community capacity; v2 = community-of-communities 2nd tier + higher load",
        "community_bounded_retrieval_scale_invariance_v1 landed-VET MEASURED_MECHANISM",
    ],
    "added_atom_id": None,
}
atom["added_atom_id"] = atom["id"]

ledger = {
    "ts": TS, "ts_iso": TS_ISO, "op": "add", "atom_id": atom["id"], "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "disposition": "measured_mechanism_proven_boundary_community_bounded_two_stage_retrieval_decouples_crosstalk_from_total_store_size",
    "cert_status": atom["cert_status"],
    "cert_class": atom["cert_class"],
    "cert_increment_delta": {"CG": 0, "MM": 1, "HF": 0},
    "cert_delta": {"CG": 0, "MM": 1, "HF": 0},
    "cert_delta_note": (
        "MM +1 (proven boundary): community-bounded two-stage retrieval (hippocampal-index + community-route "
        "coarse stage-1 over ~sqrt(V) gist codebook, then unbind + peel/SIC fine-decode WITHIN the selected "
        "community) DECOUPLES crosstalk from TOTAL store size. Over a 100x V sweep (580->58000, N=8192, 3 "
        "seeds 7/17/23) the dense-additive GLOBAL-bundle CONTROL collapses (fid 0.789->0.000, rel_deg 1.000, "
        "PER-SEED ZERO at both V=29000 and V=58000 -> discriminator fires at scale, non-vacuous) while the "
        "TREATMENT stays flat (fid 1.000, rel_deg 0.000, cv 0.000). route_acc=1.000 at n_comm=241 all seeds "
        "(load-bearing scale-invariance evidence); min Newman Q=0.510 (real structure). Verified off-disk by "
        "independent .venv recompute -- re-ran run_one_V all 3 seeds x 4 V, ALL EXACT MATCH incl both pred "
        "hashes; telemetry-sensitive (seed perturb moves control fid 0.023->0.039/0.047). WHY MM NOT CG: "
        "treatment is NEVER stressed to its own ceiling -- community size 241 sits well below the within-"
        "community Plate cliff ~630 (independently MEASURED: comm 630->0.680, 1000->0.313, 2000->0.094). So "
        "flat = TOTAL-V invariance WITHIN the community-capacity envelope, NOT unlimited capacity. SCOPE: "
        "synthetic community-structured KB (not real ingested topology); certifies total-V decoupling, does "
        "NOT certify within-community capacity (v2: community-of-communities 2nd tier + higher per-community "
        "load). Cross-arc overlap: top cosine 0.2588 (NOTES only, none a landed cell >0.30) -- genuinely "
        "novel. Symmetric anti-negativity: not deflated (mechanism clean, reproduces bit-exact), not inflated "
        "(scale-invariance is total-V-scoped). Composes FHRR bundle-capacity CG. Needs orchestrator Store-"
        "sync (skunkworks atoms do not auto-persist)."
    ),
    "verified_off_data": True,
    "verification": "reran_run_one_V_all_3seed_x_4V_exact_match_incl_pred_hashes + treatment_stress_isolation_finds_within_community_cliff_630 + seed_perturb_telemetry + modularity_reproduced",
    "anchor": "community_bounded_retrieval_scale_invariance_v1",
    "cell_commit": CELL_COMMIT,
    "auditor": "hdi_skunkworks", "atomized_by": "hdi_skunkworks",
    "landed_VET_session": SESSION,
    "composes": [P_CAPACITY],
    "needs_orchestrator_store_sync": True,
    "raw_metrics_paths": ["data/exp_community_bounded_retrieval_scale_invariance_v1/metrics.json"],
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
    append_jsonl_a5(MATH_ATOMS, atom, "math/atoms (community-bounded retrieval TOTAL-V decoupling MEASURED_MECHANISM)")
    append_jsonl_a5(CERT_LEDGER, ledger, "cert_ledger (MM +1)")
    print(f"[A5] DONE OK -> community-bounded two-stage retrieval TOTAL-V decoupling MEASURED_MECHANISM (MM +1)")


if __name__ == "__main__":
    main()
