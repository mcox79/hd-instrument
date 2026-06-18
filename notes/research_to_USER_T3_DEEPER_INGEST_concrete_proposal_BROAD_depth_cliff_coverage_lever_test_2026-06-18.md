# Research (Director) -> USER: T3 deeper-ingest concrete proposal -- design exploration for the BROAD depth-cliff lever. The honest BROAD finding (HYPERNYM recall 0.607->0.368->0.200 at 2/3/4 hops) is testable as a COVERAGE/density hypothesis (Skunkworks AGREE on framing): denser HYPERNYM backbone -> fewer out-of-5k misses -> walker attests more paths -> higher recall at deep hops. SUBSTRATE STATE confirms sparsity: 2884 HYPERNYM edges over 5000 noun synsets = 0.58 edges/atom; current 5k = 4.2% of full WordNet (~117k synsets). Proposed test: targeted +5k WordNet ingest (10k total = 8.5% of full WordNet; estimated +3-5k HYPERNYM edges) -> re-run BROAD HYPERNYM benchmarks with deterministic-BFS cell -> measure cliff shift. Falsifiable; cheap; composes with FrameNet (independent).

**From:** Research (Director); USER-routed
**To:** USER
**Date:** 2026-06-18 ~15:10 PDT
**Re:** T3 deeper-ingest concrete proposal for your scope-decision. fname_v2.

## The honest finding being tested

BROAD landed an empirical curve for the substrate's composed-reasoning at scale:

```
HYPERNYM (taxonomy chains, animal -> mammal -> ... -> entity):
  2-hop recall: 0.607  (MIDDLE_BAND)
  3-hop recall: 0.368  (between MIDDLE_BAND and HARD-FAIL)
  4-hop recall: 0.200  (HARD-FAIL territory)
  
PART_OF (partonomy, finger -> hand -> arm):
  Depth-robust to 3 hops; the cliff is HYPERNYM-specific
```

This is the substrate's first cert-grade observation of WHERE composed-reasoning works and where it doesn't. The next question: **WHY does HYPERNYM cliff at 3+ hops?**

## Skunkworks-AGREE hypothesis: it's a coverage/density issue

```
MECHANISM (the explanation):
  Deeper hypernym chains route through MORE intermediate synsets.
  Each intermediate has a probability p_in_corpus of being in the 5k ingest.
  If ANY intermediate is OUT-of-5k -> the BFS walker can't attest the hop ->
      the path is REFUSED (it's not in the Store; un-attested hop = NON_CERT
      per the 5th multi-hop-provenance gate).
  
  -> P(full chain attestable) = p_in_corpus ^ chain_length
  -> Probability drops exponentially with depth
  -> Hence the cliff

THIS IS NOT:
  - A fundamental limit of the substrate's composed-reasoning capability
  - An algorithmic limit (deterministic BFS is complete + sound; 100% provenance)
  - A semantic limit (HYPERNYM relations DO chain semantically)

THIS IS:
  - A sparsity limit of the ingested backbone (5k = 4.2% of full WordNet)
  - The 5th gate working as designed (refusing un-attested hops honestly)
  - A testable, falsifiable prediction
```

## Substrate state (confirms the sparsity claim)

```
LEXICON atoms        5018 (5000 WordNet NOUN synsets + 18 other)
HYPERNYM edges       2884 (avg 0.58 hypernyms per atom)
Coverage             ~4.2% of full WordNet (~117k synsets total)
IS_A edges           7094 (GO partonomy; SCIENCE_CONCEPT)
PART_OF edges        434  (depth-robust per BROAD; subset of partonomy is dense)

Ingest pattern proven: Bucket B (5018+5000 = 10k atoms; 10412 typed edges)
Pre-ingest cert-gate: ALL passed via Skunkworks SCHEMA-VET-equiv
2nd-witness: Testbed independent harness 13/13 HARD_PASS
```

## Proposed test: targeted +5k WordNet ingest

```
PROPOSAL:
  Ingest +5k WordNet noun synsets (10k total = ~8.5% of full WordNet).
  Targeting strategy: by SEMANTIC FREQUENCY (most-frequently-referenced synsets
    + the synsets that connect existing atoms via 1-hop HYPERNYM gaps; closes
    the most coverage holes per atom added).
  Estimated +3-5k HYPERNYM edges (proportional to existing 0.58 ratio).
  
COST (cheap):
  - ~1-2h Bucket B pattern (proven)
  - No GPU (LEXICON ingest is laptop-side)
  - Skunkworks pre-ingest cert-gate-equiv (~30 min VET)

CERT-CONDITIONS (Skunkworks ARC-3 standing rules):
  - edge-budget declared (+5k atoms + ~3-5k edges)
  - 0-phantom verified post-ingest
  - axiom_term/cap_pres SNAPSHOT-before
  - SERIAL bulk
  - cross-corpus absence verified (no name-collisions with existing 5018 LEXICON)
  - RESEARCH_FINDING tier OR LEXICON variant (Skunkworks discretion at SCHEMA-VET)

TEST CELL:
  Re-run B-alpha BROAD HYPERNYM benchmarks with the denser substrate.
  Same B-alpha mechanism (deterministic BFS + 5th gate + independent nltk gold).
  Same pre-reg bands (HARD-PASS >=70% / HARD-FAIL <40%).
  Compare: 2-hop, 3-hop, 4-hop recall vs the BROAD baseline.

PREDICTION (the falsifiable hypothesis):
  - If COVERAGE hypothesis correct: recall at 3-4 hops should RISE proportional
    to the (1 - miss_probability) increase. Roughly:
        baseline p_in_corpus = 5000/117000 ~= 0.043
        new      p_in_corpus = 10000/117000 ~= 0.085
        recall(3-hop) baseline = ~0.368; expected new ~0.368 * (0.085/0.043)^2 ~= 1.4x
        recall(4-hop) baseline = ~0.200; expected new ~0.200 * (0.085/0.043)^3 ~= 1.5x
    BUT capped at 1.0 (saturation) + honest scope (the model is naive; reality more
    complex due to chain structure + targeted-ingest improving coverage above pure
    proportional)
  - If COVERAGE hypothesis WRONG (fundamental or algorithmic): recall stays similar
    -> the depth-cliff is a deeper finding (substrate-specific limit of composed
    reasoning) and we'd need a different lever

EITHER OUTCOME IS A CERT-GRADE FINDING:
  - RISE = coverage-lever CONFIRMED (denser ingest is the path to deeper reasoning)
  - FLAT = coverage-lever REFUTED (something else; valuable honest negative)
  Both are publishable substrate-science findings.
```

## Compose with existing roadmap

```
COMPOSES with:
  - FrameNet (if USER GOes that): SEMANTIC_FRAME atoms + frame-evokes edges
    independent; both could ingest in same 6h
  - The 5th multi-hop-provenance gate: already LIVE; enforces honest refusal
  - The 4-item joint-rec policy: ARC-3 OPEN with per-direction sign-off; this is
    a NEW direction under ARC-3 (technically an ARC-1 deeper-ingest scope question
    but the work is ARC-3 ingest-side)
  - Bucket B EXTENSION pattern: proven; cert-gates carry; risk LOW

ROADMAP placement:
  - This is preliminary design + concrete proposal (Director T3 deliverable today)
  - The actual ingest + re-test cycle = next-6h or later window (your scope-decision)
  - If GO: this becomes a new track in the next-6h or queues post-FrameNet
  - If HOLD: stays as documented design for future return
```

## Your scope-decision ask

```
3 options:

(a) GO on the deeper-ingest test as proposed
    -> Targeted +5k WordNet ingest + re-run BROAD HYPERNYM benchmarks
    -> ~3-4h total (ingest + cert-gate + re-test + verdict-VET)
    -> Falsifiable hypothesis test on the BROAD depth-cliff
    -> Could land another cert-grade composed-reasoning atom this window

(b) HOLD / QUEUE FOR LATER (e.g., after FrameNet lands)
    -> Stays as documented preliminary design
    -> Surfaces again when relevant (post-FrameNet; post-ARC-3 menu progress)

(c) REFRAME -- you see a different lever I'm missing
    -> Examples:
        - Test PART_OF depth-cliff before HYPERNYM (PART_OF was depth-robust;
          when does PART_OF cliff? at depth 4 or 5?)
        - Test combined HYPERNYM + PART_OF chains
        - Test denser ingest of OTHER WordNet POS (verbs, adjectives) since
          we only have nouns
        - Wait for FrameNet to land + test frame-edge composed reasoning instead
```

Director's lean: **(a) GO**, but (b) is equally reasonable if you want to sequence after FrameNet for cleaner timing.

This is the T3 deliverable promised in the 6h plan (preliminary design + concrete proposal for USER scope-decision when ready). Standing on your call + parallel execution on T2 (6th gate at Skunkworks bandwidth) + T5 (A2-v6 verdict cascade).

Tag: user_t3_deeper_ingest_concrete_proposal_broad_depth_cliff_coverage_lever_test_honest_finding_hypernym_recall_0_607_0_368_0_200_2_3_4_hops_part_of_depth_robust_3_cliff_hypernym_specific_substrate_first_cert_grade_observation_composed_reasoning_works_doesnt_skunkworks_agree_hypothesis_coverage_density_mechanism_deeper_chains_more_intermediates_each_probability_p_in_corpus_5k_any_out_of_5k_bfs_walker_attest_path_refused_5th_multi_hop_provenance_un_attested_non_cert_p_full_chain_p_in_corpus_chain_length_drops_exponentially_depth_cliff_not_fundamental_not_algorithmic_bfs_complete_sound_provenance_not_semantic_chain_semantically_sparsity_ingested_backbone_5k_4_2_full_wordnet_117k_5th_gate_working_designed_refusing_un_attested_honestly_testable_falsifiable_substrate_confirms_sparsity_lexicon_5018_5000_wordnet_noun_18_other_hypernym_2884_avg_0_58_atom_4_2_coverage_117k_is_a_7094_go_part_of_434_depth_robust_subset_dense_ingest_pattern_bucket_b_proven_5018_5000_10k_10412_typed_pre_ingest_cert_gate_schema_vet_equiv_passed_2nd_witness_testbed_13_proposed_test_targeted_5k_wordnet_10k_8_5_full_wordnet_targeting_semantic_frequency_referenced_synsets_1_hop_hypernym_gaps_closes_most_coverage_holes_atom_3_5k_hypernym_edges_proportional_0_58_cost_cheap_1_2h_bucket_b_no_gpu_lexicon_laptop_skunkworks_pre_ingest_30_min_cert_conditions_skunkworks_arc_3_standing_edge_budget_5k_atoms_3_5k_edges_0_phantom_axiom_cap_pres_snapshot_serial_bulk_cross_corpus_absence_no_collisions_research_finding_lexicon_variant_discretion_test_cell_re_run_b_alpha_broad_hypernym_denser_substrate_deterministic_bfs_5th_independent_nltk_gold_pre_reg_70_40_compare_2_3_4_hop_recall_baseline_prediction_falsifiable_coverage_correct_recall_3_4_hops_rise_proportional_miss_probability_baseline_0_043_new_0_085_recall_3_hop_baseline_0_368_new_1_4x_4_hop_baseline_0_200_new_1_5x_capped_1_saturation_naive_model_complex_chain_structure_targeted_ingest_above_proportional_coverage_wrong_fundamental_algorithmic_recall_similar_deeper_finding_substrate_specific_limit_composed_reasoning_different_lever_either_outcome_cert_grade_finding_rise_coverage_lever_confirmed_denser_path_deeper_flat_refuted_else_honest_negative_publishable_substrate_science_compose_framenet_user_go_semantic_frame_frame_evokes_independent_both_6h_5th_multi_hop_provenance_live_honest_refusal_4_item_joint_rec_arc_3_open_per_direction_sign_off_new_direction_arc_1_deeper_ingest_arc_3_ingest_side_bucket_b_extension_pattern_proven_carry_low_risk_roadmap_preliminary_concrete_director_t3_today_actual_ingest_re_test_next_6h_later_scope_decision_go_new_track_queues_post_framenet_hold_documented_design_future_return_scope_decision_3_options_a_go_proposed_targeted_5k_wordnet_re_run_broad_3_4h_ingest_cert_re_test_vet_falsifiable_cert_grade_composed_reasoning_window_b_hold_queue_later_post_framenet_lands_documented_relevant_arc_3_menu_progress_c_reframe_lever_missing_examples_part_of_depth_cliff_before_hypernym_robust_4_5_combined_hypernym_part_of_chains_denser_other_pos_verbs_adjectives_nouns_framenet_lands_frame_edge_composed_director_lean_a_go_b_reasonable_sequence_framenet_cleaner_timing_t3_deliverable_promised_6h_plan_preliminary_concrete_proposal_user_scope_decision_standing_call_parallel_t2_6th_gate_skunkworks_bandwidth_t5_a2_v6_verdict_cascade_fname_v2_50

-- Research (Director); USER-routed
