# Exp-Dev -> Research: ColBERT MaxSim proxy INCONCLUSIVE (raw checkpoint != ColBERT-v2); needs ragatouille

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** colbert_pretest_authorize #1

Built a brute-force MaxSim proxy (colbert-ir/colbertv2.0 raw token embeddings, no Ragatouille index needed for per-question
candidate sets). Smoke n=40: recall@2hop=0.150, recall@10=0.625.

## Read: this proxy is NOT a valid ColBERT-v2 test -- DO NOT gate on it
recall@2=0.15 is well BELOW bge-small (0.42); a real late-interaction model should at least match bge on coverage. The
proxy is missing the machinery that DEFINES ColBERT-v2:
- the 128-dim linear projection head (raw 768-d BERT hidden states are not the ColBERT representation)
- [Q]/[D] prefix markers + query augmentation (mask-token padding)
- proper normalization/scoring as trained
Without those, MaxSim on raw hidden states is meaningless. The 0.15 reflects the broken proxy, not ColBERT's capability.

## Recommendation
The gating decision (worth the 2-3wk ColBERT integration?) requires the PROPER stack: install ragatouille (+ colbert-ir),
build the ColBERT-v2 index on HotpotQA passages, measure recall@2/@10. That's a dependency-install + index-build (~2-3hr
GPU as you scoped). I did not install ragatouille unauthorized (new dep on the runner). Two options:
1. Authorize the ragatouille install -> I build the real ColBERT-v2 pretest.
2. Treat ColBERT as deferred and lean on the BM25+bge RRF hybrid (pretest #2, cheap, no new heavy dep) for the floor-lift
   question first; if RRF gets close, ColBERT may be unnecessary.
Recommend option 2 first (cheaper, no install), then ColBERT only if RRF stalls. The queued colbert_maxsim_hotpot_v1 should
be read as "proxy invalid" not "ColBERT failed". Awaiting your call on ragatouille.
