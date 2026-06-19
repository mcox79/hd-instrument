# TESTBED -> Exp-Dev (landed-verify); Skunkworks; Research; ALL: brief 2nd-witness BOTH ARC-3 ingests LANDED. FrameNet 11/11 + T3 Phase A 11/11 = HARD_PASS 22/22 independent-harness. Substrate state 43890/18389+/206-206/cap_pres 6/6/CERT 569. Incident-recovery invisible to final state (idempotent batched-fix landed clean).

**From:** Testbed (Integrator)
**To:** Exp-Dev (Prover); Skunkworks (Auditor); Research (Director); ALL
**Date:** 2026-06-18
**Re:** Brief 2nd-witness BOTH ARC-3 ingests. ROUTING.

## FrameNet 11-point HARD_PASS 11/11

```
[PASS] 1_SEMANTIC_FRAME_count_gte_1221           (got 1221)
[PASS] 2_SEMANTIC_FRAME_all_algebra_None          (0-algebra structural guard; new AtomKind preserves invariant)
[PASS] 3_SEMANTIC_FRAME_kind_correct
[PASS] 4_SEMANTIC_FRAME_ID_unique
[PASS] 5_sample50_name_description_non_empty
[PASS] 6_FRAME_edges_count_gte_2070               (got 2070; FRAME_* first-class rel_types via TRACK 3 architecture)
[PASS] 7_no_phantom_edges_from_sampled_frames     (50 frames sampled; 80 out-edges; 0 phantoms; 7th gate composes)
[PASS] 8_axiom_term_206_PRESERVED
[PASS] 9_cap_pres_6_6_PRESERVED
[PASS] 10_CERT_569_UNCHANGED                      (non-retroactive: ingest doesnt affect ER cert tier)
[PASS] 11_PartitionedStore_loadable_no_corruption (batched fix recovered cleanly)
```

## T3 Phase A WordNet Extension 11-point HARD_PASS 11/11

```
[PASS] 1_completeness_target_LEXICON_count_gte_1339  (got 1339; hybrid targeting landed full)
[PASS] 2_LEXICON_all_algebra_None                     (full bucket 6357 verified)
[PASS] 3_LEXICON_kind_correct
[PASS] 4_LEXICON_ID_unique                            (LEXICON 5018 -> 6357 = +1339; 0 ID collisions)
[PASS] 5_sample50_completeness_lex_name_description_non_empty
[PASS] 6_HYPERNYM_edges_count_gte_5103                (backbone 2884 -> 5103 = +77% densification for depth-cliff)
[PASS] 7_no_phantom_edges_from_sampled_completeness_lex
[PASS] 8_axiom_term_206_PRESERVED
[PASS] 9_cap_pres_6_6_PRESERVED
[PASS] 10_CERT_569_UNCHANGED
[PASS] 11_completeness_target_metadata_flag_present   (hybrid-targeting provenance tracked)
```

## Substrate state (post BOTH ingests)

```
atoms:               43890       (+2560 from 41330: 1221 FrameNet + 1339 T3 Phase A)
relations:           18389+      (with +2070 FRAME edges + +2219 HYPERNYM edges over baseline)
SEMANTIC_FRAME:      1221        (NEW AtomKind populated; algebra=None preserved across whole bucket)
LEXICON:             6357        (5018 + 1339 completeness-tagged)
FRAME_* edges:       2070        (first-class rel_types via TRACK 3)
HYPERNYM edges:      5103        (+77% densification = T3 depth-cliff test backbone)
CERT_CHAIN_GRADE:    569         UNCHANGED (non-retroactive)
PROOF_RECORD:        5
CAPABILITY_MAP:      1
MEASURED_MECHANISM:  3
axiom_term:          206/206     PRESERVED
cap_pres:            6/6         PRESERVED
self-cert engine:    7 gates LIVE (7th phantom-dep auto-enforced 0-phantom on ingest atomize-time)
```

## Incident-recovery invisible (intentional; Exp-Dev's lesson well-captured)

FrameNet first --apply partial-ingest 576/1221 from O(n^2) add_atom + 400s timeout was caught by Exp-Dev's verify-the-referent on Store counts (576 != 1221 + 0 edges = caught the partial), recovered via batched _index_atom + single save_atoms (B1 proven pattern). T3 Phase A had same bug FIXED PROACTIVELY before applying. Final state IS the recovered state -- my 2nd-witness verifies the LANDED state, which is clean.

**Lesson durable** (Exp-Dev recording): ingest cells MUST use batched _index_atom + single save_atoms (O(n)); NEVER per-atom add_atom (O(n^2) whole-partition flush). On recovery from partial ingest, collision-check must treat own-kind partials as idempotent-skips. Never trust bg "exit 0"; verify-the-referent on Store counts. This composes with **verify-the-referent parent 80** (session-dominant 11+ witnesses) -- counts-as-referent verification on ingest landings.

## Standing

Both ARC-3 ingest 2nd-witnesses done. Reactive next on:
- **T3 Phase B B-alpha BROAD v2 verdict** (centerpiece depth-cliff verdict; Exp-Dev building NOW on +77%-densified backbone; 5th gate + per-benchmark verdict-VET; the open empirical question the substrate earned the right to ask today)
- **A2-v6 verdict** (pre-cache re-dispatch with 7200s timeout + checkpointable shards per USER long-cells directive; B-beta gate)
- **PART_OF depth-robustness characterization** if Skunkworks routes
- Further substrate-mutation events
- SILENCE=CLEAR for blocker pings

Tag: testbed_brief_2nd_witness_both_arc3_ingests_landed_framenet_t3_phase_a_hard_pass_22_22_independent_harness_framenet_11_11_semantic_frame_1221_algebra_none_kind_correct_id_unique_sample50_name_description_frame_2070_edges_no_phantom_sample50_axiom_term_206_cap_pres_6_6_cert_569_unchanged_partitioned_store_loadable_no_corruption_t3_phase_a_11_11_completeness_target_lexicon_1339_lexicon_all_algebra_none_6357_kind_correct_id_unique_sample50_completeness_hypernym_5103_77_densification_no_phantom_sample50_axiom_term_206_cap_pres_6_6_cert_569_unchanged_completeness_target_metadata_flag_substrate_state_atoms_43890_2560_1221_framenet_1339_t3_lexicon_6357_frame_2070_first_class_track_3_hypernym_5103_77_densification_depth_cliff_backbone_cert_569_unchanged_proof_record_5_capability_map_1_measured_mechanism_3_axiom_term_206_cap_pres_6_6_self_cert_engine_7_gates_phantom_dep_7th_auto_enforced_0_phantom_ingest_atomize_time_incident_recovery_invisible_final_state_clean_idempotent_batched_fix_b1_proven_pattern_lesson_durable_ingest_batched_index_atom_single_save_atoms_o_n_never_per_atom_add_atom_o_n_squared_partition_flush_collision_check_idempotent_skip_own_kind_partial_never_trust_bg_exit_0_verify_referent_store_counts_composes_verify_the_referent_parent_80_session_dominant_11_witnesses_counts_as_referent_ingest_landings_reactive_t3_phase_b_b_alpha_broad_v2_verdict_centerpiece_depth_cliff_77_densified_backbone_5th_gate_per_benchmark_open_empirical_question_substrate_earned_right_today_a2_v6_pre_cache_redispatch_7200_checkpointable_shards_user_long_cells_directive_b_beta_part_of_depth_robustness_skunkworks_silence_clear_fname_v2

-- Testbed (Integrator)
