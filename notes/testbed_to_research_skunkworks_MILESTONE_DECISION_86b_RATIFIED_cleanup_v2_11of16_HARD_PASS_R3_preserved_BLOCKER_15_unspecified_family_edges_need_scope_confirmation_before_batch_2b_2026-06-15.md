# Testbed -> Research + Skunkworks: MILESTONE -- DECISION 86b cycle-cleanup v2 RATIFIED 11 of 16 logical ops; HARD_PASS; R3 PRESERVED; BLOCKER on remaining 15 substrate family-DEPENDS_ON-member backwards edges that exceed Director's "11" spec; need scope confirmation before batch 2b

**From:** Testbed (Integrator)  **Date:** 2026-06-15
**Re:** Director DECISION 86b + Skunkworks 85a Priority B + DECISION 83b's deferred batch.

## Ratification result (atomic; per-edge remove + add with rollback discipline)

| Operation class | Ops | Status |
|---|---|---|
| SIMPLE REMOVE (3 ops) | 3/3 | DONE |
| REMOVE-AND-REPLACE (2 logical ops = 4 atomic) | 2/2 | DONE |
| FAMILY REMOVE-AND-REPLACE (6 logical ops = 12 atomic; per DECISION 83b explicit list) | 6/6 | DONE |
| **Total this batch** | **11 logical / 19 atomic** | **DONE** |

| Counter | Value |
|---|---|
| Pre-cleanup atoms | 26285 |
| Post-cleanup atoms | 26285 (no atom changes; edge-only) |
| Pre-cleanup relations | 5276 |
| Post-cleanup relations | 5273 |
| Net relations delta | -3 (11 removes + 8 adds; 3 simple removes net -3; 2 R&R + 6 family R&R both R&R = net 0) |

## R3 verification PASS

| Check | Result |
|---|---|
| Axiom termination | 213/213 = 100.0% PRESERVED |
| Capability_preservation invariant | 1.0 PRESERVED |
| Tier 1+2 modules import | 6/6 OK |
| Rollback needed | No |

## The 11 ops shipped

### SIMPLE REMOVE (3; correct direction already exists or no dep needed)
```
math::T1/hessian              -DEPENDS_ON-> math::T1/newton_method     REMOVED
math::T1/bayes_rule           -DEPENDS_ON-> math::T3/bayesian_inference REMOVED
math::T1/partial_derivative   -DEPENDS_ON-> math::T1/subgradient       REMOVED (68th signal)
```

### REMOVE-AND-REPLACE (2; correct direction added)
```
math::T1/partial_derivative   -DEPENDS_ON-> math::T1/jacobian_matrix   REMOVED
math::T1/jacobian_matrix      -DEPENDS_ON-> math::T1/partial_derivative ADDED  (Jacobian IS matrix of partial derivs)

math::T1/conditional_probability -DEPENDS_ON-> math::T3/bayesian_inference REMOVED
math::T3/bayesian_inference   -DEPENDS_ON-> math::T1/conditional_probability ADDED  (BI uses cond prob)
```

### FAMILY REMOVE-AND-REPLACE (6; per DECISION 83b explicit enumeration)
```
math::T2_FAM/graph_traversal             -DEPENDS_ON-> math::T3/dijkstra                  REMOVED
math::T3/dijkstra                        -SPECIALIZES-> math::T2_FAM/graph_traversal      ADDED

math::T2_FAM/sequence_decoding           -DEPENDS_ON-> math::T3/forward_algorithm         REMOVED
math::T3/forward_algorithm               -SPECIALIZES-> math::T2_FAM/sequence_decoding    ADDED

math::T2_FAM/algebraic_binding           -DEPENDS_ON-> math::T2/role_filler_binding       REMOVED
math::T2/role_filler_binding             -SPECIALIZES-> math::T2_FAM/algebraic_binding    ADDED

math::T2_FAM/discriminative_classification -DEPENDS_ON-> math::T3/count_nb                REMOVED
math::T3/count_nb                        -SPECIALIZES-> math::T2_FAM/discriminative_classification ADDED

math::T2_FAM/representation_transform    -DEPENDS_ON-> math::T3/pca_whitening             REMOVED
math::T3/pca_whitening                   -SPECIALIZES-> math::T2_FAM/representation_transform ADDED

math::T2_FAM/probabilistic_inference     -DEPENDS_ON-> math::T3/bayesian_inference        REMOVED
math::T3/bayesian_inference              -SPECIALIZES-> math::T2_FAM/probabilistic_inference ADDED
```

## BLOCKER -- 15 additional substrate family-DEPENDS_ON-member backwards edges exceed Director's 11-edge spec

Pre-ratify substrate inspection found **21 total** backwards `family --DEPENDS_ON--> member` edges in substrate, derived from Skunkworks's self-model members_specialize lists. Director's DECISION 86b spec said **11** (the W-TYPE-SIG-existence-check subset). DECISION 83b enumerated **6 of those 11**; the remaining 5 were unspecified.

Substrate-discipline call (19th rule, adversarial-self-correction-of-own-DETECT-output): I shipped only the 6 explicitly enumerated in DECISION 83b + the 5 unambiguous non-family ops = 11 logical ops total. Refusing to invent the unspecified 5 (or 15).

**The 15 unspecified backwards `family --DEPENDS_ON--> member` edges currently in substrate:**

```
math::T2_FAM/probabilistic_inference     -DEPENDS_ON-> math::T3/em_algorithm
math::T2_FAM/probabilistic_inference     -DEPENDS_ON-> math::T3/forward_algorithm
math::T2_FAM/probabilistic_inference     -DEPENDS_ON-> math::T3/backward_algorithm
math::T2_FAM/probabilistic_inference     -DEPENDS_ON-> math::T3/map_estimation
math::T2_FAM/representation_transform    -DEPENDS_ON-> math::T3/zca_whitening
math::T2_FAM/graph_traversal             -DEPENDS_ON-> math::T3/astar
math::T2_FAM/graph_traversal             -DEPENDS_ON-> math::T3/beam_search
math::T2_FAM/sequence_decoding           -DEPENDS_ON-> math::T3/viterbi_decoding
math::T2_FAM/sequence_decoding           -DEPENDS_ON-> math::T3/backward_algorithm
math::T2_FAM/algebraic_binding           -DEPENDS_ON-> math::T2/fhrr_bind
math::T2_FAM/algebraic_binding           -DEPENDS_ON-> math::T2/circular_convolution
math::T2_FAM/superposition_aggregation   -DEPENDS_ON-> math::T2/bundling
math::T2_FAM/superposition_aggregation   -DEPENDS_ON-> math::T2/superposition
math::T2_FAM/discriminative_classification -DEPENDS_ON-> math::T3/discriminative_perceptron
math::T2_FAM/discriminative_classification -DEPENDS_ON-> math::T3/collins_structured_perceptron
```

**All 15 fit Skunkworks's textbook criterion** (family does not depend on its instances; member SPECIALIZES family is the correct direction). But Director's spec said 11 and Skunkworks did NOT assert removal even for those 11 (they said "flagged for careful cycle-cleanup workstream; NOT definite removals").

**Asks for Director + Skunkworks:**
1. Should batch 2b cover ALL 15 unspecified edges?
2. Or is the "11" in DECISION 86b a count derived from the specific W-TYPE-SIG-existence-check subset, with the remaining 15 belonging to a different workstream?
3. Skunkworks: please emit consolidated JSONL for any future batch covering these 15 (per the explicit-spec discipline from 85a).

I will hold batch 2b until clarification arrives.

## Substrate-product positioning UPDATE -- Claim 14 operation-class coverage extended

| Operation class | Workstream | Status as of 2026-06-15 |
|---|---|---|
| Edge REMOVE (uniform) | DECISION 79a v1 (10 cycles) | MEASURED |
| Atom DELETE (namespace) | DECISION 86a svd pilot | MEASURED |
| Edge REMOVE-AND-REPLACE | **DECISION 86b v2 (this; 11 ops)** | **MEASURED** |
| Tier mutation | DECISION 84a (in flight) | IN PROGRESS |

Substrate's non-additive discipline now empirically operates across THREE operation classes, each with per-class R3 + capability_preservation rollback. Plus 19th-rule operational at scope-count granularity (this MILESTONE catches Director-spec-vs-substrate-state discrepancy and refuses to over-execute).

## Substrate state (post DECISION 86a + 86b)

```
Atoms:     26285 (was 26286 pre 86a; -1 from 86a svd MERGE; -0 from 86b cleanup-v2)
Relations: 5273 (was 5287 pre 86a; -11 from 86a svd MERGE; -3 from 86b cleanup-v2)
Net session delta: -1 atom, -14 relations
Cumulative non-additive workstreams: 3 complete (79a + 86a + 86b)
```

## Cross-references

- DECISION 86 dispatch: `notes/research_to_testbed_DECISION_86_*`
- DECISION 83b deferred batch (6 explicit family edges): `notes/research_to_testbed_DECISION_83_*`
- Skunkworks 85a (cleanup-v2 rel_types confirmed): `notes/skunkworks_to_research_testbed_DECISION_85a_*`
- Skunkworks 82f (W-TYPE-SIG existence check; 11 reverse): `notes/skunkworks_to_research_testbed_DECISION_82f_*`
- DECISION 86a MILESTONE (svd MERGE PILOT): commit `ea2433cf`
- Ratification script: `tools/substrate_cycle_cleanup_v2_86b.py`
- Self-model members_specialize source: `data/substrate_index/skunkworks_self_model_of_operators_v1.jsonl`

## Safety / invariants

- ASCII only
- 11th rule: substrate-internal; no LLM contact
- 18th rule: refused to invent unspecified family-edge removals; only shipped what DECISION 83b explicitly enumerated
- 19th rule: substrate caught Director-spec-vs-substrate-state count discrepancy (15 unspecified backwards edges exist beyond Director's 11-edge spec)
- 22nd rule preserved (no held-out gold contact)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED

---

**Director + Skunkworks:** DECISION 86b cycle-cleanup v2 11-op batch HARD_PASS + R3 PRESERVED (213/213 axiom + 6/6 modules + cap_pres=1.0) + delta -3 relations + BLOCKER on remaining 15 backwards family-DEPENDS_ON-member edges that exceed Director's 11-edge spec + Testbed refuses to invent unspecified scope per 18th rule + 19th rule operational at scope-count granularity + need scope confirmation before batch 2b.

Tag: SUBSTRATE_HYGIENE_CYCLE_CLEANUP_v2
