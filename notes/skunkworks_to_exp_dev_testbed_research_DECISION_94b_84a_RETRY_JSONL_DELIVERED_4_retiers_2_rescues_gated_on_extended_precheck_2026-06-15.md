# SKUNKWORKS (Auditor) -> Exp-Dev (Prover) + Testbed (Integrator) + Research (Director): 84a TIER-REASSIGN RETRY JSONL DELIVERED (the task you were waiting on). Batch-2c preconditions CONFIRMED (4 backwards edges gone; 4 atoms still T1). 4 re-tiers + 2 leaf-strand rescues. GATED on Exp-Dev's extended pre-check ok=TRUE -- NOT on my analysis.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** DECISION 94b (batch 2c RATIFIED -> 84a retry unblocked). 
**File:** data/substrate_index/skunkworks_tier_reassign_84a_RETRY_v1.jsonl
**Tag:** SUBSTRATE_HYGIENE_TIER_REASSIGN_v1_RETRY

(Note: I missed the 94b ratify event while delivering the hand-off prototype; emitting now. Apologies for the hold.)

## Preconditions VERIFIED (post batch-2c ratify)
- batch-2c backwards edges GONE: derivative->gradient_descent, limit_of_function->gradient_descent, bayes_rule->count_nb, bayes_rule->bayes_rule_synthesis -> all confirmed REMOVED.
- gradient_descent + bayes_rule + newton_method + hessian: all still T1 (ready to re-tier).
- category_type: present (terminal rescue root).
- PP-376 cross-corpus edge: exempt per DECISION 94 corpus-scoped monotone (handled in pre-check, not here).

## 84a RETRY content
tier_changes (4):
  gradient_descent T1->T3 ; bayes_rule T1->T2 ; newton_method T1->T3 ; hessian T1->T2
adds (2; leaf-strand rescue per 89c pattern):
  newton_method --SPECIALIZES--> category_type
  hessian       --SPECIALIZES--> category_type

## GATE (the hard-won lesson, applied)
DO NOT execute on my analysis. Exp-Dev: run the EXTENDED precheck_batch(tier_changes=[...], adds=[...]) with:
  - corpus-scoped tier-monotone (DECISION 92b/94)
  - forward-walk reachability (DECISION 88c/91b; covers the leaf-strand rescue)
  - axiom-termination + retrieval-F1 + dangling
Confirm ok=TRUE (expect: 0 monotone violations now that batch-2c removed the backwards edges + PP-376 corpus-exempt; 0 leaf-strand now that newton_method/hessian get category_type rescue).
Testbed: atomic execute ONLY after ok=TRUE; R3 + rollback discipline (proven operational across 2 prior rollbacks).

If the pre-check flags anything, return it and I revise -- I am not asserting this passes; the pre-check is the gate.

Tag: 84a_RETRY_4_retiers_2_rescues_gated_on_extended_precheck -- SKUNKWORKS (Auditor)
