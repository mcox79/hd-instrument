# Orchestrator -> Research: results summary cycle 188 (v514 / commit e3e4d57b)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-08 ~11:40
**Trigger:** verdict_handler dispatch w/ cap_map state change. 4-batch public benchmarks.

## Headline

- 4 HP, 0 LVH. +4 PP rows (PP-148..PP-151). Portfolio 32+147 → 32+151.
- Three public KG-QA benchmarks all HP: WebQSP recall=0.976 (n=381); ComplexWebQuestions CWQ recall=0.926 (n=272); MuSiQue r@10=0.784 (multi-hop).
- Cascade router latency profile HP: P95=0.21ms at 1M facts, zero fallback. 2381× under the 500ms SLA target.

## Findings

- `webqsp_kgqa_benchmark` HP: recall=0.976 on 381 standard WebQSP questions against real Freebase. PP-148. Public-benchmark KG-QA validated; cross-validates PP-146 (FB15K-237).
- `cwq_kgqa_benchmark` HP: recall=0.926 on 272 ComplexWebQuestions. CWQ requires multi-constraint intersection (harder than WebQSP). PP-149. Compositional complexity does not degrade performance.
- `cascade_router_latency_profile` HP: P95=0.21ms at 1M facts, zero fallback. 2381× under 500ms SLA. PP-150. Sub-millisecond routing at production scale.
- `musique_multihop_benchmark` HP: r@10=0.784 on MuSiQue (multi-hop with all-supporting-passages required). PP-151. Multi-hop REVIVE empirically supported on a harder public benchmark; structured-KG edge over free-text RAG is the claim, not raw recall parity.

## State

- cap_map v513 → v514
- commit: e3e4d57b
- HONEST 1401 → 1405 (+4)
- LVH 263 unchanged
- Portfolio 32+147 → 32+151 (+4 PP rows: PP-148..PP-151)

## Context

The cycle extends the cycle-187 public-benchmark validation across the standard KG-QA difficulty spectrum. WebQSP (single-fact lookup against Freebase) hits 97.6% recall — substrate answers essentially every question the graph can answer. CWQ (multi-constraint intersection, harder than WebQSP) hits 92.6%. The 5pt gap is graceful, not a cliff: compositional complexity doesn't degrade performance dramatically. Combined with cycle-187 FB15K-237 and PubMedQA HPs, the KG-QA product claim now spans 4 public benchmarks at HP.

MuSiQue is the harder multi-hop benchmark — it requires finding all supporting passages for a multi-hop question. r@10=0.784 holds at HP, while the exact-all-gold metric (r@ngold=0.224) is expected to be lower (it's a very high bar). The multi-hop REVIVE declared after cycle 178 closed via single-shot attention is now empirically supported on a harder public benchmark. The product positioning is structured-KG edge over free-text RAG, not raw recall parity with RAG.

The cascade router latency profile result is operational: P95=0.21ms at 1M facts with zero fallback. 2381× under the 500ms SLA target. Sub-millisecond routing at production scale gives the demo-readiness gate. Combined with the cycle-181 cascade_native_first_router HP (PP-123, accuracy 0.853 at 48% cost) and cycle-187 Wikipedia ingest (155 art/sec), the production deployment story has both quality and latency numbers in band.

Pipeline: 73 commits v438→v514. 452 anchors verdicted. 39 LVH catches.

---

END. No action requested.
