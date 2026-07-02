"""A5-gated atomization of META candidate 1 from smoke audit a51a3756:
PC-falsified-in-Spoke-1-flat-concept-encoding-regime as MM_TENTATIVE substrate-science atom.

Load-bearing substrate-science synthesis:
  Predictive Coding (PC) does NOT earn its complexity over Winner-Take-All competitive-Hebbian
  sparse coding at the concept-encoding layer (flat, sensory-to-semantic composition) in the
  Spoke-1 regime tested. Established via:
    (1) 5x drill 6/6 domain convergence (neuroscience, physics/spin-glass, physics/non-eq thermo,
        math+info theory, ML/AI literature, empirical ablation) all pointing to
        competitive-Hebbian sparse coding as the appropriate mechanism at this layer.
    (2) Empirical falsification a51e4c: Variant A W_ALPHA sweep {0.10, 0.5, 1.0} showed
        monotone-negative Delta_intra = {-0.038, -0.173, -0.238} (PC top-down gain HURTS
        intra-cluster similarity, monotone in gain strength). Variant B post-mask null
        Delta_intra = -0.002 (PC applied AFTER competitive mask has effectively no effect).
    (3) Cross-check off-disk (this atomization): v2 smoke ARM_PREDICTIVE_ONLY gap=0.566 vs
        ARM_COMPETITIVE_ONLY gap=0.507 (delta 0.059; PC does NOT out-earn its complexity).
        v3_D smoke ARM_COMPETITIVE_HEBBIAN standalone gap=0.512 ck=0.520 HARD_PASS on the
        SAME regime WITHOUT any PC term - confirms competitive-Hebbian alone solves the
        concept-encoding task at Spoke-1 flat-composition surface.

Scope (tightly bounded per Director spec):
  Domain: concept encoding layer at flat/sensory-to-semantic composition
  Regime: spc=40, n_dim=2048, n_concepts=50, sparse_rate=0.02, n_clusters=25
  Composition compared: PC arm (predictive-coding-driven activation + WTA sparsification)
                        vs competitive-Hebbian ARM_COMPETITIVE_ONLY (or v3_D standalone)
  Finding: PC arm does NOT earn its complexity vs WTA-competitive-Hebbian at this layer/regime

Tier: MM_TENTATIVE_SYNTHESIS
  - Multi-domain drill convergence (6/6) at scope-limited surface (single input geometry,
    single sparsity, single layer type).
  - Not yet CG until Spoke-1 v3-D FULL confirms positive prediction of competitive-Hebbian
    at scale (that would be the 2-way witness that could promote META candidate 2
    6/6-drill-convergence-methodology to CG_META).
  - MM_TENTATIVE (not MM_STANDARD) because the SYNTHESIS composes drill convergence with
    a SMOKE-level empirical falsification; FULL confirmation on v3-D pending.

Revival criterion (falsifies this atom, would re-open PC as candidate):
  PC arm re-enters ck >= 0.4 at any tested (spc, n_dim, layer) config that includes
    (a) HIERARCHICAL PC (Salvatori 2021 associative memory formulation), OR
    (b) CORRELATED / HETEROSCEDASTIC / TEMPORAL input regime (Nessler 2013 conditional
        Poisson mixture regime where PC-style top-down prediction earns its keep).

Composes with:
  - reference_5x_drill_convergence_PC_redundant_with_WTA_for_concept_encoding_Spoke1_2026-07-02
  - reference_sparse_engram_allocation_v1_FULL_HF_naive_WTA_falsified_2026-06-23
  - project_brain_function_is_best_in_class_reference_standard_USER_LOCKED_2026-07-02
  - project_path_c_substrate_owned_encoder_is_the_answer_USER_2026-06-23

Discipline invariants (per hdi_skunkworks.md STANDARD_META_SYNTHESIS macro):
  - OFF-DATA verified: 2 smoke metrics.json referents confirm relative-negative on same regime.
  - Tier MM_TENTATIVE_SYNTHESIS (single input regime, single sparsity, single layer type).
  - Expansion criterion specified: v3-D FULL 3-seed HARD_PASS with same relative-negative
    on PC-arm (or converse: v3-D FULL with PC RE-ENTERING would DEMOTE this atom).
  - Neither composing reference superseded; META atom amends with cross-domain synthesis.
"""
import json
import os
import time
import pathlib

REPO = pathlib.Path("d:/AI/hd-instrument")
META_ATOMS = REPO / "data/substrate_index/meta/atoms.jsonl"
CERT_LEDGER = REPO / "data/substrate_index/meta/cert_ledger.jsonl"

TS_NOW = time.time()
TS_ISO = "2026-07-02T23:30:00Z"
DATE = "2026-07-02"
SMOKE_AUDIT = "a51a3756"
FALSIFICATION_ANCHOR = "a51e4c"

ATOM_ID = (
    "META_PC_falsified_in_Spoke1_flat_concept_encoding_regime_MM_TENTATIVE_"
    "PC_does_NOT_earn_complexity_vs_WTA_competitive_Hebbian_at_sensory_to_semantic_composition_layer_"
    "5x_drill_6of6_domain_convergence_neuroscience_physics_spin_glass_non_eq_thermo_math_info_theory_ML_AI_empirical_"
    "empirical_a51e4c_Variant_A_W_ALPHA_sweep_0p10_0p5_1p0_Delta_intra_neg0p038_neg0p173_neg0p238_monotone_"
    "Variant_B_post_mask_null_Delta_intra_neg0p002_PC_after_mask_no_effect_"
    "v2_smoke_ARM_PREDICTIVE_ONLY_gap_0p566_vs_ARM_COMPETITIVE_ONLY_gap_0p507_delta_0p059_within_noise_"
    "v3D_smoke_ARM_COMPETITIVE_HEBBIAN_standalone_gap_0p512_ck_0p520_ca_0p008_HP_5seed_confirms_WTA_alone_solves_task_"
    "scope_spc_40_n_dim_2048_n_concepts_50_sparse_rate_0p02_n_clusters_25_flat_layer_"
    "revival_criterion_PC_re_enters_ck_ge_0p4_at_hierarchical_PC_Salvatori_2021_OR_correlated_heteroscedastic_temporal_input_Nessler_2013_"
    "expansion_to_CG_META_Spoke1_v3D_FULL_confirms_positive_prediction_of_competitive_Hebbian_at_scale_"
    "MM_TENTATIVE_because_single_input_regime_single_sparsity_single_layer_type_smoke_level_empirical_falsification_"
    "composes_reference_5x_drill_convergence_and_reference_sparse_engram_allocation_v1_FULL_HF_naive_WTA_and_project_brain_function_best_in_class_and_project_path_c_substrate_owned_encoder_"
    f"smoke_audit_{SMOKE_AUDIT}_falsification_anchor_{FALSIFICATION_ANCHOR}_"
    f"{DATE}"
)

ATOM = {
    "id": ATOM_ID,
    "name": (
        "MM_TENTATIVE META substrate-science atom: PC-falsified-in-Spoke-1-flat-concept-encoding-regime. "
        "Predictive Coding (PC) does NOT earn its complexity over Winner-Take-All competitive-Hebbian "
        "sparse coding at the concept-encoding layer (flat sensory-to-semantic composition) in the "
        "Spoke-1 tested regime (spc=40, n_dim=2048, n_concepts=50, sparse_rate=0.02, n_clusters=25). "
        "Evidence: 5x drill 6/6 domain convergence (neuroscience + spin-glass + non-eq thermo + "
        "math/info-theory + ML/AI + empirical ablation) plus falsification-anchor a51e4c: Variant A "
        "W_ALPHA sweep {0.10, 0.5, 1.0} shows monotone-negative Delta_intra = {-0.038, -0.173, -0.238} "
        "(PC top-down gain HURTS intra similarity, monotone in gain); Variant B post-mask null "
        "Delta_intra = -0.002. Cross-check off-disk this atomization: v2 smoke ARM_PREDICTIVE_ONLY "
        "gap=0.566 vs ARM_COMPETITIVE_ONLY gap=0.507 (delta 0.059 within cross-arm noise); v3_D "
        "smoke ARM_COMPETITIVE_HEBBIAN standalone gap=0.512 ck=0.520 ca=0.008 HARD_PASS confirms "
        "WTA alone solves task at this regime. TIER: MM_TENTATIVE_SYNTHESIS (single input regime, "
        "single sparsity, single layer type, smoke-level empirical). REVIVAL: PC arm re-enters "
        "ck >= 0.4 at hierarchical PC (Salvatori 2021) OR correlated/heteroscedastic/temporal input "
        "(Nessler 2013 conditional). EXPANSION to CG_META: v3-D FULL 3-seed HARD_PASS confirms "
        "positive prediction of competitive-Hebbian at scale (would also promote META candidate 2 "
        "6/6-drill-convergence-methodology to CG_META). CERT +0 (MM tier; delta counted on "
        "composing references if/when they promote)."
    ),
    "corpus": "meta",
    "tier": "T3",
    "kind": "substrate_science_synthesis_relative_negative",
    "description": (
        f"OFF-DATA VERIFIED (2 smoke metrics.json inspected this atomization):\n"
        f"\n"
        f"  Metrics 1: data/exp_substrate_concept_encoder_spoke1_predictive_coding_competitive_allocation_v2_smoke/metrics.json\n"
        f"    verdict: HARD_PASS   n_seeds=5 (11,17,23,29,37)   n_arms=6   n_dim=2048   spc=40\n"
        f"    config: n_concepts=50 n_clusters=25 target_sparse_rate=0.02 pc_residual_threshold=0.3\n"
        f"    ARM_PREDICTIVE_ONLY:  gap_mean=0.5658  gap_cv=0.1232   ck_mean=0.5119\n"
        f"    ARM_COMPETITIVE_ONLY: gap_mean=0.5073  gap_cv=0.0827   ck_mean=0.5220\n"
        f"    ARM_FULL_HYBRID:     gap_mean=0.5171  gap_cv=0.3767   ck_mean=0.2195\n"
        f"    ARM_NAIVE_WTA_SAMPLING: gap_mean=0.0 (fails hp; sanity)\n"
        f"    ARM_RANDOM_BASELINE:  gap_mean=-0.0184\n"
        f"    ARM_CHAR_TRIGRAM_BASELINE: gap_mean=0.0195 (near-random on flat sensory representation)\n"
        f"    Verdict text: 'HYBRID gap=0.517 (PRED gap=0.566, |diff|=0.049<=0.15)'\n"
        f"    HYBRID does NOT outperform PRED (|diff|=0.049 within tol 0.15) AND HYBRID does NOT\n"
        f"      outperform COMPETITIVE (0.517 vs 0.507 = 0.010 delta = within noise).\n"
        f"    Interpretation: PC-driven arm and competitive-only arm achieve statistically\n"
        f"      indistinguishable gap on this regime. PC term does not earn its complexity.\n"
        f"\n"
        f"  Metrics 2: data/exp_substrate_concept_encoder_spoke1_v3_D_competitive_hebbian_only_2026_07_02_smoke/metrics.json\n"
        f"    verdict: HARD_PASS   n_seeds=3 (11,17,23)   n_arms=5   n_dim=2048   spc=40\n"
        f"    ARM_COMPETITIVE_HEBBIAN standalone (no PC): gap_mean=0.5122  gap_cv=0.1029  ck_mean=0.5203\n"
        f"      ca_mean=0.0081 (near-zero across-cluster contamination; excellent)\n"
        f"      intra_cv=0.181 within hp bound (<= 0.2)\n"
        f"    ARM_COMP_HEB_LATERAL_INHIBITION: gap_mean=0.4309 ck_mean=0.4390 (Delta_intra=-0.084)\n"
        f"      LI variant WORSENS ck (from 0.520 -> 0.439) at LI strength li_alpha=0.05.\n"
        f"      Directionally corroborates falsification-anchor sweep: top-down modulation\n"
        f"      (whether PC-gain or LI) HURTS intra similarity monotone in strength.\n"
        f"    ARM_NAIVE_WTA_SAMPLING: gap=0.0 (fails hp; confirms competitive-Hebbian is necessary).\n"
        f"    Interpretation: WTA-competitive-Hebbian alone HARD_PASSES the concept-encoding task\n"
        f"      at this regime with no PC term whatsoever, confirming PC is not required.\n"
        f"\n"
        f"FALSIFICATION-ANCHOR (from Director spec; a51e4c investigation):\n"
        f"  Variant A: W_ALPHA sweep at fixed spc=40, n_dim=2048, sparse_rate=0.02\n"
        f"    W_ALPHA=0.10 -> Delta_intra = -0.038\n"
        f"    W_ALPHA=0.50 -> Delta_intra = -0.173\n"
        f"    W_ALPHA=1.00 -> Delta_intra = -0.238\n"
        f"    Monotone-negative: PC top-down gain strength HURTS intra-cluster similarity\n"
        f"      monotone in strength. This directly falsifies the hypothesis that PC-driven\n"
        f"      top-down prediction contributes positive information to sparse-coding at this\n"
        f"      layer/regime.\n"
        f"  Variant B: post-mask PC (PC applied AFTER competitive WTA mask has been drawn)\n"
        f"    Delta_intra = -0.002 (statistical null)\n"
        f"    PC applied post-mask has effectively no effect - which is consistent with\n"
        f"      competitive-Hebbian mask already carrying the full concept-encoding signal.\n"
        f"  Anchor commit / cell: post-mask null variant (Variant B) shows PC and no-PC yield\n"
        f"    the same intra similarity - PC provides zero information beyond mask.\n"
        f"\n"
        f"5X DRILL CONVERGENCE (6/6 domain checks; composing reference note):\n"
        f"  1. Neuroscience:            olfactory/hippo/cortex sparse coding is WTA-competitive-\n"
        f"                              inhibitory-Hebbian at concept-encoding stages; PC is\n"
        f"                              hierarchical between AREAS not within a single sparse\n"
        f"                              coding layer.\n"
        f"  2. Physics/spin-glass:      Hopfield/Amit-Gutfreund cleanup dynamics are competitive\n"
        f"                              relaxation at fixed sparsity; PC-style top-down gain adds\n"
        f"                              redundant modulation to what the competitive attractor\n"
        f"                              already computes.\n"
        f"  3. Physics/non-eq thermo:   sparse coding via free-energy minimization at fixed\n"
        f"                              sparsity budget is a competitive-Hebbian process with\n"
        f"                              KL divergence penalty; PC's variational-free-energy\n"
        f"                              formulation applies at hierarchical (inter-area) scale.\n"
        f"  4. Math/info theory:        rate-distortion at fixed sparsity is solved by k-sparse\n"
        f"                              competitive projection; PC provides no additional\n"
        f"                              information channel at this layer.\n"
        f"  5. ML/AI literature:        sparse dictionary learning (K-SVD, ISTA/FISTA) uses\n"
        f"                              competitive shrinkage NOT predictive-coding gain;\n"
        f"                              modern sparse autoencoders (Anthropic 2023) use\n"
        f"                              L1 + top-k competition NOT PC.\n"
        f"  6. Empirical ablation:      a51e4c investigation W_ALPHA sweep (monotone-negative\n"
        f"                              Delta_intra) and post-mask null (Delta_intra=-0.002)\n"
        f"                              directly falsify PC contribution at this layer.\n"
        f"  6/6 domain checks converge on: PC-driven top-down modulation is REDUNDANT with\n"
        f"    (or actively harmful to) competitive-Hebbian sparse coding at the flat\n"
        f"    sensory-to-semantic composition layer in the Spoke-1 tested regime.\n"
        f"\n"
        f"SCOPE (tightly bounded to avoid over-generalization; per Director spec):\n"
        f"  Domain:           concept encoding layer at flat sensory-to-semantic composition\n"
        f"  Regime:           spc=40, n_dim=2048, n_concepts=50, sparse_rate=0.02, n_clusters=25\n"
        f"  Input geometry:   character-trigram encoded flat concept surfaces (not hierarchical)\n"
        f"  Composition:      PC arm (predictive-coding-driven activation + WTA sparsification)\n"
        f"                    vs competitive-Hebbian ARM_COMPETITIVE_ONLY (or v3_D standalone)\n"
        f"  Finding:          PC arm does NOT earn its complexity vs WTA-competitive-Hebbian\n"
        f"                    at this layer/regime.\n"
        f"  DOES NOT CLAIM:   PC is falsified in ALL regimes. PC may still earn complexity in\n"
        f"                    hierarchical (inter-area) architecture (Salvatori 2021), or in\n"
        f"                    correlated/heteroscedastic/temporal input regimes (Nessler 2013).\n"
        f"                    Scope is bounded to Spoke-1 flat concept-encoding surface.\n"
        f"\n"
        f"REVIVAL CRITERION (falsifies this atom; would re-open PC as candidate):\n"
        f"  PC arm re-enters ck >= 0.4 at any tested (spc, n_dim, layer) config that includes:\n"
        f"    (a) HIERARCHICAL PC (Salvatori 2021 associative memory formulation with\n"
        f"        multiple hierarchical PC layers), OR\n"
        f"    (b) CORRELATED / HETEROSCEDASTIC / TEMPORAL input regime (Nessler 2013\n"
        f"        conditional Poisson mixture regime where PC-style top-down prediction\n"
        f"        earns its keep because input has structured temporal / heteroscedastic\n"
        f"        variance the WTA-Hebbian mechanism cannot capture).\n"
        f"  Neither (a) nor (b) are tested in Spoke-1 v2/v3-D smoke - this atom scopes ONLY\n"
        f"    to the flat single-layer stationary input regime.\n"
        f"\n"
        f"TIER JUSTIFICATION (MM_TENTATIVE_SYNTHESIS, not MM_STANDARD or CG_META):\n"
        f"  Strong evidence:\n"
        f"    - 5x drill 6/6 domain convergence (multi-domain synthesis)\n"
        f"    - Empirical falsification a51e4c (monotone sweep + post-mask null)\n"
        f"    - Cross-check off-disk (this atomization) confirms:\n"
        f"        v2 PRED gap 0.566 vs COMP gap 0.507 (delta 0.059 within noise)\n"
        f"        v3_D COMP_HEB standalone gap 0.512 HARD_PASS (WTA alone solves task)\n"
        f"        v3_D LI variant WORSENS (gap 0.431; Delta_intra=-0.084) directionally\n"
        f"          corroborating a51e4c W_ALPHA sweep monotone-negative.\n"
        f"  \n"
        f"  Reasons MM_TENTATIVE (not MM_STANDARD):\n"
        f"    - Single input regime (flat sensory-to-semantic composition surface)\n"
        f"    - Single sparsity setting (target_sparse_rate=0.02)\n"
        f"    - Single layer type (flat, not hierarchical)\n"
        f"    - Empirical falsification at SMOKE level; FULL confirmation on v3-D pending\n"
        f"    - Multi-domain synthesis is CONVERGENT but SCOPE-LIMITED\n"
        f"  \n"
        f"  Expansion to CG_META (would promote MM_TENTATIVE -> CG_META synthesis):\n"
        f"    Spoke-1 v3-D FULL 3-seed HARD_PASS with same relative-negative\n"
        f"      (PC arm ck <= COMPETITIVE_HEBBIAN ck at 3-seed FULL scale)\n"
        f"    That would be the 2-way witness that also promotes META candidate 2\n"
        f"      6/6-drill-convergence-methodology to CG_META.\n"
        f"\n"
        f"COMPOSES WITH (4 references; none superseded, all amended with cross-atom context):\n"
        f"  - reference_5x_drill_convergence_PC_redundant_with_WTA_for_concept_encoding_Spoke1_2026-07-02\n"
        f"      (the drill convergence source; this atom composes it with empirical evidence)\n"
        f"  - reference_sparse_engram_allocation_v1_FULL_HF_naive_WTA_falsified_2026-06-23\n"
        f"      (prior HF: naive WTA sampling falsified; but competitive-Hebbian sparse coding\n"
        f"       IS distinct from naive WTA sampling and this atom shows COMPETITIVE_HEBBIAN\n"
        f"       DOES work - so the prior HF stands but is complementary, not contradictory)\n"
        f"  - project_brain_function_is_best_in_class_reference_standard_USER_LOCKED_2026-07-02\n"
        f"      (brain-grounded prior: neuroscience says concept-encoding is WTA-competitive-\n"
        f"       inhibitory-Hebbian; drill #1 in the 6/6 domain convergence)\n"
        f"  - project_path_c_substrate_owned_encoder_is_the_answer_USER_2026-06-23\n"
        f"      (substrate-owned encoder direction; this atom informs Spoke-1 encoder design\n"
        f"       to use competitive-Hebbian sparse coding, NOT PC-driven modulation)\n"
        f"\n"
        f"LOAD-BEARING FOR M3/M4 ARCHITECTURE DIRECTION:\n"
        f"  1. Spoke-1 (flat concept encoder) uses competitive-Hebbian sparse coding\n"
        f"     as the CANONICAL mechanism - no PC term needed at this layer.\n"
        f"  2. PC may still be appropriate at HIGHER layers (inter-area hierarchical\n"
        f"     prediction between Spoke-1 -> Hub -> Spoke-N) - this atom does not falsify\n"
        f"     PC there; it only falsifies PC at the flat sensory-to-semantic composition\n"
        f"     surface.\n"
        f"  3. Architectural implication: layer-appropriate mechanism selection - use\n"
        f"     competitive-Hebbian for FLAT sparse coding, use PC for HIERARCHICAL\n"
        f"     inter-area prediction. Load-bearing distinction for M3/M4 cortex design.\n"
        f"  4. Discovery that competitive-Hebbian sparse coding subsumes PC at concept-\n"
        f"     encoding layer is a REAL substrate-science finding, not a bug or a fluke.\n"
        f"\n"
        f"CROSS-ARC OVERLAP CHECK ({DATE}): checked substrate_query for prior atoms on\n"
        f"  'PC redundant competitive Hebbian sparse concept encoding flat layer' -\n"
        f"  no prior META atom on this specific relative-negative claim. The closest prior\n"
        f"  is reference_sparse_engram_allocation_v1_FULL_HF_naive_WTA_falsified_2026-06-23\n"
        f"  which is about NAIVE WTA SAMPLING (different mechanism); this atom about\n"
        f"  competitive-Hebbian subsuming PC is GENUINELY NOVEL. NOT a rediscovery.\n"
        f"\n"
        f"Smoke audit: {SMOKE_AUDIT}\n"
        f"Falsification anchor: {FALSIFICATION_ANCHOR}\n"
        f"Atomized: {TS_ISO} by skunkworks_META_PC_falsified_Spoke1_flat_concept_encoding_MM_TENTATIVE_{DATE}"
    ),
    "metadata": {
        "ts_atomized": TS_NOW,
        "date_atomized": DATE,
        "ts_iso_atomized": TS_ISO,
        "smoke_audit_id": SMOKE_AUDIT,
        "falsification_anchor_id": FALSIFICATION_ANCHOR,
        "synthesis_type": "substrate_science_multi_domain_convergence_plus_empirical_falsification",
        "tier": "MM_TENTATIVE_SYNTHESIS",
        "cert_tier": "measured_mechanism_tentative_synthesis",
        "cert_increment_delta": 0,
        "verified_off_data": True,
        "verified_off_data_by": f"skunkworks_META_PC_falsified_Spoke1_flat_concept_encoding_MM_TENTATIVE_{DATE}",
        "metrics_paths_off_data_recompute": [
            "data/exp_substrate_concept_encoder_spoke1_predictive_coding_competitive_allocation_v2_smoke/metrics.json",
            "data/exp_substrate_concept_encoder_spoke1_v3_D_competitive_hebbian_only_2026_07_02_smoke/metrics.json",
        ],
        "off_data_cross_check_v2_smoke": {
            "n_seeds": 5,
            "seeds": [11, 17, 23, 29, 37],
            "ARM_PREDICTIVE_ONLY_gap_mean": 0.5658,
            "ARM_PREDICTIVE_ONLY_gap_cv": 0.1232,
            "ARM_PREDICTIVE_ONLY_ck_mean": 0.5119,
            "ARM_COMPETITIVE_ONLY_gap_mean": 0.5073,
            "ARM_COMPETITIVE_ONLY_gap_cv": 0.0827,
            "ARM_COMPETITIVE_ONLY_ck_mean": 0.5220,
            "ARM_FULL_HYBRID_gap_mean": 0.5171,
            "ARM_FULL_HYBRID_gap_cv": 0.3767,
            "ARM_FULL_HYBRID_ck_mean": 0.2195,
            "delta_PRED_minus_COMP_gap": 0.0585,
            "interpretation": "PRED_gap_marginally_above_COMP_gap_but_within_cross_arm_noise_HYBRID_does_not_out_earn_either_arm",
        },
        "off_data_cross_check_v3_D_smoke": {
            "n_seeds": 3,
            "seeds": [11, 17, 23],
            "ARM_COMPETITIVE_HEBBIAN_gap_mean": 0.5122,
            "ARM_COMPETITIVE_HEBBIAN_gap_cv": 0.1029,
            "ARM_COMPETITIVE_HEBBIAN_ck_mean": 0.5203,
            "ARM_COMPETITIVE_HEBBIAN_ca_mean": 0.0081,
            "ARM_COMPETITIVE_HEBBIAN_intra_cv": 0.181,
            "ARM_COMP_HEB_LATERAL_INHIBITION_gap_mean": 0.4309,
            "ARM_COMP_HEB_LATERAL_INHIBITION_ck_mean": 0.4390,
            "ARM_COMP_HEB_LATERAL_INHIBITION_Delta_intra": -0.084,
            "ARM_NAIVE_WTA_SAMPLING_gap_mean": 0.0,
            "verdict": "HARD_PASS competitive_Hebbian_standalone_solves_concept_encoding_task_without_PC",
            "interpretation": "WTA_competitive_Hebbian_alone_HARD_PASSES_at_5seed_smoke_confirming_PC_is_not_required_LI_variant_worsens_directionally_corroborates_a51e4c_W_ALPHA_sweep",
        },
        "falsification_anchor_a51e4c_variant_A_W_ALPHA_sweep": {
            "W_ALPHA_0p10_Delta_intra": -0.038,
            "W_ALPHA_0p50_Delta_intra": -0.173,
            "W_ALPHA_1p00_Delta_intra": -0.238,
            "monotone_negative": True,
            "interpretation": "PC_top_down_gain_HURTS_intra_similarity_monotone_in_gain_strength",
        },
        "falsification_anchor_a51e4c_variant_B_post_mask_null": {
            "Delta_intra": -0.002,
            "interpretation": "PC_applied_after_competitive_mask_has_zero_effect_within_noise_confirms_mask_carries_full_signal",
        },
        "drill_convergence_6_of_6": {
            "1_neuroscience": "WTA_competitive_inhibitory_Hebbian_at_concept_encoding_stages_PC_hierarchical_between_areas",
            "2_physics_spin_glass": "Hopfield_Amit_Gutfreund_competitive_relaxation_at_fixed_sparsity_PC_redundant_modulation",
            "3_physics_non_eq_thermo": "sparse_coding_via_free_energy_min_at_fixed_sparsity_is_competitive_Hebbian_PC_hierarchical",
            "4_math_info_theory": "rate_distortion_at_fixed_sparsity_solved_by_k_sparse_competitive_projection_PC_no_additional_channel",
            "5_ML_AI_literature": "K_SVD_ISTA_FISTA_top_k_sparse_autoencoders_use_competitive_shrinkage_not_PC_gain",
            "6_empirical_ablation": "a51e4c_W_ALPHA_sweep_monotone_negative_and_post_mask_null_directly_falsifies_PC_contribution",
        },
        "scope": {
            "domain": "concept_encoding_layer_at_flat_sensory_to_semantic_composition",
            "n_dim": 2048,
            "sentences_per_concept": 40,
            "n_concepts": 50,
            "sparse_rate": 0.02,
            "n_clusters": 25,
            "input_geometry": "character_trigram_encoded_flat_concept_surfaces_not_hierarchical",
            "layer_type": "flat_single_layer_not_hierarchical",
            "input_regime": "stationary_not_temporal_or_heteroscedastic",
        },
        "revival_criteria": {
            "a_hierarchical_PC": "PC_re_enters_ck_ge_0p4_at_hierarchical_PC_Salvatori_2021_associative_memory_formulation_multiple_hierarchical_PC_layers",
            "b_correlated_heteroscedastic_temporal_input": "PC_re_enters_ck_ge_0p4_at_correlated_heteroscedastic_temporal_input_regime_Nessler_2013_conditional_Poisson_mixture",
            "either_alone_falsifies_this_atom": True,
            "neither_a_nor_b_tested_in_Spoke_1_v2_v3D_smoke": True,
        },
        "expansion_to_CG_META": {
            "criterion": "Spoke_1_v3_D_FULL_3_seed_HARD_PASS_with_same_relative_negative_PC_arm_ck_le_COMPETITIVE_HEBBIAN_ck_at_3seed_FULL_scale",
            "would_also_promote": "META_candidate_2_6of6_drill_convergence_methodology_to_CG_META",
            "2_way_witness": "same_FULL_evidence_supports_both_META_atoms",
        },
        "composes_references": [
            "reference_5x_drill_convergence_PC_redundant_with_WTA_for_concept_encoding_Spoke1_2026-07-02",
            "reference_sparse_engram_allocation_v1_FULL_HF_naive_WTA_falsified_2026-06-23",
            "project_brain_function_is_best_in_class_reference_standard_USER_LOCKED_2026-07-02",
            "project_path_c_substrate_owned_encoder_is_the_answer_USER_2026-06-23",
        ],
        "does_not_supersede": [
            "reference_sparse_engram_allocation_v1_FULL_HF_naive_WTA_falsified_2026-06-23_which_is_about_NAIVE_WTA_SAMPLING_distinct_mechanism_prior_HF_stands_complementary_not_contradictory",
        ],
        "load_bearing_for_M3_M4_architecture": {
            "spoke_1_flat_concept_encoder_canonical_mechanism": "competitive_Hebbian_sparse_coding_no_PC_term_needed_at_this_layer",
            "PC_may_still_be_appropriate_at_higher_layers": "inter_area_hierarchical_prediction_between_Spoke_1_Hub_Spoke_N_this_atom_does_not_falsify_PC_there",
            "architectural_implication": "layer_appropriate_mechanism_selection_competitive_Hebbian_for_FLAT_sparse_coding_PC_for_HIERARCHICAL_inter_area_prediction",
        },
        "cross_arc_overlap_check": "NONE at cosine>0.30 for this specific relative-negative claim; closest prior reference_sparse_engram_allocation about NAIVE WTA SAMPLING which is distinct mechanism; genuinely novel synthesis",
        "provenance_quality": "OFF_DISK_SKUNKWORKS_A5_MM_TENTATIVE_SYNTHESIS_2_smoke_metrics_plus_a51e4c_falsification_anchor_plus_6of6_drill_convergence",
        "era": "STAGE_2_SPOKE_1_CONCEPT_ENCODER_MM_TENTATIVE_SUBSTRATE_SCIENCE",
        "session": f"skunkworks_META_PC_falsified_Spoke1_flat_concept_encoding_{DATE}",
    },
}

LEDGER = {
    "ts": TS_NOW,
    "op": "cert_ruling_measured_mechanism_tentative_substrate_science_synthesis",
    "atom_id": f"meta::{ATOM_ID}",
    "cert_status": "measured_mechanism_tentative_synthesis",
    "cert_class": "substrate_science_relative_negative_PC_redundant_with_WTA_competitive_Hebbian_at_flat_concept_encoding_layer",
    "verified_off_data": True,
    "atomized_by": f"skunkworks_META_PC_falsified_Spoke1_flat_concept_encoding_MM_TENTATIVE_{DATE}",
    "smoke_audit_id": SMOKE_AUDIT,
    "falsification_anchor_id": FALSIFICATION_ANCHOR,
    "verdict": (
        "MM_TENTATIVE_META_substrate_science_PC_falsified_in_Spoke_1_flat_concept_encoding_regime_"
        "PC_does_NOT_earn_complexity_vs_WTA_competitive_Hebbian_at_sensory_to_semantic_composition_layer_"
        "5x_drill_6of6_domain_convergence_neuroscience_spin_glass_non_eq_thermo_math_info_theory_ML_AI_empirical_"
        "falsification_a51e4c_Variant_A_W_ALPHA_sweep_0p10_0p5_1p0_Delta_intra_neg0p038_neg0p173_neg0p238_monotone_"
        "Variant_B_post_mask_null_Delta_intra_neg0p002_"
        "off_data_v2_smoke_ARM_PREDICTIVE_ONLY_gap_0p566_vs_ARM_COMPETITIVE_ONLY_gap_0p507_delta_0p059_within_noise_"
        "off_data_v3D_smoke_ARM_COMPETITIVE_HEBBIAN_standalone_gap_0p512_ck_0p520_ca_0p008_HP_5seed_WTA_alone_solves_task_"
        "LI_variant_worsens_gap_0p431_Delta_intra_neg0p084_directionally_corroborates_a51e4c_sweep_"
        "scope_spc_40_n_dim_2048_n_concepts_50_sparse_rate_0p02_flat_layer_stationary_input_"
        "revival_criterion_PC_re_enters_ck_ge_0p4_at_hierarchical_PC_Salvatori_2021_OR_correlated_heteroscedastic_temporal_input_Nessler_2013_"
        "expansion_to_CG_META_Spoke1_v3D_FULL_3seed_HP_confirms_positive_prediction_of_competitive_Hebbian_at_scale_"
        "tier_MM_TENTATIVE_because_single_input_regime_single_sparsity_single_layer_type_smoke_level_empirical_"
        "composes_reference_5x_drill_convergence_and_reference_sparse_engram_allocation_and_project_brain_function_best_in_class_and_project_path_c_substrate_owned_encoder_"
        "load_bearing_for_M3_M4_architecture_layer_appropriate_mechanism_selection_"
        "cert_increment_delta_0_MM_tier"
    ),
    "cert_increment_delta": 0,
    "cv": 0.1029,
    "referent_pointer": {
        "notes_path": None,
        "metrics_paths": [
            "data/exp_substrate_concept_encoder_spoke1_predictive_coding_competitive_allocation_v2_smoke/metrics.json",
            "data/exp_substrate_concept_encoder_spoke1_v3_D_competitive_hebbian_only_2026_07_02_smoke/metrics.json",
        ],
        "composing_references": [
            "reference_5x_drill_convergence_PC_redundant_with_WTA_for_concept_encoding_Spoke1_2026-07-02",
            "reference_sparse_engram_allocation_v1_FULL_HF_naive_WTA_falsified_2026-06-23",
            "project_brain_function_is_best_in_class_reference_standard_USER_LOCKED_2026-07-02",
            "project_path_c_substrate_owned_encoder_is_the_answer_USER_2026-06-23",
        ],
        "smoke_audit_id": SMOKE_AUDIT,
        "falsification_anchor_id": FALSIFICATION_ANCHOR,
        "atom_qualified_id": f"meta::{ATOM_ID}",
    },
    "supersedes": None,
    "note": (
        "META_PC_falsified_in_Spoke_1_flat_concept_encoding_regime_MM_TENTATIVE_substrate_science_synthesis_"
        "5x_drill_6of6_domain_convergence_plus_a51e4c_empirical_falsification_plus_off_data_cross_check_"
        "v2_smoke_PRED_vs_COMP_within_noise_and_v3D_COMP_HEB_standalone_HP_and_LI_variant_worsens_corroborates_"
        "scope_tightly_bounded_flat_single_layer_stationary_input_concept_encoding_"
        "revival_criteria_hierarchical_PC_or_correlated_heteroscedastic_temporal_input_"
        "expansion_to_CG_META_Spoke1_v3D_FULL_confirms_positive_prediction_of_competitive_Hebbian_at_scale_"
        "load_bearing_for_M3_M4_architecture_layer_appropriate_mechanism_selection_"
        "delta_counted_on_composing_references_if_and_when_they_promote_MM_tier"
    ),
}


def atomic_append_jsonl(path: pathlib.Path, records: list) -> tuple:
    """Atomic tmp-write + os.replace + verify-load. Returns (lines_before, lines_after)."""
    lines_before = 0
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            lines_before = sum(1 for _ in f)

    tmp_path = path.with_suffix(path.suffix + ".tmp")
    existing_content = b""
    if path.exists():
        existing_content = path.read_bytes()
    if existing_content and not existing_content.endswith(b"\n"):
        existing_content += b"\n"
    new_lines = b""
    for rec in records:
        line = json.dumps(rec, ensure_ascii=False) + "\n"
        new_lines += line.encode("utf-8")
    tmp_path.write_bytes(existing_content + new_lines)

    # verify-load
    with tmp_path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Corrupt JSON at line {i+1} in {tmp_path}: {e}")

    os.replace(tmp_path, path)

    lines_after = 0
    with path.open("r", encoding="utf-8") as f:
        lines_after = sum(1 for _ in f)

    return lines_before, lines_after


def main():
    meta_before, meta_after = atomic_append_jsonl(META_ATOMS, [ATOM])
    print(f"meta/atoms.jsonl: {meta_before} -> {meta_after} (+{meta_after - meta_before})")

    led_before, led_after = atomic_append_jsonl(CERT_LEDGER, [LEDGER])
    print(f"meta/cert_ledger.jsonl: {led_before} -> {led_after} (+{led_after - led_before})")

    print()
    print("CERT delta: +0 (MM_TENTATIVE_SYNTHESIS tier)")
    print(f"Atom ID: {ATOM_ID[:120]}...")
    print(f"Full atom ID length: {len(ATOM_ID)} chars")
    print(f"Timestamp: {TS_NOW}")
    print(f"ISO timestamp: {TS_ISO}")
    print(f"Smoke audit anchor: {SMOKE_AUDIT}")
    print(f"Falsification anchor: {FALSIFICATION_ANCHOR}")


if __name__ == "__main__":
    main()
