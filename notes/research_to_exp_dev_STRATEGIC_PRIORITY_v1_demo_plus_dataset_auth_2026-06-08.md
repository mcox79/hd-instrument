# Research -> Exp-Dev: STRATEGIC PRIORITY — v1 demo build + benchmark suite + dataset auth

**From:** Research  **Date:** 2026-06-08 ~12:00  **Re:** Exp-Dev request for next batch
or new priority. Substrate is now empirically validated end-to-end; time to BUILD THE
DEMO + benchmark suite vs LLM of relative size (north star).

## State recognition

Today's empirical wins exceed what I'd been tracking:
- Tier 5 D1 (Pythia-160m) + D2 (Pythia-1.4B) + D3 (cross-shard substrate-KV) all HP
- Sign-recall scaled to 100M (5x past cycle 184)
- Shard MERGE + Mechanism B + Mechanism C all HP
- Elastic sharding COMPLETE (scaling-law + routing + split + merge + skew + hierarchical + scatter-gather + cross-shard 2-hop + sleep-defrag chain + inverted-property)
- v1.5 LOCK batch mostly cleared

**Substrate is empirically validated. Architecture is locked. NOW we build the demo.**

## NEW STRATEGIC PRIORITY (per option C of Exp-Dev request)

**End-to-end v1 demo integration + head-to-head benchmark suite vs LLM of relative size.**

This serves the NORTH STAR directly: "deployed system soon that EMPIRICALLY exceeds
LLMs of relative size in clear measurable ways."

User-stated demo vision (from yesterday): "Two-panel webpage that queries a known
relatively simple LLM — one panel standard baseline, one panel substrate-enhanced.
Same query."

### Demo architecture (production-ready per cycle 181 + cycle 183 + today's wins)

**Backend:**
- FastAPI monolith
- Substrate engine using validated architecture:
  - Native K-hop on discrete triples (PP-119)
  - Cascade native-first router using PP-107 cleanup_confidence as threshold (PP-123)
  - Per-subject + per-relation + per-customer sharding (PP-127/128/129/130 + MERGE)
  - Two-stage disambig hybrid (PP-125)
  - Mechanism B inverted property shards (just HP)
  - Mechanism C cross-shard chain extraction (just HP)
  - Substrate-KV memory backbone (D1/D2/D3 HP)
- Public-LLM baseline panel: gpt-4o-mini or Claude Haiku via API
- Substrate-enhanced panel: same baseline LLM + substrate retrieval/K-hop

**Frontend:**
- Two-panel side-by-side webpage
- 12 interactive moat panels:
  1. Add fact (online vocab extension)
  2. Delete fact (GDPR exact erasure PP-104)
  3. Audit chain (Merkle proof + reasoning chain replay)
  4. Bitemporal AS OF (0.003 ms at 1M)
  5. Inconsistency detection (PP-107 AUC=1.0 anti-hallucination + adversarial)
  6. Knowledge update speed (SMW 4.174 ms at 1M)
  7. Multi-hop (substrate K-hop on discrete triples)
  8. Legal citation snowball (PP-120 100% 3-hop demo asset)
  9. Algebraic anti-hallucination (PP-107)
  10. Sharding scale contrast (58x sharded vs monolithic)
  11. Counterfactual do() (cycle 175 + Wish 1)
  12. One-shot relation transfer (PP-115)

### Benchmark suite (head-to-head vs baseline LLM)

- HotpotQA (multi-hop QA; cycle 178 PP-99 substrate -0.023 of RAG)
- TriviaQA (encyclopedic; substrate +0.023 over RAG)
- PubMedQA (biomedical; 97.1% RAG parity with PubMedBERT swap)
- BabiLong (long-context distractor; 93% parity vs bare LLM 39%)
- WebQSP / ComplexWebQuestions (KG-QA; substrate K-hop categorical advantage)
- NELL-595 (real KG; substrate native K-hop)
- Wikipedia-subset (5.84M articles pre-trained substrate)

For each:
- Substrate-enhanced vs LLM-only metrics (recall@K, F1, EM)
- Cost-per-query (substrate's 10-30x downstream advantage per HippoRAG)
- Categorical moats demonstrated (audit, GDPR, sharding, counterfactual)

## Dataset authorization (per option A of Exp-Dev request)

AUTHORIZED dataset downloads:
- WebQSP (~500MB) — for R3 real-KG benchmark
- ComplexWebQuestions (~30K questions; ~1GB) — for R3 multi-hop benchmark
- NELL-595 (~50MB) — for I1 real-KG K-hop
- PubMedQA (already cached per cycle 167+174) — for R2 biomedical
- Wikipedia subset (10K dry-run + full 5.84M) — for E1 substrate pre-training
- HotpotQA distractor + fullwiki (already cached) — multi-hop baseline
- MSCOCO subset (~1GB; for E2 Wish 2 multimodal pre-test) — optional

Library installs authorized:
- spaCy + en_core_web_lg + sciSpacy (for NER pipelines)
- Pythia-160M + Pythia-1.4B (for parser + Tier 5)
- bitsandbytes for Llama-8B 4-bit quant (Path B)
- CLIP for multimodal (E2)

Cloud envelope: standard $20-50 per week as needed; Lambda for Llama-8B + larger Tier 5.

## v1 demo build sequencing (4-6 weeks; per evening brief estimate)

Week 1: backend substrate engine wired with all 12 primitives + cascade router
Week 2: benchmark suite (run all 7 benchmarks; compile head-to-head data)
Week 3: frontend two-panel webpage + 12 moat interactive panels
Week 4: integration + smoke tests + curated demo queries
Weeks 5-6: polish + customer-ready presentation materials

## Anchors for new v2.0 capability axis (per option B of Exp-Dev request, lower priority)

Park for later:
- Sparse-VALUE coding 5x drill (in flight; could surface 10-20x per-shard capacity gain)
- Fact representation RETHINK 5x drill (in flight; v3+ architectural exploration)
- Differentiable VSA (Tier 4 alternative)
- Substrate-as-attention production scale (Llama-3B + substrate-KV)
- Inter-shard analogy detection with role vocabulary normalization (Loss 1; P=0.35)

These can dispatch after v1 demo ships. The substrate now has enough empirical depth
to build the demo with current primitives.

## Cross-references
- North star locked: C:/Users/marsh/.claude/projects/d--AI/memory/north_star_functional_system_beats_LLMs.md
- User-stated v1 demo vision (yesterday): conversation context
- Cycle 181 multi-hop architecture convergence: notes/orchestrator_to_research_results_summary_2026-06-08_cycle181.md
- Cycle 183 sharding architecture complete: notes/orchestrator_to_research_results_summary_2026-06-08_cycle183.md
- v1.5 LOCK-IN batch: notes/exp_dev_handoff_research_v1.5_LOCK_batch_2026-06-08.md
- Substrate state-of-play report: chat context

---

**Exp-Dev:** STRATEGIC PRIORITY: build the v1 demo (option C) + AUTHORIZE the dataset
downloads (option A). 4-6 week timeline. North-star-serving deliverable. Substrate
architecture is empirically locked; demo + benchmarks are now the load-bearing work.

This becomes the de facto direction; sparse-VALUE coding + fact-representation rethink
drills continue in research background for v3+ but don't gate demo build.
