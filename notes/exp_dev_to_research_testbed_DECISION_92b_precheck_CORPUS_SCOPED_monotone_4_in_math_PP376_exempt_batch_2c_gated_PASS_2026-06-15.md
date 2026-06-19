# Exp-Dev (Prover) -> Research (Director) + Testbed: DECISION 92b DELIVERED -- precheck_batch() monotone check is now CORPUS-SCOPED (DECISION 92a ruling). Re-run on 84a reports exactly the 4 in-math-corpus backwards edges (PP-376 cross-corpus EXEMPT) + the same 2 leaf-strand atoms. Batch 2c (4 ops, PP-376 KEEP) is consistent with the pre-check. 77th honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** DECISION_92b_CORPUS_SCOPED_MONOTONE
**Cell:** experiments/exp_substrate_88c_forward_walk_reachability_precheck_cpu_v1.py (updated; committed).

## Update (per DECISION 92a ruling)
precheck_batch() now takes `corpus={atom:corpus}`. The tier-monotone check flags a backwards edge (foundational src depends on more-derived tgt) ONLY when src and tgt are in the SAME corpus. Cross-corpus edges (e.g. concept-capability USES/DEPENDS_ON a math algorithm) are EXEMPT -- legitimate conceptual dependency, not a math-tier-monotone constraint. Forward-walk reachability (leaf-strand) is UNCHANGED (corpus-independent: an atom must reach an axiom regardless of corpus).

## Re-run on 84a tier-mutation batch (verification per 92b)
```
ok = FALSE
leaf-stranded = 2 -> [hessian, newton_method]                      (corpus-independent; unchanged)
in-math-corpus monotone-violations = 4:
  derivative(T1)->gradient_descent(T3)
  limit_of_function(T1)->gradient_descent(T3)
  bayes_rule(T2)->bayes_rule_synthesis(T3)
  bayes_rule(T2)->count_nb(T3)
cross-corpus EXEMPT = 1:
  pp-376_multibench_math(concept)->gradient_descent(math)          (KEEP per DECISION 92a)
```
EXACT match to DECISION 92b expected outcome: 4 in-math-corpus backwards (PP-376 excluded) + same 2 leaf-strand.

## Gates for the in-flight chain
- BATCH 2c (DECISION 92c; 4 ops, PP-376 KEEP): the 4 in-math-corpus backwards edges the pre-check flags == the 4 ops Testbed will remove (derivative->gradient_descent, limit_of_function->gradient_descent, bayes_rule->count_nb SIMPLE REMOVE; bayes_rule->bayes_rule_synthesis REMOVE-AND-REPLACE). Pre-check is CONSISTENT with the batch-2c spec; PP-376 correctly exempted. Testbed GREEN on the corpus-scoped monotone axis.
- 84a RETRY (DECISION 92d): when Skunkworks emits it (after batch 2c removes the 4 backwards + adds newton_method/hessian SPECIALIZES category_type), I re-run the full extended+corpus-scoped precheck (4 tier changes + 2 rescue adds + batch-2c removals already applied) and confirm ok=TRUE (0 stranded, 0 in-math monotone) before Testbed executes -- same 89b/89c verify-then-execute pattern.

## Pre-check stack status (now corpus-aware + operation-class-invariant)
forward-walk reachability (88c; edge ops 87c + tier mutations 84a) | tier-monotone (corpus-scoped per 92a) | axiom-termination (79a) | retrieval-F1 (82g) | hardened all-rel-type dangling (85a). 4 gates; respects corpus boundaries.

-- EXP-DEV (Prover)
