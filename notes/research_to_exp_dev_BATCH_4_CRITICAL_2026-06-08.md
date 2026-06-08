# Research -> Exp-Dev: BATCH 4 — CRITICAL untapped experiments

**From:** Research  **Date:** 2026-06-09 ~04:30 UTC
**Re:** User asking for more critical experiments. Today's 90+ anchors covered breadth; this batch is DEMO/PRODUCT CRITICAL gaps.

## PRIORITY A: Vertical empirical proofs (demo + customer pipeline)

**A1: PACER legal corpus extension** (verticals drill flagged as decisive empirical risk)
- Substrate-product reading: extend PP-120 legal citation snowball to real PACER corpus (vs cycle 195's curated 1000-seed); test generalization
- Tier: LOCAL CPU
- HARD-PASS: recall=precision ≥ 0.95 on 1000 real PACER cases

**A2: Drug-drug interaction K-hop (medical)**
- Substrate-product reading: DrugBank ingestion; substrate K-hop over drug-interaction graph; predict 1000 known interactions
- Tier: LOCAL CPU
- HARD-PASS: drug interaction recall ≥ 0.90 + audit chain per prediction

**A3: FDA-grade audit chain regulatory simulation**
- Substrate-product reading: simulate FDA audit on substrate-mediated medical AI decisions; trace 100 decisions end-to-end
- Tier: LOCAL CPU
- HARD-PASS: 100% audit chain completeness; all decisions traceable to source facts

**A4: SEC 10-K filing substrate**
- Substrate-product reading: ingest 100 SEC 10-K filings; substrate retrieval over financial entities
- Tier: LOCAL CPU
- HARD-PASS: cross-filing query recall ≥ 0.85 on 100 test questions

## PRIORITY B: Substrate-augmented LLM benchmarks (already in BATCH 3; ELEVATING priority)

**B1: VER-MMLU** — substrate-augmented small LLM on MMLU subset
- 1000 questions; Qwen-1.5B + substrate vs gpt-4o-mini bare
- HARD-PASS: substrate-augmented Qwen-1.5B ≥ gpt-4o-mini bare on knowledge-intensive subset

**B2: VER-GSM8K** — substrate-augmented LLM on math
- 100 GSM8K problems; substrate provides intermediate math facts
- HARD-PASS: substrate-augmented Qwen-1.5B ≥ +10pp over Qwen-1.5B bare

**B3: VER-TRIVIAQA** — substrate-augmented LLM on TriviaQA
- 500 TriviaQA questions; substrate has facts; LLM formats
- HARD-PASS: substrate-augmented ≥ 0.90 (vs gpt-4o-mini bare ~0.75)

**B4: Direct substrate+small-LLM vs gpt-4o-mini head-to-head** (categorical demo claim validation)
- 100 mixed-domain questions; full comparison
- HARD-PASS: substrate-augmented Qwen-1.5B wins ≥ 50% of knowledge tasks at <100x cost

## PRIORITY C: Encoder drift critical radius (extreme-scale drill flagged as next critical)

**C1: Encoder drift critical-mass test (E2)**
- 10M facts; simulate 6 months drift via fine-tuned encoder; measure recall@1 degradation per 0.05 drift unit
- Tier: LOCAL GPU (~4 hr)
- HARD-PASS: empirical critical radius identified (drift at which recall drops below 0.70); anchors production maintenance cadence

## PRIORITY D: Production hardening

**D1: Concurrent multi-user load test**
- 100 concurrent queries; substrate behavior under contention
- HARD-PASS: P95 latency < 5ms + no fact corruption

**D2: Substrate failover (shard loss)**
- Simulate loss of 1 of 10 shards; recovery via redundancy
- HARD-PASS: recovery to baseline recall within 60s

**D3: Hot-swap encoder**
- Switch from bge-small to bge-large mid-deployment; substrate continues serving
- HARD-PASS: zero downtime + recall preservation

**D4: Online sleep-defrag (continuous)**
- Sleep-defrag running while queries served; quality preservation
- HARD-PASS: query quality stable; defrag progress measurable

## PRIORITY E: Categorical demo moments

**E1: Substrate forgetting test (demonstrates GDPR categorical)**
- Insert fact about person X; demonstrate substrate retrieves; delete fact; substrate AND LLM context confirm cannot retrieve
- HARD-PASS: post-delete recall = 0.000; LLM confirms (via PP-186 PII strip-inject pattern)

**E2: Substrate audit forensics**
- For any answer: trace ALL contributing facts; show Merkle proof
- HARD-PASS: complete audit chain rendered for 100% of answers; cryptographically verifiable

**E3: Substrate multi-tenant isolation demo (PP-101 extension)**
- 3 tenants with overlapping schemas; cross-tenant query attempts
- HARD-PASS: 0.000 cross-tenant leakage + each tenant's own queries at full performance

**E4: Substrate counterfactual demo (Pearl do() in realistic domain)**
- Real domain (e.g., economic policy; medical intervention); substrate counterfactual reasoning
- HARD-PASS: do() reasoning correct ≥ 0.85 vs ground truth

## PRIORITY F: TALKS extensions (substrate conversational completeness)

**F1: TALKS-6 abstention dialogue**
- When substrate doesn't know, substrate gracefully says so + suggests where to find
- HARD-PASS: appropriate abstention ≥ 0.95 + helpful redirect rate ≥ 0.80

**F2: TALKS-7 clarification turns**
- Substrate asks for clarification when query ambiguous
- HARD-PASS: ambiguity detected ≥ 0.85 + clarification useful ≥ 0.75

**F3: TALKS-8 conversational repair**
- Substrate detects own error in prior turn; corrects
- HARD-PASS: error self-detection ≥ 0.80 + repair appropriate ≥ 0.90

## PRIORITY G: Universal interface (substrate as standard)

**G1: Substrate exports to Datalog**
- Substrate-stored facts → Datalog rules
- HARD-PASS: round-trip preserves 100% of substrate semantics

**G2: Substrate exports to SPARQL**
- Substrate-stored facts → SPARQL queryable
- HARD-PASS: 100% query equivalence vs native substrate

**G3: Substrate REST API**
- /retrieve + /add + /delete + /audit endpoints
- HARD-PASS: API matches substrate-native query semantics

## Recommended sequencing

**Day 1 (cheapest CPU):**
- A1 PACER legal extension (highest demo-critical; verticals drill flagged)
- A2 DDI medical (categorical healthcare claim)
- E1 forgetting test (visceral demo moment)
- E2 audit forensics

**Day 2:**
- B1/B2/B3 substrate-augmented benchmarks (categorical demo claim validation)
- D1 concurrent multi-user

**Day 3:**
- C1 encoder drift critical-mass (~4hr GPU; production maintenance cadence)
- A3 FDA-grade audit simulation
- B4 head-to-head substrate vs gpt-4o-mini

**Day 4-5:**
- A4 SEC 10-K substrate
- D2/D3/D4 production hardening
- F1/F2/F3 TALKS extensions
- E3/E4 multi-tenant + counterfactual

## Critical priorities summarized

**TOP 5 MOST CRITICAL** (highest demo/customer leverage):
1. **A1 PACER legal extension** (verticals drill named it; demo decisive)
2. **B4 substrate+small-LLM vs gpt-4o-mini head-to-head** (categorical claim empirical)
3. **C1 encoder drift critical radius** (anchors production maintenance cadence; gates 1B-scale)
4. **E1 forgetting test** (visceral demo moment; GDPR/HIPAA categorical)
5. **E2 audit forensics** (categorical demo moment; regulated-industries)

## Cross-references
- Verticals drill (flagged A1): notes/research_drill_substrate_verticals_5x_2026-06-08.md
- Emergent extreme-scale drill (flagged C1): notes/research_drill_substrate_emergent_extreme_scale_5x_2026-06-08.md
- BATCH 3 (B1-B4 elevation): notes/research_to_exp_dev_BATCH_3_FRESH_30_ANCHORS_2026-06-08.md
- STATE OF PLAY: notes/research_STATE_OF_PLAY_2026-06-08.md

---

**Exp-Dev:** 25+ critical anchors filed. TOP 5 are demo/customer-leverage critical.
A1 (PACER) + B4 (head-to-head categorical) + C1 (encoder drift production) + E1
(forgetting test demo) + E2 (audit forensics) are the must-runs for demo + customer
positioning.

When TALKS-1/2/3 + T5C-B1 + BATCH 3 anchors continue draining, this batch refills.
