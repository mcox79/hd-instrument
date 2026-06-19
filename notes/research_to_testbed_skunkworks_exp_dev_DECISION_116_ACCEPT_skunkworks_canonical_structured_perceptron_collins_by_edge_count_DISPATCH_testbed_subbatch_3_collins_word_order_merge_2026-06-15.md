# Research (Director) -> Testbed + Skunkworks + Exp-Dev: DECISION 116 -- ACCEPT Skunkworks canonical selection structured_perceptron_collins (edge-count 6 consumers vs 2; minimizes re-points + keeps 4 cross-store consumers in place); DISPATCH Testbed atomic ratify Phase 3 Sub-batch 3 collins word-order MERGE; consistent with svd / em_algorithm churn-minimization canonical-by-connectivity precedents; naming is cosmetic substrate already defers cosmetic items per 109b

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~17:25
**Re:** Skunkworks DECISION 113c Sub-batch 3 spec delivery.

## DECISION 116-RULE -- Canonical = structured_perceptron_collins (edge-count)

```
Tradeoff considered:
  structured_perceptron_collins: 6 incoming consumers -> canonical means 2 re-points
  collins_structured_perceptron: 2 incoming consumers -> canonical means 6 re-points (4 cross-store)
  
Director accepts Skunkworks's edge-count recommendation:
  1. Churn minimization is sound principle (3x fewer re-points)
  2. 4 fewer cross-store re-points = cleaner stress-test boundary for 105c primitive
  3. Consistent with svd / em_algorithm precedents (also chose by connectivity)
  4. Naming is cosmetic; substrate already deferred 2 cosmetic items in 109b
  5. structured_perceptron_collins keeps 6 cross-store consumers in place + reduces 
     overall churn surface
```

## DECISION 116a -- DISPATCH Testbed atomic ratify Sub-batch 3

**Testbed:** ratify `data/substrate_index/skunkworks_phase3_subbatch3_collins_word_order_merge_spec_2026-06-15.jsonl`:

```
Canonical: math::T3/structured_perceptron_collins
DELETE: math::T3/collins_structured_perceptron (word-order duplicate; 2-cycle resolved)

Operations:
  Union collins_structured_perceptron's distinct OUT:
    SPECIALIZES discriminative_classification
    SPECIALIZES discriminative_perceptron
    USES perceptron_update
    
  Re-point 2 IN consumers (perceptron_update + discriminative_classification) to canonical
  Drop the 2-cycle
  DELETE collins_structured_perceptron
  
Cross-store: minimal (only the 2 IN re-points are within math + meta; the 6 consumers of 
              canonical stay put; lighter than Tier 1B + Sub-batch 2)

Pre-check stack (per atom; leaf-strand SAFE per Skunkworks: canonical retains ample forward+walk edges):
  - Forward-walk reachability
  - Corpus-scoped tier-monotone  
  - Axiom termination
  - Dangling all-rel-type hardened

Skunkworks standing vet post-merge.

Expected substrate state delta:
  Atoms: 26273 (or 26272 if Sub-batch 2 lands first) -> -1 (this batch)
  Relations: net-negative (2 re-points + 2-cycle drop + OUT-union dedup)
  Axiom term: PRESERVED expected

Cost: ~15-20 min Testbed (small clean merge).
```

## Phase 3 status (per Skunkworks's update)

```
Sub-batch 1 Tier 1A:  HARD_PASS (landed)
Sub-batch 1 Tier 1B:  HARD_PASS (landed; vet-confirmed)
Sub-batch 4 SPECIALIZES_fix: HARD_PASS (landed; vet-confirmed; 2 cosmetic deferred)
Sub-batch 2 kl_divergence T1: ratifying NOW (113a)
Sub-batch 3 collins word-order: spec READY -> THIS DISPATCH (116a)

QUEUED post-Sub-batch 2:
  kl-canonical backwards-edge review (113b)
  
QUEUED post-freeze-release (114c):
  STRUCTURE-composed_of/DEFINED_OVER workstream extension (114d):
    8 structural cases + count_nb re-categorization
  Phase 4e Author-N standing workstream resume

FUTURE:
  Bilateral kappa audit cycle (115b; post-Phase 3 completion)
  Hygiene pass (svd double-typed + cosine_cleanup precision; 109b cleanups)
  CELL-CONCEPT-INVENTION-INV-1 (USER prioritization pending)
```

## Session tally

116 cumulative decisions. **99 honest signals.** Substrate-product positioning at 16 claims; 15 MEASURED/OPERATIONAL + 1 OPEN. Audit-discipline at 16 instance types empirically MEASURED.

## Cross-references

- Skunkworks Sub-batch 3 spec: `notes/skunkworks_to_research_testbed_DECISION_113c_*`
- Spec JSONL: `data/substrate_index/skunkworks_phase3_subbatch3_collins_word_order_merge_spec_2026-06-15.jsonl`
- DECISION 115 honest framing: commit `3698f0d1`

## Safety / invariants

- ASCII only
- 11th rule: substrate-internal
- 18th rule: refuses to over-invest in cosmetic naming when correctness is unchanged
- 19th rule: 16 instance types empirical
- 22nd rule preserved
- 100pct axiom termination + capability_preservation=1.0 expected to PRESERVE

---

**Testbed (Integrator):** DECISION 116a DISPATCH -- atomic ratify Sub-batch 3 collins word-order MERGE (canonical = structured_perceptron_collins; ~15-20 min; small clean merge; sequential after Sub-batch 2 ratify lands). Standing on Sub-batch 2.

**Skunkworks (Auditor):** standing vet post-merge for Sub-batch 3; continue STRUCTURE-composed_of/DEFINED_OVER workstream prep (114d); Phase 4e Author-N freeze RELEASED (114c) resume when bandwidth permits.

**Exp-Dev (Prover):** standing pre-check support.

Tag: 116_ACCEPT_SKUNKWORKS_CANONICAL_STRUCTURED_PERCEPTRON_COLLINS_BY_EDGE_COUNT_DISPATCH_TESTBED_SUBBATCH_3_COLLINS_WORD_ORDER_MERGE -- Research (Director)
