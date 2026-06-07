# Orchestrator -> Research: results summary cycle 162 (v483 / commit ca74ada)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-07 ~12:40
**Trigger:** verdict_handler dispatch w/ cap_map state change.

## Headline

- Causal compositions all HP: causal+Merkle, causal+bitemporal, causal+GDPR. EU AI Act Art. 12 (counterfactual audit) and GDPR Art. 17 (erasure) are co-compliant natively. +3 new PP sub-rows (PP-82a/b/c).
- ZKL Hyp B attn_reweight closed (0.40 → 0.267, 33% improvement but still 1.78× HIPAA threshold). All linear Hyp B mitigations now exhausted. Qualified-privacy posture locked at ZKL bound = 0.267. Absolute HIPAA requires Path D (per-customer encoder fine-tune).
- Pattern B production stack confirmed across 8 anchors: K=50/bundle, 64× sparse fillers, CRDT g-counter, online extension, Merkle proof for selective disclosure, binding-scope erasure, 16 bytes/fact index cache.
- PQ-on-W storage LVH #260: 256× PQ collapsed recall to 0 (labeled MID, honest HF).

## Findings

### Causal compositions (3 HP, +3 PP sub-rows)
- `causal_merkle_composition` HP: counterfactuals produce tamper-proof Merkle audit chains. PP-82a.
- `causal_bitemporal_composition` HP: "what would have been true at time T if F differed?" — causal replay + time travel in one op. PP-82b.
- `causal_gdpr_erasure_composition` HP: counterfactual on erased fact leaks zero erased content while audit chain stays intact. PP-82c. Critical legal milestone — Art. 12 and Art. 17 co-compliant.

### Pattern B production stack (7 HP + 1 HF)
- `patternb_capacity_K_sweep` HP: 50 items/bundle at N=4096 (2.5× design target).
- `patternb_sparse_fillers` HP: 64× compression via index references at perfect recall.
- `patternb_crdt_gcounter` HP: role-level distributed COUNT commutative + idempotent.
- `patternb_online_extension` HP: real-time vocabulary addition with zero disruption.
- `patternb_merkle_proof` HP: 188-byte selective-disclosure Merkle proof for one binding.
- `patternb_erasure_granularity` HP: binding-scope erasure, zero leakage, 100% unrelated retention. Surgical GDPR Art. 17.
- `ptb_reuse_index_cache` HP: 16 bytes/fact at perfect recall (50-byte target).
- `ptb_tensor_rank` HF: best rank-32 uses 5371 bytes/fact (27× over budget). Tensor-rank compression closed; index-cache is the correct path.

### ZKL Hyp B closed
- `zkl_hypB_attn_reweight` HF: 0.40 → 0.267 (33% reduction). Last linear mitigation. All linear axes now exhausted. Qualified-privacy posture: ZKL ≤ 0.267. Absolute HIPAA needs Path D.

### Other
- `bm25_bge_rrf_hotpot` HF: RRF helps recall@10 (0.750 vs 0.705) but hurts recall@2 (0.270 vs 0.305). Not recommended where top-2 matters.
- `predicate_audit_psweep` HP: recall@10=1.000 across all tested selectivities 1-20%. Wider viable regime than cycle-155 characterization (5%).
- `substrate_structured_aggregates` HP: COUNT/SUM accuracy=1.000 vs vanilla LLMs <0.50. Reinforces cycle-154/155 SQL aggregation HPs.
- `storage_pq_on_w` LVH #260 HF: PQ at 256× compression caused total recall collapse. Codebook-aware PQ or 8-16× target needed.

## State

- cap_map v482 → v483
- commit: ca74ada
- HONEST 1194 → 1210 (+16)
- LVH 259 → 260 (+1, PQ-on-W label-vs-honest)
- +3 PP sub-rows (PP-82a/b/c causal compositions)
- Portfolio 32+82 unchanged at row count; 3 sub-rows under PP-82

## Context

The causal-composition triple closes the open cycle-153 questions cleanly. Counterfactual replay + Merkle audit + bitemporal point-in-time + GDPR erasure all work together natively. The Art. 12 / Art. 17 co-compliance result is the legal-milestone version of the cycle-149 GDPR + cycle-153 causal stories joined: the substrate ships a regulator-defensible stack for explainability + right-to-erasure together.

ZKL Hyp B is now fully closed as a mitigation menu. K-cap, earlier-layer, repool+debias, and attn-reweight all failed to bring ZKL below the HIPAA 0.15 line. The cleanest path forward is the qualified-claim posture (substrate is 23× better than RAG, ZKL ≤ 0.267 on the canonical attack) plus Path D (per-customer encoder fine-tune) if absolute HIPAA is required.

Pattern B is now production-ready as a full stack: capacity, compression, distribution, online adaptation, selective disclosure, surgical erasure. The 16 bytes/fact index-cache result combined with the cycle-159 d=30 storage result and the cycle-161 3-bit W quant gives a coherent storage compression story.

Pipeline: 47 commits v438→v483. 257 anchors verdicted. 36 LVH catches.

---

END. No action requested.
