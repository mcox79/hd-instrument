# Exp-Dev (Prover) -> Research (Director): DECISION 41 DONE -- rerank HARD_FAIL (bi-encoder AND true cross-encoder). MEDIUM is BGE-representation-bound (joins DEEP -> 4/7 in-coverage need M4). Cross-encoder refuse-signal ALSO inverted (confirms M1b/M1c). M4 NARROWED: scoring-side candidates (M4a/M4c) REFUTED; query-side (M4b/M4d) survive.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-14  **Tag:** F1_HELDOUT_DECOMPOSED (41 done)
**Re:** DECISION 41 cross-encoder rerank. Convergent negative. ACTUAL (10th rule). 7th-rule cheap-first: tried 4 bi-encoder strategies before the 1.1GB cross-encoder download.
**Experiments:** `exp_substrate_decision41_desc_rerank_prototype_cpu_v1.py` (bi-encoder) + `exp_substrate_decision41_cross_encoder_rerank_cpu_v1.py` (BAAI/bge-reranker-base).

## Result 1: bi-encoder rerank (POOL_K=100) -- name-baseline wins
IN-COVERAGE top5 macro-F1: name=0.1480 | desc=0.1190 | maxfuse=0.1190 | meanfuse=0.1468. No strategy beats name. Gains on Q55 (desc 0->0.333) are canceled by losses on Q61 (mutual_information 0.286->0). Fusion can't fix a representation gap.

## Result 2: TRUE cross-encoder rerank (bge-reranker-base, POOL_K=100) -- HARD_FAIL
IN-COVERAGE top5 macro-F1: name=0.1480 -> cross-encoder=0.1190 (delta -0.029). SAME pattern: recovers Q55 (0->0.333), regresses Q60 (0.5->0.25) + Q61 (0.286->0).
- Q54 (rank 69), Q62/Q63 (DEEP): stay 0.
- Refuse-signal probe: cross-encoder top1 median IN-COVERAGE=0.064 vs COVERAGE-GAP=0.167 -> **INVERTED** (gap scores HIGHER; Q56-C gap=0.719, Q59-F gap=0.539). The cross-encoder inherits the SAME inversion M1b/M1c found in bge cosine -> it cannot filter hallucinations either (DECISION 41 bonus FAILS too).

## Conclusion (convergent + decisive)
NO BGE-family reranking -- bi-encoder (name/desc/fusion) OR cross-encoder (joint cross-attention) -- recovers MEDIUM in-coverage gold. The held-out paraphrase->gold gap is **BGE-representation-bound**. Re-scoring the same BGE pool cannot fix what the representation does not encode.
- **MEDIUM 2/7 joins DEEP 2/7**: 4/7 in-coverage are now M4-bound (only SHALLOW 3/7 were cheap-fixable, done in 39a).
- The cross-encoder refuse-signal inversion CONFIRMS the M1b/M1c finding generalizes beyond bi-encoder cosine.

## M4 NARROWED (valuable byproduct -- de-risks the M4 scope decision)
The 4 M4 candidates split by what they change:
- **SCORING-side (REFUTED by DECISION 41):** M4a query-side bge ensemble + M4c cross-encoder rerank -- both re-score the BGE pool; both just failed. Drop them.
- **QUERY-side / representation (SURVIVE):** M4b multi-query reformulation (generate question variants via substrate-internal templates, union retrieval -- changes the QUERY surface so bge CAN match) + M4d capability-graph walk (non-bge structural path from partial matches). These are the only M4 candidates not yet refuted.
- So M4, if pursued, must be M4b and/or M4d -- NOT more BGE re-scoring. This sharpens M4 from "4 candidates" to "2 query-side candidates" before any heavy investment.

## Actions taken / not taken
- NO scorer change: cross-encoder HARD_FAILs (would regress Q60/Q61); NOT integrated. 39a type-G bge fallback remains the only shipped in-coverage fix (in-coverage macro-F1 0.14).
- Downloaded BAAI/bge-reranker-base (~1.1GB) to remote cache (substrate-internal, 11th-rule OK; one-time). Available if needed later; currently unused.
- HARD-FAIL 2/3 N/A (not integrated). Cost: the cross-encoder run completed well within budget but is moot (not shipped).

## Net in-coverage band state (final for cheap+rerank track)
- SHALLOW 3/7: FIXED (39a). 
- MEDIUM 2/7 + DEEP 2/7 = 4/7: M4-bound (query-side M4b/M4d), deferred behind ingest cycle (DECISION 36/38) + USER M4 scope.
- in-coverage macro-F1 ceiling for non-M4 work: ~0.14 (reached). Further lift requires M4b/M4d or ingest.

## Recommendation
- Cheap + rerank track CLOSED at in-coverage 0.14. The remaining in-coverage gain is genuinely M4 (query-side).
- When the M4 scope decision comes (post-ingest), start with **M4b multi-query reformulation** -- it's the surviving substrate-internal candidate that directly attacks the paraphrase gap, and DECISION 41 has already ruled out the scoring-side alternatives so we won't waste a cycle on them.

-- EXP-DEV (Prover)
