# Phase-2-light proposal batch review

- Smoke run: `phase_2_light_smoke_1781289531.json`
- n_input_files: 50
- n_atoms_baseline: 1742
- elapsed: 80.2s
- proposals: 30

## Instructions

For each proposal: replace `[ ]` with `[A]`=ACCEPT, `[R]`=REJECT, `[U]`=UPDATE (existing atom), `[D]`=DEFER, `[M]`=MODIFY (note in comment).

---

### #1. `independent_verifier` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.99)
- Distant supervision: max score 0.00
- Raw mentions: ['independent-verifier', 'INDEPENDENT-VERIFIER', 'independent-verifier']
- Source files (sample): ['research_drill_substrate_tier_5_benchmark_design_2x_2026-06-12.md', 'research_drill_substrate_tier_5_self_discovery_pathway_2x_2026-06-11.md', 'research_drill_substrate_self_discovery_validation_2x_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: independent_verifier
  ```

### #2. `algebra_hrr` (Z=8)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.98)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T2/circular_convolution (sim=0.33)
  - math::T1/lie_algebra (sim=0.33)
- Raw mentions: ['algebra-HRR', 'algebra-HRR', 'algebra-HRR']
- Source files (sample): ['research_drill_free_probability_F4_free_cumulants_substrate_observability_beyond_mean_variance_2x_2026-06-12.md', 'research_drill_free_probability_R_transform_clustered_codebook_constructive_cleanup_cliff_prediction_2x_2026-06-12.md', 'research_drill_distractor_density_ceiling_vector_retrieval_corpus_growth_2x_2026-06-12.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: algebra_hrr
  ```

### #3. `open_domain` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 7 (density=2 atoms; novelty=0.97)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - science::CS/transfer_learning (sim=0.33)
- Raw mentions: ['Open-domain', 'open-domain', 'open-domain']
- Source files (sample): ['research_drill_substrate_language_beyond_tier_a_hard_drill_3x_2026-06-12.md', 'research_drill_substrate_eval_recall_gap_alternatives_2x_2026-06-11.md', 'research_drill_substrate_CRF_universal_nl_2x_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 7
  about_topic: open_domain
  ```

### #4. `hrr_bind` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 15 (density=2 atoms; novelty=0.97)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T2/fhrr_bind (sim=0.33)
  - math::T2/circular_convolution (sim=0.33)
  - math::T3/ghrr_noncommutative_bind (sim=0.33)
- Raw mentions: ['HRR-bind', 'HRR-bind', 'HRR-bind']
- Source files (sample): ['research_drill_substrate_creativity_capabilities_hard_drill_3x_2026-06-12.md', 'research_drill_substrate_VSA_position_is_meaning_4x_2026-06-12.md', 'research_drill_mwp_comprehension_wall_phase_6_corpus_3x_2026-06-12.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 15
  about_topic: hrr_bind
  ```

### #5. `query_privacy` (Z=7)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 5 (density=3 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['query-privacy', 'query-privacy', 'query-privacy']
- Source files (sample): ['research_drill_vsa_composition_decomposition_benchmark_methodology_2x_2026-06-12.md', 'research_drill_asymmetric_retrieval_leg_degradation_methodology_2x_2026-06-12.md', 'research_drill_substrate_language_beyond_tier_a_hard_drill_3x_2026-06-12.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 5
  about_topic: query_privacy
  ```

### #6. `long_form` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.96)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T1/tensor (sim=0.33)
- Raw mentions: ['long-form', 'long-form', 'Long-form']
- Source files (sample): ['research_drill_substrate_language_beyond_tier_a_hard_drill_3x_2026-06-12.md', 'research_drill_substrate_tier_5_benchmark_design_2x_2026-06-12.md', 'research_drill_substrate_self_discovery_validation_2x_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: long_form
  ```

### #7. `hard_fail` (Z=42)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.96)
- Distant supervision: max score 0.00
- Raw mentions: ['HARD-FAIL', 'HARD-FAIL', 'HARD-FAIL']
- Source files (sample): ['research_drill_free_probability_F4_free_cumulants_substrate_observability_beyond_mean_variance_2x_2026-06-12.md', 'research_drill_shares_math_false_merge_auditing_entity_resolution_thresholding_methodology_1x_2026-06-12.md', 'research_drill_free_probability_MP_bulk_subleading_1sqrtN_correction_empirical_test_design_2x_2026-06-12.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: hard_fail
  ```

### #8. `surface_form` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.96)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T1/tensor (sim=0.33)
- Raw mentions: ['surface-form', 'surface-form', 'surface-form']
- Source files (sample): ['research_drill_phase_2_full_substrate_corpus_self_mining_active_learning_methodology_2x_2026-06-12.md', 'research_drill_substrate_classical_NER_architectural_ceiling_beyond_feature_engineering_2x_2026-06-12.md', 'research_drill_substrate_eval_recall_gap_alternatives_2x_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: surface_form
  ```

### #9. `tier_hierarchy` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 5 (density=3 atoms; novelty=0.97)
- Distant supervision: max score 0.00
- Raw mentions: ['tier-hierarchy', 'tier-hierarchy', 'tier-hierarchy']
- Source files (sample): ['research_drill_substrate_cross_disc_analogue_surfacing_2x_2026-06-12.md', 'research_drill_ner_3datapoint_plateau_substrate_paths_2x_2026-06-11.md', 'research_drill_7_invariants_empirical_validation_2x_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 5
  about_topic: tier_hierarchy
  ```

### #10. `if_hard` (Z=5)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.96)
- Distant supervision: max score 0.00
- Raw mentions: ['If HARD', 'If HARD', 'If HARD']
- Source files (sample): ['research_drill_pos_brown_ptb_cross_domain_transfer_3rd_appearance_capability_class_test_1x_2026-06-12.md', 'research_drill_asymmetric_retrieval_leg_degradation_methodology_2x_2026-06-12.md', 'research_drill_ner_substrate_paths_remaining_2x_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: if_hard
  ```

### #11. `does_not` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 7 (density=2 atoms; novelty=0.96)
- Distant supervision: max score 0.00
- Raw mentions: ['DOES NOT', 'DOES NOT', 'DOES NOT']
- Source files (sample): ['research_drill_elegant_hyperdimensional_mathematics_representation_4x_2026-06-12.md', 'research_drill_substrate_VSA_position_is_meaning_4x_2026-06-12.md', 'research_drill_substrate_3op_compositional_extension_2x_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 7
  about_topic: does_not
  ```

### #12. `prediction_p2` (Z=5)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.96)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T3/conformal_prediction (sim=0.33)
  - science::BIO/predictive_coding (sim=0.33)
- Raw mentions: ['Prediction P2', 'Prediction P2', 'Prediction P2']
- Source files (sample): ['research_drill_substrate_as_full_research_ledger_2x_2026-06-11.md', 'research_drill_asdiv_030_plateau_substrate_paths_2x_2026-06-11.md', 'research_drill_substrate_universal_scientific_corpus_2x_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: prediction_p2
  ```

### #13. `bag_of_words` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 7 (density=2 atoms; novelty=0.96)
- Distant supervision: max score 0.00
- Raw mentions: ['bag-of-words', 'bag-of-words', 'bag-of-words']
- Source files (sample): ['research_drill_substrate_VSA_position_is_meaning_4x_2026-06-12.md', 'research_drill_substrate_classical_nl_multiseed_variance_pattern_2x_2026-06-12.md', 'research_drill_substrate_classical_mechanism_transfer_replication_2x_2026-06-12.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 7
  about_topic: bag_of_words
  ```

### #14. `low_data` (Z=5)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.95)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - science::CS/data_structure (sim=0.33)
  - science::CS/data_structure (sim=0.33)
- Raw mentions: ['low-data', 'low-data', 'low-data']
- Source files (sample): ['research_drill_shares_math_false_merge_auditing_entity_resolution_thresholding_methodology_1x_2026-06-12.md', 'research_drill_pos_brown_ptb_cross_domain_transfer_3rd_appearance_capability_class_test_1x_2026-06-12.md', 'research_drill_substrate_classical_NER_architectural_ceiling_beyond_feature_engineering_2x_2026-06-12.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: low_data
  ```

### #15. `feature_engineering` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 7 (density=2 atoms; novelty=0.96)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T3/feature_hashing (sim=0.33)
- Raw mentions: ['feature-engineering', 'feature-engineering', 'feature-engineering']
- Source files (sample): ['research_drill_shares_math_false_merge_auditing_entity_resolution_thresholding_methodology_1x_2026-06-12.md', 'research_drill_pos_brown_ptb_cross_domain_transfer_3rd_appearance_capability_class_test_1x_2026-06-12.md', 'research_drill_substrate_classical_NER_architectural_ceiling_beyond_feature_engineering_2x_2026-06-12.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 7
  about_topic: feature_engineering
  ```

### #16. `weak_label` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 15 (density=2 atoms; novelty=0.96)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T2_FAM/weak_supervision (sim=0.33)
  - math::T2_FAM/weak_supervision (sim=0.33)
- Raw mentions: ['weak-label', 'weak-label', 'weak-label']
- Source files (sample): ['research_drill_substrate_operand_selection_mwp_2x_2026-06-12.md', 'research_drill_substrate_classical_mechanism_transfer_conditions_2x_2026-06-11.md', 'research_drill_beyond_discriminative_mwp_mechanism_classes_2x_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 15
  about_topic: weak_label
  ```

### #17. `low_resource` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 5 (density=3 atoms; novelty=0.96)
- Distant supervision: max score 0.00
- Raw mentions: ['low-resource', 'low-resource', 'low-resource']
- Source files (sample): ['research_drill_low_data_ner_structured_perceptron_architecture_2x_2026-06-12.md', 'research_drill_substrate_language_beyond_tier_a_hard_drill_3x_2026-06-12.md', 'research_drill_ner_3datapoint_plateau_substrate_paths_2x_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 5
  about_topic: low_resource
  ```

### #18. `higher_order` (Z=11)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 15 (density=2 atoms; novelty=0.96)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - science::PHYS/topological_phase (sim=0.33)
- Raw mentions: ['Higher-order', 'HIGHER-ORDER', 'higher-order']
- Source files (sample): ['research_drill_free_probability_F4_free_cumulants_substrate_observability_beyond_mean_variance_2x_2026-06-12.md', 'research_drill_free_probability_MP_bulk_subleading_1sqrtN_correction_empirical_test_design_2x_2026-06-12.md', 'research_drill_free_probability_R_transform_clustered_codebook_constructive_cleanup_cliff_prediction_2x_2026-06-12.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 15
  about_topic: higher_order
  ```

### #19. `structure_mapping` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 5 (density=3 atoms; novelty=0.96)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - science::BIO/dna_double_helix (sim=0.33)
  - science::CHEM/atomic_structure (sim=0.33)
  - science::CS/data_structure (sim=0.33)
- Raw mentions: ['structure-mapping', 'structure-mapping', 'structure-mapping']
- Source files (sample): ['research_drill_substrate_creativity_capabilities_hard_drill_3x_2026-06-12.md', 'research_drill_substrate_cross_disc_analogue_surfacing_2x_2026-06-12.md', 'research_drill_substrate_tier_5_self_discovery_pathway_2x_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 5
  about_topic: structure_mapping
  ```

### #20. `pattern_completion` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.95)
- Distant supervision: max score 0.00
- Raw mentions: ['pattern-completion', 'pattern-completion', 'pattern-completion']
- Source files (sample): ['research_drill_substrate_creativity_capabilities_hard_drill_3x_2026-06-12.md', 'research_drill_substrate_cross_disc_analogue_surfacing_2x_2026-06-12.md', 'research_drill_substrate_tier_5_self_discovery_pathway_2x_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: pattern_completion
  ```

### #21. `serves_capability` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.95)
- Distant supervision: max score 0.00
- Raw mentions: ['serves_capability', 'serves_capability', 'serves_capability']
- Source files (sample): ['research_drill_shares_math_edge_type_design_anchored_in_32_collision_empirical_1x_2026-06-12.md', 'research_drill_elegant_hyperdimensional_mathematics_representation_4x_2026-06-12.md', 'research_drill_semantic_a_axis_beyond_bge_2x_2026-06-12.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: serves_capability
  ```

### #22. `linear_chain` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 5 (density=3 atoms; novelty=0.96)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T1/vector_space (sim=0.33)
  - math::T2_FAM/sequence_decoding (sim=0.33)
  - math::T1/chain_rule (sim=0.33)
- Raw mentions: ['Linear-chain', 'linear-chain', 'linear-chain']
- Source files (sample): ['research_drill_ner_3datapoint_plateau_substrate_paths_2x_2026-06-11.md', 'research_drill_substrate_CRF_universal_nl_2x_2026-06-11.md', 'research_drill_ner_substrate_paths_2x_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 5
  about_topic: linear_chain
  ```

### #23. `document_level` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.95)
- Distant supervision: max score 0.00
- Raw mentions: ['document-level', 'Document-level', 'document-level']
- Source files (sample): ['research_drill_substrate_classical_NER_architectural_ceiling_beyond_feature_engineering_2x_2026-06-12.md', 'research_drill_ner_substrate_paths_remaining_2x_2026-06-11.md', 'research_drill_ner_3datapoint_plateau_substrate_paths_2x_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: document_level
  ```

### #24. `hard_pass` (Z=43)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.95)
- Distant supervision: max score 0.00
- Raw mentions: ['HARD-PASS', 'HARD-PASS', 'HARD-PASS']
- Source files (sample): ['research_drill_free_probability_F4_free_cumulants_substrate_observability_beyond_mean_variance_2x_2026-06-12.md', 'research_drill_shares_math_false_merge_auditing_entity_resolution_thresholding_methodology_1x_2026-06-12.md', 'research_drill_free_probability_MP_bulk_subleading_1sqrtN_correction_empirical_test_design_2x_2026-06-12.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: hard_pass
  ```

### #25. `sequence_tagging` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 15 (density=2 atoms; novelty=0.95)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T2_FAM/sequence_decoding (sim=0.33)
  - math::T1/cauchy_sequence (sim=0.33)
  - math::T1/cauchy_sequence (sim=0.33)
- Raw mentions: ['Sequence Tagging', 'sequence-tagging', 'sequence-tagging']
- Source files (sample): ['research_drill_pos_brown_ptb_cross_domain_transfer_3rd_appearance_capability_class_test_1x_2026-06-12.md', 'research_drill_low_data_ner_structured_perceptron_architecture_2x_2026-06-12.md', 'research_drill_ner_substrate_paths_2x_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 15
  about_topic: sequence_tagging
  ```

### #26. `kappa_n` (Z=5)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 7 (density=2 atoms; novelty=0.95)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T3/kappa_4_free (sim=0.33)
- Raw mentions: ['kappa_n', 'kappa_n', 'kappa_n']
- Source files (sample): ['research_drill_free_probability_F4_free_cumulants_substrate_observability_beyond_mean_variance_2x_2026-06-12.md', 'research_drill_substrate_tier_5_benchmark_design_2x_2026-06-12.md', 'research_drill_free_probability_F4_substrate_observability_3x_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 7
  about_topic: kappa_n
  ```

### #27. `algebra_index` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.94)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T1/lie_algebra (sim=0.33)
- Raw mentions: ['algebra_index', 'algebra_index', 'algebra_index']
- Source files (sample): ['research_drill_phase_2_full_substrate_corpus_self_mining_active_learning_methodology_2x_2026-06-12.md', 'research_drill_vsa_composition_decomposition_benchmark_methodology_2x_2026-06-12.md', 'research_drill_asymmetric_retrieval_leg_degradation_methodology_2x_2026-06-12.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: algebra_index
  ```

### #28. `static_robust` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 15 (density=2 atoms; novelty=0.95)
- Distant supervision: max score 0.00
- Raw mentions: ['STATIC-robust', 'static-robust', 'static-robust']
- Source files (sample): ['research_drill_beyond_discriminative_mwp_mechanism_classes_2x_2026-06-11.md', 'research_drill_substrate_as_full_research_ledger_2x_2026-06-11.md', 'research_drill_dep_parse_0787_to_085_substrate_paths_2x_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 15
  about_topic: static_robust
  ```

### #29. `within_cluster` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 7 (density=2 atoms; novelty=0.95)
- Distant supervision: max score 0.00
- Raw mentions: ['within-cluster', 'within-cluster', 'within-cluster']
- Source files (sample): ['research_drill_free_probability_R_transform_clustered_codebook_constructive_cleanup_cliff_prediction_2x_2026-06-12.md', 'research_drill_free_probability_VSA_cleanup_clustered_codebook_capacity_2x_2026-06-12.md', 'research_drill_substrate_proposed_atom_candidates_2x_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 7
  about_topic: within_cluster
  ```

### #30. `penn_treebank` (Z=5)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 15 (density=2 atoms; novelty=0.95)
- Distant supervision: max score 0.00
- Raw mentions: ['Penn Treebank', 'Penn Treebank', 'Penn Treebank']
- Source files (sample): ['research_drill_substrate_classical_mechanism_transfer_conditions_2x_2026-06-11.md', 'research_drill_ner_3datapoint_plateau_substrate_paths_2x_2026-06-11.md', 'research_drill_substrate_CRF_universal_nl_2x_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 15
  about_topic: penn_treebank
  ```
