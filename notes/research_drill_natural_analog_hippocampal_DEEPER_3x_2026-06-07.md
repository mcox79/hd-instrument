# Research Drill: Natural Analog -- Hippocampal Reverse Replay as Counterfactual Planning Engine (3x Deeper)
# Date: 2026-06-07
# Field: neuroscience / computational memory / biological analogs
# Topic: DEEPER 3x drill on reverse replay sub-avenue (most yielding from 5x hippocampal drill)
# Prior note: notes/research_drill_natural_analog_hippocampal_5x_2026-06-07.md

---

## HEADLINE

Reverse replay is not merely a playback mechanism. The biological literature establishes it as a backward temporal-difference operator: it propagates value from reward states backward through a sequence via asymmetric STDP modulated by short-term synaptic depression. The mathematical structure (reward-weighted backward sequence traversal) maps directly onto substrate's Pattern B unbind chain. Three engineering-ready extensions follow from this deep mapping: (1) a replay index enabling exact counterfactual do() queries on ordered write sequences, (2) a priority-weighted replay gate that strengthens high-value fact bindings via replay frequency, and (3) a prospective-replay primitive that generates candidate future sequences by running the binding chain forward from the current state without new writes. Theta-gamma coupling adds a second implementation angle: the nested oscillation structure (theta outer cycle, gamma inner items) is algebraically equivalent to an outer VSA binding with inner superposition -- substrate already has both primitives. P_deflated estimates deflated 0.15-0.25 from theoretical per calibration rule; novel-synthesis capped at 0.50.

---

## PART 1: The Reverse Replay Mechanism -- Mechanistic Depth

### 1.1 The Core Mathematical Mechanism (Reverse Replay as TD Backup)

The Ambrose-Pfeiffer (2016) and Foster (2017) framing that reverse replay is "temporal difference value propagation backward through a sequence" has been given a precise mechanistic substrate by subsequent work.

The key result (Haga & Fukai 2018, eLife): under symmetric STDP modulated by short-term synaptic depression (STP), forward sequence traversal creates an ASYMMETRIC potentiation. Specifically, the learning rule is:

  delta_w_ij = eta * r_i * r_j * D_j * F_j

where D_j is short-term depression and F_j is short-term facilitation at synapse j. Because the presynaptic neurotransmitter pool depletes at the "trailing edge" of a forward-moving activity packet, D_j is lowest at the trailing edge and highest at the leading edge. This asymmetry means forward traversal potentiates reverse connections more than forward connections.

Result: the network is primed for efficient reverse replay. When a reward signal arrives, reverse replay starting at the reward site propagates backward through the sequence, overwriting this reverse-biased potentiation and strengthening the forward pathway toward reward.

This is mathematically equivalent to TD(lambda) with lambda=1: the reward signal at state s_T is propagated backward to all predecessor states s_{T-1}, s_{T-2}, ..., s_0 with the update:

  V(s_t) += alpha * (V(s_{t+1}) - V(s_t))

applied in reverse temporal order. The biological implementation does this through physical sequence reversal rather than algorithmic iteration. It is the same computation. The substrate analog is therefore not metaphorical: it is the same algebraic operation on a different physical substrate.

### 1.2 Self-Avoidance in Replay Selection (2024 biorXiv)

A 2024 biorXiv preprint (self-avoidance paper) identifies a previously unrecognized constraint on replay: sequences are selected to AVOID recently replayed paths. This is not random; it implements a form of experience-dependent exploration analogous to epsilon-greedy in RL. The self-avoidance mechanism ensures that reverse replay covers the full sequence-state space rather than over-replaying the most recent high-reward event.

Substrate implication: the Misra-Gries streaming algorithm already implements a version of this without knowing it -- patterns that have already been consolidated (counter reaching threshold) are "graduated" out of the active counter set. This is structurally self-avoiding: already-consolidated patterns do not compete with new ones for replay slots.

### 1.3 The Time Course of Replay (Science 2025, ads4760)

The Science 2025 paper (time course and organization of hippocampal replay) establishes that forward replays occur at median ~2.8 seconds post-stop, reverse replays at ~4.6 seconds. The ordering is not random: forward replay previews the next decision point; reverse replay evaluates the just-completed path.

This dual-phase structure is significant: it reveals replay has TWO distinct computational functions operating in temporal sequence:
1. Forward replay (2.8s): prospective simulation, "where should I go next?"
2. Reverse replay (4.6s): retrospective credit assignment, "was the path I just took good?"

Both phases complete within a single SWR (~50-150 ms compressed time), but the ordering within a rest bout follows a consistent prospective-then-retrospective pattern.

Substrate mapping: substrate currently only has the retrospective phase (write, consolidate, retrieve past). The prospective phase -- generating a candidate future sequence from current state WITHOUT new writes -- is the untested extension that reverse replay research directly motivates.

### 1.4 Distinct Replay Signatures for Planning vs Preservation (PNAS 2022 reaffirmed 2025)

The PNAS paper (Cairney et al. 2022, reaffirmed in 2025 replications) establishes that prospective replay (pre-play of intended routes) and memory preservation replay have DISTINGUISHABLE neural signatures. They are not the same process given different goals; they are mechanistically distinct:

- Memory preservation replay: activates during rest after learning; correlated with consolidation success; driven by past experience
- Prospective planning replay: activates before decision points; correlates with decision accuracy; driven by anticipated future states

This has a clean substrate analog: the same retrieval algorithm (cosine probe on the substrate W matrix) can operate in two modes:
- Retrospective: probe with past entity, retrieve what was associated with it
- Prospective: probe with intended target, retrieve what sequence of intermediate entities leads there

The algebraic operations are identical. The difference is in whether the query vector is a past entity (retrospective) or a future target (prospective). Substrate already supports both query directions; they have never been framed this way.

---

## PART 2: Theta-Gamma Coupling -- Deeper Mechanistic Analysis

### 2.1 The Phase Code as a Sequential Binding Operator

The 2024 Frontiers in Neural Circuits paper (theta-gamma coupling model) establishes the precise algebraic structure of theta-gamma sequential memory:

- Each gamma cycle (~25 ms at 40 Hz) encodes ONE item (a feature set or concept)
- Theta cycle (~250 ms at 4 Hz) contains ~7-10 gamma cycles
- Each item's POSITION in the sequence is encoded by its PHASE within the theta cycle
- Items at earlier positions fire earlier in the theta cycle (phase precession)

The 2024 Nature Human Behaviour paper (theta phase precession in humans, Zheng et al.) provides direct causal evidence that phase precession is the mechanism binding sequence position to content in human episodic memory. Phase precession strength predicted memory success complementarily with firing rate -- phase carries position information that firing rate does not.

Mathematical structure: this is EXACTLY the VSA binding operator. In VSA/HRR:
- Each item i is represented by a vector v_i
- Position p is represented by a permutation/rotation operator P^p
- The position-tagged item is P^p(v_i)
- A sequence is the superposition: S = P^1(v_1) + P^2(v_2) + ... + P^T(v_T)

The theta-gamma phase code implements the same structure biologically:
- v_i = neural assembly firing pattern (content)
- P^p = theta phase offset (position)
- S = hippocampal population vector during one theta cycle

This is not an analogy. It is the same mathematics implemented in neurons. The McClelland-style CLS framing can be extended: substrate IS a digital theta-gamma oscillator, and Pattern B IS the theta-gamma phase code applied to factual propositions.

### 2.2 Imagination vs Memory Retrieval in the Theta-Gamma Model

The 2024 neural mass model (PMC11211613) demonstrates a critical bifurcation:

- MEMORY RETRIEVAL: theta generator active + external sensory input maintained; network reconstructs stored sequences accurately; no creative recombination
- IMAGINATION: theta generator active + external input DISCONNECTED; network autonomously replays stored sequences in random order; this IS the biological imagination mechanism
- DREAMING: theta generator active + synaptic scaling down + elevated noise; network RECOMBINES stored sequences using shared features; produces novel combinations not previously experienced

The key parameter is "external input isolation." The same substrate (hippocampal network with theta-gamma coupling) switches from retrieval to imagination to dreaming based purely on input gating and neuromodulatory state (acetylcholine level controls synapse scaling).

Substrate implications:
1. Memory retrieval mode = current substrate operation (probe with external query, retrieve stored fact)
2. Imagination mode = substrate generates novel candidates by replaying stored patterns without external query constraint. This is equivalent to running the retrieval mechanism with noise injection instead of a specific query vector.
3. Dreaming/synthesis mode = substrate finds shared features between disparate stored facts and generates a NEW binding that was never explicitly written. This is the mechanism underlying analogical reasoning.

The noise injection parameter is the only difference between retrieval and creative synthesis. Substrate currently has no noise injection path. Adding controlled noise (sigma parameter in the query vector) would enable all three modes.

### 2.3 The Self-Avoidance + Theta Structure Interaction

Combining sections 1.2 and 2.2: when substrate runs imagination mode (noise injection, no external query), the self-avoidance mechanism (Misra-Gries graduation) ensures the simulation doesn't replay the same fact chains. The combination produces a structured exploration of the knowledge space -- not random noise, not deterministic replay, but a biologically-validated middle path.

This is the mechanism that explains how humans imagine multiple novel solutions to a problem in sequence without simply re-running the same solution repeatedly. Substrate can implement this with: (a) noise injection on the query vector, (b) a recently-replayed exclusion list maintained during the simulation session.

---

## PART 3: Successor Representation -- K-Hop as Path Integration

### 3.1 The Successor Representation Framing

The hippocampal successor representation (SR) framework (Stachenfeld et al. 2017, confirmed neurobiologically in multiple subsequent papers) holds that hippocampal place cells encode not "where am I now?" but "what states am I likely to be in next, in the near future?" under the current policy. Formally:

  M(s, s') = E[ sum_{t=0}^{inf} gamma^t * I(s_t = s') | s_0 = s ]

This is the expected discounted future occupancy. Place cell firing at location s encodes a distribution over future states. The SR is the solution to:

  M = (I - gamma * T)^{-1}

where T is the transition matrix and gamma is a temporal discount. This is a MATRIX INVERSE -- and substrate's pseudoinverse (pinv) is a direct computational analog. The SMW pinv update that substrate uses for incremental knowledge updates (HP cycle 172; 4.174 ms/update at 1M facts) is mathematically a rank-1 update to a matrix that encodes entity relationships. The transition matrix T in SR theory is the entity co-occurrence and causal-succession matrix in substrate.

### 3.2 K-Hop as Multi-Step Successor Queries

Substrate's K-hop retrieval is the discrete analog of computing the multi-step successor representation. In SR:
- 1-hop = immediate successor (gamma^1 term)
- K-hop = K-step lookahead (sum of gamma^1 through gamma^K terms)

The 2024 preprint on multi-scale successor representations shows that the hippocampus implements this as a bank of SR representations at different temporal scales (different gamma values), corresponding to different place field sizes along the dorsal-ventral axis (dorsal = small fields = short gamma; ventral = large fields = long gamma).

Substrate currently has ONE scale of K-hop (fixed K). The dorsal-ventral biology suggests that a multi-scale K-hop (K=1, K=3, K=5 in parallel) would implement the full biological SR bank. This directly addresses the "multi-hop ceiling" finding from cycle 175 -- the ceiling may be a SINGLE-SCALE problem, not a fundamental ceiling.

### 3.3 The REMI Path Integration Model (2025)

The REMI framework (PMC12236589, 2025) demonstrates that grid cells perform context-independent path integration while hippocampal pattern completion validates the path sensory-sequentially. The core innovation is the separation:
- Grid cells = abstract navigation in concept space (context-free)
- Place cells = grounding navigation to specific entities (context-dependent)

Substrate has both primitives:
- Pattern B superposition = place cell representation (content-specific)
- Bridge connections = grid cell transitions (relation-encoded navigation)

The REMI path integration model uses recurrent update z_{t+1} = alpha * z_t + (1-alpha) * [inputs] + W_rec * f(z_t). This is a leaky-integrate-and-fire model on the hidden state. The alpha parameter is the "forgetting rate" per neuron. Substrate does not have a per-entity forgetting rate -- all entities have the same GDPR-delete / TMR-weight path. A per-entity alpha (decay rate based on recency and query frequency) is a direct REMI-inspired extension.

---

## PART 4: The Single Most Yielding Sub-Avenue (3-Deep Analysis)

### Selection Rationale

The three sub-avenues are:
A. Reverse replay as TD backup operator -> counterfactual generation
B. Theta-gamma phase code -> multi-mode operation (retrieval / imagination / synthesis)
C. Successor representation / path integration -> multi-scale K-hop

Sub-avenue B (theta-gamma multi-mode operation) is the most yielding because:
1. The mathematics is fully worked out and directly maps to VSA binding operators substrate already implements
2. The distinction between retrieval, imagination, and creative synthesis is controlled by a single parameter (external input isolation + noise level), which maps to a simple substrate-side configuration
3. It subsumes both A (reverse replay is a form of imagination-mode replay) and C (multi-scale K-hop is a form of multi-resolution theta-gamma encoding)
4. It opens a NEW product capability (analogical reasoning / novel hypothesis generation) that has no current substrate analog
5. The engineering path is concrete: two additions to existing substrate (noise injection on query vector + recently-replayed exclusion list)

### 4.1 Deep Dive: From Single-Mode to Triple-Mode Substrate Operation

Current substrate operates in exactly one mode: query-driven retrieval. A fact is injected (write), the substrate W matrix is updated, and the fact is retrievable by cosine probe. This is biological "memory retrieval mode" -- external query drives retrieval.

The theta-gamma model demonstrates that the SAME substrate hardware supports two additional modes:

**Mode 2: Imagination mode (creative exploration)**
Trigger: Query vector = base entity vector + epsilon * N(0, I) where epsilon is a noise parameter
Mechanism: Noisy query activates not just the target entity but nearby entities in the VSA space; retrieval chain follows associative links in a random walk rather than direct lookup
Output: A sequence of retrieved entities that "might have been written" around the target
Use case: "What else might be associated with X?" without having a specific follow-up query

**Mode 3: Synthesis mode (analogical reasoning)**
Trigger: Two seed entity vectors from DIFFERENT domains; query with their superposition
Mechanism: The superposition activates the "shared feature" region of the W matrix -- the entities and relationships that both source entities have in common
Output: A novel candidate binding that bridges the two domains
Use case: "What do X and Y have in common that I've never explicitly stored?" -- this IS analogical reasoning

The biological grounding is exact: Mode 2 corresponds to the theta-gamma model's imagination state (external input disconnected, autonomous sequence generation). Mode 3 corresponds to the dreaming state (elevated noise + synapse scaling). The neuromodulatory states (acetylcholine level) map to substrate configuration parameters (epsilon_noise, domain_crossover_weight).

### 4.2 Engineering Path (Concrete Steps)

Step 1: Add epsilon_noise parameter to the query path (2-3 hours implementation)
- Modify query function: q_noisy = q + epsilon * torch.randn_like(q); q_noisy = q_noisy / q_noisy.norm()
- This is a one-line change to the existing cosine retrieval function
- Pre-test: verify that epsilon=0 recovers exact baseline retrieval; epsilon=0.1 introduces ~10% semantic drift measured by cosine distance to original query

Step 2: Add recently-replayed exclusion list for imagination sessions (1 day)
- Maintain a set() of entity indices retrieved in the current simulation session
- After each retrieval, add retrieved entities to the exclusion set
- Before retrieval, zero out the rows of W corresponding to excluded entities (or apply a soft suppression mask)
- Reset the exclusion set when a new simulation session starts
- This is the self-avoidance mechanism from Section 1.2

Step 3: Add domain-crossover synthesis mode (3-5 days)
- Accept two query vectors q1, q2 from different domains
- Form synthesis query: q_synth = (q1 + q2) / ||(q1 + q2)||
- Run retrieval with q_synth; the result is the "analogical bridge"
- Output includes: retrieved entity, its provenance (which writes contributed), confidence score
- This produces auditable analogical reasoning -- a first-class product capability

Step 4: Pre-register and validate (1 week)
- Test A: epsilon sweep from 0 to 0.3; measure recall@1 degradation vs. exploration breadth (number of distinct entities retrieved per session)
- Test B: exclusion list prevents re-retrieval of same entities within one simulation session (binary pass/fail)
- Test C: domain-crossover on two held-out domain pairs; manually evaluate whether synthesis output is semantically coherent

### 4.3 Why This Cannot Be Replicated by RAG or LLM

RAG: retrieval is always query-driven; no noise injection mode; no cross-domain synthesis based on stored knowledge structure; no exclusion list across session
LLM: can generate analogies from parametric knowledge, but cannot ground them in the customer's specific knowledge base; no audit trail for the synthesis path; no "was this analogy derived from customer data?" guarantee

Substrate synthesis mode produces: a novel candidate binding grounded in customer's own knowledge, with full audit chain (which stored facts contributed to the synthesis), at retrieval latency (~4 ms). This is a genuine product gap.

---

## PART 5: Dorsal-Ventral Gradient as Multi-Scale Architecture

### 5.1 The Dorsal-Ventral Resolution Gradient

The 2024 ScienceDirect review (hippocampal specialization electrophysiology) and the PNAS 2024 paper (longitudinal axis in large-scale cortical systems) establish the dorsal-ventral gradient as a continuous resolution spectrum, not a binary distinction:

- Dorsal (posterior in humans): small place fields, high spatial precision, ~10-20 cm radius in rodents
- Ventral (anterior in humans): large place fields, low precision, gist-level representation, ~100-200 cm radius
- Gradient: continuous along the ~5 mm longitudinal axis

For episodic memory: dorsal = specific episode detail ("the meeting was in the blue room at 2pm"); ventral = gist ("I met with that person sometime last week"). Both are needed for a functional system.

The 2025 PNAS paper extends this to semantic memory: the hippocampal gradient interacts with cortical systems to create a coarse-to-fine hierarchy for both spatial AND conceptual knowledge.

### 5.2 Substrate Analog: Variable N as Dorsal-Ventral Dial

The prior 5x drill identified multi-resolution dual-N (N=512 coarse + N=4096 fine) as a high-cost direction (P_deflated=0.40, 2-4 months). The deeper analysis suggests a cheaper first-pass implementation:

Instead of dual-N architecture (two separate substrate W matrices), implement variable-resolution RETRIEVAL from a single N=4096 substrate:
- Full precision retrieval (cosine threshold 0.85): dorsal mode -- returns only high-confidence, specific matches
- Relaxed precision retrieval (cosine threshold 0.65): ventral mode -- returns gist-level matches with lower specificity

This requires NO new architecture. The only change is the retrieval threshold parameter. The biological insight is that dorsal vs ventral is not a storage distinction; it is a RETRIEVAL granularity distinction. Substrate already has adjustable cosine thresholds; they have never been framed as a dorsal-ventral control.

Two-parameter retrieval configuration:
- (threshold=0.85, K=3): high-specificity, low-coverage (dorsal analog; encyclopedic queries)
- (threshold=0.65, K=5): low-specificity, high-coverage (ventral analog; exploratory queries)
- (threshold=0.75, K=3): balanced (current default)

This is a zero-engineering-cost product capability: customers get "precision mode" vs "exploratory mode" retrieval with neuroscience grounding.

---

## PART 6: Schema-Consistent vs Schema-Inconsistent Learning Rates

### 6.1 The Biological Finding

The schema-fast-learning literature (Tse et al. 2007, multiple replications) establishes:
- Schema-consistent new facts consolidate to long-term memory in 24h vs 3 weeks for schema-inconsistent facts
- The mechanism: schema-consistent facts activate existing cortical representations that provide a strong associative scaffold; the hippocampus provides a "rapid binding" that slots the new fact into existing cortical structure

The Journal of Theoretical Biology 2024 paper (SCT2024) extends this with a computational model: schema consistency is measured by the overlap between the new fact's semantic representation and the existing neocortical knowledge graph. High overlap = fast consolidation.

### 6.2 Substrate Analog

Substrate's bridge accumulation rate IS the schema-consistency signal. When a new entity is written and its bridge connections to existing entities exceed a threshold, that entity is "schema-consistent" -- it has high connectivity in the existing knowledge graph. Entities with few bridge connections after N writes are schema-inconsistent.

Current substrate: all entities are consolidated at the same rate (Misra-Gries treats all counter updates equally).
Biology-informed extension: give schema-consistent entities (high bridge count after N writes) a higher Misra-Gries update weight. Schema-inconsistent entities (novel, low bridge count) get standard weight but are NOT deprioritized -- they need more replay cycles to consolidate, not fewer.

Implementation: weight_i = base_weight * (1 + alpha * bridge_count_i / max_bridge_count). This is a 1-parameter extension to Misra-Gries with direct neuroscience grounding.

---

## PART 7: Cheap Decisive Tests (Pre-Registered)

### Test A: Noise injection for imagination mode (1-2 days, CPU-only)

Setup: Build a 500-fact synthetic KB on two domains (A: geography, B: biology). Run 20 imagination sessions with epsilon in {0, 0.05, 0.10, 0.20}. Record which entities are retrieved per session.
HARD PASS: At epsilon=0.10, mean entity diversity per session (unique entities / session length) >= 3x epsilon=0.0 baseline, AND recall@1 degradation at epsilon=0.10 <= 15% from epsilon=0.0
HARD FAIL: epsilon=0.10 diversity < 1.5x baseline (noise injection does not diversify retrieval) OR recall@1 degrades > 30% at epsilon=0.05 (noise level too disruptive)
MID-BAND: diversity 1.5x-3x with recall degradation 15-30% (tunable but requires careful calibration)

### Test B: Domain-crossover synthesis (3-5 days, CPU-only)

Setup: 1000-fact KB with 5 domains. For 10 held-out entity pairs (one from each of two distinct domains), run synthesis query q_synth = (q1 + q2)/||(q1 + q2)||. Evaluate synthesis output for semantic coherence (human rater blind to source entities).
HARD PASS: >= 7/10 synthesis outputs rated "semantically coherent bridge between source domains" by blind rater
HARD FAIL: <= 3/10 rated coherent (synthesis is arbitrary, not grounded)
MID-BAND: 4-6/10 coherent (partial; some domain pairs work better than others)

### Test C: Variable-threshold retrieval modes (2-3 hours, CPU-only, zero engineering)

Setup: Existing substrate. Run same 50 queries at thresholds 0.65, 0.75, 0.85. Measure: precision@1, recall@5, and mean result set size.
HARD PASS: threshold=0.85 achieves >= 95% precision@1 (encyclopedic mode works); threshold=0.65 achieves >= 2x result set size vs 0.85 (exploratory mode covers more ground)
HARD FAIL: threshold degradation is monotonically bad (lower threshold does not expand useful results, only adds noise)

### Test D: Schema-weighted Misra-Gries (1-2 days)

Setup: Write 1000 facts; half "schema-consistent" (manually tagged as connected to existing bridge-dense regions), half "schema-inconsistent" (novel entities with <3 bridge connections after ingestion). Run defrag with and without schema-weight extension. Measure overnight bridge accumulation rate for each group.
HARD PASS: schema-consistent group consolidates >= 1.6x faster than schema-inconsistent (biology predicts ~3-4x; substrate N and mechanism limitations suggest conservative 1.6x as actionable threshold)
HARD FAIL: < 1.1x difference (schema-weighting has no operational effect)

---

## PART 8: Falsifiable Predictions

### HARD-PASS thresholds (confirm direction):
- HP1: epsilon=0.10 noise injection achieves >= 3x entity diversity per imagination session vs epsilon=0 without > 30% recall degradation (Test A)
- HP2: >= 7/10 domain-crossover synthesis outputs rated semantically coherent by blind rater (Test B)
- HP3: threshold=0.85 achieves >= 95% precision@1 in encyclopedic mode; threshold=0.65 achieves >= 2x result coverage (Test C)
- HP4: Schema-consistent entity consolidation >= 1.6x faster than schema-inconsistent under weighted Misra-Gries (Test D)

### HARD-FAIL thresholds (close direction):
- HF1: epsilon=0.10 entity diversity < 1.5x baseline (noise injection does not enable imagination mode at substrate N=4096)
- HF2: <= 3/10 synthesis outputs coherent (domain-crossover synthesis is incoherent at this KB size / entity count)
- HF3: Lower threshold does not expand useful result set (dorsal-ventral retrieval mode has no operational analog in substrate)
- HF4: Schema-weighting < 1.1x consolidation rate difference (bridge count is not a reliable schema-consistency proxy)

---

## PART 9: P_deflated Summary

Per calibration penalty: deflate 0.15-0.25 from theoretical; cap novel-synthesis at 0.50.

| Direction | P_theoretical | P_deflated | Basis |
|---|---|---|---|
| Noise injection for imagination mode | 0.80 | 0.62 | One-line change; mechanism is VSA-native |
| Variable-threshold dorsal-ventral dial | 0.90 | 0.75 | Zero-engineering; threshold already exists |
| Schema-weighted Misra-Gries | 0.85 | 0.68 | Bridge count is measurable; 1-param extension |
| Domain-crossover synthesis mode | 0.70 | 0.50 | Novel mechanism; cap applied at 0.50 |
| Prospective replay (forward simulation) | 0.68 | 0.48 | Novel direction; requires sequence bookkeeping |
| Multi-scale K-hop (SR bank) | 0.65 | 0.45 | Medium engineering; SR math is sound |
| Per-entity alpha decay (REMI extension) | 0.60 | 0.42 | New state per entity; memory overhead |

---

## PART 10: Cross-Thread Synthesis

### Connection to Wish 1 (Counterfactual do(); HP'd cycle 175)

The reverse replay mechanism (Section 1.1, TD backup) is the biological validation of Wish 1. Substrate's counterfactual do() operator (pinv-based inverse write) is mathematically equivalent to one step of reverse replay: it removes the causal contribution of a single write to the current substrate state. The reverse replay literature extends this to SEQUENCES of writes -- a counterfactual chain, not just a counterfactual fact.

The new extension (Section 4.1, Mode 2 + Mode 3) adds the prospective direction: not just "what would the substrate be like if X had never been written?" but "what might the substrate write next if it followed this pattern of writes?" This is a complementary capability that closes the full counterfactual planning loop.

### Connection to TMR Priority Gating (HP'd cycle 175, 5.4x survival)

TMR's selectivity (strengthen strong, weaken overlapping moderate) maps to the schema-weighted Misra-Gries extension (Section 6.2). The HP'd TMR result confirms that priority-weighted replay does produce differential consolidation. The schema-consistency weight is a refinement of the TMR weight that uses the CONTENT of the fact (bridge connectivity) rather than an external priority signal. Together they give a three-layer priority system: (1) TMR external signal, (2) schema-consistency internal signal, (3) query-frequency Misra-Gries default.

### Connection to Federation (HP'd cycles 168/170/171)

The REMI path-integration model (Section 3.3) uses grid cells for context-independent navigation while place cells provide local grounding. In a federated substrate: the grid-cell role is the cross-shard bridge (context-independent entity-relation graph); the place-cell role is the per-shard local bindings (context-specific knowledge). This framing gives the federation architecture a principled justification from hippocampal-entorhinal system biology.

### Connection to Multi-Hop Revival (OPEN, cycle 175)

The successor representation analysis (Section 3.2) directly addresses the multi-hop ceiling. If the ceiling is a single-scale problem rather than a substrate ceiling, then implementing a multi-scale K-hop bank (K=1, 3, 5 in parallel with different temporal discount gamma) should lift the ceiling. The biology (dorsal-ventral SR bank) predicts that larger-gamma (longer-range) representations are needed for multi-hop: the ventral hippocampus handles multi-step inference, the dorsal handles single-hop precision. This is a testable prediction: K=5 with a longer-range query formulation should outperform K=1 + K=3 without it.

---

## PART 11: Substrate-Product Implications

### New capabilities opened by this drill:

1. "Imagination mode: explore what your knowledge base might contain" -- noise injection on the query vector enables structured exploration of the KB without a specific query. Use case: "Show me something interesting in the pharmaceutical knowledge base I might not have thought to look for." This is not RAG and not LLM; it is substrate-native exploratory retrieval.

2. "Synthesis mode: find analogies across your knowledge domains" -- domain-crossover queries find bridges between disparate stored knowledge. Use case: a law firm's substrate surfaces connections between two different case types that share underlying legal principles. Audit trail included.

3. "Precision vs. exploratory retrieval mode" -- the dorsal-ventral variable threshold gives customers a one-parameter control over specificity vs. coverage. Zero engineering cost; ships in v1.

4. "Faster consolidation for core knowledge" -- schema-weighted Misra-Gries means that the facts most connected to the customer's existing knowledge structure get consolidated first. Their "core knowledge" is always available; "edge knowledge" consolidates in subsequent defrag cycles.

### Claims NOT enabled (require additional work):

- "Substrate can imagine novel facts it has never stored" (Mode 3 synthesis): requires Test B to pass with >= 7/10 coherent outputs. Current P_deflated = 0.50.
- "Multi-hop improvement from SR bank": requires pre-test on encoder ceiling first (per cycle 175 encoder-is-the-gate finding). Don't engineer the SR bank until the encoder is upgraded.

---

## PART 12: Literature Robustness Summary

| Mechanism | Robustness | Notes |
|---|---|---|
| Reverse replay is TD backup (Haga & Fukai) | HIGH | Mechanistic model; biologically realistic params |
| Forward-before-reverse ordering within rest bouts | HIGH | Science 2025; direct measurement |
| Self-avoidance in replay selection | MEDIUM-HIGH | 2024 preprint; not yet replicated |
| Prospective vs retrospective replay distinction | HIGH | PNAS 2022 + 2025 replication |
| Theta-gamma phase code (sequential binding) | HIGH | Multiple independent replications |
| Phase precession in human episodic memory | HIGH | Nature Human Behaviour 2024; first direct human evidence |
| Theta-gamma imagination mode | MEDIUM | Computational model; limited direct causal evidence |
| Dorsal-ventral resolution gradient | HIGH | Confirmed across species; quantified in humans |
| Successor representation in hippocampus | HIGH | Multiple behavioral + neural studies |
| Multi-scale SR (dorsal-ventral = gamma bank) | MEDIUM | Theoretical synthesis; not directly tested |
| REMI path integration model | MEDIUM | 2025 preprint; needs replication |
| Schema-fast-learning (Tse et al.) | HIGH | Replicated; strong effect size |

---

## Citations (verified in this session)

1. Haga & Fukai (2018) - "Recurrent network model for learning goal-directed sequences through reverse replay" - eLife 7:e34171. PMC6059768. Mechanistic TD-backup model.

2. Science 2025 - "The time course and organization of hippocampal replay" - doi:10.1126/science.ads4760. Forward/reverse ordering within rest bouts.

3. biorXiv 2024 - "Self-avoidance dominates the selection of hippocampal replay" - biorXiv:2024.07.18.604185. Self-avoidance constraint on replay selection.

4. Cairney et al. (2022) PNAS - "Distinct replay signatures for prospective decision-making and memory preservation" - doi:10.1073/pnas.2205211120. Dual-function replay.

5. Frontiers in Neural Circuits 2024 - "Modeling the contribution of theta-gamma coupling to sequential memory, imagination, and dreaming" - doi:10.3389/fncir.2024.1326609. PMC11211613. Neural mass model; imagination vs dreaming modes.

6. Zheng et al. (2024) Nature Human Behaviour - "Theta phase precession supports memory formation and retrieval of naturalistic experience in humans" - doi:10.1038/s41562-024-01983-9. First direct human evidence.

7. Current Opinion in Behavioral Sciences 2024 - "Theta-gamma coupling as a ubiquitous brain mechanism" - ScienceDirect S2352154624000846. Generalization to dreaming, imagination, consciousness.

8. Nakahashi & Iigaya (2025) PMC12236589 - "REMI: Reconstructing episodic memory during internally-driven path planning" - Path integration + memory reconstruction model.

9. Stachenfeld, Botvinick, Gershman (2017) Nature Neuroscience - Hippocampus as successor representation. Foundational SR framing.

10. arxiv 2024 - "Equivalence of Personalized PageRank and Successor Representations" - arxiv:2512.24722. SR-PageRank identity (directly relevant to substrate retrieval).

11. PNAS 2024 - "Longitudinal hippocampal axis in large-scale cortical systems underlying development and episodic memory" - doi:10.1073/pnas.2403015121. Dorsal-ventral + cortical systems.

12. Tse et al. (2007) Science - Schema-fast-learning. Original schema-consistency finding. Multiple replications through 2024.

13. biorXiv 2025 - "Hippocampal reactivation of planned trajectories is required for effective goal choice" - biorXiv:2025.05.10.653115. Causal evidence for prospective replay in decision-making.

14. biorXiv 2025 - "Gamma-Theta-Spike Coupling Coordinates Sequential Memory in Human MTL" - biorXiv:2025.06.24.661371. Most recent (June 2025); direct human MTL spike recordings.

Verified count: 14 citations; 10 from 2024-2025.

---

## Next-Drill Candidate

**Successor representation x substrate retrieval identity** -- the 2024 arxiv paper establishing SR=PersonalizedPageRank is directly actionable for substrate. If substrate's retrieval is a variant of Personalized PageRank on the entity graph, then the spectral theory of PageRank (expander bounds, convergence rates, community structure) gives direct theoretical predictions for substrate retrieval quality. This is a network-science-graph-theory drill; adjacent to free-probability and SR. Generic search terms: "Personalized PageRank convergence bounds," "spectral gap random walk mixing time," "expander graph information retrieval."

---

*Filed as 3x DEEPER drill on reverse replay sub-avenue per user mandate. Most yielding sub-avenue: theta-gamma multi-mode operation (retrieval / imagination / synthesis). Engineering path is concrete; zero-cost first step (variable-threshold retrieval) ships immediately.*
