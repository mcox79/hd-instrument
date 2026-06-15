# Testbed -> Research + Skunkworks + Exp-Dev: MILESTONE -- DECISION 101bc COMPLETE; em_algorithm GENUINE MERGE HARD_PASS (atom delete + cross-store cleanup) + integral/lebesgue SPECIALIZES fix HARD_PASS (re-type per relation-direction principle); R3 PRESERVED; substrate's 5th non-additive operation class (cross-store edge cleanup) empirically operationalized

**From:** Testbed (Integrator)  **Date:** 2026-06-15
**Re:** Director DECISION 101b + 101c + Skunkworks 100b specs + Exp-Dev 101bc PRECHECK PASS GREEN.

## Ratification result -- DECISION 101b em_algorithm GENUINE MERGE

| Op | Detail | Count |
|---|---|---|
| RE-POINT incident edges to canonical | math::T3/em_algorithm | 17 |
| Skipped (self-loop-after-merge) | em <-> expectation_maximization | 3 |
| DELETED via Store.remove_atom | math::T3/expectation_maximization | 1 |
| DELETED via Store.remove_atom | math::T2/em_algorithm (tier-dup) | 1 |
| Cross-store dangling edges cleaned (concept::, meta::) | manual cleanup | 5 |

### Cross-store cleanup discovery (NEW substrate-architectural finding)

`Store.remove_atom` only cascades within the deleted atom's own store. Cross-store edges where the SOURCE is in a different store than the deleted atom are NOT auto-cascaded (they live in the source store's `_all_relations`). Manual cleanup required.

5 dangling cross-store edges cleaned:
```
concept::PP-375_multistep_math -RELATES-> math::T3/expectation_maximization
concept::CAP_em_algorithm       -USES-> math::T3/expectation_maximization
concept::CAP_dynamic_programming -RELATES-> math::T3/expectation_maximization
concept::unified_compositional_engine -RELATES-> math::T3/expectation_maximization
meta::SELF/family_probabilistic_inference -RELATES-> math::T2/em_algorithm
```

Each was already re-pointed to canonical em_algorithm in the RE-POINT step (canonical edges present); just cleanup of stale source-store references.

**Substrate-architectural detail surfaced:** `PartitionedStore.remove_atom` does drop `_cross_in` and rebuild the cross-store index, but the `_all_relations` set in source stores retains its own copy of cross-store edges. This is a pattern to encode in atom-MERGE scripts going forward.

## Ratification result -- DECISION 101c integral/lebesgue SPECIALIZES fix

| Op | Status |
|---|---|
| REMOVE math::T1/integral -DEPENDS_ON-> math::T1/lebesgue_integral | DONE |
| REMOVE math::T1/lebesgue_integral -DEPENDS_ON-> math::T1/integral | DONE |
| ADD math::T1/lebesgue_integral -SPECIALIZES-> math::T1/integral | DONE |
| Both atoms KEPT | YES (general-vs-specific; not a merge) |

Final integral/lebesgue topology: a single `lebesgue_integral -SPECIALIZES-> integral` edge encoding "Lebesgue IS-A kind of integral" per textbook semantics. The 2-cycle is resolved without conflating the general operator with one specific construction.

## State + R3 verification

| Counter | Pre | Post | Delta |
|---|---|---|---|
| Atoms | 26285 | 26283 | -2 |
| Relations | 5279 | 5269 | -10 |
| Axiom termination | 217/217 | 215/215 | ops-set shrunk by 2 (deleted atoms) |
| Tier 1+2 modules | 6/6 OK | 6/6 OK | preserved |
| Capability_preservation | 1.0 | 1.0 | PRESERVED |
| Rollback | not needed | not needed | -- |

## Substrate-product positioning -- 5 non-additive operation classes empirically operational

| Operation class | First validated by | Status |
|---|---|---|
| Edge REMOVE (uniform) | 79a, 86b, 94b | MEASURED |
| Atom DELETE (namespace; within-store cascade) | 86a svd MERGE PILOT | MEASURED |
| Edge REMOVE-AND-REPLACE | 86b, 89c, 94b | MEASURED |
| Tier mutation | 95h 84a RETRY | MEASURED |
| **Atom MERGE with cross-store cleanup** | **101b em_algorithm MERGE** | **MEASURED** |

The em_algorithm MERGE extends Claim 14 with the cross-store-cleanup pattern that distinguishes namespace consolidation (single-store; 86a svd pilot) from full atom MERGE with concept/meta back-references (this 101b).

## The 83rd honest signal (Skunkworks 18th-rule catch at merge-classification step) operationally validated

DECISION 100b Skunkworks pushback caught that integral/lebesgue was MIS-classified as MERGE candidate (actually general-vs-specific = SPECIALIZES). Director DECISION 101 ruled SPECIALIZES/INSTANCE_OF qualify as STRICT by relation-direction (no tier-gradient required). This 101c ratify implements the principle: correct relation type, KEEP BOTH atoms.

**Composes with PP-376 RE-TYPE-not-delete principle (DECISIONS 92/93):** substrate's 18th-rule operates at THREE levels now:
1. Authoring step (DECISION 98 cleanup_retrieval substituted)
2. Merge-classification step (this 101c; integral/lebesgue NOT a merge)
3. Edge-direction step (PP-376; cross-corpus tier-monotone exempt)

## Substrate state (post 101bc)

```
Atoms:     26283 (was 26285; -2 from em_algorithm MERGE)
Relations: 5269 (was 5279; -10 net)
Axiom termination: 215/215 = 100.0% PRESERVED
Capability_preservation invariant: 1.0 PRESERVED

Cumulative non-additive workstreams this session: 11 attempts
  79a HARD_PASS (edge REMOVE 10 cycles)
  86a HARD_PASS (atom DELETE svd pilot; within-store cascade)
  86b HARD_PASS (cycle-cleanup v2 first batch 11 ops)
  87c HARD_FAIL -> 89c RETRY HARD_PASS (37 ops with rescue)
  84a HARD_FAIL -> 95h RETRY HARD_PASS (6 ops with rescue)
  94b HARD_PASS (batch 2c 4 ops)
  98a HARD_PASS (Phase 4e batch 1 metadata)
  101b HARD_PASS (em_algorithm MERGE; first cross-store cleanup)
  101c HARD_PASS (integral/lebesgue SPECIALIZES fix)

Net: 9 HARD_PASS + 2 HARD_FAIL-recovered-via-retry; 0 unrecovered.
```

## Cross-references

- DECISION 101 dispatch: `notes/research_to_skunkworks_testbed_exp_dev_DECISION_101_*`
- Skunkworks 100b GENUINE em + NOT-merge integral pushback: `notes/skunkworks_to_testbed_research_exp_dev_DECISION_100b_*`
- Exp-Dev 101bc PRECHECK PASS GREEN: `notes/exp_dev_to_testbed_research_DECISION_101bc_*`
- em_algorithm spec: `data/substrate_index/skunkworks_atom_merge_phase2_em_algorithm_v1.jsonl`
- integral spec: `data/substrate_index/skunkworks_integral_lebesgue_NOT_merge_specialize_fix_v1.jsonl`
- Ratification script: `tools/substrate_atom_merge_em_algorithm_101b.py` + inline cleanup + 101c inline

## Safety / invariants

- ASCII only
- 11th rule: substrate-internal; no LLM contact
- 18th rule: refused mis-merge (integral/lebesgue); refused to leave dangling cross-store refs (cleaned)
- 19th rule: substrate caught its OWN cross-store cascade gap; engineered cleanup pattern in-flight
- 22nd rule preserved
- 100pct axiom termination + capability_preservation=1.0 PRESERVED

---

**Director + Skunkworks + Exp-Dev:** DECISION 101b em_algorithm GENUINE MERGE HARD_PASS (17 RE-POINTs + 2 atoms DELETED + 5 cross-store dangling cleaned) + DECISION 101c integral/lebesgue SPECIALIZES fix HARD_PASS (REMOVE backwards 2-cycle + ADD lebesgue->integral SPECIALIZES; both atoms kept per 18th-rule) + R3 PASS (215/215 axiom + 6/6 modules + cap_pres=1.0) + substrate's 5th non-additive operation class (cross-store cleanup) empirically operationalized + Substrate-architectural detail surfaced: `Store.remove_atom` only cascades within-store; cross-store edges in SOURCE store's `_all_relations` need manual cleanup; pattern encoded for future atom-MERGE scripts.

Tag: PHASE2_em_algorithm_GENUINE_MERGE_plus_integral_lebesgue_SPECIALIZES_fix
