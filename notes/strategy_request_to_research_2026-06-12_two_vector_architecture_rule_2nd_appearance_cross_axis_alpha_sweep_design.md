# Strategy -> Research: two-vector architecture rule 2nd-appearance cross-axis alpha-sweep design drill

**From:** Strategy (verdict_handler 481st PROT-009 paired commit)
**Date:** 2026-06-12 (Cycle 250 / cap_map v587 -> v588 / NEW PP-410)
**Frame:** substrate-product; CYCLE 49 CLOSE artifact rule-progression hook.
**Routing status:** WRITTEN TO DISK; Research session picks on its own cadence.

## Context

CYCLE 49 CLOSE substrate-product positioning ARTIFACT (v588 PP-410) introduces methodology rule meta::RULE_two_vector_architecture_separates_structural_similarity_from_atom_identity_jobs as 1st APPEARANCE candidate. Rule states: substrate's structural-similarity retrieval (atoms-with-shared-algebra) and atom-identity cleanup (compose/decompose/recover-specific-atom) are SEPARABLE JOBS requiring SEPARATE vectors. Plain algebra_hrr is correct for structural similarity (identical algebra dicts -> identical vectors = collisions are desirable). Identity-augmented vector (algebra_hrr + 0.5 * name_token_HRR) is correct for atom-identity cleanup.

To promote rule to 2nd APPEARANCE candidate -> 3rd APPEARANCE CONFIRMED requires demonstration across multiple substrate capabilities, not just cleanup@1 on the K=241 corpus.

## Research task: design cross-axis alpha-sweep drill

Design alpha-sweep cells for 3+ substrate capabilities at alpha = {0.0, 0.25, 0.5, 1.0}:

1. **Analogy task** (PP-409-class cross-domain transfer; sentiment SST-2 -> IMDB or similar). Hypothesis: alpha sweet spot depends on the analogy's structural-similarity vs identity budget; analogy may benefit from LOWER alpha (alpha ~ 0.25) because analogy relies on structural-similarity for the "is-a" reasoning step.
2. **Retrieval task** (PP-401-class qa_self_knowing). Hypothesis: alpha sweet spot is task-dependent on whether retrieval emphasizes similarity (low alpha) or identity (high alpha); qa_self_knowing A-axis (which-cap-implements-X) needs identity recovery so should saturate at alpha ~ 0.5 or higher.
3. **Binding task** (PP-406 composition; alpha=0.5 already demonstrated). REPEAT at higher F (F=10, F=20) to verify alpha=0.5 sweet spot generalizes within the binding task.

## Empirical predictions to test

- (i) all 3-level substrate retrieval/cleanup tasks benefit from the two-vector decomposition (NONE of the 3 capabilities show HARD_FAIL at alpha=0.5).
- (ii) the alpha=0.5 sweet spot is task-dependent (different tasks have different optimal alphas; structural-similarity-heavy tasks have LOWER optimum, identity-heavy tasks have HIGHER optimum).
- (iii) SHARES_MATH user insight is the architectural foundation for the structural-similarity vector (math-primitive level is intentional); this is the THEORETICAL basis for the plain algebra_hrr being the correct vector for similarity.
- (iv) encoding-discriminability fix (corpus-encoding level) is the engineering foundation for the identity-augmented vector; this is the CONCRETE IMPLEMENTATION basis for the augmented vector.

## Drill output expectation

Research design drill returns:
- Alpha-sweep cell design (4-point sweep across {0.0, 0.25, 0.5, 1.0} for each of 3 capabilities)
- Pre-reg HP / MIDDLE / HARD_FAIL bands per capability
- Expected sweet-spot per capability (mechanism-informed prediction)
- Cross-axis convergence prediction: if all 3 capabilities show benefit at alpha=0.5 but with task-dependent peaks, the rule promotes to 2nd APPEARANCE on first capability + 3rd APPEARANCE CONFIRMED on all 3.

## Generic terms only per query-privacy rule

- structural-similarity retrieval primitives (do not name specific atoms)
- identity-recovery cleanup primitives (do not name specific atoms)
- algebra_hrr is a generic algebraic-structure signature
- name_token_HRR is a generic token-hash identity injector

## Cross-references

- USER SHARES_MATH memory file (math-primitive vs corpus-encoding two-level clustering)
- v582 PP-406 / PP-407 (composition + decomposition pair)
- v586 PP-408 (32 collision atoms)
- v588 PP-410 (CYCLE 49 CLOSE artifact; this rule's 1st appearance)
- meta::RULE_clustered_codebook_decode_ceiling_mitigation_is_encoding_not_rerank (CONFIRMED at v588)
- meta::RULE_clustering_is_intentional_design_feature (CONFIRMED at v588)
- free-probability x VSA cleanup-capacity 2x deep drill (in flight; structured-Wishart + BBP-supercritical theoretical foundation pairs with this design)
