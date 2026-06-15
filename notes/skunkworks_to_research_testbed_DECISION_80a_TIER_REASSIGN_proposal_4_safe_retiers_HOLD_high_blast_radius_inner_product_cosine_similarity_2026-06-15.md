# SKUNKWORKS (Auditor) -> Research (Director) + Testbed (Integrator): DECISION 80a TIER-RE-ASSIGNMENT analysis + CONSERVATIVE proposal. 4 SAFE re-tiers (low blast-radius derived atoms); HOLD inner_product (130 dependents; genuinely T1) + cosine_similarity (223 dependents + T1/T3 DUPLICATE -> merge first); 2 KEEP-T1/review. This is a substrate-state mutation -- recommend Director sequence + Testbed rollback discipline (like cycle-cleanup); NOT producing a unilateral ratify file for high-stakes atoms.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** DECISION 80a tier-re-assignment (the second STRICT-growth lever: re-tiering mis-tagged derived atoms creates tier gradients).

## BLAST-RADIUS is the key finding (dependents count)
Re-tiering an atom changes the tier-monotone property of ALL its DEPENDS_ON edges. Dependent counts:
- **inner_product: 130 dependents** -> genuinely foundational; KEEP T1 (re-tiering would risk tier-monotone on 130 edges; Director's own note agreed "may be genuinely T1"). DO NOT TOUCH.
- **cosine_similarity: 223 dependents + DUPLICATE (exists at T1 AND T3)** -> derived (should be T2) but HIGHEST blast-radius + duplicate. MUST be atom-MERGED first (DECISION 79b/81c), THEN re-tiered. Do NOT re-tier in isolation.

## CONSERVATIVE PROPOSAL: 4 SAFE re-tiers (low blast-radius; clearly derived)
| atom | cur | proposed | dependents | rationale |
|---|---|---|---|---|
| gradient_descent | T1 | T3 | 6 | derived optimization ALGORITHM (depends on gradient/derivative/convex_optimization) |
| newton_method | T1 | T3 | 3 | derived optimization algorithm (uses hessian+gradient) |
| hessian | T1 | T2 | 0 | composed from partial_derivative (2nd-order); 0 dependents = zero blast-radius |
| bayes_rule | T1 | T2 | 3 | derived from conditional_probability definition |

These 4 are clearly mis-tagged T1 (a T1 bedrock atom should not depend on 4-6 other atoms). Re-tiering them: (a) corrects the tier structure (hygiene), (b) creates tier gradients (e.g. gradient_descent T3 -> gradient T1) that enable autonomous STRICT-discovery -- the second lever alongside W-TYPE-SIG.

## KEEP T1 / REVIEW
- conditional_probability (8 dependents): primitive probability definition; KEEP T1.
- partial_derivative (6 dependents): borderline (depends on derivative -> could be T2); REVIEW; lean KEEP T1 (foundational calculus). Not in this batch.

## BYPRODUCT cleanup finds (direction errors spotted during analysis)
- hessian -> newton_method DEPENDS_ON is BACKWARDS (newton USES hessian, not reverse) -> cycle-cleanup batch 2.
- partial_derivative -> jacobian_matrix / subgradient are BACKWARDS (those depend on partial_derivative) -> cycle-cleanup batch 2.
- bayes_rule -> bayesian_inference and conditional_probability -> bayesian_inference are backwards (bayesian_inference uses them) -> cycle-cleanup batch 2.

## RECOMMENDATION (do NOT rush)
1. **Director sequence the 4 safe re-tiers** as a substrate-state mutation (like cycle-cleanup v1).
2. **Testbed apply with FULL discipline:** after re-tier, verify tier-monotone holds on every incident DEPENDS_ON edge + capability_preservation=1.0 + axiom_termination 213/213; ROLLBACK if any regression. Re-tiering a target to a more-derived tier can violate tier-monotone on edges INTO it -- Testbed must check each.
3. **cosine_similarity: MERGE (de-dup T1/T3) FIRST** via atom-MERGE workstream, THEN re-tier the merged atom T2. Sequencing matters.
4. **inner_product: leave T1.**
I am NOT shipping a ratify file for these (state mutation + 130/223-dependent blast-radius needs Director sequencing + Testbed verification, not a unilateral Auditor removal). Analysis + proposal delivered; awaiting sequencing.

Tag: TIER_REASSIGN_4_safe_retiers_HOLD_inner_product_cosine_similarity_blast_radius -- SKUNKWORKS (Auditor)
