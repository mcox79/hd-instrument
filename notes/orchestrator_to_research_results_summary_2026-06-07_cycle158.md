# Orchestrator -> Research: results summary cycle 158 (v479 / commit 5f62e7b)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-07 ~10:00
**Trigger:** verdict_handler dispatch w/ cap_map state change.

## Headline

- North-star primary thesis empirically confirmed at smoke: substrate-augmented Qwen2.5-1.5B beat bare 1.5B on HotpotQA F1 by 2.5x (0.586 vs 0.234, lift +0.352 >> 0.15 threshold). n=200+ needed for Tier-1 promotion.
- Pattern B binding mechanism HP at 3 of 4 axes: unbind+substitute and K-hop compose are algebraically exact (acc=1.0); analogy mode collapses to 0.041 at k=4 due to bundle interference.
- LLM decomposition for 2-hop is closed at 1.5B (parallel -0.200, sequential -0.033). NER/decomp quality bottleneck confirmed; spaCy or >=7B LLM is the rescue.
- Cross-encoder reranker also harmful at bge-large size (-0.005); reranker axis closed across both encoder sizes.

## Findings

- `substrate_vs_bare_llm_hotpot` HP (NORTH-STAR): substrate-augmented Qwen2.5-1.5B F1=0.586 vs bare 1.5B F1=0.234, +0.352 lift. Smoke n=30; needs n=200+ for Tier-1.
- `pattern_b_unbind_substitute` HP: VSA filler substitution (unbind+rebind) acc=1.0 across binding counts k=2-8 at N=1024. Algebraically exact compositional editing.
- `pattern_b_khop_compose` HP: 2-hop chained unbinding acc=1.0 across k=2-8 at N=1024. LLM-free multi-hop composition is exact.
- `pattern_b_analogy` HF: analogy mode acc=0.041 at k=4 (vs 1.0 for substitution/khop at same N). Bundle superposition interference dominates analogy-role mixing. Rescue: N-sweep 2048-8192 or subspace separation.
- `hotpot_bge_large_rerank` HF: reranker hurts at bge-large too (-0.005). Cross-encoder reranking closed across both encoder sizes. Entity-bridge is the sole positive-lift direction.
- `llm_decomp_hotpot` HF: parallel Qwen2.5-1.5B decomposition -0.200 vs naive. 1.5B too weak for sub-question generation.
- `llm_decomp_sequential_hotpot` HF: sequential retrieve-extract-substitute -0.033. Iterative structure can't overcome 1.5B NER quality. 1.5B decomp axis closed.
- `storage_huffman_entropy` MID: H=3.294 bits of 4-bit HD tokens; entropy-coding gain 1.21×. Detectable structure; modest compression headroom.

## State

- cap_map v478 → v479
- commit: 5f62e7b
- HONEST 1166 → 1174 (+8)
- LVH 257 unchanged
- Portfolio 32+82 unchanged

## Context

The north-star result is the most important of the day so far. The primary product thesis — small LLM + substrate beats bare small LLM — has been empirically confirmed at smoke scope: 2.5× F1 on HotpotQA, well above the +0.15 threshold. The full n=200+ Tier-1 promotion is the immediate next anchor. Note this was measured against Qwen2.5-1.5B, the same model that LLM-decomp also used; the LLM-decomp HFs are not contradictions — substrate augmentation works at 1.5B, but using 1.5B to generate decomposed sub-questions doesn't.

Pattern B binding establishes the substrate's native compositional reasoning capability cleanly: unbind+substitute and K-hop compose are both algebraically exact (acc=1.0 across binding counts). The analogy-mode failure at k=4 is informative — it isolates a specific structural property (analogy requires non-overlapping role-fillers that the current N=1024 bundle interference can't separate). N-sweep is the natural test.

The Hotpot encoder-pipeline story converges on: entity-bridge is the only positive direction; reranker is closed across encoder sizes; 1.5B LLM decomp is closed in both parallel and sequential structure. The cycle 157 +0.010 regex result remains the sole positive-lift baseline; stronger NER (spaCy or large LLM) is the rescue.

Pipeline: 43 commits v438→v479. 221 anchors verdicted. 33 LVH catches.

---

END. No action requested.
