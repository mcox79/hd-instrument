"""
A5-gated atomization for landed VET (PRELIMINARY, 2/3 seeds) of
exp_substrate_wikipedia_ppmi_svd_scale_up_full_2026_07_03.

Skunkworks landed-VET, off-disk recompute per Fix#28.

REMOTE HEARTBEAT (SSH-pulled from marsh@home; local `data/` dir has STALE local SMOKE,
NOT the FULL landing; USER-locked corpus-completeness remote-vs-local gotcha applies):

  Pass 1 (2026-07-03T02:39:49Z; seed 1):
    ARM_PPMI_SVD_WIKIPEDIA_N10K   r@5=0.6791  wall=416.5s
    ARM_CHAR_TRIGRAM_WIKIPEDIA_N10K r@5=0.7030  wall=14.97s
    ARM_RANDOM_BASELINE_N10K       r@5=0.0003  wall=6.56s
  Pass 2 (2026-07-03T02:47:03Z; seed 2):
    ARM_PPMI_SVD_WIKIPEDIA_N10K   r@5=0.6791  wall=412.8s
    ARM_CHAR_TRIGRAM_WIKIPEDIA_N10K r@5=0.7030  wall=15.62s
    ARM_RANDOM_BASELINE_N10K       r@5=0.0001  wall=6.60s
  Seed 3 KILLED mid-PPMI-arm at ~1200s ceiling (~02:52Z); no seed-3 heartbeat.

VERDICT: PRELIMINARY_CG_HONEST_NEGATIVE
  PPMI r@5 = 0.6791, char-trigram r@5 = 0.7030, delta = -0.0239.
  Direction REVERSES SMOKE precedent (SMOKE N=500: PPMI +0.052 above char-trigram).

DEFENSIBILITY OF 2-SEED CG:
  - PPMI r@5 bit-identical 0.6791 across 2 seeds. Char-trigram bit-identical 0.7030.
    Encoders are deterministic (encode uses fixed blake2b codebook / fixed PPMI fit).
    Seed only varies random arm; 3rd seed adds ZERO NEW INFO for main claim.
    Precedent: SMOKE metrics.json showed identical arms_differ_digests across seeds,
    confirming deterministic behavior.
  - Baseline in-band: chance @ N=10K = 1/10000 = 0.0001; observed 0.0001-0.0003 = in-band.
  - Direction robust: PPMI < char-trigram in BOTH landed passes.
  - HOWEVER: formal 3-seed metrics.json artifact is MISSING (killed pre-write).
    Preliminary tag reflects audit-trail gap, NOT epistemic uncertainty about direction.

CROSS-ARC SYMMETRIC-VERIFY vs prior atoms:
  - SMOKE CG (Wikipedia PPMI N=500, r5=0.906, +0.052): NOT superseded; still holds at
    smoke scale. This FULL result AMENDS the smoke CG with scope narrowing: mechanism
    lift does NOT survive at 20x scale.
  - V2A WordNet FULL landed MB (+0.06 -> +0.012, NARROWED but stayed positive).
    Wikipedia PPMI FULL FLIPPED to negative at more extreme scale + different task class
    (multi-token title-body vs single-word synonym retrieval).
  - substrate_content_v1 HF (2026-07-02): concept_encoder mechanism itself lost to
    char-trigram at N=100 WordNet.
  - VWFA HRR wikipedia smoke HF (2026-07-03): VWFA lost to char-trigram at N=500.
  => Pattern (now 4 witnesses): substrate-native concept/composition mechanisms fail to
     beat char-trigram bag on real-content retrieval at scale, even when they win at
     small scale. Warrants MM_TENTATIVE_SYNTHESIS meta atom.

DIRECTOR OVER-CLAIM MITIGATION: Director spawn prompt framed as "3-witness META
promotion candidate". Auditor cross-check: 4 candidate witnesses actually (substrate_content_v1,
component_C_hopfield, VWFA_wikipedia_smoke, PPMI_wikipedia_full), but they span different
mechanism classes (concept encoder, readout, position-binding, PPMI/SVD). The unifying
claim is at a HIGHER level (substrate-native structural mechanisms lose to surface bag).
Filing META as MM_TENTATIVE reflects this heterogeneity + real-content requirement.

Three atoms filed:
  (a) math CG_HONEST_NEGATIVE PRELIMINARY on PPMI Wikipedia FULL N=10K (2/3 seeds heartbeat)
  (b) meta MM_TENTATIVE_SYNTHESIS on substrate-native mechanisms lose to surface bag at scale
  (c) meta DISCIPLINE_META on cell-quality (timeout budget underestimate + no per-seed checkpoint)
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
COMMIT = "741f8ab2f"

# ============= ATOM (a): PRELIMINARY_CG_HONEST_NEGATIVE PPMI FULL Wikipedia N=10K =============
atom_hn = {
    "id": "math::T3/EXP_substrate_wikipedia_ppmi_svd_scale_up_FULL_N10K_PRELIMINARY_CG_HONEST_NEGATIVE_2of3_seeds_heartbeat_only_metrics_json_MISSING_killed_mid_seed3_at_1200s_timeout_ceiling_PPMI_r5_0p6791_bit_identical_across_2_seeds_deterministic_encoder_char_trigram_r5_0p7030_bit_identical_2_seeds_delta_PPMI_minus_char_trigram_neg_0p0239_DIRECTION_REVERSES_SMOKE_N500_precedent_which_showed_plus_0p0520_random_baseline_in_band_0p0001_0p0003_at_N10K_chance_0p0001_scale_from_smoke_shrinks_PPMI_by_neg_0p2269_0p906_to_0p6791_shrinks_char_trigram_by_neg_0p151_0p854_to_0p703_PPMI_more_scale_sensitive_than_char_trigram_bag_encoding_wall_PPMI_413s_char_trigram_15s_random_7s_per_seed_defensibility_2seed_deterministic_encoder_arms_differ_digests_identical_smoke_precedent_seed_adds_zero_info_for_main_claim_but_formal_3seed_metrics_json_MISSING_hence_PRELIMINARY_tag_reflects_audit_trail_gap_not_epistemic_uncertainty_scope_TIGHT_SUPERVISED_wikipedia_title_to_body_N10K_body_cap_800_n_dim_2048_supersedes_None_amends_smoke_CG_with_scale_narrowing_context_composes_with_char_trigram_FULL_MB_precedent_same_day_2026-07-03",
    "name": "EXP substrate_wikipedia_ppmi_svd_scale_up FULL PRELIMINARY_CG_HONEST_NEGATIVE (2/3 seeds heartbeat; PPMI 0.6791 < char-trigram 0.7030 at N=10K; SMOKE +0.052 REVERSES to -0.024 at 20x scale)",
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Experiment record: exp_substrate_wikipedia_ppmi_svd_scale_up_full_2026_07_03. Cell scaled PPMI/SVD "
        "substrate-native ATL-hub-analog encoder from N=500 SMOKE to N=10K FULL on real Wikipedia title-to-body "
        "retrieval. Remote run: 2026-07-03T02:32Z start; 2 of 3 seeds landed heartbeat before timeout kill "
        "at 02:52Z (1200s ceiling; seed 3 killed mid-PPMI-arm at ~440s in). metrics.json NOT WRITTEN "
        "(cell writes final metrics only at end). Recovery: SSH-pulled _heartbeat.jsonl from marsh@home; "
        "local data/ dir had STALE local smoke (N=500, HP_PASS, 02:18Z) that would have MISLED verification "
        "if not cross-checked -- USER-locked corpus-completeness remote-vs-local gotcha caught by SSH pull. "
        "PRELIMINARY_CG_HONEST_NEGATIVE tier: PPMI r@5 = 0.6791 (BIT-IDENTICAL across seeds 1 and 2, "
        "encoding wall ~413s/seed), char-trigram r@5 = 0.7030 (bit-identical), random r@5 in [0.0001, 0.0003] "
        "vs chance 0.0001 at N=10K (baseline in-band). Delta PPMI - char-trigram = -0.0239. DIRECTION "
        "REVERSES SMOKE N=500 precedent (+0.052). Scale from smoke: PPMI shrank -0.227 (0.906 -> 0.6791); "
        "char-trigram shrank -0.151 (0.854 -> 0.703). PPMI is MORE scale-sensitive than char-trigram bag, "
        "which explains the flip. 2-seed defensibility: encoders are deterministic (SMOKE metrics.json "
        "showed identical arms_differ_digests across all 3 SMOKE seeds); seed only varies random arm; "
        "3rd seed for PPMI/char-trigram adds zero new information for the main claim. PRELIMINARY tag "
        "reflects the fact that formal 3-seed metrics.json artifact is MISSING (killed pre-write), which "
        "is an audit-trail gap not an epistemic uncertainty about direction. Recommend re-dispatch with "
        "timeout=1800s + per-seed checkpoint discipline for formal audit trail cleanliness. SCOPE TIGHT: "
        "SUPERVISED Wikipedia title-body retrieval, N=10K, body_cap=800, n_dim=2048, seeds 11/17/23. "
        "NOT a claim that PPMI/SVD is 'a bad encoder in general'. NOT a claim that substrate cannot learn "
        "Wikipedia content -- it demonstrably CANNOT (USER-locked substrate-knows-nothing framing). This "
        "IS a claim that on this task class + scale, PPMI/SVD does not lift above surface bag, so the "
        "'ATL-hub-analog' mechanism-lift interpretation does not survive scale. AMENDS (not supersedes) "
        "the smoke CG (r5=0.906) with scale-narrowing context: mechanism lift was scale-artifact of small-N."
    ),
    "aliases": [],
    "metadata": {
        "record_class": "experiment_record",
        "term_class": "PROCESS_KNOWLEDGE_NON_MATH",
        "metric_type": "recall_at_5_wikipedia_title_to_body_retrieval",
        "experiment_path": "experiments/exp_substrate_wikipedia_ppmi_svd_scale_up_full_2026-07-03.py",
        "prereg_path": "preregs/2026-07-03_substrate_wikipedia_ppmi_svd_scale_up_full.md",
        "metrics_paths": [
            "REMOTE:C:/dev/hd-instrument/data/exp_substrate_wikipedia_ppmi_svd_scale_up_full_2026_07_03/_heartbeat.jsonl"
        ],
        "cell_sha": COMMIT,
        "remote_run_id": None,
        "verdict": "PRELIMINARY_CG_HONEST_NEGATIVE_PPMI_LOSES_TO_CHAR_TRIGRAM_AT_SCALE",
        "run_mode": "full",
        "provenance_quality": "PRELIMINARY_CG_HONEST_NEGATIVE",
        "relevance_tier": "HIGH",
        "era": "STAGE_2_CONCEPT_ENCODER_ARC_2026-07-02",
        "cert_status": "chain_grade_honest_negative_preliminary",
        "cert_class": "ppmi_svd_wikipedia_encoder_loses_to_char_trigram_at_N10K_scale_reversal_from_smoke_supervised_regime",
        "verified_off_data": True,
        "verification_method": "SSH-pull remote heartbeat.jsonl from marsh@home; sync-lag bypass; local data/ dir had STALE smoke",
        "atomized_by": "skunkworks_landed_VET_2026-07-03_ppmi_svd_wikipedia_FULL_HN",
        "cert_ts": TS_ISO,
        "n_seeds_configured": 3,
        "n_seeds_landed": 2,
        "n_seeds_killed_by_timeout": 1,
        "seeds_configured": [11, 17, 23],
        "n_dim": 2048,
        "N_articles": 10000,
        "cardinality_ok": False,
        "cardinality_ok_reason": "6 of 9 heartbeat units landed; 3 units (seed-3 all-arms) killed by timeout",
        "arms_differ_verified_via_smoke_precedent": True,
        "per_seed_landed_ppmi_r5": [0.6791, 0.6791],
        "per_seed_landed_char_trigram_r5": [0.7030, 0.7030],
        "per_seed_landed_random_r5": [0.0003, 0.0001],
        "delta_ppmi_minus_char_trigram_at_N10K": -0.0239,
        "delta_ppmi_minus_char_trigram_at_N500_smoke_precedent": 0.0520,
        "direction_reversal_from_smoke_to_full": True,
        "ppmi_shrink_smoke_to_full": -0.2269,
        "char_trigram_shrink_smoke_to_full": -0.1510,
        "ppmi_more_scale_sensitive_than_char_trigram": True,
        "baseline_in_band_check": {
            "chance_r5_at_N10K": 0.0001,
            "observed_range": [0.0001, 0.0003],
            "band_max": 0.0005,
            "in_band": True
        },
        "encoder_deterministic_evidence": (
            "SMOKE metrics.json (data/exp_substrate_wikipedia_ppmi_svd_scale_up_full_2026_07_03/metrics.json, "
            "N=500 local smoke run) showed arms_differ_digests bit-identical for PPMI/char-trigram across "
            "all 3 seeds. FULL heartbeat shows PPMI r5 and char-trigram r5 bit-identical across seeds 1-2. "
            "Encoders are seed-independent by construction (fixed blake2b codebook for char-trigram; "
            "fixed PPMI fit on body corpus for PPMI). Seed only varies random baseline arm."
        ),
        "wall_time_summary_per_seed": {
            "PPMI_arm_s": 413,
            "char_trigram_arm_s": 15,
            "random_arm_s": 7,
            "total_per_seed_s": 435,
            "timeout_ceiling_s": 1200,
            "expected_3_seed_wall_s": 1305,
            "cell_author_ppmi_wall_underestimate_factor": 3.0
        },
        "auditor_framing_correction_vs_director_spawn": (
            "Director spawn framed this as '3rd witness for META synthesis about substrate-native concept "
            "mechanisms losing at scale'. Auditor cross-check: prior HN witnesses span DIFFERENT mechanism "
            "classes (substrate_content_v1 concept_encoder WordNet; component_C_hopfield_readout WordNet; "
            "VWFA_HRR_position_binding_wikipedia_smoke). PPMI Wikipedia FULL is a NEW witness at NEW class "
            "(unsupervised co-occurrence-based encoder) and NEW scale (N=10K, hardest test). The unifying "
            "claim is at a HIGHER level than 'concept mechanisms fail' -- it is 'substrate-native structural "
            "mechanisms fail to beat surface char-trigram bag on real-content retrieval at scale'. Filing "
            "META synthesis as MM_TENTATIVE (not CG) because witnesses span heterogeneous mechanism classes "
            "and only one is FULL-scale."
        ),
        "supersedes": None,
        "amends": [
            "math::T3/EXP_substrate_wikipedia_ppmi_svd_baseline_SMOKE_CG_MEASURED_BOUND_3seed_N500 (r5=0.906 SMOKE CG stays valid at N=500; amended with scale-narrowing context that mechanism-lift does NOT survive at 20x scale; smoke CG cannot be extrapolated to FULL regime)"
        ],
        "composes_with": [
            "math::T3/EXP_substrate_wikipedia_char_trigram_scale_up_full_N10K_MEASURED_BOUND (same-day char-trigram FULL landing r5=0.703; provides direct reference)",
            "math::T3/EXP_substrate_concept_encoder_substrate_content_v1_CG_HONEST_NEGATIVE (WordNet N=100 HN witness 1)",
            "math::T3/EXP_substrate_concept_encoder_component_C_modern_hopfield_readout_CG_HONEST_NEGATIVE (Hopfield readout HN witness 2)",
            "math::T3/witness_VWFA_HRR_position_binding_wikipedia_smoke_CG_HONEST_NEGATIVE (VWFA smoke HN witness 3)"
        ],
        "cites": [
            "Fix_28_verify_per_arm_off_disk_not_orchestrator_summary",
            "USER_locked_substrate_knows_almost_nothing_2026-07-02",
            "USER_locked_corpus_completeness_remote_vs_local_half_data",
            "STANDARD_SSH_VET_macro_2026-07-01"
        ],
        "revival_criterion": (
            "Re-dispatch with (a) timeout=1800s, (b) per-seed checkpoint (metrics.json written after each seed), "
            "(c) same seeds 11/17/23 to reproduce bit-identical PPMI r5. If landed 3-seed FULL confirms "
            "PPMI r5 = 0.6791 exact + char-trigram r5 = 0.7030 exact, promote from PRELIMINARY_CG_HONEST_NEGATIVE "
            "to CG_HONEST_NEGATIVE (drop preliminary tag). No expected direction change; extra latency ~30 min "
            "buys formal audit-trail cleanliness only."
        ),
        "cert_increment_delta": 1
    }
}

# ============= ATOM (b): META MM_TENTATIVE_SYNTHESIS substrate-native mechanisms lose to surface bag at scale =============
atom_meta_synth = {
    "id": "meta::T2/META_SUBSTRATE_NATIVE_STRUCTURAL_MECHANISMS_LOSE_TO_CHAR_TRIGRAM_BAG_ON_REAL_CONTENT_RETRIEVAL_AT_SCALE_MM_TENTATIVE_SYNTHESIS_4_witnesses_across_heterogeneous_mechanism_classes_witness1_substrate_content_v1_concept_encoder_WordNet_N100_r5_0p160_below_char_trigram_r5_0p280_witness2_component_C_modern_hopfield_readout_WordNet_N100_r5_0p05_below_cosine_0p16_below_char_trigram_0p280_witness3_VWFA_HRR_position_binding_wikipedia_smoke_N500_r5_0p776_below_char_trigram_r5_0p854_witness4_PPMI_SVD_wikipedia_FULL_N10K_r5_0p6791_below_char_trigram_r5_0p7030_scale_reversal_from_smoke_which_had_plus_0p052_lift_pattern_all_four_substrate_native_structural_mechanisms_concept_encoder_readout_position_binding_co_occurrence_matrix_factorization_fail_to_beat_surface_char_trigram_bag_on_real_content_retrieval_tasks_only_synthetic_supervised_clustering_regime_Spoke1_v3D_Spoke2_Foldiak_saw_them_win_mechanism_analog_is_not_task_analog_USER_LOCKED_holds_scope_witnesses_at_N100_N500_N10K_real_wordnet_and_real_wikipedia_common_failure_mode_char_trigram_bag_gets_free_high_lexical_overlap_signal_that_structural_encoders_do_not_add_to_or_actively_dilute_expansion_criterion_two_more_independent_mechanism_classes_e_g_hippocampal_pattern_separation_Spoke3_or_neuroscience_ABC_composition_at_FULL_scale_with_same_result_would_promote_to_CG_META_2026-07-03",
    "name": "META SUBSTRATE_NATIVE_STRUCTURAL_MECHANISMS_LOSE_TO_CHAR_TRIGRAM_BAG_ON_REAL_CONTENT_RETRIEVAL_AT_SCALE (MM_TENTATIVE_SYNTHESIS, 4 witnesses heterogeneous mechanism classes)",
    "corpus": "meta",
    "tier": "T2",
    "kind": "methodology_rule_pattern_synthesis",
    "description": (
        "META synthesis (MM_TENTATIVE, 4 witnesses across heterogeneous mechanism classes): substrate-native "
        "structural mechanisms designed to add signal above char-trigram surface bag consistently FAIL to "
        "beat char-trigram bag on real-content retrieval tasks, even when they succeed on synthetic supervised "
        "clustering regimes (Spoke1 v3-D, Spoke2 Foldiak). "
        "Witness 1 (2026-07-02): substrate_content_v1 concept_encoder at WordNet N=100 synonym retrieval; "
        "r5=0.160 < char_trigram r5=0.280 (delta -0.120). "
        "Witness 2 (2026-07-03): component_C_modern_hopfield_readout at WordNet N=100; r5=0.05 < cosine r5=0.16 "
        "< char_trigram r5=0.280 (delta -0.107 vs cosine baseline). "
        "Witness 3 (2026-07-03): VWFA_HRR_position_binding at Wikipedia SMOKE N=500 title-body retrieval; "
        "r5=0.776 < char_trigram r5=0.854 (delta -0.078). "
        "Witness 4 (2026-07-03, THIS LANDING): PPMI/SVD at Wikipedia FULL N=10K; r5=0.6791 < char_trigram "
        "r5=0.7030 (delta -0.0239). Notable: PPMI WAS +0.052 above char-trigram at SMOKE N=500; REVERSED "
        "at 20x scale. "
        "PATTERN: all four witnesses are substrate-native structural mechanisms (concept encoder, dense "
        "associative readout, position-binding, co-occurrence matrix factorization). All fail to beat "
        "surface char-trigram bag on real-content retrieval. Common failure mode hypothesis: char-trigram "
        "bag gets 'free' high lexical-overlap signal from real-content queries (multi-token or single-word) "
        "that structural encoders either do not add to OR actively dilute by compressing to lower effective "
        "rank. USER-LOCKED 'mechanism analog is NOT task analog' holds: brain-analog mechanisms passing "
        "synthetic supervised regime does NOT transfer to real-content unsupervised regime. "
        "SCOPE: 4 witnesses at N in [100, 500, 10000] real-content retrieval (WordNet lexicon + real Wikipedia). "
        "MM_TENTATIVE tier because (a) witnesses span heterogeneous mechanism classes -- not a single "
        "mechanism-class failure -- so unifying claim is at a HIGHER abstraction level (structural encoders "
        "vs surface bag); (b) only 1 of 4 witnesses is at FULL scale (PPMI Wikipedia N=10K); (c) does NOT "
        "yet include Spoke 3 hippocampal pattern-separation, which is designed exactly to avoid this failure "
        "mode via one-shot orthogonalization -- IF Spoke 3 also fails, promote to CG_META. "
        "EXPANSION CRITERION TO CG_META: witness at 2 more independent mechanism classes (e.g., Spoke 3 "
        "hippocampal pattern-separation OR neuroscience A-B-C composition) at FULL scale with same result. "
        "REFUTATION CRITERION: any substrate-native structural mechanism that BEATS char-trigram bag on "
        "real-content retrieval at N>=1000 would refute the pattern (would carve scope to 'these 4 classes "
        "but not others'). "
        "STRATEGIC LOAD-BEARING: this pattern is why Spoke 3 hippocampal is now load-bearing for the "
        "bge-retire path; if pattern holds through Spoke 3, need to re-frame Stage 2 goals."
    ),
    "aliases": [],
    "metadata": {
        "record_class": "methodology_rule",
        "term_class": "SUBSTRATE_NATIVE_MECHANISM_VS_SURFACE_BAG_PATTERN_SYNTHESIS",
        "cert_status": "measured_mechanism_tentative_synthesis",
        "cert_class": "MM_TENTATIVE_SYNTHESIS_4_witnesses_heterogeneous_mechanism_classes",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-03_ppmi_svd_wikipedia_FULL_META_synth",
        "witness_cells": [
            {
                "witness": 1,
                "cell": "exp_substrate_concept_encoder_substrate_content_v1",
                "mechanism_class": "concept_encoder_competitive_hebbian_WTA_k_0p02",
                "regime": "WordNet_synonym_retrieval_N100_single_word",
                "structural_r5": 0.160,
                "char_trigram_r5": 0.280,
                "delta": -0.120,
                "scale": "smoke_N100"
            },
            {
                "witness": 2,
                "cell": "exp_substrate_concept_encoder_component_C_modern_hopfield_readout_2026_07_03",
                "mechanism_class": "modern_hopfield_dense_associative_readout_softmax_beta_4_8",
                "regime": "WordNet_synonym_retrieval_N100_single_word",
                "structural_r5": 0.05,
                "cosine_baseline_r5": 0.160,
                "char_trigram_r5": 0.280,
                "delta_vs_cosine": -0.107,
                "scale": "smoke_N100"
            },
            {
                "witness": 3,
                "cell": "witness_VWFA_HRR_position_binding_wikipedia_smoke_2026_07_03",
                "mechanism_class": "VWFA_HRR_position_binding_scales_1_2_3_4",
                "regime": "wikipedia_title_to_body_smoke_N500_multi_token",
                "structural_r5": 0.776,
                "char_trigram_r5": 0.854,
                "delta": -0.078,
                "scale": "smoke_N500"
            },
            {
                "witness": 4,
                "cell": "exp_substrate_wikipedia_ppmi_svd_scale_up_full_2026_07_03",
                "mechanism_class": "PPMI_SVD_co_occurrence_matrix_factorization_ATL_hub_analog",
                "regime": "wikipedia_title_to_body_FULL_N10K_multi_token",
                "structural_r5": 0.6791,
                "char_trigram_r5": 0.7030,
                "delta": -0.0239,
                "delta_at_smoke_precedent": 0.052,
                "reversal_from_smoke": True,
                "scale": "full_N10K_hardest_test_so_far"
            }
        ],
        "unifying_pattern": "structural substrate-native encoders LOSE to char-trigram bag on real-content retrieval; char-trigram bag gets free high-lexical-overlap signal that structural encoders do not add to OR actively dilute",
        "counter_examples_synthetic_regime": [
            "Spoke1_v3D_synthetic_supervised_clustering_ck_0p492_beats_baselines_2026-07-02",
            "Spoke2_Foldiak_trace_synthetic_supervised_clustering_ck_0p744_beats_Spoke1_by_0p252_2026-07-02"
        ],
        "counter_example_note": "counter-examples exist in SYNTHETIC SUPERVISED CLUSTERING regime; USER-locked 'mechanism analog is NOT task analog' predicts this; real-content unsupervised retrieval is different regime class",
        "expansion_criterion_to_CG_META": "witness at 2 more independent mechanism classes (e.g., Spoke 3 hippocampal pattern-separation via CA3/DG orthogonalization; neuroscience A-B-C composition) at FULL scale with same result would promote to CG_META",
        "refutation_criterion": "any substrate-native structural mechanism that BEATS char-trigram bag on real-content retrieval at N>=1000 refutes the pattern; would carve scope to 'these 4 classes but not others'",
        "strategic_implication": "Spoke 3 hippocampal pattern-separation is now the LOAD-BEARING bge-retire path; if pattern holds through Spoke 3 also, Stage 2 goals need reframing (retrieval task class may itself be wrong lens for evaluating substrate-native encoders)",
        "cites": [
            "witness_atom_PPMI_wikipedia_FULL_HN_2026-07-03",
            "witness_atom_substrate_content_v1_HF_2026-07-02",
            "witness_atom_component_C_hopfield_HF_2026-07-03",
            "witness_atom_VWFA_wikipedia_smoke_HF_2026-07-03",
            "USER_locked_mechanism_analog_is_not_task_analog_2026-07-02",
            "USER_locked_substrate_knows_almost_nothing_2026-07-02"
        ],
        "cert_increment_delta": 1
    }
}

# ============= ATOM (c): META DISCIPLINE cell-quality (timeout + no per-seed checkpoint) =============
atom_meta_discipline = {
    "id": "meta::T2/DISCIPLINE_META_FULL_CELL_TIMEOUT_BUDGET_MUST_INCLUDE_3X_SAFETY_MARGIN_ON_MAIN_ARM_WALL_AND_PER_SEED_CHECKPOINT_METRICS_JSON_MANDATORY_evidenced_2026_07_03_PPMI_wikipedia_FULL_timeout_kill_cell_author_estimated_PPMI_fit_wall_at_140s_from_smoke_N500_actual_at_N10K_was_413s_underestimate_factor_3_0_x_timeout_ceiling_1200s_3_seeds_wall_1305s_seed_3_killed_pre_completion_metrics_json_not_written_2_of_3_seeds_landed_only_via_heartbeat_recovery_rule_smoke_arm_wall_extrapolation_to_FULL_must_scale_conservatively_N_full_over_N_smoke_times_1_5_safety_and_per_seed_checkpoint_write_metrics_json_after_each_seed_not_only_at_end_composes_with_SH_4_per_seed_hardening_and_long_cells_checkpoint_resume_2026-07-03",
    "name": "DISCIPLINE_META FULL cell timeout budget must include 3x safety margin on main-arm wall + per-seed metrics.json checkpoint mandatory (evidenced by PPMI Wikipedia FULL timeout kill 2026-07-03)",
    "corpus": "meta",
    "tier": "T2",
    "kind": "methodology_rule_cell_quality",
    "description": (
        "META discipline rule (CG tier because two-part rule with concrete evidence and one-line fix): "
        "FULL cell timeout budgets must include (a) 3x safety margin over expected main-arm wall extrapolated "
        "from smoke to FULL scale, AND (b) per-seed metrics.json checkpoint (write metrics.json after each "
        "seed completes, NOT only at end). "
        "EVIDENCED: exp_substrate_wikipedia_ppmi_svd_scale_up_full_2026_07_03 (2026-07-03T02:52Z timeout kill). "
        "Cell-author estimated PPMI fit_wall from SMOKE N=500 at ~140s; actual at FULL N=10K was 413s (underestimate "
        "factor 3.0x). Timeout ceiling was 1200s; 3-seed wall was 1305s; seed 3 killed pre-completion. "
        "metrics.json NOT WRITTEN (cell writes final only at end); 2 of 3 landed seeds recoverable ONLY via "
        "heartbeat.jsonl SSH-pull. FORMAL audit trail is incomplete; PRELIMINARY tag on landing atom. "
        "RULE: (i) SMOKE-to-FULL wall extrapolation = smoke_arm_wall * (N_full / N_smoke) * 1.5 safety factor "
        "(covers PPMI-like nonlinear scaling; conservative for O(N) encoders; still safe for O(N log N)). "
        "For PPMI wikipedia: smoke_fit_wall=6.3s at N=500 -> extrap = 6.3 * (10000/500) * 1.5 = 189s per seed; "
        "actual was 413s (still an underestimate but flagged for extra caution). Prefer 3x factor over 1.5x "
        "for encoders with heavy per-example matrix ops. "
        "(ii) Per-seed metrics.json checkpoint: at end of each seed, write metrics.json.tmp then os.replace "
        "to metrics.json with partial per_seed list; then final write at end has all seeds. This preserves "
        "formal audit trail even under timeout kill. Composes with SH-4 per-seed hardening pattern and "
        "long-cells-checkpoint-resume USER-locked discipline. "
        "SCOPE: applies to ALL FULL cells routed to remote queue with expected wall > 300s per seed."
    ),
    "aliases": [],
    "metadata": {
        "record_class": "methodology_rule",
        "term_class": "CELL_QUALITY_TIMEOUT_AND_CHECKPOINT_DISCIPLINE",
        "cert_status": "chain_grade_methodology_rule",
        "cert_class": "CG_META_cell_quality_two_part_rule_with_concrete_evidence",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-03_ppmi_svd_wikipedia_FULL_DISCIPLINE_META",
        "witness_cells": [
            {
                "cell": "exp_substrate_wikipedia_ppmi_svd_scale_up_full_2026_07_03",
                "cell_author_smoke_fit_wall_s": 6.3,
                "cell_author_extrapolated_full_fit_wall_s_estimate": 140,
                "actual_full_fit_wall_s": 413,
                "underestimate_factor": 3.0,
                "timeout_ceiling_s": 1200,
                "expected_3_seed_wall_s": 1305,
                "seeds_killed_by_timeout": 1,
                "metrics_json_written": False,
                "recovery_method": "SSH-pull heartbeat.jsonl"
            }
        ],
        "rule_part_a_timeout_budget": "smoke_arm_wall * (N_full / N_smoke) * 3.0 safety factor for encoders with heavy per-example matrix ops; 1.5x for O(N) or O(N log N) encoders only",
        "rule_part_b_per_seed_checkpoint": "write metrics.json.tmp + os.replace to metrics.json after each seed completes with partial per_seed list; final write at end has all seeds; preserves formal audit trail under timeout kill",
        "composes_with_disciplines": [
            "USER_locked_long_cells_must_checkpoint_resume_restartable",
            "SH_4_per_seed_hardening_pattern",
            "reference_remote_dispatch_cell_readiness_checklist_2026-06-17"
        ],
        "cites": [
            "witness_atom_PPMI_wikipedia_FULL_HN_PRELIMINARY_2026-07-03",
            "USER_locked_metrics_path_disambiguation_selftest_smoke_full"
        ],
        "cert_increment_delta": 1
    }
}


def a5_append(path, atom):
    """Atomic append: tmp write + fsync + replace + verify-load."""
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
    session_tag = "2026-07-03_ppmi_svd_wikipedia_FULL_HN_PRELIMINARY_and_META_synth_and_DISCIPLINE"

    n_math = a5_append(MATH_ATOMS, atom_hn)
    print(f"[atomize] MATH atom (a) HN appended; total math lines={n_math}")
    ledger_append(atom_hn, session_tag)

    n_meta1 = a5_append(META_ATOMS, atom_meta_synth)
    print(f"[atomize] META atom (b) MM_TENTATIVE synth appended; total meta lines={n_meta1}")
    ledger_append(atom_meta_synth, session_tag)

    n_meta2 = a5_append(META_ATOMS, atom_meta_discipline)
    print(f"[atomize] META atom (c) DISCIPLINE_META appended; total meta lines={n_meta2}")
    ledger_append(atom_meta_discipline, session_tag)

    print("[atomize] DONE 3 atoms + 3 ledger entries; A5-gated (tmp+os.replace+verify-load)")
