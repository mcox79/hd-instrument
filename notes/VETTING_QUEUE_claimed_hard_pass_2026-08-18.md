# VETTING QUEUE -- 199 CLAIMED HARD_PASS AWAITING VERIFICATION (2026-08-18)

**WHY THIS EXISTS.** The owner said our snapshot of progress was badly out of date. It was.
`tools/substrate_query.sh` -- the MANDATORY prior-work check -- returns ZERO BYTES and exits 0,
so every "no prior work found" report was vacuous and `STATUS.md` got assembled from whatever
the Director happened to stumble into. `tools/experiment_index.py` (dc408b95e) replaced it and
found **2,678 HARD_PASS** across 8,834 cells, **236 of them meaning-relevant**, including **25
that landed on 2026-08-17, the day before the session that ignored them.**

**A HARD_PASS HERE IS A CLAIM, NOT A CAPABILITY.** Five apparently clean wins died to their own
controls in ONE session on 2026-08-18; 21 arms are suspended for a bar imported across
representations; one queue entry is explicitly `PENDING_VET`. **This is a list of things to
CHECK, not a list of things we have.**

**RANKING.** The owner asked for newest-first AND reading/word-learning-first, and said "both",
so both axes are applied jointly: relevance tier first, recency within tier.

**WHAT VETTING MEANS HERE** (the bar this project already set, not a new one):
1. FAIR TEST -- can-fail, one variable, a REAL baseline that was actually run standalone.
2. FLOORS RECOMPUTED on that cell's OWN representation and population -- nothing imported.
3. CI-SEPARATED margin over the STRONGEST floor, read from the CI LOWER BOUND, never a point
   estimate; CI half-width and null p95 reported beside it.
4. CONTROLS THAT BIND -- report how many items each removed; a control that removes nothing is
   not a control.
5. NOT AN ARTIFACT -- would a rank-matched / rate-matched / scrambled twin reproduce the win?


## CORE READING / WORD-LEARNING (50 cells) -- vet these first

| # | landed | cell | status |
|---|---|---|---|
| 1 | 2026-08-17 | `exp_base_reader_grounded_relations_coref_v1` | PENDING |
| 2 | 2026-08-17 | `exp_causal_link_comprehension_fuller_v2` | PENDING |
| 3 | 2026-08-17 | `exp_online_knowledge_condenser_selectional_v1` | PENDING |
| 4 | 2026-08-17 | `exp_pivot_scaled_seed_knowledge_table_v1` | PENDING |
| 5 | 2026-08-17 | `exp_read_grow_adaptor_pyp_kn_breadth_v1` | PENDING |
| 6 | 2026-08-17 | `exp_read_grow_construction_induction_dop_fragments_v1` | PENDING |
| 7 | 2026-08-17 | `exp_read_grow_foundation_realprose_glassbox_ie_v1` | PENDING |
| 8 | 2026-08-17 | `exp_read_grow_oov_verb_extension_v1` | PENDING |
| 9 | 2026-08-17 | `exp_read_grow_openvocab_fastmap_v1` | PENDING |
| 10 | 2026-08-14 | `exp_information_foraging_reading_v1` | PENDING |
| 11 | 2026-08-13 | `exp_lexicon_coverage_audit_barrier2_v1` | PENDING |
| 12 | 2026-08-12 | `exp_context_vector_signal_v1` | PENDING |
| 13 | 2026-08-12 | `exp_gap_driven_reader_controlled_v1` | PENDING |
| 14 | 2026-08-12 | `exp_reading_grounding_loop_cycle1_v1` | PENDING |
| 15 | 2026-08-12 | `exp_reading_grounding_loop_cycle2_v1` | PENDING |
| 16 | 2026-08-06 | `exp_verb_class_openvocab_similarity_v1` | PENDING |
| 17 | 2026-08-05 | `exp_c5_multigoal_content_coherence_tiebreak_v1` | PENDING |
| 18 | 2026-08-05 | `exp_c5_primacy_trap_endtoend_goal_coherence_candidate_gen_v1` | PENDING |
| 19 | 2026-08-05 | `exp_outcome_valence_goal_congruence_v1` | PENDING |
| 20 | 2026-08-03 | `exp_causal_link_comprehension_fuller_v3_cleaned` | PENDING |
| 21 | 2026-08-02 | `exp_causal_link_comprehension_pilot_v1` | PENDING |
| 22 | 2026-07-27 | `exp_unified_self_learning_loop_v3` | PENDING |
| 23 | 2026-07-23 | `exp_pivot_selectional_knowledge_richness_2afc_v1` | PENDING |
| 24 | 2026-07-19 | `exp_learned_argstruct_parser_lccp_independent_gold_v1` | PENDING |
| 25 | 2026-07-19 | `exp_role_filler_factorization_conceptnet_cg_v1` | PENDING |
| 26 | 2026-07-19 | `exp_role_filler_factorization_reader_coupled_cg_v1` | PENDING |
| 27 | 2026-07-18 | `exp_learned_role_assigner_reader_composition_v3` | PENDING |
| 28 | 2026-07-17 | `exp_read_discourse_state_of_mind_wsm_coupling_v1` | PENDING |
| 29 | 2026-07-17 | `exp_read_grow_oov_fullyopen_multiclause_v1` | PENDING |
| 30 | 2026-07-17 | `exp_read_grow_oov_pos_extension_v1` | PENDING |
| 31 | 2026-07-16 | `exp_lexicon_grounding_loop_v1` | PENDING |
| 32 | 2026-07-16 | `exp_lexicon_learned_grounding_scaled_v1` | PENDING |
| 33 | 2026-07-16 | `exp_lexicon_learned_grounding_v1` | PENDING |
| 34 | 2026-07-16 | `exp_lexicon_realvec_endtoend_reframe_v1` | PENDING |
| 35 | 2026-07-16 | `exp_nativelang_svo_vsa_probe_v1` | PENDING |
| 36 | 2026-07-16 | `exp_read_coref_hobbs_centering_resolver_v1` | PENDING |
| 37 | 2026-07-16 | `exp_read_grow_relation_identity_v1` | PENDING |
| 38 | 2026-07-06 | `exp_frame_order_recovery_hard_comprehension_v2` | PENDING |
| 39 | 2026-07-06 | `exp_frame_order_recovery_hard_comprehension_v2_preview5` | PENDING |
| 40 | 2026-07-05 | `exp_comprehension_envelope_superposition_vocab_v1` | PENDING |
| 41 | 2026-07-03 | `exp_bilingual_dual_substrate_cpu_v1` | PENDING |
| 42 | 2026-07-03 | `exp_combo3_unified_api_n32768_v1` | PENDING |
| 43 | 2026-07-03 | `exp_comm_lex_emission_cpu_v1` | PENDING |
| 44 | 2026-07-03 | `exp_patternb_erasure_granularity_v1` | PENDING |
| 45 | 2026-07-03 | `exp_substrate_72a_iter2_fullP2_derivation_truth_cpu_v1` | PENDING |
| 46 | 2026-07-03 | `exp_substrate_benchmark_vector_B1_B6_dashboard_cpu_v1` | PENDING |
| 47 | 2026-07-03 | `exp_substrate_curry_howard_type_checker_cpu_v1` | PENDING |
| 48 | 2026-07-03 | `exp_tabular_algebraic_sql_cpu_v1` | PENDING |
| 49 | 2026-07-03 | `exp_temporal_ordering_recovery_cpu_v1` | PENDING |
| 50 | 2026-06-25 | `exp_kinetic_proofreading_refuse_envelope_smoke_v1` | PENDING |

## REMAINING MEANING-RELEVANT (149 cells)

| # | landed | cell | status |
|---|---|---|---|
| 51 | 2026-08-17 | `exp_relational_vs_similarity_conflict_viability_probe_v1` | PENDING |
| 52 | 2026-08-17 | `exp_np_head_finder_grounding_gate_break050_v1` | PENDING |
| 53 | 2026-08-11 | `exp_grounded_meaning_wire_lexical_fallback_v1` | PENDING |
| 54 | 2026-08-11 | `exp_three_tier_loop_concept_coherence_v1` | PENDING |
| 55 | 2026-08-09 | `exp_grounding_acquisition_loop_v1` | PENDING |
| 56 | 2026-08-07 | `exp_social_relational_grounding_axis_v1` | PENDING |
| 57 | 2026-08-07 | `exp_word_context_affect_superposition_map_v1` | PENDING |
| 58 | 2026-08-06 | `exp_n11c_shared_feature_lexical_similarity_v1` | PENDING |
| 59 | 2026-08-05 | `exp_bridge1_governor_grounding_v1` | PENDING |
| 60 | 2026-08-05 | `exp_event_boundary_relevance_gate_v1` | PENDING |
| 61 | 2026-07-27 | `exp_scale_meaning_learn_arc_heldout_v2` | PENDING |
| 62 | 2026-07-26 | `exp_analogy_candidate_inference_dense_corpus_v1` | PENDING |
| 63 | 2026-07-26 | `exp_grounded_inductive_concept_encoder_heldout_new_v3` | PENDING |
| 64 | 2026-07-26 | `exp_leakproof_relational_inference_heldout_v1` | PENDING |
| 65 | 2026-07-26 | `exp_leakproof_relinfer_twonew_v1` | PENDING |
| 66 | 2026-07-23 | `exp_vision_integrated_recognize_bind_ground_v1` | PENDING |
| 67 | 2026-07-22 | `exp_agreement_depth_productivity_generalization_v1` | PENDING |
| 68 | 2026-07-22 | `exp_agreement_learned_depth_accumulator_v1` | PENDING |
| 69 | 2026-07-22 | `exp_grounding_attn_bind_incremental_curve_v1` | PENDING |
| 70 | 2026-07-22 | `exp_pun_coherence_alarm_viability_probe_v1` | PENDING |
| 71 | 2026-07-21 | `exp_wordnet_noun_semantics_kb_who_affected_v1` | PENDING |
| 72 | 2026-07-19 | `exp_affectedness_change_of_state_patient_selection_design_gate_v1` | PENDING |
| 73 | 2026-07-19 | `exp_arg_adjunct_role_eligibility_categorial_break050_v1` | PENDING |
| 74 | 2026-07-19 | `exp_lccp_motion_aspectual_distributional_detector_deconfound_v1` | PENDING |
| 75 | 2026-07-19 | `exp_lccp_motion_aspectual_syntactic_frame_teacher_v1` | PENDING |
| 76 | 2026-07-19 | `exp_scene_coherence_verifier_contrastive_scv_v1` | PENDING |
| 77 | 2026-07-18 | `exp_srn_predict_category_v1` | PENDING |
| 78 | 2026-07-18 | `exp_visual_grounding_coherence_v1` | PENDING |
| 79 | 2026-07-17 | `exp_fuzzy_shard_router_attractor_stage12_v1` | PENDING |
| 80 | 2026-07-15 | `exp_ingest_gate_strong_foundation_novelty_v2` | PENDING |
| 81 | 2026-07-15 | `exp_interference_avoidance_conjunctive_vs_additive_v1` | PENDING |
| 82 | 2026-07-14 | `exp_cold_placement_recovery_opt_v1` | PENDING |
| 83 | 2026-07-14 | `exp_grounding_by_redundancy_joint_corruption_allometry_v1` | PENDING |
| 84 | 2026-07-14 | `exp_grounding_law_consistency_allometry_v1` | PENDING |
| 85 | 2026-07-13 | `exp_grounding_gated_fusion_relation_inference_mammal_v1` | PENDING |
| 86 | 2026-07-10 | `exp_grounding_measured_attribute_concreteness_v1` | PENDING |
| 87 | 2026-07-10 | `exp_gt_induction_fb15k237_dense_v1` | PENDING |
| 88 | 2026-07-09 | `exp_grounding_bind_chain_systematicity_v1` | PENDING |
| 89 | 2026-07-09 | `exp_grounding_snowball_transitive_inheritance_v1` | PENDING |
| 90 | 2026-07-08 | `exp_conceptnet_rerank_parity_multiseed_v1` | PENDING |
| 91 | 2026-07-08 | `exp_encoder_peel_sic_readout_realcodes_v1` | PENDING |
| 92 | 2026-07-08 | `exp_resonator_theta_gamma_peel_v1` | PENDING |
| 93 | 2026-07-08 | `exp_teacher_free_relational_encoder_cn_subgraph_v1` | PENDING |
| 94 | 2026-07-07 | `exp_ingest_knowledge_integration_verify_v1` | PENDING |
| 95 | 2026-07-07 | `exp_ingest_knowledge_integration_verify_v2` | PENDING |
| 96 | 2026-07-07 | `exp_n8_conceptnet_ingest_eval_canon_v1` | PENDING |
| 97 | 2026-07-07 | `exp_n8_conceptnet_ingest_eval_v1_smoke3` | PENDING |
| 98 | 2026-07-05 | `exp_grammar_recursive_function_word_blocklocal_v1` | PENDING |
| 99 | 2026-07-05 | `exp_ingest_knowledge_livepath_verify_v1` | PENDING |
| 100 | 2026-07-05 | `exp_morph_ruleset_wug_v2_cpu` | PENDING |
| 101 | 2026-07-03 | `exp_api_as_of_checkpoint_v1` | PENDING |
| 102 | 2026-07-03 | `exp_argumentation_grounded_cpu_v1` | PENDING |
| 103 | 2026-07-03 | `exp_batched_deletion_reliability_v1` | PENDING |
| 104 | 2026-07-03 | `exp_caching_write_allocate_per_pattern_v1` | PENDING |
| 105 | 2026-07-03 | `exp_calibrated_confidence_ece_v1_n1024` | PENDING |
| 106 | 2026-07-03 | `exp_cheap2_gap_score_uncertainty_cpu_v1` | PENDING |
| 107 | 2026-07-03 | `exp_cheap3_pp107_tiers_cpu_v1` | PENDING |
| 108 | 2026-07-03 | `exp_chunking_discriminative_cpu_v1` | PENDING |
| 109 | 2026-07-03 | `exp_comm1_paragraph_compose_cpu_v1` | PENDING |
| 110 | 2026-07-03 | `exp_comm2_translation_distant_cpu_v1` | PENDING |
| 111 | 2026-07-03 | `exp_continuous_embedding_storage_substrate_v2_n16384` | PENDING |
| 112 | 2026-07-03 | `exp_creative_dreaming_smoke_cpu_v1` | PENDING |
| 113 | 2026-07-03 | `exp_d2_4_neurogenesis_cpu_v1` | PENDING |
| 114 | 2026-07-03 | `exp_dreaming_substrate_cpu_v1` | PENDING |
| 115 | 2026-07-03 | `exp_g5_entity_substitution_kf1_v1` | PENDING |
| 116 | 2026-07-03 | `exp_h_hotpotqa_ingest_v1` | PENDING |
| 117 | 2026-07-03 | `exp_hierarchical_concept_formation_instrumentation_v3_costructured_n4096` | PENDING |
| 118 | 2026-07-03 | `exp_hoc1_word_bigram_v1` | PENDING |
| 119 | 2026-07-03 | `exp_humaneval_structural_lite_cpu_v1` | PENDING |
| 120 | 2026-07-03 | `exp_intent_atis_multiseed_cpu_v1` | PENDING |
| 121 | 2026-07-03 | `exp_kf1_paraphrase_robustness_marianmt_v1` | PENDING |
| 122 | 2026-07-03 | `exp_lang_math_coexist_cpu_v1` | PENDING |
| 123 | 2026-07-03 | `exp_lap2_11_haiku_cpu_v1` | PENDING |
| 124 | 2026-07-03 | `exp_lap5_schema_layer_cpu_v1` | PENDING |
| 125 | 2026-07-03 | `exp_lap6_inheritance_index_cpu_v1` | PENDING |
| 126 | 2026-07-03 | `exp_lex_wug_test_cpu_v1` | PENDING |
| 127 | 2026-07-03 | `exp_n1b_perhop_ablation_cpu_v1` | PENDING |
| 128 | 2026-07-03 | `exp_negative_knowledge_tree_4level_v1_n4096` | PENDING |
| 129 | 2026-07-03 | `exp_now1_temporal_grounding_cpu_v1` | PENDING |
| 130 | 2026-07-03 | `exp_online_sparse_concept_extension_v1` | PENDING |
| 131 | 2026-07-03 | `exp_patternb_online_extension_v1` | PENDING |
| 132 | 2026-07-03 | `exp_pb_kf1_multilang_chain_robustness_v1` | PENDING |
| 133 | 2026-07-03 | `exp_pb_mmr_real_encoder_clustered_v1` | PENDING |
| 134 | 2026-07-03 | `exp_pb_multilang_paraphrase_chain_kf1_v1` | PENDING |
| 135 | 2026-07-03 | `exp_phase05_v1_pythia160m_residual_extract_pertoken_v1` | PENDING |
| 136 | 2026-07-03 | `exp_phase4b_multibench_multiseed_cpu_v1` | PENDING |
| 137 | 2026-07-03 | `exp_phase4b_multibench_solver_cpu_v1` | PENDING |
| 138 | 2026-07-03 | `exp_phase4b_multistep_cpu_v1` | PENDING |
| 139 | 2026-07-03 | `exp_phase4b_multistep_multiseed_cpu_v1` | PENDING |
| 140 | 2026-07-03 | `exp_phase4b_unified_solver_cpu_v1` | PENDING |
| 141 | 2026-07-03 | `exp_phase4d_code_fulldata_cpu_v1` | PENDING |
| 142 | 2026-07-03 | `exp_phase4d_code_multiseed_cpu_v1` | PENDING |
| 143 | 2026-07-03 | `exp_polysemy_context_bound_cpu_v1` | PENDING |
| 144 | 2026-07-03 | `exp_qa_self_knowledge_A_cue_alignment_diagnosis_gpu_v1` | PENDING |
| 145 | 2026-07-03 | `exp_qa_self_knowledge_E_bge_route_gpu_v1` | PENDING |
| 146 | 2026-07-03 | `exp_qa_self_knowledge_candidate_edges_cpu_v1` | PENDING |
| 147 | 2026-07-03 | `exp_qa_self_knowledge_full_stack_AE_combined_gpu_v1` | PENDING |
| 148 | 2026-07-03 | `exp_qa_self_knowledge_full_stack_A_top5_ab_gpu_v1` | PENDING |
| 149 | 2026-07-03 | `exp_qa_self_knowledge_route_a_tuned_cpu_v1` | PENDING |
| 150 | 2026-07-03 | `exp_qa_self_knowledge_route_ab_v4_cpu_v1` | PENDING |
| 151 | 2026-07-03 | `exp_qa_self_knowledge_route_b_v3_cpu_v1` | PENDING |
| 152 | 2026-07-03 | `exp_qa_self_knowledge_unified_a_tuned_b_v3_e_bge_threshold_cpu_v1` | PENDING |
| 153 | 2026-07-03 | `exp_qdef_watermark_canary_v1` | PENDING |
| 154 | 2026-07-03 | `exp_query_redundancy_methodology_v1` | PENDING |
| 155 | 2026-07-03 | `exp_reasoning_storage_4way_cleanup_v3_hadamard_hopid_v1_n16384` | PENDING |
| 156 | 2026-07-03 | `exp_schema_retrieval_rt1_cpu_v1` | PENDING |
| 157 | 2026-07-03 | `exp_sentiment_headtohead_gpu_v1` | PENDING |
| 158 | 2026-07-03 | `exp_srht_iterated_passes_zkl_v1` | PENDING |
| 159 | 2026-07-03 | `exp_srht_llama_l15_zkl_v1` | PENDING |
| 160 | 2026-07-03 | `exp_storage_huffman_entropy_v1` | PENDING |
| 161 | 2026-07-03 | `exp_substrate_61a_m4d_on_56d_concept_disjoint_heldout_cpu_v1` | PENDING |
| 162 | 2026-07-03 | `exp_substrate_cognitive_core_introspection_toolkit_v1` | PENDING |
| 163 | 2026-07-03 | `exp_substrate_cognitive_core_smoke_pythia70m_synthetic_v1` | PENDING |
| 164 | 2026-07-03 | `exp_substrate_concept_construct_1_carrier_extending_with_internal_utility_cpu_v1` | PENDING |
| 165 | 2026-07-03 | `exp_substrate_concept_invention_COMPOUND_F4_hr_fingerprint_discriminator_cpu_v1` | PENDING |
| 166 | 2026-07-03 | `exp_substrate_extended_context_ceiling_posbind_symw_v1_8192_16384_gpu` | PENDING |
| 167 | 2026-07-03 | `exp_substrate_hallucination_detection_minilm_v1` | PENDING |
| 168 | 2026-07-03 | `exp_substrate_hallucination_robustness_hard_negatives_v1` | PENDING |
| 169 | 2026-07-03 | `exp_substrate_kgram_xor_context_binding_v1` | PENDING |
| 170 | 2026-07-03 | `exp_substrate_max_for_reasoning_tasks_not_lm_v1` | PENDING |
| 171 | 2026-07-03 | `exp_substrate_multimodal_binding_text_kg_v1` | PENDING |
| 172 | 2026-07-03 | `exp_substrate_phase3_coevolve1_iter1_P1bge_remote_cpu_v1` | PENDING |
| 173 | 2026-07-03 | `exp_substrate_pp8_cosine_variance_gate_v1` | PENDING |
| 174 | 2026-07-03 | `exp_substrate_pp8_learned_discriminability_probe_v1` | PENDING |
| 175 | 2026-07-03 | `exp_substrate_real_encoder_capabilities_v1` | PENDING |
| 176 | 2026-07-03 | `exp_sustained_agentic_load_v1_n4096` | PENDING |
| 177 | 2026-07-03 | `exp_t5c_a2_projection_quality_cpu_v1` | PENDING |
| 178 | 2026-07-03 | `exp_t5c_orchestrator_routing_cpu_v1` | PENDING |
| 179 | 2026-07-03 | `exp_textclass_headtohead_calibrated_gpu_v1` | PENDING |
| 180 | 2026-07-03 | `exp_textclass_headtohead_gpu_v1` | PENDING |
| 181 | 2026-07-03 | `exp_timeseries_xor_prot021_fix_v1` | PENDING |
| 182 | 2026-07-03 | `exp_type_confusion_sharded_cpu_v1` | PENDING |
| 183 | 2026-07-02 | `exp_substrate_concept_encoder_spoke2_temporal_contiguity_foldiak_trace_v1` | PENDING |
| 184 | 2026-07-02 | `exp_substrate_semantic_parser_intent_slot_extraction_v1` | PENDING |
| 185 | 2026-07-02 | `exp_substrate_concept_encoder_spoke1_v3_D_competitive_hebbian_only_2026_07_02` | PENDING |
| 186 | 2026-07-02 | `exp_substrate_concept_encoder_v2_A_ppmi_svd_sparse_2026_07_03` | PENDING |
| 187 | 2026-07-01 | `exp_metric_dependence_top_k_semantic_v3_seed_13` | PENDING |
| 188 | 2026-07-01 | `exp_metric_dependence_top_k_semantic_v3_seed_19` | PENDING |
| 189 | 2026-07-01 | `exp_metric_dependence_top_k_semantic_v3_seed_7` | PENDING |
| 190 | 2026-06-30 | `exp_substrate_routing_geometry_family_kg_ingest_v2_seed_13` | PENDING |
| 191 | 2026-06-30 | `exp_substrate_routing_geometry_family_kg_ingest_v2_seed_19` | PENDING |
| 192 | 2026-06-30 | `exp_substrate_routing_geometry_family_kg_ingest_v2_seed_7` | PENDING |
| 193 | 2026-06-25 | `exp_n8_conceptnet_ingest_eval_v1` | PENDING |
| 194 | 2026-06-25 | `exp_substrate_clean_encoder_substrate_as_LM_v1` | PENDING |
| 195 | 2026-06-25 | `exp_substrate_pc_hierarchy_fair_harness_v1` | PENDING |
| 196 | 2026-06-25 | `exp_substrate_role_tagged_compositional_generalization_on_concept_KG_v1` | PENDING |
| 197 | 2026-06-25 | `exp_substrate_stage1_SEMANTIC_concept_learner_battery_v2_FULL` | PENDING |
| 198 | 2026-06-25 | `exp_substrate_stage1_SEMANTIC_concept_learner_battery_v3_CV_TIGHTENING` | PENDING |
| 199 | 2026-06-25 | `exp_n8_conceptnet_ingest_eval_v1_smoke2` | PENDING |
