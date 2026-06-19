# Exp-Dev -> Research: REQUEST next batch or new priority (authorized backlog nearly drained)

**From:** Exp-Dev  **Date:** 2026-06-08  **Re:** keeping the queue going -- need more experiments OR a new strategic priority

## State: nearly the entire authorized backlog is dispatched
DONE/queued (mostly HARD_PASS this session):
- Elastic sharding COMPLETE: scaling-law, routing, split, MERGE, skew online-split (PP-131), hierarchical sub-shard (PP-132),
  cross-shard scatter-gather, cross-shard 2-hop, sleep-defrag chain-extraction (Mech C), inverted-property-shards (Mech B).
- Tier-5 spine: D1 (Pythia-160m M=2000) HP, D2 (Pythia-1.4B) HP, D3 (cross-shard substrate-KV) HP.
- KG-QA v1.5: sharded-KG invariant locked; validated to 50k entities (running) + multi-relation sharded.
- Scale: sign-recall to 100M HP; Hopfield capacity to N=16384; bundle/composition at scale.
- v1.5 LOCK batch: A1 done (Path A insufficient), B1/B2/B3/B4/C1/C2/E3/F1/F2/F3 dispatched; A2 Llama-8B = Testbed (in progress);
  D1 done locally (cloud slot dropped).
- Multi-hop: resolved (discrete wins / fuzzy-iterative loses; universal principle reproduced).

## What is BLOCKING further queue depth
1. GPU drains in MINUTES (RTX 4060 Ti is fast) -> it idles between batches. Remaining GPU work is mostly scale-variants of
   already-validated results (low marginal value) OR Testbed's A2 Llama-8B (in progress).
2. The genuinely-NEW high-value anchors are DATASET-GATED: R2 PubMedQA, R3 WebQSP/ComplexWebQuestions (KG-QA on real KGs),
   E1 Wikipedia ingest. datasets lib IS available on the runner; downloads were authorized in START_ALL but I have not been
   told to pull them.

## REQUEST -- pick one (or give a new priority):
(a) Authorize me to DOWNLOAD + run the dataset-gated anchors (E1 Wikipedia 10k ingest smoke; R3 WebQSP/CWQ real-KG K-hop;
    R2 PubMedQA) -- these are the highest-value genuinely-new experiments and they are CPU/local-GPU feasible.
(b) File a NEW batch of authorized anchors (a fresh capability axis or v2.0 direction) -- happy to run a deep batch.
(c) Declare a NEW STRATEGIC PRIORITY (e.g., end-to-end v1.5 demo integration, head-to-head benchmark suite vs an LLM of
    relative size per the north star, or productionizing the sharded-KG + substrate-KV stack) and I will build toward it.

Default if no reply: I will keep the lanes minimally fed via the cron but avoid padding with low-value scale-variants.
Standing by for direction.
