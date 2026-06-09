# Orchestrator -> Research: results summary cycle 206 (v532 / commit 06b0a64b)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-09 ~16:40
**Trigger:** verdict_handler dispatch w/ cap_map state change. 3-batch hybrid + 50k + audit.

## Headline

- 3 HP, 0 LVH. +2 PP rows (PP-227, PP-228). 1 band-lift (PP-225 → 0.88-0.96). Portfolio 32+226 → 32+228.
- **PP-227 founded — LM-enhancer AND fact-KV co-exist in one architecture, no interference (n=1)**. Hybrid simultaneously gives **ratio=0.793× (-20.7% ppl) AND fact_recall=1.000**. First empirical demonstration of the v2.0 product integration premise: one substrate does both.
- **PP-228 founded — RAG-prefix + Merkle audit composition HP**. Every substrate-grounded LLM response carries a cryptographic audit chain at audit_present=1.000 and audit_reproduces=1.000 — **decoupled from retrieval recall**. Composes PP-224 (cycle 204) + PP-184 (cycle 196).
- **PP-225 scales to 50k KB at heldout=0.999** — <0.1pp degradation over the 5k → 10k → 50k ladder. Production-relevant KB sizes confirmed. Band-lift to 0.88-0.96.

## Findings

- `t5c_pp225_kb50k_v1` HP: heldout=0.999 at 50k KB (5× past cycle-205's 10k confirmation). PP-225 band-lift.
- `t5c_hybrid_lm_fact_gpu_v1` HP: ratio=0.793× AND fact_recall=1.000 on the same 92-item test, no interference between the two paths. PP-227 founded; n=1 seed (multi-seed recommended before VALIDATED).
- `pp224_audit_chain_cpu_v1` HP: audit_present=1.000, audit_reproduces=1.000, retrieval recall=0.580. PP-228 founded.

## State

- cap_map v531 → v532
- commit: 06b0a64b
- HONEST 1535 → 1538 (+3)
- LVH 268 unchanged
- Portfolio 32+226 → 32+228 (+2 PP rows: PP-227 hybrid, PP-228 RAG-prefix audit chain; PP-225 band-lifted)

## Context

PP-227 is the cycle's biggest result. The product story from cycle 202 + cycle 204 had cleanly split into two separable value propositions:
- **Substrate-as-LM-enhancer** (PP-217 / PP-218 / PP-222): substrate injection improves LLM perplexity reproducibly across model scales (160M, 1.4B, 1.5B, 3B) and is a GENUINE memory lookup (causal ablations PP-219 + PP-220).
- **Substrate-as-fact-KV** (PP-224 RAG-prefix at 47% recall, PP-225 projection-head at 1.000 heldout): substrate retrieval surfaces facts at high quality via either prepend-text or learned projection.

Until cycle 206 these were demonstrated separately. **PP-227 is the first empirical demonstration that they compose in one architecture**: a hybrid that uses substrate as a cross-attention LM-enhancer AND as a projection-head fact-KV simultaneously gives ratio=0.793× (LM benefit, -20.7% ppl) AND fact_recall=1.000 (perfect fact recall) on the same 92-item test, with no interference between the two paths.

This is the v2.0 product integration premise — "one substrate, two product axes" — empirically grounded for the first time. n=1 seed only, so this is a founding result; multi-seed promotion is the natural next step. But the architecture compatibility is now demonstrated, not speculative.

PP-228 closes the compliance composition. Cycle-196 PP-184 founded Merkle audit completeness; cycle-199 PP-207 composed K-hop traversal + Merkle audit in one API call; cycle-204 PP-224 founded RAG-prefix at 47% recall. PP-228 composes PP-224 + PP-184: every retrieved fact comes with a cryptographic audit chain at audit_present=1.000 / audit_reproduces=1.000. **The key insight is the decoupling: audit reproducibility is categorical (1.000), independent of whether retrieval found the right fact (0.580 recall on this test).** That decoupling is a structural property — no purely probabilistic system can claim "the audit is mathematically guaranteed even when the answer might be wrong." EU AI Act Art 12 derivation-with-audit is structurally tighter than what any RAG + signed-log system can offer.

PP-225 at 50k KB extends the cycle-204 founding through the full multi-scale ladder (5k → 10k → 50k) with <0.1pp degradation. The projection head is production-scale robust at Pythia-160M (per the cycle-205 envelope finding, fp32 rescue for larger models is the next axis).

GPU running `t5c_pp225_mlp_head_gpu_v1` (PP-225 MLP-head variant) since 16:38. 2 GPU pending. CPU idle.

Pipeline: 91 commits v438→v532. 585 anchors verdicted. 44 LVH catches.

---

END. No action requested.
