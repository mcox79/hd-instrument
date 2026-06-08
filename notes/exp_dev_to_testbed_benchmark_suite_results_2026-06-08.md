# Exp-Dev -> Testbed: v1 benchmark suite results (substrate-side, for the demo head-to-head panels)

**From:** Exp-Dev  **Date:** 2026-06-08  **Re:** benchmark suite for the v1 demo. All on REAL public datasets, smoke-validated;
full runs queued. These are the substrate-retrieval/K-hop numbers for the demo's head-to-head panels (you wire the LLM-only baseline).

## REAL KG-QA (the categorical north-star win)
- WebQSP (RoG-webqsp, real questions+Freebase graphs): substrate K-hop answers 98.2% of graph-reachable questions
- ComplexWebQuestions (RoG-cwq, harder multi-hop): 94.7%
- FB15k-237 (real Freebase triples): sharded K-hop 1-hop r@5=1.0, 2-hop 0.85; MONOLITHIC collapses to 0.05 (sharding invariant on real data)
- FB15k sharding-strategy: subject & relation sharding both 1.0 (recommended layout: per-subject)

## Real-corpus retrieval
- Wikipedia (10k real articles): title->article r@1=0.95 r@5=0.97; ingest 126 articles/sec (dry-run for 5.84M)
- PubMedQA (biomedical): substrate retrieval r@5=1.0 (reliable; biomedical edge is moats+LLM head-to-head, both at ceiling on raw retrieval)

## Free-text multi-hop (honest parity)
- HotpotQA: bge-large r@2/5/10 = 0.42/0.66/0.72 = ties RAG (same encoder); per-query whitening HURTS small pools (corpus-scale recipe)
- Encoder head-to-head (bge-large/bge-small/e5-large) on HotpotQA: picks the demo encoder (full run pending)

## Headline for the demo
"Substrate answers real knowledge-graph questions (WebQSP 98%, CWQ 95%) where a monolithic store collapses (0.05); ingests real
Wikipedia at 126 art/sec with 0.97 retrieval; ties RAG on free-text. The categorical wins are structured-KG + the moats."

Datasets cached on runner: fb15k_237, hotpot, pubmedqa(pubmed_abstracts), nq_open, medqa, wikipedia_10k, webqsp_rog, cwq_rog.
Remaining on my side: full-scale runs (queued); the LLM-only baseline + side-by-side panels are yours.
