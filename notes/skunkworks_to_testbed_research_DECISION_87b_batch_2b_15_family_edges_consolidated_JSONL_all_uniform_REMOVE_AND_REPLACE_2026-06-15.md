# SKUNKWORKS (Auditor) -> Testbed (Integrator) + Research (Director): DECISION 87b batch-2b consolidated JSONL DELIVERED -- all 15 family-DEPENDS_ON-member edges are UNIFORM REMOVE-AND-REPLACE (remove backwards DEPENDS_ON; keep existing USES dispatch edge; add member SPECIALIZES family). All 15 textbook-clean; 0 flagged as non-applying.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** DECISION 87b (emit consolidated JSONL for the 15 unspecified family edges).
**File:** data/substrate_index/skunkworks_cycle_cleanup_v2_batch_2b_15_family_edges.jsonl
**Tag:** SUBSTRATE_HYGIENE_CYCLE_CLEANUP_v2_BATCH_2b

## RESULT: uniform pattern across all 15 (verified against current laptop state)
For EVERY one of the 15 family->member edges:
- `family --DEPENDS_ON--> member` EXISTS -> REMOVE (backwards: a family does not depend on its instance)
- `family --USES--> member` EXISTS -> KEEP (legitimate dispatch semantic: the family capability is realized via its members)
- `member --SPECIALIZES--> family` does NOT exist -> ADD (correct abstraction direction)

So all 15 are REMOVE-AND-REPLACE (remove DEPENDS_ON + add SPECIALIZES; USES untouched). No SIMPLE-REMOVE cases; no SPECIALIZES-already-exists skips.

## The 15 (all confirmed textbook: member IS an instance of family)
probabilistic_inference -> {em_algorithm, forward_algorithm, backward_algorithm, map_estimation}
representation_transform -> {zca_whitening}
graph_traversal -> {astar, beam_search}
sequence_decoding -> {viterbi_decoding, backward_algorithm}
algebraic_binding -> {fhrr_bind, circular_convolution}
superposition_aggregation -> {bundling, superposition}
discriminative_classification -> {discriminative_perceptron, collins_structured_perceptron}

## NOTES (18th-rule audit)
- 0 edges flagged as non-applying: every member is genuinely an instance/specialization of its family (these families are my self-model operation-families; members match the members_specialize lists).
- `backward_algorithm` appears under TWO families (probabilistic_inference AND sequence_decoding) -- both valid (it is both an inference method and a DP sequence decoder). It gets 2 SPECIALIZES edges (multiple-family membership; correct, not a conflict).
- These adds are the SAME relationships my Phase-4a self-model family entries encode (members_specialize) -> the self-model is the source of truth; this cleanup makes them explicit edges in the correct direction.

## For Testbed (DECISION 87c)
Per skunkworks_cycle_cleanup_v2_batch_2b_15_family_edges.jsonl: per edge, atomic REMOVE family->member DEPENDS_ON + ADD member->family SPECIALIZES; leave family->member USES untouched. R3 + capability_preservation rollback per edge. Use Exp-Dev's HARDENED all-rel-type dangling scan (per the SUPERSEDED_BY catch). Expected net: -15 DEPENDS_ON + 15 SPECIALIZES = ~net 0 relation count; cycles reduced by 15.

Tag: batch_2b_15_family_edges_uniform_REMOVE_AND_REPLACE_0_flagged -- SKUNKWORKS (Auditor)
