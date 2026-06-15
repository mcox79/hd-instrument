# Research (Director) -> Testbed (Integrator): DECISION 87c GREEN -- batch 2b spec delivered; 15 family edges all UNIFORM REMOVE-AND-REPLACE (remove DEPENDS_ON + add SPECIALIZES; KEEP existing USES); 0 flagged as non-applying; substrate-product positioning gains "multiple-family membership" detail (backward_algorithm under both probabilistic_inference AND sequence_decoding); proceed atomic per edge

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~12:05
**Re:** Skunkworks DECISION 87b consolidated JSONL (commit pending).

## ACK -- Skunkworks 87b: 15 edges, 0 flagged, uniform pattern

```
Pattern (uniform across all 15):
  REMOVE: family --DEPENDS_ON--> member  (backwards)
  ADD:    member --SPECIALIZES--> family  (correct abstraction)
  KEEP:   family --USES--> member  (legitimate dispatch semantic; if exists)

0 SIMPLE-REMOVE cases (no SPECIALIZES-already-exists skips)
0 flagged as non-applying (every member textbook-confirms as instance)
```

**Substrate-architectural detail surfaced:** `backward_algorithm` appears under TWO families (`probabilistic_inference` AND `sequence_decoding`). Both valid (DP sequence decoder used in inference). Gets 2 SPECIALIZES edges (multiple-family membership; correct, not a conflict).

**Substrate-product positioning addition:** "Substrate's typed-operator graph supports MULTIPLE-FAMILY MEMBERSHIP via multiple SPECIALIZES edges -- an atom can specialize from multiple families when it genuinely belongs in each. backward_algorithm is the witness case: it specializes from both probabilistic_inference (as a DP-style inference method) and sequence_decoding (as a backward-pass DP algorithm)."

## DECISION 87c -- GREEN to execute (Testbed)

```
Spec: data/substrate_index/skunkworks_cycle_cleanup_v2_batch_2b_15_family_edges.jsonl

Per edge atomic operation:
  REMOVE family --DEPENDS_ON--> member
  ADD member --SPECIALIZES--> family
  LEAVE family --USES--> member untouched

R3 invariant per edge:
  capability_preservation = 1.0
  axiom_termination 213/213
  Tier 1+2 modules import OK
ROLLBACK on ANY regression

Dangling scan: use HARDENED all-rel-type scan (per the svd SUPERSEDED_BY catch)
to confirm no orphaned references post-batch.

Tag: SUBSTRATE_HYGIENE_CYCLE_CLEANUP_v2_BATCH_2b

Expected net effect: -15 DEPENDS_ON + 15 SPECIALIZES = ~net 0 relation count;
                     cycles reduced by 15.
```

## DECISION 87d -- Substrate's source-of-truth observation

Skunkworks notes: "These adds are the SAME relationships my Phase-4a self-model family entries encode (members_specialize) -> **the self-model is the source of truth**; this cleanup makes them explicit edges in the correct direction."

**Substrate-product positioning consolidates:**
- Phase 4a self-model (DECISION 68b/82a; 100 signatures) encodes implicit relationships via `members_specialize` lists
- Cycle-cleanup v2 batch 2b makes these IMPLICIT relationships EXPLICIT as substrate edges
- The self-model + cleanup-v2 composition realizes substrate's self-knowledge as substrate's actual graph structure

This is exactly the Level-2 enabling-machinery work USER described in DECISION 68: substrate's self-model BECOMES substrate's structure (via sound discipline; CHTV + Auditor vet + Testbed atomic ratify + capability_preservation).

## Substrate state preview (post 87c)

```
Atoms:     26285 (unchanged)
Relations: ~5273 (current; cleanup-v2 batch 2b nets ~0)
Cumulative non-additive workstreams completed: 4 (79a + 86a + 86b + 87c when shipped)
```

## Session tally

85 cumulative decisions. **70 honest signals** (Skunkworks's 0-flagged + multiple-family-membership observation are substrate-architectural details, not new honest corrections).

## Cross-references

- Skunkworks 87b consolidated JSONL: this commit responds
- DECISION 87 (BATCH 2b authorized): commit `25850070`
- DECISION 82 (Phase 4a 100 signatures): commit `985b5cdf`
- Self-model source: `data/substrate_index/skunkworks_self_model_of_operators_v1.jsonl`

## Safety / invariants

- ASCII only
- 11th rule: cleanup substrate-internal; no LLM
- 18th rule: 0 flagged as non-applying; substrate proceeds only on uniformly-textbook-applicable edges
- 19th rule: Skunkworks self-validated against self-model source of truth
- 22nd rule preserved
- 100pct axiom termination + capability_preservation=1.0 expected (additive in net per Skunkworks analysis)

---

**Testbed (Integrator):** DECISION 87c GREEN to execute -- atomic per-edge REMOVE + ADD per `skunkworks_cycle_cleanup_v2_batch_2b_15_family_edges.jsonl`; HARDENED all-rel-type dangling scan; ~30-45 min.

Tag: 87c_GREEN_batch_2b_15_uniform_REMOVE_AND_REPLACE_self_model_source_of_truth -- Research (Director)
