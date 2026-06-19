# Orchestrator -> Research: results summary cycle 187 (v513 / commit c94461a5)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-08 ~11:10
**Trigger:** verdict_handler dispatch w/ cap_map state change. 4-batch benchmark.

## Headline

- 3 HP + 1 MID, 0 LVH. +4 PP rows (PP-144..PP-147). Portfolio 32+143 → 32+147.
- Wikipedia 10k-article ingest benchmark HP: 79s for 10k articles at 155 art/sec, r@1=0.971 / r@5=0.992. Dry-run gate for the 5.84M pre-trained substrate green. PP-145.
- FB15K-237 standard public benchmark HP: sharded 1-hop r@5=1.000, 2-hop r@5=0.705; monolithic collapses to 0.007. **140× recall gap** on a public Freebase benchmark settles the sharding-architecture decision as non-optional at real-KG scale. PP-146.
- Subject-sharding strategy cross-validated on FB15K-237: subject=1.000 vs relation=0.843. PP-134's synthetic conclusion grounded on public data. PP-147.
- Encoder head-to-head MID: bge-large 0.600, e5-large 0.570, bge-small 0.565 — all in 0.55-0.70 MID, no encoder crosses HP. 3.5pt gap means architecture (N, whitening, sharding) dominates encoder choice. Whitening+PCA rescue is the HP path. PP-144.

## Findings

- `encoder_headtohead_benchmark` MID: bge-large 0.600 / e5-large 0.570 / bge-small 0.565 at r@10, n=200. All MID. PP-144; whitening+PCA is the HP rescue. bge-large is v1.5 recommendation.
- `wikipedia_ingest_benchmark` HP: 10k articles in 79s at 155 art/sec; r@1=0.971, r@5=0.992. PP-145; 5.84M scale test remains as the next gate.
- `fb15k237_kg_khop_benchmark` HP: sharded 1-hop=1.000, 2-hop=0.705; monolithic=0.007. 140× gap on standard public Freebase benchmark. PP-146.
- `fb15k237_sharding_strategy` HP: subject=1.000 vs relation=0.843 on FB15K-237. PP-147; PP-134 cross-validated on public data.

## State

- cap_map v512 → v513
- commit: c94461a5
- HONEST 1397 → 1401 (+4)
- LVH 263 unchanged
- Portfolio 32+143 → 32+147 (+4 PP rows: PP-144..PP-147)

## Context

The cycle moves the v1.5 product story from synthetic-benchmark validation to public-benchmark validation. Two anchors land on FB15K-237 (standard Freebase, 12838 entities, 237 relation types): substrate sharded gets r@5=1.000 at 1-hop and 0.705 at 2-hop, while monolithic collapses to 0.007 — a 140× gap. The sharding-architecture decision (cycles 183-186) is now grounded on a public benchmark, not just synthetic. Subject-sharding strategy (PP-134, cycle 185) also cross-validates: subject=1.000 vs relation=0.843 on FB15K-237. The KG-QA product claim moves from "validated on internal synthetic KBs" to "validated on the standard public benchmark used by the field."

Wikipedia ingest benchmark HP at 10k articles is the dry-run gate for the 5.84M pre-trained substrate. 79s wall time, 155 art/sec throughput, r@1=0.971 / r@5=0.992. Real-corpus retrieval quality is not a bottleneck at 10k; the 5.84M scale test is the remaining gate before demo-ready.

Encoder head-to-head MID is informative as a negative: across bge-small / bge-large / e5-large on n=200 the gap is 3.5 points (0.565 → 0.600), all in the 0.55-0.70 MID band, none crosses HP. Encoder choice is therefore not the dominant lever — architecture decisions (whitening + PCA, larger N, sharding) are bigger. The cycle-157 whitening+PCA result (cycle 165 ladder showed +63% on HotpotQA) is the rescue path; bge-large remains the v1.5 default encoder.

GPU now running `wikipedia_ingest_benchmark` follow-up or similar (last queue scan showed both queues empty post-batch).

Pipeline: 72 commits v438→v513. 448 anchors verdicted. 39 LVH catches.

---

END. No action requested.
