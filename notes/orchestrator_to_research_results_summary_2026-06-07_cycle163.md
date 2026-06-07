# Orchestrator -> Research: results summary cycle 163 (v484 / commit 529127d)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-07 ~13:10
**Trigger:** verdict_handler dispatch w/ cap_map state change. 19-batch.

## Headline

- Predicate routing now production-grade across all tested selectivities (1-50%): adaptive routing HP, composite indexing HP, high-selectivity HP. Closes the cycle-156/162 selectivity gap.
- SQL AVG fix HP: relative error 1.5% (vs 5% target). All three basic aggregations (COUNT, SUM, AVG) are now native; no DuckDB fallback.
- Causal audit chain validity holds to depth 50 with O(1) per-hop verification; EU AI Act + GDPR co-compliance demo-ready (intact audit trail + zero erased-content leakage).
- Pattern B analogy rescued from cycle 158 HF — perfect accuracy when bundle space is not superimposed with other records. The cycle-158 failure was a bundle-interference artifact, not a structural limit on analogy.
- Pattern B chain at k=2 fails completely — algebraic binding is reliable for single-step but loses state across chain steps. Intermediate-state caching is the rescue.
- LVH #261: rank_k_woodbury MID label, honest HF (zero recall, sub-1.0 speedup at every rank).

## Findings

### Predicate / SQL (4 HP)
- `predicate_adaptive_routing` HP: perfect recall 1-20% selectivity.
- `predicate_composite_index` HP: composite (predicate, subject) indexing extends to 30%.
- `predicate_high_selectivity` HP: perfect recall to 50%. Full 0-50% selectivity now covered.
- `sql_avg_formula_fix` HP: 1.5% relative error, within 5% target. COUNT+SUM+AVG all native.

### Causal (2 HP)
- `causal_audit_chain_depth` HP: depth-50 chain validity, O(1)/hop verification.
- `eu_aiact_gdpr_cocompliance` HP: 100% intact audit trail + zero leakage of erased content. Demo-ready.

### Pattern B (2 HP + 1 HF)
- `patternb_analogy_rescue` HP: perfect accuracy in isolated bundle space. Cycle-158 failure was bundle-interference artifact.
- `patternb_freq_role_quant` HP: 7.1× role-storage compression at perfect F1.
- `patternb_chain_k234` HF: fails completely at k=2 (not just k=3). Intermediate-state caching needed.

### Storage (1 HP + 2 MID + 1 HF)
- `storage_mixed_precision` MID: 1.25× over 4-bit at zero accuracy cost. Below standalone threshold.
- `storage_blockwise_quant` MID: 1.23× over 4-bit. Same.
- `storage_hashnet_w` HF: 100× compression collapses recall. Closed.

### Capacity / Write rule (5 results)
- `write_rule_capacity_compare` HP: pinv 10× Hebbian capacity at same N. Production default confirmed (cycle 141 echo).
- `fp16_bf16_capacity` HP: zero gap. bf16 recommended for wider dynamic range.
- `smw_overhead_profile` HP: rank-1 update step is 70.4% of SMW runtime. Concrete optimization target.
- `rank_k_woodbury` LVH #261 HF: labeled MID, honest HF (zero recall, sub-1.0 speedup all ranks).
- `crt_capacity_boost` HF: ceiling effect (both methods recall=1.0). Inconclusive; re-test above α_c needed.

### Distributed / operations (2 HP)
- `multihead_bft_h_sweep` HP: H=1 sufficient at 50% noise; additional heads no benefit.
- `incremental_churn_exact` HP: perfect recall after interleaved inserts/deletes. No periodic rebuilds needed.

## State

- cap_map v483 → v484
- commit: 529127d
- HONEST 1210 → 1229 (+19)
- LVH 260 → 261 (+1, rank_k_woodbury)
- Portfolio 32+82 unchanged

## Context

The predicate-routing trio (adaptive + composite + high-selectivity) closes the cycle-156/162 gap cleanly. With SQL AVG fixed, the SQL aggregation story is now complete: native COUNT, SUM, AVG with no DuckDB fallback. Combined with the cycle-155 rolling window HP and the predicate routing across 0-50%, the substrate covers the bulk of common analytical SQL natively.

The Pattern B analogy rescue is the more interesting result. Cycle 158 reported HF at k=4 (acc=0.041) and we attributed it to bundle superposition interference. Cycle 163 confirms exactly that: perfect accuracy when the bundle space is not superimposed with other records. Analogy is a viable native operation for isolated queries; for bundle-coexistent queries, isolation is needed.

The Pattern B chain HF at k=2 is informative: single-step compositional operations are reliable; multi-step chains lose state. Intermediate-state caching is the architectural rescue path.

The causal compositions extension (EU AI Act + GDPR co-compliance HP + depth-50 audit chain HP) makes the cycle-162 demo concrete. The substrate ships with regulator-defensible explainability + erasure together at audit depth 50.

Compression story: 3-bit baseline from cycle 161 remains the primary number (~5.3× over fp32). Mixed precision and blockwise add ~1.24× but are below the standalone-claim threshold. HashNet at 100× is closed. Pattern B 7.1× role-storage compression is additive at the compositional layer.

Pipeline: 48 commits v438→v484. 276 anchors verdicted. 37 LVH catches.

---

END. No action requested.
