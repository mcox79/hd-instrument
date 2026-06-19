# SKUNKWORKS (Auditor) -> Research (Director) + Testbed (Integrator): DECISION 82f PRIORITY 1 -- existence-check of 24 W-TYPE-SIG + family candidates DONE. HONEST counts: 8 GENUINELY NEW sound edges (ready for ratify), 5 already exist, 11 family->member edges are DIRECTION-QUESTIONABLE (cycle-cleanup batch 2 candidates, NOT asserted as removals). No "new edge" over-claim -- existence-checked per DECISION 78 lesson.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** DECISION 82f Priority 1 (existence-check before any new-edge claim).
**File:** data/substrate_index/skunkworks_wtypesig_new_edges_v1.jsonl (the 8 new)  **Tag:** W_TYPE_SIG_EXISTENCE_CHECK

## RESULT (24 candidates cross-checked against current substrate, both directions)
- **8 GENUINELY NEW** (neither direction exists; sound + direction-vetted) -> ready for CHTV + ratify
- **5 ALREADY EXIST** (forward edge present) -> not new (mcmc_sampling->markov_chain, astar->dijkstra, subgradient->gradient, jensen_shannon_divergence->kl_divergence, viterbi_decoding->sequence_decoding)
- **11 REVERSE present** (family->member edge exists) -> DIRECTION-QUESTIONABLE; cycle-cleanup batch 2

This contrasts honestly with the first W-TYPE-SIG round (0 new, all pre-existing). The 8 new come from the NEW operators authored in batches 3+4 -- the "new operators yield new edges" path DECISION 78 predicted. I existence-checked BEFORE claiming, per the DECISION 78 lesson; I do not repeat the 0-new over-claim.

## THE 8 GENUINELY-NEW SOUND EDGES (ready for ratify)
- variational_inference --USES--> kl_divergence   (VI minimizes KL to posterior)
- attention_mechanism --USES--> inner_product      (QK^T inner products)
- kalman_filter --USES--> bayes_rule               (recursive Bayesian estimation)
- convex_optimization --USES--> lagrange_multiplier (constrained convex opt)
- chu_liu_edmonds --SPECIALIZES--> graph_traversal  (directed-MST graph algorithm)
- prims_mst --SPECIALIZES--> graph_traversal        (greedy MST)
- context_binding --SPECIALIZES--> algebraic_binding
- tensor_product_representation --SPECIALIZES--> algebraic_binding

All direction-vetted (consumer/member -> foundational/family). For Testbed: CHTV-verify + atomic ratify with witness=W_TYPE_SIG; these are incident to operator atoms (no held-out gold; additive; preserve R3). NOTE remote/laptop substrate drift (82: laptop 5043 vs remote 4947 rel) -- ratify on laptop; sync before GPU work.

## 11 DIRECTION-QUESTIONABLE family->member edges (cycle-cleanup batch 2; NOT asserted)
The substrate has DEPENDS_ON (and USES) edges from FAMILY -> MEMBER (e.g. graph_traversal->dijkstra, sequence_decoding->forward_algorithm, algebraic_binding->role_filler_binding, discriminative_classification->count_nb, representation_transform->pca_whitening, probabilistic_inference->bayesian_inference, ...11 total). A member SPECIALIZES its family; the family does NOT DEPENDS_ON its member -> the DEPENDS_ON direction is backwards.
- CAUTION (not asserting removal): the USES direction MIGHT be a deliberate "family dispatches to members" relation; only the DEPENDS_ON is clearly backwards. I flag these for the careful cycle-cleanup workstream (capability_preservation + rollback), NOT as definite removals. My self-model families already encode the correct member->family SPECIALIZES via members_specialize lists.
- Recommend: cycle-cleanup batch 2 reviews these 11 (remove backwards family->member DEPENDS_ON; the member->family SPECIALIZES is available from the self-model family entries).

## STATUS / NEXT (per DECISION 82f sequence)
- Priority 1 (this) DONE: 8 new + 5 exist + 11 direction-questionable.
- Priority 2 NEXT: tier-re-assignment workstream (8 mis-tiered atoms; creates tier-gradient = second STRICT-growth lever).
- The 8 new edges -> Testbed ratify when sequenced; Iter 4 can then use them + W-TYPE-SIG on further new operators.

Tag: W_TYPE_SIG_EXISTENCE_CHECK_8_new_5_exist_11_direction_questionable_no_overclaim -- SKUNKWORKS (Auditor)
