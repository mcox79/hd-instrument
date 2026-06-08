# Orchestrator -> Research: results summary cycle 189 (v515 / commit ecc2c481)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-08 ~12:05
**Trigger:** verdict_handler dispatch w/ cap_map state change.

## Headline

- `twowiki_multihop_benchmark` HP: r@10=0.720 on 2WikiMultiHopQA (n=250). Third standard free-text multi-hop benchmark at HP. PP-152.
- Multi-hop benchmark cluster now consistent across 3 datasets: HotpotQA r@10=0.640 (MID, cycle 186 PP-138), MuSiQue r@10=0.784 (HP, cycle 188 PP-151), 2WikiMultiHopQA r@10=0.720 (HP, cycle 189 PP-152). The 0.640-0.784 cluster supports the "ties RAG (same encoder)" framing — gap is retrieval overhead, not capability floor.

## Findings

- `twowiki_multihop_benchmark` HP: r@10=0.720, n=250, threshold 0.65 (10.8% margin). PP-152 founded (0.72-0.85 EXPLORATORY band).

## State

- cap_map v514 → v515
- commit: ecc2c481
- HONEST 1405 → 1406 (+1)
- LVH 263 unchanged
- Portfolio 32+151 → 32+152 (+1 PP row: PP-152)

## Context

Three independent multi-hop benchmarks on substrate are now in the 0.64-0.78 r@10 range: HotpotQA (cycle 186 MID at 0.640), MuSiQue (cycle 188 HP at 0.784), 2WikiMultiHopQA (cycle 189 HP at 0.720). The cluster width is 14 percentage points across datasets that vary considerably in difficulty. The framing that matches: substrate ties RAG at the same encoder, with the small gap reflecting retrieval-overhead cost — not a capability floor where multi-hop fundamentally fails. Whitening + PCA encoder rescue (cycle 165 showed +63% on HotpotQA) is the open path to lift this cluster.

Rescue sketches filed for PP-152: 3-seed promotion, whitening+PCA, n=1000 statistical confidence.

GPU now running `wikipedia_ingest_100k_gpu_v1` — 10× scale-up from cycle-187's 10k HP. CPU running `legal_citation_1000seed` (extending PP-120 to 1000 seeds). CPU queue refilled to 13 pending.

Pipeline: 74 commits v438→v515. 453 anchors verdicted. 39 LVH catches.

---

END. No action requested.
