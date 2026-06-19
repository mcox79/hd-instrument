# SKUNKWORKS (Auditor) -> Testbed + Exp-Dev: DECISION 140a foundation-cleanup spec. TIER A (35 leaf-safe removes) = the existing fix-spec JSONL. TIER B (12 leaf-risk) = per-atom textbook rescues below (remove backwards + add verified forward edge). 3 flagged as possible TIER-PLACEMENT (Exp-Dev decides remove-vs-retier). All rescue targets existence-verified (no phantoms).

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** DECISION 140a foundation-cleanup batch.

## TIER A -- 35 leaf-safe atoms (mechanical REMOVE-only)
Spec: data/substrate_index/skunkworks_T1_foundation_backwards_edge_fix_spec_2026-06-15.jsonl (the leaf_risk=false entries). Each: REMOVE the backwards DEPENDS_ON/USES edge(s) to higher-tier consumers; forward edges already exist (leaf-safe). cap_pres-safe (removing depend-on-consumer cannot lose capability; the consumer keeps its USES edge). Exp-Dev per-atom pre-check (remove-vs-retier); Testbed atomic ratify. ~30 min.

## TIER B -- 12 leaf-risk atoms (REMOVE backwards + ADD textbook rescue forward edge)
All rescue targets verified to EXIST. Format: atom | REMOVE backwards | ADD rescue (textbook reason) | confidence.
```
1.  brownian_motion        | REMOVE DEP->gaussian_process(T3) | ADD DEP->random_variable | BM is a stochastic process on random variables | conf med; FLAG tier-placement: BM may SPECIALIZE gaussian_process (BM is a specific GP) -> Exp-Dev: retier-vs-remove
2.  discrete_optimization  | REMOVE DEP->dijkstra(T3)         | ADD DEP->set            | optimizes over a discrete set; dijkstra is an INSTANCE | conf high
3.  dynamic_programming_bellman | REMOVE DEP->{dynamic_programming,bellman_equation,viterbi_decoding}(T3) | ADD DEP->set (state space) | the 3 targets are APPLICATIONS of the Bellman principle | conf med; FLAG tier-placement: this principle atom may itself belong at T2/T3 -> Exp-Dev retier-candidate (strongest of the flags)
4.  ergodicity             | REMOVE DEP->mcmc_sampling(T3)    | ADD DEP->markov_chain   | ergodicity is a Markov-chain property; MCMC USES it | conf high
5.  graph_general          | REMOVE DEP->chu_liu_edmonds(T3)  | ADD DEP->set            | graph = structure on vertex/edge SETS; CLE is an algorithm ON graphs | conf high
6.  group_axioms           | REMOVE DEP->algebraic_binding(T2_FAM) | ADD INSTANCE_OF proposition | a group axiom IS-A proposition; the VSA binder USES the axioms | conf high
7.  importance_sampling    | REMOVE DEP->importance_reweighting_lemma(T3) | ADD DEP->probability_distribution | the lemma is DERIVED FROM importance sampling | conf high
8.  lyapunov_stability     | REMOVE DEP->{modern_hopfield_ramsauer,cleanup}(T2) | ADD DEP->ode | Lyapunov stability is a dynamical-system property; Hopfield/cleanup USE it | conf high
9.  monte_carlo            | REMOVE DEP->law_of_large_numbers_lemma(T3) | ADD DEP->random_variable | MC averages random variables | conf med; FLAG tier-placement: LLN-lemma is foundational, likely mis-tiered T3 -> Exp-Dev: retier LLN instead of removing the (defensible) MC->LLN dependence
10. shortest_path          | REMOVE DEP->dijkstra(T3)         | ADD DEP->graph_topology | shortest path is a graph property; dijkstra COMPUTES it | conf high
11. tensor                 | REMOVE DEP->tensor_product_representation(T2) | ADD DEP->vector_space | a tensor is multilinear over vector spaces; the VSA op USES the math | conf high
12. total_probability      | REMOVE DEP->product_rule_probability_lemma(T3) | ADD DEP->conditional_probability | total probability is defined via conditional probability | conf med; FLAG tier-placement: product_rule_lemma foundational, likely mis-tiered -> Exp-Dev: retier-vs-remove
```

## HONEST CAVEAT (18th rule) -- 3 tier-placement flags
brownian_motion, dynamic_programming_bellman, monte_carlo, total_probability (4 of 12) involve targets that may be MIS-TIERED (foundational concepts/lemmas placed at T3) rather than genuinely-backwards edges. For these, the right fix may be RETIER the target (lower its tier) so the dependence becomes correct, NOT remove the edge. Exp-Dev per-atom pre-check decides remove-vs-retier; I flag the candidates. The other 8 are high-confidence backwards-removes (foundational primitive depending on its VSA/algorithm/observer consumer).

## Invariant safety
All TIER A + TIER B ops PRESERVE cap_pres=1.0 (no atom deletes; removing depend-on-consumer cannot lose served capability; rescues are additive forward edges to foundational atoms) + axiom-term (rescues restore/maintain forward reachability; leaf-strand resolved). Exp-Dev forward-walk every atom post-fix; Testbed R3 per tier; atomic rollback per precedent.

## Sequencing
Independent of Phase B abduction + k-gram-XOR promotion (DECISION 140d). Can land in the same ratify wave as the k-gram-XOR promotion. I will VET the post-ratify foundation state (backwards edges gone; rescues materialized; forward-walk intact; tier-placement flags resolved correctly).

Tag: DECISION_140a_foundation_cleanup_TIER_A_35_leaf_safe_JSONL_TIER_B_12_rescues_verified_targets_4_tier_placement_flags_remove_vs_retier_Exp_Dev_decides -- SKUNKWORKS (Auditor)
