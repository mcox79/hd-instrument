# Strategic Priority Analysis -- Blocking Characteristics and Performance Barriers
# hd-instrument substrate research

**Date:** 2026-06-07
**Scope:** Step-back survey across current empirical state, negative findings, untested domains
**Method:** Synthesis from cap_map v462 + today's production architecture snapshot + field advisor output
**Word cap:** 2500

---

## HEADLINE

Three barriers dominate: (1) encoder geometric alignment (d_eff theory refuted; no replacement measure deployed), (2) adaptive adversarial robustness (Probe 2 was non-adaptive paraphrase -- the hardest attack class untested), and (3) production deployment scale gap (sharding HP at 5x load, 500x untested; pseudoinverse at production N unquantified). Everything else is secondary.

---

## Cheap decisive test

**For encoder geometric alignment (Barrier 1):**
Measure cosine-similarity distribution between encoder output centroids across N=100 stored key-value pairs using last-token pooled Llama-1B embeddings. Compute alignment ratio: (fraction of pairs with cos-sim > 0.3) / (fraction with cos-sim < 0.1). If alignment ratio > 3.0, geometric clustering is the dominant capacity tax. CPU, ~5 min.

**For adaptive adversarial (Barrier 2):**
Run KF-1 adversary with iterative text mutation: start from seed query, apply greedy word substitution guided by KF-1 confidence score (maximizing detection evasion). Compare evasion rate at 20 iterations vs the non-adaptive baseline. If adaptive evasion rate > 2x non-adaptive, the current 0.977/0.983 numbers are non-conservative. CPU, ~30 min.

---

## Top-15 Blocking Characteristics + Opportunities (ranked by impact)

### Rank 1 -- Encoder Geometric Alignment (Unmeasured)
**Strategic value: 10 | Effort: M | Risk if ignored: 10 | Time-to-impact: immediate**

The BGE-large empirical cap at d_eff=40 (Drill 5 theory refuted) has NO replacement theory. The current explanation "geometric alignment matters more than rank" is a verbal hypothesis, not a falsifiable model. The production encoder (Llama-1B + PCA whitening) has 17.43x capacity lift over MiniLM -- but the mechanism behind this lift is not characterized. If geometric alignment is the operative variable, then:
- The 17.43x lift is not stable across domains (distribution shift may alter geometry)
- The sparse-KEY alpha=0.005 selection implicitly depends on geometric properties that could degrade on out-of-distribution inputs
- CRT 6-module 800x gain may rest on the same geometric foundation

No geometric alignment metric is currently computed at write-time or monitored in production. This is a silent single point of failure.

**Cheap decisive test:** Per above. Complementary: compute nearest-neighbor graph entropy for stored keys; entropy < 0.5 bits per key indicates dangerous clustering.

### Rank 2 -- Adaptive Adversarial Robustness
**Strategic value: 9 | Effort: M | Risk if ignored: 9 | Time-to-impact: immediate**

KF-1 3-layer adversarial coverage reports 0.977 (hard-negative + word-bigram) and 0.983 (paraphrase). Both were validated on NON-ADAPTIVE attackers: fixed paraphrase banks, static hard-negative sets. Adaptive attackers that observe the detector's confidence output and iteratively optimize the evasion attack are structurally harder and have not been tested. For a "physics-grade guarantees" product narrative, a KF-1 component that fails against adaptive evasion is a critical story gap. Compliance use cases (the primary GTM) will face adversarial content injection from well-resourced actors.

**Hard-fail threshold:** Adaptive evasion rate > 30% at 10 iterations means KF-1 requires architectural upgrade.

### Rank 3 -- Pseudoinverse Computational Cost at Production Scale
**Strategic value: 9 | Effort: L | Risk if ignored: 9 | Time-to-impact: month**

The pseudoinverse write rule gives "infinite" lift on real keys vs Hebb (cycle 141). The cost is a matrix inversion at write time. For a dense W matrix of size N x N (N=16384), the pseudoinverse is O(N^2.376) at best (Coppersmith-Winograd) -- roughly O(10^9) floating-point operations per write. At 1000 writes per second (a modest production throughput target), this is ~10^12 FLOPS/second, which is not feasible on CPU and marginal on GPU. The current benchmarks are single-write-call timings at moderate N. No throughput-at-scale test exists. This is the most direct production deployment blocker.

**Mitigation paths to test:**
- Rank-k pseudoinverse approximation (k << N): does accuracy degrade gracefully?
- Incremental Sherman-Morrison-Woodbury updates vs full recompute
- Preconditioning to amortize cost over batch writes

**Hard-fail threshold:** If pseudoinverse throughput < 100 writes/second at N=16384 with no approximation viable, the write rule requires architectural replacement.

### Rank 4 -- Production Scale Gap (Sharding at 500x)
**Strategic value: 8 | Effort: L | Risk if ignored: 8 | Time-to-impact: month**

Sharding was validated at HP with 5x overload (cycle 142). The gap between 5x and 500x is not characterized. Distributed substrate shards face:
- Cross-shard key routing: how are keys assigned to shards? Random hashing? Geometric clustering?
- Shard rebalancing under addition/deletion
- Query fan-out cost (query must hit all shards at N=500 if key routing is unknown)
- Consistency during concurrent writes across shards

The continual-KV "100% at 120 sessions" number is per-shard. Cross-shard temporal ordering is unvalidated.

### Rank 5 -- M_max=50 Systematic Censoring
**Strategic value: 8 | Effort: S | Risk if ignored: 7 | Time-to-impact: immediate**

Four negative findings (norm-gate, kf1_contradiction, kf1_truthfulqa, multi_head_x_corruption) may be artifacts of M_max=50 censoring (Batch F re-audit pending). If the effective capacity cliff for these capabilities falls below M=50, the HF classification is correct. If the capabilities require M>50 to operate, the HF conclusions are false negatives that have incorrectly closed research lines. Given that three of these involve KF-1 hallucination detection -- a Tier-1 product story -- this is high-priority to resolve.

**Cheap decisive test:** Re-run multi_head_x_corruption at M_max=5 (below corruption onset). If corruption-induced HF disappears at M=5, the failure mode is capacity-induced not mechanism-broken.

### Rank 6 -- HNSW Recall at Production Scale (Cell 10 Pending)
**Strategic value: 7 | Effort: S | Risk if ignored: 7 | Time-to-impact: immediate**

HNSW approximate nearest neighbor search is the retrieval backbone at production scale (800K Wikipedia substrate). Cell 10 is still pending. HNSW recall degrades as shard size grows, especially when stored vectors have geometric clustering (Rank 1 issue). If HNSW recall at 800K items falls below 0.95, the 17.43x encoder lift is partially eaten by retrieval misses. No systematic recall-vs-scale curve exists for the production encoder geometry.

### Rank 7 -- Long-Context Handling (Untested >1000 Tokens)
**Strategic value: 7 | Effort: M | Risk if ignored: 6 | Time-to-impact: month**

Production queries are English text. No test has been run with queries or stored passages exceeding ~1000 tokens. For the compliance-sidecar GTM (processing regulatory documents, contracts, medical records), passages commonly run 5K-50K tokens. Three failure modes are uncharacterized:
- Last-token pooling on 10K-token documents: does the last token encode the full document?
- PCA whitening fitted on short-text distribution: does it transfer to long-text?
- HNSW recall on long-context embeddings: geometric distribution shifts

**Hard-fail threshold:** Recall@1 drops below 0.70 at 5K tokens means the production encoder requires long-context fine-tuning or chunking strategy.

### Rank 8 -- Multi-Modal Substrate (Text-Only Limit)
**Strategic value: 7 | Effort: XL | Risk if ignored: 5 | Time-to-impact: quarter**

The cap_map notes cross-modal binding was HARD_PASS for text-KG binding (substrate_multimodal_binding_text_kg_v1), but image-embedding extension is untested. For agentic workflows (the "substrate as agentic memory layer" opportunity) the substrate needs to bind visual observations, tool outputs, and text into a single retrievable memory. Multi-modal Hopfield networks exist in the literature (Ramsauer 2020 generalization); the binding algebra may extend cleanly. The strategic value is high because text-only memory limits the agentic use case significantly.

### Rank 9 -- Catastrophic Forgetting Beyond 120 Sessions
**Strategic value: 7 | Effort: M | Risk if ignored: 6 | Time-to-impact: month**

Continual-KV shows 100% at 120 sessions. No test beyond 120 sessions exists. Production agentic workflows accumulate thousands of sessions. The 4-stage continual learning result shows ret_A=0.740 (misses 0.80 bar) -- this is the deep-retention problem at stage-4 not 120-session scale. But the two failure modes interact: at session 1000, both session-count stress and stage-count stress combine. The stress test shape (linear vs power-law degradation vs cliff) is unknown.

### Rank 10 -- Compound Axis Stacking (Engineering vs Rigorous Test)
**Strategic value: 6 | Effort: M | Risk if ignored: 6 | Time-to-impact: month**

Cycle 142 confirms pinv x sparse x multi-head "mostly works for engineering purposes." The cap_map has a strong CANNOT section on compound mechanisms (R3 x R10 x replay = closed; C3 factored = closed). The production architecture stacks: Llama-1B + PCA whitening + pseudoinverse + alpha=0.005 sparse-KEY + M=2 multi-head + CRT 6-module + sharding + continual-KV + KF-1. That is 9 stacked components, each individually validated. The compound stack at full production depth (all 9 together) has NOT been empirically validated as a unit. Interactions between pseudoinverse write and sparse-KEY alpha at M=2 heads, for example, are empirically unverified. One interaction that breaks a property could cascade silently.

### Rank 11 -- Numerical and Symbolic Reasoning
**Strategic value: 6 | Effort: L | Risk if ignored: 5 | Time-to-impact: quarter**

All validated capabilities are on natural-language text. No numerical (arithmetic, algebra) or symbolic (logical inference, constraint satisfaction) reasoning has been tested. The compliance-sidecar GTM involves documents that contain numbers, dates, constraints. If the substrate cannot store and retrieve "the contract rate is 4.75%" correctly (vs paraphrasticly similar "the rate is approximately 5%"), a critical product accuracy gap exists. VSA/HRR frameworks in principle support symbolic variable binding -- but this is unvalidated for the production encoder.

### Rank 12 -- Multi-Tenant Security / Isolation
**Strategic value: 6 | Effort: M | Risk if ignored: 7 | Time-to-impact: quarter**

The cap_map primary product narrative includes "per-tenant W" isolation. This is stated as a design property, not an empirical result. No adversarial cross-tenant leakage test has been run. If Tenant A's stored keys can be recovered by a well-crafted Tenant B query (via HNSW approximate neighbor leakage or W matrix side-channel), the compliance-sidecar story is critically weakened. For regulated industries (healthcare, finance), this must be empirically demonstrated, not theoretically asserted.

### Rank 13 -- Substrate as Agentic Memory Layer
**Strategic value: 8 | Effort: L | Risk if ignored: 3 | Time-to-impact: quarter**

This is a BLUE OCEAN opportunity. The production substrate has: exact retrieval with audit trail, real-time learning during inference (cycle 142 HARD-PASS), continual-KV, per-hop localization. This is a natural architecture for agentic workflows where the agent must remember across episodes, correct factual errors, and provide citations. No integration experiment with an agent framework exists. The gap is not a technical barrier -- it is a prioritization gap. The substrate already has the primitives; nobody has assembled them for an agent loop.

### Rank 14 -- Energy Efficiency at Production Scale
**Strategic value: 5 | Effort: M | Risk if ignored: 4 | Time-to-impact: quarter**

All current benchmarks are wall-clock time, not energy. For edge deployment or on-device personalization (a Tier-2 killer capability), energy per inference/write matters more than absolute latency. The Hebbian-only training is theoretically compatible with neuromorphic hardware -- but no energy model exists. For the compliance-sidecar GTM (always-on audit process) energy efficiency is a TCO argument, not just a performance argument.

### Rank 15 -- Temporal Reasoning and Fact Versioning
**Strategic value: 5 | Effort: M | Risk if ignored: 4 | Time-to-impact: quarter**

The substrate stores facts but has no model of fact validity over time ("the CEO as of 2025-01-01 was X; as of 2026-01-01 was Y"). For compliance use cases, temporal provenance is load-bearing. Continual-KV tracks session ordering but not wall-clock time or logical versioning of facts. A temporal query ("what did we know about X before the June 2025 update?") is currently unserviceable.

---

## Things Substrate Research Has NOT Prioritized (5+ items)

### 1. Compound stack integration test
The most glaring gap. Nine production components are individually validated. The full 9-component stack has never been tested as a unit. Research has focused on individual capabilities; compound failure modes at the stack level are unexplored. One undiscovered interaction between pseudoinverse and sparse-KEY under multi-head could silently degrade the 800x CRT gain.

### 2. Encoder distribution shift robustness
Llama-1B + PCA whitening was validated on English Wikipedia (800K substrate) and English-language benchmarks. No out-of-distribution test exists for: domain shift (legal documents vs Wikipedia), language shift (non-English inputs hitting the English-trained PCA), or temporal shift (text from a different year hitting a PCA fitted on 2024 data). For production deployment, distribution shift is the dominant source of silent degradation.

### 3. Production write throughput benchmark
The pseudoinverse write rule (cycle 141) is measured as accuracy lift, not throughput. How many writes per second can the system sustain at N=16384 before becoming a bottleneck? This is the number a customer will ask first. It does not appear in any experiment result. This is an over-investment in accuracy validation and under-investment in throughput characterization.

### 4. Customer integration latency (end-to-end, not component)
The Merkle-cert is <0.051ms in isolation. The full pipeline (encode -> sparse-KEY -> multi-head M=2 -> sharded HNSW -> CRT decode -> KF-1 audit) end-to-end latency at P99 under concurrent load is unmeasured. The compliance-sidecar GTM requires P99 latency < some threshold to be viable. This number does not exist yet.

### 5. Substrate compression / quantization
All experiments run at float32. For the on-device personalization use case (Tier-2 killer), the substrate must fit in edge hardware (4-16 GB RAM). INT8 or INT4 quantization of W matrices is unexplored. The binding algebra (XOR/MAJ/bipolar multiplication) may be quantization-tolerant or not -- this is unknown.

### 6. Federated substrate learning
The cap_map includes federated unlearning as a theoretical property. No experiment tests a federated scenario: two substrates trained on different private datasets, merged without sharing raw data, with a query that must route to the correct private partition. The algebraic deletion-cert moat depends on this working correctly in federated mode.

---

## Top-5 Priorities with Concrete Cell Proposals

### Priority 1: Geometric Alignment Characterization
**Proposed cell:** `encoder_geometric_alignment_audit_v1`
- Compute pairwise cosine similarity matrix for N=500 random stored keys (Llama-1B last-token pooled)
- Compute alignment entropy (Shannon entropy of cosine-sim histogram)
- Run across 3 domains: Wikipedia, legal text, code
- Compare PCA-whitened vs raw embeddings on alignment entropy
**Cost:** CPU, ~20 min, $0
**Expected outcome:** Entropy map that shows whether PCA whitening is homogenizing the geometric distribution (good) or preserving dangerous clusters (bad)
**HP threshold:** Alignment entropy > 4.0 bits for all 3 domains = whitening works
**HF threshold:** Any domain alignment entropy < 2.0 bits = geometric clustering is an active capacity tax; requires new whitening strategy or retrieval redesign

### Priority 2: Adaptive Adversarial KF-1 Stress Test
**Proposed cell:** `kf1_adaptive_adversary_v1`
- Implement greedy confidence-guided word substitution: at each step, swap the word that most reduces KF-1 detection confidence
- Run 20 iterations on 100 fabricated claims
- Measure evasion rate at iterations 1, 5, 10, 20
- Compare to non-adaptive baseline (static paraphrase set)
**Cost:** CPU, ~1 hour, $0
**Expected outcome:** Evasion rate curve; if adaptive rate > 2x non-adaptive at iteration 10, KF-1 architecture needs adversarial training extension
**HP threshold:** Adaptive evasion rate < 1.5x non-adaptive at 20 iterations = current KF-1 is robust to adaptive attacks
**HF threshold:** Adaptive evasion rate > 3x non-adaptive at 10 iterations = hard architectural gap

### Priority 3: Pseudoinverse Write Throughput Benchmark
**Proposed cell:** `pseudoinverse_throughput_vs_N_v1`
- Measure writes/second for pinv write rule at N = {512, 1024, 2048, 4096, 8192, 16384}
- Test: batch write (10 keys per call), incremental SMW update, full recompute
- Profile: time-per-write vs N, memory-per-write vs N
- Compare: Hebb write throughput at same N as baseline
**Cost:** CPU, ~30 min, $0 (GPU beneficial for large N)
**Expected outcome:** Throughput curve; identify the N threshold where pinv throughput falls below 100 writes/second
**HP threshold:** Pinv throughput > 500 writes/second at N=16384 = production-viable without approximation
**HF threshold:** Pinv throughput < 50 writes/second at N=8192 = approximation required; file to exp_dev for SMW rescue path

### Priority 4: Full Compound Stack Integration Test
**Proposed cell:** `compound_stack_integration_v1`
- Instantiate the full production stack: Llama-1B encoder + PCA whitening + pseudoinverse write + alpha=0.005 sparse-KEY + M=2 multi-head + CRT 6-module + sharding (2 shards) + continual-KV + KF-1
- Store 500 real Wikipedia passages, run 200 retrieval queries
- Measure: recall@1, recall@5, KF-1 precision/recall on 50 fabricated claims, write throughput
- Compare recall to single-component baselines (pinv alone, sparse-KEY alone)
**Cost:** GPU recommended (N=8192, 500 passages), ~1 hour
**Expected outcome:** Stack-level recall number; identify any interaction degradation vs isolated components
**HP threshold:** Stack recall@1 > 0.85 = compound stack is coherent
**HF threshold:** Stack recall@1 < 0.70 (worse than single best component by > 15pp) = destructive interaction exists; bisect to identify

### Priority 5: Agentic Memory Loop Prototype
**Proposed cell:** Research drill first, then experiment
- Research: survey VSA-based agent memory architectures; generic terms (associative memory + agent workflow + episodic retrieval + attribution)
- Then experiment: implement minimal agent loop (10-step sequence, each step stores observation, later retrieval with citation)
- Measure: retrieval accuracy for step-N observation at step-N+K (K=1,5,10)
- Target: demonstrate that per-hop localization (cycle 134+137) works in a closed agent loop
**Cost:** Research = CPU 1 hour; Experiment = CPU 30 min
**Expected outcome:** Agent memory loop that shows provenance for each recalled fact
**HP threshold:** Retrieval accuracy > 0.90 at K=5 = agent memory layer is viable
**HF threshold:** Accuracy < 0.70 at K=1 = fundamental compatibility issue between continual-KV and agent-loop temporal structure

---

## Resource Allocation Recommendation (Next 1-2 Days)

**Day 1 focus: Characterization (zero GPU cost)**
- Priority 1 (geometric alignment audit) -- 20 min CPU
- Priority 3 (pseudoinverse throughput benchmark) -- 30 min CPU
- M_max=50 censoring re-audit (Batch F) -- interpret pending results

These three characterization tasks address the top two blockers and the most likely false-negative closure. Combined cost: ~1 hour CPU. Output: two hard numbers that either (a) confirm production readiness on the encoding and write-rule fronts, or (b) surface architectural remediation requirements.

**Day 2 focus: Stress test highest-risk claim**
- Priority 2 (adaptive adversarial) -- 1 hour CPU
- Begin Priority 4 compound stack integration -- 1 hour GPU

The adaptive adversarial test directly stress-tests the KF-1 claim that anchors the product narrative. If it holds, confidence in the compliance-sidecar GTM goes up substantially. If it fails, that is better to know now before product positioning commits to it.

**What to deprioritize:**
Research has over-invested in individual component validation (11 production-ready capabilities) and under-invested in compound behavior, throughput, and adversarial robustness. The next 10 drills should follow a different profile: 4 characterization (geometry, throughput, compound, latency), 3 stress tests (adaptive adversarial, long-context, distribution shift), 3 new-domain probes (agentic loop, numerical reasoning, multi-modal). The current pattern of individual-component confirmation drills is showing diminishing returns.

---

## Blue Ocean Opportunities (3 Untested Domains, High Strategic Value)

### Blue Ocean 1: Substrate as Agentic Memory Layer
Why now: Real-time inference learning (cycle 142 HARD-PASS), per-hop localization, continual-KV, and Merkle-cert form a natural agentic memory primitive. No other memory system combines: writes from observation, retrieval with citation, exact edit, and algebraic audit in one layer. The agentic AI market is currently served by naive context-window stuffing or external vector stores with no audit. Substrate's compliance-sidecar architecture positions it as the ONLY audit-grade agentic memory. First-mover if pursued in the next 30 days before the agentic tooling market standardizes around RAG-only patterns.

### Blue Ocean 2: Temporal Fact Versioning for Compliance Documents
Why now: No RAG system correctly handles "what did policy X say BEFORE the March 2026 amendment?" This is a real compliance requirement (regulatory change management, contract version history, medical record updates). Substrate already has deletion-cert + edit-individual-bindings. Adding a temporal key (timestamp as a bound dimension in the binding algebra) would make this query answerable with algebraic certainty -- not approximate. This is a direct product story not available from any vector database competitor, and it leverages existing validated primitives.

### Blue Ocean 3: Federated Privacy-Preserving Knowledge Accumulation
Why now: Enterprise customers cannot share training data across entities (competitor data, HIPAA). Substrate's per-tenant W architecture with algebraic isolation could enable: each entity trains its own W on private data, substrates are merged at the binding algebra level (superposition), cross-entity queries are possible WITHOUT any entity's raw data leaving its boundary. The mathematical structure for this exists in VSA/HRR frameworks (superposition is additive). The engineering for it does not. If the algebraic isolation claim holds empirically, this opens the federated learning market without any of the privacy-engineering complexity that currently blocks that market.

---

## Falsifiable Predictions (HARD-PASS + HARD-FAIL)

**HARD-PASS (would substantially increase production confidence):**
- HP-1: Encoder geometric alignment entropy > 3.5 bits across 3 domains (whitening is effective)
- HP-2: Pseudoinverse throughput > 200 writes/second at N=16384 on GPU (production-viable)
- HP-3: KF-1 adaptive evasion rate < 2x non-adaptive at 20 iterations (robustness holds)
- HP-4: Compound stack recall@1 > 0.82 (stack is coherent)
- HP-5: Agentic loop retrieval accuracy > 0.88 at K=5 (agent memory viable)

**HARD-FAIL (would require architectural remediation):**
- HF-1: Alignment entropy < 2.0 bits in any domain -> encoder geometry is the binding capacity tax; PCA whitening requires redesign
- HF-2: Pseudoinverse throughput < 30 writes/second at N=8192 -> write rule is not production-viable at current formulation; require SMW or rank-k approximation
- HF-3: KF-1 adaptive evasion rate > 4x non-adaptive at 10 iterations -> KF-1 requires adversarial training; current 0.977/0.983 numbers are non-conservative
- HF-4: Compound stack recall@1 < 0.65 -> destructive interaction in production stack; bisect required before any deployment claim
- HF-5: M_max=50 censoring re-audit confirms all 4 HF closures are genuine -> those research lines correctly closed; move resources to Blue Ocean priorities

---

## Cross-Thread Synthesis

The field advisor identifies free-probability (Tracy-Widom edge statistics) and semiconductor drift-diffusion (Glauber dynamics) as Tier-1 next-drill candidates. These are adjacent to the geometric alignment question: Tracy-Widom edge fluctuations govern the spectral tail of the encoder Gram matrix, which directly determines the effective alignment geometry after PCA whitening. A targeted free-probability drill asking "what do Tracy-Widom statistics predict about encoder alignment geometry after PCA?" would give a theoretical prediction to test against the empirical alignment audit (Priority 1 above). This is a natural cross-thread synthesis that the field advisor adjacency map supports.

The semiconductor / Glauber dynamics candidates (D1, D2, D7) address the agentic memory loop question from a different angle: if substrate iterated retrieval is zero-temperature Glauber dynamics, then finite-temperature variants predict the probability of "wrong basin attraction" in a multi-session agent loop. This is directly relevant to Blue Ocean 1 (agentic memory) and the long-context stress test (Rank 7).

Materials-physics is saturated (31% yield, 16 drills, last 3 weak). Do not drill further there.

---

## Substrate-Product Implications

The current portfolio of 11 production-ready capabilities is technically impressive. The strategic gap is not capability breadth -- it is deployment readiness. The three most commercially load-bearing questions are:

1. **Can the write rule sustain production throughput?** (Pseudoinverse cost at scale -- Rank 3)
2. **Are the adversarial robustness claims non-conservative?** (Adaptive attackers -- Rank 2)
3. **Does the compound stack behave coherently?** (Rank 10)

None of these requires a new theoretical breakthrough. They are engineering characterization tasks. The next research investment should weight characterization over expansion: the capability map is rich enough; what is missing is the throughput/robustness/integration evidence that makes the existing capabilities credible to a customer.

The compliance-sidecar GTM narrative ("physics-grade guarantees, not policy-grade") is strategically correct. The gap is that "physics-grade" must be empirically demonstrated under adversarial and production-scale conditions, not just validated in isolated single-component experiments.

---

## Citations (verified count: 0 external)

This is a synthesis-only note from internal empirical state. No external literature cited. Field advisor adjacency cues cited inline (free-probability F2/F4, semiconductor D1/D2/D7 from research_field_advisor.py output 2026-06-06).

---

## P_deflated estimates

- Geometric alignment entropy > 3.5 bits: P_deflated = 0.55 (alignment is likely but unverified; standard lit-scan penalty applied; PCA whitening has known geometry-homogenizing properties)
- Pseudoinverse throughput > 200 writes/second at N=16384 GPU: P_deflated = 0.40 (matrix inversion is O(N^2.376); at N=16384 this is genuinely uncertain; cap at 0.50 for novel-regime estimate)
- KF-1 adaptive robustness holds (evasion < 2x): P_deflated = 0.45 (non-adaptive numbers are strong; adaptive attack uplift is structurally uncertain; no published precedent for this specific architecture)
- Compound stack recall@1 > 0.82: P_deflated = 0.50 (individual components validate; compound interactions are the dominant unknown; cap at 0.50)
- Agentic loop retrieval > 0.88: P_deflated = 0.45 (primitives exist; integration is untested; agentic loop adds temporal ordering complexity)
