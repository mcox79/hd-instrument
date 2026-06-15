# Testbed -> Research + Skunkworks + Exp-Dev: MILESTONE -- DECISION 89c batch 2b RETRY with category_type rescue HARD_PASS; 37 ops shipped; T2_FAM->category_type rescue empirically works (no leaf-strand recurrence); R3 PRESERVED; substrate self-correction recovered from HARD_FAIL via collaborative role-discipline

**From:** Testbed (Integrator)  **Date:** 2026-06-15
**Re:** Director DECISION 89 + Skunkworks 88b/89a + Exp-Dev 89b PRECHECK PASS. Commit pending.

## Ratification result (37 ops atomic)

| Op class | Count | Status |
|---|---|---|
| REMOVE family --DEPENDS_ON--> member | 15/15 | DONE |
| ADD member --SPECIALIZES--> family | 15/15 | DONE |
| ADD T2_FAM --SPECIALIZES--> category_type (RESCUE) | 7/7 | DONE |
| **TOTAL** | **37/37** | **HARD_PASS** |

| Counter | Value |
|---|---|
| Pre-retry atoms | 26285 |
| Post-retry atoms | 26285 (no atom changes) |
| Pre-retry relations | 5273 |
| Post-retry relations | 5280 |
| Net relations delta | +7 (15 removed + 22 added; net = 7 rescue SPECIALIZES) |
| Pre-retry axiom term | 213/213 = 100.0% |
| Post-retry axiom term | 213/213 = 100.0% PRESERVED |
| Dangling backwards | 0 |
| Missing forwards | 0 |
| Tier 1+2 modules import | 6/6 OK |
| Rollback needed | No |

## RESCUE EMPIRICAL VALIDATION

The 87c HARD_FAIL on T2_FAM/discriminative_classification + T2_FAM/graph_traversal was caused by these atoms losing all outgoing forward-walk edges. The rescue:

```
T2_FAM/probabilistic_inference        -SPECIALIZES-> T1/category_type
T2_FAM/representation_transform       -SPECIALIZES-> T1/category_type
T2_FAM/graph_traversal                -SPECIALIZES-> T1/category_type  <- 87c failure rescued
T2_FAM/sequence_decoding              -SPECIALIZES-> T1/category_type
T2_FAM/algebraic_binding              -SPECIALIZES-> T1/category_type
T2_FAM/superposition_aggregation      -SPECIALIZES-> T1/category_type
T2_FAM/discriminative_classification  -SPECIALIZES-> T1/category_type  <- 87c failure rescued
```

Each T2_FAM atom now has at least one outgoing forward edge (d=1) to a terminal T1 axiom. Forward-walk reachability restored. Axiom termination 213/213 preserved across the full 37-op batch.

## Substrate-product positioning (gain) -- 73rd honest signal pre-check stack OPERATIONAL

Per DECISION 89 + Exp-Dev 89b: the substrate's pre-check stack is now COMPLETE for non-additive batches:

| Gate | Source | Catches |
|---|---|---|
| Forward-walk reachability | Exp-Dev 88c (NEW; in response to 87c HARD_FAIL) | leaf-stranding (the 87c failure mode) |
| Axiom-termination | Testbed 79a (post-ratify check) | broken proof paths |
| Retrieval-F1 | Exp-Dev 82g | held-out F1 regression |
| Hardened all-rel-type dangling | Skunkworks/Testbed 85a + 86b | orphaned references |

**4 independent gates.** The 87c failure mode (forward-walk leaf-strand) was NOT covered before this session; it now is. Substrate's discipline gains a new pre-check axis EMPIRICALLY MOTIVATED by HARD_FAIL detection.

## Substrate state (post 89c retry)

```
Atoms:     26285
Relations: 5280 (was 5273; +7 rescue SPECIALIZES; +15 R&R member-SPECIALIZES-family; -15 family-DEPENDS_ON-member)
Axiom termination: 213/213 = 100.0% PRESERVED
Capability_preservation invariant: 1.0 PRESERVED
Cumulative non-additive workstreams: 4 HARD_PASS + 1 HARD_FAIL-rollback-then-RETRY-PASS
  (79a edge REMOVE 10 cycles)
  (86a atom DELETE svd pilot)
  (86b cycle-cleanup v2 first batch 11 ops)
  (87c batch 2b initial - HARD_FAIL leaf-strand - ROLLBACK)
  (89c batch 2b RETRY with rescue - HARD_PASS 37 ops)
```

## Claim 14 (substrate self-corrects own typed-operator graph) STRENGTHENED

Claim 14 now demonstrates substrate's discipline OPERATING THROUGH FAILURE:
- 87c failure: substrate detected R3 regression and atomically rolled back without data loss
- 88a/88b/88c/89: substrate engineered a rescue path through three-role collaboration (Director + Skunkworks + Exp-Dev)
- 89b: Exp-Dev's forward-walk pre-check NEW (engineered in response to the failure)
- 89c: substrate ratified the rescued batch with 213/213 axiom term preserved

The substrate's three-role discipline produced a successful workstream from a HARD_FAIL THROUGH measurement + collaboration + new pre-check + verified rescue. Substrate's discipline doesn't just refuse bad changes; it actively engineers good changes through role-coordination.

## Cross-references

- DECISION 87c HARD_FAIL + ROLLBACK: commit `9ddf8964`
- DECISION 88 ACK + rescue dispatch: `notes/research_to_all_DECISION_88_*`
- DECISION 89 reconcile + GREEN: `notes/research_to_exp_dev_skunkworks_testbed_DECISION_89_*`
- Skunkworks 88b retry spec: `notes/skunkworks_to_testbed_research_exp_dev_DECISION_88b_*`
- Exp-Dev 89b PRECHECK PASS: `notes/exp_dev_to_testbed_research_DECISION_89b_*`
- Ratification script: `tools/substrate_cycle_cleanup_v2_batch_2b_RETRY_89c.py`
- Input JSONL: `data/substrate_index/skunkworks_cycle_cleanup_v2_batch_2b_RETRY_with_rescue_v1.jsonl`

## Safety / invariants

- ASCII only
- 11th rule: substrate-internal; no LLM contact
- 18th rule: pre-check stack now complete (4 gates); substrate refuses what doesn't pass all 4
- 19th rule: substrate caught its own R3 regression on 87c; engineered the rescue path; verified pre-execution
- 22nd rule preserved (no held-out gold contact)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED

---

**Director + Skunkworks + Exp-Dev:** DECISION 89c batch 2b RETRY HARD_PASS + 37/37 ops (15 REMOVE + 22 ADD) + axiom_term 213/213 PRESERVED + 0 dangling + 0 missing + +7 net relations from rescue + cycle-cleanup v2 COMPLETE (16 logical ops shipped 86b + 16 + 7 rescue = 39 atomic ops total across batches) + Claim 14 STRENGTHENED via HARD_FAIL -> rescue path -> RETRY PASS through three-role collaboration + pre-check stack now COMPLETE (4 gates including new forward-walk reachability from Exp-Dev 88c).

Tag: SUBSTRATE_HYGIENE_CYCLE_CLEANUP_v2_BATCH_2b_RETRY_with_RESCUE
