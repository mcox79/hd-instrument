"""
A5-gated atomization for research 2x-drill on CA3 anti-signal mechanism analysis
(notes/research_2x_drill_ca3_anti_signal_at_cluster_codebook_mechanism_analysis_2026-07-03.md;
committed at 78facd6a8 via hd_metrics_sync auto-stage; research spawn a87e1eda8a0630197).

Skunkworks landed-VET off-disk (research-note verify-referent + prior-arc cross-check).

===============================================================================
VERIFICATION RECAP (off-disk):
===============================================================================
1. Research note exists at correct path (23.9KB, ts Jul 3 01:58); committed at 78facd6a8.
2. Cited internal note research_drill_optimal_shard_granularity_5x_2026-06-08.md exists;
   Cycle 178 numbers verified verbatim (grep hits lines 147, 310):
     "Cycle 178 iterative_regime_crossover_cpu_v1 showed rho=0.5 (mild ... )"
     Empirical values as cited: rho=0.5 -> recall=0.93 (BONUS); rho=0.0 -> 0.80; rho=0.9 -> 0.33.
3. Cited internal note research_drill_free_probability_VSA_cleanup_clustered_codebook_capacity_2x_2026-06-12.md exists;
   structure-aware-vs-structure-blind decoder framework verified verbatim at lines 38, 45:
     "structured patterns LIFT capacity ... IF the decoder is structure-aware.
      With a structure-blind decoder, structured patterns can DROP capacity."
4. Prior CG_HN_ARCHITECTURAL atom (bipolar+Gaussian 2nd witness at 4801f19c0) already
   encodes cluster_cos_theoretical=0.9 and observed cluster_cos in [0.899, 0.901] in
   self_audit_math. Anchor text says "at_cluster_structured_codebook" without explicit
   scope threshold -- REAL extrapolation risk if downstream consumers read only the anchor.
5. L6 CG_META rule (META_DISCIPLINE_ANALYTICAL_SCOPE_REFINEMENT_CHAINS_REQUIRE_MM_TENTATIVE)
   at 6d0da70dc explicitly states: "analytical scope-refinements over a single-axis
   mechanistic distinction MUST file as MM_TENTATIVE (not MM_STANDARD) until an empirical
   boundary probe validates the refinement's stability."
6. L6 boundary probe cell (6d0da70dc) measured COSINE ARM ONLY across cluster_cos in
   [0.30, 0.90] x corruption in [0.50, 0.75]. It did NOT include HIPPO/CA3 arms across
   the grid. So there is NO direct empirical measurement of CA3-anti-signal at
   cluster_cos < 0.9. The Cycle 178 inverted-U (rho=0.5 bonus) is from a DIFFERENT
   mechanism class (iterative_regime_crossover shard-granularity), not CA3 auto-associator.

===============================================================================
SYMMETRIC-VERIFY (both directions; honest downward per Fix #28):
===============================================================================
UPWARD claim from research drill: "Cycle 178 inverted-U + June-12 structure-blind decoder
framework converge on same scope-refinement question as the L6 boundary probe -- two
independent methods (literature + empirical) converge on same finding."

AUDITOR CORRECTION: L6 boundary probe measured COSINE only, not HIPPO. So the convergence
is at the ANALYTICAL LEVEL (both say "the anti-signal is bounded at high cluster_cos"),
NOT at the direct-empirical-measurement level. The Cycle 178 result is from a DIFFERENT
mechanism-class (iterative_regime_crossover shard-granularity, not CA3 auto-associator);
its extrapolation to CA3 relies on the "structure-blind decoder class" abstraction.
This is legitimate as CONVERGENT ANALYTICAL EVIDENCE, but NOT as direct empirical
witness. The correct disposition is therefore MM_TENTATIVE per L6 CG_META rule
(analytical scope-refinement without direct empirical boundary probe on the specific
mechanism in question).

===============================================================================
DIRECTOR OVER-CLAIM MITIGATION:
===============================================================================
Director requested "up to 4 candidates" and specifically mentioned hypothesis candidate
atoms (C at P=0.55) and a discipline_META atom on convergent research + empirical.
Both DEFERRED here on symmetric-verify grounds:
  - Hypothesis C at P=0.55 is a literature-derived probability with NO substrate-empirical
    test yet. Filing as CANDIDATE atom would violate discipline "don't over-file atoms
    based on research drill alone; empirical follow-up is standard".
  - Convergent-methods META atom relies on Cycle 178 + L6 probe converging -- but as
    noted above, L6 probe measured COSINE only, not HIPPO. The convergence is weaker
    than framed; the L6 CG_META rule ALREADY captures the analytical-scope-refinement
    discipline; a new META atom is not warranted this cycle.

Prior atom's SCOPE decision:
The prior CG_HN_ARCHITECTURAL atom's self_audit_math ALREADY encodes
cluster_cos_theoretical=0.9 and observed values ~0.90. The anchor text is silent on
threshold, but the metadata is explicit. Extrapolation risk is REAL but mitigated by
the atom's own metadata. A small MM_TENTATIVE scope-annotation amendment atom is
cheap insurance per L6 CG_META rule, without demoting the parent.

===============================================================================
FILINGS:
===============================================================================
Atom (a): META MM_TENTATIVE scope-annotation amendment on prior CG_HN_ARCHITECTURAL
   atom. Scope-refines the anti-signal to cluster_cos >~ 0.8-0.9 pending direct CA3-HIPPO
   arm boundary probe. Explicit expansion criterion. NO parent demotion.
Atom (b): META MM_STANDARD literature-synthesis on the structure-blind vs structure-aware
   decoder class. 4-axis literature convergence (Rolls / Amit / Ramsauer / Foldiak +
   arXiv:2301.02196) as substrate-KB memory-rule. NOT CG (no substrate-empirical CA3-arm
   witness yet); MM_STANDARD because 4-axis literature converge is standard synthesis
   under the deflated P=0.42 calibration.

DEFERRED (not filed this cycle):
  - Hypothesis C candidate atom (P=0.55 literature only, no substrate-empirical witness).
  - Convergent research + empirical DISCIPLINE_META atom (convergence weaker than claimed;
    L6 CG_META rule already covers).

2 atoms filed; matching TS_ISO ledger entries.
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
COMMIT = "78facd6a8"
RESEARCH_NOTE = "notes/research_2x_drill_ca3_anti_signal_at_cluster_codebook_mechanism_analysis_2026-07-03.md"
PARENT_CG_HN_ATOM_ID = "math::T2/MATH_CA3_AUTO_ASSOCIATOR_ANTI_SIGNAL_CROSS_GEOMETRY_2ND_WITNESS_CG_HONEST_NEGATIVE_ARCHITECTURAL_HIPPO_minus_DG_ONLY_neg_0p163_at_gaussian_filler_geometry_cluster_cos_0p90_matches_neg_0p176_at_bipolar_filler_geometry_witness_1_regime_cross_geometry_reproduction_promotion_criterion_from_prior_atom_second_witness_cluster_regime_probe_satisfied_Marr_CA3_pattern_completion_actively_hurts_at_cluster_structured_codebook_regardless_of_filler_encoding_geometry_supervised_synthetic_regime_n_seeds_3_corruption_75pct_dim_zero_masking_N500_cluster_size_5_hippo_G_r1_0p500_dg_only_G_r1_0p663_delta_neg_0p163_matches_bipolar_hippo_B_r1_0p517_dg_only_B_r1_0p693_delta_neg_0p176_architectural_finding_solidified_2026_07_03"


# ============= ATOM (a): META MM_TENTATIVE SCOPE-ANNOTATION AMENDMENT =============
atom_a_scope_amendment = {
    "id": "meta::T2/META_SCOPE_ANNOTATION_AMENDMENT_TO_CA3_ANTI_SIGNAL_CG_HN_ARCHITECTURAL_bound_to_cluster_cos_ge_0p8_pending_direct_HIPPO_arm_boundary_probe_MM_TENTATIVE_prior_atom_metadata_encodes_cluster_cos_0p90_but_anchor_text_silent_extrapolation_risk_downstream_consumers_reading_only_anchor_may_over_extrapolate_to_lower_correlation_regimes_but_Cycle_178_shows_INVERTED_U_at_iterative_regime_crossover_class_rho_0p5_recall_0p93_BONUS_rho_0p9_recall_0p33_COLLAPSE_though_that_is_different_mechanism_class_not_direct_CA3_witness_L6_boundary_probe_at_6d0da70dc_measured_COSINE_arm_only_NOT_HIPPO_across_grid_so_no_direct_CA3_empirical_boundary_yet_per_L6_CG_META_rule_analytical_scope_refinements_MUST_file_MM_TENTATIVE_until_empirical_boundary_probe_expansion_criterion_direct_HIPPO_CA3_arm_probe_at_cluster_cos_grid_0p3_0p5_0p7_0p9_would_promote_MM_TENTATIVE_to_MM_STANDARD_or_CG_scope_refined_2026_07_03",
    "name": "META scope-annotation AMENDMENT MM_TENTATIVE: CA3 anti-signal CG_HN_ARCHITECTURAL bound to cluster_cos >~ 0.8-0.9 pending direct HIPPO-arm boundary probe (L6 CG_META rule compliant)",
    "corpus": "meta",
    "tier": "T2",
    "kind": "metadata_amendment_scope_annotation_analytical_scope_refinement_pending_boundary_probe",
    "description": (
        "AMENDS parent CG_HONEST_NEGATIVE_ARCHITECTURAL atom (Store atoms are immutable-append; "
        "this is a cross-referencing amendment atom that annotates the parent's scope). "
        "Parent atom id (see amends_parent_atom_id): CG_HN_ARCHITECTURAL 2ND_WITNESS "
        "(bipolar + Gaussian at cluster_cos observed [0.899, 0.901], commit 4801f19c0). "
        "PARENT ATOM STATUS: NOT demoted. Parent remains CG_HN_ARCHITECTURAL. "
        "PARENT metadata correctly encodes cluster_cos_theoretical=0.9 and observed values "
        "~0.90 in self_audit_math. Anchor text says 'at_cluster_structured_codebook' without "
        "explicit threshold, which creates extrapolation risk for downstream consumers reading "
        "only the anchor. This amendment records the scope-boundary annotation. "
        "AMENDMENT SUBSTANCE: The CA3-anti-signal negative claim is empirically established at "
        "cluster_cos ~ 0.90 (2 witnesses: bipolar, Gaussian). It is NOT established below this "
        "threshold. Analytical evidence from research 2x-drill "
        "(notes/research_2x_drill_ca3_anti_signal_at_cluster_codebook_mechanism_analysis_2026-07-03.md) "
        "suggests the boundary is somewhere in [0.5, 0.8] via convergent literature (Ramsauer "
        "cluster-metastable states; Amit mixture-state dominance under crosstalk) and substrate-"
        "internal Cycle 178 inverted-U (rho=0.5 recall=0.93 BONUS; rho=0.9 recall=0.33 COLLAPSE). "
        "IMPORTANT AUDITOR CAVEAT: Cycle 178 result is from iterative_regime_crossover_cpu_v1 "
        "(shard-granularity mechanism class), NOT the CA3 auto-associator per se. Its "
        "extrapolation to CA3 relies on the analytical structure-blind-decoder-class "
        "abstraction (see atom b in this batch). The L6 boundary probe cell at 6d0da70dc measured "
        "COSINE baseline only across cluster_cos in [0.30, 0.90] x corruption in [0.50, 0.75]; it "
        "did NOT include HIPPO/CA3 arms in the grid. So there is NO DIRECT EMPIRICAL "
        "MEASUREMENT of CA3-anti-signal at cluster_cos < 0.9. "
        "TIER DISPOSITION: MM_TENTATIVE per L6 CG_META rule "
        "(META_DISCIPLINE_ANALYTICAL_SCOPE_REFINEMENT_CHAINS_REQUIRE_MM_TENTATIVE_TIER_UNTIL_"
        "EMPIRICAL_BOUNDARY_CLOSURE, commit 6d0da70dc): 'analytical scope-refinements over a "
        "single-axis mechanistic distinction MUST file as MM_TENTATIVE (not MM_STANDARD) until "
        "an empirical boundary probe validates the refinement's stability'. "
        "EXPANSION CRITERION: a direct HIPPO/CA3-arm boundary probe cell running the CA3 auto-"
        "associator arm across cluster_cos grid {0.3, 0.5, 0.7, 0.9} (matched N=500, 75% dim-zero "
        "corruption, same DG-analog config as the bipolar+Gaussian 2nd witness cell) would either: "
        "  (i) confirm inverted-U (HIPPO delta >= 0 at cluster_cos <= 0.7 AND delta << 0 at "
        "      cluster_cos = 0.9) -> promote this amendment to MM_STANDARD or CG "
        "      SCOPE_REFINED_TO_HIGH_CLUSTER_COS; parent atom scope tightened; "
        "  (ii) show HIPPO delta remains < 0 across the entire cluster_cos grid -> falsify this "
        "       amendment; parent atom scope broadens (or stays as-is); "
        "  (iii) show HIPPO delta is inconsistent (e.g., cluster_cos=0.5 bonus but cluster_cos=0.7 "
        "        still collapse) -> partial resolution; MB. "
        "This is a HIGH-EV empirical follow-up given the L6 CG_META rule and the CG_HN_ARCHITECTURAL "
        "atom's downstream engineering relevance (Spoke 3 hippocampal encoder design already flags "
        "DG-analog quality as load-bearing). "
        "COMPOSES WITH: parent CG_HN_ARCHITECTURAL atom (does not supersede); L6 CG_META rule "
        "on analytical scope refinement discipline; atom (b) in this batch (structure-blind "
        "decoder class literature synthesis providing the analytical framing for this scope claim). "
        "USER-LOCKED FRAMING: substrate knows nothing; this is mechanism math scope-annotation on "
        "supervised synthetic HD binding task, NOT a language/knowledge claim."
    ),
    "aliases": ["scope_annotation_amendment_CA3_anti_signal_cluster_cos_boundary_MM_TENTATIVE_2026_07_03"],
    "metadata": {
        "verified_off_data": True,
        "verified_ts": TS_ISO,
        "verifier": "hdi_skunkworks",
        "commit_hash": COMMIT,
        "research_note_path": RESEARCH_NOTE,
        "cert_status": "measured_mechanism_tentative_scope_annotation_amendment",
        "cert_class": "MM_TENTATIVE_scope_annotation_amendment_pending_direct_HIPPO_arm_boundary_probe",
        "cert_ts": TS_ISO,
        "amends_parent_atom_id": PARENT_CG_HN_ATOM_ID,
        "amendment_type": "scope_annotation_pending_empirical_boundary_probe_no_parent_demotion",
        "parent_atom_status_after_amendment": "unchanged_CG_HN_ARCHITECTURAL_retained_scope_annotation_recorded_via_this_amendment_atom",
        "empirical_scope_established_by_parent_atom": "cluster_cos_observed_bipolar_0p899_0p899_0p899_and_gaussian_0p899_0p901_0p900_i_e_cluster_cos_approx_0p90",
        "analytical_scope_hypothesis_from_research_drill": "cluster_cos_boundary_somewhere_in_0p5_to_0p8_based_on_convergent_literature_plus_Cycle_178_inverted_U_at_different_mechanism_class",
        "l6_boundary_probe_measured_only_COSINE_not_HIPPO": True,
        "cycle_178_is_iterative_regime_crossover_cpu_v1_NOT_CA3_auto_associator_direct_witness": True,
        "cycle_178_verified_numbers": {
            "rho_0p0_recall": 0.80,
            "rho_0p5_recall": 0.93,
            "rho_0p9_recall": 0.33,
            "source": "notes/research_drill_optimal_shard_granularity_5x_2026-06-08.md line 147 and 310"
        },
        "expansion_criterion_direct_hippo_arm_probe": {
            "regime": "HIPPO CA3 arm at cluster_cos in {0.3, 0.5, 0.7, 0.9}, matched N=500 75% dim-zero corruption same DG-analog config as bipolar+Gaussian 2nd witness",
            "outcome_i": "inverted_U_confirmed_HIPPO_delta_ge_0_at_low_and_lt_0_at_0p9_promote_this_amendment_MM_STANDARD_or_CG_parent_scope_tightens",
            "outcome_ii": "HIPPO_delta_lt_0_across_grid_falsifies_amendment_parent_scope_broadens_or_stays",
            "outcome_iii": "inconsistent_partial_resolution_MB"
        },
        "composes_with_atoms": [
            PARENT_CG_HN_ATOM_ID,
            "meta::T2/META_DISCIPLINE_ANALYTICAL_SCOPE_REFINEMENT_CHAINS_REQUIRE_MM_TENTATIVE_TIER_UNTIL_EMPIRICAL_BOUNDARY_CLOSURE_CG_META_PROMOTION_3RD_WITNESS_L2_L4_L6_2026_07_03",
            "atom_b_this_batch_META_STRUCTURE_BLIND_DECODER_CLASS_KNOWN_ATTRACTOR_FAILURE_MM_STANDARD_2026_07_03"
        ],
        "user_locked_framing_substrate_knows_nothing": True,
        "term_class": "SCOPE_ANNOTATION_ANALYTICAL_REFINEMENT_PENDING_EMPIRICAL",
        "cross_arc_substrate_KB_overlap_check": "L6 CG_META rule directly composes; L6 boundary probe atom (COSINE-only scope) directly cited as EVIDENCE_OF_MISSING_HIPPO_ARM_EMPIRICAL, not as evidence of CA3-boundary; symmetric-verify caveat recorded",
        "cert_increment_delta": 0
    }
}


# ============= ATOM (b): META MM_STANDARD structure-blind-decoder literature synthesis =============
atom_b_structure_blind_meta = {
    "id": "meta::T2/META_HEBBIAN_OUTER_PRODUCT_IS_STRUCTURE_BLIND_DECODER_CLASS_KNOWN_ATTRACTOR_NETWORK_FAILURE_CLASS_UNDER_TIGHT_CLUSTERING_MM_STANDARD_4_LITERATURE_AXES_CONVERGENT_Rolls_2013_correlation_reduces_CA3_capacity_Amit_1985_1989_mixture_state_dominance_under_correlated_storage_Ramsauer_2020_modern_Hopfield_cluster_metastable_states_at_low_beta_Foldiak_1990_arXiv_2301_02196_2023_competitive_learning_preprocessing_fixes_it_upstream_all_four_axes_agree_plain_Hebbian_CA3_is_structure_blind_and_upstream_pattern_separation_via_competitive_Hebbian_is_the_dominant_literature_fix_June_12_substrate_internal_note_independently_derived_same_dichotomy_structure_aware_LIFT_vs_structure_blind_DROP_under_clustering_all_evidence_LITERATURE_no_substrate_empirical_CA3_arm_witness_yet_so_MM_STANDARD_not_CG_expansion_criterion_direct_CA3_arm_probe_across_cluster_cos_grid_or_competitive_Hebbian_DG_preprocessing_probe_HARD_PASS_would_promote_to_CG_META_2026_07_03",
    "name": "META MM_STANDARD: Plain Hebbian outer-product auto-associator is a STRUCTURE-BLIND DECODER CLASS that DROPS capacity under tight clustering (known attractor-network failure class; 4-axis literature convergence + substrate-internal June-12 note)",
    "corpus": "meta",
    "tier": "T2",
    "kind": "literature_synthesis_meta_rule_known_failure_class",
    "description": (
        "META rule as substrate-KB memory: the observed CA3-anti-signal at cluster-structured "
        "codebooks (parent CG_HN_ARCHITECTURAL atom) is a KNOWN CLASS of attractor-network failure, "
        "NOT a substrate-novel pathology. Four independent literature axes converge on the diagnosis; "
        "one substrate-internal note independently derived the same abstract framing. "
        "AXIS 1 (NEUROSCIENCE): Rolls 2013 (PMC3812781): 'correlations between patterns reduce the "
        "memory capacity' of CA3, with p_max ~ C_RC*[a*ln(1/a)]/k. Hopfield prototype-attractor "
        "literature (arXiv:2407.03342) shows patterns sharing a prototype generate crosstalk terms "
        "creating dominant 'prototype attractor' swamping individually-stored patterns. In-vivo "
        "prevention: DG sparsification + Hasselmo cholinergic-theta-gating -- both UPSTREAM of CA3. "
        "AXIS 2 (MATH/PHYSICS): Amit-Gutfreund-Sompolinsky 1985/1987 + Amit 1989: mixture-state "
        "spurious attractors are a KNOWN class even at sub-saturation; correlated/clustered storage "
        "make mixture-state convergence the DOMINANT outcome. Storkey 1997 partial fix (pairwise). "
        "Tight clustering (near-singular Gram matrix) makes standard fixes only partial; full "
        "decorrelation (whitening/Gram-Schmidt) cited as fuller fix. "
        "AXIS 3 (ML): Ramsauer 2020 ('Hopfield Networks is All You Need'): modern/continuous "
        "Hopfield has three fixed-point classes -- single-pattern minima, global average, and "
        "METASTABLE CLUSTER-AVERAGING STATES; at low inverse-temperature beta, clustered/"
        "insufficiently-separated patterns converge to cluster-averaging metastable state. "
        "Direct theoretical match. Foldiak 1990 + arXiv:2301.02196 (2023 Neural Networks): "
        "competitive-learning front end sparsifies inputs BEFORE associator; 'beats sparse coding "
        "baselines' and approaches optimal random-code capacity. "
        "AXIS 4 (SUBSTRATE-INTERNAL): June-12 note research_drill_free_probability_VSA_cleanup_"
        "clustered_codebook_capacity_2x_2026-06-12.md, verified verbatim at lines 38, 45: "
        "'structured patterns LIFT capacity ... IF the decoder is structure-aware. With a "
        "structure-blind decoder, structured patterns can DROP capacity (intra-cluster crowding) "
        "because the decoder cannot exploit the cluster separation.' Written 3 weeks BEFORE the "
        "CA3 finding, about a DIFFERENT mechanism (Resonator cleanup), and independently derives "
        "the same abstract framing that predicts the CA3-anti-signal sign and mechanism. "
        "CONVERGENT DIAGNOSIS: Plain Hebbian outer-product CA3 is a textbook STRUCTURE-BLIND decoder "
        "(sums outer products of all stored patterns identically regardless of cluster membership). "
        "Under tight clustering, crosstalk terms dominate and pull retrieval toward shared "
        "prototype/mixture attractor. The dominant literature-favored fix is UPSTREAM pattern-"
        "separation (competitive-Hebbian DG preprocessing, per Foldiak 1990 + arXiv:2301.02196), "
        "NOT a CA3-internal storage rule change (Storkey; partial only for tight clustering) or "
        "iteration count change (weakest-supported). "
        "TIER: MM_STANDARD, NOT CG_META. Justification: literature convergence is strong (4 axes) "
        "and independently corroborated by a prior substrate-internal note, but no direct substrate-"
        "empirical CA3-arm test of the upstream-fix hypothesis has been run yet. Research drill's "
        "P_deflated=0.42 calibration also supports MM_STANDARD tier (below the deflated-70pct "
        "typical CG_META bar). "
        "EXPANSION CRITERION TO CG_META: either (i) direct CA3-arm probe across cluster_cos grid "
        "{0.3, 0.5, 0.7, 0.9} showing inverted-U consistent with structure-blind-decoder framing "
        "(atom a expansion criterion); OR (ii) competitive-Hebbian DG preprocessing probe "
        "(research drill Probe 3, Foldiak-1990-style WTA) HARD-PASSES (delta >= +0.05 over current "
        "HIPPO baseline AND >= DG_ONLY). Either would upgrade this MM_STANDARD to CG_META. "
        "OPERATIONAL RULE FOR SUBSTRATE ENGINEERING: for any future Marr-CA3-adjacent design in "
        "Stage 2/3 (Spoke 3 or later), the DG-analog upstream stage MUST include a learned "
        "structure-aware pattern-separator (competitive-Hebbian / anti-Hebbian lateral inhibition, "
        "Foldiak 1990), NOT just a fixed random-projection + top-K threshold. This applies to the "
        "in-flight Spoke 3 hippocampal encoder design's DG-analog choice (Option A fixed-projection "
        "vs Option B Hebbian-adjusted). "
        "USER-LOCKED FRAMING: substrate knows nothing; this is a math META rule on decoder-class "
        "attractor-network theory, NOT a language/knowledge claim. Not 'first' / 'novel law of "
        "physics' -- this is convergent confirmation of decades-old attractor-network theory "
        "applied to a substrate-specific configuration."
    ),
    "aliases": ["structure_blind_decoder_class_known_attractor_failure_META_MM_STANDARD_2026_07_03"],
    "metadata": {
        "verified_off_data": True,
        "verified_ts": TS_ISO,
        "verifier": "hdi_skunkworks",
        "commit_hash": COMMIT,
        "research_note_path": RESEARCH_NOTE,
        "cert_status": "measured_mechanism_standard",
        "cert_class": "MM_STANDARD_4_axis_literature_convergence_plus_1_substrate_internal_axis_prior_arc",
        "cert_ts": TS_ISO,
        "n_literature_axes": 4,
        "literature_axes": {
            "neuroscience": [
                "Rolls 2013 PMC3812781 correlations_reduce_CA3_memory_capacity",
                "Marr 1971 archicortex_theory_codon_preprocessing_upstream",
                "Hopfield_prototype_attractor_arXiv_2407_03342",
                "Hasselmo_Kunec_cholinergic_theta_gating_upstream_prevention"
            ],
            "math_physics": [
                "Amit_Gutfreund_Sompolinsky_1985_1987_and_Amit_1989_mixture_state_spurious_attractors",
                "Tsodyks_Feigelman_1988_sparse_capacity_assumes_decorrelated",
                "Storkey_1997_partial_fix_for_pairwise_correlation_insufficient_for_tight_clustering"
            ],
            "ml_computational": [
                "Ramsauer_2020_arXiv_2008_02217_modern_Hopfield_cluster_metastable_states",
                "Foldiak_1990_competitive_anti_Hebbian_sparse_decorrelated_code",
                "arXiv_2301_02196_2023_Neural_Networks_competitive_learning_preprocessing_for_associative_memory",
                "Sarra_2025_arXiv_2405_08777_daydreaming_Hopfield_iterative_unlearning"
            ],
            "substrate_internal": [
                "notes/research_drill_free_probability_VSA_cleanup_clustered_codebook_capacity_2x_2026-06-12.md structure_aware_vs_structure_blind_decoder_framework verified verbatim lines 38 45"
            ]
        },
        "convergent_diagnosis": "plain_Hebbian_outer_product_CA3_is_structure_blind_decoder_under_tight_clustering_crosstalk_terms_dominate_pulling_retrieval_toward_shared_prototype_or_mixture_attractor",
        "literature_favored_fix": "upstream_pattern_separation_competitive_Hebbian_DG_preprocessing_Foldiak_1990_plus_arXiv_2301_02196",
        "not_favored_fixes": {
            "storkey_pairwise_correlation_fix": "partial_only_for_tight_clustering_near_singular_Gram",
            "iteration_count_change": "weakest_supported_no_direct_literature_hit"
        },
        "expansion_criterion_to_CG_META": {
            "path_1": "direct_CA3_arm_probe_across_cluster_cos_grid_showing_inverted_U",
            "path_2": "competitive_Hebbian_DG_preprocessing_probe_HARD_PASS_delta_ge_0p05_over_HIPPO_and_ge_DG_ONLY"
        },
        "operational_rule_for_substrate_engineering": "future_Marr_CA3_adjacent_designs_MUST_include_learned_structure_aware_DG_analog_competitive_Hebbian_anti_Hebbian_lateral_inhibition_not_fixed_random_projection_top_K_threshold_alone",
        "applies_to_in_flight_design": "Spoke_3_hippocampal_encoder_DG_analog_choice_Option_A_fixed_projection_vs_Option_B_Hebbian_adjusted",
        "p_deflated_research_drill": 0.42,
        "cross_arc_substrate_KB_overlap_check": "June_12_free_probability_note_directly_composes_at_cosine_0p3086_prior_arc; L6 CG_META rule cited as tier discipline; overlap is legitimate and load-bearing not rediscovery",
        "composes_with_atoms": [
            PARENT_CG_HN_ATOM_ID,
            "atom_a_this_batch_META_SCOPE_ANNOTATION_AMENDMENT_MM_TENTATIVE_2026_07_03",
            "meta::T2/META_DISCIPLINE_ANALYTICAL_SCOPE_REFINEMENT_CHAINS_REQUIRE_MM_TENTATIVE_TIER_UNTIL_EMPIRICAL_BOUNDARY_CLOSURE_CG_META_PROMOTION_3RD_WITNESS_L2_L4_L6_2026_07_03"
        ],
        "user_locked_framing_substrate_knows_nothing": True,
        "term_class": "META_LITERATURE_SYNTHESIS_KNOWN_ATTRACTOR_FAILURE_CLASS_STRUCTURE_BLIND_DECODER",
        "cert_increment_delta": 1
    }
}


# ================================================================================
# A5-GATED APPENDS (atomic tmp+os.replace+verify-load) with matching TS_ISO ledger
# ================================================================================
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
        "atomized_by": atom["metadata"].get("verifier"),
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
    session_tag = "2026-07-03_research_2x_drill_ca3_anti_signal_scope_amendment_and_structure_blind_META"

    n_meta1 = a5_append(META_ATOMS, atom_a_scope_amendment)
    print(f"[atomize] META atom (a) MM_TENTATIVE scope-annotation amendment appended; total meta lines={n_meta1}")
    ledger_append(atom_a_scope_amendment, session_tag)

    n_meta2 = a5_append(META_ATOMS, atom_b_structure_blind_meta)
    print(f"[atomize] META atom (b) MM_STANDARD structure-blind decoder literature synthesis appended; total meta lines={n_meta2}")
    ledger_append(atom_b_structure_blind_meta, session_tag)

    print("[atomize] DONE 2 atoms + 2 ledger entries; A5-gated (tmp+os.replace+verify-load); matching TS_ISO")
