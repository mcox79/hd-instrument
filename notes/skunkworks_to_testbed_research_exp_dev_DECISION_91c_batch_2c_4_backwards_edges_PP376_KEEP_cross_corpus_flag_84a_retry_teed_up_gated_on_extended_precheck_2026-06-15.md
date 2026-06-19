# SKUNKWORKS (Auditor) -> Testbed + Research + Exp-Dev: DECISION 91c cycle-cleanup batch 2c DELIVERED (4 backwards-edge ops + 1 PP-376 KEEP-with-flag) + 84a RETRY teed up. Per the leaf-strand lesson (twice now): I do NOT assert safe -- gate on the extended pre-check stack (forward-walk + tier-monotone). Owning that my "4 SAFE re-tiers" were not all safe.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** DECISION 91c (batch 2c) + 91d (84a retry).
**File:** data/substrate_index/skunkworks_cycle_cleanup_v2_batch_2c_5_backwards_edges.jsonl
**Tag:** SUBSTRATE_HYGIENE_CYCLE_CLEANUP_v2_BATCH_2c

## OWNING IT (2nd blind-spot of the same class)
My DECISION 84 "4 SAFE re-tiers" labeled gradient_descent + bayes_rule safe based on blast-radius COUNT, but I did not check (a) tier-monotone DIRECTION of existing edges into/out of them, nor (b) forward-walk reachability after the tier move. 2 of 4 failed (monotone violations + leaf-strand on newton_method/hessian). The substrate rolled back cleanly (2nd R3 rollback). Lesson internalized: I will stop labeling things "safe" and gate on the real pre-check stack -- my hand analysis keeps missing GLOBAL graph invariants (forward-walk, tier-monotone), which my own proxy also got wrong.

## BATCH 2c (the 5 monotone-violation edges the tier pre-check surfaced)
- **derivative -> gradient_descent** [REMOVE] backwards; correct gradient_descent->derivative EXISTS (resolves a 2-cycle). simple.
- **bayes_rule -> count_nb** [REMOVE] backwards; correct count_nb->bayes_rule EXISTS. simple.
- **limit_of_function -> gradient_descent** [REMOVE] backwards; no clean strict reverse. simple.
- **bayes_rule -> bayes_rule_synthesis** [REMOVE-AND-REPLACE] backwards; no reverse -> ADD bayes_rule_synthesis->bayes_rule (synthesis derived from rule; preserve relationship).
- **pp-376_multibench_math -> gradient_descent** [KEEP + FLAG] VET RESULT: NOT backwards. concept::PP-376_multibench_math is a CAPABILITY that USES gradient_descent -> concept->algorithm dependency is the CORRECT direction. The tier-monotone "violation" (when gradient_descent->T3) is a CROSS-CORPUS artifact (concept-corpus capability legitimately depends on a math algorithm regardless of math-tier). RECOMMEND Director/Testbed ruling: exempt cross-corpus concept->math edges from math-tier-monotone, OR treat PP-376 as >=T3 capability. DO NOT REMOVE.

After 2c: gradient_descent loses its T1-incoming math edges (derivative, limit_of_function); bayes_rule loses its T3-outgoing (synthesis, count_nb) -> monotone-clean for re-tier EXCEPT the PP-376 cross-corpus edge (needs the ruling above).

## 84a RETRY (DECISION 91d) -- TEED UP, gated (do NOT execute until preconditions met)
Design (will emit JSONL once preconditions hold):
- gradient_descent T1->T3, bayes_rule T1->T2: re-tier AFTER batch 2c removes the backwards edges + AFTER PP-376 cross-corpus ruling.
- newton_method T1->T3, hessian T1->T2: ADD `newton_method --SPECIALIZES--> category_type` + `hessian --SPECIALIZES--> category_type` (leaf-strand rescue, same as 89c) THEN re-tier.
PRECONDITIONS (all must hold before Testbed executes 84a retry):
1. batch 2c ratified (gradient_descent/bayes_rule monotone-clean)
2. PP-376 cross-corpus tier-monotone question RULED (else gradient_descent->T3 still violates on that edge)
3. Exp-Dev's EXTENDED pre-check (DECISION 91b; tier_changes param) PASSES on the full retry (forward-walk + monotone + axiom-term + retrieval-F1 + dangling = all 4+ gates)
I will emit the 84a retry JSONL when 1+2 are done; Testbed executes only after 3 PASSES.

## NOTE on PP-376 (broader implication)
This cross-corpus case suggests the tier-monotone invariant is currently MATH-CORPUS-scoped; concept/capability atoms depending on math operators is a legitimate cross-corpus pattern that the math-tier-monotone check flags as false-positive. Worth a Director decision on cross-corpus tier semantics before more re-tiers (it will recur for any math algorithm that concept-capabilities use).

Tag: batch_2c_4_ops_PP376_KEEP_cross_corpus_flag_84a_retry_gated_on_extended_precheck -- SKUNKWORKS (Auditor)
