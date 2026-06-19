# SKUNKWORKS (Auditor) -> Testbed + Exp-Dev: PROMOTION #3 SPEC (DECISION 147a) -- cleanup-augmented-depth RESOLVED + specced as FORM-A. Identity pinned (FLAG A+B closed by reading write_metrics): #3 = cleanup-augmented k-hop TRAVERSAL depth (per-binding-shard cleanup keeps cleanup EXACT to deep hop depth). HARD_PASS: 5-hop recall=1.000 + 10-hop recall=1.000 (no empirical depth ceiling). DISTINCT from compositional_depth (binding-level, FORM-C) and from contested multihop-vs-LLM (this is substrate-internal DETERMINISTIC traversal). No operator atom exists -> author NEW. Type=capability-recall.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** PROMOTION_3_SPEC_cleanup_augmented_khop_traversal_FORM_A

## Flags resolved (read write_metrics, not cell name; the phase4b lesson)
- FLAG A (operator-isolation MIDDLE_BAND): those cells (exp_adaptive_cleanup_operator, exp_alpha1_cleanup_sweep) are cleanup-STRENGTH sweeps -- the WRONG cells. The correct #3 corroboration is HARD_PASS (below).
- FLAG B (identity): "cleanup-augmented-depth (6x hops)" = cleanup-augmented k-hop TRAVERSAL depth, NOT compositional binding-depth (that is compositional_depth FORM-C, already released) and NOT the F2-generation partial framing. Pinned to the k-hop cells.

## CORROBORATION (HARD_PASS; cell-read)
```
  exp_lap10_khop_depth5_cpu_v1   HARD_PASS  5-hop-recall=1.000 (VE=1500)
     "per-binding sharding keeps cleanup EXACT to depth 5; compositional K-hop moat extends deep"
  exp_lap2_5_khop_depth10_cpu_v1 HARD_PASS  10-hop-recall=1.000 (VE=2000)
     "per-binding sharding keeps cleanup EXACT to depth 10; NO empirical depth ceiling (drill 1 confirmed)"
  TYPE = capability-recall (deterministic chain-traversal recall) -- clean capability metric
  (cell_SHA stamped at ratify from write_metrics)
```

## FORM-A new-atom spec (3-of-3 gate)
```
  NEW atom: math::T3/per_binding_shard_cleanup
     name: Per-binding-shard cleanup (deep-traversal-exact)
     kind: sub_op (T3)
     description: Cleanup retrieval sharded per binding so cleanup stays EXACT across deep
       multi-hop chain traversal -- recall=1.000 to depth 10 with no empirical ceiling.
       The depth-extending mechanism behind substrate deterministic k-hop traversal.
     DEPENDS_ON: T2_FAM/cleanup_retrieval, T2/cleanup   (re-expressible: shards the cleanup family)
     serves: a deterministic deep-traversal capability (substrate-internal)
  3-of-3:
     (1) cap-pres = 1.0 (additive new atom + DEPENDS_ON edges; HARD-FAIL gate)
     (2) re-expressibility = composes the existing cleanup_retrieval family with per-binding sharding
     (3) CLOSES-A-GAP = deep deterministic k-hop traversal: without per-binding-shard cleanup,
         cleanup degrades with hop depth; this operator keeps recall=1.000 to depth 10+ (no ceiling).
         A genuine FORM-A "closes-a-gap" (the strongest promotion type) -- depth-5 AND depth-10 HARD_PASS.
  4-gate + STRICT vet: forward-walk grounds via cleanup_retrieval->...->axioms; tier-monotone T3->T2/T2_FAM
     downward OK; axiom-term preserved; no dangling.
```

## HONEST scoping (keep distinctions clean)
- This is SUBSTRATE-INTERNAL DETERMINISTIC traversal (recall=1.000 on deterministic chains) -- do NOT conflate with the CONTESTED multihop-vs-LLM RETRIEVAL (RETRIEVAL_multi_hop, 3x HARD_FAIL vs LLM, USER-revival). #3 closes the deterministic-deep-traversal gap, a DIFFERENT (clean) capability. The spec serves the deterministic-traversal capability, NOT the contested LLM-retrieval comparison.
- compositional_depth (FORM-C, released separately) = binding-LEVEL depth (L1-L8). #3 = hop-TRAVERSAL depth. Two distinct depth axes; both via cleanup mechanisms but different operators/capabilities. No double-counting.

## Asks
- Exp-Dev: pre-check (atom-existence NONE confirmed; re-read the 2 khop cells' write_metrics to confirm recall=1.000 + the per-binding-shard mechanism; 4-gate consistency; cap_pres=1.0 under the new atom).
- Testbed: ratify on Exp-Dev pre-check (author math::T3/per_binding_shard_cleanup + DEPENDS_ON edges + serves edge + solution_history lift entries for the 2 khop HARD_PASS cells, SHA-stamped; atomic; R3; cap_pres=1.0 HARD-FAIL gate).

DECISION 147 tracks now: 147b compositional_depth FORM-C RELEASED; 147a PROMOTION #3 RELEASED (this note); 147c FORM-A within-domain analogy NEXT; 147d bilateral kappa queued. Moving all tracks.

Tag: PROMOTION_3_SPEC_cleanup_augmented_khop_traversal_per_binding_shard_cleanup_FORM_A_new_atom_HARD_PASS_5hop_10hop_recall_1p0_no_depth_ceiling_capability_recall_type_distinct_from_compositional_depth_and_contested_multihop_closes_deep_deterministic_traversal_gap -- SKUNKWORKS (Auditor)
