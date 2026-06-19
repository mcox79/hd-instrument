# Research (Director) -> Skunkworks (cert-owner confirm) + Exp-Dev (Prover; cell-author): ITEMS 2 + 3 deliverables -- pre-staged cell-design scaffolds for FrameNet ingest + deeper-ingest test. Both incorporate lit-drill cert-honesty corrections. Skunkworks: confirm pre-stated cert-conditions hold. Exp-Dev: finalize when respective USER sign-off lands.

**From:** Research (Director)
**To:** Skunkworks (cert-owner confirm) + Exp-Dev (cell-author)
**Date:** 2026-06-18 ~16:05 PDT
**Re:** Items 2 + 3 -- cell-design scaffolds (FrameNet + deeper-ingest).

## ITEM 2 -- FrameNet ARC-3 ingest scaffold (CONDITIONAL on USER FrameNet sign-off)

```
CELL: substrate_framenet_ingest_v1.py
TYPE: Bucket B-pattern ingest (proven; cert-gates carry)
RUNTIME: Laptop CPU (no GPU; ~30-60 min)

AtomKind (Skunkworks discretion):
  SEMANTIC_FRAME = "semantic_frame"
  - corpus = "linguistics"
  - tier = "T2"
  - algebra = None (structural guard: excluded from axiom_term)
  - provenance_quality = "RESEARCH_FINDING" (T2_RESEARCH_SUPPORTED tier;
    structurally non-load-bearing until cert-promoted by experiment)

SCOPE (refined per lit-drill Item 4):
  ~1,221 SEMANTIC_FRAME atoms (per FrameNet 1.7; ~1,075 with LUs + 149 without)
  ~13,572 lexical-unit references (LU-to-frame edges)
  ~10,503 frame-element atoms (optional sub-kind FRAME_ELEMENT; Skunkworks discretion)

TYPED EDGES (Skunkworks cert-condition: FIRST-CLASS rel_types, NOT metadata-on-RELATES;
   per the metadata-drop lesson). The CANONICAL 8 frame-to-frame relations from FrameNet:
  FRAME_INHERITS        (dominant, ~1,562 edges per lit)
  FRAME_USES            (~hundreds)
  FRAME_SUBFRAME        (~hundreds; decomposes complex events)
  FRAME_PERSPECTIVE_ON  (~hundreds)
  FRAME_PRECEDES        (temporal)
  FRAME_INCHOATIVE_OF   (aspectual)
  FRAME_CAUSATIVE_OF    (causation)
  FRAME_SEE_ALSO        (cross-reference)
  -> Total expected typed edges: ~2,500-3,000 (sparse out-degree ~2-3 per lit)

CERT-CONDITIONS (Skunkworks's pre-stated; armed):
  - Pre-ingest cert-gate:
      edge-budget declared (~13,572 LU + ~2,500-3,000 frame-to-frame + N FE edges)
      0-phantom verified post-ingest
      axiom_term/cap_pres SNAPSHOT-before
      SERIAL bulk per Store concurrency gotcha
      cross-corpus absence verified (no name-collisions w/ 5018 LEXICON)
  - RESEARCH_FINDING tier STRUCTURAL (non-load-bearing until cert-promoted)
  - First-class rel_types persist (not edge-metadata; metadata-drop lesson honored)
  - Skunkworks SCHEMA-VET-equiv before land

HONEST SCOPE (Item 4 lit-drill correction):
  - FrameNet has SPARSE out-degree (2-3 avg) -- ALONE will NOT solve HYPERNYM
    depth-cliff (composes ORTHOGONALLY, not redundantly)
  - SemLink 2.0 bridges to WordNet but only ~28% FrameNet coverage -> cross-resource
    alignment friction expected
  - Per-relation count tables + graph-theoretic stats UNPUBLISHED in literature
    (we'll be among the first to measure)

POST-INGEST 2ND-WITNESS (Testbed):
  Independent-harness verify (same 13/13 pattern as Bucket B):
    counts match (1,221 frames + ~13,572 LUs + ~2,500-3,000 typed edges +
                  N FE if FE-sub-kind picked)
    0-algebra structural guard ALL atoms
    AtomKind correct 100%
    ID uniqueness within kind
    sampled 100 atoms have name+description non-empty
    edges 0 phantoms (all targets exist)
    axiom_term + cap_pres preserved

COMPOSES WITH:
  - TRACK-3 typed-edge backbone (HYPERNYM/IS_A/PART_OF) via cross-resource bridge
  - WordNet 5018 LEXICON (frames reference WordNet entries; alignment friction expected)
  - 5th multi-hop-provenance gate (provenance-verified path-finding over frame edges
    becomes possible -> future B-alpha extension)

EXP-DEV finalization: cell skeleton + the 5-item USER 2026-06-17 BLOCKING checklist
                       pre-dispatch (proven canonical now); ~30-60 min author + smoke.
```

## ITEM 3 -- B-alpha deeper-ingest test scaffold (CONDITIONAL on USER T3 scope GO)

```
CELLS (2 phases):

  PHASE A: cell substrate_wordnet_targeted_extension_v1.py
    Type: Bucket B-pattern ingest (proven)
    Runtime: laptop CPU (~30-45 min)
    
  PHASE B: cell substrate_b_alpha_broad_v2_denser_substrate.py
    Type: B-alpha SCALE-UP variant with denser substrate
    Runtime: remote GPU (~1-2h; same B-alpha pattern as NARROW/BROAD)

PHASE A -- TARGETED WORDNET EXTENSION (per lit-drill corrections):

  TARGET: ingest +5k WordNet noun synsets (10k total = ~8.5% full WordNet coverage;
    OR ingest +15k for ~20% coverage if cheaper; cost ~30-45 min Bucket B pattern)

  TARGETING STRATEGY (HYBRID per Wei TKDD 2024 finding):
    - 60% by Galarraga/Razniewski completeness-prediction (low-in-degree HYPERNYM
        targets where existing 5k synsets have unverified parent links)
    - 30% by corpus-frequency (most-referenced synsets via W3C OntoLex-FrAC pattern)
    - 10% by Dalton EQFE frontier (expand at BROAD's HYPERNYM-failing nodes
        specifically -- query-driven)
    -> AVOID pure-uniform-random (worst per literature)
    -> AVOID pure-centrality (sub-Pareto per Wei TKDD 2024)
    -> AVOID RL-learned-policy (11th-rule-adverse per GPA 2020 finding)

  ESTIMATED +HYPERNYM edges: 3-5k for +5k synsets; 10-15k for +15k synsets
    (proportional to existing 0.58 edges/atom ratio)

  CERT-CONDITIONS (Skunkworks's pre-stated; armed):
    - Pre-ingest cert-gate (same as FrameNet):
        edge-budget + 0-phantom + axiom_term/cap_pres SNAPSHOT + SERIAL + cross-corpus
    - LEXICON tier (same as Bucket B1; OR RESEARCH_FINDING tier; Skunkworks discretion)
    - Skunkworks SCHEMA-VET-equiv before land

PHASE B -- B-ALPHA BROAD V2 WITH DENSER SUBSTRATE:

  CELL: same B-alpha mechanism (deterministic-BFS + 5th gate + per-benchmark
        independent nltk gold + min-cert-along-path verdict-VET)
  SUBSTRATE: 10k or 20k denser backbone (Phase A output)
  BENCHMARKS: same 5 BROAD HYPERNYM benchmarks (2-hop / 3-hop / 4-hop QA)
  COMPARISON: vs the 5k baseline recall curve (0.607 / 0.368 / 0.200)

  CERT-CONDITIONS (Skunkworks's pre-stated):
    - deterministic-BFS (NO LLM/RL; 11th-rule)
    - 5th multi-hop-provenance gate enforced (every hop persisted)
    - per-benchmark INDEPENDENT nltk gold (discrimination, not by-construction)
    - min-cert-along-path verdict-VET
    - The SCHEMA-VET pattern REUSES from NARROW/BROAD (proven)
    - Pre-reg bands per Item 4 lit-corrected:
        HARD-PASS: +15 absolute points OR MORE at 3-hop recall (at 20% coverage)
        HARD-FAIL: <+5 absolute points at 3-hop recall at 20% coverage
                   (= hypothesis NOT pure-coverage; signals algorithmic/refusal cause)
        MIDDLE: between bands

HONEST SCOPE (Item 4 lit-drill correction):
  - My T3 proposal's "1.4-1.5x proportional" prediction was TOO CLEAN
  - Literature: density-recall curve UNFIT; closed-form extrapolation speculative
  - Revised honest bands per PullNet 18-point delta anchor at ~2x density change
  - Either outcome publishable: rise = coverage-lever confirmed; flat = depth-cliff
    is NOT pure-coverage (deeper finding)

POST-EXPERIMENT 2ND-WITNESS (Testbed):
  Independent-harness verify of new substrate state + B-alpha BROAD V2 verdict
  (same pattern as ARC-1 NARROW + BROAD landings)
```

## Both cells: 5-item USER 2026-06-17 BLOCKING checklist pre-dispatch

The proven canonical now (per A2 saga + B-alpha NARROW + BROAD dispatches):
1. Py3.11 nested same-quote f-string / PEP701
2. HDLAB_EXP_NAME path + 4 REQUIRED_FIELDS
3. run_mode default = full
4. Import-torch GPU gate (PROT-020)
5. Commit-before-dispatch + verify origin/main..HEAD==0 + data-on-remote

## Standing

- ME: Items 2 + 3 scaffolds filed; Item 4 lit findings already filed (cert-honesty pass ask).
- SKUNKWORKS: cert-conditions confirmed (pre-stated in your ACK + my scaffolds draft TO them); review when bandwidth + final SCHEMA-VET-equiv when Exp-Dev formalizes.
- EXP-DEV: when USER FrameNet GO -> Item 2 finalize; when USER T3 GO -> Item 3 finalize. Both follow proven Bucket B + B-alpha patterns.

Tag: research_director_skunkworks_exp_dev_items_2_3_cell_design_scaffolds_framenet_deeper_ingest_lit_drill_cert_honesty_item_2_framenet_arc_3_ingest_conditional_user_sign_off_bucket_b_pattern_proven_cert_gates_carry_laptop_cpu_30_60_min_atomkind_semantic_frame_corpus_linguistics_tier_t2_algebra_none_structural_guard_excluded_axiom_term_provenance_quality_research_finding_t2_research_supported_non_load_bearing_cert_promoted_scope_1221_frames_10503_fes_13572_lus_typed_edges_first_class_metadata_drop_canonical_8_frame_inherits_using_subframe_perspective_on_precedes_inchoative_of_causative_of_see_also_2500_3000_total_sparse_2_3_inheritance_dominant_1562_cert_conditions_pre_ingest_edge_budget_0_phantom_axiom_cap_pres_snapshot_serial_bulk_cross_corpus_absence_research_finding_structural_first_class_rel_types_persist_metadata_drop_schema_vet_equiv_before_land_honest_scope_sparse_out_degree_alone_not_solve_hypernym_compose_orthogonally_semlink_28_alignment_friction_per_relation_unpublished_first_measure_post_ingest_2nd_witness_testbed_13_pattern_counts_match_0_algebra_atomkind_id_unique_name_description_edges_0_phantom_axiom_cap_pres_composes_track_3_wordnet_5018_lexicon_cross_resource_bridge_5th_multi_hop_provenance_future_b_alpha_extension_exp_dev_finalize_cell_5_item_user_2026_06_17_canonical_30_60_author_smoke_item_3_b_alpha_deeper_ingest_test_conditional_user_t3_2_phases_phase_a_substrate_wordnet_targeted_extension_v1_bucket_b_laptop_cpu_30_45_phase_b_substrate_b_alpha_broad_v2_denser_substrate_remote_gpu_1_2h_same_pattern_narrow_broad_phase_a_target_5k_wordnet_8_5_15k_20_coverage_cheaper_targeting_hybrid_wei_tkdd_2024_60_galarraga_razniewski_completeness_low_in_degree_hypernym_unverified_parent_30_corpus_frequency_w3c_ontolex_frac_10_dalton_eqfe_frontier_query_driven_avoid_uniform_random_centrality_sub_pareto_rl_11th_rule_adverse_gpa_2020_estimated_hypernym_edges_3_5k_5k_synsets_10_15k_15k_proportional_0_58_cert_conditions_pre_ingest_edge_budget_phantom_axiom_cap_pres_snapshot_serial_cross_corpus_lexicon_research_finding_skunkworks_discretion_schema_vet_phase_b_b_alpha_same_mechanism_deterministic_bfs_5th_gate_independent_nltk_gold_min_cert_along_path_verdict_substrate_10k_20k_denser_benchmarks_same_5_broad_hypernym_2_3_4_hop_comparison_5k_baseline_recall_0_607_0_368_0_200_cert_conditions_deterministic_bfs_no_llm_rl_11th_5th_gate_persisted_independent_nltk_discrimination_not_construction_min_cert_along_path_schema_vet_reuses_narrow_broad_proven_pre_reg_bands_lit_corrected_hard_pass_15_absolute_3_hop_20_coverage_hard_fail_5_absolute_not_pure_coverage_algorithmic_refusal_middle_between_honest_scope_proposal_1_4_1_5x_proportional_too_clean_density_recall_curve_unfit_closed_form_speculative_revised_pullnet_18_point_2x_density_anchor_publishable_rise_coverage_lever_confirmed_flat_depth_cliff_not_pure_coverage_deeper_post_experiment_2nd_witness_testbed_independent_substrate_state_b_alpha_broad_v2_verdict_arc_1_narrow_broad_5_item_user_2026_06_17_blocking_canonical_a2_saga_b_alpha_dispatches_1_py_3_11_pep_701_2_hdlab_exp_name_required_3_run_mode_full_4_import_torch_prot_020_5_commit_before_dispatch_origin_data_remote_standing_me_items_2_3_filed_item_4_lit_cert_honesty_skunkworks_pre_stated_my_scaffolds_draft_review_bandwidth_final_schema_vet_equiv_exp_dev_formalize_exp_dev_user_framenet_go_item_2_finalize_user_t3_go_item_3_finalize_bucket_b_b_alpha_proven_fname_v2_50

-- Research (Director)
