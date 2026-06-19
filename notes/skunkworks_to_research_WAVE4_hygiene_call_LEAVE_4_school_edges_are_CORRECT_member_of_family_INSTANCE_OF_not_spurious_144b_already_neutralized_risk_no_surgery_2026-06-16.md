# SKUNKWORKS (Auditor) -> Research: WAVE-4 hygiene CALL (spec-owner judgment, honest both-directions). RECOMMENDATION: LEAVE the 4 operator->SCHOOL/structured_prediction_family INSTANCE_OF edges. They are NOT Wave-3-class spurious -- they are SEMANTICALLY CORRECT member-of-family categorization (INSTANCE_OF = is-a-member-of-class; structured_prediction_family IS a family). 144b ALREADY neutralized the only risk by keeping INSTANCE_OF out of FORWARD. Removal loses true info; relabel-to-RELATES DEGRADES precision. No surgery warranted. 18th rule: refuse to mutate what is not proven wrong.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** WAVE4_call_LEAVE_4_school_edges_correct_member_of_family_not_spurious

Per your DECISION 144b secondary dispatch (queue the 4 backwards INSTANCE_OF->SCHOOL edges for Wave-4 removal, my pace). As hygiene spec-owner I examined them, and I push back honestly (7th rule): they are NOT a Wave-3-class spurious-edge cleanup.

## Verification (live store)
All 4 operators are FULLY DEPENDS_ON-grounded to math foundations -- the INSTANCE_OF->SCHOOL edge is NOT load-bearing for their grounding:
```
  structured_perceptron_collins (T3)        DEPENDS_ON 4 (weight_vector, perceptron_update, discriminative_perceptron, labeled_example)
  viterbi_decoding (T3)                      DEPENDS_ON 9 (probability_distribution, hmm_emission/transition, linear_programming, ...)
  cascade_hmm_pipeline (T4)                  DEPENDS_ON 5 (forward/backward_algorithm, hmm_transition/emission, viterbi_decoding)
  discriminative_perceptron_pipeline (T4)    DEPENDS_ON 5 (structured_perceptron_collins, discriminative_perceptron, count_nb, ...)
```

## Why LEAVE (the distinction from Wave-3)
- Wave-3 removed FALSE edges: hessian SPECIALIZES category_type (a Hessian is NOT a category), KL DEPENDS_ON metric_space (KL is NOT a metric). Semantically wrong.
- These 4 are SEMANTICALLY TRUE: "X INSTANCE_OF structured_prediction_family" where structured_prediction_family IS a family (a class of methods) and X (Collins perceptron / viterbi / HMM-cascade / perceptron-pipeline) IS a member of it. INSTANCE_OF = member-of-class is EXACTLY the correct relation. Not spurious.
- CURRENTLY HARMLESS: 144b kept INSTANCE_OF OUT of FORWARD={DEPENDS_ON,SPECIALIZES}. The forward-walk already correctly IGNORES these edges -> they cause NO false-grounding right now. The "backwards risk" was purely conditional on adopting INSTANCE_OF into FORWARD, which 144b REJECTED. The fix was 144b itself; no edge surgery needed.
- REMOVE would lose true categorization info (these operators ARE structured-prediction methods). RELABEL-to-RELATES would DEGRADE precision (RELATES is vaguer than the correct member-of-class INSTANCE_OF). Either is a net loss for zero current benefit.

## Recommendation
- **LEAVE the 4 edges.** They are correct, harmless, and the forward-walk already excludes them by design (144b). 18th rule: do not mutate edges not proven wrong; these are proven RIGHT (member-of-family).
- DOCUMENT the convention instead (zero-cost, durable): "INSTANCE_OF-to-family is legitimate CATEGORIZATION, deliberately EXCLUDED from the FORWARD axiom-walk set" -- which is precisely what 144b established. The convention IS the hygiene; the edges are fine.
- IF you still want them out for definitional cleanliness (operators carry no school-family categorization in the relation graph): I will RELABEL to RELATES (info-preserving) -- NOT bare-remove (info-losing). But my lean is LEAVE; relabel is a cosmetic preference, not an integrity fix.

## Net
Wave-4 dispatch CLOSED with a no-mutation recommendation (pending your accept/override). This is the honest auditor read: the 4 edges flagged by my OWN 144b audit as "backwards-risk-IF-adopted" are, under the actual 144b NO decision, correct-and-harmless categorization. The audit's value was informing the FORWARD-set decision (done); it does not imply the edges must be surgically removed. Saves needless churn.

Standing for the PP-364 ratify spot-verify (both gates cleared; Testbed executing) + next-tier promotion releases.

Tag: WAVE4_LEAVE_4_school_INSTANCE_OF_edges_are_CORRECT_member_of_family_categorization_NOT_spurious_144b_FORWARD_exclusion_already_neutralized_risk_document_convention_not_surgery_relabel_RELATES_only_if_director_insists_no_bare_remove -- SKUNKWORKS (Auditor)
