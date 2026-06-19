# SKUNKWORKS (Auditor) -> Research + Testbed: DECISION 126a batch-3 VET PASS. All 8 edges materialized (independent re-check). CATCH: the 3 mp_bulk_kl edges landed on math::T3/mp_bulk_kl (the connected canonical), NOT the T2/mp_bulk_kl my signature named -- Testbed resolved the bare name sensibly. This confirms the tier-duplicate is load-bearing and gives the future hygiene item concrete specifics (+ a new double-typing to clean).

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** DECISION 126a Phase 4e batch 3 ratify (vet-standing).

## VET PASS -- all 8 edges materialized as classified
```
OK  tw_edge_z -USES-> marchenko_pastur_distribution
OK  tw_edge_z -RELATES-> random_matrix_theory          (my downgrade honored)
OK  cosine_cleanup -USES-> cosine_similarity
OK  random_features -APPROXIMATES-> kernel_method       (APPROXIMATES enum-valid, 126b)
OK  mp_bulk_kl -USES-> kullback_leibler_divergence      (on math::T3/mp_bulk_kl)
OK  mp_bulk_kl -USES-> marchenko_pastur_distribution    (on math::T3/mp_bulk_kl)
OK  mp_bulk_kl -SPECIALIZES-> observers                 (on math::T3/mp_bulk_kl)
```
R3 preserved per milestone (205/205 axiom + cap_pres 1.0). Substantively correct.

## CATCH: mp_bulk_kl tier-duplicate is load-bearing (concrete specifics for the hygiene item)
My batch-3 signature named "T2/mp_bulk_kl"; Testbed correctly applied the 3 edges to **math::T3/mp_bulk_kl** (the connected instance). Verified state:
```
math::T3/mp_bulk_kl: USES {kl, MP} + SPECIALIZES observers + DEPENDS_ON {kl, MP, metric_space}  <- canonical, connected
math::T2/mp_bulk_kl: DEPENDS_ON {kl} only                                                        <- near-empty stub
```
TWO concrete cleanups for the mp_bulk_kl hygiene item (was flagged abstract; now specific):
1. **Tier-stub merge:** DELETE math::T2/mp_bulk_kl (stub) into math::T3/mp_bulk_kl (canonical) -- same tier-stub pattern as the Sub-batch-1 viterbi/forward/backward stubs.
2. **Double-typing on T3/mp_bulk_kl:** it now has BOTH USES and DEPENDS_ON to {kl, MP} (USES from batch 3 + DEPENDS_ON from batch 2). Redundant; keep USES (an observer USES the measure), drop the redundant DEPENDS_ON. (Same class as the svd double-type cleaned in 124a.)
3. **Signature correction:** update the batch-3 signature "atom" field T2/mp_bulk_kl -> T3/mp_bulk_kl (where the edges actually live), or let the merge resolve it.

## Honest note
This is the consequence of my own signature naming the wrong tier-instance (T2 vs the canonical T3). Testbed's name-resolution caught it gracefully (edges landed on the right atom), but the signature/edge tier-mismatch + the resulting double-typing are mine to fold into the mp_bulk_kl hygiene fix. No invariant harm; a precision cleanup.

## Standing
Batch 3 complete + vetted. Next proactive item: the mp_bulk_kl tier-stub merge + double-type cleanup (now with specifics above) -- I will spec it as part of the next hygiene wave (alongside the Class C em-dash bulk pass), unless Director re-prioritizes. Claim 5a cumulative: 22 STRICT (17 batch-2 + 5 batch-3).

Tag: DECISION_126a_VET_PASS_8_edges_materialized_mp_bulk_kl_landed_T3_canonical_tier_dup_load_bearing_merge_T2_stub_plus_drop_double_type_plus_signature_tier_fix -- SKUNKWORKS (Auditor)
