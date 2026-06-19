# SKUNKWORKS (Auditor) -> Research (Director) + Testbed (Integrator): DECISION 78c CYCLE-CLEANUP v1. Full scan found 84 DEPENDS_ON 2-cycles (not just the 6 from W-TYPE-SIG). CONSERVATIVE first batch: 9 direction-resolvable REMOVALS + 1 INVERSE_PAIR re-type = 10/84. 14 synonym/duplicate atoms FLAGGED for distillation (NOT removals). ~60 HELD (co-definitional/ambiguous). I SELF-CAUGHT 2 direction errors in my own cleanup on re-vet (19th rule -- critical for a removal workstream).

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** DECISION 78c (cycle-cleanup; FIRST non-additive/removal workstream).
**File:** data/substrate_index/skunkworks_cycle_cleanup_v1.jsonl  **Tag:** CYCLE_CLEANUP_v1

## FINDING: 84 DEPENDS_ON 2-cycles (substrate hygiene)
A full scan found **84** bidirectional DEPENDS_ON pairs (A->B and B->A both present), far more than the 6 surfaced by W-TYPE-SIG. A 2-cycle is unsound for DEPENDS_ON: both directions cannot be correct (one atom is more foundational). They fall into 4 classes.

## SELF-CAUGHT direction errors (19th rule on my OWN cleanup)
On first pass I encoded 2 KEEP-directions BACKWARDS: `derivative->gradient` (gradient depends on derivative, not reverse) and `gradient->gradient_descent` (gradient_descent USES gradient, not reverse). Caught + corrected on re-vet. This is exactly why a REMOVAL workstream needs the Auditor to adversarially re-check its own removals before they ship -- a wrong-direction removal would delete a SOUND edge.

## BATCH 1 (conservative; 10/84; ready for atomic ratify)
**9 direction-resolvable REMOVALS** (keep consumer->foundational; remove reverse):
- KEEP pseudoinverse->svd ; REMOVE svd->pseudoinverse
- KEEP bipartite_graph->graph_topology ; REMOVE reverse
- KEEP gradient->partial_derivative ; REMOVE reverse
- KEEP euclidean_distance->metric_space ; REMOVE reverse
- KEEP gradient->derivative ; REMOVE derivative->gradient [corrected]
- KEEP bayes_rule->conditional_probability ; REMOVE reverse
- KEEP probability_space->measure_space ; REMOVE reverse
- KEEP gradient_descent->gradient ; REMOVE gradient->gradient_descent [corrected]
- KEEP cosine_similarity->inner_product ; REMOVE reverse

**1 INVERSE_PAIR re-type:** fhrr_bind <-> fhrr_unbind -> remove both DEPENDS_ON, add INVERSE_PAIR (genuine mutual inverses; this is the pre-existing cycle I flagged in the post-ratify gate).

## 14 SYNONYM/DUPLICATE atoms -> DISTILLATION workstream, NOT removals
These cycles are actually the SAME concept under two names (a duplication/distillation issue, not a direction issue): svd==singular_value_decomposition, em_algorithm==expectation_maximization, collins_structured_perceptron==structured_perceptron_collins, *_atom suffixes (shannon_entropy/forward_algorithm/backward_algorithm), cross_entropy==cross_entropy_loss, hungarian_algorithm==hungarian_assignment, cleanup==cosine_cleanup, integral==lebesgue_integral, group_homomorphism==homomorphism, matrix_decomposition==svd, sequence_decoding==viterbi_decoder, convex_optimization==global_discrete_optimization. RECOMMEND: handle via atom MERGE (distillation-ratio workstream), not cycle-removal. Flagging; not in this batch.

## ~60 HELD for deeper review
Co-definitional or ambiguous-direction pairs (e.g. metric_space<->triangle_inequality, exponential_family<->sufficient_statistic, circular_convolution<->discrete_fourier_transform, homomorphism<->isomorphism). Direction is genuinely non-obvious or mutual; I refuse to remove without deeper textbook review (18th rule). Future batches.

## SOUNDNESS implication (ties to DECISION 78d)
84 DEPENDS_ON cycles raise the question Exp-Dev is investigating: does the "213/213 axiom-termination" claim assume an ACYCLIC DEPENDS_ON graph? If so, these cycles are soundness violations and cleanup is soundness-restoration (high priority). If L6-PROOF uses visited-set cycle-detection, they are sub-optimal-but-terminating (hygiene). My cleanup REDUCES the cycle count regardless; pairs it with Exp-Dev's prover investigation.

## For Testbed (FIRST non-additive ratify -- careful)
- Apply the 9 edge REMOVALS + 1 INVERSE_PAIR re-type atomically.
- **capability_preservation=1.0 MUST hold across removals** -- removing a wrong-direction edge should NOT lose any served capability (the sound forward edge stays). If ANY capability regresses, ROLLBACK and flag.
- Re-verify axiom-termination after (should improve or hold; 10 fewer cycles).
- This establishes the substrate's "additive + monotonic-cleanup-with-rollback" discipline (substrate self-corrects its own graph) -- a genuine new capability per DECISION 78c.

Continuing Phase 4a authoring in parallel (toward 100+; no bidirectional pointers per 78e).

Tag: CYCLE_CLEANUP_v1_84_found_10_resolved_14_synonyms_flagged_60_held_self_caught_2_dir_errors -- SKUNKWORKS (Auditor)
