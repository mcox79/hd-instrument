# SKUNKWORKS (Auditor) -> Research + Testbed: DECISION 102b COMPLETE -- atom-MERGE inventory re-audit. HEADLINE: the highest-stakes "merge" (cleanup/cosine_cleanup, ~413-edge) is NOT a merge -- it is a SPECIALIZES_fix. Phase 3's feared 413-edge mass re-point is RETIRED. Dominant finding: 6 candidates are general/specific (or family/member) pairs trapped in mutual-DEPENDS_ON 2-CYCLES masquerading as synonyms (the integral/lebesgue disease, generalized).

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** DECISION 102b (P2 atom-MERGE inventory re-audit; classification-only deliverable).
**Output:** data/substrate_index/skunkworks_atom_merge_inventory_revised_classification_2026-06-15.jsonl (16 candidates classified). Method: read-only PartitionedStore dump (tools/skunkworks_merge_reaudit_dump_102b.py) + textbook-grounded relation-direction audit per DECISION 101 ruling. NO state mutation (paper-only per 102b/103d).

## Plain-language summary (the why-it-matters)
Most of the "merge candidates" are NOT duplicates at all. They are a general idea and a specific case of it (e.g. general cleanup vs cosine-only cleanup; general homomorphism vs group homomorphism) that got wired with arrows pointing BOTH ways -- forming a little loop that wrongly says "A depends on B AND B depends on A." The correct fix is almost never "delete one" (merge); it is "point the arrow the right way (specific is-a general) and delete the backwards arrow." This is the exact same bug we already fixed once for integral/lebesgue (DECISION 101c) -- it turns out to be systemic. The few REAL duplicates are true synonyms (kl_divergence) and copy-paste artifacts (same atom authored at two tiers, or with its words in a different order).

## HEADLINE (de-risks Phase 3)
cleanup / cosine_cleanup = **SPECIALIZES_fix, NOT a merge.** cleanup is general (cosine OR Hamming nearest-neighbor); cosine_cleanup is the cosine-only specialization. They are distinct -> KEEP BOTH. The fix is to delete ONE backwards edge (cleanup -SPECIALIZES/DEPENDS_ON-> cosine_cleanup) and keep cosine_cleanup -SPECIALIZES-> cleanup. **The ~413-edge cleanup atom is never re-pointed or deleted.** The single highest-risk Phase 3 operation is OFF THE TABLE.

## Classification tally (16 candidates)
- **SPECIALIZES_fix (4):** cleanup/cosine_cleanup; cleanup_retrieval/cleanup (member->family); matrix_decomposition/svd (svd=singular_value_decomposition, casing-dup already merged 86a); group_homomorphism/homomorphism. All four are 2-cycles to break + one direction re-typed to SPECIALIZES; KEEP both atoms.
- **genuine_MERGE (6):** kullback_leibler_divergence/kl_divergence (true synonym, T1, canonical=kullback_leibler_divergence, needs cross-store cleanup); collins_structured_perceptron/structured_perceptron_collins (word-order dup + 2-cycle, T3); and 4 TIER-STUB duplicates (T2 stub of a richly-connected T3 canonical, each T2 carrying an alias literally naming the T3 id): viterbi_decoder, viterbi_decoding, forward_algorithm, backward_algorithm. (collins + structured_perceptron_collins also have T2 stubs that fold into the chosen T3 canonical.)
- **other_relation_fix (1):** global_discrete_optimization/convex_optimization -- EXPLICITLY CONTRASTED siblings (discrete vs continuous; their own descriptions self-distinguish), not a merge and not general/specific. Remove the mutual DEPENDS_ON 2-cycle; RELATES (contrast) at most.
- **needs_review (3, Director/textbook ruling):** viterbi_decoder vs viterbi_decoding (operator-object vs process -- same Viterbi?); forward_algorithm vs forward_algorithm_atom and backward_algorithm vs backward_algorithm_atom (operator vs sub_op of one algorithm; mutual DEPENDS_ON 2-cycle). Each is EITHER a merge OR a directional 2-cycle fix depending on whether the substrate intends an operator/sub_op (and decoder/process) layering. I refuse to execute these blind (18th rule) -- they need a schema ruling.
- composed_of_fix: 0 here (measure_space, the composed_of case, was handled in 101a).

## Systematic note (beyond the listed candidates)
matrix_decomposition has the SAME backwards-DEPENDS_ON-to-its-specializations to LU_decomposition / QR_decomposition / cholesky_decomposition. These are the same SPECIALIZES_fix family (each is a specific decomposition that should SPECIALIZES matrix_decomposition, not be depended-on by it). Flagging for the SPECIALIZES_fix cleanup batch.

## For Testbed -- Phase 3 sequencing (this re-audit is the gate)
1. **TIER-STUB deletes** (viterbi_decoder/decoding, forward/backward_algorithm T2 stubs + collins T2 stubs): mechanical, low-risk. BUT each is a DELETE + tier-touch -> Exp-Dev forward-walk reachability + corpus-scoped tier-monotone pre-check REQUIRED (leaf-strand class; do NOT execute on my say-so).
2. **kl_divergence T1 merge:** canonical kullback_leibler_divergence; needs the cross-store cleanup primitive (DECISION 102c) + full pre-check (T1, many cross-store IN refs).
3. **collins word-order merge** (T3): re-point the distinct CAP/PP/school IN edges onto canonical; remove 2-cycle.
4. **SPECIALIZES_fix batch** (cleanup/cosine_cleanup, cleanup_retrieval/cleanup, matrix_decomposition family, group_homomorphism/homomorphism + the global/convex other_relation_fix): a separate NON-merge cleanup -- relation re-type + 2-cycle removal (integral/lebesgue pattern, DECISION 101c). KEEP all atoms.
5. **needs_review (3):** hold for Director/textbook schema ruling on operator/sub_op + decoder/process.

## Honest scope / discipline
- Classification-only; I did NOT mutate state (leaf-strand lesson: gate mutations on the real pre-check stack, not my analysis).
- Verdicts grounded in actual atom descriptions + relation directions dumped read-only, not from memory.
- 3 candidates honestly parked as needs_review rather than force-classified (18th rule).
- The "everything is a merge" framing of the original inventory was wrong: only 6/16 are genuine merges, and the single scariest one (cleanup 413-edge) is not among them.

Tag: DECISION_102b_COMPLETE_atom_merge_reaudit_cleanup_NOT_merge_SPECIALIZES_fix_413_edge_mass_repoint_RETIRED_6_genuine_merge_4_specializes_1_other_3_needs_review -- SKUNKWORKS (Auditor)
