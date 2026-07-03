"""
A5-gated atomization: PPMI/SVD Wikipedia FULL N=10K FORMAL 3-seed landing.

Landed-VET off-disk verification (Fix #28):
  metrics.json: d:/AI/hd-instrument/data/exp_substrate_wikipedia_ppmi_svd_scale_up_full_2026_07_03/metrics.json
  ts_iso_end = 2026-07-03T03:30:47.893262+00:00
  run_mode = "full"; n_seeds = 3 [11, 17, 23]; elapsed_s = 1332.87

  PPMI_SVD_N10K       r@5 mean = 0.6791  std = 0.0     (bit-identical across 3 seeds)
  CHAR_TRIGRAM_N10K   r@5 mean = 0.7030  std = 0.0     (bit-identical across 3 seeds)
  RANDOM_N10K         r@5 mean = 0.0003  std = 0.000163 (seed varies random arm; chance=0.0005)

  delta_PPMI_minus_char_trigram = -0.02389999... < 0.03 MB floor -> MB_LOW_DELTA
  delta_from_smoke_r5_ppmi = -0.2269
  cardinality_ok = True (6/6, actual_n_units=9 = expected)
  arms_differ_verified = True (all 3 seeds; digests seed-invariant for PPMI/CT arms;
     seed-varying for RANDOM arm, as expected -- deterministic encoders + stochastic baseline)
  baseline_in_band_check = in_band (0.0003 in [0, 0.0025])

GATE 1 check (Director def: "formal 3-seed within +/-0.02 of preliminary"):
  Preliminary PPMI r@5 = 0.6791; Formal PPMI r@5 = 0.6791
  Delta = 0.0000  <  +/-0.02  -> GATE 1 SATISFIED (bit-identical)

SYMMETRIC-VERIFY on bit-identity:
  Question: could bit-identity be a code bug (corpus subsample same despite seeded seeds)?
  Analysis: arms_differ_digests show PPMI + char_trigram digests INVARIANT across seeds
     (655e385af... and 591c3a5be... respectively) while RANDOM arm digests VARY per seed.
     This is CONSISTENT WITH deterministic encoders + fixed corpus subsample selection
     (first-N articles); RNG only affects RANDOM baseline arm. This IS legitimate mechanism-
     property, NOT a code bug. Auditor flag: "3-seed cardinality" for PPMI/CT does not
     provide corpus-subsample-variance evidence -- only encoder-determinism replication.
     This is not a defect for the current claim (deterministic reproduction), but a scope
     note for anyone reading the r@5_std=0.0 numbers.

Atoms filed (3):
  (a) MATH: formal CG_HONEST_NEGATIVE, supersedes PRELIMINARY atom; drops preliminary tag
  (b) META: parent META synth advances MM_TENTATIVE_SYNTHESIS_4 -> MM_STANDARD_5_WITNESS_GATE1_SATISFIED
      (formalizes witness4 + adds Spoke3 hippocampal SMOKE HF as witness5)
      Supersedes prior 4-witness MM_TENTATIVE version.
      CG_META promotion STILL gated on: 2nd FULL-scale mechanism-class witness (Spoke3 FULL or ABC composition FULL)
  (c) META: sibling META TASK_CLASS_FIT advances -- Gate 1 blocker cleared; regime caveats remain
      Supersedes prior sibling atom.
      CG_META promotion path clarified: HP3-K_DIST rec'd 20-K resolved, saturation ceiling caveat, VSA WIN-side clean
"""
import json
import os
import time
import tempfile

MATH_ATOMS = "d:/AI/hd-instrument/data/substrate_index/math/atoms.jsonl"
META_ATOMS = "d:/AI/hd-instrument/data/substrate_index/meta/atoms.jsonl"
CERT_LEDGER = "d:/AI/hd-instrument/data/substrate_index/meta/cert_ledger.jsonl"

TS = time.time()
TS_ISO = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(TS))
COMMIT = "416022ecc"  # cell timeout 1800s + per-seed checkpoint fix

# ============= ATOM (a): FORMAL CG_HONEST_NEGATIVE (supersedes PRELIMINARY) =============
atom_hn_formal = {
    "id": (
        "math::T3/EXP_substrate_wikipedia_ppmi_svd_scale_up_FULL_N10K_FORMAL_3SEED_CG_HONEST_NEGATIVE_"
        "supersedes_PRELIMINARY_atom_formal_metrics_json_landed_2026_07_03T03_30_47Z_"
        "PPMI_r5_0p6791_std_0p0_bit_identical_all_3_seeds_char_trigram_r5_0p7030_std_0p0_bit_identical_"
        "random_r5_0p0003_std_0p00016_chance_0p0005_in_band_delta_PPMI_minus_char_trigram_neg_0p0239_"
        "below_MB_floor_0p03_MB_LOW_DELTA_verdict_direction_matches_preliminary_bit_identical_within_0p00_"
        "of_preliminary_0p6791_Gate_1_SATISFIED_within_plus_minus_0p02_tolerance_"
        "scale_from_smoke_shrinks_PPMI_neg_0p2269_shrinks_char_trigram_neg_0p151_PPMI_more_scale_sensitive_"
        "cardinality_6_of_6_arms_differ_verified_baseline_in_band_run_mode_full_seeds_11_17_23_"
        "elapsed_1333s_symmetric_verify_bit_identity_is_legitimate_encoder_determinism_plus_fixed_corpus_subsample_"
        "NOT_code_bug_confirmed_via_arms_differ_digests_PPMI_and_char_trigram_seed_invariant_random_seed_varying_"
        "audit_trail_gap_from_preliminary_resolved_formal_metrics_json_authoritative_"
        "scope_TIGHT_SUPERVISED_wikipedia_title_to_body_N10K_body_cap_800_n_dim_2048_"
        "amends_smoke_CG_r5_0p906_with_scale_narrowing_confirmed_at_FULL_supersedes_preliminary_atom_"
        "2026-07-03"
    ),
    "name": "EXP substrate_wikipedia_ppmi_svd_scale_up FULL FORMAL 3-seed CG_HONEST_NEGATIVE (r5=0.6791 vs char_trigram 0.7030 delta -0.024 MB_LOW_DELTA; Gate 1 SATISFIED bit-identical to preliminary; supersedes PRELIMINARY atom)",
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Experiment record: exp_substrate_wikipedia_ppmi_svd_scale_up_full_2026_07_03 (FORMAL landing). "
        "Cell re-dispatched with cell timeout 1800s + per-seed checkpoint fix (commit 416022ecc); "
        "landed cleanly 2026-07-03T03:30:47Z (elapsed ~22 min wall). Off-disk metrics.json is authoritative "
        "(SH-9-recovered; corpus-completeness remote-vs-local gotcha caught; local dir had stale smoke). "
        "PPMI/SVD ATL-hub-analog encoder r@5 = 0.6791 (std=0.0 bit-identical across seeds 11, 17, 23); "
        "char_trigram surface-bag reference r@5 = 0.7030 (std=0.0 bit-identical); random baseline r@5 mean "
        "0.0003 (std=0.000163) vs chance 0.0005 -- in-band. Delta PPMI - char_trigram = -0.0239 < 0.03 "
        "MB floor -> MEASURED_BOUND_LOW_DELTA verdict tier. Cardinality 6/6 (arms_differ_verified True "
        "per seed; actual_n_units=9 = expected). Direction REVERSES SMOKE precedent (SMOKE +0.052 -> "
        "FULL -0.024); PPMI shrinks -0.2269 (0.906 -> 0.6791) vs char_trigram shrinks -0.151 (0.854 -> "
        "0.7030); PPMI more scale-sensitive. "
        "GATE 1 (Director def: 'formal 3-seed within +/-0.02 of preliminary'): Preliminary PPMI r@5 = "
        "0.6791 (2-seed heartbeat) vs Formal PPMI r@5 = 0.6791 (3-seed) -- 0.00 delta, BIT-IDENTICAL. "
        "GATE 1 SATISFIED. "
        "SYMMETRIC-VERIFY on bit-identity: arms_differ_digests show PPMI (655e385a...) and char_trigram "
        "(591c3a5b...) digests INVARIANT across seeds; RANDOM arm digests VARY per seed. This is "
        "CONSISTENT with deterministic encoders (fixed blake2b codebook for CT; fixed PPMI fit on body "
        "corpus for PPMI) + fixed corpus subsample selection (first-N articles). Seed only affects "
        "stochastic RANDOM baseline. NOT a code bug. Auditor scope-note: '3-seed cardinality' for PPMI/CT "
        "does not provide corpus-subsample-variance evidence -- only encoder-determinism replication. "
        "This is not a defect for the current claim, but a scope note for anyone reading std=0.0. "
        "SUPERSEDES the PRELIMINARY_CG_HONEST_NEGATIVE atom (2-seed heartbeat with metrics.json MISSING). "
        "Formal metrics.json is now authoritative and audit-trail gap is resolved. "
        "AMENDS the smoke CG (r5=0.906 N=500) with confirmed scale-narrowing at FULL: mechanism-lift "
        "does NOT survive at 20x scale. SCOPE TIGHT: SUPERVISED Wikipedia title-body retrieval, N=10K, "
        "body_cap=800, n_dim=2048, seeds 11/17/23. NOT a general capability claim (USER-locked "
        "substrate-knows-almost-nothing framing respected). PPMI mechanism arc TERMINATES in supervised "
        "regime here; further exploration routes to v3-composed or Spoke 3 pathway analysis."
    ),
    "aliases": [],
    "metadata": {
        "record_class": "experiment_record",
        "term_class": "PROCESS_KNOWLEDGE_NON_MATH",
        "metric_type": "recall_at_5_wikipedia_title_to_body_retrieval",
        "experiment_path": "experiments/exp_substrate_wikipedia_ppmi_svd_scale_up_full_2026-07-03.py",
        "prereg_path": "preregs/2026-07-03_substrate_wikipedia_ppmi_svd_scale_up_full.md",
        "metrics_paths": [
            "d:/AI/hd-instrument/data/exp_substrate_wikipedia_ppmi_svd_scale_up_full_2026_07_03/metrics.json"
        ],
        "cell_sha": COMMIT,
        "remote_run_id": "cpu_runner_0_2026-07-03T03:08Z_to_03:30Z",
        "verdict": "MEASURED_BOUND_LOW_DELTA",
        "verdict_tier_auditor": "CG_HONEST_NEGATIVE_FORMAL",
        "run_mode": "full",
        "provenance_quality": "CG_HONEST_NEGATIVE_FORMAL",
        "relevance_tier": "HIGH",
        "era": "STAGE_2_CONCEPT_ENCODER_ARC_2026-07-02",
        "cert_status": "chain_grade_honest_negative_formal",
        "cert_class": "ppmi_svd_wikipedia_encoder_loses_to_char_trigram_at_N10K_scale_reversal_from_smoke_supervised_regime_FORMAL_3SEED",
        "verified_off_data": True,
        "verification_method": "SH-9-recovered metrics.json off-disk; run_mode=full disambiguated per orchestrator ae42cf5f3f2f0b3fa",
        "atomized_by": "skunkworks_landed_VET_2026-07-03_ppmi_svd_wikipedia_FULL_FORMAL_GATE1_satisfied",
        "cert_ts": TS_ISO,
        "n_seeds_configured": 3,
        "n_seeds_landed": 3,
        "seeds": [11, 17, 23],
        "n_dim": 2048,
        "N_articles": 10000,
        "elapsed_s": 1332.87,
        "cardinality_ok": True,
        "arms_differ_verified": True,
        "baseline_in_band": True,
        "run_mode_verified_full": True,
        "per_seed_ppmi_r5": [0.6791, 0.6791, 0.6791],
        "per_seed_char_trigram_r5": [0.7030, 0.7030, 0.7030],
        "per_seed_random_r5": [0.0003, 0.0001, 0.0005],
        "ppmi_r5_mean": 0.6791,
        "ppmi_r5_std": 0.0,
        "char_trigram_r5_mean": 0.7030,
        "char_trigram_r5_std": 0.0,
        "random_r5_mean": 0.0003,
        "random_r5_std": 0.000163,
        "chance_r5_at_N10K": 0.0005,
        "delta_ppmi_minus_char_trigram_at_N10K_FORMAL": -0.0239,
        "delta_ppmi_minus_char_trigram_at_N500_smoke_precedent": 0.0520,
        "direction_reversal_from_smoke_to_full": True,
        "ppmi_shrink_smoke_to_full": -0.2269,
        "char_trigram_shrink_smoke_to_full": -0.1510,
        "ppmi_more_scale_sensitive_than_char_trigram": True,
        "GATE_1_definition": "formal 3-seed within +/-0.02 of preliminary heartbeat",
        "GATE_1_preliminary_ppmi_r5": 0.6791,
        "GATE_1_formal_ppmi_r5": 0.6791,
        "GATE_1_delta": 0.0,
        "GATE_1_status": "SATISFIED_bit_identical",
        "symmetric_verify_bit_identity": {
            "hypothesis_a_legitimate": "deterministic encoders (fixed codebook + fixed PPMI fit) + fixed corpus subsample selection (first-N articles); seed only affects RANDOM baseline",
            "hypothesis_b_code_bug": "seed intended to shuffle corpus but silently ignored",
            "evidence": "arms_differ_digests show PPMI/CT digests SEED-INVARIANT (655e385a..., 591c3a5b...) but RANDOM arm digest VARIES per seed (e2ecc07..., 4fc1ff0c..., 4508efcf...); RNG plumbing IS wired to random arm; encoders are deterministic by design",
            "conclusion": "hypothesis_a confirmed; NOT a code bug; legitimate mechanism-property",
            "scope_note": "3-seed cardinality for PPMI/CT does NOT provide corpus-subsample-variance evidence, only encoder-determinism replication"
        },
        "supersedes": [
            "math::T3/EXP_substrate_wikipedia_ppmi_svd_scale_up_FULL_N10K_PRELIMINARY_CG_HONEST_NEGATIVE_2of3_seeds_heartbeat_only_metrics_json_MISSING_killed_mid_seed3_at_1200s_timeout_ceiling_PPMI_r5_0p6791_bit_identical_across_2_seeds_deterministic_encoder_char_trigram_r5_0p7030_bit_identical_2_seeds_delta_PPMI_minus_char_trigram_neg_0p0239_DIRECTION_REVERSES_SMOKE_N500_precedent_which_showed_plus_0p0520_random_baseline_in_band_0p0001_0p0003_at_N10K_chance_0p0001_scale_from_smoke_shrinks_PPMI_by_neg_0p2269_0p906_to_0p6791_shrinks_char_trigram_by_neg_0p151_0p854_to_0p703_PPMI_more_scale_sensitive_than_char_trigram_bag_encoding_wall_PPMI_413s_char_trigram_15s_random_7s_per_seed_defensibility_2seed_deterministic_encoder_arms_differ_digests_identical_smoke_precedent_seed_adds_zero_info_for_main_claim_but_formal_3seed_metrics_json_MISSING_hence_PRELIMINARY_tag_reflects_audit_trail_gap_not_epistemic_uncertainty_scope_TIGHT_SUPERVISED_wikipedia_title_to_body_N10K_body_cap_800_n_dim_2048_supersedes_None_amends_smoke_CG_with_scale_narrowing_context_composes_with_char_trigram_FULL_MB_precedent_same_day_2026-07-03"
        ],
        "amends": [
            "math::T3/EXP_substrate_wikipedia_ppmi_svd_baseline_SMOKE_CG_MEASURED_BOUND_3seed_N500 (r5=0.906 SMOKE CG stays valid at N=500; amended with confirmed scale-narrowing at FULL N=10K)"
        ],
        "composes_with": [
            "math::T3/EXP_substrate_wikipedia_char_trigram_scale_up_full_N10K_MEASURED_BOUND (same-day char_trigram FULL r5=0.703 reference)",
            "math::T3/EXP_substrate_concept_encoder_substrate_content_v1_CG_HONEST_NEGATIVE (WordNet N=100 witness 1)",
            "math::T3/witness_VWFA_HRR_position_binding_wikipedia_smoke_CG_HONEST_NEGATIVE (VWFA smoke witness 3)"
        ],
        "cites": [
            "Fix_28_verify_per_arm_off_disk",
            "USER_locked_substrate_knows_almost_nothing_2026-07-02",
            "USER_locked_corpus_completeness_remote_vs_local_half_data",
            "cell_author_verdict_MEASURED_BOUND_LOW_DELTA_matches_auditor_recompute"
        ],
        "verdict_arc_terminal": True,
        "next_arc_routing": "PPMI mechanism arc TERMINATES in supervised regime; further exploration routes to v3-composed (already MIDDLE_BAND) or Spoke 3 hippocampal pathway analysis",
        "cert_increment_delta": 1
    }
}


# ============= ATOM (b): PARENT META synth advances MM_TENTATIVE_4 -> MM_STANDARD_5_WITNESS_GATE1_SATISFIED =============
atom_meta_parent_advanced = {
    "id": (
        "meta::T2/META_SUBSTRATE_NATIVE_STRUCTURAL_MECHANISMS_LOSE_TO_CHAR_TRIGRAM_BAG_ON_REAL_CONTENT_"
        "RETRIEVAL_AT_SCALE_MM_STANDARD_5_WITNESS_GATE_1_SATISFIED_supersedes_MM_TENTATIVE_4_witness_atom_"
        "witness4_PPMI_SVD_wikipedia_FULL_N10K_r5_0p6791_delta_neg_0p0239_now_FORMAL_3seed_bit_identical_to_preliminary_"
        "witness5_added_MATH_SPOKE3_HIPPOCAMPAL_DG_CA3_wikipedia_smoke_N500_r5_0p145_vs_char_trigram_0p854_delta_neg_0p709_HUGE_lose_new_mechanism_class_hippocampal_orthogonalization_but_at_SMOKE_scale_not_FULL_half_credit_toward_CG_META_expansion_criterion_"
        "5_witnesses_span_5_mechanism_classes_concept_encoder_hopfield_readout_VWFA_position_binding_PPMI_SVD_cooccurrence_hippocampal_DG_CA3_orthogonalization_"
        "Gate_1_SATISFIED_formal_PPMI_FULL_within_plus_minus_0p00_of_preliminary_"
        "CG_META_promotion_STILL_gated_on_2nd_FULL_scale_mechanism_class_witness_e_g_Spoke3_hippocampal_at_wikipedia_FULL_or_ABC_composition_at_FULL_scale_"
        "scope_witnesses_at_N100_N500_N10K_real_wordnet_and_real_wikipedia_common_failure_mode_char_trigram_bag_gets_free_high_lexical_overlap_signal_"
        "PPMI_mechanism_arc_TERMINATES_in_supervised_regime_here_Spoke3_arc_now_load_bearing_"
        "2026-07-03"
    ),
    "name": "META SUBSTRATE_NATIVE_STRUCTURAL_MECHANISMS_LOSE_TO_CHAR_TRIGRAM_BAG_ON_REAL_CONTENT_RETRIEVAL_AT_SCALE (MM_STANDARD 5-witness; GATE 1 SATISFIED; CG_META still gated on 2nd FULL-scale mechanism-class witness)",
    "corpus": "meta",
    "tier": "T2",
    "kind": "methodology_rule_pattern_synthesis",
    "description": (
        "META synthesis (MM_STANDARD, 5 witnesses across 5 heterogeneous mechanism classes; supersedes "
        "MM_TENTATIVE 4-witness prior atom): substrate-native structural mechanisms designed to add signal "
        "above char-trigram surface bag consistently FAIL to beat char-trigram bag on real-content retrieval "
        "tasks, even when they succeed on synthetic supervised clustering regimes. "
        "Witness 1 (2026-07-02): substrate_content_v1 concept_encoder WordNet N=100 r5=0.160 < CT r5=0.280 (delta -0.120). "
        "Witness 2 (2026-07-03): component_C_modern_hopfield_readout WordNet N=100 r5=0.05 < CT 0.280 (delta -0.107 vs cosine). "
        "Witness 3 (2026-07-03): VWFA_HRR_position_binding Wikipedia SMOKE N=500 r5=0.776 < CT 0.854 (delta -0.078). "
        "Witness 4 (2026-07-03, NOW FORMAL 3-seed): PPMI/SVD Wikipedia FULL N=10K r5=0.6791 < CT 0.7030 (delta -0.0239). "
        "  Gate 1 satisfied: formal 3-seed matches preliminary heartbeat bit-identically (0.6791 = 0.6791; delta 0.00). "
        "  Direction REVERSES from SMOKE N=500 which had +0.052 lift; scale collapses PPMI mechanism-lift. "
        "Witness 5 (2026-07-03): MATH_SPOKE3_HIPPOCAMPAL_DG_CA3 Wikipedia SMOKE N=500 r5=0.145 < CT 0.854 (delta -0.709 HUGE lose). "
        "  New mechanism class (hippocampal DG/CA3 orthogonalization) but at SMOKE scale only; half-credit toward CG_META. "
        "PATTERN: 5 witnesses span 5 mechanism classes -- concept encoder (competitive Hebbian WTA), dense associative "
        "readout (modern Hopfield), position-binding (VWFA HRR), co-occurrence matrix factorization (PPMI/SVD), "
        "hippocampal orthogonalization (DG expansion + CA3 completion). All fail to beat surface char-trigram bag "
        "on real-content retrieval. Common failure mode: char-trigram bag gets 'free' high lexical-overlap signal "
        "from real-content queries (multi-token or single-word) that structural encoders either do not add to OR "
        "actively dilute by compressing to lower effective rank. USER-LOCKED 'mechanism analog is NOT task analog' "
        "holds: brain-analog mechanisms passing synthetic supervised regime does NOT transfer to real-content "
        "unsupervised regime. "
        "SCOPE: 5 witnesses at N in [100, 500, 10000] real-content retrieval (WordNet lexicon + real Wikipedia). "
        "TIER ADVANCE: MM_TENTATIVE 4-witness -> MM_STANDARD 5-witness because (a) witness4 now formal 3-seed "
        "landing (Gate 1 satisfied), (b) witness5 adds 5th independent mechanism class (though at SMOKE scale). "
        "CG_META PROMOTION STILL GATED ON: 2nd FULL-scale mechanism-class witness with same result "
        "(e.g., Spoke 3 hippocampal at Wikipedia FULL N=10K, OR ABC composition at FULL scale). Currently ONLY "
        "witness4 (PPMI) is at FULL scale. "
        "REFUTATION CRITERION unchanged: any substrate-native structural mechanism that BEATS char-trigram bag "
        "on real-content retrieval at N>=1000 would refute the pattern (would carve scope to 'these 5 classes but not others'). "
        "STRATEGIC LOAD-BEARING: PPMI mechanism arc TERMINATES in supervised regime here. Spoke 3 hippocampal FULL "
        "scale-up is now load-bearing for CG_META promotion and for the bge-retire path. If Spoke 3 FULL also loses, "
        "pattern promotes to CG_META and Stage 2 retrieval-task-class framing may need re-evaluation."
    ),
    "aliases": [],
    "metadata": {
        "record_class": "methodology_rule",
        "term_class": "SUBSTRATE_NATIVE_MECHANISM_VS_SURFACE_BAG_PATTERN_SYNTHESIS",
        "cert_status": "measured_mechanism_standard_5_witness_gate_1_satisfied",
        "cert_class": "MM_STANDARD_5_WITNESS_GATE_1_SATISFIED_supersedes_MM_TENTATIVE_4_witness",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-03_ppmi_svd_wikipedia_FULL_FORMAL_GATE1_META_advance",
        "n_witnesses": 5,
        "n_witnesses_full_scale": 1,
        "n_mechanism_classes": 5,
        "GATE_1_status": "SATISFIED_bit_identical_formal_matches_preliminary",
        "witness_cells": [
            {
                "witness": 1,
                "mechanism_class": "concept_encoder_competitive_hebbian_WTA",
                "regime": "WordNet_N100_single_word_smoke",
                "delta": -0.120,
                "scale_tier": "smoke",
                "formal_scale": False
            },
            {
                "witness": 2,
                "mechanism_class": "modern_hopfield_dense_associative_readout",
                "regime": "WordNet_N100_single_word_smoke",
                "delta_vs_cosine": -0.107,
                "scale_tier": "smoke",
                "formal_scale": False
            },
            {
                "witness": 3,
                "mechanism_class": "VWFA_HRR_position_binding",
                "regime": "wikipedia_smoke_N500_multi_token",
                "delta": -0.078,
                "scale_tier": "smoke",
                "formal_scale": False
            },
            {
                "witness": 4,
                "mechanism_class": "PPMI_SVD_cooccurrence_matrix_factorization_ATL_hub_analog",
                "regime": "wikipedia_FULL_N10K_multi_token",
                "delta": -0.0239,
                "delta_at_smoke_precedent": 0.052,
                "reversal_from_smoke": True,
                "scale_tier": "full",
                "formal_scale": True,
                "GATE_1_witness": True
            },
            {
                "witness": 5,
                "mechanism_class": "hippocampal_DG_expansion_plus_CA3_completion_orthogonalization",
                "regime": "wikipedia_smoke_N500_multi_token",
                "delta": -0.709,
                "scale_tier": "smoke",
                "formal_scale": False,
                "flag": "HUGE_lose_HF_tier_new_mechanism_class_but_smoke_only"
            }
        ],
        "unifying_pattern": "structural substrate-native encoders LOSE to char-trigram bag on real-content retrieval; char-trigram bag gets free high-lexical-overlap signal that structural encoders do not add to OR actively dilute",
        "counter_examples_synthetic_regime": [
            "Spoke1_v3D_synthetic_supervised_clustering_ck_0p492_beats_baselines_2026-07-02",
            "Spoke2_Foldiak_trace_synthetic_supervised_clustering_ck_0p744_beats_Spoke1_2026-07-02"
        ],
        "counter_example_note": "counter-examples in SYNTHETIC SUPERVISED CLUSTERING regime; USER-locked mechanism-analog-is-not-task-analog predicts this; real-content unsupervised retrieval is different regime class",
        "expansion_criterion_to_CG_META": "2nd FULL-scale mechanism-class witness (e.g., Spoke 3 hippocampal at Wikipedia FULL N=10K, or ABC composition at FULL scale) with same result would promote to CG_META",
        "refutation_criterion": "any substrate-native structural mechanism that BEATS char-trigram bag on real-content retrieval at N>=1000 refutes the pattern",
        "strategic_implication": "PPMI arc terminates in supervised regime; Spoke 3 hippocampal FULL scale-up load-bearing for CG_META and bge-retire path",
        "supersedes": [
            "meta::T2/META_SUBSTRATE_NATIVE_STRUCTURAL_MECHANISMS_LOSE_TO_CHAR_TRIGRAM_BAG_ON_REAL_CONTENT_RETRIEVAL_AT_SCALE_MM_TENTATIVE_SYNTHESIS_4_witnesses_across_heterogeneous_mechanism_classes_witness1_substrate_content_v1_concept_encoder_WordNet_N100_r5_0p160_below_char_trigram_r5_0p280_witness2_component_C_modern_hopfield_readout_WordNet_N100_r5_0p05_below_cosine_0p16_below_char_trigram_0p280_witness3_VWFA_HRR_position_binding_wikipedia_smoke_N500_r5_0p776_below_char_trigram_r5_0p854_witness4_PPMI_SVD_wikipedia_FULL_N10K_r5_0p6791_below_char_trigram_r5_0p7030_scale_reversal_from_smoke_which_had_plus_0p052_lift_pattern_all_four_substrate_native_structural_mechanisms_concept_encoder_readout_position_binding_co_occurrence_matrix_factorization_fail_to_beat_surface_char_trigram_bag_on_real_content_retrieval_tasks_only_synthetic_supervised_clustering_regime_Spoke1_v3D_Spoke2_Foldiak_saw_them_win_mechanism_analog_is_not_task_analog_USER_LOCKED_holds_scope_witnesses_at_N100_N500_N10K_real_wordnet_and_real_wikipedia_common_failure_mode_char_trigram_bag_gets_free_high_lexical_overlap_signal_that_structural_encoders_do_not_add_to_or_actively_dilute_expansion_criterion_two_more_independent_mechanism_classes_e_g_hippocampal_pattern_separation_Spoke3_or_neuroscience_ABC_composition_at_FULL_scale_with_same_result_would_promote_to_CG_META_2026-07-03"
        ],
        "cites": [
            "witness_atom_PPMI_wikipedia_FULL_FORMAL_CG_HN_2026-07-03",
            "witness_atom_SPOKE3_HIPPO_wikipedia_smoke_HF_2026-07-03",
            "USER_locked_mechanism_analog_is_not_task_analog",
            "USER_locked_substrate_knows_almost_nothing"
        ],
        "cert_increment_delta": 1
    }
}


# ============= ATOM (c): SIBLING META TASK_CLASS_FIT advances Gate 1 SATISFIED =============
atom_meta_sibling_advanced = {
    "id": (
        "meta::T2/META_TASK_CLASS_FIT_STRUCTURAL_MECHANISMS_WIN_VSA_NATIVE_LOSE_OPEN_DOMAIN_RETRIEVAL_"
        "MM_STANDARD_5_WITNESS_GATE_1_SATISFIED_supersedes_MIXED_CAVEATS_prior_"
        "PPMI_FULL_FORMAL_3seed_landed_bit_identical_to_preliminary_within_plus_minus_0p00_of_preliminary_"
        "Gate_1_blocker_CG_META_promotion_CLEARED_"
        "LOSE_side_retrieval_witness_formalized_PPMI_r5_0p6791_vs_char_trigram_r5_0p7030_CG_tier_at_N10K_"
        "WIN_side_VSA_analogy_HP_r1_0p8613_composition_multi_hop_all_CG_or_MB_"
        "regime_caveats_on_WIN_side_witness4_HP1_ceiling_miss_and_witness5_saturation_ceiling_UNRESOLVED_"
        "CG_META_promotion_now_gated_ONLY_on_WIN_side_regime_caveat_resolution_"
        "e_g_hop_degradation_curve_measurement_or_HP1_ceiling_regime_probe_"
        "task_class_pattern_recurrent_unbind_plus_cleanup_canonical_FHRR_HRR_holds_across_4_task_classes_analogy_composition_episodic_multi_hop_"
        "2026_07_03"
    ),
    "name": "META TASK_CLASS_FIT (MM_STANDARD 5-witness; GATE 1 SATISFIED; CG_META promotion now gated ONLY on WIN-side regime caveat resolution)",
    "corpus": "meta",
    "tier": "T2",
    "kind": "methodology_rule_pattern_synthesis",
    "description": (
        "META synthesis (MM_STANDARD, 5 witnesses; supersedes prior MM_STANDARD_5_WITNESS_MIXED_CAVEATS "
        "with Gate 1 satisfied annotation): substrate-native structural mechanisms WIN on VSA-native "
        "canonical tasks (recurrent unbind + cleanup: analogy, composition, episodic recall, multi-hop) "
        "and LOSE on open-domain real-content retrieval tasks. Task-class fit is the predictor. "
        "GATE 1 STATUS UPDATE (this atomization): "
        "PPMI/SVD Wikipedia FULL N=10K formal 3-seed landed 2026-07-03T03:30Z with r5=0.6791 (bit-identical "
        "to preliminary heartbeat 0.6791; delta 0.00, well within +/-0.02 tolerance). Gate 1 blocker for "
        "CG_META promotion is now CLEARED. LOSE-side retrieval witness now at CG-tier at FULL scale. "
        "WITNESSES (unchanged): "
        "Witness 1: VSA analogy_HP r1=0.8613 vs char_trigram r1<0.05 (WIN; z=72sigma). "
        "Witness 2: VSA_composition CG_MB. "
        "Witness 3: VSA_analogy K_DIST sweep resolved HP3 MB_caveat at K=20; gap +0.175. "
        "Witness 4: VSA episodic recall (regime caveat: HP1 ceiling miss). "
        "Witness 5: VSA multi-hop reasoning r1=1.000 saturated (regime caveat: hop-degradation curve unmeasured). "
        "LOSE-side witnesses (composed with parent META): concept_encoder, hopfield, VWFA, PPMI FULL (all lose on retrieval). "
        "REMAINING GATE for CG_META (after Gate 1 satisfied): WIN-side regime caveat resolution. "
        "Either: (a) hop-degradation curve measurement at witness 5 that lands within cleanup_capacity K_eff, "
        "OR (b) HP1 ceiling-regime probe at witness 4 that clears the ceiling. Either would promote MM_STANDARD -> CG_META. "
        "TASK-CLASS PATTERN unchanged: recurrent unbind + cleanup canonical FHRR/HRR (Plate 1995, Eliasmith 2005 Spaun, "
        "Frady/Sommer 2020) mechanism WINS across 4 task classes; open-domain retrieval LOSES. "
        "AUDITOR NOTE: sibling atom advances from MIXED_CAVEATS to GATE_1_SATISFIED tier; CG_META promotion is "
        "closer but still requires WIN-side regime caveat resolution before advance."
    ),
    "aliases": [],
    "metadata": {
        "record_class": "methodology_rule",
        "term_class": "TASK_CLASS_FIT_STRUCTURAL_MECHANISMS_VSA_NATIVE_VS_OPEN_DOMAIN_RETRIEVAL",
        "cert_status": "measured_mechanism_standard_5_witness_gate_1_satisfied",
        "cert_class": "MM_STANDARD_5_WITNESS_GATE_1_SATISFIED_supersedes_MIXED_CAVEATS",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-03_ppmi_svd_wikipedia_FULL_FORMAL_sibling_advance",
        "GATE_1_status": "SATISFIED_bit_identical_formal_matches_preliminary",
        "GATE_1_prior_blocker": "PPMI FULL 10K formal landing (now cleared)",
        "remaining_blockers_for_CG_META": [
            "witness4_HP1_ceiling_miss_regime_caveat_unresolved",
            "witness5_saturation_ceiling_hop_degradation_curve_unmeasured"
        ],
        "promotion_path_to_CG_META": "resolve at least one WIN-side regime caveat (hop-degradation curve OR HP1 ceiling probe) -> CG_META",
        "n_witnesses_win_side": 5,
        "n_witnesses_lose_side_via_parent_META": 5,
        "task_class_pattern": "recurrent_unbind_plus_cleanup_canonical_FHRR_HRR_wins_on_VSA_native_task_classes_loses_on_open_domain_retrieval",
        "supersedes": [
            "meta::T2/META_TASK_CLASS_FIT_STRUCTURAL_MECHANISMS_WIN_VSA_NATIVE_LOSE_OPEN_DOMAIN_RETRIEVAL_MM_STANDARD_5_WITNESS_MIXED_CAVEATS_witness5_VSA_multi_hop_reasoning_r1_1p000_saturated_all_HP_gates_clean_but_ceiling_regime_miss_hop_degradation_curve_unmeasured_K_eff_15_SNR_11p68_far_above_cleanup_capacity_witness_STRENGTHENS_task_class_pattern_recurrent_unbind_plus_cleanup_canonical_FHRR_HRR_Plate_1995_Eliasmith_2005_Spaun_Frady_Sommer_2020_mechanism_5th_witness_across_4_distinct_task_classes_analogy_composition_episodic_multi_hop_HOLD_at_MM_STANDARD_CG_META_promotion_still_blocked_on_Gate_1_PPMI_FULL_10K_formal_landing_and_now_witness4_and_witness5_carry_regime_caveats_HP1_ceiling_miss_and_saturation_ceiling_respectively_2026_07_03"
        ],
        "cites": [
            "witness_atom_PPMI_wikipedia_FULL_FORMAL_CG_HN_2026-07-03_gate_1_witness",
            "parent_META_SUBSTRATE_NATIVE_STRUCTURAL_MECHANISMS_LOSE_5_witness_2026-07-03"
        ],
        "cert_increment_delta": 0,
        "cert_increment_delta_note": "no new cert increment (Gate 1 was pending-blocker on prior MM_STANDARD; advance is annotation-level clearing, not new witness)"
    }
}


def a5_append(path, atom):
    """Atomic append: tmp write + fsync + os.replace + verify-load."""
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_atomize_", suffix=".jsonl")
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
    found = False
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            n_lines += 1
            if atom["id"] in line:
                found = True
    if not found:
        raise RuntimeError(f"verify-load failed: atom id not found in {path}")
    return n_lines


def ledger_append(atom, session_tag, ledger_path=CERT_LEDGER):
    entry = {
        "ts": TS,
        "ts_iso": TS_ISO,
        "atom_id": atom["id"],
        "corpus": atom["corpus"],
        "cert_status": atom["metadata"].get("cert_status"),
        "cert_class": atom["metadata"].get("cert_class"),
        "cert_increment_delta": atom["metadata"].get("cert_increment_delta", 0),
        "verified_off_data": atom["metadata"].get("verified_off_data", False),
        "cell_sha": atom["metadata"].get("cell_sha"),
        "atomized_by": atom["metadata"].get("atomized_by"),
        "landed_VET_session": session_tag,
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
    print(f"[atomize] ts_iso={TS_ISO} commit={COMMIT}")
    session_tag = "2026-07-03_ppmi_svd_wikipedia_FULL_FORMAL_GATE1_satisfied_and_META_advances"

    n_math = a5_append(MATH_ATOMS, atom_hn_formal)
    print(f"[atomize] MATH (a) FORMAL CG_HN appended; total math lines={n_math}")
    ledger_append(atom_hn_formal, session_tag)

    n_meta1 = a5_append(META_ATOMS, atom_meta_parent_advanced)
    print(f"[atomize] META (b) parent MM_STANDARD_5_WITNESS_GATE1 appended; total meta lines={n_meta1}")
    ledger_append(atom_meta_parent_advanced, session_tag)

    n_meta2 = a5_append(META_ATOMS, atom_meta_sibling_advanced)
    print(f"[atomize] META (c) sibling GATE1_SATISFIED appended; total meta lines={n_meta2}")
    ledger_append(atom_meta_sibling_advanced, session_tag)

    print("[atomize] DONE 3 atoms + 3 ledger entries; A5-gated (tmp+os.replace+verify-load)")
