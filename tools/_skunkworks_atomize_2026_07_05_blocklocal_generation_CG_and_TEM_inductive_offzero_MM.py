"""
A5-gated atomization -- Skunkworks landed-VET 2026-07-05.
Two FULLs: (1) generation native-GSBC block-local decoder HARD_PASS -> CHAIN_GRADE;
(2) TEM structural/content-binding inductive transfer MIDDLE_BAND -> MM_STANDARD (canonical
confirm of off-zero). AUDIT-ONLY. Both independently recomputed off the landed metrics.json
via .venv (recompute.py): per-seed cliff mean, full envelope, capacity-law fit, and
real_minus_shuf recomputed from raw cells_aggregate means (NOT the pre-computed cell_diag) --
Fix#28 discipline. Reproduced disk EXACTLY.

BATCH CONTENTS (2 atoms, matching TS_ISO):
  (1) math CHAIN_GRADE -- generation_decoder_gsbc_native_blocklocal_v1 HARD_PASS. Native GSBC
      fillers round-trip PERFECTLY (exact_ordered=1.000, cv=0) via block-local sparse resonator
      across V<=8192@D<=6 and V<=1024@D<=12 (0.9889 @V1024D26), 3 seeds. Encoding-mismatch PROVEN
      (dense bipolar-BSC full-resonator=0.000 on same GSBC fillers vs 1.000 iid-synth). Non-vacuous
      (noorder->0, dense-gsbc->0, dense-synth->1.0). PLUS a MEASURED capacity boundary at V8192D26
      (exact=0.856 3-seed mean) reconciled with the sparse-Hebbian law V_max~0.7n/(a ln(1/a)):
      cliff at V/Vmax=2.9x, holds where <1x. CG +1. Cliff number RESOLVED: 0.856 = canonical FULL
      3-seed mean; 0.700 was the seed-7 single-seed probe (FULL reproduces seed7=0.7 exactly).
  (2) math MM_STANDARD -- schema_relation_TEM_structural_content_binding_v1 MIDDLE_BAND. First
      NON-VACUOUS canonical evidence of inductive relational transfer to NOVEL entities: the
      content-conditioned SCORER (bilinear/RESCAL) real_minus_shuf(inductive)=+0.049..+0.16 on
      semantic relations, where GLOBAL (averaged/TransE-marginal) = ~0 (-0.004..+0.009, confirming
      the prior arc's shuffle-invariant ZERO). SHUFFLED collapses to floor; synth discriminators
      FIRE and DIFFERENTIATE (type_hard 0.66/0.775, content_map 0.035/0.207 -- NOT saturated,
      repairs the prior estimator-ablation's vacuous discriminator). DerivedFrom positive control
      SCORER=+0.624 (HARD_PASS) proves the discriminator reaches HP magnitude when signal exists ->
      semantic MIDDLE_BAND is SUBSTANTIVE, not test-design failure. Modest magnitude (<0.2075 HP)
      = under-parameterization + CapableOf data-starvation + one-to-many entropy ceiling, NOT a
      mechanism wall. SCORER >= TEM on net real_minus_shuf. MM +1.

NET CERT DELTA (this batch): CG +1, MM +1, HF 0.
No DEMOTE. Prior generation_decoder_roundtrip_v1 (MM_STANDARD, 1fd6f580a) NOT superseded --
this EXTENDS it (block-local native architecture + envelope + capacity law); it remains valid as
the dense-anchor + dense-0.000-on-correlated-fillers observation.
"""
import json
import os
import time
import tempfile

MATH_ATOMS = "d:/AI/hd-instrument/data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = "d:/AI/hd-instrument/data/substrate_index/meta/cert_ledger.jsonl"

TS = time.time()
TS_ISO = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(TS))
SESSION_TAG = "2026-07-05_blocklocal_generation_CG_and_TEM_inductive_offzero_MM"

PRIOR_GEN_ID = "generation_decoder_roundtrip_v1"  # 1fd6f580a, MM_STANDARD (dense anchor)
PRIOR_HF_ESTIMATOR_ABLATION = "math::HARD_FAIL_SCOPED_schema_relation_transform_estimator_ablation_real_conceptnet_holistic_map_naive_AND_trained_rotation_extracts_NO_subject_conditional_INDUCTIVE_transfer_under_EITHER_surface_char_trigram_OR_semantic_BGE_encoding_every_ABOVE_FLOOR_score_is_SHUFFLE_INVARIANT_relation_prior_not_per_instance_mapping_bge_raises_raw_acc_AtLoc_0p047_to_0p158_and_CausesDesire_0p082_to_0p191_BUT_real_minus_shuf_0p000_so_the_semantic_gain_is_PRIOR_semantic_neighborhood_NOT_transfer_real_minus_meanobj_plus0p14_means_subject_dependent_yet_shuffle_matches_so_dependence_is_encoding_geometry_not_learned_correspondence_CLOSES_scope_guard_of_parent_b8a8d107d_semantic_BGE_NOW_in_ARM_REAL_and_STILL_FAILS_weakens_encoder_bottleneck_rescue_for_the_holistic_map_estimator_OVER_REACH_A_trained_vs_naive_max_delta_0p0044_is_INCONCLUSIVE_synth_hard_SATURATED_1p0_1p0_trained_adv_0p000_discriminator_NOT_firing_estimator_axis_VACUOUS_so_direction_drill_NOT_refuted_OVER_REACH_B_transductive_inductive_gap_NOT_supported_gaps_mostly_NEGATIVE_minus0p01_to_minus0p10_ind_higher_than_trans_neither_mode_transfers_SCOPING_C_DerivedFrom_high_0p86_to_0p92_shuffle_invariant_in_BOTH_encodings_relation_prior_not_uniquely_char_trigram_cell_verdict_MIDDLE_BAND_correct_harness_SOUND_synth_clean_1p0_randenc_0p01_arms_differ_bind_rt_1p0_432of432_3seed_FULL_N8192_V100_2026-07-05"

# ---------------------------------------------------------------------------
# ATOM 1 -- GENERATION native-GSBC block-local (math, CHAIN_GRADE)
# ---------------------------------------------------------------------------
atom_gen = {
    "id": "math::CHAIN_GRADE_generation_decoder_native_GSBC_block_local_sparse_resonator_round_trips_REAL_native_GSBC_EXPAND2X_fillers_PERFECTLY_exact_ordered_1p000_cv0_across_full_envelope_V256_to_8192_at_D3_D6_and_V1024_at_D12_and_0p9889_at_V1024D26_3seed_ENCODING_MISMATCH_PROVEN_dense_bipolar_BSC_full_resonator_0p000_on_SAME_GSBC_fillers_vs_1p000_on_iid_synth_NON_VACUOUS_noorder_ctrl_0p000_and_dense_gsbc_fullreso_0p000_collapse_dense_synth_1p000_ceiling_PLUS_MEASURED_capacity_boundary_at_V8192D26_exact_0p856_3seed_mean_reconciled_with_sparse_Hebbian_law_Vmax_0p7n_over_a_ln_inv_a_cliff_at_V_over_Vmax_2p9x_holds_below_1x_block_local_is_brain_grounded_Sparse_Block_Codes_not_a_partition_cheat_positions_known_by_construction_for_generation_decode_3seed_FULL_N8192_K192_2026-07-05",
    "name": "MATH CHAIN_GRADE: native-GSBC generation decoder -- the block-local sparse resonator round-trips REAL native GSBC_EXPAND2X fillers PERFECTLY (exact_ordered=1.000, cv=0, 3 seeds) across the envelope V<=8192@D<=6 and V<=1024@D<=12 (0.9889 @V1024D26). Encoding-mismatch PROVEN: dense bipolar-BSC full-resonator=0.000 on the SAME GSBC fillers vs 1.000 on iid-synth. Non-vacuous (noorder->0, dense-gsbc-fullreso->0; dense-synth 1.0 ceiling). PLUS a MEASURED capacity boundary at V8192D26 (exact=0.856 3-seed mean) that reconciles with the sparse-Hebbian law V_max~0.7n/(a ln(1/a)): cliff appears at V/Vmax~2.9x, holds where <1x. Block-local = brain-grounded Sparse Block Codes (positions known by construction for a generation decode), not a partition cheat.",
    "corpus": "math",
    "tier": "CHAIN_GRADE",
    "kind": "experiment_landed_vet",
    "cert_status": "chain_grade_capability_plus_measured_capacity_boundary",
    "cert_class": "native_GSBC_ordered_generation_roundtrip_via_block_local_sparse_resonator_perfect_in_envelope_encoding_mismatch_proven_capacity_cliff_characterized_sparse_hebbian_law",
    "description": (
        "LANDED-VET of exp_generation_decoder_gsbc_native_blocklocal_v1 (verdict HARD_PASS, run_mode=full, "
        "N=8192, GSBC_DIM=8192, K_ACTIVE=192, F_SPARSE=0.02, 9-point V×D grid, 3 seeds [7,13,19], 90 units, "
        "cardinality_ok=True, arms_differ_verified=True; commit ec7aa9064). "
        "AUDITOR INDEPENDENT RECOMPUTE (.venv, off the landed metrics.json -- per-seed arrays, envelope, "
        "capacity-law fit; did NOT rely on verdict_msg): all headline numbers reproduce EXACTLY. "
        "CORE CAPABILITY: blocklocal_gsbc exact_ordered=1.0000 (cv=0, all seeds 1.000) at every grid point "
        "through V8192D6 and V1024D12; 0.9889 at V1024D26 (per_term/per_token 0.9996); per_term/per_token "
        "1.000 elsewhere. This is a genuine ordered round-trip of REAL native GSBC_EXPAND2X fillers "
        "(concept-encoder v12 gwta seed7, sparse bipolar, 10000-concept bounded pool) from a block-"
        "superposition bundle, decoded by a disjoint-block-index sparse resonator (16 restarts, 40 iters). "
        "ENCODING-MISMATCH DISCRIMINATOR (proves it is the ARCHITECTURE not the data): dense bipolar-BSC "
        "positions-unknown full resonator COLLAPSES to exact=0.000 on the SAME GSBC fillers, while the SAME "
        "dense resonator scores 1.000 on iid synthetic fillers (dense_synth_fullreso) and dense_gsbc_"
        "rolesknown scores 1.000 (roles known) -- so dense multiply-bind is the mismatch, block-local is the "
        "GSBC-native factorizer. "
        "NON-VACUITY (the 1.000 saturation is NOT by-construction-vacuous -- genuine failure modes exist on "
        "the SAME fillers/metric): (a) noorder_ctrl exact_ordered=0.000 across all cells/seeds (order info is "
        "actually used and recovered; per_term degrades from 0.111@D3 to ~0.0004@D26); (b) dense_gsbc_"
        "fullreso=0.000; (c) the SAME block-local construction DEGRADES at the cliff (V8192D26=0.856) and the "
        "capacity law predicts where 1.000 stops. "
        "MEASURED CAPACITY BOUNDARY (proven sub-boundary within the CG): at V8192D26 exact_ordered=0.8556 "
        "(3-seed mean of per-seed [0.700, 0.9667, 0.900]); still >= the HP_exact_ordered band 0.85, but this "
        "is the noisy cliff edge (cross-seed sample_cv~0.162, expected for a boundary cell; the CG claim "
        "rests on the in-envelope cells where cv=0). This RECONCILES quantitatively with the mechanism-"
        "research sparse-Hebbian capacity law V_max ~ 0.7*n/(a*ln(1/a)) with n=N/D (block size), a=F_SPARSE: "
        "V_max(n=315)~2819 -> V=8192 is 2.91x over critical load -> degrades but does not collapse (0.856); "
        "V1024D26 is 0.36x -> holds (0.9889); V8192D6 (n=1365, V_max~12215) is 0.67x -> holds (1.000). The "
        "law fits all three boundary points. "
        "MECHANISM SOUNDNESS (per USER mechanism+envelope directive): block-local sparse resonator is a "
        "literature-recognized, brain-grounded mechanism (Sparse Block Codes / Resonator Networks family, "
        "Frady-Kleyko-Sommer 2021, Hersche 2025; grid-cell modular precedent), NOT a partitioning cheat -- "
        "for a GENERATION decode the sequence positions ARE known by construction (decode slot 1..D in "
        "order), and the noorder control confirms order is genuinely recovered not assumed. The cliff is a "
        "block-size-vs-vocabulary capacity wall with a computable, TUNABLE form; the next lever (RNS/CRT "
        "modular sub-blocks, Kymn-Kleyko-Frady-Sommer 2024, grid-cell-grounded Fiete 2008) is sound and "
        "directly targets the V-per-block ceiling without growing N. "
        "TIER RATIONALE: CHAIN_GRADE -- a new, non-trivially-composable primitive (native-GSBC ordered "
        "generation round-trip) with high-quality evidence (3 seeds, cv=0 in-envelope, 9 grid points, 4 "
        "control arms all behaving correctly, capacity law fitting 3 boundary points), non-vacuous "
        "saturation with proven encoding-mismatch and order discriminators, plus a MEASURED capacity boundary "
        "at the cliff. EXTENDS (does NOT supersede) prior generation_decoder_roundtrip_v1 (MM_STANDARD, "
        "1fd6f580a) which established the dense anchor + dense-0.000-on-correlated-fillers observation; this "
        "adds the block-local native architecture as the FIX, the full V×D envelope, and the capacity law."
    ),
    "aliases": ["blocklocal_sparse_resonator_native_gsbc_generation_roundtrip_CG",
                "gsbc_native_mouth_block_local_ordered_decode_envelope_and_cliff"],
    "metadata": {
        "record_class": "experiment_landed_vet_chain_grade_capability_plus_measured_boundary",
        "term_class": "GENERATION_DECODER_NATIVE_GSBC_BLOCK_LOCAL_SPARSE_RESONATOR_ORDERED_ROUNDTRIP_ENVELOPE_AND_CAPACITY_CLIFF",
        "cert_status": "chain_grade_capability_plus_measured_capacity_boundary",
        "cert_class": "native_GSBC_ordered_generation_roundtrip_block_local_perfect_in_envelope_encoding_mismatch_proven_capacity_cliff_sparse_hebbian_law",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "verified_via": "independent .venv recompute off landed metrics.json (per-seed cliff mean, full envelope, control arms, capacity-law fit); not verdict_msg",
        "atomized_by": "skunkworks_landed_VET_2026-07-05_blocklocal_generation",
        "anchor": "generation_decoder_gsbc_native_blocklocal_v1",
        "cell_commit": "ec7aa9064",
        "raw_metrics_path": "data/exp_generation_decoder_gsbc_native_blocklocal_v1/metrics.json",
        "run_mode": "full", "N": 8192, "GSBC_DIM": 8192, "K_ACTIVE": 192, "F_SPARSE": 0.02,
        "n_seeds": 3, "seeds": [7, 13, 19], "n_units": 90, "cardinality_ok": True,
        "recompute_off_disk": {
            "envelope_blocklocal_gsbc_exact_ordered": {
                "V256D3": 1.0, "V1024D3": 1.0, "V256D6": 1.0, "V1024D6": 1.0,
                "V4096D6": 1.0, "V8192D6": 1.0, "V1024D12": 1.0,
                "V1024D26": 0.9889, "V8192D26": 0.8556},
            "cliff_V8192D26_exact_per_seed": [0.700, 0.9667, 0.900],
            "cliff_V8192D26_mean": 0.8556, "cliff_sample_cv": 0.162,
            "cliff_per_term_mean": 0.9945, "cliff_per_token_mean": 0.9945,
            "controls": {"noorder_ctrl_exact": 0.000, "dense_gsbc_fullreso_exact": 0.000,
                         "dense_synth_fullreso_exact": 1.000, "dense_gsbc_rolesknown_exact": 1.000},
            "capacity_law_Vmax_0p7n_over_a_ln_inv_a": {
                "V8192D26": {"n": 315, "Vmax": 2819, "V_over_Vmax": 2.91, "exact": 0.8556},
                "V1024D26": {"n": 315, "Vmax": 2819, "V_over_Vmax": 0.36, "exact": 0.9889},
                "V8192D6": {"n": 1365, "Vmax": 12215, "V_over_Vmax": 0.67, "exact": 1.000}},
            "match_disk": "EXACT",
        },
        "cliff_number_resolution": "The prereg/probe cited exact=0.700 at V8192D26; the FULL 3-seed mean is 0.856. NO discrepancy -- 0.700 is the seed-7 SINGLE-seed probe value (the FULL reproduces seed7=0.700 EXACTLY as its low seed; seeds 13/19 are 0.9667/0.900). CANONICAL FULL cliff number = 0.856 (3-seed mean). The mechanism-research note's DISK-VERIFY flag was correct to treat 0.700 as the only disk-grounded number BEFORE the FULL landed; the FULL now supersedes it with 0.856.",
        "non_vacuity_checks": {
            "noorder_control": "exact_ordered=0.000 all cells/seeds; per_term degrades 0.111@D3 -> ~0.0004@D26 (order genuinely recovered, not assumed)",
            "dense_gsbc_mismatch": "dense bipolar-BSC full-resonator=0.000 on same GSBC fillers (encoding mismatch)",
            "dense_synth_ceiling": "same dense resonator=1.000 on iid synth (proves mechanism-vs-data, not a broken dense arm)",
            "cliff_degradation": "same block-local construction degrades to 0.856 at V8192D26 -> 1.000 is within-capacity success, not by-construction-vacuous",
        },
        "by_construction_verdict": "NON-VACUOUS. Positions are known by construction (legitimate for a generation DECODE of ordered slots), but recovery of the ordered fillers is a real task the mechanism solves in-envelope and fails out-of-envelope (cliff) and that dense multiply-bind fails on the same data. The capacity law bounds exactly where 1.000 holds.",
        "cross_arc_overlap_check_2026_07_01_USER_locked": "substrate_query 'block-local sparse resonator generation decoder native GSBC round-trip ordered sequence capacity cliff' -> top hits @cosine 0.28-0.29 are PRIOR resonator NEGATIVES (N6 resonator-dense V=100 GENUINE negative; N7 SQ1-resonator-generative GENUINE negative) + SQ1-generative goal note chunks. Those are the DENSE-resonator generative negatives; the block-local NATIVE-GSBC architecture is the mechanism that turns that negative into a positive. Below the 0.30 rail; NOT a rediscovery -- it is the FIX for the prior dense-resonator generative negatives and a targeted extension of generation_decoder_roundtrip_v1.",
        "composes_with_atoms": [PRIOR_GEN_ID],
        "composition_note": "EXTENDS prior generation_decoder_roundtrip_v1 (MM_STANDARD, commit 1fd6f580a), which established the dense anchor at V1024D3 + the dense-factorization=0.000-on-correlated-fillers observation. This cell adds: (a) the block-local sparse resonator as the GSBC-native FIX, (b) the full V×D envelope with cv=0 in-box, (c) the MEASURED capacity cliff + sparse-Hebbian law reconciliation. Prior atom NOT superseded; it remains the dense-anchor record.",
        "framing_corrections_vs_director_and_cell": "(1) CLIFF NUMBER RESOLVED (Director's central question): 0.86 vs 0.70 is NOT a discrepancy -- 0.856 is the CANONICAL FULL 3-seed mean; 0.700 was the seed-7 single-seed probe, reproduced EXACTLY as the FULL's low seed. Canonical = 0.856. (2) Minor precision on the claim 'exact-ordered=1.000 ... holding to D=26/V<=1024': at V1024D26 it is 0.9889 (near-perfect), not literally 1.000 -- the verdict_msg itself correctly says 0.99; the task-summary rounded up. True perfect-1.000 envelope = V<=8192@D<=6 and V1024@D<=12. (3) V8192D26=0.856 still clears the HP_exact_ordered band (0.85) but only barely and with wide cross-seed spread (0.70-0.967) -- it is a cliff-EDGE, correctly framed as a measured boundary not a clean pass. All symmetric: no inflation, the core HARD_PASS is fully affirmed.",
        "expansion_criterion": "The CG is already firm for the in-envelope round-trip capability. Envelope-push (per USER directive): the mechanism-research n0-location dispute (sparse-Hebbian n0~915 vs channel-dispersion n0~400-500) is resolved by adding fixed-V=8192 grid points at D∈{8,12,16,20}; and the RNS/CRT modular sub-block scheme is the ranked next lever to push the V-per-block ceiling past 8192 without growing N. DEMOTES only if a re-run fails to reproduce exact=1.000 in-envelope across seeds (not expected; cv=0).",
        "disposition": "CHAIN_GRADE_native_GSBC_ordered_generation_roundtrip_via_block_local_sparse_resonator_PERFECT_in_envelope_encoding_mismatch_PROVEN_non_vacuous_PLUS_measured_capacity_cliff_at_V8192D26_0p856_reconciled_with_sparse_hebbian_law",
        "cert_increment_delta": 1,
    },
}

# ---------------------------------------------------------------------------
# ATOM 2 -- TEM inductive transfer OFF ZERO (math, MM_STANDARD / MIDDLE_BAND)
# ---------------------------------------------------------------------------
atom_tem = {
    "id": "math::MM_STANDARD_inductive_relational_transfer_to_NOVEL_entities_moves_OFF_ZERO_at_canonical_the_content_conditioned_SCORER_bilinear_RESCAL_yields_real_minus_shuf_inductive_plus0p049_to_plus0p16_on_semantic_relations_AtLocation_CausesDesire_CapableOf_where_the_averaged_transform_GLOBAL_TransE_marginal_is_ZERO_minus0p004_to_plus0p009_shuffle_invariant_SHUFFLED_collapses_to_floor_0p007_to_0p042_vs_randenc_0p011_NON_VACUOUS_synth_discriminators_FIRE_and_DIFFERENTIATE_type_hard_0p66_vs_0p775_content_map_0p035_vs_0p207_NOT_saturated_repairs_prior_vacuous_ablation_DerivedFrom_positive_control_SCORER_plus0p624_HARD_PASS_proves_discriminator_reaches_HP_magnitude_so_semantic_MIDDLE_BAND_is_SUBSTANTIVE_not_test_design_failure_magnitude_below_HP_0p2075_is_under_parameterization_M200_plus_CapableOf_data_starvation_plus_one_to_many_entropy_ceiling_NOT_mechanism_wall_SCORER_ge_TEM_on_net_real_minus_shuf_3seed_FULL_N8192_V100_528units_2026-07-05",
    "name": "MATH MM_STANDARD: inductive relational transfer to NOVEL entities moves OFF ZERO at canonical. The content-conditioned SCORER (bilinear/RESCAL) yields real_minus_shuf(inductive)=+0.049..+0.16 on the semantic relations (AtLocation/CausesDesire/CapableOf), where the averaged-transform GLOBAL (TransE-marginal) is ~0 (-0.004..+0.009, shuffle-invariant -- confirming the prior arc). SHUFFLED collapses to floor; synth discriminators FIRE and DIFFERENTIATE (type_hard 0.66/0.775, content_map 0.035/0.207 -- NOT saturated, repairs the prior vacuous ablation). DerivedFrom positive control SCORER=+0.624 (HARD_PASS) proves the discriminator reaches HP magnitude -> semantic MIDDLE_BAND is SUBSTANTIVE, not test-design failure. Modest magnitude (<0.2075 HP) = under-parameterization + CapableOf data-starvation + one-to-many entropy ceiling, NOT a mechanism wall. SCORER >= TEM on net real_minus_shuf.",
    "corpus": "math",
    "tier": "MM_STANDARD",
    "kind": "experiment_landed_vet",
    "cert_status": "proven_bound_measured_mechanism_middle_band_genuine_nonzero_inductive_transfer",
    "cert_class": "inductive_relational_transfer_novel_entities_content_conditioned_bilinear_scorer_off_zero_averaged_transform_still_zero_non_vacuous_modest_magnitude_under_parameterized",
    "description": (
        "LANDED-VET of exp_schema_relation_TEM_structural_content_binding_v1 (verdict MIDDLE_BAND, "
        "run_mode=full, N=8192, V=100, 4 relations [AtLocation, CausesDesire, CapableOf, DerivedFrom], 2 "
        "content encodings [bge_semantic, gsbc], mech slots [GLOBAL, TEM_K5/K10/K20, SCORER], REAL/SHUFFLED "
        "arms x inductive/transductive, 3 seeds [7,13,19], 528/528 units, cardinality_ok=True, "
        "arms_differ_verified=True, bind_roundtrip=1.000; commit d814a43bc). "
        "AUDITOR INDEPENDENT RECOMPUTE (.venv): real_minus_shuf recomputed from the RAW cells_aggregate "
        "REAL/SHUFFLED inductive means (NOT the pre-computed cell_diag field -- Fix#28), reproduced disk "
        "EXACTLY. "
        "CANONICAL CONFIRMS THE SMOKE (all three Director scrutiny points): "
        "(a) GENUINE NONZERO real_minus_shuf on real relations where the averaged-transform family was ZERO. "
        "SCORER (content-conditioned bilinear) inductive real_minus_shuf: AtLocation +0.0622(bge)/+0.0489(gsbc), "
        "CausesDesire +0.0933(bge)/+0.0533(gsbc), CapableOf +0.1600(bge)/+0.0800(gsbc). GLOBAL (single additive "
        "relation vector = TransE-marginal) inductive real_minus_shuf: -0.0022..+0.0089 across all 6 semantic "
        "cells -- i.e. ~0, shuffle-invariant, exactly the prior arc's finding (the averaged/holistic-map family "
        "extracts a relation PRIOR not a per-instance mapping). "
        "(b) NON-VACUOUS (the load-bearing check -- prior ablation's discriminator SATURATED and was ruled "
        "vacuous): THIS cell's SHUFFLED collapses to floor (SCORER shuf 0.007-0.042 vs randenc_floor 0.011) "
        "while REAL stays elevated -- REAL differentiates from SHUFFLED, not both saturating. Both synthetic "
        "by-construction discriminators FIRE AND DIFFERENTIATE (NOT saturated): synth_type_hard GLOBAL=0.661 vs "
        "TEM_best=0.775 (tem_adv=+0.114); synth_content_map GLOBAL=0.035 vs SCORER=0.207 (scorer_adv=+0.172). "
        "This directly REPAIRS the prior estimator-ablation whose synth_hard saturated at 1.0/1.0 (trained_adv "
        "0.000) making its comparison axis vacuous. "
        "(c) MECHANISM READ CONFIRMED: content-conditioned bilinear (SCORER=RESCAL/DistMult move, O(d^2) "
        "capacity) beats/ties the single additive transform (GLOBAL=TransE, O(d), provably degenerates to the "
        "population-marginal object on one-to-many relations); TEM's hard K-means type-clustering also moves "
        "off zero (best-K net real_minus_shuf +0.018..+0.067) but by LESS than SCORER because TEM's SHUFFLED "
        "stays elevated (coarse type structure partially survives shuffle). Modest magnitude is a mix of "
        "recoverable under-parameterization (M_OP=200 fixed smoke=full; AtLocation/CausesDesire have real "
        "in-codebook headroom) + a hard CapableOf data-availability ceiling (4.2% top-100 codebook coverage, "
        "near one-to-one) + a true one-to-many entropy ceiling the KG-embedding field never fully escapes -- "
        "NOT a mechanism failure. "
        "POSITIVE CONTROL CLEARS ITS FLOOR (auditor discipline: verify PC before crediting/faulting the "
        "negative): DerivedFrom (lexical/orthographic relation) SCORER real_minus_shuf=+0.624(bge)/+0.222(gsbc), "
        "HARD_PASS -- the discriminator DOES reach HP magnitude when the content signal is strong, so the "
        "semantic relations' MIDDLE_BAND is a SUBSTANTIVE property of semantic content-availability, NOT a "
        "broken/insensitive test. "
        "TIER RATIONALE: MM_STANDARD (MIDDLE_BAND) -- genuine signal above RMS_SIGNAL_MIN (0.05) but below "
        "HP_RMS_MIN (0.2075) on the semantic relations; the FIRST non-vacuous evidence that the substrate can "
        "turn stored facts into transferable relational knowledge about entities it has never seen (inductive/"
        "novel), a real if modest capability. Under-parameterized, not a wall. "
        "SCOPE (honest, per USER no-smoke): usable-in-principle today only for relations with training-pair "
        "headroom AND coarse-type-predictable objects (AtLocation/CausesDesire-like); NOT yet for near-one-to-"
        "one/long-tail relations (CapableOf-like) at small V; and NOT at magnitude sufficient to replace "
        "curated relation lookups. The decisive next spend (M_OP/steps/DF scale-up + SOFT-TEM, CPU) tells us "
        "whether this is an engineering ramp (more data + richer content, per the BLP/SimKGC trend) or a "
        "content-ceiling on thin generic-sentence encodings."
    ),
    "aliases": ["inductive_relational_transfer_off_zero_content_conditioned_scorer_MM",
                "TEM_vs_SCORER_vs_GLOBAL_real_minus_shuf_novel_entity_middle_band"],
    "metadata": {
        "record_class": "experiment_landed_vet_middle_band_genuine_nonzero",
        "term_class": "INDUCTIVE_RELATIONAL_TRANSFER_NOVEL_ENTITIES_CONTENT_CONDITIONED_OFF_ZERO_AVERAGED_TRANSFORM_ZERO_MIDDLE_BAND",
        "cert_status": "proven_bound_measured_mechanism_middle_band_genuine_nonzero_inductive_transfer",
        "cert_class": "inductive_transfer_novel_entities_scorer_bilinear_off_zero_global_transE_zero_non_vacuous_modest_under_parameterized",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "verified_via": "independent .venv recompute of real_minus_shuf from RAW cells_aggregate REAL/SHUFFLED inductive means (not cell_diag; Fix#28); reproduced disk EXACTLY",
        "atomized_by": "skunkworks_landed_VET_2026-07-05_TEM_inductive_offzero",
        "anchor": "schema_relation_TEM_structural_content_binding_v1",
        "cell_commit": "d814a43bc",
        "raw_metrics_path": "data/exp_schema_relation_TEM_structural_content_binding_v1/metrics.json",
        "run_mode": "full", "N": 8192, "V": 100, "M_OP": 200,
        "n_seeds": 3, "seeds": [7, 13, 19], "n_units": 528, "cardinality_ok": True,
        "recompute_off_disk": {
            "SCORER_real_minus_shuf_inductive": {
                "AtLocation_bge": 0.0622, "AtLocation_gsbc": 0.0489,
                "CausesDesire_bge": 0.0933, "CausesDesire_gsbc": 0.0533,
                "CapableOf_bge": 0.1600, "CapableOf_gsbc": 0.0800},
            "GLOBAL_real_minus_shuf_inductive_semantic": {
                "AtLocation_bge": -0.0022, "AtLocation_gsbc": 0.0022,
                "CausesDesire_bge": -0.0044, "CausesDesire_gsbc": 0.0089,
                "CapableOf_bge": 0.0022, "CapableOf_gsbc": 0.0000},
            "TEM_bestK_real_minus_shuf_inductive_range": [0.0178, 0.0667],
            "DerivedFrom_positive_control_SCORER_real_minus_shuf": {"bge": 0.6244, "gsbc": 0.2222},
            "synth_type_hard": {"GLOBAL": 0.6608, "TEM_best": 0.775, "tem_adv": 0.1142},
            "synth_content_map": {"GLOBAL": 0.035, "SCORER": 0.2067, "scorer_adv": 0.1717},
            "randenc_floor": 0.0106, "bind_roundtrip": 1.000,
            "bands": {"HP_RMS_MIN": 0.2075, "RMS_SIGNAL_MIN": 0.05},
            "match_disk": "EXACT",
        },
        "non_vacuity_checks": {
            "shuffled_collapses": "SCORER shuf inductive 0.007-0.042 (near randenc floor 0.011) while REAL 0.055-0.171 -> REAL differentiates from SHUFFLED (not both saturating)",
            "synth_discriminators_fire_AND_differentiate": "type_hard 0.661/0.775 (tem_adv +0.114, NOT saturated); content_map 0.035/0.207 (scorer_adv +0.172, NOT saturated) -- repairs prior ablation's 1.0/1.0 vacuous discriminator",
            "positive_control_clears_floor": "DerivedFrom SCORER real_minus_shuf +0.624 (HARD_PASS) -> discriminator reaches HP magnitude when signal strong -> semantic MIDDLE_BAND is SUBSTANTIVE not test-design failure",
            "arms_differ_digests_distinct": "GLOBAL_REAL/TEM_REAL/MEAN_OBJECT/SCORER_REAL/SCORER_SHUF all distinct sha256 -> arms are genuinely different computations",
        },
        "confirmed_off_zero": True,
        "honest_scope": "GENUINE modest inductive transfer to NOVEL entities via content-conditioned bilinear scoring (SCORER=RESCAL), where the averaged/holistic-map family (GLOBAL here; prior arc HARD_FAILs) is exactly ZERO. Magnitude 0.05-0.16 real_minus_shuf < 0.2075 HP -> MIDDLE_BAND. Usable-in-principle for headroom + coarse-type-predictable relations (AtLocation/CausesDesire), not for near-one-to-one long-tail (CapableOf) at small V, not at replace-curated-lookup magnitude. Under-parameterized (M_OP=200), not a wall.",
        "cross_arc_overlap_check_2026_07_01_USER_locked": "substrate_query 'inductive relational transfer novel entities content-conditioned bilinear scorer real minus shuffled off zero' -> top hits @cosine 0.28 (below 0.30 rail): a track2-B schema-VET note + the P9 drill note ('trained Tier-1 universal-relation embedding provides no cross-domain transfer, hurts vs reading geometry'). Those are the PRIOR NEGATIVE (averaged/universal-relation = zero); this cell's content-conditioned SCORER/TEM off-zero is the genuinely NEW positive counterpart. Below rail; NOT a rediscovery -- it is the FIX-side result to the exhausted-zero averaged-transform family.",
        "composes_with_atoms": [PRIOR_HF_ESTIMATOR_ABLATION],
        "composition_note": "COMPOSES WITH (does NOT supersede) the prior HARD_FAIL_SCOPED estimator-ablation (e17098868) and its parent bundle-transfer HARD_FAIL (b8a8d107d): those proved the AVERAGED/holistic-map transform (naive AND trained rotation) yields ZERO shuffle-invariant inductive transfer. This cell is the POSITIVE counterpart -- CONTENT-CONDITIONING (bilinear SCORER, type-clustering TEM) moves OFF that zero (GLOBAL here reproduces the ~0). It also amends the prior META rule on vacuous ablation discriminators: this cell's discriminators are NON-vacuous (fire and differentiate), demonstrating the repaired design.",
        "framing_corrections_vs_director_and_cell": "AFFIRM all three Director claims (off-zero real, non-vacuous, MIDDLE_BAND, SCORER>=TEM). Two symmetric corrections: (1) UPWARD -- the claimed range '~0.05-0.13' UNDERSTATES the top: CapableOf|bge SCORER real_minus_shuf reaches +0.16 (above 0.13). Tier unaffected (still < 0.2075 HP -> MIDDLE_BAND); noted for accuracy, not inflation. (2) NUANCE on 'SCORER>=TEM': true on NET real_minus_shuf, but TEM and SCORER win DIFFERENT synthetic discriminators (TEM wins synth_type_hard +0.114; SCORER wins synth_content_map +0.172) -- TEM is a type-structural mechanism, SCORER a content/bilinear one; SCORER's net edge on the REAL relations comes from its SHUFFLED collapsing further. Not 'TEM is worse at everything'.",
        "expansion_criterion": "PROMOTES toward CHAIN_GRADE iff the scale-up cell (schema_relation_TEM_scorer_scaleup_v1: M_OP∈{200,500,800}, SCORER_STEPS∈{150,300,600}, SCORER_DF∈{96,192}, + SOFT-TEM) lifts real_minus_shuf(inductive) >= 0.2075 on >=1 semantic relation with discriminators firing (engineering-ramp confirmed). Stays MM if partial (0.03-0.10 gain). DEMOTES toward HARD_FAIL/ceiling iff 4x M_OP + 4x steps improves real_minus_shuf by < 0.03 on ALL semantic relations x both families (genuine content/entropy ceiling -> fix is richer content, not more compute).",
        "disposition": "MM_STANDARD_MIDDLE_BAND_genuine_nonzero_inductive_transfer_to_novel_entities_via_content_conditioned_bilinear_SCORER_off_the_averaged_transform_ZERO_non_vacuous_positive_control_fires_modest_magnitude_under_parameterized_not_a_wall_SCORER_ge_TEM_on_net_real_minus_shuf",
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


def ledger_append(atom, ledger_path=CERT_LEDGER):
    md = atom["metadata"]
    entry = {
        "ts": TS,
        "ts_iso": TS_ISO,
        "atom_id": atom["id"],
        "corpus": atom["corpus"],
        "tier": atom["tier"],
        "cert_status": md.get("cert_status"),
        "cert_class": md.get("cert_class"),
        "cert_increment_delta": md.get("cert_increment_delta", 0),
        "verified_off_data": True,
        "anchor": md.get("anchor"),
        "cell_commit": md.get("cell_commit"),
        "auditor": "skunkworks",
        "atomized_by": md.get("atomized_by"),
        "landed_VET_session": SESSION_TAG,
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

    n = a5_append(MATH_ATOMS, atom_gen)
    print(f"[atomize] (1) math CHAIN_GRADE blocklocal-native-GSBC-generation appended; math lines={n}")
    ledger_append(atom_gen)

    n = a5_append(MATH_ATOMS, atom_tem)
    print(f"[atomize] (2) math MM_STANDARD TEM-inductive-off-zero appended; math lines={n}")
    ledger_append(atom_tem)

    print("[atomize] DONE 2 atoms + 2 ledger entries; A5-gated (tmp+os.replace+verify-load+json-integrity); matching TS_ISO")
    print("[atomize] NET CERT DELTA: CG +1 (generation), MM +1 (TEM inductive off-zero), HF 0")
