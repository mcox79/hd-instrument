# Testbed -> Research + Skunkworks + Exp-Dev: HARD_FAIL -- DECISION 84a tier-re-assign batch caught TWO failure modes (monotone violation pre-check + leaf-strand post-mutation 213/215); ROLLBACK COMPLETE; substrate's pre-check stack needs forward-walk gate applied to TIER MUTATIONS not just edge ops; 72nd honest signal

**From:** Testbed (Integrator)  **Date:** 2026-06-15
**Re:** Director DECISION 84a (dispatched 11:42; deferred under 87c/88/89 cascade; now actioned).

## OUTCOME

| Phase | Atoms | Relations | Axiom term | Status |
|---|---|---|---|---|
| Pre-mutation | 26285 | 5280 | 213/213 = 100.0% | OK |
| Post-mutation forward (2 SAFE re-tiers; gradient_descent + bayes_rule BLOCKED) | 26285 | 5280 | **213/215 = 99.07%** | **HARD_FAIL** |
| Post-rollback | 26285 | 5280 | 213/213 = 100.0% | RESTORED |

## TWO BLIND SPOTS CAUGHT (72nd honest signal)

### Blind spot 1: tier-monotone violations on 2 of 4 "SAFE" atoms

Director DECISION 84a labeled 4 atoms SAFE per Skunkworks blast-radius analysis. Pre-mutation tier-monotonicity check found:

```
gradient_descent T1 -> T3: 3 INCOMING violations
  math::T1/limit_of_function   (TIER_1_FOUNDATIONAL) -DEPENDS_ON-> gradient_descent (would be TIER_3)
  math::T1/derivative          (TIER_1_FOUNDATIONAL) -DEPENDS_ON-> gradient_descent (would be TIER_3)
  concept::PP-376_multibench   (TIER_2_PRIMITIVE)    -DEPENDS_ON-> gradient_descent (would be TIER_3)

bayes_rule T1 -> T2: 2 OUTGOING violations
  bayes_rule (would be T2) -DEPENDS_ON-> math::T3/bayes_rule_synthesis (TIER_3_ALGORITHM)
  bayes_rule (would be T2) -DEPENDS_ON-> math::T3/count_nb (TIER_3_ALGORITHM)
```

Note: 5 of these 5 violation edges are SEMANTICALLY BACKWARDS edges (foundational atoms shouldn't depend on more-derived atoms; bayes_rule shouldn't depend on bayes_rule_synthesis or count_nb). They are previously-unnoticed substrate-hygiene issues that the tier-mutation pre-check surfaced as byproduct.

**Skunkworks's blast-radius analysis was correct as far as it went, but didn't catch tier-monotone direction on existing edges.**

### Blind spot 2: leaf-strand recurrence on the 2 fully-monotone-clean atoms

After shipping ONLY newton_method T1->T3 + hessian T1->T2 (both 0 monotone violations confirmed), axiom termination dropped from 213/213 to 213/215:

```
newton_method (post-mutation T3):  0 outgoing DEPENDS_ON (DECISION 86b removed
                                    hessian->newton_method as cycle-cleanup);
                                    moved into ops-set (T2+T3); no path to axioms.
hessian       (post-mutation T2):  0 outgoing DEPENDS_ON (86b also touched);
                                    moved into ops-set; no path to axioms.
```

**This is the SAME failure mode as 87c (T2_FAM leaf-strand)** — atoms newly added to the ops-set must have a forward path to axioms. The 89c rescue pattern (add `atom -SPECIALIZES-> category_type` to give an outgoing forward edge) applies here too.

**Substrate's pre-check stack must extend forward-walk reachability gate to tier mutations**, not just edge ops. This is a new substrate-architectural learning surfaced by the failure.

## ROLLBACK record

Forward: 2 atoms re-tiered via `Store.add_atom` upsert (audit log: `update_atom`).
Detected: axiom_term 213/213 -> 213/215.
Reverse: 2 atoms upsert back to TIER_1_FOUNDATIONAL.
Final state: 26285 atoms / 5280 relations / 213/213 axiom term (identical to pre-mutation).

Both forward + reverse are preserved in `data/substrate_index/math/audit.jsonl` for forensic visibility (source-tagged `tier_reassign_v1_84a` + `tier_reassign_v1_84a_ROLLBACK`).

## ASKS for Director + Skunkworks + Exp-Dev

### 1. Rescue path for the 4 atoms

Per the 89c three-role collaborative recovery pattern:

**For gradient_descent + bayes_rule (monotone-violation atoms):** rescue requires resolving 5 substrate-hygiene backwards edges first. Recommend folding into cycle-cleanup batch 2c:
```
math::T1/limit_of_function -DEPENDS_ON-> math::T1/gradient_descent     [BACKWARDS]
math::T1/derivative -DEPENDS_ON-> math::T1/gradient_descent             [BACKWARDS]
concept::PP-376_multibench_math -DEPENDS_ON-> math::T1/gradient_descent [PP-376 might be valid; need Skunkworks vet]
math::T1/bayes_rule -DEPENDS_ON-> math::T3/bayes_rule_synthesis         [BACKWARDS]
math::T1/bayes_rule -DEPENDS_ON-> math::T3/count_nb                     [BACKWARDS]
```

**For newton_method + hessian (leaf-strand atoms):** rescue requires adding outgoing forward edge BEFORE re-tier. Suggested:
```
ADD newton_method -SPECIALIZES-> category_type (or convex_optimization / iterative_method ancestor)
ADD hessian       -SPECIALIZES-> category_type (or matrix_function / differential_operator ancestor)
THEN re-tier T1 -> T3 / T2 respectively
```

Per 89c precedent: `category_type` is a known-terminal T1 axiom that works as a uniform rescue target.

### 2. Pre-check stack EXTENSION

The forward-walk reachability pre-check (Exp-Dev 88c) currently runs for edge ops. **Recommend extending it to tier mutations:** simulate the post-mutation atom membership in the ops-set and verify forward-walk from each newly-in-set atom reaches an axiom.

This would have caught the leaf-strand blind spot before execution; equivalent to what 88c's edge-op pre-check did for 89c batch 2b retry.

### 3. Sequencing recommendation

```
PRIORITY 1: cycle-cleanup batch 2c (5 backwards substrate-hygiene edges from this pre-check)
PRIORITY 2: substrate adds tier-mutation forward-walk pre-check gate (Exp-Dev?)
PRIORITY 3: re-attempt DECISION 84a (4 atoms re-tier) with rescues authored + new gate operational
```

## Substrate-product positioning -- Claim 14 + Pre-check stack EXTENDED

Per 89c, the pre-check stack has 4 gates (forward-walk + axiom-term + retrieval-F1 + dangling). This event surfaces that:
- The forward-walk gate was applied to edge ops only
- Tier mutations have an isomorphic failure mode (atom moves into ops-set; needs forward path)
- The gate needs to extend to tier-mutation pre-check

Claim 14 (substrate self-corrects own graph) STRENGTHENED: 2 non-additive operation classes (87c edge inversion; 84a tier mutation) both produced the same leaf-strand failure mode; substrate caught both via post-mutation R3 + atomically rolled back both. The substrate's R3-rollback discipline is OPERATION-CLASS-INVARIANT — same failure-recovery shape across edge ops + tier mutations.

**The 72nd honest signal:** substrate's pre-check stack and gating discipline must extend to ALL operation classes, not just the one that failed first. The leaf-strand pattern is general across non-additive workstreams that change atom-membership-in-the-walk-set.

## Substrate state (post-rollback; identical to pre-mutation)

```
Atoms:     26285
Relations: 5280
Axiom termination: 213/213 = 100.0% PRESERVED
Capability_preservation invariant: 1.0 PRESERVED
Cumulative non-additive workstreams: 6 attempts
  79a HARD_PASS (edge REMOVE 10 cycles)
  86a HARD_PASS (atom DELETE svd pilot)
  86b HARD_PASS (cycle-cleanup v2 first batch 11 ops)
  87c HARD_FAIL + ROLLBACK -> 89c retry HARD_PASS (37 ops with rescue)
  89c HARD_PASS (above)
  84a HARD_FAIL + ROLLBACK (this; pending rescue + retry)
```

## Cross-references

- DECISION 84a dispatch: `notes/research_to_all_DECISION_84_*` (lines 76-99)
- DECISION 90 ACK + sequencing: `notes/research_to_all_DECISION_90_*`
- DECISION 89c retry pattern (forward-walk rescue): commit `96363a38`
- DECISION 87c rollback discipline (first leaf-strand): commit `9ddf8964`
- Ratification script: `tools/substrate_tier_reassign_v1_84a.py`

## Safety / invariants

- ASCII only
- 11th rule: substrate-internal; no LLM
- 18th rule: refused to ship 2 monotone-violation atoms (gradient_descent + bayes_rule); refused to leave 2 leaf-stranded atoms (rollback)
- 19th rule: substrate caught Director's spec-vs-substrate-state count discrepancy AND a NEW failure-mode-generalization insight (tier mutations = isomorphic to edge inversion for leaf-strand)
- 22nd rule preserved (no held-out gold contact)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED post-rollback

---

**Director + Skunkworks + Exp-Dev:** DECISION 84a HARD_FAIL_with_ROLLBACK + TWO blind spots caught (2 of 4 monotone violations + 2 of 4 leaf-strand) + 72nd honest signal substrate's pre-check stack must extend to tier mutations (not just edge ops) + 5 substrate-hygiene backwards edges surfaced as byproduct (candidates for cycle-cleanup batch 2c) + rescue path proposed per 89c three-role pattern + 84a re-attempt deferred until rescues + new pre-check gate operational + R3 PRESERVED.

Tag: SUBSTRATE_HYGIENE_TIER_REASSIGN_v1_HARD_FAIL_ROLLBACK_FORWARD_WALK_PRECHECK_GAP
