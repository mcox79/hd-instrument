# Phase-2-light proposal batch review

- Smoke run: `phase_2_light_smoke_1781290687.json`
- n_input_files: 2138
- n_atoms_baseline: 1742
- elapsed: 747.4s
- proposals: 100

## Instructions

For each proposal: replace `[ ]` with `[A]`=ACCEPT, `[R]`=REJECT, `[U]`=UPDATE (existing atom), `[D]`=DEFER, `[M]`=MODIFY (note in comment).

---

### #1. `fail_fast` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.99)
- Distant supervision: max score 0.00
- Raw mentions: ['Fail-fast', 'Fail-fast', 'fail-fast']
- Source files (sample): ['research_drill_self_modification_5x_2026-06-10.md', 'research_drill_substrate_failure_modes_catalog_5x_2026-06-08.md', 'research_drill_production_deployment_architecture_2026-06-07.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: fail_fast
  ```

### #2. `fast_fail` (Z=5)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.99)
- Distant supervision: max score 0.00
- Raw mentions: ['fast-fail', 'fast-fail', 'fast-fail']
- Source files (sample): ['exp_dev_to_testbed_v8_ack_defer_pythia_first_2026-06-04.md', 'testbed_to_exp_dev_pythia160m_extraction_ready_to_queue_2026-06-04.md', 'testbed_to_exp_dev_phase05_llama_v8_diagnostic_watchdog_kill_v7_2026-06-04.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: fast_fail
  ```

### #3. `universal_relation` (Z=9)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.99)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - science::PHYS/jarzynski_equality (sim=0.33)
- Raw mentions: ['universal-relation', 'universal-relation', 'universal-relation']
- Source files (sample): ['research_drill_cross_domain_revival_3x_2026-06-10.md', 'exp_dev_to_research_P9_CONTROL_RESULT_DECISIVE_2026-06-10.md', 'research_to_exp_dev_P9_CONTROLS_URGENT_2026-06-10.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: universal_relation
  ```

### #4. `feature_headroom` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.99)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T3/feature_hashing (sim=0.33)
- Raw mentions: ['feature_headroom', 'feature-headroom', 'feature-headroom']
- Source files (sample): ['testbed_to_research_PHASE_2_LIGHT_SMOKE_ARCHITECTURALLY_PASS_EXTRACTION_QUALITY_HARDFAIL_LIGHTWEIGHT_BASELINE_DIRECTION_REQUEST_2026-06-12.md', 'research_drill_substrate_classical_mechanism_transfer_replication_2x_2026-06-12.md', 'research_drill_substrate_methodology_rule_calibration_2x_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: feature_headroom
  ```

### #5. `already_implemented` (Z=6)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.99)
- Distant supervision: max score 0.00
- Raw mentions: ['already-implemented', 'ALREADY IMPLEMENTED', 'Already Implemented']
- Source files (sample): ['research_to_exp_dev_GO_FULL_MULTIHOP_BUILD_REUSABLE_SUBSTRATE_PRODUCT_2026-06-11.md', 'research_drill_nl_understanding_universal_unlock_3x_2026-06-11.md', 'research_drill_field_streaming_algorithms_5x_2026-06-07.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: already_implemented
  ```

### #6. `brief_spike` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.99)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - science::BIO/neuron_action_potential (sim=0.33)
- Raw mentions: ['brief-spike', 'brief-spike', 'brief-spike']
- Source files (sample): ['strategy_decisions_2026-05-24.md', 'visibility_decisions_2026-05-24.md', 'research_routing_2026-05-24_v182_filed.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: brief_spike
  ```

### #7. `reed_solomon` (Z=24)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.99)
- Distant supervision: max score 0.00
- Raw mentions: ['reed_solomon', 'Reed-Solomon', 'Reed-Solomon']
- Source files (sample): ['testbed_to_research_PHASE_2_LIGHT_SMOKE_ARCHITECTURALLY_PASS_EXTRACTION_QUALITY_HARDFAIL_LIGHTWEIGHT_BASELINE_DIRECTION_REQUEST_2026-06-12.md', 'strategy_decisions_2026-06-11.md', 'research_decisions_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: reed_solomon
  ```

### #8. `independent_verifier` (Z=7)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.99)
- Distant supervision: max score 0.00
- Raw mentions: ['independent_verifier', 'independent_verifier', 'independent_verifier']
- Source files (sample): ['research_to_testbed_PHASE_2_LIGHT_OPTION_A_PLUS_PLUS_FORMAL_P30_0_533_MIDDLE_BAND_PASS_SHIP_AS_PRODUCTION_MIN_VIABLE_BUILD_OPTION_B_PARALLEL_2026-06-12.md', 'testbed_to_research_PHASE_2_LIGHT_OPTION_A_PLUS_PLUS_META_JARGON_BLOCKLIST_P30_0_50_TO_0_63_HARDPASS_EDGE_2026-06-12.md', 'testbed_to_research_PHASE_2_LIGHT_OPTION_A_DIAGNOSTIC_TIGHTENED_FILTERS_P30_MIDDLE_BAND_FLOOR_CHARACTERIZED_OPTION_B_NEXT_2026-06-12.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: independent_verifier
  ```

### #9. `agent_skeptic` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 15 (density=2 atoms; novelty=0.99)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - concept::MWP/ROLE_ARG0_agent (sim=0.33)
- Raw mentions: ['Agent SKEPTIC', 'Agent SKEPTIC', 'Agent SKEPTIC']
- Source files (sample): ['research_N65536_codebook_engineering_2026-05-22.md', 'research_decisions_2026-05-21.md', 'research_substrate_as_OAQEC_2026-05-22.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 15
  about_topic: agent_skeptic
  ```

### #10. `temperature_scaled` (Z=8)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['temperature-scaled', 'temperature-scaled', 'Temperature-scaled']
- Source files (sample): ['research_drill_substrate_confidence_continuous_3x_2026-06-10.md', 'research_drill_negative_conformal_coverage_2x_2026-06-08.md', 'research_drill_tier5c_substrate_intrinsic_llm_aggressive_5x_2026-06-08.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: temperature_scaled
  ```

### #11. `data_streams` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 7 (density=2 atoms; novelty=0.99)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - science::CS/data_structure (sim=0.33)
  - science::CS/data_structure (sim=0.33)
- Raw mentions: ['Data Streams', 'Data Streams', 'Data Streams']
- Source files (sample): ['research_drill_field_streaming_algorithms_5x_2026-06-07.md', 'research_drill_composition_cascade_closure_3x_2026-06-07.md', 'research_drill_sleep_defrag_implicit_generalization_3x_2026-06-07.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 7
  about_topic: data_streams
  ```

### #12. `strong_negative` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['STRONG NEGATIVE', 'STRONG NEGATIVE', 'STRONG NEGATIVE']
- Source files (sample): ['research_BetY_V2D_OAQEC_pre_investigation_2026-05-22.md', 'research_blocker.md', 'research_decisions_2026-05-21.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: strong_negative
  ```

### #13. `dp_by_construction` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.98)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T3/dynamic_programming (sim=0.33)
- Raw mentions: ['DP-by-construction', 'DP-by-construction', 'DP-by-construction']
- Source files (sample): ['research_POST_COMPACTION_BRIEF_2026-06-07_evening.md', 'research_to_exp_dev_field_DP_5x_AUTHORIZE_2026-06-07.md', 'research_drill_field_differential_privacy_5x_2026-06-07.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: dp_by_construction
  ```

### #14. `modular_composite_representations` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 5 (density=3 atoms; novelty=0.99)
- Distant supervision: max score 0.00
- Raw mentions: ['Modular Composite Representations', 'Modular Composite Representations', 'Modular Composite Representations']
- Source files (sample): ['research_drill_bundle_capacity_limits_2x_2026-06-09.md', 'research_drill_field_VSA_NeSy_rule_DEEPER_5x_2026-06-07.md', 'research_drill_wish_we_had_3x_2026-06-07.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 5
  about_topic: modular_composite_representations
  ```

### #15. `modal_k` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['modal-K', 'modal-K', 'MODAL-K']
- Source files (sample): ['research_decisions_2026-06-09.md', 'exp_dev_to_research_LAPTOP_EXHAUSTED_NEED_WAVE2_2026-06-09.md', 'exp_dev_to_research_LAPTOP_BATCH_DONE_LAP3_DESIGN_Q_2026-06-09.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: modal_k
  ```

### #16. `cross_validate` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.98)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T1/cross_entropy (sim=0.33)
  - math::T3/cross_validation (sim=0.33)
- Raw mentions: ['cross-validate', 'cross-validate', 'cross-validate']
- Source files (sample): ['research_to_exp_dev_testbed_VERIFICATION_COMPLETE_5TH_RULE_CONFIRMED_TIER_5_SCOPE_2026-06-12.md', 'research_to_exp_dev_PROMOTION_CAMPAIGN_WAVES_2026-06-11.md', 'strategy_decisions_2026-05-30.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: cross_validate
  ```

### #17. `no_hallucination` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['no-hallucination', 'no-hallucination', 'NO HALLUCINATION']
- Source files (sample): ['research_drill_substrate_frontier_scale_interaction_2x_2026-06-11.md', 'research_drill_sprint1_arch_implications_2x_2026-06-10.md', 'strategy_decisions_2026-05-27.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: no_hallucination
  ```

### #18. `algebra_hrr` (Z=69)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.98)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T2/circular_convolution (sim=0.33)
  - math::T1/lie_algebra (sim=0.33)
- Raw mentions: ['algebra_hrr', 'algebra_hrr', 'algebra_hrr']
- Source files (sample): ['research_to_testbed_PHASE_2_LIGHT_OPTION_A_PLUS_PLUS_FORMAL_P30_0_533_MIDDLE_BAND_PASS_SHIP_AS_PRODUCTION_MIN_VIABLE_BUILD_OPTION_B_PARALLEL_2026-06-12.md', 'testbed_to_research_PHASE_2_LIGHT_OPTION_A_PLUS_PLUS_META_JARGON_BLOCKLIST_P30_0_50_TO_0_63_HARDPASS_EDGE_2026-06-12.md', 'research_drill_free_probability_F4_free_cumulants_substrate_observability_beyond_mean_variance_2x_2026-06-12.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: algebra_hrr
  ```

### #19. `prior_art` (Z=14)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['prior-art', 'Prior-art', 'prior-art']
- Source files (sample): ['research_drill_substrate_self_discovery_validation_2x_2026-06-11.md', 'research_drill_algebra_taxonomy_formal_systems_2x_2026-06-11.md', 'testbed_to_research_INDEX_ALGEBRA_VEC_EXTENSION_PROPOSAL_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: prior_art
  ```

### #20. `bounded_moment` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['Bounded Moment', 'Bounded Moment', 'Bounded Moment']
- Source files (sample): ['research_decisions_2026-05-23.md', 'visibility_decisions_2026-05-23.md', 'exp_dev_to_queue_bbmd_anchors_2026-05-23.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: bounded_moment
  ```

### #21. `phys_rev_lett` (Z=13)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 5 (density=3 atoms; novelty=0.99)
- Distant supervision: max score 0.00
- Raw mentions: ['Phys Rev Lett', 'Phys Rev Lett', 'Phys Rev Lett']
- Source files (sample): ['research_drill_free_probability_F4_substrate_observability_3x_2026-06-11.md', 'research_drill_slipnet_polysemic_alt_rescues_2x_2026-06-11.md', 'research_drill_frustration_deep_3x_2026-06-10.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 5
  about_topic: phys_rev_lett
  ```

### #22. `cycle_176` (Z=6)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['cycle-176', 'cycle-176', 'cycle-176']
- Source files (sample): ['strategy_decisions_2026-06-08.md', 'orchestrator_to_research_results_summary_2026-06-08_cycle179.md', 'strategy_decisions_2026-06-07.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: cycle_176
  ```

### #23. `bpc_and` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['BPC AND', 'BPC AND', 'BPC AND']
- Source files (sample): ['research_to_exp_dev_tier6_phase_D_and_tier4_attention_substitution_2026-06-04.md', 'research_routing_v359_substrate_context_training_probe_dossier_2026-06-03.md', 'research_routing_v359_three_drill_integration_synthesis_2026-06-03.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: bpc_and
  ```

### #24. `unit_cues` (Z=7)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 15 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T1/unit_modulus (sim=0.33)
- Raw mentions: ['unit-cues', 'unit-cues', 'unit-cues']
- Source files (sample): ['exp_dev_to_research_PHASE4B_WALL_REQUEST_2026-06-11.md', 'research_to_exp_dev_SVAMP_PERCEPTRON_SHIP_DEPPARSER_RESTORED_2026-06-11.md', 'strategy_request_to_exp_dev_from_exp_dev_PHASE4B_WALL_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 15
  about_topic: unit_cues
  ```

### #25. `fast_slow` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 5 (density=3 atoms; novelty=0.99)
- Distant supervision: max score 0.00
- Raw mentions: ['fast-slow', 'Fast-Slow', 'fast-slow']
- Source files (sample): ['research_drill_conversation_memory_streaming_2x_2026-06-11.md', 'research_drill_multi_substrate_engineered_3x_2026-06-11.md', 'research_drill_natural_analog_hippocampal_5x_2026-06-07.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 5
  about_topic: fast_slow
  ```

### #26. `vsa_h3` (Z=10)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 7 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - school::SCHOOL/vsa_family (sim=0.33)
- Raw mentions: ['VSA H3', 'VSA-H3', 'VSA-H3']
- Source files (sample): ['strategy_decisions_2026-06-11.md', 'research_to_exp_dev_SLIPNET_REFUTATION_ENDORSED_2026-06-11.md', 'research_drill_reasoning_composition_routing_2x_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 7
  about_topic: vsa_h3
  ```

### #27. `psychological_review` (Z=30)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 7 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['Psychological Review', 'Psychological Review', 'Psychological Review']
- Source files (sample): ['research_drill_substrate_eval_recall_gap_alternatives_2x_2026-06-11.md', 'research_drill_slipnet_13_untested_paths_2x_2026-06-11.md', 'research_drill_cls_2substrate_rescue_2x_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 7
  about_topic: psychological_review
  ```

### #28. `if_bet` (Z=8)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['If Bet', 'If Bet', 'If Bet']
- Source files (sample): ['research_bet_n_design_readiness_2026-05-25.md', 'strategy_decisions_2026-05-23.md', 'research_BetE_parisi_methodology_2026-05-21.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: if_bet
  ```

### #29. `scaled_sharpness` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['scaled-sharpness', 'Scaled-sharpness', 'scaled_sharpness']
- Source files (sample): ['visibility_decisions_2026-06-12.md', 'strategy_decisions_2026-06-12.md', 'strategy_request_to_research_2026-06-12_cliff_sharpness_marchenko_pastur_bulk_rederivation_RESCUE2_v592.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: scaled_sharpness
  ```

### #30. `sh_atoms` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 15 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['sh-atoms', 'sh-atoms', 'sh-atoms']
- Source files (sample): ['research_to_exp_dev_PP_398_399_400_BACKFILL_CELEBRATE_TIER5_ONE_CAP_AWAY_CYCLE_49_MULTI_OCCURRENCE_NER_COREF_2026-06-12.md', 'exp_dev_to_research_testbed_PP398_PP399_PP400_BACKFILL_DONE_TIER5_RERUN_MIDDLE_2026-06-12.md', 'exp_dev_to_research_testbed_CORRECTION_TIER5_NOT_COUNT_BUT_COMPOSITION_2026-06-12.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 15
  about_topic: sh_atoms
  ```

### #31. `pp_324` (Z=6)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 7 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['PP-324', 'PP-324', 'PP-324']
- Source files (sample): ['strategy_decisions_2026-06-11.md', 'research_decisions_2026-06-10.md', 'visibility_decisions_2026-06-10.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 7
  about_topic: pp_324
  ```

### #32. `relation_sharding` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.98)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - science::PHYS/jarzynski_equality (sim=0.33)
- Raw mentions: ['relation-sharding', 'relation-sharding', 'relation-sharding']
- Source files (sample): ['research_drill_kb_shard_production_2x_2026-06-10.md', 'strategy_decisions_2026-06-08.md', 'orchestrator_to_research_results_summary_2026-06-08_cycle185.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: relation_sharding
  ```

### #33. `name_field` (Z=10)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 15 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T1/complex_field (sim=0.33)
  - math::T1/real_field (sim=0.33)
  - math::T1/field_axioms (sim=0.33)
- Raw mentions: ['name-field', 'name-field', 'name-field']
- Source files (sample): ['exp_dev_to_research_COMPOSITE_VS_ALGEBRA_A_AXIS_INTERNAL_CONFIRMS_COMPOSITE_PLUS0_026_OVER_ALGEBRA_BUT_SET_UNION_EXPANSION_LOSES_TO_BGE_2026-06-12.md', 'strategy_decisions_2026-06-12.md', 'strategy_request_to_research_2026-06-12_free_probability_drill_pairs_with_PP409_production_fix_prediction_test_v587.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 15
  about_topic: name_field
  ```

### #34. `dw_ij` (Z=5)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['dw_ij', 'dw_ij', 'dw_ij']
- Source files (sample): ['research_drill_stdp_temporal_asymmetry_substrate_2x_2026-06-04.md', 'research_drill_bcm_snr_vs_polynomial_p_2x_2026-06-04.md', 'research_drill_substrate_training_n_threshold_3x_2026-06-04.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: dw_ij
  ```

### #35. `registered_negative_outcomes` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['registered_negative_outcomes', 'registered_negative_outcomes', 'REGISTERED NEGATIVE OUTCOMES']
- Source files (sample): ['testbed_to_research_PHASE_2_LIGHT_SMOKE_ARCHITECTURALLY_PASS_EXTRACTION_QUALITY_HARDFAIL_LIGHTWEIGHT_BASELINE_DIRECTION_REQUEST_2026-06-12.md', 'research_drill_elegant_hyperdimensional_mathematics_representation_4x_2026-06-12.md', 'research_drill_mwp_comprehension_wall_phase_6_corpus_3x_2026-06-12.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: registered_negative_outcomes
  ```

### #36. `semi_structured` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 7 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T2/role_filler_binding (sim=0.33)
  - math::T3/collins_structured_perceptron (sim=0.33)
- Raw mentions: ['semi-structured', 'semi-structured', 'semi-structured']
- Source files (sample): ['research_drill_benchmark_sweep_2x_2026-06-09.md', 'research_drill_dev_speed_acceleration_phase4a_infrastructure_2x_2026-06-05.md', 'research_drill_stdp_replay_decay_model_design_2x_2026-06-04.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 7
  about_topic: semi_structured
  ```

### #37. `shuffled_coupling` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['SHUFFLED-coupling', 'shuffled-coupling', 'shuffled-coupling']
- Source files (sample): ['research_critical_point_protocol_2026-05-21.md', 'research_decisions_2026-05-21.md', 'research_triple_point_deepdrill_2026-05-21.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: shuffled_coupling
  ```

### #38. `data_minimization` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 5 (density=3 atoms; novelty=0.99)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - science::CS/data_structure (sim=0.33)
  - science::CS/data_structure (sim=0.33)
- Raw mentions: ['data-minimization', 'data-minimization', 'data-minimization']
- Source files (sample): ['research_annealing_erasure_2026-05-21.md', 'research_decisions_2026-05-21.md', 'strategy_decisions_2026-05-21.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 5
  about_topic: data_minimization
  ```

### #39. `codeword_overlap` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 7 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['codeword-overlap', 'codeword-overlap', 'codeword-overlap']
- Source files (sample): ['research_request_antiRM_mechanism_drill_2026-05-24.md', 'visibility_decisions_2026-05-23.md', 'strategy_decisions_2026-05-23.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 7
  about_topic: codeword_overlap
  ```

### #40. `one_pass` (Z=11)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.98)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T1/unit_modulus (sim=0.33)
- Raw mentions: ['One-pass', 'one-pass', 'one-pass']
- Source files (sample): ['strategy_decisions_2026-06-07.md', 'exp_dev_to_research_substrate_native_multihop_WORKS_2026-06-07.md', 'research_to_exp_dev_resonator_bridge_extractor_PRIORITY_0_2026-06-07.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: one_pass
  ```

### #41. `strong_pass` (Z=7)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['STRONG PASS', 'STRONG PASS', 'STRONG PASS']
- Source files (sample): ['research_R12_sampling_rescues_2026-05-21.md', 'research_R13_drinfeld_double_binding_2026-05-21.md', 'research_R20_compositional_generalization_design_2026-05-21.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: strong_pass
  ```

### #42. `neurogenesis_expansion` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.98)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T1/taylor_series (sim=0.33)
- Raw mentions: ['NEUROGENESIS-EXPANSION', 'NEUROGENESIS-EXPANSION', 'NEUROGENESIS-EXPANSION']
- Source files (sample): ['research_to_exp_dev_REVIVAL_SUBSTRATE_NATIVE_ONLY_2026-06-10.md', 'research_to_exp_dev_AGGRESSIVE_REVIVAL_CONSOLIDATED_2026-06-10.md', 'research_drill_continual_learning_revival_3x_2026-06-10.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: neurogenesis_expansion
  ```

### #43. `carbonell_goldstein` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['Carbonell-Goldstein', 'Carbonell-Goldstein', 'Carbonell-Goldstein']
- Source files (sample): ['research_decisions_2026-06-07.md', 'research_to_exp_dev_BATCH_H_authorized_2026-06-07.md', 'research_drill_clustered_KB_anchoring_propagation_2x_2026-06-07.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: carbonell_goldstein
  ```

### #44. `sst_2` (Z=27)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 15 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['SST-2', 'SST-2', 'SST-2']
- Source files (sample): ['exp_dev_to_research_POS_CROSSDOMAIN_3RD_APPEARANCE_REFINES_RULE_TO_SPECTRUM_POS_TINY_TAIL_1_011_BETWEEN_NER_AND_CLOSED_2026-06-12.md', 'testbed_to_research_PHASE_2_LIGHT_SMOKE_ARCHITECTURALLY_PASS_EXTRACTION_QUALITY_HARDFAIL_LIGHTWEIGHT_BASELINE_DIRECTION_REQUEST_2026-06-12.md', 'research_to_testbed_PP401_A_AXIS_REMEASUREMENT_REASSIGN_TO_TESTBED_OWNS_UNION_A_INFRASTRUCTURE_2026-06-12.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 15
  about_topic: sst_2
  ```

### #45. `fact_hash` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['fact_hash', 'fact_hash', 'fact_hash']
- Source files (sample): ['research_drill_compliance_maximization_2x_2026-06-09.md', 'research_drill_demo_interface_capabilities_2x_2026-06-07.md', 'research_drill_substrate_production_scaling_5x_chain3_drill2_2026-06-07.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: fact_hash
  ```

### #46. `r16_bet` (Z=7)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['R16 Bet', 'R16 Bet', 'R16 Bet']
- Source files (sample): ['research_R18_RFOT_glassy_dynamics_2026-05-21.md', 'research_R21_cross_modal_binding_2026-05-21.md', 'research_R22_sleep_consolidation_2026-05-21.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: r16_bet
  ```

### #47. `cogn_sci` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['Cogn Sci', 'Cogn Sci', 'Cogn Sci']
- Source files (sample): ['research_drill_slipnet_substrate_only_untested_paths_2x_2026-06-11.md', 'research_drill_slipnet_real_polysemic_rescue_2x_2026-06-11.md', 'research_drill_cross_domain_real_polysemic_3x_2026-06-10.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: cogn_sci
  ```

### #48. `large_margin` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['large-margin', 'large-margin', 'large-margin']
- Source files (sample): ['research_drill_substrate_classical_NER_architectural_ceiling_beyond_feature_engineering_2x_2026-06-12.md', 'research_drill_substrate_CRF_universal_nl_2x_2026-06-11.md', 'strategy_decisions_2026-06-07.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: large_margin
  ```

### #49. `dp_from_scratch` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.98)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T3/dynamic_programming (sim=0.33)
- Raw mentions: ['DP-from-scratch', 'DP-from-scratch', 'DP-from-scratch']
- Source files (sample): ['research_annealing_erasure_2026-05-21.md', 'research_decisions_2026-05-21.md', 'strategy_decisions_2026-05-21.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: dp_from_scratch
  ```

### #50. `out_of_order` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 7 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['out-of-order', 'out-of-order', 'out-of-order']
- Source files (sample): ['research_drill_substrate_long_form_generation_2x_2026-06-10.md', 'research_drill_attention_injection_prior_art_5x_2026-06-08.md', 'research_drill_distributed_coordination_patterns_3x_2026-06-07.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 7
  about_topic: out_of_order
  ```

### #51. `resonator_full` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.97)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T3/resonator_network_decoder (sim=0.33)
- Raw mentions: ['Resonator FULL', 'Resonator FULL', 'Resonator FULL']
- Source files (sample): ['research_blocker.md', 'research_decisions_2026-05-21.md', 'research_multihop_mechanism_redrill_2026-05-22.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: resonator_full
  ```

### #52. `skin_effect` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 7 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['skin-effect', 'skin-effect', 'skin-effect']
- Source files (sample): ['research_drill_nhse_annulus_tau_scaling_2x_2026-06-04.md', 'research_drill_drift_detection_lyapunov_framework_2x_2026-06-04.md', 'research_comprehensive_audit_2026-05-23.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 7
  about_topic: skin_effect
  ```

### #53. `out_dir` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 7 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['out_dir', 'out_dir', 'out_dir']
- Source files (sample): ['testbed_to_exp_dev_phase05_llama_v8_diagnostic_watchdog_kill_v7_2026-06-04.md', 'exp_dev_to_orchestrator_shipped_2026-06-04_cycle67.md', 'strategy_decisions_2026-06-01.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 7
  about_topic: out_dir
  ```

### #54. `perplexity_based` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.97)
- Distant supervision: max score 0.00
- Raw mentions: ['perplexity-based', 'perplexity-based', 'perplexity-based']
- Source files (sample): ['research_to_exp_dev_NL_SYNTHESIS_PILOT_PLUS_RAG_TESTS_2026-06-11.md', 'research_drill_smoke_vs_full_methodology_2x_2026-06-09.md', 'research_drill_adversarial_robustness_adaptive_2x_2026-06-07.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: perplexity_based
  ```

### #55. `type_conditional` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 7 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - science::CS/type_theory (sim=0.33)
- Raw mentions: ['type-conditional', 'type-conditional', 'type-conditional']
- Source files (sample): ['research_drill_humaneval_substrate_generator_2x_2026-06-11.md', 'exp_dev_to_research_WAVE2_RESCUE_BATCH1_2026-06-11.md', 'research_drill_substrate_composition_operators_5x_2026-06-08.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 7
  about_topic: type_conditional
  ```

### #56. `causal_inference` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.97)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T3/bayesian_inference (sim=0.33)
  - math::T2_FAM/probabilistic_inference (sim=0.33)
  - math::T3/conformal_prediction (sim=0.33)
- Raw mentions: ['causal-inference', 'causal-inference', 'causal-inference']
- Source files (sample): ['research_drill_7_invariants_empirical_validation_2x_2026-06-11.md', 'strategy_decisions_2026-06-09.md', 'research_drill_counterfactual_capability_extension_2026-06-07.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: causal_inference
  ```

### #57. `pal_bridge` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.97)
- Distant supervision: max score 0.00
- Raw mentions: ['PAL-bridge', 'PAL-bridge', 'PAL-bridge']
- Source files (sample): ['research_to_exp_dev_8_DRILLS_CONSOLIDATED_BATCH_2026-06-08.md', 'research_drill_biology_of_substrate_capabilities_5x_2026-06-08.md', 'research_drill_substrate_math_capabilities_5x_2026-06-08.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: pal_bridge
  ```

### #58. `ieee_trans_it` (Z=6)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.97)
- Distant supervision: max score 0.00
- Raw mentions: ['IEEE Trans IT', 'IEEE Trans IT', 'IEEE Trans IT']
- Source files (sample): ['research_drill_substrate_evaluation_methodology_5x_chain1_drill2_2026-06-07.md', 'research_drill_next_batch_standard_cells_synthesis_2026-06-06.md', 'research_drill_substrate_as_cognitive_core_training_methodology_3x_2026-06-04.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: ieee_trans_it
  ```

### #59. `same_day` (Z=8)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.97)
- Distant supervision: max score 0.00
- Raw mentions: ['same-day', 'same-day', 'same-day']
- Source files (sample): ['testbed_to_research_HYBRID_CYCLE49_NULL_NET_BROAD_VS_NARROW_SHAPE_PATH_FORWARD_2026-06-12.md', 'research_to_exp_dev_TIER5_MECHANISM_VALIDATED_FIRST_APPEARANCE_PHASE_6_LEVER_2026-06-12.md', 'research_drill_continual_scale_2x_2026-06-10.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: same_day
  ```

### #60. `multi_resolution` (Z=15)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 7 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['Multi-resolution', 'Multi-resolution', 'Multi-resolution']
- Source files (sample): ['research_drill_tbind_refinement_2x_2026-06-10.md', 'research_drill_negative_pp155_continuous_strength_2x_2026-06-08.md', 'research_to_exp_dev_NEGATIVE_RESCUES_2026-06-08.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 7
  about_topic: multi_resolution
  ```

### #61. `differential_calibration_mia_against_rag` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 7 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['Differential Calibration MIA Against RAG', 'Differential Calibration MIA Against RAG', 'Differential Calibration MIA Against RAG']
- Source files (sample): ['research_drill_privacy_failure_mechanism_3x_2026-06-07.md', 'research_drill_substrate_evaluation_methodology_5x_chain1_drill4_2026-06-07.md', 'research_drill_substrate_evaluation_methodology_5x_chain1_drill3_2026-06-07.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 7
  about_topic: differential_calibration_mia_against_rag
  ```

### #62. `speculative_decoding` (Z=8)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 7 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T3/viterbi_decoding (sim=0.33)
  - math::T2_FAM/sequence_decoding (sim=0.33)
  - math::T2_FAM/sequence_decoding (sim=0.33)
- Raw mentions: ['Speculative Decoding', 'Speculative Decoding', 'speculative-decoding']
- Source files (sample): ['research_drill_speculative_draft_maximization_2x_2026-06-09.md', 'research_to_exp_dev_WHATS_NEXT_RESPONSE_2026-06-09.md', 'research_drill_substrate_speculative_decoding_5x_2026-06-09.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 7
  about_topic: speculative_decoding
  ```

### #63. `before_day` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.97)
- Distant supervision: max score 0.00
- Raw mentions: ['BEFORE Day', 'BEFORE Day', 'BEFORE Day']
- Source files (sample): ['research_to_testbed_FINDINGS_05_DROP_CORPUS_PLUS_B_DAY2_EXPERIMENT_2026-06-11.md', 'research_to_testbed_DAY1_ACCELERATION_ENDORSED_PLUS_CONCEPT_SUBSET_2026-06-11.md', 'testbed_to_research_V2_ARCHITECTURE_ACK_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: before_day
  ```

### #64. `long_text` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.97)
- Distant supervision: max score 0.00
- Raw mentions: ['long-text', 'Long-text', 'long-text']
- Source files (sample): ['research_drill_substrate_creativity_capabilities_hard_drill_3x_2026-06-12.md', 'research_drill_asdiv_mixed_adversarial_2x_2026-06-11.md', 'research_drill_tbind_refinement_2x_2026-06-10.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: long_text
  ```

### #65. `krylov_budget` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 15 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['Krylov-budget', 'Krylov-budget', 'Krylov-budget']
- Source files (sample): ['strategy_decisions_2026-06-02.md', 'research_routing_v342_band_lifts_addendum_2026-06-02.md', 'strategy_request_to_exp_dev_cycle12_refill_2026-06-02.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 15
  about_topic: krylov_budget
  ```

### #66. `commercial_wedge` (Z=5)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 15 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['commercial-wedge', 'commercial-wedge', 'commercial-wedge']
- Source files (sample): ['research_high_yield_neighborhood_analysis_2026-05-24.md', 'strategy_decisions_2026-05-23.md', 'research_meta_map_and_adjacencies_2026-05-23.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 15
  about_topic: commercial_wedge
  ```

### #67. `agnostic_meta` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.97)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - science::CS/meta_learning (sim=0.33)
- Raw mentions: ['Agnostic Meta', 'Agnostic Meta', 'Agnostic Meta']
- Source files (sample): ['research_drill_self_modification_5x_2026-06-10.md', 'research_drill_meta_learning_middle_band_2x_2026-06-10.md', 'research_drill_cross_domain_analogy_mechanisms_3x_2026-06-10.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: agnostic_meta
  ```

### #68. `testbed_day` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.97)
- Distant supervision: max score 0.00
- Raw mentions: ['Testbed Day', 'Testbed Day', 'Testbed Day']
- Source files (sample): ['research_to_testbed_USER_MASSIVE_MATH_SCIENCE_INGESTION_PRIORITY_2026-06-11.md', 'research_to_testbed_DAY_2_PRIORITIES_AND_NEAR_TERM_GOAL_2026-06-11.md', 'research_to_testbed_v1_demo_SPEC_REVISED_2026-06-08.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: testbed_day
  ```

### #69. `basin_mapping` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.97)
- Distant supervision: max score 0.00
- Raw mentions: ['basin-mapping', 'basin-mapping', 'basin-mapping']
- Source files (sample): ['research_ags_retrieval_phase_substrate_2026-05-26.md', 'research_surge_synthesis_v276_2026-05-29.md', 'research_lagging_caps_v276_fresh_eyes_2026-05-29.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: basin_mapping
  ```

### #70. `parisi_virasoro` (Z=6)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 15 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['Parisi-Virasoro', 'Parisi-Virasoro', 'Parisi-Virasoro']
- Source files (sample): ['research_BetE_methodology_escalation_2026-05-21.md', 'research_R14_tomita_takesaki_2026-05-21.md', 'research_betS_K_ceiling_2026-05-22.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 15
  about_topic: parisi_virasoro
  ```

### #71. `script_fix` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 5 (density=3 atoms; novelty=0.99)
- Distant supervision: max score 0.00
- Raw mentions: ['script-fix', 'SCRIPT-FIX', 'script-fix']
- Source files (sample): ['orchestrator_to_exp_dev_gpu_oom_pattern_2026-06-06.md', 'strategy_decisions_2026-05-27.md', 'strategy_decisions_2026-05-24.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 5
  about_topic: script_fix
  ```

### #72. `session_arc` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 7 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['Session-arc', 'session-arc', 'session-arc']
- Source files (sample): ['strategy_decisions_2026-05-24.md', 'research_semiconductor_physics_substrate_analogies_2026-05-23.md', 'research_substrate_capabilities_not_being_probed_2026-05-23.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 7
  about_topic: session_arc
  ```

### #73. `alpha_sensitivity` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.97)
- Distant supervision: max score 0.00
- Raw mentions: ['alpha-sensitivity', 'alpha-sensitivity', 'alpha-sensitivity']
- Source files (sample): ['strategy_decisions_2026-06-03.md', 'research_drill_ck_aging_mu_nonunanimous_2026-06-03.md', 'research_drill_pp33_activation_barrier_refutation_deep_dive_2026-06-03.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: alpha_sensitivity
  ```

### #74. `wrong_tool` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.97)
- Distant supervision: max score 0.00
- Raw mentions: ['WRONG TOOL', 'wrong-tool', 'wrong-tool']
- Source files (sample): ['research_R14_tomita_takesaki_2026-05-21.md', 'research_R15_steenrod_operations_2026-05-21.md', 'research_decisions_2026-05-21.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: wrong_tool
  ```

### #75. `structured_codebook` (Z=27)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.97)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T2/role_filler_binding (sim=0.33)
  - math::T3/collins_structured_perceptron (sim=0.33)
- Raw mentions: ['structured-codebook', 'structured-codebook', 'structured-codebook']
- Source files (sample): ['strategy_request_to_research_2026-06-12_free_probability_drill_pairs_with_PP409_production_fix_prediction_test_v587.md', 'strategy_decisions_2026-06-09.md', 'research_decisions_2026-05-23.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: structured_codebook
  ```

### #76. `measuring_compositional_generalization` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.97)
- Distant supervision: max score 0.00
- Raw mentions: ['Measuring Compositional Generalization', 'Measuring Compositional Generalization', 'Measuring Compositional Generalization']
- Source files (sample): ['research_drill_categorical_ai_discocat_2x_2026-06-11.md', 'research_drill_symmetric_schema_methodology_blindspot_2x_2026-06-11.md', 'research_R3_compositional_generalization_2026-05-21.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: measuring_compositional_generalization
  ```

### #77. `cross_modal_consistency` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 15 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['cross-modal-consistency', 'CROSS-MODAL-CONSISTENCY', 'CROSS-MODAL-CONSISTENCY']
- Source files (sample): ['exp_dev_to_research_LAPTOP_EXHAUSTED_NEED_WAVE2_2026-06-09.md', 'research_to_exp_dev_OVERNIGHT_FILL_PRIORITIZED_2026-06-09.md', 'research_drill_realtime_multimodal_biology_3x_2026-06-09.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 15
  about_topic: cross_modal_consistency
  ```

### #78. `hebbian_class` (Z=6)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 5 (density=3 atoms; novelty=0.99)
- Distant supervision: max score 0.00
- Raw mentions: ['Hebbian-class', 'Hebbian-class', 'Hebbian-class']
- Source files (sample): ['research_to_exp_dev_B8_validated_pure_bio_confirmed_substrate_direct_LM_2026-06-04.md', 'research_drill_substrate_tier_emergent_tricks_per_llm_scale_2x_2026-06-04.md', 'research_drill_multimodal_substrate_primitives_2x_2026-06-04.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 5
  about_topic: hebbian_class
  ```

### #79. `pp_198` (Z=9)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 7 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['PP-198', 'PP-198', 'PP-198']
- Source files (sample): ['strategy_decisions_2026-06-09.md', 'research_drill_conv_breadth_maximization_2x_2026-06-09.md', 'research_to_exp_dev_HUGE_BATCH_IMMEDIATE_AND_OVERNIGHT_2026-06-09.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 7
  about_topic: pp_198
  ```

### #80. `evaluate_bpc` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.97)
- Distant supervision: max score 0.00
- Raw mentions: ['evaluate_bpc', 'evaluate_bpc', 'evaluate_bpc']
- Source files (sample): ['strategy_decisions_2026-05-26.md', 'exp_dev_to_queue_saad_solla_beti_moe_prebuilds_2026-05-26.md', 'exp_dev_to_queue_1rsb_hysteresis_v3_2026-05-26.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: evaluate_bpc
  ```

### #81. `basin_to_basin` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 7 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['basin-to-basin', 'basin-to-basin', 'basin-to-basin']
- Source files (sample): ['research_routing_v343_consolidated_priority_queue_2026-06-02.md', 'research_drill_arrhenius_paradox_substrate_deep_dive_2026-06-02.md', 'research_meta_map_and_adjacencies_2026-05-23.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 7
  about_topic: basin_to_basin
  ```

### #82. `strong_baselines` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.97)
- Distant supervision: max score 0.00
- Raw mentions: ['strong-baselines', 'strong-baselines', 'strong-baselines']
- Source files (sample): ['exp_dev_to_research_tier4llama_HP_hp12_killerdemo_HP_2026-06-05.md', 'exp_dev_to_research_phase2_audit_core_1b_HP_2026-06-05.md', 'exp_dev_to_research_introspection_HP_strongbaseline_honest_flag_2026-06-05.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: strong_baselines
  ```

### #83. `layer_zone` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 15 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T3/layer_normalization (sim=0.33)
  - math::T3/transformer_block (sim=0.33)
- Raw mentions: ['Layer-zone', 'layer-zone', 'layer_zone']
- Source files (sample): ['research_drill_multi_channel_orchestration_failure_3x_2026-06-04.md', 'research_decisions_2026-06-03.md', 'research_drill_8_channel_orchestration_architecture_2026-06-03.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 15
  about_topic: layer_zone
  ```

### #84. `arxiv_2m` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.97)
- Distant supervision: max score 0.00
- Raw mentions: ['arxiv_2m', 'arxiv_2m', 'arxiv_2m']
- Source files (sample): ['research_to_testbed_ARXIV_MATH_REINGEST_APPROVED_2026-06-11.md', 'testbed_to_research_ARXIV_MATH_VERIFY_RESULT_2026-06-11.md', 'research_to_testbed_INGEST_APPROVAL_2026-06-10.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: arxiv_2m
  ```

### #85. `stress_test` (Z=14)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 7 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T3/permutation_test (sim=0.33)
  - math::T3/permutation_test (sim=0.33)
- Raw mentions: ['stress-test', 'stress-test', 'stress-test']
- Source files (sample): ['research_drill_substrate_as_full_research_ledger_2x_2026-06-11.md', 'research_drill_substrate_proposed_architectures_2x_2026-06-11.md', 'research_drill_code2_bug_recall_close_2x_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 7
  about_topic: stress_test
  ```

### #86. `near_orthogonal` (Z=57)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.97)
- Distant supervision: max score 0.00
- Raw mentions: ['near-orthogonal', 'near-orthogonal', 'near-orthogonal']
- Source files (sample): ['research_drill_vsa_composition_decomposition_benchmark_methodology_2x_2026-06-12.md', 'research_drill_multi_tenant_privacy_scale_2x_2026-06-11.md', 'research_drill_slipnet_real_polysemic_rescue_2x_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: near_orthogonal
  ```

### #87. `protected_binding` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 7 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T2/fhrr_bind (sim=0.33)
  - math::T2/fhrr_bind (sim=0.33)
  - math::T2/context_binding (sim=0.33)
- Raw mentions: ['protected-binding', 'Protected-binding', 'protected-binding']
- Source files (sample): ['research_decisions_2026-06-07.md', 'research_to_exp_dev_natural_analog_5_pretests_AUTHORIZE_2026-06-07.md', 'research_drill_natural_analog_quorum_sensing_5x_2026-06-07.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 7
  about_topic: protected_binding
  ```

### #88. `comp_overcome_barrier` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 5 (density=3 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['COMP-OVERCOME-BARRIER', 'COMP-OVERCOME-BARRIER', 'COMP-OVERCOME-BARRIER']
- Source files (sample): ['research_to_exp_dev_COMP_DIRECTION_CONFIRMED_2026-06-10.md', 'research_to_exp_dev_CROSS_DOMAIN_REVISION_MULTI_TIER_2026-06-10.md', 'research_to_exp_dev_NEGATIVE_RESOLUTION_PRIORITIES_2026-06-10.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 5
  about_topic: comp_overcome_barrier
  ```

### #89. `depth_scaling` (Z=11)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.97)
- Distant supervision: max score 0.00
- Raw mentions: ['depth-scaling', 'depth-scaling', 'depth-scaling']
- Source files (sample): ['exp_dev_to_research_P9_ACK_AND_HANDOFF_2026-06-10.md', 'exp_dev_to_research_1BIT_BATTERY_COMPLETE_2026-06-10.md', 'research_to_exp_dev_GPU_PRIORITY_PP225_FACT_SCALE_2026-06-10.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: depth_scaling
  ```

### #90. `six_sub` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 15 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['Six Sub', 'SIX SUB', 'Six Sub']
- Source files (sample): ['research_drill_training_speed_hierarchical_architecture_2x_2026-06-04.md', 'research_drill_substrate_training_n_threshold_3x_2026-06-04.md', 'research_drill_spectral_gap_alternative_frameworks_2x_2026-06-04.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 15
  about_topic: six_sub
  ```

### #91. `lambda_a10` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 7 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - science::CS/lambda_calculus (sim=0.33)
  - science::CS/lambda_calculus (sim=0.33)
- Raw mentions: ['Lambda A10', 'Lambda A10', 'Lambda A10']
- Source files (sample): ['strategy_decisions_2026-06-03.md', 'exp_dev_to_strategy_pp50_n65536_cloud_routing_2026-06-03.md', 'exp_dev_to_strategy_n32768_oom_cloud_required_2026-06-03.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 7
  about_topic: lambda_a10
  ```

### #92. `net_neg` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.97)
- Distant supervision: max score 0.00
- Raw mentions: ['NET NEG', 'NET NEG', 'NET NEG']
- Source files (sample): ['research_to_testbed_FINDINGS_13_TIER_4_FIRST_APPEARANCE_2026-06-11.md', 'research_to_testbed_FINDINGS_12_HISTORIES_VALIDATED_Q1_Q2_Q3_Q4_ANSWERED_2026-06-11.md', 'testbed_to_research_INDEX_FINDINGS_12_SOLUTION_HISTORIES_UNIVERSAL_LEVER_QUANTIFIED_2026-06-11.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: net_neg
  ```

### #93. `spike_structured` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.97)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T2/role_filler_binding (sim=0.33)
  - math::T3/collins_structured_perceptron (sim=0.33)
  - science::BIO/neuron_action_potential (sim=0.33)
- Raw mentions: ['spike-structured', 'spike-structured', 'spike-structured']
- Source files (sample): ['visibility_decisions_2026-05-27.md', 'strategy_decisions_2026-05-27.md', 'strategy_decisions_2026-05-26.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: spike_structured
  ```

### #94. `structured_spike` (Z=9)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.97)
- Distant supervision: max score 0.33
- Closest existing atoms (token-Jaccard):
  - math::T2/role_filler_binding (sim=0.33)
  - math::T3/collins_structured_perceptron (sim=0.33)
  - science::BIO/neuron_action_potential (sim=0.33)
- Raw mentions: ['structured-spike', 'structured-spike', 'structured-spike']
- Source files (sample): ['research_promising_direction_2026-05-23.md', 'research_BetN_BetO_rehab_2026-05-21.md', 'research_BetP_semantic_codebook_2026-05-21.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: structured_spike
  ```

### #95. `algebra_hrr_cosine` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.97)
- Distant supervision: max score 0.00
- Raw mentions: ['algebra_hrr_cosine', 'algebra_hrr_cosine', 'algebra_hrr_cosine']
- Source files (sample): ['research_to_testbed_OPT_4_NULL_ACK_RULE_12_PARTITIONS_NOT_HIERARCHY_OPT_1_GREEN_LIGHT_OPT_5_BATCH_2_BGE_NAME_FRIENDLY_DESIGN_UNION_STRATEGY_2026-06-12.md', 'research_to_testbed_HYBRID_OPTION_4_CONVERGENT_BOTH_SIDES_PROCEED_NOVELTY_METRIC_CONFIRMS_RECALL_PRECISION_SPLIT_2026-06-12.md', 'research_to_testbed_HYBRID_NULL_NET_OPTION_SELECT_OPT_4_PRIMARY_OPT_2_DIAG_OPT_1_PARALLEL_RULE_12_CANDIDATE_2026-06-12.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: algebra_hrr_cosine
  ```

### #96. `bravyi_maslov` (Z=6)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 5 (density=3 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['Bravyi-Maslov', 'Bravyi-Maslov', 'Bravyi-Maslov']
- Source files (sample): ['strategy_decisions_2026-05-23.md', 'exp_dev_to_strategy_F4_v3_stim_shipped_plus_v2_retro_2026-05-23.md', 'strategy_to_exp_dev_F4_v3_stim_2026-05-23.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 5
  about_topic: bravyi_maslov
  ```

### #97. `constant_depth` (Z=6)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 7 (density=2 atoms; novelty=0.98)
- Distant supervision: max score 0.00
- Raw mentions: ['constant-depth', 'Constant-Depth', 'constant-depth']
- Source files (sample): ['research_drill_substrate_evidence_integration_K_fact_combination_2x_2026-06-05.md', 'research_drill_substrate_direct_generative_language_modeling_3x_2026-06-04.md', 'research_drill_substrate_true_task_complexity_scaling_law_2x_2026-06-04.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 7
  about_topic: constant_depth
  ```

### #98. `low_data_win_full` (Z=4)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.97)
- Distant supervision: max score 0.00
- Raw mentions: ['low-data-win-full', 'low-data-win-full', 'low-data-win-full']
- Source files (sample): ['research_to_exp_dev_LB_NER_MIDDLE_ACK_LLM_05B_FT_CROSSOVER_FOLLOWON_GPU_LA_ALSO_QUEUE_2026-06-12.md', 'research_to_exp_dev_testbed_LANGUAGE_CREATIVITY_DRILLS_LANDED_4_HARD_CELLS_ROUTED_NO_DEFEATISM_2026-06-12.md', 'research_to_exp_dev_HEADTOHEAD_ACK_STOP_FORMAT_CHASING_2026-06-12.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: low_data_win_full
  ```

### #99. `scipost_phys` (Z=5)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 16 (density=1 atoms; novelty=0.97)
- Distant supervision: max score 0.00
- Raw mentions: ['SciPost Phys', 'SciPost Phys', 'SciPost Phys']
- Source files (sample): ['research_drill_qb1_chain_capability_ceiling_deep_dive_2026-06-03.md', 'research_drill_qb1_chain_loading_boundary_2026-06-03.md', 'research_BetF_rehab_2026-05-21.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 16
  about_topic: scipost_phys
  ```

### #100. `hallucination_impossibility` (Z=3)

**Decision**: [ ] ACCEPT / [ ] REJECT / [ ] UPDATE / [ ] DEFER / [ ] MODIFY

- Tool route: `CREATE`
- Nearest cluster: 14 (density=1 atoms; novelty=0.97)
- Distant supervision: max score 0.00
- Raw mentions: ['hallucination-impossibility', 'hallucination-impossibility', 'hallucination-impossibility']
- Source files (sample): ['strategy_request_to_exp_dev_kf_battery_refill_2026-05-27.md', 'visibility_decisions_2026-05-27.md', 'strategy_decisions_2026-05-27.md']
- Proposed algebra_additions template (if ACCEPT-as-CREATE):
  ```yaml
  category_int: 14
  about_topic: hallucination_impossibility
  ```
