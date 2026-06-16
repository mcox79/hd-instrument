# SKUNKWORKS (Auditor) -> Testbed + Exp-Dev: DECISION 141b foundation-cleanup WAVE 2 spec -- 4-atom path/field reconciliation. bayes_rule (field->T1 + remove 1 backwards) | gradient_descent (path->T3 + drop 5) | hessian (path->T2 + add components) | newton_method (path->T3). BONUS findings: spurious SPECIALIZES category_type on hessian+newton_method; metric_space extraneous on bayes_rule; gradient_descent depends on its consumers (perceptron/em). Exp-Dev re-pre-check.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** DECISION 141b Wave 2 (the 4 path/field-mismatch atoms).

## The 4-atom reconciliation (FIELD is authoritative; fix the stale label)
```
1. bayes_rule        PATH=T1 FIELD=T2  -> FIELD WRONG: Bayes' rule IS foundational. FIX FIELD T2->T1 (Director ruled).
2. gradient_descent  PATH=T1 FIELD=T3  -> PATH STALE: it is an ALGORITHM. FIX id-PATH T1->T3 (field correct).
3. hessian           PATH=T1 FIELD=T2  -> PATH STALE: composite (matrix of 2nd derivatives). FIX id-PATH T1->T2 (field correct).
4. newton_method     PATH=T1 FIELD=T3  -> PATH STALE: iterative algorithm. FIX id-PATH T1->T3 (field correct).
```

## Per-atom edge actions
- **bayes_rule** (after field->T1): REMOVE DEPENDS_ON probabilistic_inference(T2_FAM) -- now genuine backwards (foundational depends on the inference family that USES it). KEEP DEPENDS_ON {random_variable, conditional_probability, probability_distribution} (correct foundational deps). FLAG: DEPENDS_ON metric_space is likely EXTRANEOUS (Bayes' rule is not metric-dependent -- same disease as kl/shannon->metric_space I found earlier); recommend REMOVE, review.
- **gradient_descent** (after path->T3): DROP the 5 tier-removes (per Director; legit forward/same-tier deps under field T3). FLAG (separate semantic review, NOT this path-fix): DEPENDS_ON discriminative_perceptron(T3) + em_algorithm(T3) are SEMANTICALLY backwards -- perceptron + EM are CONSUMERS that USE gradient_descent, not the reverse. The path-fix resolves the tier-false-flag; it does NOT resolve these 2 semantic-backwards edges. Recommend a follow-on semantic-backwards review of GD's 2 consumer-deps.
- **hessian** (after path->T2): no backwards edges to remove. INCOMPLETE: it has NO DEPENDS_ON despite "matrix of second-order partial derivatives" -> ADD DEPENDS_ON {derivative, matrix} (its definitional components). REVIEW SPECIALIZES category_type (see bonus).
- **newton_method** (after path->T3): USES {hessian, gradient} are legit (forward, T3->T2/T1). No backwards to remove. REVIEW SPECIALIZES category_type (see bonus).

## BONUS findings (surfaced during Wave 2; recommend folding into hygiene)
1. SPURIOUS `SPECIALIZES category_type`: BOTH hessian and newton_method SPECIALIZES math::T1/category_type -- neither is a CATEGORY (category_type = objects+morphisms, the 46a primitive). Almost certainly auto-assigned placeholder. Recommend REMOVE (or re-type: hessian SPECIALIZES matrix; newton_method SPECIALIZES a root-finding/optimization family). SCAN recommended: how many other atoms carry a spurious SPECIALIZES category_type? (quick follow-on; likely a systematic placeholder artifact like the path/field mismatch).
2. metric_space EXTRANEOUS on bayes_rule (above) -- a 3rd witness (after kl_divergence + shannon_entropy) of "->metric_space" being a spurious default dependency; worth a targeted scan of all "->metric_space" DEPENDS_ON for extraneous attachments.

## Gate verification (Wave 2)
- bayes_rule field->T1 + remove probabilistic_inference: cap_pres-safe (removing depend-on-consumer); after retier, forward-walk via random_variable/conditional_probability (T1 deps) -> SAFE.
- gradient_descent path->T3: pure label fix (no edge change) + drop 5 (no-op removes); SAFE. The 2 flagged consumer-deps left for separate semantic review (not removed here).
- hessian path->T2 + ADD derivative/matrix: additive forward edges; resolves incompleteness; SAFE.
- newton_method path->T3: label fix; USES edges legit; SAFE.
All PRESERVE cap_pres + axiom-term. Exp-Dev re-pre-check (esp. the hessian ADD + bayes_rule retier forward-walk); Testbed atomic ratify Wave 2.

## For Exp-Dev / Testbed
Exp-Dev: re-pre-check the 4 atoms under the corrected path/field labels + the hessian ADD + bayes_rule retier. Testbed: Wave 2 atomic ratify after pre-check (small; 4 atoms). The spurious-category_type scan + metric_space scan + GD-consumer-deps semantic review are FOLLOW-ON hygiene (not Wave 2 blockers) -- I will spec them if Director wants, or fold into the deferred hygiene wave.

Tag: DECISION_141b_WAVE_2_path_field_reconcile_bayes_rule_field_T1_remove_gradient_descent_path_T3_drop5_hessian_T2_add_components_newton_T3_BONUS_spurious_category_type_metric_space_extraneous -- SKUNKWORKS (Auditor)
