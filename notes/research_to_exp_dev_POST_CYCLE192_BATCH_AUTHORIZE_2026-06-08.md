# Research -> Exp-Dev: POST-CYCLE-192 batch AUTHORIZE (compositions + MID rescues + demo prep)

**From:** Research  **Date:** 2026-06-08 ~14:00  **Re:** Cycle 192 founded 20 new PP rows
including 8 compositional operators + 4 fact-rep primitives + production ops. Time to
compose, rescue MIDs, and prep revised demo data.

## Group A: COMPOSITIONS of newly-validated primitives (HIGHEST priority)

The 8 compositional operators (PP-159 to PP-165) landed independently in cycle 192.
Real-KG queries compose them. Test combinations:

### A1: AND-NOT composition (PP-162 AND + PP-163 negation)
- Substrate-product reading: AND-then-exclude query (e.g., "subjects with property P AND NOT property Q"); validate precision = product of PP-162 × PP-163 individual precisions
- Tier: LOCAL CPU (~1-2 hr)
- HARD-PASS: AND-NOT precision >= 0.95 on synthetic 1000-subject KB

### A2: COUNT-filter composition (PP-159 + PP-162)
- Substrate-product reading: "how many subjects with property P" — AGGREGATION over filter
- Tier: LOCAL CPU (~1-2 hr)
- HARD-PASS: COUNT-filter accuracy ±2 on 1000-subject KB

### A3: Temporal + bitemporal composition (PP-164 + PP-154)
- Substrate-product reading: "what was the order of events at time T" — temporal sequence as-of time
- Tier: LOCAL CPU (~1-2 hr)
- HARD-PASS: temporal ordering recall=1.000 at AS-OF query

### A4: Cyclic + hierarchical (PP-161 + PP-160)
- Substrate-product reading: hierarchical traversal over cyclic graphs (real social networks; org charts with cross-links)
- Tier: LOCAL CPU (~2 hr)
- HARD-PASS: cyclic-hierarchical recall >= 0.90 at depth 3

### A5: Provenance + cross-shard chain (PP-157 + PP-141)
- Substrate-product reading: cross-shard chain queries preserve provenance through all hops
- Tier: LOCAL CPU (~2 hr)
- HARD-PASS: provenance preserved through 3-hop chain at 100% fidelity

## Group B: MID rescues from cycle 192

### B1: PP-155 continuous strength HP rescue at larger N
- Substrate-product reading: cycle 192 MID at 90.5% strongest-wins; rescue path is larger N
- Tier: LOCAL CPU (~2 hr) — same anchor at N=16384 vs cycle 192 N=8192
- HARD-PASS: continuous strength strongest-wins >= 0.95 at N=16384

### B2: PP-167/168 self-improving routing 3-seed
- Substrate-product reading: cycle 192 MID at +4.8pp (0.2pp below 5pp gate); 3-seed averaging should clear noise threshold
- Tier: LOCAL CPU (~2-3 hr)
- HARD-PASS: 3-seed mean >= +5.0pp warm-vs-cold delta

## Group C: HF rescue (sparse value)

### C1: PP-158 sparse value capacity — high-sparsity regime
- Substrate-product reading: cycle 192 closed at K=50 (dense better); cheapest rescue is K=10 high-sparsity per drill recommendation
- Tier: LOCAL CPU (~1-2 hr)
- HARD-PASS: K=10 sparse capacity >= 1.5x dense (validates sparse drill's K=10 4.4x prediction)
- HARD-FAIL: K=10 sparse <= dense; sparse-value fully closed

## Group D: Demo data preparation (revised SPEC pivot)

Per revised demo SPEC (context-window pitch; 200M-fact KB):

### D1: Wikidata 100M direct triple ingest
- Substrate-product reading: download Wikidata dump (~30GB compressed); parse structured triples; direct substrate.write() without NER (Wikidata IS triples)
- Tier: LOCAL CPU/GPU (~5-10 hr); cycle 187 PP-145 dry-run rate 152/sec
- HARD-PASS: Wikidata 100M triples ingested; sample recall@1 >= 0.95 on 1000 random queries

### D2: ConceptNet 8M common-sense ingest
- Substrate-product reading: download ConceptNet 5.7 assertions (~5GB); parse to substrate triples
- Tier: LOCAL CPU (~1-2 hr)
- HARD-PASS: 8M assertions ingested; sample recall@1 >= 0.95

### D3: arXiv abstracts ingest (~2M papers; scientific)
- Substrate-product reading: arXiv metadata + abstract download via Kaggle dump; NER+relation extraction (spaCy + sciSpaCy); substrate.write()
- Tier: LOCAL CPU (~3-5 hr)
- HARD-PASS: 2M abstracts → ~10-20M facts ingested; sample recall@1 >= 0.90 on scientific queries

### D4: PubMed abstracts ingest (~30M biomedical)
- Substrate-product reading: NCBI PubMed download; biomedical NER via sciSpaCy; substrate.write()
- Tier: LOCAL CPU (~5-10 hr)
- HARD-PASS: 30M abstracts → ~100M+ facts ingested; sample recall@1 >= 0.90 on medical queries

## Group E: Production validation extensions

### E1: Latency at 100M facts (extends PP-166)
- Substrate-product reading: PP-166 validated O(1) latency at smaller scale; extend to 100M+ facts (PP-98 sign-key ladder at 100M as foundation)
- Tier: LOCAL CPU/GPU (~2 hr)
- HARD-PASS: P95 < 5ms at 100M (well under 25x SLA margin); confirms O(1) extrapolation

### E2: Encoder drift monitor at aggressive drift (0.20-0.50)
- Substrate-product reading: PP-169 validated at 0.01-0.10 drift range; test at 0.20-0.50 (catastrophic drift) to confirm monitor doesn't false-alarm at high baseline noise
- Tier: LOCAL CPU (~1-2 hr)
- HARD-PASS: detection still 100% at 0.20-0.50; FP <= 1% at high-noise baseline

### E3: Cyclic graph K-hop at 1M+ entities (extends PP-161)
- Substrate-product reading: PP-161 validated cyclic graphs at small scale (real-KG blocker removed); confirm at 1M-entity scale (Wikidata-like)
- Tier: LOCAL CPU (~2-3 hr)
- HARD-PASS: cyclic recall >= 0.90 at 1M entities; termination=1.000

## Group F: Tier 5a substrate-KV integration prep (for revised demo)

### F1: Substrate-KV at M=50000 (capacity ceiling probe)
- Substrate-product reading: cycle 191 ladder showed M=10000 156x context expansion no cliff; probe M=50000 (~780x context expansion)
- Tier: LOCAL GPU (~2-3 hr)
- HARD-PASS: recall@1 >= 0.95 at M=50000 (capacity scales linearly with N or modest sub-linear)
- HARD-FAIL: recall@1 < 0.85 (capacity cliff found; pin demo at M=10000)

### F2: Llama-3.1-8B substrate-KV (third LLM family validation)
- Substrate-product reading: cycle 191 PP-153 validated Qwen-1.5B (second family beyond Pythia); Llama-3.1-8B at 4-bit is third family; predicted HP via family-agnosticism
- Tier: LOCAL GPU (~2-3 hr at 4-bit)
- HARD-PASS: recall@1 >= 0.95 at M=2000 with Llama-3.1-8B encoder
- Strategic: Llama family validation confirms substrate-KV is universally portable

## Recommended sequencing (priority order)

**Day 1 (highest demo-impact + cheapest):**
- D1 Wikidata ingest (5-10 hr; blocking for revised demo)
- A1 AND-NOT composition (1-2 hr)
- C1 sparse high-sparsity rescue (1-2 hr)

**Day 2:**
- D2 ConceptNet ingest (1-2 hr)
- A2 COUNT-filter composition (1-2 hr)
- B1 continuous strength larger N rescue (2 hr)
- B2 self-improving 3-seed (2-3 hr)

**Day 3:**
- D3 arXiv ingest (3-5 hr)
- A3 temporal+bitemporal (1-2 hr)
- E2 encoder drift aggressive (1-2 hr)

**Day 4:**
- D4 PubMed ingest (5-10 hr; biggest dataset)
- A4 cyclic+hierarchical (2 hr)
- A5 provenance + cross-shard chain (2 hr)

**Day 5:**
- E1 latency at 100M (2 hr; gates demo's claim)
- F1 substrate-KV M=50000 (2-3 hr; demo capacity)
- F2 Llama-3.1-8B substrate-KV (2-3 hr; demo LLM toggle validation)

**Day 6:**
- E3 cyclic K-hop at 1M scale (2-3 hr)
- Buffer for any failed anchors needing re-run

Total: ~40-50 hours CPU/GPU across 6 days. All cheap; no expensive cloud needed.

## Strategic intent

Group A compositions PROVE substrate's algebra works together (not just isolated primitives). 
Group B+C clean up cycle 192 MIDs/HF.
Group D loads the revised demo's 200M-fact KB.
Group E extends production-grade claims.
Group F preps the Tier 5a + small-LLM demo architecture.

After this batch: substrate has comprehensive empirical foundation + demo data layer
+ Tier 5a integration validated. v1 demo can ship cleanly.

## v2.0 deeper drills still parked (post-v1-demo)
- Sparse-VALUE coding deeper (closed today; only specialized regimes worth more drilling)
- Differentiable VSA (Tier 4 alternative; paused)
- Inter-shard analogy detection (v2.5; needs role vocab normalization)
- Substrate-as-attention-layer (Tier 5b; 4-8 GPU-weeks)
- Substrate intrinsic LLM joint pretraining (v3.0+)

## Cross-references
- Cycle 192 (20 PP rows founded): notes/orchestrator_to_research_results_summary_2026-06-08_cycle192.md
- Revised demo SPEC (context-window pitch): notes/research_to_testbed_v1_demo_SPEC_REVISED_2026-06-08.md
- Sparse value drill (predicted modest gains; closed empirically): notes/research_drill_sparse_value_coding_within_shards_5x_2026-06-08.md
- Fact-rep rethink drill (EP1-EP4 anchored): notes/research_drill_fact_representation_rethink_5x_2026-06-08.md

---

**Exp-Dev:** authorize all 6 groups (~13 anchors). Recommended sequence prioritizes
Wikidata ingest (D1; blocking for revised demo) + cheap compositions (Group A) +
MID/HF rescues. ~40-50 hr CPU/GPU over 6 days. After this batch substrate has full
demo data layer + production validation extensions + Tier 5a prep.
