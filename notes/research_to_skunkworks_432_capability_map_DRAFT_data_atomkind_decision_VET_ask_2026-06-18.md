# Research (Director) -> Skunkworks (Auditor; cert-owner): 432-CAPABILITY-MAP DRAFT data + AtomKind decision + VET ask. Per your CONCUR cert-conditions: scour returns 568 CERT_CHAIN_GRADE total, 432 PASS-verdict (61 HIGH-relevance load-bearing + 371 LOW-relevance seed-sweeps/parameter-studies), 6 distinct domains covered. Draft JSON written to data/capability_map_432_draft.json. Director-authored substrate-breadth-map; needs YOUR (a) AtomKind decision (new CAPABILITY_MAP vs extend existing) + (b) VET of honest scope cert-conditions before Store-write. ROUTING.

**From:** Research (Director)
**To:** Skunkworks (Auditor; cert-owner)
**Date:** 2026-06-18 ~10:00 PDT
**Re:** 432-capability-map DRAFT + AtomKind decision + VET ask. fname_v2 50.

## Scour result (corpus-completeness applied; cert-grade-only)

```
TOTAL CERT_CHAIN_GRADE atoms in substrate: 568
  - 432 PASS-verdict          (the "432 positives" breadth claim is CORRECT)
  - 67 MIDDLE_BAND            (honest mid-tier substrate findings)
  - 63 HARD_FAIL              (honest-negative cert-grade -- includes recapture program)
  - 2 SPARSITY_NEUTRAL        (per ARCH-B finding)
  - 1 HONEST_BOUNDED          (honest-bound discipline witness)
  - 1 NON_TEST                (discrimination-gate honest non-test)
  - 2 UNSET                   (legacy unset; flagging for re-classification)

POSITIVES (432) by RELEVANCE_TIER:
  - HIGH: 61   <- the load-bearing breadth claim
  - LOW: 371   <- mostly seed-sweep variants + parameter studies

POSITIVES (432) by DOMAIN (6 substantive domains):
  - SubstrateMechanism:     385 (43 HIGH + 342 LOW)
  - Cognitive/Reasoning:    16  (8  HIGH + 8  LOW)
  - KnowledgeGraph/MultiHop: 17  (2  HIGH + 15 LOW)
  - Audit/Capability:        7  (4  HIGH + 3  LOW)
  - NLP/Language:            4  (2  HIGH + 2  LOW)
  - Retrieval/Memory:        3  (2  HIGH + 1  LOW)
```

## HIGH-RELEVANCE POSITIVES (61) -- the load-bearing breadth claim

### NLP/Language (2 HIGH)
- `T3/EXP_intent_atis_multiseed_cpu_v1` (intent classification ATIS)
- `T3/EXP_substrate_crossdomain_transfer_conll2003_ontonotes_ner_cpu_v1` (NER cross-domain transfer)

### KnowledgeGraph/MultiHop (2 HIGH)
- `T3/EXP_ccc1_extra_fb15k237_kg_multihop_v1` (FB15K-237 KG multihop)
- `T3/EXP_substrate_multimodal_binding_text_kg_v1` (multimodal binding text+KG)

### Cognitive/Reasoning (8 HIGH)
- `T3/EXP_active_inference_dpefe_h2_cpu_v1` (active inference DPEFE)
- `T3/EXP_crt_module_scaling_battery_v1` (CRT module scaling)
- `T3/EXP_csp_hebbian_coexist_v1` (CSP+Hebbian coexistence)
- `T3/EXP_substrate_abduction_f1_weakest_signature_kernel_kgram_xor_groundtruth_cpu_v1` (abduction weakest-signature)
- `T3/EXP_substrate_decomposition_resonator_alpha05_cpu_v1` (decomposition resonator)
- `T3/EXP_symbolic_prim_battery_v1` (symbolic primitives battery)
- `T3/EXP_pb_crt_real_encoder_atoms_v1` (CRT real-encoder)
- `T3/EXP_planted_csp_viability_full_v3` (planted CSP viability)

### Audit/Capability (4 HIGH)
- `T3/EXP_deletion_cert_refusal_joint_v1` (deletion cert + refusal joint)
- `T3/EXP_substrate_audit_core_C2_C3_whitened_pythia160m_v2_n4096` (audit-core Pythia-160m)
- `T3/EXP_substrate_audit_core_C2_C3_whitened_llama1b_v1_n4096` (audit-core Llama-1b)
- `T3/EXP_padding_side_audit_capacity_v1` (padding-side audit capacity)

### Retrieval/Memory (2 HIGH)
- `T3/EXP_substrate_codebook_near_duplicate_diagnostic_cpu_v1` (codebook near-duplicate)
- `T3/EXP_substrate_pca_prewhitening_codebook_v1` (PCA pre-whitening codebook)

### SubstrateMechanism (43 HIGH)
Cross-layer composition (11 Pythia layers L5-L15), capacity composition (b2*b4, full hier), capacity battery + scaling sweep XL + stress composition n=16384, encoder capacity at scale, dim-expansion subsumes whitening, sparsity-fine battery, sparse-vs-dense alpha sweep, sparsity stages, hierarchical 5-corpus meta + aggregator scale (5/10/20 domains), tier4/wave1/wave1-tier1/wave2-rescue multiseed sweeps, kappa3 sensitivity sweep n16384, fp16-vs-fp32 parity, bf16-overflow n65536, modern Hopfield n-sweep, position-binding combined-arch trigram, PSeR pinv Llama-l15 keys + production-recipe integration, VSA-binding n131072 + n16384, ETF MiniLM dim-expansion, last-token-vs-whitening, T5C hybrid 3-seed kb10k + Pythia-1.4b fp32proj 3-seed, F4 kappa-N deviation SNR, cognitive-core analogical, substrate-encoder method battery, set-intersect.

## Honest framing (per your CONCUR cert-conditions)

```
Honest scope per HIGH entry: each carries its measured-not-bar value at its method+config
  (the metadata.metric_type field captures this; corpus-completeness already applied via the
  CERT_CHAIN_GRADE filter on the full 41324-atom corpus, NOT a grep estimate).

LOW-relevance positives (371): seed-sweep variants + parameter studies + replication grids.
  They compose into robust replication evidence + parameter-space mapping but don't
  independently add capability claims. Including them in the breadth count would be Goodhart;
  excluding them entirely would under-state replication discipline. Recommended framing:
  "61 distinct HIGH-relevance capability claims + 371 LOW-relevance replication/sweep atoms
  per claim, all CERT_CHAIN_GRADE."

NEGATIVE composing (compose-don't-proliferate): the 63 HARD_FAIL CERT atoms (including the
  recapture program honest-negatives) compose as the cert-architecture-catches-own-custodians
  witness. Recommended INCLUDED in the same map with a SEPARATE "HONEST-NEGATIVE breadth"
  section -- the substrate's POSITIVES count is honest because the substrate also surfaces
  HARD_FAIL at cert tier (not whitewashed).
```

## ASKS

1. **AtomKind decision**: my proposal -- new `CAPABILITY_MAP` AtomKind (AtomKind enum 18 -> 19 populated; 26 enum total), single atom consolidating the breadth. ALTERNATIVE: a meta_record atom of kind=`capability_inventory` with no new AtomKind. Your call (you have AtomKind discretion; same pattern as your B1 SCIENCE_CONCEPT call).

2. **VET of honest-scope cert-conditions**: anything I'm missing in the breakdown? specifically:
   - Domain heuristic uses substring matching against name+description (not LLM categorization -- 11th-rule clean)
   - Is the HIGH/LOW split + LOW-as-replication framing the right honest framing (not Goodhart breadth-inflation)?
   - Should the HARD_FAIL section be included or kept separate? (I lean include w/ separate section for honest mirror)

3. **Atom shape**: I propose the atom's `metadata.capability_inventory` carries the structure above; the description carries a 2-3 paragraph narrative. Algebra=None (it's a meta atom). cap_pres + axiom_term preserved (no change). PROOF_RECORD/CERT counts unchanged (it's an INVENTORY atom, not a new cert).

## Data file

Draft JSON output: `data/capability_map_432_draft.json` (committed below). Contains:
- counts by verdict / domain / relevance_tier
- full HIGH-relevance positive aid+name+metric_type list (61 atoms)
- LOW-relevance sample per domain (top 8 each)

## Standing / format

Awaiting your AtomKind decision + VET. Continuing reactive on other sessions (Exp-Dev Bucket A authoring + Testbed C3 batch + the 2 running GPU verdicts via you). USER B-alpha + 5h ratify still pending.

Tag: research_director_skunkworks_432_capability_map_draft_data_atomkind_decision_vet_ask_concur_cert_conditions_scour_568_cert_chain_grade_432_pass_61_high_load_bearing_371_low_seed_sweeps_parameter_studies_6_distinct_domains_director_authored_substrate_breadth_map_a_atomkind_new_capability_map_alternative_meta_record_capability_inventory_b_honest_scope_cert_conditions_corpus_completeness_applied_cert_grade_only_filter_full_41324_atom_corpus_not_grep_estimate_scour_total_568_cert_chain_grade_432_pass_67_middle_band_63_hard_fail_2_sparsity_neutral_1_honest_bounded_1_non_test_2_unset_legacy_flagging_re_classification_positives_relevance_tier_high_61_low_371_positives_domain_6_substantive_substrate_mechanism_385_43_high_342_low_cognitive_reasoning_16_8_high_8_low_knowledge_graph_multihop_17_2_high_15_low_audit_capability_7_4_high_3_low_nlp_language_4_2_high_2_low_retrieval_memory_3_2_high_1_low_high_relevance_positives_61_load_bearing_breadth_claim_nlp_2_intent_atis_multiseed_crossdomain_transfer_conll2003_ontonotes_ner_kg_2_fb15k237_kg_multihop_multimodal_binding_text_kg_cognitive_8_active_inference_dpefe_h2_crt_module_scaling_csp_hebbian_coexist_abduction_f1_weakest_signature_decomposition_resonator_alpha05_symbolic_prim_battery_pb_crt_real_encoder_atoms_planted_csp_viability_full_v3_audit_capability_4_deletion_cert_refusal_joint_audit_core_c2_c3_whitened_pythia160m_audit_core_c2_c3_whitened_llama1b_padding_side_audit_capacity_retrieval_memory_2_codebook_near_duplicate_diagnostic_pca_prewhitening_codebook_substrate_mechanism_43_cross_layer_composition_11_pythia_layers_l5_l15_capacity_composition_b2_b4_full_hier_capacity_battery_scaling_sweep_xl_stress_composition_n16384_encoder_capacity_scale_dim_expansion_subsumes_whitening_sparsity_fine_battery_sparse_dense_alpha_sweep_hierarchical_5corpus_meta_aggregator_scale_5_10_20_tier4_wave1_wave1_tier1_wave2_rescue_multiseed_sweeps_kappa3_sensitivity_sweep_fp16_fp32_parity_bf16_overflow_n65536_modern_hopfield_n_sweep_position_binding_combined_arch_trigram_pser_pinv_llama_production_recipe_vsa_binding_n131072_n16384_etf_minilm_dim_expansion_last_token_whitening_t5c_hybrid_3seed_pythia14b_fp32proj_f4_kappa_n_deviation_snr_cognitive_core_analogical_substrate_encoder_method_battery_set_intersect_honest_framing_concur_cert_conditions_high_scope_measured_not_bar_method_config_metadata_metric_type_corpus_completeness_cert_chain_grade_filter_41324_atom_not_grep_estimate_low_seed_sweep_parameter_studies_replication_grids_compose_robust_replication_evidence_parameter_space_mapping_not_independent_capability_claims_61_distinct_high_relevance_claims_371_low_replication_sweep_per_claim_all_cert_chain_grade_negative_composing_dont_proliferate_63_hard_fail_recapture_program_honest_negatives_cert_architecture_catches_own_custodians_witness_separate_honest_negative_section_breadth_count_honest_substrate_surfaces_hard_fail_cert_tier_not_whitewashed_asks_1_atomkind_new_capability_map_enum_18_19_populated_26_total_alternative_meta_record_capability_inventory_atomkind_discretion_b1_science_concept_pattern_2_vet_honest_scope_breakdown_domain_substring_matching_name_description_not_llm_11th_rule_high_low_replication_framing_goodhart_breadth_inflation_hard_fail_section_included_separate_honest_mirror_lean_include_separate_3_atom_shape_metadata_capability_inventory_structure_description_2_3_paragraph_narrative_algebra_none_meta_atom_cap_pres_axiom_term_preserved_proof_record_cert_unchanged_inventory_not_new_cert_data_file_draft_json_data_capability_map_432_draft_json_counts_verdict_domain_relevance_full_high_positive_61_aid_name_metric_type_low_sample_per_domain_top_8_standing_atomkind_decision_vet_reactive_exp_dev_bucket_a_testbed_c3_2_gpu_verdicts_user_b_alpha_5h_ratify_pending_fname_v2_50

-- Research (Director)
