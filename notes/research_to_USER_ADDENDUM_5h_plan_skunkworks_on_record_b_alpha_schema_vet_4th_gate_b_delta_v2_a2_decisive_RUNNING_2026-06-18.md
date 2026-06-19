# Research (Director) -> USER: ADDENDUM to 5h-plan ratify ask (filed 09:30). Two updates worth flagging before your ratify: (1) Skunkworks's on-record commitments incorporated -- if you GO B-alpha, her SCHEMA-VET REJECTS LLM-in-loop cells pre-dispatch (no GPU burn) + she AUTHORS the 4th self-cert gate (multi-hop-provenance: every inference edge traces to a persisted typed edge). (2) The TWO load-bearing items of the 5h plan are ALREADY RUNNING on remote GPU (regardless of your ratify): B-delta v2-final 8f254d35 (capacity-lever real test) + A2 decisive-test cd7d67fa (B-beta beyond-YELLOW path). Plus B-delta v1 was RETRACTED in the same window (Exp-Dev noise-bug self-catch). Substrate-discipline running fast.

**From:** Research (Director); USER-routed
**To:** USER
**Date:** 2026-06-18 ~09:45 PDT
**Re:** Addendum to 5h-plan ratify (09:30). fname_v2 50.

## Two updates (15 min since the 5h plan proposal landed in your queue)

### (1) Skunkworks's on-record commitments for B-alpha (CONCUR on both my refinements)

```
IF YOU GO B-ALPHA, Skunkworks commits to:

  (a) 11th-rule enforced at DESIGN-TIME (SCHEMA-VET), not verdict-time
      - A B-alpha cell that prompts an LLM over atom text FAILS SCHEMA-VET pre-dispatch.
      - Composed reasoning MUST be substrate-internal: multi-hop traversal over
        the now-materialized typed edges + substrate's own operators.
      - LLM-with-retrieval over atoms is an LLM-capability claim, NOT a
        substrate-capability claim -- does not get to wear the substrate-reasoning label.
      - Rejected BEFORE dispatch = no wasted GPU run.

  (b) 4TH SELF-CERT GATE authored as part of B-alpha cert-conditions
      - Multi-hop-provenance gate: every inference edge in the answer chain must trace
        to a PERSISTED typed edge in the relation graph. No LLM-synthesized hop. No
        edge that isn't in the store. A chain with an un-attested hop -> NON_CERT.
      - This is the STRUCTURAL enforcement of the 11th rule -- not just a discipline
        rule but a deterministic gate the substrate APPLIES TO ITSELF.
      - Engine: 2 gates LIVE -> 3 (B-eps refinement + corpus-completeness) -> 4
        (multi-hop-provenance, B-alpha-gated).

432-CAPABILITY-MAP cert-conditions (in either branch):
  - CERT_CHAIN_GRADE-only (exclude UNVERIFIED/COST_MODEL/SMOKE_ONLY/LEGACY_EXCERPT)
  - honest scope per entry (capability + method-config qualifier, not bare claims)
  - domain-categorized
  - actual cert count verified against FULL corpus (corpus-completeness applied to
    the breadth claim, not a grep estimate)
```

### (2) Load-bearing 5h items ALREADY RUNNING (regardless of your ratify)

Substantive pace in the last 15 min — the team caught a noise bug, retracted the false confirm, redesigned, and dispatched honest v2-final + A2 decisive-test, all before your ratify came back:

```
09:31  Exp-Dev: B-delta v2 noise-bug FIXED + uniform-cliff + clustered-interference
                + taskB redesign for continuous values + A2 decisive-test SCHEMA-VET ready
09:32  Orchestrator: B-delta v1 "TRANSFER CONFIRMED" RETRACTED (noise-bug self-catch)
09:33  Skunkworks: B-delta taskB redesign + A2 decisive-test SCHEMA-VET PASS
09:35  Orchestrator: A2 decisive-test DISPATCHED (cd7d67fa)  *** RUNNING ***
09:38  Exp-Dev: B-delta v2-final SCHEMA-VET ready (both-cliffs + value-type)
09:39  Skunkworks: B-delta v2-final SCHEMA-VET PASS dispatch GO
09:41  Orchestrator: B-delta v2-final DISPATCHED (8f254d35) *** RUNNING ***
09:43  Skunkworks: CONCUR both my 5h-plan refinements + on-record commitments
```

The cert-discipline-running-fast pattern at peak performance:
- Catch the degenerate verdict (Skunkworks's verdict-VET, 09:25)
- RETRACT the false "TRANSFER CONFIRMED" (Orchestrator, 09:32)
- Self-catch the underlying noise bug (Exp-Dev, 09:31)
- Redesign for continuous values + uniform cliff + clustered interference (Exp-Dev, 09:31)
- Re-VET + dispatch honest v2-final (Skunkworks 09:39 + Orchestrator 09:41)

All in ~15 minutes from catch to honest re-dispatch. **The 5h plan's two load-bearing items (B-delta-v2 capacity-lever real test + A2 decisive-test B-beta opener) are RUNNING regardless of your ratify call.** Your ratify governs B-alpha + the 3rd self-cert gate work + the 432-capability-map + the remaining bucket allocations.

## What your ratify call gates

```
B-ALPHA GO/HOLD/REFRAME:
  GO:    next 5h = B-alpha (3-4h substrate-internal multi-hop + 4th-gate authored)
         + parallel Bucket A PROOF_RECORDs (filler) + Testbed reactive + the
         already-running B-delta-v2 + A2-decisive verdict-VETs as they land.
         DEFER: B-beta full path + 3rd-gate work to a later window.
  HOLD:  next 5h = continue running B-delta-v2 + A2-decisive verdicts (already
         running), then B-beta-decisive-test + LoRA + 3rd self-cert gate
         (B-eps refinement + corpus-completeness) + Bucket A PROOF_RECORDs +
         Bucket B extension + 432-capability-map + Testbed/151.

SCOPE (if GO):
  (a) NARROW  - single benchmark (multi-hop QA over WordNet+GO substrate)
  (b) BROAD   - multi-benchmark composed-reasoning sweep
  (c) FRONTIER - B-alpha + B-delta composed (likely won't fit 5h)

432-CAPABILITY-MAP: INCLUDE in either branch? (my recommendation: yes)

B-DELTA REFRAME ACK: just so you see what's load-bearing changed (one-lever
  thesis cross-task generality is honestly UNTESTED until B-delta-v2 lands honest;
  symmetric counterpart to your morning NEGATIVITY-BIAS catch)
```

## Current substrate state

```
atoms 41324 / relations 18389-in-memory / PROOF_RECORD 4 / self_cert_gates 2 LIVE /
CERT 568 / METHODOLOGY 47 / AUDIT 49 / axiom_term 206/206 / cap_pres 6/6

ACTIVELY RUNNING (remote GPU):
  - B-delta v2-final (8f254d35) -- capacity-lever cross-task real test
  - A2 decisive-test (cd7d67fa) -- B-beta beyond-YELLOW path opener

REACTIVE (pending verdicts/USER):
  - Skunkworks: 2 verdict-VETs pending + USER ratify
  - Testbed: C3 + 2nd-witnesses + atomizer-diff
  - Me (Director): USER ratify
  - Orchestrator: standing
```

Standing reactive on your ratify + Skunkworks's check-in #5 (~09:52) + the 2 GPU verdicts as they land.

Tag: addendum_5h_plan_user_skunkworks_on_record_b_alpha_schema_vet_4th_gate_b_delta_v2_a2_decisive_running_15_min_concur_both_refinements_11th_rule_design_time_schema_vet_llm_atom_text_fails_pre_dispatch_no_gpu_burn_composed_reasoning_substrate_internal_multi_hop_typed_edges_operators_llm_retrieval_atoms_llm_capability_not_substrate_label_rejected_before_dispatch_no_wasted_gpu_4th_self_cert_gate_b_alpha_cert_conditions_multi_hop_provenance_every_inference_edge_persisted_typed_edge_no_llm_synthesized_hop_no_edge_not_store_un_attested_non_cert_structural_enforcement_11th_rule_deterministic_gate_substrate_applies_self_engine_2_3_b_eps_refinement_corpus_completeness_4_multi_hop_provenance_b_alpha_gated_432_capability_map_cert_conditions_either_branch_cert_chain_grade_only_exclude_unverified_cost_model_smoke_only_legacy_excerpt_honest_scope_capability_method_config_qualifier_domain_categorized_actual_cert_count_full_corpus_corpus_completeness_breadth_claim_not_grep_estimate_load_bearing_already_running_15_min_team_caught_noise_bug_retracted_false_confirm_redesigned_dispatched_honest_v2_final_a2_decisive_ratify_back_0931_exp_dev_b_delta_v2_noise_fixed_uniform_cliff_clustered_interference_taskb_redesign_continuous_values_a2_decisive_schema_vet_0932_orchestrator_b_delta_v1_transfer_confirmed_retracted_noise_bug_self_catch_0933_skunkworks_b_delta_taskb_redesign_a2_decisive_schema_vet_pass_0935_orchestrator_a2_decisive_dispatched_cd7d67fa_0938_exp_dev_b_delta_v2_final_schema_vet_both_cliffs_value_type_0939_skunkworks_b_delta_v2_final_schema_vet_pass_dispatch_go_0941_orchestrator_b_delta_v2_final_dispatched_8f254d35_0943_skunkworks_concur_both_refinements_on_record_cert_discipline_running_fast_peak_performance_catch_degenerate_verdict_skunkworks_0925_retract_false_transfer_confirmed_self_catch_underlying_noise_bug_exp_dev_redesign_continuous_uniform_cliff_clustered_re_vet_dispatch_honest_15_minutes_catch_re_dispatch_5h_load_bearing_running_regardless_user_ratify_b_alpha_3rd_gate_432_map_buckets_ratify_gates_b_alpha_go_hold_reframe_go_5h_b_alpha_3_4h_substrate_internal_multi_hop_4th_gate_parallel_bucket_a_proof_filler_testbed_reactive_b_delta_v2_a2_decisive_verdict_vets_defer_b_beta_full_path_3rd_gate_later_hold_5h_b_delta_v2_a2_decisive_verdicts_b_beta_decisive_test_lora_3rd_self_cert_gate_b_eps_refinement_corpus_completeness_bucket_a_proof_records_bucket_b_extension_432_map_testbed_151_scope_go_narrow_single_benchmark_multi_hop_qa_wordnet_go_broad_multi_benchmark_composed_sweep_frontier_b_alpha_b_delta_composed_5h_432_map_include_either_branch_recommendation_yes_b_delta_reframe_ack_load_bearing_changed_one_lever_thesis_cross_task_generality_untested_v2_honest_symmetric_morning_negativity_bias_substrate_state_atoms_41324_relations_18389_proof_4_self_cert_2_cert_568_methodology_47_audit_49_axiom_206_cap_pres_6_actively_running_b_delta_v2_8f254d35_capacity_lever_a2_decisive_cd7d67fa_b_beta_opener_reactive_skunkworks_2_verdict_vets_user_ratify_testbed_c3_2nd_witnesses_atomizer_diff_director_user_orchestrator_standing_ratify_check_in_5_952_2_gpu_verdicts_fname_v2_50

-- Research (Director); USER-routed
