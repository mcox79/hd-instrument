# Exp-Dev -> Research: BM25+bge RRF -- marginal (helps r@10 +0.02, hurts r@2); RRF stalled -> ColBERT now indicated

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** bm25_hybrid_first_colbert_deferred (pretest #2)

BM25+bge RRF, HotpotQA, smoke n=50:
  bge alone:  r@2=0.420  r@10=0.740
  BM25 alone: r@2=0.160  r@10=0.620   (lexical weak on these short sentences)
  RRF fusion: r@2=0.260  r@10=0.760

## Read: RRF does not give the multi-hop floor lift
BM25 alone is weak (r@2=0.16) and DILUTES bge's strong r@2 under fusion (0.42 -> 0.26). It adds a sliver of r@10 coverage
(0.74 -> 0.76) -- the lexical signal catches a few exact-entity matches bge misses -- but nowhere near enough. RRF is not
the answer. Per your conditional ("ColBERT install conditional on RRF outcome"), RRF stalled -> **ColBERT-v2 (proper, via
ragatouille) is now the indicated next test** if multi-hop precision is still the goal. Awaiting your go on the ragatouille
install (the MaxSim proxy was invalid; the real index-based ColBERT-v2 is the only valid late-interaction test).
Note: tuning RRF weights (down-weight BM25) would recover bge's r@2 but then RRF ~ bge -- no net gain. The r@10=0.76 is the
honest ceiling of lexical+dense fusion here.
Queued: bm25_bge_rrf_hotpot_v1 (full n=200).
