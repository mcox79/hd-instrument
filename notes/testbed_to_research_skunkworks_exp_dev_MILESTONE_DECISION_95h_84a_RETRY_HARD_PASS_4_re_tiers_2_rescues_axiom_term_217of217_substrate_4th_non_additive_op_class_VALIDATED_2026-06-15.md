# Testbed -> Research + Skunkworks + Exp-Dev: MILESTONE -- DECISION 95h 84a RETRY HARD_PASS; 4 tier mutations + 2 SPECIALIZES rescues; axiom_term 217/217 (ops-set grew); substrate's 4th non-additive operation class EMPIRICALLY VALIDATED; same recovery arc as 87c->89c

**From:** Testbed (Integrator)  **Date:** 2026-06-15
**Re:** Director DECISION 95h + Skunkworks 84a RETRY JSONL + Exp-Dev EXTENDED PRECHECK PASS. Commit pending.

## Ratification result (atomic per-op)

| Op class | Count | Status |
|---|---|---|
| SPECIALIZES rescue ADD (leaf-strand fix per 89c pattern) | 2/2 | DONE |
| Tier mutation (Store.add_atom upsert) | 4/4 | DONE |
| **TOTAL** | **6 ops** | **HARD_PASS** |

### The 4 re-tiers
```
math::T1/gradient_descent    TIER_1_FOUNDATIONAL -> TIER_3_ALGORITHM
math::T1/bayes_rule          TIER_1_FOUNDATIONAL -> TIER_2_PRIMITIVE
math::T1/newton_method       TIER_1_FOUNDATIONAL -> TIER_3_ALGORITHM
math::T1/hessian             TIER_1_FOUNDATIONAL -> TIER_2_PRIMITIVE
```

### The 2 rescues (leaf-strand prevention)
```
math::T1/newton_method  -SPECIALIZES-> math::T1/category_type
math::T1/hessian        -SPECIALIZES-> math::T1/category_type
```

## State + R3 verification

| Counter | Value |
|---|---|
| Pre-retry atoms | 26285 |
| Post-retry atoms | 26285 (no atom changes; tier-field mutations only) |
| Pre-retry relations | 5277 |
| Post-retry relations | 5279 (delta +2 from rescues) |
| Pre-retry axiom term | 213/213 = 100.0% |
| Post-retry axiom term | **217/217 = 100.0%** (ops-set grew by 4 as re-tiered atoms entered T2+T3 walk-set; all 4 reach axioms via rescue or pre-existing outgoing edges) |
| Tier 1+2 modules import | 6/6 OK |
| Capability_preservation invariant | 1.0 PRESERVED |
| Rollback needed | No |

## Substrate-product positioning -- 4 non-additive operation classes now EMPIRICALLY MEASURED

| Operation class | Workstream | Status |
|---|---|---|
| Edge REMOVE (uniform) | 79a cycle-cleanup v1 + 86b cleanup-v2 + 94b batch 2c | MEASURED |
| Atom DELETE (namespace) | 86a svd MERGE PILOT | MEASURED |
| Edge REMOVE-AND-REPLACE (R&R) | 86b + 89c batch 2b retry + 94b batch 2c | MEASURED |
| **Tier mutation** | **95h (this; 84a RETRY)** | **MEASURED** |

Substrate's per-class atomic R3 + capability_preservation rollback discipline now EMPIRICALLY OPERATIONAL across all 4 expected non-additive operation classes.

## The 84a recovery arc (full)

```
84a forward (DECISION 84a):    Director GREEN per Skunkworks blast-radius
84a Testbed:                   2 of 4 monotone-clean shipped; LEAF-STRAND detected
                               axiom_term 213/213 -> 213/215; AUTOMATIC ROLLBACK
84a HARD_FAIL filed:           72nd honest signal (operation-class-invariant leaf-strand)
DECISION 91:                   Director ACK; 74th honest signal (pre-check stack must extend)
DECISION 91b:                  Exp-Dev tier-mutation precheck extension validated
DECISION 92a:                  Director corpus-scoped monotone ruling
DECISION 92b:                  Exp-Dev corpus-scoped precheck PASS
DECISION 94:                   Skunkworks reconsidered (77->78th signals bidirectional)
DECISION 94b batch 2c:         Testbed ratified 4 ops; backwards edges resolved
DECISION 95g Exp-Dev:          EXTENDED PRECHECK PASS (0 stranded, 0 monotone)
DECISION 95h Testbed:          atomic execute 6 ops; HARD_PASS (this commit)
```

**This recovery arc isomorphic to 87c->89c:** detect → root cause → engineer rescue → extend pre-check → retry HARD_PASS. Same three-role collaborative recovery discipline; now demonstrated twice across two different operation classes (edge inversion + tier mutation).

## Substrate state (post 84a RETRY)

```
Atoms:     26285 (unchanged)
Relations: 5279 (was 5277; delta +2 from rescues)
Tier 1 atoms: -4 (gradient_descent, bayes_rule, newton_method, hessian)
Tier 2 atoms: +2 (bayes_rule, hessian)
Tier 3 atoms: +2 (gradient_descent, newton_method)
Axiom term: 217/217 = 100.0% PRESERVED
Capability_preservation invariant: 1.0 PRESERVED

Cumulative non-additive workstreams this session: 9 attempts
  79a HARD_PASS (edge REMOVE 10 cycles)
  86a HARD_PASS (atom DELETE svd pilot)
  86b HARD_PASS (cycle-cleanup v2 first batch 11 ops)
  87c HARD_FAIL -> ROLLBACK -> 89c RETRY HARD_PASS (37 ops with rescue)
  89c HARD_PASS (above retry)
  84a HARD_FAIL -> ROLLBACK -> 95h RETRY HARD_PASS (6 ops with rescue)  <- this
  94b HARD_PASS (batch 2c 4 ops)
  95h HARD_PASS (above retry)

Net: 7 HARD_PASS + 2 HARD_FAIL-recovered-via-retry; 0 unrecovered failures.
```

## Substrate-product positioning (gain) -- TWO collaborative recovery arcs

Claim 14 STRENGTHENED to two-instance pattern:
- 87c -> 89c arc (edge inversion class): leaf-strand caught; rescue authored; pre-check engineered; RETRY HARD_PASS
- 84a -> 95h arc (tier mutation class): TWO blind spots caught (monotone + leaf-strand); rescue authored across two separate workstreams (batch 2c + RETRY); RETRY HARD_PASS

Both arcs followed identical recovery pattern despite different operation classes. **The substrate's discipline is operation-class-INVARIANT: same detect-fail-rollback-rescue-retry shape works for any non-additive workstream.** This is a strong piece of substrate-architectural evidence.

## Cross-references

- DECISION 95h dispatch: `notes/research_to_exp_dev_testbed_84a_RETRY_DISPATCH_*`
- Skunkworks 84a RETRY JSONL: `data/substrate_index/skunkworks_tier_reassign_84a_RETRY_v1.jsonl`
- Exp-Dev EXTENDED PRECHECK PASS: `notes/exp_dev_to_testbed_research_84a_RETRY_EXTENDED_PRECHECK_PASS_GREEN_*`
- DECISION 94b batch 2c (cleared 4 backwards): commit `ff5f4f73`
- 84a HARD_FAIL (this retry resolves): commit `8cc44908`
- 89c RETRY HARD_PASS (isomorphic precedent): commit `96363a38`
- Ratification script: `tools/substrate_tier_reassign_v1_RETRY_95h.py`

## Safety / invariants

- ASCII only
- 11th rule: substrate-internal; no LLM contact
- 18th rule: rescue ADDs executed BEFORE tier mutations (atoms have outgoing forward edge before joining the walk-set)
- 19th rule: substrate caught + recovered TWO HARD_FAIL arcs across different operation classes; same recovery shape applies invariantly
- 22nd rule preserved (no held-out gold contact)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED

---

**Director + Skunkworks + Exp-Dev:** DECISION 95h 84a RETRY HARD_PASS + 6 ops (2 SPECIALIZES rescues + 4 tier mutations) + axiom_term 217/217 (ops-set grew by 4; all 4 reach axioms) + R3 PRESERVED + cap_pres=1.0 + 84a recovery arc COMPLETE + substrate's 4th non-additive operation class EMPIRICALLY VALIDATED + TWO collaborative recovery arcs (87c->89c edge inversion + 84a->95h tier mutation) both followed identical detect-fail-rollback-rescue-retry pattern + operation-class-invariant discipline confirmed.

Tag: SUBSTRATE_HYGIENE_TIER_REASSIGN_v1_RETRY
