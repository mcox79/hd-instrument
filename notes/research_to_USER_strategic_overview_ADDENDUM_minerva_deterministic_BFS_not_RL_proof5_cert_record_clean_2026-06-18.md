# Research (Director) -> USER: ADDENDUM to strategic-overview synthesis (filed 11:00). Two cert-honesty corrections from Skunkworks's CAPABILITY_MAP landed-verify pass + PROOF #5 review: (1) The lit-anchor language "MINERVA path-walking RL" overstates -- the canonical MINERVA paper uses an RL-trained policy, but our 11th-rule architectural commitment (no learned-policy in reasoning loop) means our version must be the DETERMINISTIC BFS variant Exp-Dev specced for A1, NOT the RL policy. The PROVENANCE GATE works identically (every hop = persisted typed edge), but the path-SELECTION mechanism is deterministic-BFS not learned. Important for the cert-honesty of the synthesis. (2) PROOF #5 was VET'd BEFORE the land (Skunkworks SEMANTICS-MATCH conditional -> trio-confirm -> unconditional PASS -> land 58cfbc78); my earlier note saying "Exp-Dev landed without VET first" was a note-ordering lag, NOT a cert-integrity issue. Cert-record is clean. The CAPABILITY_MAP landed-verify also PASS'd cleanly (CERT 569 unchanged + both structural guards held in the landed atom).

**From:** Research (Director); USER-routed
**To:** USER
**Date:** 2026-06-18 ~11:10 PDT
**Re:** Strategic-overview addendum -- 2 cert-honesty corrections. fname_v2 50.

## Correction 1 -- MINERVA MUST be deterministic-BFS, NOT RL-trained policy

In the strategic-overview synthesis (11:00) I cited "MINERVA path-walking RL" as the literature anchor for ARC 1 multi-hop provenance. Skunkworks's cert-honesty catch on this is important:

```
The CANONICAL MINERVA paper (Das+18) uses an RL-TRAINED POLICY to pick
the next typed edge at each hop.

Our 11th-rule architectural commitment: NO LEARNED-POLICY in reasoning/cert loop
(the LLM ban generalizes -- no learned controller in the reasoning loop either).

So our version of A1 / B-alpha NARROW must be the DETERMINISTIC BFS variant
(exp_dev specced this; substrate-internal multi-hop path-walking with
deterministic path-selection over typed edges), NOT the RL-policy proper.

The PROVENANCE GATE is unchanged: every hop in the answer chain still maps
to a persisted typed edge; the multi-hop-provenance 5th self-cert gate
works identically.

What changes: the path SELECTION mechanism. Deterministic BFS guarantees
the same answer chain for the same query + same substrate state -- the
substrate is REPRODUCIBLE. RL-policy would introduce non-determinism +
a learned-controller in the reasoning loop (both 11th-rule-adverse).
```

The lit-drill EXCLUDED set (RotatE/R-GCN/PullNet/GraftNet -- vector or aggregation hops, not edge-auditable) was correctly excluded. The INCLUDED set (MINERVA-pattern + AMIE 3 + PRA) is still correct, but **MINERVA is included for its EDGE-AUDITABILITY pattern, not its RL policy**. We adapt it to deterministic BFS for the 11th-rule.

**Substantive implication:** the achievability assessment in the synthesis stays YES (deterministic-BFS multi-hop QA over the 18389 typed edges is straightforward graph algorithm work, not novel research). The cert path is actually *cleaner* with deterministic-BFS (provenance gate verifies same chain across runs).

## Correction 2 -- PROOF #5 cert-record was clean

In my earlier note ("CAPABILITY_MAP LANDED + parallel landings") I said PROOF #5 was "landed without your VET first." Skunkworks verified the cert-record: the actual sequence was:

```
1. Skunkworks SEMANTICS-MATCH = PASS (conditional on the #print-axioms trio)
2. Exp-Dev confirmed the trio producer-side ([propext, Classical.choice, Quot.sound])
3. Skunkworks SEMANTICS-MATCH = PASS UNCONDITIONAL -> land GO
4. Exp-Dev landed (commit 58cfbc78) -- the LANDED note explicitly cited
   "per your UNCONDITIONAL PASS"
5. Skunkworks landed-verify = PASS (count 5, CERT 569 unchanged)
6. Testbed 2nd-witness = 5-of-5 HARD_PASS (additive independent)
```

The cert-flow was followed correctly. My note was written before Skunkworks's VET notes propagated through the bus (note-ordering lag). **PROOF #5 cert-record is clean.** A PROOF_RECORD landing without VET would be a cert-integrity problem; this wasn't one. The 5-of-5 Testbed 2nd-witness HARD_PASS is the independent confirmation.

This is verify-the-referent in action (Skunkworks catching a Director mischaracterization of the cert-record); the discipline is working at its own layer.

## CAPABILITY_MAP landed-verify confirmed PASS

For completeness: Skunkworks independently scanned the landed CAPABILITY_MAP atom (verify-the-referent):
- CERT_CHAIN_GRADE = 569 UNCHANGED (Guard 2 held)
- capability_map atoms = 1 (first instance; pq=INVENTORY_NON_CERT + algebra=None + corpus=meta = both structural guards verified in landed atom)
- axiom_term 206/206 preserved (structurally excluded by algebra=None + corpus=meta)
- cap_pres 6/6 preserved
- The breadth-map is queryable by kind=capability_map

## The 3 USER asks from the strategic overview stand (unchanged)

```
1. USER GO on B-alpha NARROW (the foundation stone; now with the cert-honesty
   clarification: deterministic-BFS multi-hop QA over WordNet+GO, 1 cycle 3-4h)
2. Sign off on the priority order (ARC 0 spine -> ARC 1 NARROW B-alpha ->
   ARC 2 gate-encoding -> ARC 3/4 gated later)
3. Ratify honest-scope framing (substrate is cert-graded reasoning, not general
   oracle; 89% substrate-mechanism core / 11% applied-domain = real growth axis)
```

Substrate state unchanged from synthesis (atoms 41327; CERT 569; PROOF_RECORD 5; methodology_rule 45; audit_lesson 49; self-cert engine 4 LIVE; capability_map 1 LIVE; axiom_term + cap_pres preserved).

Standing reactive on your ratify + Skunkworks's cert-honesty pass on the synthesis (she's reactive on the draft; will run a precision check on the rationality/achievability/risk verdicts + the deterministic-BFS clarification).

Tag: strategic_overview_addendum_user_minerva_deterministic_bfs_not_rl_proof5_cert_record_clean_skunkworks_landed_verify_capability_map_pass_proof5_review_correction_1_minerva_path_walking_rl_overstate_canonical_paper_das18_rl_trained_policy_11th_rule_no_learned_policy_reasoning_loop_llm_ban_generalizes_no_learned_controller_a1_b_alpha_narrow_deterministic_bfs_variant_exp_dev_specced_substrate_internal_multi_hop_path_walking_deterministic_selection_typed_edges_not_rl_policy_provenance_gate_unchanged_hop_answer_chain_persisted_typed_edge_multi_hop_provenance_5th_self_cert_gate_identical_path_selection_mechanism_changes_deterministic_bfs_same_answer_chain_query_substrate_state_reproducible_rl_policy_non_determinism_learned_controller_reasoning_both_11th_adverse_lit_drill_excluded_rotate_r_gcn_pullnet_graftnet_vector_aggregation_hops_correctly_included_minerva_amie_3_pra_minerva_included_edge_auditability_pattern_not_rl_adapt_deterministic_bfs_substantive_implication_achievability_yes_deterministic_bfs_multi_hop_qa_18389_typed_edges_straightforward_graph_algorithm_not_novel_research_cert_path_cleaner_deterministic_bfs_provenance_gate_same_chain_across_runs_correction_2_proof_5_cert_record_clean_earlier_note_landed_without_vet_first_skunkworks_verified_cert_record_actual_sequence_semantics_match_pass_conditional_print_axioms_trio_exp_dev_confirmed_producer_propext_classical_choice_quot_sound_pass_unconditional_land_go_landed_58cfbc78_per_unconditional_pass_landed_verify_pass_count_5_cert_569_testbed_5_of_5_2nd_witness_hard_pass_additive_independent_cert_flow_followed_correctly_note_written_before_vet_propagated_bus_ordering_lag_clean_proof_record_landing_without_vet_cert_integrity_problem_wasnt_5_of_5_testbed_2nd_witness_hard_pass_independent_confirmation_verify_referent_action_skunkworks_director_mischaracterization_cert_record_discipline_working_own_layer_capability_map_landed_verify_pass_skunkworks_independent_scan_cert_chain_grade_569_guard_2_capability_map_1_first_instance_pq_inventory_non_cert_algebra_none_corpus_meta_structural_guards_verified_landed_axiom_206_excluded_algebra_meta_cap_pres_6_breadth_queryable_kind_3_user_asks_stand_unchanged_b_alpha_narrow_foundation_stone_cert_honesty_clarification_deterministic_bfs_multi_hop_qa_wordnet_go_1_cycle_3_4h_priority_order_arc_0_spine_arc_1_narrow_b_alpha_arc_2_gate_encoding_arc_3_4_gated_later_honest_scope_framing_cert_graded_reasoning_not_general_oracle_89_core_11_applied_growth_axis_substrate_unchanged_atoms_41327_cert_569_proof_5_methodology_45_audit_49_self_cert_4_capability_map_1_axiom_206_cap_pres_6_standing_ratify_skunkworks_cert_honesty_pass_synthesis_reactive_draft_precision_rationality_achievability_risk_verdicts_deterministic_bfs_clarification_fname_v2_50

-- Research (Director); USER-routed
