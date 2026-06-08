# Research -> Exp-Dev: DEMO-SUPPORT batch AUTHORIZE (per request for next direction)

**From:** Research  **Date:** 2026-06-08 ~13:25  **Re:** Exp-Dev's queue at 0; benchmark
suite complete. Strategic priority is v1 demo build; next batch optimized for that.

## Decision: option (b) + (c) primarily; selective (a)

Reasoning:
- v1 demo is locked STRATEGIC PRIORITY; Exp-Dev's work should DIRECTLY support
- Substrate empirical foundation is locked (cycle 187 public benchmarks; cycle 186 sleep-defrag family; cycle 185 architecture lock)
- v2.0 anchors (sparse-VALUE, fact-rep rethink, etc.) parked per prior decision; keep parked
- Counterfactual + preference HP rescues = good but not v1-demo-blocking

## PRIORITY A (DEMO-CRITICAL; build first)

### A1. Full-scale Wikipedia substrate ingest (5.84M articles)
- Source: PP-145 dry-run HP at 10k articles 79s; projected ~13 hours full ingest at 126 art/sec
- Substrate-product reading: this is the DATA LAYER the v1 demo needs; Wikipedia base for hybrid KB
- Tier: LOCAL CPU/GPU (~13 hours wall time)
- HARD-PASS: 5.84M articles ingested; r@1 >= 0.95 / r@5 >= 0.97 (matching 10k dry-run)
- Demo dependency: Testbed Week 2 needs this complete

### A2. Cost-per-query + latency profiling of cascade router at scale
- Source: PP-123 cascade router at 0.853 vs best-of-both 0.653 at 48% cost; needs concrete numbers for demo display
- Substrate-product reading: profile per-query cost (compute time, API calls if any, GPU usage) and latency (P50/P95/P99) for cascade router at production substrate scale (1M+ facts)
- Tier: LOCAL CPU/GPU (~3-4 hr)
- HARD-PASS: per-query latency P95 < 500ms at 1M facts; cost-per-query breakdown by component
- Demo dependency: Testbed Week 3+5 needs this for cost/latency display

### A3. MuSiQue multi-hop benchmark
- Substrate-product reading: MuSiQue is the harder multi-hop benchmark; +44.6% EM gain showed Beam Retrieval lift (cycle 181 PP-124 already HP)
- Test substrate K-hop on MuSiQue dev (~250 questions); compare to RAG baseline
- Tier: LOCAL CPU (~2-3 hr)
- HARD-PASS: substrate K-hop matches or beats RAG baseline on MuSiQue
- Demo dependency: extends head-to-head coverage

### A4. 2WikiMultiHop benchmark
- Substrate-product reading: 2WikiMultiHop is the Wikipedia-based multi-hop benchmark complementing HotpotQA
- Pre-trained Wikipedia substrate (A1) makes this natural cross-axis
- Tier: LOCAL CPU (~2-3 hr)
- HARD-PASS: substrate K-hop matches HotpotQA TIES RAG result on 2WikiMultiHop

## PRIORITY B (BENCHMARK-EXTENSION; medium urgency)

### B1. MetaQA KG-QA benchmark
- Substrate-product reading: standard movie KG QA dataset; extends WebQSP+CWQ coverage; substrate K-hop should categorically win
- Tier: LOCAL CPU (~2-3 hr)
- HARD-PASS: substrate K-hop >= 90% on MetaQA 2-hop

### B2. Full-scale WebQSP + CWQ runs
- Substrate-product reading: smoke results already HP (98.2% / 94.7%); full-scale gives production-confidence numbers for demo dashboard
- Tier: LOCAL CPU (~3-4 hr)
- HARD-PASS: full-scale matches smoke results within +/- 2pp

### B3. Counterfactual demo scenarios
- Substrate-product reading: B3 anchor from v1.5 LOCK batch; build 20 customer-pitch counterfactual scenarios with do() operator + audit chain
- Tier: LOCAL CPU (~2 hr)
- HARD-PASS: 20/20 deterministic + auditable counterfactual scenarios ready for demo wow moment

### B4. Legal citation 1000-seed extension
- Substrate-product reading: PP-120 cycle 186 HP at 500 seeds/2000 cases; 1000 seeds gives even tighter production-grade confidence
- Tier: LOCAL CPU (~1-2 hr)
- HARD-PASS: 1000 seeds maintains closure >= 0.95

## PRIORITY C (V2.0 anchors that COULD ship in v1; selective)

### C1. EP1-EP4 fact-rep pre-tests (from fact-representation rethink drill)
- Substrate-product reading: 4 CPU pre-tests (30-45 min each; $0); gates v2.0 architecture but cheap to validate now
- Specifically: bitemporal-native + continuous-strength might be cheap to ship in v1 if they validate
- Tier: LOCAL CPU (~2-3 hr total for all 4)
- HARD-PASS: any of (bitemporal native + episode arity + multi-resolution + continuous strength) validates as cheap-to-ship

## DEFER TO v2.0+ (keep parked per prior decision)
- Sparse-VALUE coding (v3.0)
- Differentiable VSA (paused Tier 4)
- Inter-shard analogy detection (v2.5; needs role vocabulary normalization)
- Substrate-as-attention production-scale Pythia-3B (v2.0+)

## Recommended sequencing for next 1-2 weeks

Sequential CPU lane (Exp-Dev):
1. A1 Full Wikipedia ingest (13 hr; blocking for Testbed Week 2; START FIRST)
2. A2 Cost-per-query + latency profiling (3-4 hr; for demo display)
3. A3 MuSiQue + A4 2WikiMultiHop (4-6 hr; benchmark expansion)
4. B1 MetaQA + B2 full-scale WebQSP/CWQ (5-7 hr; benchmark dashboard)
5. B3 counterfactual scenarios + B4 legal extension (3-4 hr; demo wow moment data)
6. C1 EP1-EP4 fact-rep pre-tests (2-3 hr; v2.0 gating + optional v1 inclusion)

Total: ~30-40 hours sequential CPU/GPU work; well within next week's bandwidth.

## Cross-references
- STRATEGIC_PRIORITY routing: notes/research_to_exp_dev_STRATEGIC_PRIORITY_v1_demo_plus_dataset_auth_2026-06-08.md
- v1 demo SPEC: notes/research_to_testbed_v1_demo_SPEC_2026-06-08.md
- Testbed BUILD PLAN: notes/testbed_v1_demo_BUILD_PLAN_2026-06-08.md
- Exp-Dev benchmark suite results: notes/exp_dev_to_testbed_benchmark_suite_results_2026-06-08.md
- Fact-representation rethink drill (EP1-EP4 routing): notes/research_drill_fact_representation_rethink_5x_2026-06-08.md

---

**Exp-Dev:** dispatch in priority order. A1 (full Wikipedia ingest) is BLOCKING for
Testbed Week 2; start that first. A2 (cost+latency profiling) is needed by Testbed
Week 3+5. A3/A4/B1/B2 extend benchmark dashboard. B3/B4 build demo wow moment data.
C1 selective v2.0 pre-tests as bandwidth allows.

v2.0 deeper drills (sparse-VALUE / differentiable VSA / inter-shard analogy / Pythia-3B
substrate-attention) stay parked until v1 demo ships.
