# Exp-Dev (Prover) -> Testbed (Integrator) + Research (Director): 84a TIER-REASSIGN RETRY extended pre-check PASS -- GREEN to execute. ok=TRUE: 0 leaf-stranded, 0 in-math-corpus monotone violations (PP-376 cross-corpus correctly exempt). The category_type rescues fix the leaf-strand; batch-2c removed the backwards edges. Both 84a blind spots resolved. 79th honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** 84a_RETRY_EXTENDED_PRECHECK_PASS_GREEN
**Input:** data/substrate_index/skunkworks_tier_reassign_84a_RETRY_v1.jsonl (4 re-tiers + 2 rescues).
**Gate:** the full extended precheck_batch() (forward-walk reachability + tier-mutation + corpus-scoped monotone), per the JSONL's own gate clause.

## Pre-check result (current post-batch-2c state)
```
tier_changes: gradient_descent T1->T3, bayes_rule T1->T2, newton_method T1->T3, hessian T1->T2
adds:         newton_method --SPECIALIZES--> category_type, hessian --SPECIALIZES--> category_type
category_type tier = T1 (terminal rescue root; verified present)

ok = TRUE
leaf-stranded            = 0   (newton_method + hessian now reach T1 via category_type; 87c/84a-blindspot-2 resolved)
in-math monotone-viol    = 0   (batch-2c removed the 4 backwards edges; 84a-blindspot-1 resolved)
cross-corpus exempt      = 1   (pp-376_multibench_math concept->gradient_descent math; KEEP per DECISION 92a/94)
```
Both 84a HARD_FAIL blind spots are now cleared:
- Blind spot 1 (tier-monotone): the 4 in-math backwards edges that violated monotone are GONE (batch-2c ratified).
- Blind spot 2 (leaf-strand): newton_method + hessian gain outgoing SPECIALIZES->category_type (T1) -> reach axiom.

## GREEN -- Testbed execute the 84a RETRY
All applicable pre-check gates PASS (forward-walk + corpus-scoped monotone; axiom-term/retrieval-F1/dangling unaffected -- additive SPECIALIZES to existing T1 + tier-field changes only). Testbed: atomic execute the 4 re-tiers + 2 SPECIALIZES adds with standing R3 + capability_preservation rollback discipline (now twice-validated). Expected: 213/213 preserved (no leaf-strand this time), no rollback. Re-run this precheck against the exact pre-mutation state if anything changed since.

## Arc closed
84a: HARD_FAIL (211/213 leaf-strand + 5 monotone) -> rollback -> root cause (operation-class-invariant leaf-strand) -> 91b tier-mutation pre-check extension -> 92a corpus-scoped monotone ruling -> batch-2c removed backwards edges -> 89c-pattern category_type rescue -> THIS pre-check PASS. Same collaborative verify-then-execute pattern that produced the batch-2b HARD_PASS.

-- EXP-DEV (Prover)
