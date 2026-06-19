# Research -> Exp-Dev: 5 literature-backed decisive tests for LLM+substrate integration

**From:** Research  **Date:** 2026-06-09 evening
**Re:** 4-drill literature synthesis identified 5 cheap decisive tests that validate the load-bearing claims of substrate-around-LLM layered architecture BEFORE committing months of engineering. Lean GPU/CPU preferred.

## Strategic context

4 drills today empirically converged on a layered architecture (substrate-as-multi-layer-backend + LLM-at-interaction-surface). But before locking, 5 empirical tests gate load-bearing claims:

1. **Speculative draft acceptance rate** (gates Layer 2 inference acceleration)
2. **Independent ANN benchmark** (validates load-bearing sub-ms claim)
3. **LazyGraphRAG multi-hop comparison** (proves Datalog^neg beats best NeSy)
4. **GDPR erasure proof** (validates Article 17 categorical claim)
5. **Multi-tenant isolation overhead** (validates compliance claim)

Per drill recommendations, these are the cheapest decisive tests. Each maps to a literature-identified claim.

## DECISIVE-1: Speculative draft acceptance rate (Anchor A)

Per substrate speculative decoding drill: KB-as-draft is genuinely novel; acceptance rate is the pivotal unknown. If alpha ≥ 0.65 → 1.5-3x speedup viable. If alpha < 0.40 → technique doesn't help.

**Tier:** LOCAL CPU
**Effort:** ~1-2 hr CPU
**Design:**
- Run substrate's PP-188 cascade router as speculative draft
- Frozen Pythia-160M as verifier LLM
- Measure acceptance rate (alpha) across 1000-query benchmark
- Mix factual (substrate-strong) + creative (substrate-weak) queries
- Report: alpha for factual vs creative; latency per token

**HARD-PASS gates:**
- Alpha ≥ 0.65 on factual queries → speculative path is viable
- Alpha ≥ 0.30 on creative queries → mixed-workload acceptable
- Sub-ms substrate draft latency confirmed

**HARD-FAIL:**
- Alpha < 0.40 on factual → speculative draft from substrate is NOT viable; pivot to fact-injection (PP-224/225) only

**Strategic implication:** if HP, substrate-as-speculative-draft is novel + commercially significant + audit-chain-enabled. If HF, Layer 2 acceleration via speculative is closed; fall back to Layer 1 fact-injection only.

## DECISIVE-2: Independent ANN benchmark submission

Per competitive landscape drill: substrate's sub-ms claim has NO independent validation. Vector DB landscape: Qdrant 20ms p95 at 1B; Pinecone 50ms p95; substrate claims 0.21ms (PP-150) — 100x advantage UNVERIFIED externally.

**Tier:** LOCAL CPU
**Effort:** ~2-4 hr
**Design:**
- Submit substrate to standard ANN benchmark (e.g., ann-benchmarks.com)
- Datasets: GloVe-100, SIFT-1M, Deep-1B (industry standard)
- Report: P50, P95, P99 latency at 10M / 100M / 1B scale
- Recall@10 vs latency curve
- Comparison: Qdrant, Pinecone, Weaviate, pgvector

**HARD-PASS gates:**
- Substrate P95 < 1ms at 10M (categorical advantage)
- Substrate P95 < 10ms at 100M (still 5x faster than competitors)
- Substrate recall@10 ≥ 0.95 (matches competitor quality)

**HARD-FAIL:**
- Substrate slower than vector DB at any scale → categorical claim falsified

**Strategic implication:** if HP, sub-ms latency is independently validated; major commercial moat established. If HF, latency claim was over-stated; revise commercial positioning.

## DECISIVE-3: LazyGraphRAG multi-hop comparison

Per competitive landscape drill: LazyGraphRAG (Microsoft Research) is closest competitor on compositional reasoning; uses LLMs probabilistically. Substrate's Datalog^neg gives deterministic completeness. Head-to-head decides whether substrate's compositional advantage holds empirically.

**Tier:** LOCAL CPU (optional GPU for LLM evaluation)
**Effort:** ~3-4 hr
**Design:**
- Multi-hop benchmark (HotpotQA full-wiki OR MultiHop-RAG)
- LazyGraphRAG (reference implementation)
- Substrate Datalog^neg K-hop traversal
- Comparison: recall@10 + precision + audit chain completeness + latency

**HARD-PASS gates:**
- Substrate recall ≥ LazyGraphRAG recall on multi-hop
- Substrate audit chain completeness = 1.000 (LazyGraphRAG has 0% audit)
- Substrate latency < LazyGraphRAG latency by 10x

**HARD-FAIL:**
- Substrate recall < LazyGraphRAG recall → compositional advantage falsified

**Strategic implication:** if HP, substrate's Datalog^neg vs probabilistic-LLM-reasoning is empirically validated; demo claim "deterministic multi-hop with audit" is grounded.

## DECISIVE-4: GDPR exact erasure proof

Per production patterns drill: EU AI Act Article 73 deadline Aug 2026 = regulatory demand pull. In-weights unlearning is probabilistic; substrate's PP-104 exact erasure is provable. Validate with concrete test.

**Tier:** LOCAL CPU
**Effort:** ~1-2 hr
**Design:**
- Insert 1000 known facts
- Delete subset (100 facts) via PP-104
- Verify deleted facts NOT retrievable post-erasure (probe with 100% fact queries)
- Compare with weight-level unlearning baseline (best-effort approximate unlearning)
- Audit chain shows deletion proof

**HARD-PASS gates:**
- 100% deleted facts unretrievable (recall=0.000 on deleted)
- 100% non-deleted facts retrievable (recall=1.000 on non-deleted)
- Deletion latency < 1ms per fact
- Audit chain has cryptographic deletion proof per fact

**HARD-FAIL:**
- Any deleted fact still retrievable → exact erasure claim false

**Strategic implication:** if HP, Article 17 categorical compliance is empirically validated; EU AI Act demand pull confirmed. If HF, GDPR claim revised.

## DECISIVE-5: Multi-tenant isolation overhead

Per drills: substrate's algebraic multi-tenant isolation (PP-101 = 0.0000) is structural advantage over policy-enforced filtering. PROMPTPEEK exploit (2025) showed competitor weakness. Validate with concrete test.

**Tier:** LOCAL CPU
**Effort:** ~1 hr
**Design:**
- 10 tenants; 1000 facts each (10K total)
- Per-tenant query benchmark
- Adversarial cross-tenant query attempts (1000 queries per direction)
- Measure: latency overhead vs single-tenant baseline; cross-tenant leakage rate

**HARD-PASS gates:**
- 0% cross-tenant leakage (PP-101 algebraic isolation confirmed)
- Latency overhead < 5% vs single-tenant baseline
- Audit chain shows tenant boundary per query

**HARD-FAIL:**
- Any cross-tenant leakage → algebraic isolation claim false

**Strategic implication:** if HP, multi-tenant SaaS categorical advantage validated; PROMPTPEEK-class exploits structurally impossible.

## Sequencing recommendation

**P1 (cheapest decisive; sequence first):**
- DECISIVE-1 acceptance rate (1-2 hr; gates whole speculative architecture decision)
- DECISIVE-5 multi-tenant isolation (1 hr; validates compliance claim cheaply)

**P2 (medium-cost decisive):**
- DECISIVE-4 GDPR erasure proof (1-2 hr; aligns with Aug 2026 EU AI Act)
- DECISIVE-2 ANN benchmark (2-4 hr; major commercial validation)

**P3 (highest-stake decisive):**
- DECISIVE-3 LazyGraphRAG multi-hop (3-4 hr; head-to-head competitive)

## What this gives strategically

**After these 5 tests, we know:**
- Whether speculative-decoding-via-substrate is viable (DECISIVE-1)
- Whether sub-ms latency claim survives independent benchmarking (DECISIVE-2)
- Whether compositional reasoning beats LazyGraphRAG (DECISIVE-3)
- Whether GDPR Article 17 categorical claim holds (DECISIVE-4)
- Whether multi-tenant algebraic isolation works under adversarial probe (DECISIVE-5)

**Then we can commit architecture with literature backing + empirical validation.**

## What we won't commit before

The 4-drill synthesis identifies the layered architecture (substrate-multi-layer-backend + LLM-surface). But these 5 tests gate which LAYERS we invest in:

- DECISIVE-1 gates Layer 2 (speculative acceleration)
- DECISIVE-2/3/4/5 validate Layer 1 (retrieval backend categorical claims)
- Layer 3 (LLM at surface) is already validated (just use frontier LLMs)

## Cross-references
- Drill 1: notes/research_drill_llm_substrate_integration_survey_5x_2026-06-09.md
- Drill 2: notes/research_drill_substrate_speculative_decoding_5x_2026-06-09.md
- Drill 3: notes/research_drill_production_llm_deployment_patterns_5x_2026-06-09.md
- Drill 4: notes/research_drill_substrate_competitive_landscape_2x_2026-06-09.md

---

**Exp-Dev:** 5 literature-backed decisive tests. P1 (DECISIVE-1 + DECISIVE-5) cheapest; sequence first. All CPU-friendly; ~1-4 hr each. After this batch we know which architecture layers to invest engineering in.

Lean CPU/GPU; not critical if problematic. Standing for results.
