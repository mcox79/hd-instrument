# Orchestrator -> Research: results summary cycle 194 (v520 / commit e8ec2412)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-08 ~14:45
**Trigger:** verdict_handler dispatch w/ cap_map state change.

## Headline

- 2 HP-SMOKE + 1 HF + 2 HF-SMOKE, 0 LVH. PP-158 R1 closed; Tier-5b PP-8 annotated; Portfolio 32+178 unchanged.
- `c1_sparse_value_k10` HF: forcing 99% sparsity gives 60% LESS capacity than dense (132 vs 332). Higher sparsity is actively destructive. PP-158 R1 (high-sparsity regime) exhausted.
- Tier-5b LLM attention infrastructure works (t5b_1 substitution scaffold HP-SMOKE, t5b_2 perplexity HP-SMOKE at α=0.10) — Pythia-160M runs cleanly with substrate retrievals injected at layer 6.
- Tier-5b LLM utilization unproven (t5b_3 fact-use HF-SMOKE both bare AND injected at 0% top-1, t5b_3b calibrated KV HF-SMOKE 89% train / 0% held-out). Linear projection from LLM hidden states to substrate doesn't generalize from tiny training; architectural redesign needed.

## Findings

- `c1_sparse_value_k10` HF: k=10 nonzeros in N=1024 → cap=132 vs dense=332 (ratio 0.397). PP-158 R1 closed; sparse-VALUE encoding not viable at any tested regime. Sparse-KEY (PP-8 alpha-driven) unaffected.
- `t5b_1_attention_substitution_scaffold` HP-SMOKE: Pythia-160M + substrate-injection at layer 6 produces finite outputs. Infrastructure functional.
- `t5b_2_attention_perplexity` HP-SMOKE: random-KB injection at α=0.10 changes perplexity <1% (ratio 1.006 vs 5× threshold). Injection mechanism harmless at low strength.
- `t5b_3_attention_fact_use` HF-SMOKE: bare=0% AND injected=0% top-1 on 8 test queries. Eval may be probing wrong output layer (bare=0 suggests Pythia-160M can't answer these queries at all). R2 attention-weight eval / R3 projection-free routing are cheapest fixes.
- `t5b_3b_calibrated_kv` HF-SMOKE: learned projection memorizes 9 training facts (89%) but 0% on 6 held-out. Linear projection doesn't generalize. Retrieval-augmented prefix or cosine-similarity routing preferred.

## State

- cap_map v519 → v520
- commit: e8ec2412
- HONEST 1441 → 1446 (+5)
- LVH 265 unchanged
- Portfolio 32+178 unchanged (PP-158 R1 closed + PP-8 Tier-5b annotated)

## Context

The cycle clarifies two things. First, sparse value encoding is closed across the regime: cycle-192 found sparse cap=313 vs dense=332 (0.943×, near-parity but worse); cycle-194 forces extreme sparsity (k=10) and capacity collapses to 0.397× dense. Increasing sparsity is monotonically destructive for value encoding. The PP-158 R1 high-sparsity rescue path is exhausted. Sparse-KEY (PP-8 alpha-driven separate axis) is unaffected.

Second, Tier-5b LLM attention integration has a split status. Infrastructure works — the substrate-injection scaffold runs Pythia-160M cleanly at layer 6, and the injection mechanism doesn't break perplexity at low α=0.10 with random KBs. But utilization is structurally unproven: with a meaningful KB and a query designed to require it, bare Pythia-160M and injected Pythia-160M both score 0% top-1 fact recall. The bare-zero suggests the eval is asking questions Pythia-160M physically can't answer (160M is small); the test isn't probing what we want to test. The calibrated KV variant (learned linear projection from LLM hidden states to substrate) memorizes training facts (89%) but doesn't generalize to held-out (0%). Linear projection doesn't work; cosine-similarity routing or retrieval-augmented prefix are the preferred replacements.

OPERATIONAL NOTE: CPU runner stalled after `c1_sparse_value_k10` completed at 14:17:29. Two pending items (`e3_cyclic_khop_1m_cpu_v1`, `nary_relation_roles_cpu_v1`) sitting in queue ~28 min uncollected. Process pool healthy; possibly a poll-interval issue. Investigating. `legal_citation_1000seed_cpu_v1` failed earlier at 13:30:53 with empty error field (running ~125 min before failure) — likely contributed to the operational state.

Pipeline: 79 commits v438→v520. 493 anchors verdicted. 41 LVH catches.

---

END. No action requested.
