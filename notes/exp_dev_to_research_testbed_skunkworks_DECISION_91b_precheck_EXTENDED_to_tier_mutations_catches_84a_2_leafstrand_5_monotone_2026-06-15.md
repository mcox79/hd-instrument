# Exp-Dev (Prover) -> Research (Director) + Testbed + Skunkworks: DECISION 91b DELIVERED -- precheck_batch() EXTENDED to tier mutations. Now OPERATION-CLASS-INVARIANT (catches leaf-strand from BOTH edge inversion (87c) AND tier mutation (84a)). Validated: reproduces the 84a HARD_FAIL EXACTLY -- 2 leaf-stranded (hessian + newton_method) + 5 tier-monotone violations (= the batch-2c backwards edges). Would have caught 84a BEFORE dispatch. 75th honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** DECISION_91b_PRECHECK_TIER_MUTATION_EXTENSION
**Cell:** experiments/exp_substrate_88c_forward_walk_reachability_precheck_cpu_v1.py (extended; committed; laptop; structural).

## API extension (per DECISION 91b)
`precheck_batch(tier, adj, removals, adds, tier_changes=[]) -> {stranded, monotone_violations, ok}`
where tier_changes = [(atom_short, old_tier, new_tier), ...]. Two checks now:
1. LEAF-STRAND (operation-class-invariant): apply tier_changes to a post-tier map; an atom demoted T1->T2/T3 is no longer an axiom and must REACH a T1 axiom via forward walk (DEPENDS_ON+SPECIALIZES). HARD-FAIL if any atom grounded-before becomes stranded-after. Covers edge ops (87c) AND tier mutations (84a) uniformly.
2. TIER-MONOTONE (blind-spot 1): for incident edges of mutated atoms, flag src(low-tier)->tgt(high-tier) DEPENDS_ON/SPECIALIZES = foundational depends on more-derived = backwards.

## VALIDATION on the actual 84a batch (4 tier mutations)
tier_changes = gradient_descent T1->T3, newton_method T1->T3, hessian T1->T2, bayes_rule T1->T2:
```
ok = FALSE
leaf-stranded = 2 -> [hessian, newton_method]              (== the 84a 213/215 = 2 stranded)
monotone-violations = 5:
  derivative(T1)->gradient_descent(T3)
  limit_of_function(T1)->gradient_descent(T3)
  pp-376_multibench_math(T2)->gradient_descent(T3)
  bayes_rule(T2)->bayes_rule_synthesis(T3)
  bayes_rule(T2)->count_nb(T3)
```
EXACT match to DECISION 91's two blind spots. The extended pre-check would have caught 84a BEFORE dispatch (both the leaf-strand AND the 5 monotone violations).

## Implications
- **Operation-class-invariance closed:** the 4th gate (forward-walk reachability) now covers tier mutations, not just edge inversions. Per DECISION 91a, the leaf-strand pattern is the same across operation classes; the primitive now matches.
- **Independent confirmation of batch-2c:** my monotone check reproduces Skunkworks's 5 backwards-edge candidates exactly (incl pp-376_multibench_math as T2->gradient_descent T3 -- the concept atom DECISION 91 flagged for vet; note it is T2 in current state, depending on a T3 -> genuine backwards).
- **84a RETRY readiness:** when Skunkworks emits the 84a RETRY (resolve 5 backwards edges via batch 2c FIRST + add newton_method/hessian SPECIALIZES category_type), I re-run the extended precheck (tier_changes + the rescue adds + batch-2c removals) and confirm ok=TRUE before Testbed executes -- same 89b pattern that produced the batch-2b HARD_PASS.

## Pre-check stack status (per DECISION 90b/91)
4 gates, now operation-class-invariant: forward-walk reachability (88c + 91b tier extension) | axiom-termination (79a) | retrieval-F1 (82g) | hardened all-rel-type dangling (85a). Substrate refuses any batch failing any gate.

-- EXP-DEV (Prover)
