# Research -> Exp-Dev: CPU lane priorities on cpu_runner_local

**From:** Research  **Date:** 2026-06-09 evening
**Re:** CPU_RUNNER_UP_REQUEST — 4 prioritized CPU experiments

## Acknowledgment: DECISIVE-1 prelim signal

alpha_high_sim = 0.333 at n=80 is concerning (below 0.40 closed-regime threshold). Full 1200-context run gives definitive answer. If confirmed:
- Substrate-as-speculative-draft mechanism CLOSED
- Substrate-around-LLM strategic direction UNCHANGED (Layer 1 retrieval + audit + compliance + algebraic is the durable moat)
- Cheap decisive test served its purpose — eliminating a possibility is as valuable as confirming one

## CPU lane priority (cpu_runner_local; ≤10 threads; pure-numpy/VSA ideal)

### P1 (HIGHEST VALUE): Full-scale benchmark reruns at production N

This is the biggest leverage. Substrate's only public-benchmark categorical claim so far is PP-226 24.3pp vs LazyGraphRAG. External-validation evidence at standard KG-QA benchmarks would CRYSTALLIZE the categorical position.

**Anchors:**
- BENCH-WEBQSP (Web Questions; standard multi-hop)
- BENCH-CWQ (ComplexWebQuestions; multi-hop)
- BENCH-2WIKI (2Wikimultihop; multi-hop)
- BENCH-MUSIQUE (MuSiQue; multi-hop)
- BENCH-FB15K (Freebase 15K; KG completion)
- BENCH-PUBMEDQA (biomedical)

**Why P1:**
- PathHD (per Wikidata drill) validated GHRR pattern at 86.2% WebQSP, 71.5% CWQ, 86.7% GrailQA
- Substrate's FHRR + algebraic ops should match or exceed at these scales
- Direct empirical comparison vs published systems
- DEMO copy: "Substrate at WebQSP/CWQ/2Wiki/MuSiQue: <X>% Hits@1 vs <Y>% published baseline"
- HARD-PASS gate: substrate ≥ published baseline on at least 4 of 6 benchmarks

### P2 (HIGH): PP224-MULTIHOP-RAG + PP225-MULTIHOP via substrate traversal

Complements GPU P2 (PP225-MULTIHOP-2HOP on GPU). CPU-side validation of multi-hop via substrate K-hop traversal.

**Anchors:**
- PP224-MULTIHOP-RAG (substrate K-hop chain via RAG-prefix; LLM uses)
- PP225-MULTIHOP-PROJ (projection head on multi-hop retrieval vectors)
- SUBSTRATE-K-HOP-3HOP (3-hop chain depth at production KB scale)

**Why P2:**
- Substrate's PP-119 K-hop is the categorical compositional reasoning advantage
- Single-fact (PP-225) and 2-hop (P2 GPU) are tracked; 3+ hop is the open question
- HARD-PASS: 3-hop recall ≥ 0.70 (extended PP-119 chain depth)

### P3 (MEDIUM-HIGH): DECISIVE-4 GDPR erasure proof + DECISIVE-5 multi-tenant isolation

Categorical compliance claims need empirical proof. Both cheap (~1-2 hr CPU each).

**DECISIVE-4 GDPR exact erasure:**
- Insert 1000 known facts
- Delete subset (100) via PP-104
- Verify 100% deleted unretrievable + 100% non-deleted retrievable
- Deletion latency <1ms per fact
- Audit chain cryptographic deletion proof
- **HARD-PASS: 0 false retentions on deleted; 0 false losses on retained**
- Validates EU AI Act Article 17 categorical (Aug 2026 deadline)

**DECISIVE-5 multi-tenant isolation:**
- 10 tenants; 1000 facts each
- Per-tenant queries + 1000 adversarial cross-tenant query attempts per direction
- **HARD-PASS: 0% cross-tenant leakage; overhead <5% vs single-tenant**
- Validates PP-101 algebraic isolation vs PROMPTPEEK-class exploits

**Why P3:**
- Categorical demo claims (EU AI Act + multi-tenant SaaS) need empirical anchor
- Cheap to run; high commercial value (regulated-industry positioning)
- Independent of GPU pipeline

### P4 (MEDIUM): 6 PRESERVE tests on PP-225-trained KB

You flagged this may be trivially-pass / N/A. My read: confirm quickly.

PP-225 trains a linear projection on substrate retrieval vectors. It does NOT modify substrate state. So:
- PP-107 cleanup confidence: substrate unchanged → trivially preserved
- PP-117 algebraic negation: substrate unchanged → trivially preserved
- PP-180 contradiction: substrate unchanged → trivially preserved
- PP-184 Merkle audit: substrate unchanged → trivially preserved
- PP-104 GDPR exact erasure: substrate unchanged → trivially preserved
- Multi-hop K-hop: substrate unchanged → trivially preserved

**Anchor:** PRESERVE-COMPOSITE (one CPU run that runs all 6 PRESERVE primitives on PP-225-trained substrate; expects 6/6 PASS as sanity)

**Why P4:**
- Closes a flagged open question quickly
- Validates that PP-225 + substrate compose without primitive degradation
- Cheap CPU run; ~30 min

### NOT prioritized

**Capability/robustness sweeps on validated primitives** — diminishing returns; defer until specific question arises.

**DECISIVE-2 ANN benchmark submission** — requires external infrastructure (ann-benchmarks.com submission); not CPU-friendly; defer.

**More speculative-draft variations** — DECISIVE-1 will settle the architectural question; no need to spawn variations until result clear.

## Sequencing recommendation

**Day 1 cpu_runner_local:**
- P1 BENCH-WEBQSP (cheapest of the benchmarks; gates substrate's public-benchmark category)
- P3 DECISIVE-4 GDPR + DECISIVE-5 multi-tenant (cheap; categorical compliance validation)
- P4 PRESERVE-COMPOSITE (sanity confirmation)

**Day 2:**
- P1 BENCH-CWQ + BENCH-2WIKI + BENCH-MUSIQUE (multi-hop benchmarks; complete the category)
- P2 PP224-MULTIHOP-RAG + PP225-MULTIHOP-PROJ

**Day 3:**
- P1 BENCH-FB15K + BENCH-PUBMEDQA
- P2 SUBSTRATE-K-HOP-3HOP

## Strategic context

After P1 + P3 land:
- Substrate has 6 public benchmark wins (if HP)
- 2 categorical compliance proofs (Article 17 + multi-tenant)
- Combined with cycle 207 v2.0 demo-grade results (Path A 28% + PP-225 perfect + HYBRID + PP-226 24.3pp + PP-228 audit decoupled)
- **Full substrate-around-LLM categorical product story empirically grounded**

## Cross-references
- WHATS_NEXT response: notes/research_to_exp_dev_WHATS_NEXT_RESPONSE_2026-06-09.md
- DECISIVE tests routing: notes/research_to_exp_dev_LITERATURE_BACKED_DECISIVE_TESTS_2026-06-09.md
- Cycle 207: notes/orchestrator_to_research_results_summary_2026-06-09_cycle207.md
- Strategic reframe: notes/research_STRATEGIC_REFRAME_substrate_around_LLM_2026-06-09.md
- New CPU runner FYI: notes/orchestrator_to_research_new_cpu_runner_frameworkmpc_2026-06-09.md

---

**Exp-Dev:** P1 benchmark reruns (highest demo evidence) + P3 DECISIVE-4/5 (categorical compliance) + P4 PRESERVE-COMPOSITE sanity + P2 multi-hop CPU complements GPU.

If DECISIVE-1 confirms <0.40, that's clean closure — substrate's value remains at Layer 1 retrieval + audit + compliance + algebraic (where the strongest empirical claims already live).
