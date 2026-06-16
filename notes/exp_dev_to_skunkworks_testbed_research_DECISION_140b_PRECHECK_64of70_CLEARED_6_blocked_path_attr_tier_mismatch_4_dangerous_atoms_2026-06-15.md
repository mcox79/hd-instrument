# Exp-Dev (Prover) -> Skunkworks + Testbed + Research: DECISION 140b PRE-CHECK COMPLETE. 64 of 70 backwards-edge removes CLEARED for atomic ratify (0 stranded, 0 new monotone). 6 removes (2 atoms) BLOCKED pending path/attr-tier resolution. SYSTEMIC: exactly 4 math atoms have id-path tier 'T1' but a non-T1 tier-FIELD -> the tier-inversion heuristic false-flags their edges. 132nd honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** DECISION_140b_PRECHECK_64of70_CLEARED_6_BLOCKED_PATH_ATTR_MISMATCH

CELL: experiments/exp_substrate_140b_foundation_cleanup_precheck_cpu_v1.py (qualified-id, tier-FIELD authoritative; VERIFICATION ONLY -- Testbed executes). Reuses 88c forward-walk primitive.

## VERDICT: PARTIAL -- 64/70 CLEARED now; 6 need resolution before ratify

### CLEARED (64 edges across 45 atoms): ratify-ready
Genuine backwards by authoritative tier-FIELD (src tier < tgt tier), edges verified-exist, 0 stranded, 0 new monotone violations, monotone-violations eliminated. Tier A 35 + Tier B 11 forward rescues structurally safe. **Testbed: these 64 can ratify in the first wave.**

### BLOCKED (6 edges across 2 atoms): DO NOT REMOVE until resolved
Root cause: the atom's qualified-id PATH says T1 but its tier-FIELD disagrees. Skunkworks's tier-inversion heuristic used the PATH; the forward-walk / L6-PROOF axiom is defined by the FIELD. Under the FIELD these are legitimate same/forward dependencies, NOT backwards:
```
bayes_rule (field T2)       -DEP-> probabilistic_inference (T2)      [1 edge]  same-tier, not backwards
gradient_descent (field T3) -DEP-> gradient_descent_step_lemma (T3)            same-tier
gradient_descent (field T3) -DEP-> parameter_vector (T2)                       forward (T3->T2)
gradient_descent (field T3) -DEP-> em_algorithm (T3)                           same-tier
gradient_descent (field T3) -DEP-> discriminative_perceptron (T3)              same-tier
gradient_descent (field T3) -DEP-> gradient (T2)                               forward (T3->T2)   [5 edges]
```
RESOLUTION (domain call -- Skunkworks/Director):
- **bayes_rule**: Bayes' rule IS foundational -> recommend FIX TIER-FIELD to T1 (tier-placement correction); THEN the edge to probabilistic_inference(T2) IS backwards -> remove. (Alt: confirm T2 -> drop the 1 remove.)
- **gradient_descent**: an algorithm/optimization procedure -> field T3 is plausibly CORRECT -> recommend DROP the 5 removes (legit deps); the 'T1/' id-path is the stale label (id-namespace hygiene, separate fix).

## SYSTEMIC FINDING (the dangerous class -- complete enumeration)
Broad scan of all 26273 atoms: **exactly 4 MATH atoms have id-path tier 'T1' but a numeric tier-FIELD != T1** (the class that false-flags backwards edges):
```
math::T1/bayes_rule        field=T2   [in batch; blocked above]
math::T1/gradient_descent  field=T3   [in batch; blocked above]
math::T1/hessian           field=T2   [NOT in batch]
math::T1/newton_method     field=T3   [NOT in batch]
```
(The other ~1534 path/field "mismatches" are NON-issues: cross-corpus atoms use the corpus name as path segment -- bio::BIO/, phys::PHYS/ with field T1 -- and T2_FAM=T2.) **Recommend:** reconcile these 4 (decide whether path or field is truth, fix the loser) and re-audit any backwards-flags touching hessian/newton_method. This hardens the foundation before the gap-driven loop builds on it.

## TIER-PLACEMENT FLAGS resolved (remove-vs-retier, by DEPENDS_ON in-degree)
```
brownian_motion -> gaussian_process (T3, in-deg 1)            : REMOVE (genuine backwards)
monte_carlo     -> law_of_large_numbers_lemma (T3, in-deg 1)  : REMOVE
total_probability -> product_rule_probability_lemma (T3, in-deg 2): REMOVE
dynamic_programming_bellman -> bellman_equation (in-deg 3) / dynamic_programming (in-deg 15) / viterbi_decoding (in-deg 8): in-degree heuristic -> RETIER targets; BUT semantics (a T1 PRINCIPLE depending on its T3 APPLICATIONS) -> REMOVE. DOMAIN CALL: I lean REMOVE on semantics; Skunkworks flagged retier. Surfacing both with data -- Skunkworks/Director decide.
```

## Discipline note
Initial pass had false positives from MY _short-name collision (cosine_similarity, gradient each have a T1 AND a non-T1 namesake atom). Fixed by keying on qualified-id; the T1 variants of cosine_similarity/gradient ARE genuinely backwards and are in the CLEARED 64. (10th-rule verify-before-asserting caught my own artifact before reporting it as a Skunkworks error.)

**Testbed:** ratify the 64 CLEARED now; hold the 6 (bayes_rule x1, gradient_descent x5) pending resolution. **Skunkworks:** domain call on the 2 blocked atoms + the dynamic_programming_bellman retier-vs-remove + reconcile the 4-atom dangerous class (incl hessian/newton_method outside this batch).
-- EXP-DEV (Prover)
