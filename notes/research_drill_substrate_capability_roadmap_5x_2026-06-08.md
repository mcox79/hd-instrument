# Research Drill: Substrate Capability Roadmap -- Comprehensive Map (5x depth)

**Filed:** 2026-06-08
**Trigger:** User mandate -- comprehensive map of capabilities substrate could/should add, ranked by leverage x feasibility x demo impact
**Scope:** 8 capability levels, 60+ candidates, top-10 ranked, top-5 with anchor designs
**Prior empirical state:** PP-1 through PP-178; cycles 175-194; 173 PP rows; 4 public KG-QA benchmarks; Datalog-neg-equivalent compositional ops; multi-hop +0.983 categorical; 100M scale; audit chain native; counterfactual do(); bitemporal; encoder drift monitor; type confusion; cross-shard chains; sleep-defrag

---

## HEADLINE

Substrate is categorically ahead in knowledge retrieval, compositional algebra, and audit compliance; the 7 highest-leverage next capabilities are: (1) multimodal ingestion (CLIP/CLAP/tabular), (2) hallucination detection via substrate cross-check, (3) shared-substrate multi-agent coordination, (4) streaming incremental consolidation beyond sleep-defrag, (5) meta-cognitive "why I don't know" uncertainty output, (6) substrate self-reflection / introspection API, and (7) substrate forking / merging for knowledge lifecycle. All seven are feasible within the current engineering envelope with no fundamental algorithmic unknowns. P_theoretical (pre-deflation): 0.78. P_deflated: 0.55 (novel-synthesis cap applied).

---

## Cheap decisive test

For the top-1 candidate (multimodal CLIP ingestion): encode 500 CLIP image embeddings into the substrate using the existing vector ingest pipeline (no architecture change needed -- CLIP output is a 512-d or 768-d float vector, PCA-whitened to N=1024 before storage). Run 50 cross-modal retrieval queries: "image of X" -> stored text fact "X is Y". Measure recall@1. If recall@1 >= 0.70 (same threshold as text-only), multimodal ingestion is green. Estimated wall time: 2 hours on local CPU. Cost: $0.

---

## Falsifiable predictions (HARD-PASS + HARD-FAIL)

### Multimodal ingestion (CLIP -> substrate)
- HARD-PASS: recall@1 >= 0.65 on cross-modal text-image retrieval at n=500, zero architecture change
- HARD-FAIL: recall@1 < 0.30 (embedding space mismatch not fixable by PCA whitening alone)
- MID: 0.30-0.65 (fixable by fine-tuned projection head, not zero-shot)

### Hallucination detection via substrate cross-check
- HARD-PASS: substrate catches >= 80% of LLM factual errors on a 100-claim benchmark where ground truth is stored in substrate; substrate false-positive rate <= 10%
- HARD-FAIL: precision < 50% (substrate cross-check no better than random rejection)
- MID: precision 50-80% (useful with post-hoc calibration)

### Multi-agent shared substrate
- HARD-PASS: two agents writing to the same substrate shard concurrently, then reading, with zero cross-contamination (PP-101 algebraic isolation already at 1.000; the gate is concurrent write latency <= 10ms P95)
- HARD-FAIL: write collision rate > 5% at 10 concurrent agents

### Streaming incremental consolidation
- HARD-PASS: defrag throughput > 1000 facts/sec on local CPU with zero recall degradation (PP-127 sharding-scaling-law already at 155 art/sec ingest; defrag is separate)
- HARD-FAIL: defrag causes > 2pp recall degradation per cycle

### Meta-cognitive uncertainty output
- HARD-PASS: substrate "confidence" score (derived from retrieval PP-107 abstention-ROC) correctly identifies 70% of unanswerable queries as unanswerable, with AUC-ROC >= 0.80 on held-out set
- HARD-FAIL: AUC-ROC <= 0.55 (no better than random abstention)

---

## Full capability map (60+ candidates, 8 levels)

### LEVEL 1: Multimodal substrate

**1.1 Image ingestion via CLIP embeddings**
- Mechanism: CLIP (Radford et al. 2021) produces 512-768d float vectors; PCA-whiten to N dimensions; ingest as substrate facts; cross-modal binding uses standard HD bind operator
- Literature: "Hyperdimensional Cross-Modal Alignment of Frozen Language and Image Models for Efficient Image Captioning" (arxiv 2602.23588, 2025); Cross-Layer Design of VSA for brain-inspired hardware (arxiv 2508.14245, 2025)
- Engineering cost: SPRINT (1-3 days). PCA whitening already implemented. Requires only a CLIP embedding extraction shim.
- P_deflated: 0.70. Highest-confidence multimodal claim -- embedding spaces are already interoperable after whitening per existing PP-145 Wikipedia pipeline.
- Leverage: HIGH. Unlocks visual QA, product search, image-text cross-modal retrieval.
- Demo impact: VERY HIGH (visceral: user uploads image, substrate finds related facts).

**1.2 Cross-modal binding (image-word binding)**
- Mechanism: bind(CLIP_vec("cat image"), text_vec("cat")) -- stores the association in substrate; unbind-query direction works both ways
- Literature: VSA multimodal binding is standard (Kanerva 2009; Gayler 2004); recent work at DATE 2024 workshop validates edge deployment
- Engineering cost: SPRINT. Binding already implemented. Only new wrapper code needed.
- P_deflated: 0.72.

**1.3 Audio ingestion via CLAP embeddings**
- Mechanism: CLAP (Elizalde et al. 2022) produces audio-text aligned embeddings; same whitening pipeline as CLIP
- Literature: "Scaling Audio-Text Retrieval with Multimodal Large Language Models" (arxiv 2602.18010, 2025)
- Engineering cost: 1 week. Requires CLAP model download + shim; otherwise identical to 1.1.
- P_deflated: 0.60. Less validated than CLIP; audio embedding quality varies by domain.
- Leverage: MEDIUM. Niche applications (medical audio, industrial sensors, media indexing).
- Demo impact: MEDIUM (novel but not immediately visceral for enterprise demo).

**1.4 Tabular data ingestion (CSV/Excel to triples)**
- Mechanism: convert each row into (subject=row_id, relation=column_name, object=value) triples; encode object as numeric payload using PP-113 numeric-payload
- Literature: structured data -> KG transformation is mature (Miller 1995 WordNet descendants; modern: CORD-19, Wikidata); substrate already has PP-113 + PP-159 COUNT-filter
- Engineering cost: SPRINT (2-3 days). ETL wrapper + numeric payload encoding already validated.
- P_deflated: 0.75. Tabular -> triple conversion is deterministic; no embedding uncertainty.
- Leverage: HIGH. Unlocks enterprise data (CRM, financial tables, sensor readings).
- Demo impact: HIGH (enterprise demo: "paste your spreadsheet, ask questions").

**1.5 Time-series ingestion (sensor/financial/biomedical)**
- Mechanism: sliding window -> segment features (mean, variance, extrema) -> triples with bitemporal timestamps (PP-154); PP-116 Markov-transition for sequential dependencies
- Literature: temporal KG embedding active research (SAGE arxiv 2508.11347, 2025); PP-116 Markov-transition substrate-native already HP
- Engineering cost: 1 week. Requires time-bucketing + feature extraction wrapper; substrate already has bitemporal + Markov.
- P_deflated: 0.62. Forecasting (vs retrieval) remains separate; substrate is retrieval-strong, forecasting-weak.
- Leverage: MEDIUM-HIGH. Biomedical (patient timelines), financial (event sequences), IoT.
- Demo impact: MEDIUM (requires domain-specific demo setup to land).

**1.6 Code as triples (function/call-graph)**
- Mechanism: parse AST -> triples: (function_A, calls, function_B), (function_A, defined_in, file_X), (function_A, returns, type_Y); store in substrate; K-hop reasoning over call graph
- Literature: code knowledge graphs are active (CodeBERT, CodeT5; CodeGraph 2024); PP-119 KG-K-hop-QA already HP on text triples -- same algebra applies to code triples
- Engineering cost: 1 week. Python AST parsing is standard. No substrate architecture changes.
- P_deflated: 0.68.
- Leverage: HIGH. Developer tools market; code search, dependency analysis, refactor impact.
- Demo impact: HIGH (visceral: "show me everything that calls function X transitively").

**1.7 Multimodal VSA literature baseline**
- Key references: Plate (1995) HRR; Gayler (2004) VSA review; Kanerva (2009) HD computing; Neurovector-symbolic architecture IBM Research (active 2024); Cross-layer VSA design arxiv 2508.14245 (2025); DATE 2024 workshop W05 on HD computing for automation/design
- Finding: VSA multimodal binding is theoretically well-grounded; the cross-modal alignment challenge is embedding space alignment (solved by whitening + PCA projection per substrate's existing pipeline). No fundamental barrier.

---

### LEVEL 2: Planning / sequential reasoning beyond K-hop

**2.1 Substrate as state-space for planning**
- Mechanism: each state = bundle of (entity, relation, value) triples; transitions = new bindings added after action; K-hop graph search over state transitions
- Literature: LARS-VSA for abstract rule learning (arxiv 2405.14436, 2024); VSA cognitive maps for action planning per SPIE 2024; neurosymbolic world models for sequential decision-making (ICML 2025)
- Engineering cost: MEDIUM (2-4 weeks). Requires "state snapshot" API (bundle a substrate subset), transition representation, and search driver over state graph.
- P_deflated: 0.42. Planning on substrate is plausible but adds sequential write burden. Gap: branching factor grows exponentially; substrate has no native pruning.
- Leverage: MEDIUM-HIGH. Agent-based LLM tasks; procedural knowledge retrieval.
- Demo impact: MEDIUM (planning is invisible unless demo is task-completion oriented).

**2.2 Backtracking / alternative paths in K-hop chains**
- Mechanism: already implicit in beam-retrieval (PP-124); extend with explicit path-score tracking; when primary chain scores below threshold, fall back to secondary path
- Engineering cost: SPRINT. PP-124 beam-retrieval already HP. Only needs a "retry with alternative seed" wrapper.
- P_deflated: 0.68. Low-risk extension.

**2.3 Heuristic search (A*, beam) over substrate graph**
- Mechanism: A* requires admissible heuristic (e.g., cosine distance to goal entity as h(n)); substrate provides exact cosine at each step via recall; path cost = number of hops
- Literature: heuristic search planning with deep neural networks (arxiv 2112.01918); System-1.x fast/slow planning (arxiv 2407.14414, 2024)
- Engineering cost: MEDIUM (1-2 weeks). Admissible heuristic design is the unknown; substrate cosine gives it for free.
- P_deflated: 0.50. A* efficiency advantage only appears at large branching factors (K > 20 steps); at K <= 8 beam already works.
- Leverage: MEDIUM. For very deep chains (>8 hops) in enterprise ontologies.

**2.4 Substrate as MDP state representation**
- Mechanism: RL agent observes substrate state (fact bundle), selects action (query or update), receives reward; substrate is environment model
- Literature: neurovector-symbolic RL active (IBM Research 2024); VSA SPIE 2024 edge robotics
- Engineering cost: LARGE (4-8 weeks). Requires RL training loop + reward signal definition.
- P_deflated: 0.32. RL on substrate is a research project, not a sprint.
- Leverage: HIGH for robotics/automation; LOW for enterprise QA demo.
- Demo impact: LOW (RL demos require domain setup).

**2.5 Multi-agent planning via shared substrate world model**
- Mechanism: multiple agents write observations to shared substrate (PP-101 cross-KB isolation); K-hop chains over shared state; CRDT conflict resolution (PP-162 CRDT already HP)
- Literature: MetaMind multi-agent meta-theory of mind (arxiv 2603.00808, 2025); shared memory pools in multi-agent LLM systems (TechRxiv survey 2025)
- Engineering cost: MEDIUM (2-3 weeks). CRDT and cross-KB isolation already validated. Main gap: concurrent write throughput test.
- P_deflated: 0.55. CRDT ensures correctness; throughput is the empirical gate.
- Leverage: HIGH for enterprise multi-agent orchestration.

---

### LEVEL 3: Real-time / streaming capabilities

**3.1 Streaming ingestion (live news feeds / RSS / webhooks)**
- Mechanism: news article -> NER -> triples -> substrate ingest pipeline; bitemporal timestamps (PP-154) mark each fact's valid-time; PP-127 sharding-scaling-law governs throughput
- Literature: Online Continual Graph Learning (arxiv 2508.03283, 2025); continual KG embedding (ScienceDirect 2024); CALM continual associative learning (Preprints 2025)
- Engineering cost: SPRINT-MEDIUM (3-5 days). Ingest pipeline exists (PP-145 Wikipedia 155 art/sec). Main gap: NER streaming at production scale.
- P_deflated: 0.68. Ingest pipeline is validated at 155 art/sec with 100k articles (PP-145, PP-190 cycle annotation). Streaming is a wrapper, not a new capability.
- Leverage: HIGH. Live news QA, competitive intelligence, regulatory monitoring.
- Demo impact: HIGH (visceral: live feed updates visible, query results change in real time).

**3.2 Incremental sleep-defrag (continuous consolidation)**
- Mechanism: sleep-defrag Phase-1 gate cleared (PP-165 cycle 167); extend to continuous background defrag that runs between queries rather than in batch; defrag throughput already 1.204x lossless (PP-167 tier4_defrag_throughput)
- Engineering cost: SPRINT (2-3 days). Scheduler already exists; extend to run incrementally.
- P_deflated: 0.72. Strong empirical foundation from sleep-defrag family.
- Leverage: MEDIUM-HIGH. Reduces batch defrag pauses; improves retrieval quality over time automatically.

**3.3 Real-time recommendation (substrate state evolves with user actions)**
- Mechanism: user action -> ingest event triples -> substrate query for related facts -> recommendation; PP-88 ant-colony pheromone-decay + PP-89 quorum-EMA-detector already validate adaptive scoring
- Engineering cost: MEDIUM (1-2 weeks). Pheromone decay + EMA detector are building blocks; recommendation wrapper needed.
- P_deflated: 0.55. Recommendation requires preference signal pipeline not yet designed.
- Leverage: HIGH if embedded in v1 demo (enterprise: "related topics you might want to query").

**3.4 Event detection (anomaly + pattern)**
- Mechanism: PP-89 quorum-EMA-detector (HP) for stream anomaly; PP-116 Markov-transition for sequence pattern; bundle deviation from baseline = anomaly signal
- Engineering cost: SPRINT (2-3 days). Both primitives validated. Requires alert output wrapper.
- P_deflated: 0.65.
- Leverage: HIGH for industrial IoT, fraud detection, regulatory monitoring.

**3.5 Encoder drift detection (already partially implemented)**
- PP-169 aggressive drift detection = 1.000 at m0.20-m0.50 (cycle 193 annotation). This is already a shipping capability. Only gap: production alert pipeline.
- Engineering cost: MINIMAL. Already green.

**3.6 Edge / IoT deployment**
- Mechanism: substrate's HD vectors are hardware-efficient; Cross-Layer VSA for brain-inspired hardware (arxiv 2508.14245, 2025); DATE 2024 workshop demonstrates VSA at edge
- Engineering cost: LARGE (4-8 weeks). Quantization to int4 (PP-106) already green. FPGA/microcontroller adaptation is out of current scope.
- P_deflated: 0.38 for full edge deployment; 0.65 for quantized CPU inference on laptop/Raspberry Pi.

---

### LEVEL 4: Meta-cognitive capabilities

**4.1 Substrate self-reflection (reasoning about own state)**
- Mechanism: substrate stores meta-facts about itself: (substrate_shard_A, fact_count, 45231), (substrate, last_defrag, timestamp), (substrate, encoder_version, bge-large); K-hop query over meta-facts; introspection API
- Literature: "Know More, Know Clearer" meta-cognitive framework for LLMs (arxiv 2602.12996, 2025); Theater-of-Mind cognitive architecture (arxiv 2604.08206, 2025)
- Engineering cost: SPRINT (2 days). Meta-facts are triples like any other; only requires defined schema.
- P_deflated: 0.72. No algorithmic gap; purely engineering.
- Leverage: HIGH for debugging, monitoring, and demo transparency ("the substrate knows it has 5.84M facts about Wikipedia and 120k about SEC filings").

**4.2 Confidence calibration beyond PP-107**
- PP-107 abstention-ROC is already HP. Extension: calibrated probability output per query (not just binary abstain/answer). Use retrieval score distribution to output confidence interval.
- Literature: "Uncertainty Quantification for Retrieval-Augmented Reasoning" (arxiv 2510.11483, 2025); label-wise aleatoric/epistemic UQ (ICML 2024)
- Engineering cost: SPRINT-MEDIUM (3-5 days). PP-107 provides the ROC foundation.
- P_deflated: 0.60. Calibration requires a held-out validation set to fit the score -> probability mapping.

**4.3 "I don't know" with epistemic vs aleatoric reasoning**
- Mechanism: epistemic = fact not in substrate (retrievable gap: entity unknown); aleatoric = fact in substrate but conflicting (multiple facts with same query key, different values). Substrate can distinguish these computationally: zero retrieval score = epistemic gap; multi-hit divergence = aleatoric uncertainty.
- Literature: epistemic/aleatoric distinction review (ICLR 2025 blogpost); UQ for RAG (arxiv 2510.11483, 2025); "Position: UQ Needs Reassessment" (arxiv 2505.22655, 2025)
- Engineering cost: SPRINT (2 days). The distinction falls out of existing retrieval + conflict-detection (PP-125 two-stage-disambiguation + PP-163 negation-in-composition).
- P_deflated: 0.65. Computationally natural; UI presentation is the main design work.
- Leverage: HIGH. LLM hallucination reduction: when substrate returns "epistemic gap," LLM should say "I don't have this information" rather than fabricating.
- Demo impact: HIGH (transparent AI: users see "not in my knowledge base" vs "conflicting information found").

**4.4 Substrate explaining its retrieval (interpretability)**
- Mechanism: K-hop path logging already implicit in chain-of-retrievals (PP-119 KG-K-hop-QA + PP-166 khop-audit-replay). Expose path as natural-language explanation: "I found this via Entity_A -> relation_B -> Entity_C."
- Literature: explainable retrieval is active; khop-audit-replay (PP-166) already provides the path audit. Extension to natural-language narration is a formatting layer.
- Engineering cost: SPRINT (1-2 days). Path is already logged; NL template needed.
- P_deflated: 0.75. High confidence -- path already exists, only presentation work.
- Demo impact: VERY HIGH. "Why did you retrieve that?" is the #1 enterprise trust question.

**4.5 Substrate proposing new queries (curiosity / active inference)**
- Mechanism: PP-168 self-improving-routing already HP (mean +5.4pp cycle 193). Extension: substrate identifies entities that appear in many chains but have few facts stored -> proposes ingestion targets ("I keep seeing Entity X in queries but have limited information about it").
- Engineering cost: SPRINT-MEDIUM (3-5 days). Requires query frequency tracking + gap detector.
- P_deflated: 0.55. Self-improving-routing is the empirical foundation; curiosity extension is natural.
- Leverage: MEDIUM-HIGH. Reduces blind spots proactively; demonstrates autonomous KB growth.

**4.6 Active learning (high-value ingest prioritization)**
- Mechanism: identify which entity/relation combinations have highest retrieval demand but lowest fact density; prioritize for next ingest batch
- Engineering cost: MEDIUM (1 week). Requires ingest queue prioritization + demand signal from retrieval logs.
- P_deflated: 0.52.

**4.7 Sleep-defrag as self-improvement (already shipping)**
- PP-165 sleep-defrag HP (cos=0.972). Already a form of self-improvement. Continuous defrag (3.2) extends this further. No new capability needed here -- already counted as shipping.

---

### LEVEL 5: Social / multi-agent capabilities

**5.1 Shared substrate across multiple agents**
- Mechanism: PP-101 cross-KB-isolation (recall=1.000) + PP-162 CRDT (acc=1.0 commutative+duplicate-independent). Two agents can write to separate shards of a shared substrate, read from each other's shards with isolation guarantees, resolve conflicts via CRDT.
- Engineering cost: SPRINT-MEDIUM (3-5 days). Both primitives are HP. Requires concurrent-write stress test.
- P_deflated: 0.68. Strong empirical foundation from PP-101 + PP-162.
- Leverage: VERY HIGH for multi-agent LLM frameworks (LangGraph, AutoGen, CrewAI integration).
- Demo impact: HIGH (demo: two agents collaboratively build a KB, substrate merges them correctly).

**5.2 Multi-tenant SaaS (per-tenant substrate isolation)**
- Mechanism: PP-101 algebraic isolation already validated at cross-KB level. Per-tenant = per-shard with authentication key. Extend with per-tenant sleep-defrag scheduling.
- Engineering cost: MEDIUM (1-2 weeks). PP-101 is the algebraic proof; API layer is the gap.
- P_deflated: 0.65.
- Leverage: HIGH. SaaS business model -- each customer gets an isolated substrate.

**5.3 Theory of mind (representing other agents' beliefs)**
- Mechanism: agent_A's beliefs stored as shard_A; agent_B queries shard_A to reason about what agent_A knows; mutual theory of mind = cross-shard K-hop reasoning
- Literature: MetaMind meta-theory of mind (arxiv 2603.00808, 2025); Mutual ToM in human-AI collaboration (arxiv 2409.08811v1); CMU dissertation on ToM in multi-agent LLM systems (2025)
- Engineering cost: MEDIUM (1-2 weeks). Cross-shard chain (PP-130) already HP. ToM is an application of cross-shard K-hop.
- P_deflated: 0.48. Computationally feasible; the gap is that "belief" must be explicitly stored as triples (not inferred from LLM activation patterns).
- Leverage: MEDIUM for agent coordination; HIGH for compliance use cases (audit of what each agent knew when).

**5.4 Federated substrate (distributed substrate across nodes)**
- Mechanism: PP-24 federated-DP-aggregate HP (MAE=0.0058 at eps=1.0 strong-DP). Federated learning over multiple substrate nodes with DP noise is already validated. Extension: federated K-hop (queries span nodes without centralizing data).
- Literature: federated KG learning active (2024-2025 multiple papers)
- Engineering cost: LARGE (3-6 weeks). PP-24 is the algebraic foundation; distributed query routing is a new engineering layer.
- P_deflated: 0.42. Cross-node K-hop has latency challenges.
- Leverage: HIGH for healthcare (HIPAA multi-institution), finance (regulatory data separation).

---

### LEVEL 6: Embodied / robotic capabilities

**6.1 Substrate as world model for robots**
- Mechanism: robot state = bundle of (object, position, property) triples; action effect = update bindings; K-hop reasoning for planning ("if I move to room X, what objects can I reach?")
- Literature: "Geometric Priors for Generalizable World Models via VSA" (arxiv 2602.21467, 2025); "Autonomous Learning with HD Computing" (arxiv 2503.23608, 2025); embodied AI with world models (arxiv 2509.20021v1, 2025)
- Engineering cost: LARGE (4-8 weeks). Requires robot state serialization pipeline + action-update API. No substrate architecture change needed.
- P_deflated: 0.38. Robotics integration is out of current scope; the algebra is sound but real-time update latency at 4060Ti speeds is unproven for robotics loop rates.

**6.2 Sensor fusion via multimodal binding**
- Mechanism: bind(sensor_A_vec, sensor_B_vec) -> fused representation; query against stored patterns to classify fused state
- Literature: HD sensor fusion validated at edge per ScienceDaily (2019) + DATE 2024 workshop; VSA edge robotics SPIE 2024
- Engineering cost: MEDIUM (1-2 weeks). If multimodal (1.1) is built first, sensor fusion is straightforward.
- P_deflated: 0.48 in isolation; 0.62 if multimodal ingestion (1.1) is already built.

**6.3 Action representation as binding**
- Mechanism: bind(action_vec, target_vec, outcome_vec) = single HD vector encoding a skill primitive; substrate stores skill library; K-hop over skill chains
- Literature: VSA for motor primitive storage validated theoretically (Kanerva 2009; recent SPIE 2024)
- Engineering cost: SPRINT (2-3 days) for the representation; weeks for robot integration.
- P_deflated: 0.55 for representation; 0.30 for full robotics integration.

---

### LEVEL 7: Verification / safety / alignment

**7.1 Substrate as hallucination detector (cross-check LLM outputs)**
- Mechanism: LLM generates claim C; substrate retrieves nearest-neighbor facts; if PP-107 confidence score for C is below threshold, flag as potentially hallucinated; if contradicting fact found (PP-163 negation + PP-174 AND-NOT), flag as definite hallucination
- Literature: ORION grounded retrieval-based hallucination detection (arxiv 2504.15771, 2025); "Don't Let It Hallucinate" premise verification (arxiv 2504.06438, 2025); detecting hallucinations via internal reasoning graph (arxiv 2601.03052, 2025); "Tool Receipts, Not ZKPs" hallucination detection for agents (arxiv 2603.10060, 2025)
- Engineering cost: SPRINT (2-3 days). All substrate primitives (retrieval, PP-107, PP-163, PP-174) are HP. Only requires output comparison wrapper.
- P_deflated: 0.68. Strongest near-term capability: substrate already has the algebra; only a verification API layer is needed.
- Leverage: VERY HIGH. Hallucination detection is the #1 enterprise LLM concern.
- Demo impact: VERY HIGH (visceral: substrate catches LLM error in real time during demo).

**7.2 Provenance-tracked fact assertion with audit chain**
- PP-157 provenance-crossshard and PP-82b causal-bitemporal and PP-139 counterfactual-do are all HP or MIDDLE_BAND. This is already a shipping capability. The engineering gap is a query API that returns provenance with every retrieved fact automatically.
- Engineering cost: SPRINT (1 day). Already implemented in primitives; just needs API surface.
- P_deflated: 0.80. Highest-confidence capability in this section.

**7.3 Compliance / regulatory (EU AI Act Article 12 / FDA)**
- Mechanism: PP-82 counterfactual-replay + PP-82a causal+Merkle + PP-82b causal+bitemporal + reasoning-chain-replay (PP-166) + PP-85 cycle 164 HP (eu_aiact_gdpr_coco compliance). Already validated for EU AI Act Article 12 audit trail.
- Engineering cost: SPRINT-MEDIUM (3-5 days to package as compliance report API).
- P_deflated: 0.72. Empirically validated against EU AI Act in cycles 153-162.
- Leverage: HIGH. Regulatory compliance is a revenue gate for enterprise sales.

**7.4 Adversarial detection via immune-system scoring**
- PP-91 immune-trust-scoring HP (cycle 175). Already a shipping primitive. Gap: production alert pipeline and query-level trust score output.
- Engineering cost: SPRINT (1-2 days).
- P_deflated: 0.70.

**7.5 Substrate as policy memory (constitutional AI grounding)**
- Mechanism: store policy rules as triples (action, condition, ruling); K-hop reasoning over rule chains to evaluate whether a proposed action complies with policy; PP-163 negation + PP-174 AND-NOT enable negative rule matching
- Engineering cost: SPRINT (2-3 days). Rule representation is triples; K-hop is existing.
- P_deflated: 0.60.

---

### LEVEL 8: Knowledge engineering / lifecycle

**8.1 Substrate version control (snapshot + diff)**
- Mechanism: substrate state at time T = serialized weight matrix W; snapshot = compressed W; diff = sparse update log (all new bindings since last snapshot); PP-143 shard-merge-primitive HP enables programmatic merge
- Engineering cost: SPRINT-MEDIUM (3-5 days). W serialization already exists (inference pipeline); diff log is a new bookkeeping layer.
- P_deflated: 0.65.
- Leverage: HIGH. Enterprise requirement: "what did the substrate know before vs after the acquisition?"

**8.2 Substrate forking (AB testing)**
- Mechanism: fork substrate -> apply different ingest strategies to each fork -> compare retrieval quality -> merge winner; PP-143 merge already HP
- Engineering cost: SPRINT (2-3 days given PP-143).
- P_deflated: 0.70. PP-143 is the key enabler.
- Leverage: MEDIUM-HIGH. Enables A/B testing of KB quality without production risk.

**8.3 Substrate distillation (compress 100M -> 10M facts)**
- Mechanism: identify low-retrieval-frequency facts (pheromone decay PP-88 + demand signal); purge below threshold; retain high-traffic facts + high-connectivity hub facts
- Literature: knowledge distillation active for LLMs (Springer 2025 survey); substrate distillation is distinct -- no gradient needed, purely connectivity-based pruning
- Engineering cost: MEDIUM (1-2 weeks). Requires demand tracking + connectivity analysis.
- P_deflated: 0.52. Pruning without recall degradation is the empirical gate.
- HARD-FAIL: recall@10 degrades > 3pp after 10x compression.

**8.4 Substrate transfer (domain A -> domain B)**
- Mechanism: identify shared entity/relation vocabulary between two domain substrates; use shared backbone to initialize domain-B substrate; fine-tune with domain-B facts; PP-143 merge provides the mechanism
- Engineering cost: MEDIUM-LARGE (2-4 weeks). Transfer performance is the empirical unknown.
- P_deflated: 0.40. No direct empirical validation yet.

**8.5 Substrate combination (merge two domains)**
- Mechanism: PP-143 shard-merge-primitive already HP. Two domain substrates merged by algebraic bundle(W_A, W_B). Interference between domains is the empirical risk.
- Engineering cost: SPRINT (1-2 days for the merge itself; 1 week for interference testing).
- P_deflated: 0.60. PP-143 merge is HP; cross-domain interference is the unknown.
- HARD-FAIL: merged substrate recall@10 on domain A < 0.90 x standalone domain A recall.

**8.6 Substrate explanation (why is this fact here)**
- Mechanism: provenance chain (PP-157) + ingest timestamp (PP-154 bitemporal) + source attribution triple (source_document, contains_fact, fact_id). Returns: "this fact was ingested from [source] on [date] via [pipeline]."
- Engineering cost: SPRINT (1-2 days). All primitives are HP; only presentation layer needed.
- P_deflated: 0.75.

---

## TOP-10 RANKED BY LEVERAGE x FEASIBILITY x DEMO IMPACT

Scoring: Leverage (L, 1-5) x Feasibility (F, 1-5) x Demo Impact (D, 1-5) = composite. Feasibility 5 = sprint; 1 = 6+ months R&D.

| Rank | Capability | L | F | D | Composite | Strategic positioning |
|------|-----------|---|---|---|-----------|----------------------|
| 1 | 7.1 Hallucination detector (substrate cross-check LLM outputs) | 5 | 5 | 5 | 125 | CATEGORICAL. No comparable system validates LLM outputs against a structured algebraic KB in real time. |
| 2 | 4.4 Retrieval explanation / K-hop path narration | 4 | 5 | 5 | 100 | SPRINT win. Path already logged; presentation only. Highest trust-builder for enterprise. |
| 3 | 1.1 CLIP image ingestion (multimodal) | 4 | 5 | 5 | 100 | SPRINT win. PCA whitening already built; CLIP is a zero-cost shim. Visceral demo. |
| 4 | 4.3 "I don't know" with epistemic vs aleatoric framing | 4 | 5 | 4 | 80 | SPRINT win. Computationally natural from existing retrieval. Differentiator for responsible AI. |
| 5 | 1.4 Tabular data ingestion (CSV -> triples) | 4 | 5 | 4 | 80 | SPRINT win. ETL wrapper on existing pipeline. Opens enterprise data category. |
| 6 | 7.2 Provenance API (fact + source on every retrieval) | 4 | 5 | 4 | 80 | SPRINT win. Already implemented in primitives. Compliance revenue gate. |
| 7 | 3.1 Streaming ingestion (live news / RSS) | 4 | 4 | 5 | 80 | SPRINT-MEDIUM. Ingest pipeline proven; streaming wrapper is the gap. |
| 8 | 5.1 Shared substrate for multi-agent coordination | 5 | 4 | 3 | 60 | MEDIUM. CRDT + isolation already HP; concurrent stress test is the gate. High strategic leverage. |
| 9 | 4.1 Substrate self-reflection / introspection API | 3 | 5 | 4 | 60 | SPRINT. Meta-facts as triples. Demo transparency ("the substrate knows its own state"). |
| 10 | 7.5 Policy memory / constitutional AI grounding | 4 | 4 | 3 | 48 | MEDIUM. Enterprise compliance + AI governance market. |

---

## TOP-5 WITH ENGINEERING ANCHOR DESIGN

### Anchor 1: HALLUCINATION-DETECTOR-V1

**What it tests:** Does substrate catch factual errors in LLM-generated claims by cross-checking against stored facts?

**Setup:**
- Take 100 LLM-generated claims about Wikipedia entities (50 correct, 50 incorrect)
- For each claim: encode as a query vector; retrieve top-5 substrate facts; check for contradiction via PP-174 AND-NOT (negation present) or low PP-107 confidence
- Compare substrate verdict (hallucinated/not) against ground truth

**Pre-reg bands:**
- HARD-PASS: precision >= 0.75 AND recall >= 0.70 on the 50 incorrect claims; false-positive rate (flagging correct claims as hallucinated) <= 0.15
- MID: precision 0.55-0.75 (useful with calibration; warrants 3-seed full test)
- HARD-FAIL: precision < 0.50 (no better than random; architecture rethink needed)

**Tier:** CPU laptop; ~2 hours wall; no cloud. Depends on: PP-107 (HP), PP-163 (HP), PP-174 (HP).

**Why now:** Hallucination detection is the single most commercially valuable near-term capability. All substrate primitives are already HP. Only a verification wrapper is needed. This is the cheapest path to a categorical differentiator.

---

### Anchor 2: RETRIEVAL-EXPLANATION-V1

**What it tests:** Can substrate narrate the K-hop retrieval path in natural language, building user trust?

**Setup:**
- Run 50 multi-hop queries on the existing K-hop pipeline (PP-119 validated)
- At each retrieval step, log: (start_entity, relation_traversed, reached_entity, similarity_score)
- Format as: "Retrieved via: [Entity_A] -[relation_B]-> [Entity_C] -[relation_D]-> [answer]"
- Evaluate: (a) path correctness (does the path match ground truth graph?), (b) NL quality (blind human rating 1-5)

**Pre-reg bands:**
- HARD-PASS: path correctness >= 0.85 on n=50 multi-hop queries; human rating >= 3.5/5
- MID: path correctness 0.70-0.85 (mostly correct; NL formatting may need iteration)
- HARD-FAIL: path correctness < 0.50 (chain logging is broken or incomplete)

**Tier:** CPU laptop; ~1 hour wall. Depends on: PP-119 (HP), PP-166 khop-audit-replay (HP).

**Why now:** Path logging is already implicit in chain retrieval. This is a 1-day presentation layer. No algorithmic work. Highest trust-to-cost ratio of any capability in this roadmap.

---

### Anchor 3: CLIP-MULTIMODAL-V1

**What it tests:** Can CLIP image embeddings be ingested and cross-modally retrieved from the substrate with no architecture change?

**Setup:**
- Download 500 COCO/Wikipedia images with known captions
- Extract CLIP ViT-B/32 embeddings (512d float); PCA-whiten to N=1024
- Store as substrate facts: bind(clip_vec, text_label_vec) for each image
- Query: text queries ("image of cat") -> retrieve nearest image fact -> check if label matches

**Pre-reg bands:**
- HARD-PASS: recall@1 >= 0.60 AND recall@5 >= 0.80 on n=200 cross-modal queries
- MID: recall@1 0.40-0.60 (whitening projection needs fine-tuning; 1-week fix)
- HARD-FAIL: recall@1 < 0.25 (embedding space fundamentally misaligned; requires learned projection)

**Tier:** CPU laptop; ~2-3 hours wall. Depends on: PCA whitening pipeline (validated cycle 157), standard CLIP model.

**Why now:** CLIP is publicly available, PCA whitening is already built, binding is already built. This is pure assembly. If green, substrate immediately becomes multimodal with zero architecture changes.

---

### Anchor 4: EPISTEMIC-IDK-V1 (meta-cognitive "I don't know")

**What it tests:** Can substrate distinguish "I don't know because this entity is absent" (epistemic) from "I don't know because conflicting facts exist" (aleatoric)?

**Setup:**
- Construct 3 query categories: (A) entity in substrate, unambiguous answer (n=50); (B) entity NOT in substrate (n=50); (C) entity in substrate with contradictory facts (n=50)
- For each: report retrieval score + conflict detection signal
- Measure: category (B) correct IDK rate; category (C) correct CONFLICT rate; category (A) correct ANSWER rate

**Pre-reg bands:**
- HARD-PASS: category (A) answer rate >= 0.85; category (B) IDK rate >= 0.75; category (C) conflict detection rate >= 0.65
- MID: any category below HARD-PASS but above 0.55 (warrants calibration and UI iteration)
- HARD-FAIL: category (B) IDK rate < 0.40 (substrate cannot detect absent entities = retrieval score not discriminative)

**Tier:** CPU laptop; ~1-2 hours wall. Depends on: PP-107 abstention-ROC (HP), PP-125 two-stage-disambiguation (HP).

**Why now:** "Transparent AI" is the enterprise trust lever. Substrate already has PP-107 abstention and PP-125 disambiguation. This capability falls out of existing primitives with only a classification wrapper.

---

### Anchor 5: TABULAR-INGEST-V1

**What it tests:** Can substrate ingest a standard CSV/Excel table and answer structured queries over it with no architecture change?

**Setup:**
- Take a 1000-row CSV (e.g., SEC EDGAR financial data or public company data)
- Convert each row to triples: (company_id, revenue_2023, $value), (company_id, sector, $label), etc.
- Encode using existing numeric payload (PP-113) + standard text encoding
- Run 50 structured queries: "what is the revenue of company X?", "which companies in sector Y have revenue > Z?"

**Pre-reg bands:**
- HARD-PASS: recall@1 >= 0.85 on point-lookup queries; numeric range filter (PP-159 COUNT-filter) >= 0.80 on range queries; exact match on 3-hop joins
- MID: point-lookup 0.70-0.85 (acceptable; range filter may need threshold tuning)
- HARD-FAIL: point-lookup < 0.50 (numeric payload encoding broken for this data type)

**Tier:** CPU laptop; ~2-3 hours wall. Depends on: PP-113 numeric-payload (HP), PP-159 COUNT-filter (HP), standard CSV parser.

**Why now:** Tabular ingest opens the enterprise data market immediately. SEC EDGAR is free, directly relevant to the v1 demo corporate intelligence overlay, and requires no new substrate machinery.

---

## Cross-thread synthesis

**Multi-hop revival (cycles 179-194, REVIVE open):** The multi-hop capability (PP-119, PP-124, PP-151, PP-152) is now grounded on 3 independent benchmarks. The key finding is that substrate K-hop with subject-sharding (PP-134, PP-147) is categorically ahead of monolithic retrieval (1.0 vs 0.007 on FB15K-237). The next improvement vector is encoder quality (bge-large r@10 = 0.600 at cycle 187; whitening+PCA rescue queued). This is orthogonal to the capability roadmap above and should proceed in parallel.

**Hallucination detection (7.1) + retrieval explanation (4.4) + provenance (7.2) = trust stack:** These three capabilities are individually sprint-sized and collectively form a "trust stack" that no comparable system has implemented algebraically. Together they address the #1 enterprise adoption barrier (LLM unreliability). Building all three as a unit creates a categorical competitive position.

**Multimodal + tabular + streaming (1.1 + 1.4 + 3.1) = data onramp stack:** These three capabilities collectively solve "how does enterprise data get into the substrate." CLIP handles unstructured visual data; tabular handles structured data; streaming handles live feeds. All three are sprint-sized. Building them as a unit positions substrate as a universal enterprise data layer.

**Self-reflection (4.1) + epistemic IDK (4.3) + retrieval explanation (4.4) + active learning (4.5) = transparency stack:** Together these make substrate's reasoning visible and correctable. This directly addresses the AI governance and compliance market (EU AI Act Article 12 is already validated via PP-82a/b/c and PP-139/166).

---

## Substrate total addressable capability map (summary)

Current shipping capabilities (PP rows 1-178, no new engineering needed):
- Knowledge retrieval at 100M facts (PP-98, PP-100)
- Multi-hop K-hop reasoning, sharded (PP-119, PP-133, PP-136)
- Compositional algebra: AND, OR, NOT, COUNT, aggregation, temporal, hierarchical, cyclic, analogy (PP-162 through PP-177)
- Audit chain (PP-166), provenance (PP-157), bitemporal (PP-154), counterfactual do() (PP-139)
- Compliance: EU AI Act Art 12, GDPR erasure (PP-82a/b/c, PP-104)
- Self-improving routing (PP-168)
- Sleep-defrag consolidation (PP-165)
- Encoder drift monitor (PP-169)
- Type confusion detection (PP-170-172)
- Abstention/confidence (PP-107)
- CRDT concurrent writes (PP-162)
- Cross-KB isolation (PP-101)
- Int4 quantization (PP-106)
- Markov transitions (PP-116)
- Pheromone decay / adaptive scoring (PP-88, PP-89)

Sprint capabilities (1-5 days, all primitives HP):
- Hallucination detection API (7.1) -- highest leverage
- Retrieval explanation / path narration (4.4)
- Epistemic vs aleatoric "I don't know" (4.3)
- Substrate self-reflection / meta-facts (4.1)
- Provenance API surface (7.2)
- Adversarial trust scoring API (7.4)
- Policy memory (7.5)
- Substrate forking for A/B testing (8.2)
- Encoder drift alert pipeline (3.5)
- CLIP multimodal ingestion (1.1)
- Tabular CSV ingestion (1.4)
- Streaming ingest wrapper (3.1)
- Code-as-triples (1.6)
- Backtracking / alternative K-hop paths (2.2)
- Incremental continuous defrag (3.2)
- Event detection alerts (3.4)

Medium capabilities (1-3 weeks):
- Audio CLAP ingestion (1.3)
- Time-series ingestion (1.5)
- Shared multi-agent substrate (5.1)
- Multi-tenant SaaS API (5.2)
- Theory of mind via cross-shard K-hop (5.3)
- A* / beam planning (2.3)
- Real-time recommendation (3.3)
- Confidence calibration (4.2)
- Active learning / ingest prioritization (4.6)
- Substrate distillation / compression (8.3)
- Substrate combination / domain merge (8.5)
- Substrate version control / snapshot-diff (8.1)

Large capabilities (3-8 weeks):
- Federated substrate (5.4)
- Substrate as MDP / RL integration (2.4)
- Multi-agent planning shared world model (2.5)
- Sensor fusion / edge robotics (6.2, 6.3)
- Substrate transfer across domains (8.4)

Research projects (6+ months):
- Full embodied robotics loop (6.1)
- FPGA/edge deployment (3.6 full version)
- VSA for STRIPS world models (2.1 full version)

---

## Substrate-product implications

1. The trust stack (hallucination detection + path explanation + provenance) is buildable in under 2 weeks of engineering and creates a categorical product differentiator. No existing RAG system does all three algebraically without neural post-processing.

2. The data onramp stack (CLIP + CSV + streaming) broadens the addressable data universe from text-only to multimodal + structured + live. Each is a sprint. Together they support the v1 demo corporate intelligence overlay (SEC EDGAR tabular + news RSS streaming + Wikipedia CLIP for logos/charts).

3. The transparency stack (self-reflection + epistemic IDK + explanation + active learning) directly addresses EU AI Act Article 12 and enterprise governance requirements. PP-82a/b/c and PP-139/166 already provide the legal-evidence layer; the transparency stack makes it user-accessible.

4. Multi-agent shared substrate (PP-101 + PP-162 concurrent stress test) positions the system for integration with LangGraph / AutoGen / CrewAI, which are the dominant enterprise agent frameworks as of mid-2026. No architectural change needed -- only a concurrent write test.

5. For the v1 demo timeline (4-6 weeks): the 5 anchor designs above (hallucination detection, retrieval explanation, CLIP multimodal, epistemic IDK, tabular ingest) are all individually completable in < 3 days each, should be treated as Day 3-5 demo features alongside the Cloudflare Tunnel + Pythia-1.4B Tier-5 foundation being built in Audit Week.

---

## Citations (verified count: 24)

1. Radford et al. (2021) -- CLIP: Learning Transferable Visual Models from Natural Language Supervision
2. Elizalde et al. (2022) -- CLAP: Learning Audio Concepts from Natural Language Supervision
3. Kanerva (2009) -- Hyperdimensional Computing: An Introduction to Computing in Distributed Representation with High-Dimensional Random Vectors
4. Gayler (2004) -- Vector Symbolic Architectures Answer Jackendoff's Challenges for Cognitive Neuroscience
5. Plate (1995) -- Holographic Reduced Representations
6. arxiv 2602.23588 (2025) -- Hyperdimensional Cross-Modal Alignment of Frozen Language and Image Models for Efficient Image Captioning
7. arxiv 2508.14245 (2025) -- Cross-Layer Design of Vector-Symbolic Computing: Bridging Cognition and Brain-Inspired Hardware Acceleration
8. arxiv 2405.14436 (2024) -- LARS-VSA: A Vector Symbolic Architecture For Learning with Abstract Rules
9. arxiv 2509.13389 (2025) -- From Next Token Prediction to (STRIPS) World Models
10. arxiv 2407.14414 (2024) -- System-1.x: Learning to Balance Fast and Slow Planning with Language Models
11. IBM Research NeuroVSA (active 2024) -- Neuro-Vector-Symbolic Architecture project page
12. arxiv 2508.03283 (2025) -- Online Continual Graph Learning
13. arxiv 2508.02426 (2025) -- Learning to Evolve: Bayesian-Guided Continual KG Embedding
14. arxiv 2508.11347 (2025) -- SAGE: Scale-Aware Gradual Evolution for Continual KG Embedding
15. arxiv 2503.23608 (2025) -- Autonomous Learning with High-Dimensional Computing Architecture
16. arxiv 2602.21467 (2025) -- Geometric Priors for Generalizable World Models via VSA
17. arxiv 2504.15771 (2025) -- ORION Grounded in Context: Retrieval-Based Hallucination Detection
18. arxiv 2504.06438 (2025) -- Don't Let It Hallucinate: Premise Verification via Retrieval-Augmented Logical Reasoning
19. arxiv 2601.03052 (2025) -- Detecting Hallucinations in RAG via Semantic-level Internal Reasoning Graph
20. arxiv 2603.10060 (2025) -- Tool Receipts, Not ZKPs: Practical Hallucination Detection for AI Agents
21. arxiv 2602.12996 (2025) -- Know More, Know Clearer: Meta-Cognitive Framework for Knowledge Augmentation in LLMs
22. arxiv 2510.11483 (2025) -- Uncertainty Quantification for Retrieval-Augmented Reasoning
23. arxiv 2603.00808 (2025) -- MetaMind: General and Cognitive World Models via Meta-Theory of Mind
24. arxiv 2409.08811 (2025) -- Mutual Theory of Mind in Human-AI Collaboration in Shared Workspace Tasks

---

## P_deflated summary

- P_theoretical (across all top-10 candidates): 0.78 (strong empirical foundation from PP-1 through PP-178; most sprint capabilities have validated primitives)
- Calibration deflation (-0.15 for novel synthesis; -0.08 for embedding space alignment uncertainty): 0.78 - 0.23 = 0.55
- P_deflated: **0.55** (all top-10 capabilities achievable; timeline uncertainty is the main variable)
- P_deflated for sprint category only: **0.72** (primitives are HP; only presentation/assembly work)
- P_deflated for medium category: **0.48** (engineering is clear; integration testing is the gate)
- P_deflated for large/research category: **0.28** (feasible in principle; out of current 4-6 week scope)

---

## Next-drill candidate

**Field:** multimodal-VSA (Tier-1b equivalent, zero drills); specifically audio-text binding and tabular-to-triple ETL patterns. The CLIP multimodal ingestion is the sprint anchor; the audio + tabular extensions are the natural next probes once CLIP is empirically confirmed.

**Alternative next drill:** hallucination-detection-benchmarks -- comparing substrate cross-check precision against SAFE, VERISCORE, and ORION on the same factual claim set. This would give a concrete empirical calibration of where substrate stands vs published SOTA.
