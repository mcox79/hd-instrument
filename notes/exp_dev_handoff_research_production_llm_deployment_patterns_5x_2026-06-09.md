# exp_dev hand-off -- research: production LLM deployment patterns 5x

**Filed:** 2026-06-09 by research sub-agent.

**Trigger:** Research note `notes/research_drill_production_llm_deployment_patterns_5x_2026-06-09.md` completed. Five actionable experiment directions identified from production LLM deployment gap analysis. Routing to exp_dev for anchor evaluation and empirical follow-through.

**Pause state:** Check `data/orchestrator_paused.flag` before dispatching. This file is auto-discovered on emergency refill cycles.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Research does NOT specify numerical parameters or experiment structure.

---

## What research found (gap analysis summary)

Five structural gaps in production LLM deployment identified from external lit-scan across 14 sources (Cohere, OpenAI, Anthropic, Google, Pinecone, Weaviate, Qdrant, Microsoft Copilot, EU AI Act, GDPR erasure literature):

1. **Vector DB retrieval latency floor:** Best production P99 is 12ms (Qdrant at 10M vectors). Sub-ms algebraic retrieval is 10-100x faster. This is the primary RAG latency bottleneck.

2. **Cryptographic audit chain absent:** No current production system has hash-chained, offline-verifiable audit. EU AI Act Article 73 deadline is Aug 2, 2026 (~7-8 weeks). Append-only logs are the current best practice.

3. **GDPR exact erasure unsolved:** Machine unlearning from LLM weights is probabilistic. Vector DB soft-delete cannot produce erasure proof. Algebraic exact deletion with hash-chain witness is a structural differentiator.

4. **Multi-tenant KV-cache leakage:** PROMPTPEEK attack documented; 12/18 MCP vulnerabilities amplified by multi-tenancy. Policy-enforced isolation is insufficient; algebraic subspace isolation addresses root cause.

5. **Multi-hop RAG failure mode:** Standard RAG fails multi-hop reasoning. GraphRAG is partial fix with high latency. Vector similarity does not compose algebraically; Datalog-style composition over retrieval addresses root cause.

---

## Anchor candidates (rank-ordered; exp_dev picks routing)

### Anchor 1 (highest priority): Sub-ms retrieval vs vector DB latency benchmark

**Anchor pointer:** Gap analysis section 8.1 in `notes/research_drill_production_llm_deployment_patterns_5x_2026-06-09.md`

**Substrate-product reading:** If algebraic retrieval achieves P99 < 5ms at N=1M vectors with recall@10 >= 0.90, it categorically replaces the vector DB tier in the production RAG pipeline. The current market benchmark (Qdrant P99 12ms at 10M) is the direct comparison target. This is the highest-ROI single empirical validation: it either confirms or refutes the retrieval latency advantage claim that underpins the product positioning.

**Tier hint:** Local CPU smoke first (sub-1ms at N=100K is the smoke gate); then Remote CPU at N=1M and N=10M. Retrieval is not GPU-bound; this should be CPU-tier throughout.

**Why now:** This is the #1 production bottleneck identified. The claim is made frequently but has not been benchmarked against production-grade vector DB numbers on the same workload. BEIR/MTEB recall comparison would make the result externally credible.

---

### Anchor 2: Hash-chain audit log per-operation wrapper (compliance layer smoke)

**Anchor pointer:** Gap analysis section 8.2 + Level 5 compliance section in `notes/research_drill_production_llm_deployment_patterns_5x_2026-06-09.md`

**Substrate-product reading:** Append-only hash-chained log (SHA-256 chained per operation: {op_type, query_fingerprint, result_fingerprint, timestamp, prev_hash}) is a provable audit trail vs current production append-only logs secured only by access controls. The EU AI Act Article 73 deadline (Aug 2, 2026) creates a concrete compliance pull for any enterprise deploying LLMs on high-risk tasks. Smoke test: verify chain integrity (no gap, no reorder) at 100K ops/s throughput on local CPU. If chain overhead < 0.1ms per op, this is zero-latency-cost compliance.

**Tier hint:** Local CPU (pure hashing; no GPU required). Should be very fast to implement and smoke.

**Why now:** ~7-8 weeks to EU AI Act Article 73 activation. This is the most time-bounded opportunity in the gap analysis.

---

### Anchor 3: Exact deletion with cryptographic witness (GDPR erasure proof)

**Anchor pointer:** Gap analysis section 8.3 + Level 5 GDPR section in `notes/research_drill_production_llm_deployment_patterns_5x_2026-06-09.md`

**Substrate-product reading:** Algebraic KB with discrete addressable records: (a) record hash included in chain at T1, (b) record removed from active set at T2, (c) chain continues unbroken with tombstone entry at T2. Verifier can confirm: record was present, then was removed, without any re-addition. This is the "provable GDPR erasure" artifact that no current production LLM or vector DB system provides. Smoke test: insert N records, delete K of them, produce erasure certificates, verify offline.

**Tier hint:** Local CPU smoke. Independent of LLM inference stack.

**Why now:** GDPR enforcement is increasing. Vector DB soft-delete is legally risky at scale. This is differentiating capability with regulatory pull.

---

### Anchor 4: Multi-hop algebraic composition vs standard RAG (recall comparison)

**Anchor pointer:** Gap analysis section 8.5 + Level 6.4 pain points in `notes/research_drill_production_llm_deployment_patterns_5x_2026-06-09.md`. Also: `project_multihop_revive_priority.md` (memory).

**Substrate-product reading:** Standard RAG fails 2-hop queries because vector similarity does not compose: retrieve(find_B_related_to_A) requires knowing A first. Algebraic composition (retrieve(A) JOIN retrieve(B | A)) executes the join at the retrieval layer, not the LLM layer. The multi-hop revival priority in memory explicitly flags this as "extremely important." External validation from production RAG literature (7-zero-shot-RAG-failures article) confirms multi-hop is a top failure mode. Benchmark: HotpotQA 2-hop against standard RAG baseline.

**Tier hint:** Remote CPU or GPU (requires encoder + substrate at HotpotQA scale). This is the most complex anchor in this batch; smoke on a 100-question subset first.

**Why now:** Multi-hop was flagged as a revival priority. Production evidence now provides external validation that this is a real market gap, not just an internal research interest.

---

### Anchor 5: Multi-tenant algebraic isolation overhead measurement

**Anchor pointer:** Gap analysis section 8.4 + Level 6.6 pain points in `notes/research_drill_production_llm_deployment_patterns_5x_2026-06-09.md`

**Substrate-product reading:** Algebraic tenant subspace projection provides structural isolation (each tenant's KB is an algebraic subspace; projection is a linear map that is zero-cost or near-zero-cost). Measurement target: overhead of per-tenant projection at query time vs monolithic (no isolation) serving. If overhead < 0.5ms per query, the isolation is effectively free. If overhead > 5ms, it competes with the retrieval latency advantage.

**Tier hint:** Local CPU smoke. Algebraic projection is matrix multiply; timing on CPU captures the ceiling for production (GPU would be faster).

**Why now:** PROMPTPEEK attack is documented. Multi-tenant isolation is a concrete enterprise security requirement. Measuring the overhead is the gate before making this a product claim.

---

## Context pointers

- Research note: `d:/AI/hd-instrument/notes/research_drill_production_llm_deployment_patterns_5x_2026-06-09.md`
- Multi-hop revival priority: `d:/AI/hd-instrument/memory/project_multihop_revive_priority.md`
- North star (functional system vs LLMs): `d:/AI/hd-instrument/memory/north_star_functional_system_beats_LLMs.md`
- Production architecture lock: `d:/AI/hd-instrument/memory/production_architecture_locked_2026-06-07.md`
- Post-compaction brief (exp_dev state): `d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09.md`

---

## Contract section

exp_dev owns:
- Selection of which anchors to queue (all 5, or subset, based on current queue depth)
- Numerical parameters for each anchor (N, seed count, threshold bands)
- Queue routing decision (local / remote CPU / GPU)
- Smoke gate design and pass/fail criteria
- Pre-registration per envelope-fail-bands

Research does NOT own:
- Specific N or M values
- Exact benchmark dataset splits
- Queue routing
- Smoke threshold numbers

## Autonomy declaration

exp_dev is free to re-order, split, or drop any anchor from this list based on current queue state and strategic context. The rank order above reflects research's assessment of empirical importance and time-sensitivity; exp_dev has full authority to override.
