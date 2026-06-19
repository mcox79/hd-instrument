# Research -> Exp-Dev: BATCH 3 — 30+ fresh cheap-decisive CPU anchors

**From:** Research  **Date:** 2026-06-09 ~04:00 UTC
**Re:** User direction "exp dev could use more experiments." Cycle 198 just landed +10 PP. CPU lane drains fast.

## CONFORMAL RESCUE (untapped fix; cycle 198 both alternatives MID; ONE-LINE FIX simulated 88-93%)

**CONF-FIX:** Score-based nonconformity (nc = 1 - cosine_score) per drill simulation
- The drill's recommended primary; not yet empirically tested
- Cycle 198 tested temperature scaling + gap-score; both MID
- HARD-PASS: coverage ≥ 0.88 (simulation 88-93%) + set_size > 1.5

**CONF-RANK:** Rank-based with PP-181 gap-score combined
- HARD-PASS: coverage ≥ 0.85

## CONTINUAL LEARNING (substrate evolves)

**CONT-1:** Substrate incremental ingest without quality loss
- 100 ingest batches of 1000 facts each; measure recall at every batch
- HARD-PASS: recall stable ± 0.02 across all batches

**CONT-2:** Substrate forgets selectively (per PP-104 GDPR primitive extension)
- Delete random 10% facts; measure remaining recall
- HARD-PASS: 100% retained recall on non-deleted; 0% on deleted

**CONT-3:** Substrate updates (cycle 175 SMW pinv at production scale)
- 1000 fact updates; measure update latency + recall preservation
- HARD-PASS: update latency < 10ms; recall preservation > 0.99

## ADVERSARIAL ROBUSTNESS

**ADV-1:** Substrate under adversarial-prompt injection
- 100 injection attempts; substrate detection rate
- HARD-PASS: detection ≥ 0.85 + FP ≤ 5%

**ADV-2:** Substrate data poisoning detection (cycle 175 immune system extension)
- Inject 1% poisoned facts; substrate flag rate via PP-180 contradiction
- HARD-PASS: detection ≥ 0.80 + clean retention ≥ 0.95

**ADV-3:** Substrate under adversarial query (queries designed to confuse)
- 200 adversarial queries; substrate abstention or correct answer
- HARD-PASS: appropriate behavior (correct OR abstain) ≥ 0.85

## SCALING (untapped 100M+ scale)

**SCALE-1:** Substrate latency at 200M facts (extends PP-150/166)
- 200M-fact KB; latency probe
- HARD-PASS: P95 < 1ms (still O(1) extrapolation)

**SCALE-2:** Substrate end-to-end at 500M facts (stretch)
- 500M-fact KB; recall@5 sample
- HARD-PASS: recall@5 ≥ 0.95 at 500M

**SCALE-3:** Substrate cross-shard at 10K shards
- 10K shard cluster; cross-shard chain extraction
- HARD-PASS: chain accuracy ≥ 0.90 at 10K shards

## CROSS-DOMAIN TRANSFER

**XDOM-1:** Substrate-A → Substrate-B knowledge transfer (analogy at scale)
- Train on Wikipedia; transfer to PubMed; measure cold-start performance
- HARD-PASS: cold-start recall ≥ 0.70 (vs scratch ≥ 0.50)

**XDOM-2:** Substrate few-shot relation extension (PP-115 at production scale)
- Learn novel relation from 5 examples; recall on 100 test cases
- HARD-PASS: recall ≥ 0.85 from K=5 examples

## SUBSTRATE-RL AGENT

**RL-1:** Substrate as RL agent memory (substrate stores past experiences)
- Small RL task (CartPole or similar); compare with vs without substrate memory
- HARD-PASS: substrate-RL reaches solution in ≤ 50% steps vs scratch

**RL-2:** Substrate as model-based RL world model
- Substrate stores transition model; planning via substrate K-hop
- HARD-PASS: world-model rollouts correct ≥ 0.90 at 5-step horizon

## SYMBOLIC REGRESSION

**SYM-1:** Substrate finds equations from data (binding patterns ARE equations)
- 50 known equation discoveries
- HARD-PASS: substrate recovers ≥ 0.70 equation forms

## CODE GENERATION AUGMENTATION

**CODE-1:** Substrate as function library (PP-185 software supply chain extension)
- 1000-function library; user query → substrate retrieves matching function
- HARD-PASS: top-1 function match ≥ 0.90

**CODE-2:** Substrate as test specification store
- Functions + tests stored as substrate triples
- HARD-PASS: tests retrieved for given function ≥ 0.95

## TIME-SERIES SUBSTRATE

**TS-1:** Sensor stream ingestion (substrate as IoT substrate)
- 1000-sensor stream simulation; substrate ingestion
- HARD-PASS: ingestion rate ≥ 100 events/sec + retrieval accuracy ≥ 0.95

**TS-2:** Anomaly detection via substrate confidence (PP-107 application)
- Inject 5% anomalies; substrate detection
- HARD-PASS: detection ≥ 0.85 + FP ≤ 3%

**TS-3:** Time-series forecasting via substrate compositional patterns
- Simple seasonality prediction
- HARD-PASS: forecast MAE ≤ baseline ARIMA

## ALIGNMENT / SAFETY

**ALIGN-1:** Substrate as constitutional AI substrate
- 100 rule-violation test cases; substrate-mediated refusal
- HARD-PASS: violation detection ≥ 0.95

**ALIGN-2:** Substrate-mediated truthfulness gating
- Substrate scores LLM output factuality; gate refuses if score below threshold
- HARD-PASS: false-claim block rate ≥ 0.90 + true-claim allow rate ≥ 0.95

## PROOF GENERATION

**PROOF-1:** Substrate generates proof chains via K-hop traversal (math drill anchor C extension)
- 100 simple theorems; substrate generates proof sketch
- HARD-PASS: proof chain valid ≥ 0.80

## ACTIVE LEARNING

**AL-1:** Substrate identifies high-value queries to ingest
- 1000 queries; substrate picks top-10 most informative
- HARD-PASS: picked queries reduce KB error by > 0.20 (vs random selection)

## VISUALIZATION / INTERPRETABILITY

**VIS-1:** Substrate state visualization (substrate bindings as graph)
- 100-fact KB; substrate exports graph
- Engineering anchor; no HP gate; visualization quality assessment

## MULTI-MODAL EXTENSION (per cycle 196 multimodal drill)

**MM-1:** CLIP embeddings → substrate (image triples)
- 1000-image KB; substrate retrieves by text query
- HARD-PASS: image retrieval recall@5 ≥ 0.70

**MM-2:** Audio embeddings (Whisper) → substrate
- 100-audio KB; cross-modal substrate query
- HARD-PASS: audio retrieval recall@5 ≥ 0.65

## DISTRIBUTED / SAAS

**DIST-1:** Substrate CRDT under network partition
- Simulate partition; substrate eventual consistency
- HARD-PASS: convergence after partition heal; no fact loss

**DIST-2:** Multi-tenant SaaS pattern (PP-101 0.0000 cross-tenant)
- 100 tenants; 10K facts each; cross-tenant query attempts
- HARD-PASS: 0 cross-tenant leakage + within-tenant performance maintained

## SUBSTRATE-AS-VERIFIER BENCHMARKS

**VER-MMLU:** Substrate-augmented LLM on MMLU subset
- 1000 questions; baseline LLM vs LLM+substrate
- HARD-PASS: substrate-augmented ≥ +5 pp over baseline

**VER-GSM8K:** Substrate-augmented LLM on GSM8K math
- 100 problems; substrate provides math facts; LLM reasons
- HARD-PASS: substrate-augmented ≥ +10 pp

**VER-TRIVIAQA:** Substrate-augmented LLM on TriviaQA
- 500 questions; substrate has facts; LLM formats
- HARD-PASS: substrate-augmented ≥ 0.90 (vs LLM-only ~0.70)

## SUBSTRATE COMPRESSION (per PP-200 1-bit HP)

**COMPRESS-1:** 1-bit substrate at production scale (100M facts)
- Extend cycle 198 PP-200; full-scale validation
- HARD-PASS: 1-bit quality matches float32 ± 0.03 at 100M

**COMPRESS-2:** Substrate edge deployment (mobile / embedded)
- 1M-fact substrate on ARM CPU (Raspberry Pi class)
- HARD-PASS: P95 retrieval < 10ms; storage < 100 MB

## Recommended sequencing

**Day 1 (cheapest minutes-each):**
- CONF-FIX (the one-line conformal rescue; categorical close-out)
- CONT-1 (incremental ingest)
- ADV-1 (prompt injection detection)
- SCALE-1 (latency at 200M)
- CODE-1 (function library)

**Day 2:**
- XDOM-1, XDOM-2 (cross-domain transfer)
- SYM-1 (symbolic regression)
- TS-1/2 (time-series substrate)

**Day 3:**
- VER-MMLU/GSM8K/TRIVIAQA (substrate-augmented benchmarks)
- COMPRESS-1/2 (1-bit at scale + edge deployment)

**As capacity allows:**
- All others by priority

## Cross-references
- Cycle 198 (just landed): notes/orchestrator_to_research_results_summary_2026-06-08_cycle198.md
- Conformal drill (one-line fix): notes/research_drill_negative_conformal_coverage_2x_2026-06-08.md
- STATE OF PLAY: notes/research_STATE_OF_PLAY_2026-06-08.md
- Verticals drill (in flight): notes/research_drill_substrate_verticals_5x_2026-06-08.md (when lands)
- Emergent extreme scale drill (in flight): notes/research_drill_substrate_emergent_extreme_scale_5x_2026-06-08.md (when lands)

---

**Exp-Dev:** 30+ cheap CPU anchors. CONF-FIX is highest-priority categorical close-out
(simulated 88-93% coverage; one-line fix). VER-MMLU/GSM8K/TRIVIAQA are highest-value
strategic anchors (substrate-augmented benchmark wins for demo). Sequencing recommendation
prioritizes cheapest categorical close-outs first, then strategic anchors.

When verticals + emergent extreme-scale drills land, more anchors will follow.
