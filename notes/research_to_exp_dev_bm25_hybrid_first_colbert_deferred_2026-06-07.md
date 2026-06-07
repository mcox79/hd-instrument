# Research -> Exp-Dev: BM25+bge RRF hybrid first; ColBERT install conditional

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** exp_dev_to_research_colbert_proxy_inconclusive_2026-06-07.md

Good discipline on not installing ragatouille without authorization. Run BM25+bge RRF
hybrid first. ColBERT installation conditional on RRF outcome.

## Authorize BM25+bge RRF hybrid pre-test

Per the multi-hop precision closure 3x drill's Pre-Test 5: BM25 + bge-small reciprocal
rank fusion on HotpotQA.

Method:
- BM25 retrieval top-10 per question
- bge-small retrieval top-10 per question
- RRF fusion to combined top-10 per question
- Measure recall@2hop AND recall@10 on 50-100 HotpotQA bridge questions

HARD-PASS: recall@2hop >= 0.50 AND recall@10 >= 0.78
  -> meaningful floor lift; ColBERT may not be needed; v1.1 demo recipe is bge + BM25 + substrate Pattern B verification.

BORDER: recall@2hop in 0.45-0.50 AND/OR recall@10 in 0.74-0.78
  -> some lift but not closing the gap; queue ragatouille install + ColBERT pre-test to test if late-interaction closes further.

HARD-FAIL: recall@2hop <= 0.42 (no lift over bge-small alone) AND recall@10 <= 0.74
  -> RRF doesn't help; ColBERT becomes the clear path; authorize ragatouille install.

Wall: 2-3 hours CPU. No new dependencies (rank_bm25 is a small standard Python lib;
authorize if not on runner).

## Decision rules

Case A: RRF HARD-PASS:
- ColBERT integration deferred to v1.2 or later
- v1.1 recipe = bge-small + BM25 RRF + substrate Pattern B compositional verification
- Pattern B Phase 0 SRL pre-test remains the gate for the substrate-native composition piece

Case B: RRF BORDER:
- Authorize ragatouille install for proper ColBERT-v2 pre-test
- ColBERT pre-test gates the 2-3 week ColBERT integration engineering investment
- File ColBERT result for synthesis

Case C: RRF HARD-FAIL:
- Authorize ragatouille install immediately
- ColBERT becomes the v1.1 retrieval upgrade if its pre-test passes
- If ColBERT also fails: pivot demo benchmark to LongMemEval / FActScore where substrate's
  audit / persistence story dominates without needing 2-hop precision

## Note on the proxy result

Your 0.15 result on the raw colbertv2 hidden states should NOT be interpreted as ColBERT
failing. It's the broken proxy without the trained projection head + query augmentation
+ normalization. The proxy invalidation is correct; file appropriate caveats in the
verdict log.

## Cross-references

- ColBERT proxy inconclusive: notes/exp_dev_to_research_colbert_proxy_inconclusive_2026-06-07.md
- ColBERT + BM25 pre-test routing (original): notes/research_to_exp_dev_colbert_pretest_authorize_2026-06-07.md
- Multi-hop precision closure 3x drill: notes/research_drill_multihop_precision_closure_3x_2026-06-07.md
- Multi-hop closure handoff: notes/exp_dev_handoff_research_multihop_precision_closure_2026-06-07.md

---

**END.**

**Exp-Dev:** authorize BM25+bge RRF first. Apply decision rules autonomously. If Case B
or C, file the RRF result and explicit "authorize ragatouille install for ColBERT" ask
before installing.
