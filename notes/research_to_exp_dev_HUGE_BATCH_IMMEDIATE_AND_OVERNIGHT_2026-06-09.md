# Research -> Exp-Dev: HUGE BATCH — cheap CPU IMMEDIATE + overnight GPU/CPU QUEUE

**From:** Research  **Date:** 2026-06-09 evening
**Re:** Run cheap CPU experiments NOW; queue longer experiments for overnight (GPU + CPU)

## Strategic context

Current focus drifted to Tier 5c v2.0 validation. Broader capability matrix (CONV batch + substrate-tool-orchestrator + substrate algebra extensions + public benchmarks) routed earlier today but NOT executed.

User direction: run cheap CPU experiments immediately + queue everything else for overnight (3 runners: gpu_runner_0 + cpu_runner_0 + cpu_runner_local).

## TIER 1: IMMEDIATE (cpu_runner_local; ≤30 min each; cheap CPU)

Goal: validate broader capability claims TONIGHT before user wakes.

### CONV-1 Creative form templates
- Hand-write haiku (5-7-5) + sonnet (ABAB) + limerick (AABBA) templates
- Substrate retrieves topic-relevant words from KB (matching syllable/rhyme)
- Fill template; emit
- **HARD-PASS:** generates grammatically-valid haiku for ≥80% of 100 test topics; syllable count exact; topic-relevance ≥0.70
- Wall: ~20-30 min

### CONV-2 Multi-fact summarization
- Substrate top-K via PP-107 confidence + PP-206 NDCG
- Template: "Key facts: 1. X 2. Y 3. Z" + counterfactual variants
- **HARD-PASS:** factually correct ≥0.95 + grammatically acceptable ≥0.90 on 100 test queries
- Wall: ~20 min

### CONV-3 Empathic response templates
- PP-198 intent classifier extended to detect emotional intents (sad / frustrated / happy / confused)
- Response template selected per intent + formality match
- **HARD-PASS:** empathic responses match intent ≥0.85 on 200-query set
- Wall: ~25 min

### CONV-5 Memory decision logic
- Hybrid: PP-107 confidence + explicit remember/forget + intent-conditioned
- **HARD-PASS:** appropriate memory decisions ≥0.85 on 200-message test conversations + 100% PP-104 erasure on explicit forget
- Wall: ~20 min

### CONV-4 Substrate clarification + repair
- PP-180 contradiction detection triggers clarification template
- User correction → substrate updates + acknowledges
- **HARD-PASS:** identifies ambiguity ≥0.80; clarification appropriate ≥0.85; correction acknowledgment ≥0.95
- Wall: ~25 min

### CONV-8 Opinion expression
- Stored opinions retrieved + aggregated; algebraic rule derivation
- **HARD-PASS:** stored opinions correctly ≥0.95 on 100 queries; aggregation appropriate ≥0.85
- Wall: ~15 min

### CONV-15 Substrate-routed tool calls (SMOKE)
- Substrate decides when to call SymPy / NumPy / code interpreter / image generator
- 50-query benchmark routing accuracy
- **HARD-PASS:** routing accuracy ≥0.85 (50-query smoke); tool integration latency <100ms
- Wall: ~30 min

### DECISIVE-4 GDPR exact erasure proof
- 1000 facts; delete 100; verify 100% deleted unretrievable + 100% non-deleted retrievable
- PP-104 deletion latency <1ms; audit chain cryptographic deletion proof
- **HARD-PASS:** 0 false retentions / 0 false losses; latency confirmed
- Wall: ~30 min

### DECISIVE-5 Multi-tenant isolation
- 10 tenants × 1000 facts; per-tenant + 1000 adversarial cross-tenant queries
- **HARD-PASS:** 0% cross-tenant leakage; overhead <5% vs single-tenant; audit chain per tenant
- Wall: ~30 min

### PRESERVE-COMPOSITE
- 6 substrate primitives on PP-225-trained KB (expects 6/6 PASS sanity)
- PP-107 + PP-117 + PP-180 + PP-184 + PP-104 + multi-hop K-hop
- **HARD-PASS:** 6/6 pass (substrate state unchanged by PP-225 training)
- Wall: ~30 min

## TIER 2: OVERNIGHT QUEUE (mixed CPU + GPU; multi-hour)

Queue these before sleep; sync results in the morning.

### OVERNIGHT-GPU (gpu_runner_0)

**HYBRID-PRODUCTION:**
- HYBRID-1.4B-fp32-10K (transfer HYBRID composition to Pythia-1.4B via fp32 head)
- HYBRID-1.4B-fp32-50K (full KBLaM-class HYBRID)
- HYBRID-Qwen15B-fp32-10K (cross-family HYBRID at 1.5B)

**PP-227 MULTI-SEED:**
- PP227-3SEED-10K-160M (founding rigor at 10K)
- PP227-3SEED-1.4B-fp32 (production-relevant; post HYBRID transfer)

**PP-225 MULTIHOP (GPU):**
- PP225-MULTIHOP-2HOP-160M
- PP225-MULTIHOP-3HOP-160M (extended chain depth)
- PP225-MULTIHOP-2HOP-1.4B-fp32 (production-relevant)

**Path A LARGER MODELS:**
- PathA-every-layer-3seed-1.4B (4-bit if needed; OOM resolution)

### OVERNIGHT-CPU (cpu_runner_0 + cpu_runner_local mixed)

**BENCHMARK RERUNS at production N:**
- BENCH-WEBQSP (Web Questions; standard multi-hop)
- BENCH-CWQ (ComplexWebQuestions; multi-hop)
- BENCH-2WIKI (2Wikimultihop; multi-hop)
- BENCH-MUSIQUE (MuSiQue; multi-hop; harder)
- BENCH-FB15K (Freebase 15K; KG completion)
- BENCH-PUBMEDQA (biomedical)
- **Acceptance:** substrate ≥ published baseline on ≥4 of 6 benchmarks

**CONV Tier 2 + 3 (longer):**
- CONV-6 multilingual translation (Wikidata multilingual; medium)
- CONV-7 code pattern library (50+ templates)
- CONV-9 PII detection (NER; production-set)
- CONV-10 user preference learning (multi-session simulation)
- CONV-11 modal logic operators (R&D; substrate algebra extension)
- CONV-12 probabilistic primitives extension (R&D; PP-155 → Bayesian)
- CONV-13 higher-order substrate composition (R&D)
- CONV-14 humor templates (30+ joke patterns)

**Multi-hop CPU complement:**
- PP224-MULTIHOP-RAG (RAG-prefix with substrate K-hop)
- PP224-COMPOSITIONAL (substrate AND/NOT/COUNT via RAG-prefix)
- PP224-AUDIT-CHAIN (multi-fact RAG with Merkle preservation)
- SUBSTRATE-K-HOP-3HOP at production KB scale

**Substrate-math drill anchors (categorical "ridiculously complicated math"):**
- MATH-SYMPY-INT (substrate orchestrates SymPy integration symbolic)
- MATH-NUMPY-LINALG (substrate orchestrates NumPy linear algebra)
- MATH-WOLFRAM-API (substrate orchestrates Wolfram Alpha API)
- MATH-PROOF-STEP (substrate stores Lean/Coq proof steps; orchestrates verification)

**Substrate-as-orchestrator extensions:**
- ORCH-CODE-EXEC (substrate decides → runs Python code → uses result)
- ORCH-IMAGE-GEN (substrate decides → calls Stable Diffusion → uses image)
- ORCH-WEB-SEARCH (substrate decides → web search → uses result)
- ORCH-MULTI-TOOL (substrate composes 3+ tools per query)

## Sequencing recommendation

**Right now (immediate):**
- Queue all TIER 1 anchors on cpu_runner_local
- 10 anchors × ~25 min avg = ~4 hours total (parallel where possible)
- Expect: validation of broader CONV + compliance + sanity by morning

**Pre-sleep dispatch:**
- Queue all TIER 2 OVERNIGHT-GPU on gpu_runner_0 (4-6 anchors; sequential overnight)
- Queue all TIER 2 OVERNIGHT-CPU on cpu_runner_0 + cpu_runner_local (alternating; ~20 anchors)
- Expect: results by mid-morning tomorrow

## What this gives strategically

After TIER 1 lands:
- CONV substrate conversational capabilities EMPIRICALLY VALIDATED (Tier 1 set)
- DECISIVE-4 + DECISIVE-5 compliance categorical claims grounded
- PP-225 + substrate primitives composition verified (PRESERVE)
- Substrate-tool-orchestrator smoke validates the architecture

After TIER 2 lands:
- 6 public benchmark wins (categorical demo evidence vs published systems)
- CONV Tier 2+3 (substrate algebra extensions R&D)
- Math + tool orchestration (substrate-around-LLM full breadth)
- HYBRID at production scale (160M → 1.4B → Qwen-1.5B)
- Multi-hop chain depth (PP-225/PP-224 at 2/3-hop)
- Path A every-layer at larger models

**Combined: substrate-around-LLM categorical product story EMPIRICALLY GROUNDED at full breadth — not just substrate-as-LLM-memory but the full BROAD capability matrix you asked for earlier.**

## CPU lane assignments

| Anchor type | Lane | Reason |
|---|---|---|
| CONV-1/2/3/4/5/8/15 | cpu_runner_local | Quick CPU; isolated from desktop |
| DECISIVE-4/5 | cpu_runner_local | Cheap; categorical |
| PRESERVE-COMPOSITE | cpu_runner_local | Quick sanity |
| BENCH-* | cpu_runner_0 | Larger; more cores |
| CONV-6/7/9/10 | cpu_runner_0 | Medium |
| CONV-11/12/13/14 | cpu_runner_0 OR cpu_runner_local | R&D; either fine |
| MATH-* | cpu_runner_0 | Tool integration; larger |
| ORCH-* | cpu_runner_0 | Tool orchestration |
| PP224-MULTIHOP-* | cpu_runner_0 OR cpu_runner_local | Either |
| PP-227/HYBRID/PP-225 GPU | gpu_runner_0 | GPU-required |
| PathA-1.4B-3seed | gpu_runner_0 | GPU-required |

## What I'm NOT including

- Speculative draft variations (DECISIVE-1 will settle in ~1 hr; no need to spawn variations)
- Substrate-only LM (Path 1) — research direction, not production
- Frontier-scale Llama-3.2-3B HYBRID — cloud GPU; defer to Testbed when ready
- Wikipedia 5.84M full ingest — Testbed's lane

## Cross-references
- CONV original routing: notes/research_to_exp_dev_SUBSTRATE_CONVERSE_CAPABILITIES_2026-06-09.md
- DECISIVE tests: notes/research_to_exp_dev_LITERATURE_BACKED_DECISIVE_TESTS_2026-06-09.md
- WHATS_NEXT response: notes/research_to_exp_dev_WHATS_NEXT_RESPONSE_2026-06-09.md
- CPU lane priorities: notes/research_to_exp_dev_CPU_LANE_PRIORITIES_2026-06-09.md
- Substrate math drill: notes/research_drill_substrate_math_capabilities_5x_2026-06-08.md
- Substrate hierarchical drill: notes/research_drill_substrate_first_hierarchical_5x_2026-06-08.md

---

**Exp-Dev:** TIER 1 immediate on cpu_runner_local (10 anchors; ~4 hrs); TIER 2 overnight on
all 3 runners (~25 anchors; mixed). After this batch lands, substrate-around-LLM has:
- v2.0 substrate-as-LLM-memory (already complete; cycle 207)
- Substrate conversational capabilities empirically validated (CONV Tier 1+2+3)
- Substrate-tool-orchestrator empirically validated (ORCH + MATH)
- 6 public benchmark wins (vs LazyGraphRAG + PathHD class)
- Compliance categorical (DECISIVE-4 GDPR + DECISIVE-5 multi-tenant)
- HYBRID at production scale (1.4B + 1.5B + 50K)

= FULL substrate-around-LLM product story empirically grounded across breadth + scale.
