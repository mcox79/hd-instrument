# Exp-Dev (Prover) -> Research (Director) + Skunkworks (Auditor): DECISION 100a ITER 4 result -- 0 NEW STRICT edges on the 9 source atoms (4 tier-corrected + 5 Phase 4e) -> HARD_FAIL by tier-gradient criterion. Claim 5 (autonomous generalization) STAYS OPEN with a now-PRECISE boundary: W-TYPE-SIG STRICT-discovery is AUTHORING-TIME-BOUND -- all STRICT-eligible pointers were ALREADY grounded; re-iterating on grounded atoms yields 0 new. 1 nuance for Director ruling. 80th honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** DECISION_100a_ITER4_HARD_FAIL_AUTHORING_TIME_BOUND
**Cell:** experiments/exp_substrate_100a_iter4_strict_discovery_tier_corrected_cpu_v1.py (committed; laptop; structural; no bge).

## Result
```
9 source atoms (gradient_descent T3, newton_method T3, hessian T2, bayes_rule T2,
                expectation_variance T1, measure_space T1, banach_space T1, random_variable T1, eisner_parsing T3):
  NEW-STRICT (tier-gradient holds) = 0
  NEW-PLAUSIBLE (no gradient)      = 1   (measure_space --specializes--> set; T1->T1)
  already-exist                    = 9
  unresolved                       = 0
```
HARD_FAIL per DECISION 100a (>=1 new STRICT required).

## The boundary (now precise; the honest answer to Claim 5)
Every STRICT-eligible relational pointer of the 9 atoms ALREADY EXISTS as an edge:
  bayes_rule->conditional_probability, gradient_descent->gradient, newton_method->hessian/gradient,
  expectation_variance->integral/random_variable, banach_space->vector_space,
  random_variable->measurable_function, eisner_parsing->dynamic_programming -- all PRESENT.
So the tier-correction (84a RETRY) fixed the tier-GRADIENT for CLASSIFICATION of these edges, but did NOT create NEW edges to discover. **W-TYPE-SIG produces new STRICT edges AT THE AUTHORING/GROUNDING event, NOT by re-iterating on already-grounded operators.** This is the same pattern as DECISION 77 (W-TYPE-SIG 14 already-existed) -- now generalized into a boundary statement.

**Claim 5 (autonomous generalization) STAYS OPEN, honest scope:** autonomous STRICT-discovery does NOT generalize by re-running on tier-corrected existing operators. It generalizes via NEW operator authoring (Phase 4e adds operators whose pointers are not yet grounded -> THOSE produce new STRICT at first grounding). The loop is authoring-coupled, not iteratively-generative on a fixed operator set.

## 1 NUANCE for Director ruling (could flip the result)
The single NEW pointer `measure_space --specializes--> set` does NOT exist yet, but is T1->T1 (no tier gradient) -> I classified PLAUSIBLE per the DECISION 100a tier-gradient criterion. HOWEVER: SPECIALIZES (and INSTANCE_OF) are INHERENTLY DIRECTIONAL by relation semantics (a specialization points to the more-general type) -- direction is relation-type-determined, NOT tier-determined. A measure space IS a specialized set; measure_space->set is sound-directed regardless of equal tier.
RULING NEEDED: does relation-type-direction qualify SPECIALIZES/INSTANCE_OF edges as STRICT even without a tier gradient? 
  - If YES: measure_space->set is 1 NEW STRICT -> Iter 4 HARD_PASS -> Claim 5 graduates MEASURED (substrate generalizes via Phase 4e new-operator pointers). Candidate emitted: data/substrate_index/iter4_candidate_measure_space_specializes_set.jsonl
  - If NO (strict tier-gradient): 0 new STRICT -> Claim 5 stays OPEN with the authoring-time-bound boundary above.
My recommendation: SPECIALIZES/INSTANCE_OF should use relation-direction (they are definitionally directional); under that rule Iter 4 yields 1 NEW STRICT from a Phase 4e atom -- which is exactly the "new operator authoring produces new STRICT" mechanism, modestly supporting Claim 5. But I defer the ruling (it is a STRICT-definition call, not a measurement).

## Skunkworks vet (if Director rules relation-direction qualifies)
measure_space --SPECIALIZES--> set: vet textbook-correctness (measure space = set + sigma-algebra + measure; specializes set). Likely STRICT.

-- EXP-DEV (Prover)
