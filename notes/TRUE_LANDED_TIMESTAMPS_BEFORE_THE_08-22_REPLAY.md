# THE REAL DATES OF LANDED RECORDS, PRESERVED BEFORE A REPLAY OVERWRITES THEM

**Captured 2026-08-22T22:00Z from `git show HEAD:<file>`, while the overwrite was still UNCOMMITTED.**

A re-run on 2026-08-22 replayed these cells' checkpoints, did no work, and rewrote `metrics.json`
with a fresh `ts_iso`. **The NUMBERS are unchanged -- only the date and the elapsed time.**
**This table is the recovery path: if the overwrite commits, the true measurement dates survive here.**

*Recorded rather than reverted. The files belong to a concurrent session and a revert could destroy
real work; preserving the evidence makes the decision reversible either way.*

## ALSO: 3 landed `metrics.json` are DELETED in the working tree

**That is data loss rather than re-dating, and a different decision.**

- `data/cornerstone_results/exp_cornerstone_c1_c2_c3_aggregate_llama_3_1_8b_v1_h100/metrics.json`
- `data/cornerstone_results/exp_cornerstone_c2_c3_audit_llama_3_1_8b_v1_h100/metrics.json`
- `data/cornerstone_results/exp_phase05_probe_training_v1/metrics.json`

## 54 re-dated records

| cell | TRUE date | overwritten to | true elapsed_s | replay elapsed_s |
|---|---|---|---|---|
| `exp_agreement_attractor_role_binding_cg_viability_v1` | **2026-07-22T14:49:15** | 2026-07-22T15:00:53 | 89.5 | 160.06 |
| `exp_attention_salience_reliability_gate_correlated_error` | **2026-07-20T05:11:01** | 2026-07-20T05:16:00 | 27.15799 | 26.39204 |
| `exp_attention_salience_reliability_gate_independent_chan` | **2026-07-20T04:48:40** | 2026-07-20T04:51:58 | 13.82188 | 13.49649 |
| `exp_base_first_reader_crosssentence_thematic_overlay_v1` | **2026-07-18T12:54:29** | 2026-07-18T12:57:36 | 0.385 | 0.391 |
| `exp_base_reader_grounded_relations_coref_v1` | **2026-07-18T13:28:30** | 2026-07-18T13:35:08 | 4.6999 | 4.4105 |
| `exp_breadth_foundation_curriculum_order_mcguffey_v1` | **2026-07-21T23:37:48** | 2026-07-21T23:48:27 | 45.18 | 27.44 |
| `exp_bridge1_twostage_event_situation_v2` | **2026-08-05T14:08:27** | 2026-08-22T02:40:30 | 31.36217 | 0.035531 |
| `exp_bridge1_twostage_event_situation_v2_smoke` | **2026-08-05T14:07:28** | 2026-08-22T02:40:56 | 14.63087 | 0.041359 |
| `exp_causal_link_comprehension_fuller_v2` | **2026-08-03T04:12:50** | 2026-08-03T06:41:51 | 0.439650 | 0.472158 |
| `exp_coherence_gate_extraction_correctness_independent_go` | **2026-07-19T07:19:16** | 2026-08-05T20:40:20 | 5.496177 | 24.41511 |
| `exp_coref_agreement_possessive_fix_v1` | **2026-07-18T16:41:03** | 2026-07-18T16:45:49 | 8.29 | 3.85 |
| `exp_encoder_teacher_sparsifier_bypass_v1_selftest` | **2026-07-04T19:09:16** | 2026-07-04T20:48:18 | 8.235329 | 8.114180 |
| `exp_foundation_validation_harness_v1_selftest` | **2026-08-12T14:10:59** | 2026-08-12T14:21:25 | 0.097486 | 0.026685 |
| `exp_hdlab_reasoner_composed_v1` | **2026-08-13T16:09:40** | 2026-08-18T23:35:04 |  |  |
| `exp_learned_role_assigner_reader_wildtext_v4` | **2026-07-18T15:12:47** | 2026-07-18T15:19:50 | 4.771 | 4.7311 |
| `exp_mcguffey_whoaffected_wsd_frame_selectional_v1` | **2026-07-21T20:39:36** | 2026-07-21T20:46:57 | 137.52 | 109.58 |
| `exp_multisource_arena_combination_menu_v1` | **2026-07-16T15:48:30** | 2026-07-16T17:56:38 | 4.662088 | 1.438289 |
| `exp_multisource_arena_conjunction_menu_v1` | **2026-07-16T16:13:37** | 2026-07-16T17:56:40 | 1.325210 | 1.343213 |
| `exp_multisource_arena_temporal_hold_recover_v1` | **2026-07-16T16:18:05** | 2026-07-16T17:56:25 | 1.297025 | 1.377553 |
| `exp_native_binding_compositional_generalization_v1` | **2026-07-25T17:22:03** | 2026-07-25T17:32:51 | 204.17 | 276.44 |
| `exp_np_head_finder_grounding_gate_break050_v1` | **2026-07-19T10:31:54** | 2026-07-19T10:36:25 | 15.01259 | 14.84716 |
| `exp_online_knowledge_condenser_selectional_v1` | **2026-07-23T12:53:54** | 2026-07-23T12:59:09 | 650.0851 | 6.018677 |
| `exp_pivot_scaled_seed_knowledge_table_v1` | **2026-07-23T14:11:01** | 2026-07-23T14:20:08 | 1.555930 | 3.532066 |
| `exp_quotative_speaker_attribution_stack_break050_v1` | **2026-07-19T12:03:57** | 2026-07-19T12:08:20 | 8.277734 | 8.414923 |
| `exp_read_deixis_participant_tracking_third_reader_v1` | **2026-07-18T23:15:45** | 2026-07-18T23:27:01 | 168.12 | 173.73 |
| `exp_read_grow_adaptor_pyp_kn_breadth_v1` | **2026-07-17T19:09:07** | 2026-07-20T11:35:15 | 5.216936 | 21.74647 |
| `exp_read_grow_construction_induction_dop_fragments_v1` | **2026-07-17T11:27:43** | 2026-07-20T11:33:24 | 3.223149 | 2.327071 |
| `exp_read_grow_foundation_realprose_glassbox_ie_v1` | **2026-07-17T02:26:30** | 2026-07-17T02:40:00 | 0.544056 | 1.346919 |
| `exp_read_grow_full_third_reader_clauseseg_generalization` | **2026-07-18T21:31:48** | 2026-07-18T21:40:10 | 100.27 | 111.64 |
| `exp_read_grow_knowledge_guided_bootstrap_v1` | **2026-07-18T03:44:19** | 2026-07-18T03:47:47 | 7.46 | 7.81 |
| `exp_read_grow_oov_verb_extension_v1` | **2026-07-17T04:51:54** | 2026-07-17T05:02:21 | 0.122925 | 0.299193 |
| `exp_read_grow_openvocab_fastmap_v1` | **2026-07-17T03:14:58** | 2026-07-17T03:19:11 | 0.166558 | 0.185103 |
| `exp_read_grow_schema_abstraction_predictive_precision_v2` | **2026-07-17T12:39:10** | 2026-07-20T11:34:08 | 6.560012 | 36.56667 |
| `exp_read_grow_textbook_isa_growth_v1` | **2026-07-18T00:29:48** | 2026-07-18T00:35:06 | 4.6 | 4.68 |
| `exp_read_grow_textbook_multihop_clean_foundation_v1` | **2026-07-18T11:12:09** | 2026-07-18T11:17:27 | 0.42 | 0.42 |
| `exp_read_grow_textbook_multihop_compose_v1` | **2026-07-18T00:55:22** | 2026-07-18T01:00:05 | 5.57 | 5.73 |
| `exp_read_grow_textbook_multihop_genus_head_v4` | **2026-07-18T01:46:11** | 2026-07-18T01:49:38 | 0.91 | 0.86 |
| `exp_reader_component_oracle_ablation_audit_v1` | **2026-07-23T20:00:24** | 2026-07-23T20:07:04 | 123.18 | 122.94 |
| `exp_reader_grade3_envelope_readtogrow_v1` | **2026-07-18T18:06:28** | 2026-07-18T18:14:26 | 3.37 | 3.26 |
| `exp_reader_image_word_grounding_v1` | **2026-07-22T00:17:07** | 2026-07-22T00:28:57 | 84.38854 | 104.6156 |
| `exp_reader_learned_clauseseg_shared_subject_v1` | **2026-07-18T19:51:36** | 2026-07-18T19:57:14 | 5.54 | 5.23 |
| `exp_reader_meaning_correction_case_sleep_affectedness_v1` | **2026-07-21T21:20:27** | 2026-07-21T21:34:34 | 6.95 | 7.53 |
| `exp_reader_mention_source_gold_vs_handrule_corefixed_v1` | **2026-07-18T17:28:51** | 2026-07-18T17:33:34 | 6.76 | 6.35 |
| `exp_reader_oracle_parser_upperbound_v1` | **2026-07-18T18:52:58** | 2026-07-18T18:56:57 | 8.28 | 21.54 |
| `exp_relational_vs_similarity_conflict_viability_probe_v1` | **2026-07-22T13:44:06** | 2026-07-22T13:49:12 | 9.72 | 20.81 |
| `exp_reward_contingency_credit_assignment_v1` | **2026-07-18T06:09:08** | 2026-07-18T06:14:09 | 70.03167 | 66.60544 |
| `exp_reward_contingency_nonstationary_tracking_v1` | **2026-07-18T07:32:39** | 2026-07-18T07:36:37 | 24.28142 | 24.05108 |
| `exp_role_filler_factorization_compgen_v1` | **2026-07-19T03:27:26** | 2026-07-19T03:32:48 | 17.19418 | 16.09602 |
| `exp_state_change_entailment_composition_v1` | **2026-07-21T22:35:55** | 2026-07-21T22:41:05 | 1.41 | 0.75 |
| `exp_three_factor_eligibility_distal_credit_v1` | **2026-07-18T04:19:50** | 2026-07-18T04:25:12 | 61.09615 | 63.91797 |
| `exp_three_tier_loop_genuine_cross_source_corroboration_v` | **2026-08-11T20:13:19** | 2026-08-11T20:29:10 | 0.210855 | 0.271766 |
| `exp_three_tier_loop_independence_weighted_confirm_v1_sel` | **2026-08-11T20:51:31** | 2026-08-11T21:13:00 | 0.017973 | 0.091471 |
| `exp_ud_ewt_semantic_affectedness_independent_scoreboard_` | **2026-07-21T20:51:28** | 2026-07-21T20:57:03 | 3.77 | 3.68 |
| `exp_vsa_native_bind_zeroshot_role_v1` | **2026-07-30T19:27:34** | 2026-07-30T19:31:39 | 30.86196 | 16.07385 |

**54 preserved.** *Oldest true date `2026-07-04`; all overwritten to 2026-08-22.*