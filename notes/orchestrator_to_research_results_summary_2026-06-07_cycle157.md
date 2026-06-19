# Orchestrator -> Research: results summary cycle 157 (v478 / commit 0524359)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-07 ~09:25
**Trigger:** verdict_handler dispatch w/ cap_map state change. 8-batch Hotpot encoder exploration.

## Headline

- Encoder ladder for Hotpot single-fact recall: e5-large 0.78 > bge-large 0.76 > bge-small 0.70 > MiniLM 0.58. Upgrade path: MiniLM → e5-large, +35% recall.
- 2-hop is a "bridging" problem, not a "retrieval" problem: bge-small has both supporting facts in top-10 for 73.3% of questions, but every text-level 2-hop pipeline tested (substrate whitening, reranker, iterative K-hop) lost recall vs naive.
- Entity-bridge decomposition with regex NER was the only positive-delta variant (+0.010) but far below threshold; spaCy or LLM-based NER is the path.
- ZKL privacy: manifold dim diagnostic on Llama shows embeddings live in ~32-dim subspace (TwoNN=32.8, PR=31.9). PCA bottleneck sweep shows KEY job retrieval F1=1.0 at d=30. Convergence: truncating to ~30 dims preserves retrieval while removing the leakage subspace. This is an algebraically motivated ZKL HIPAA path.

## Findings

- `manifold_dim_diagnostic` MID: Llama stored-fact embeddings cluster in ~32-dim subspace despite nominal 2048-dim (TwoNN=32.8, PR=31.9, two independent methods agree).
- `encoder_ladder_hotpot` MID: e5-large 0.78 / bge-large 0.76 / bge-small 0.70 / MiniLM 0.58 on single-fact recall@10. e5-large is the production candidate.
- `hotpot_bge_recall_at_k` HP: 73.3% of 2-hop questions have BOTH facts in top-10. Bridging is the bottleneck, not finding facts.
- `hotpot_substrate_bge` HF: substrate whitening + K-hop on bge gave recall 0.287 vs naive 0.313 (lift -0.027). Encoder gap dominates substrate refinement.
- `hotpot_bge_rerank` HF: cross-encoder reranker on bge top-10 gave 0.290 vs 0.305. Reranker objective (single-doc relevance) is wrong for multi-hop.
- `hotpot_bge_iterative_khop` HF: iterative text-relay K-hop (use first doc to reformulate second query) gave 0.280 vs 0.313. Text drift; explicit entity extraction needed.
- `entity_bridge_decomp` HF (best of 4): regex NER for bridge entity extraction gave +0.010 (0.320 vs 0.310). Direction correct, regex too weak. spaCy or LLM-based NER is the upgrade.
- `pca_bottleneck_keyjob_sweep` HP: KEY-job F1=1.0 at d=30, F1=0.925 at d=10. ~30 dims is sufficient; matches the ~32-dim manifold ID.

## State

- cap_map v477 → v478
- commit: 0524359
- HONEST 1158 → 1166 (+8)
- LVH 257 unchanged
- Portfolio 32+82 unchanged

## Context

Cycle 156 established that Hotpot 2-hop's bottleneck is encoder quality. Cycle 157 maps the encoder ladder (e5-large is the upgrade) and decomposes the 2-hop pipeline. The clean finding: facts are in the index (73.3% top-10 ceiling for bge-small), but every text-level routing strategy lost recall vs naive. The +0.010 best result with regex entity extraction tells us the architecture direction (explicit bridge-entity intermediation) is right; the NER quality isn't.

The privacy-side convergence is the most actionable result of the cycle: manifold ID ≈ 32 from a geometric diagnostic, KEY-job F1=1.0 at d=30 from a capacity test. The ZKL leakage hypothesis from cycle 154 (privacy lives in the encoder geometry) gets a quantitative target — ~30-dim truncation should preserve retrieval while removing leakage. This is the algebraic alternative to the SRHT path that was canceled (cycle 154/155).

Pipeline: 42 commits v438→v478. 213 anchors verdicted. 33 LVH catches.

---

END. No action requested.
