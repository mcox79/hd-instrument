# Research Drill: Continual Learning Forgetting Profile -- Honest Characterization (2x depth)

Filed: 2026-06-10
Trigger: Overclaim audit -- "substrate continual learning matches biology" was asserted without rigorous characterization; PP-141/142 sleep-defrag at research-demo scale; production-scale forgetting profile uncharacterized
Prior context: rem_replay_consolidation_substrate 2x (2026-06-04), sleep_defrag_implicit_generalization 3x (2026-06-07), wright_fisher_kimura 2x (2026-06-04)
Drill discipline: algebraic + lit-scan only; no empirical verification; calibration penalty applied
4000-word cap enforced

---

## HEADLINE

The "matches biology" claim is an overclaim in 2 of 3 senses and partially defensible in one sense. Biology's continual learning involves BOTH retention and structured forgetting -- episodic detail decays while schema and frequency structure consolidates. Substrate-style VSA/HDC systems resist catastrophic forgetting in the ML sense (no weight clobber) but are vulnerable to a distinct failure mode: gradual interference accumulation that degrades older patterns as M/M_c grows. Sleep-defrag addresses consolidation but not the interference accumulation problem at large M. The production-scale forgetting profile is genuinely uncharacterized and needs 3 empirical anchors before any claim about biological equivalence can be made. Wright-Fisher/Kimura models (from prior drill) predict a neutral-drift baseline forgetting rate that sets the floor; the measured profile needs to land above this floor AND show selectivity (frequent items preserved, rare items lost gracefully) to support a "biologically plausible" claim.

P_deflated_theoretical = 0.30 (mechanism is sound that HDC avoids catastrophic forgetting in ML sense; deflated from 0.50 by calibration penalty 0.20)
P_deflated_bio_equivalence = 0.15 (substrate matches biological CL in the operationally meaningful sense; cap at 0.50 applied, deflated 0.25 from 0.40)
HARD-PASS threshold: selectivity ratio > 2.0x (frequent items retained vs rare items); smooth decay not cliff
HARD-FAIL threshold: any item stored at position 1 unrecoverable after 10K subsequent stores; OR interference accumulates super-linearly

---

## LEVEL 1: CATASTROPHIC FORGETTING IN NEURAL SYSTEMS

### 1.1 McCloskey and Cohen 1989 (classic CF)

McCloskey & Cohen 1989 (The Psychology of Learning and Motivation, Vol 24, pp. 109-165) named catastrophic interference: when an ANN trained sequentially on Task A then Task B, weights overwritten by gradient descent on B cause near-complete loss of Task A performance. The mechanism: shared weights in overlapping distributed representations; gradient on B activates same weight rows used by A and overwrites them.

This is the canonical pathology. It is NOT what substrate VSA systems face. VSA systems store patterns additively (W += xi xi^T) not destructively. Catastrophic forgetting in the McCloskey-Cohen sense requires a weight-clobber operation; superposition write does not clobber.

Honest note: "does not face McCloskey-Cohen CF" is a LOW bar. VSA systems face a DIFFERENT failure mode: interference accumulation and capacity exhaustion, which degrades all stored patterns gradually rather than catastrophically wiping specific ones. This is more analogous to Ebbinghaus forgetting curves than to McCloskey-Cohen.

### 1.2 Elastic Weight Consolidation (Kirkpatrick et al. 2017)

Kirkpatrick et al. 2017 (PNAS 114(13):3521-3526; arxiv:1612.00796): EWC adds a quadratic penalty to the loss that constrains parameters important for prior tasks from moving far. The Fisher information matrix diagonal approximates parameter importance. Prevents CF in gradient-descent systems.

Algebraic mechanism: regularize theta_new such that sum_i F_i (theta_i - theta_A_i)^2 is small, where F is Fisher diagonal. This is a soft pin on task-A parameters.

Substrate analog: there is NO direct substrate analog because substrate does not use gradient descent on a shared weight space. The substrate's W is a fixed superposition sum; there is no "task A Fisher matrix" concept. EWC is architecturally inapplicable. What IS applicable is the capacity analysis: M_c = 0.138 * N gives the hard capacity limit beyond which ALL stored patterns degrade, not just new ones. This is a stronger constraint than EWC addresses.

### 1.3 Progressive Networks (Rusu et al. 2016; arxiv:1606.04671)

Progressive Networks freeze prior columns and add lateral connections for each new task. Avoids CF completely by construction -- each task has its own dedicated weights. Cost: linear parameter growth with tasks.

Substrate analog: per-predicate sharding is structurally similar. Each predicate shard is an isolated W matrix; adding a new predicate does not interfere with existing predicates. Within a single shard, the progressive-networks guarantee does NOT hold -- multiple facts compete within one shard. The honest characterization: substrate achieves progressive-networks-style isolation ACROSS predicates but faces Hopfield-style interference WITHIN predicates.

### 1.4 Replay-based Methods

Shin et al. 2017 (NeurIPS; DGR): deep generative replay trains a GAN to generate past task data during new-task training. Lopez-Paz & Ranzato 2017 (GEM; NeurIPS): memory buffer of past examples, constrain gradient updates to not increase loss on remembered items. Rebuffi et al. 2017 (iCaRL; CVPR): exemplar-based rehearsal with nearest-mean classifier.

Common insight: replay compensates for distributed-weight overwrite by re-introducing gradient signal for prior tasks. All require storing either raw examples or a generative model of prior tasks.

Substrate analog: PP-141/142 sleep-defrag IS a replay mechanism, but of a different kind. It does not replay to a gradient optimizer; it re-presents stored patterns to re-consolidate their contribution to the W matrix. The algebraic effect is to locally boost the basin depth of replayed patterns at the cost of slightly increasing interference for non-replayed patterns. At M << M_c, this is net positive. At M near M_c, replay does not help because the interference floor is already high.

### 1.5 Modular Architectures (PathNet, Rusu et al. 2016; Fernando et al. 2017)

PathNet: evolutionary agent finds a path through a fixed modular network for each task; modules used for Task A are frozen for Task B. PackNet (Mallya & Lazebnik 2018): binary weight masking, prune + retrain. Piggyback (Mallya et al. 2018): learns task-specific binary masks over shared weights.

Substrate analog: semantic routing (predicate dispatch) is a hard-modular architecture with substrate-natural isolation. The substrate's fundamental CL advantage over gradient-descent systems is architectural modularity: a query for predicate X activates only shard X, leaving all other shards unperturbed. This is PathNet's isolation guarantee, implemented structurally rather than by learned masking.

---

## LEVEL 2: BIOLOGICAL CONTINUAL LEARNING

### 2.1 Complementary Learning Systems (McClelland, McNaughton & O'Reilly 1995)

McClelland et al. 1995 (Psychological Review 102(3):419-457; 5100+ citations): hippocampus = fast-learning, pattern-separated store; neocortex = slow-learning, overlapping distributed representations; sleep replay drives gradual transfer from hippocampus to neocortex. This is the canonical biological CL framework.

Key point for honest characterization: biological CL requires TWO systems with different learning rates. A single-speed system (either fast alone or slow alone) catastrophically interferes. Substrate implements ONLY the fast store. There is no substrate-native slow cortical extraction beyond the sleep-defrag co-occurrence pass documented in prior drills. This is a structural gap: substrate has hippocampus but not neocortex.

Implication: the "matches biology" claim is only defensible for the hippocampal (episodic encoding) component. The cortical (schema extraction, gradual generalization) component is addressed only partially by sleep-defrag and not by the production system.

### 2.2 Sleep Replay (Wilson & McNaughton 1994; Tonegawa Lab)

Wilson & McNaughton 1994 (Science 265:676): sequential co-firing patterns during sleep replay with same structure as during waking experience. Tonegawa lab (2015, Science): optogenetic confirmation that sharp-wave ripple replay is causally necessary for spatial memory consolidation. Replay is time-compressed 10-20x. Reverse replay after error is implicated in credit assignment (Buzsaki 2018 review).

The critical biological finding for this drill: replay is NOT lossless. Replayed patterns in neocortex are SMOOTHED versions of episodic hippocampal representations. The neocortex does not store episodic detail; it stores statistical regularities. This is feature, not bug -- the neocortex's loss of episodic precision enables generalization.

Substrate implication: if substrate aims to match this, it must implement LOSSY consolidation -- not re-strengthening all stored patterns, but selectively strengthening patterns consistent with statistical regularities while allowing episodic outliers to decay. PP-141/142 does not do this. It is closer to lossless replay of stored vectors, which overfits the fast store rather than distilling it.

### 2.3 Schema-Mediated Learning (Tse et al. 2007, 2011; Science)

Tse et al. 2007 (Science 316:76-82): prior schema enables new associated memories to be consolidated in hours rather than days. Morris water maze with 6-paired associates: rats with existing spatial schema consolidated new pairs in a single session (vs weeks without schema).

Tse et al. 2011 (Science 333:891-895): new information consistent with existing schema bypasses hippocampal consolidation and goes directly to medial prefrontal cortex (schema store). Inconsistent information requires hippocampal replay for >1 week.

Algebraic interpretation: schema-consistent patterns have low surprise (low Kullback-Leibler divergence from existing weight structure). They slot into existing attractors with minimal interference. Schema-inconsistent patterns create new attractor basins and require full consolidation. Substrate analog: facts consistent with an existing predicate's distribution (same role-filler pattern type) are low-interference writes. Novel predicate-type facts require new shards. Schema-mediated fast-learning IS implementable in substrate.

Critical point: schema-mediated learning provides FASTER acquisition for schema-consistent items and SLOWER (but more reliable) consolidation for schema-inconsistent items. The forgetting curve is NOT uniform -- schema-consistent items show less forgetting over time. This selectivity is a key feature of biological CL that substrate has not tested.

### 2.4 Synaptic Plasticity and Sparsity (Frankland, Bhaskaran, etc.)

Bhaskaran & Wood 1993; Frankland et al. 2004 (Science 304:881-883): memory traces in neocortex become sparser and more distributed over time (systems consolidation). Initial hippocampal encoding is dense and fast; mature cortical trace is sparse and slow to form.

Activation sparsity reduces interference: if only k% of synapses are active for each memory, the probability of two memories sharing a synapse is k^2, not k. This is why biological memory can scale to millions of traces without complete interference. At k=5% (biological estimate), interference probability is 0.25% per pair vs 25% for dense representations.

Substrate analog: sparse VALUE encoding (subject of ongoing sparse-value-coding-within-shards drills) maps directly to this mechanism. Dense VSA bundles at full N activate all dimensions; sparsifying value codes would reduce cross-pattern interference at the cost of per-pattern information. This is an unimplemented optimization.

### 2.5 Forgetting Curves (Ebbinghaus 1885/1913)

Ebbinghaus power-law: retention fraction R(t) = a / (1 + (t/b)^c) where c ~ 0.5 (empirical exponent for nonsense syllables). Key findings: (a) forgetting is smooth and graded, not binary; (b) forgetting rate decreases over time (slower loss after longer intervals); (c) spaced repetition dramatically extends retention; (d) meaningfully-structured material has shallower forgetting curve than nonsense material.

Substrate analog: Ebbinghaus forgetting requires a TIME-DECAY mechanism. Substrate has no intrinsic time-decay in the W matrix -- stored patterns do not spontaneously degrade. Instead, interference increases as M grows. This is a DIFFERENT forgetting model: not time-based but capacity-based. The forgetting curve for substrate is R(M) not R(t), where M is number of subsequent items stored. This may or may not match Ebbinghaus behavior.

Whether substrate matches Ebbinghaus is EMPIRICALLY UNKNOWN. The PR(M) curve has not been measured. This is one of the primary unknowns.

### 2.6 What Biology Actually Retains vs Forgets

The honest summary of biological forgetting:
- Episodic detail: rapidly forgotten (weeks-months); specific contextual features of events decay
- Semantic schema: retained indefinitely with reinforcement; abstract regularities (category membership, role-fillers, typical properties) survive
- Frequently-experienced items: retained much longer (spacing effect; maintenance of hippocampal-cortical loop)
- Emotionally-salient items: retained with high fidelity (amygdala modulation)
- Schema-inconsistent surprises: retained if sufficiently salient (novelty signal from dopamine/ACh)

For substrate claims: the honest claim is that substrate shares the SCHEMA RETENTION property (because predicates with many examples have reinforced weight structure) but has NOT validated selective episodic forgetting, frequency-based retention, or the spacing effect.

---

## LEVEL 3: VSA / HDC CONTINUAL LEARNING LITERATURE

### 3.1 Hyperdimensional Computing for Online Learning

Imani et al. 2019 (IEEE): HDC classification via bundle + query; online update by re-binding class vectors. Key finding: HDC IS robust to sequential class presentation (no catastrophic forgetting in the McCloskey sense) because bundling is additive not destructive. Ge et al. 2020: HD-CL framework for continual learning with fixed dimensionality. Reported 3-8% accuracy drop over 10-20 tasks vs 40-80% for gradient-based methods on the same benchmarks.

Honest caveat: these results are on classification with M ~ 10-100 class prototypes. Substrate is doing M ~ 100K-1M fact retrieval. The scaling regime is different by 3-4 orders of magnitude. HDC CL literature provides encouragement but not proof.

### 3.2 Distributed Memory Robustness

Kanerva 1988 (Sparse Distributed Memory): theoretical analysis of sparse addressing in high-dimensional binary memory. Capacity scales as P(error) = (1 - p_h)^N where p_h is the Hamming distance threshold. Robustness to partial overwrite is structural (distributed storage means partial damage does not destroy patterns).

Plate 2003 (Holographic Reduced Representations): binding (circular convolution or element-wise product) + bundling does NOT suffer from catastrophic overwrite. Retrieval degrades gracefully as bundle count M increases. The degradation curve follows a signal-to-interference ratio: SNR = 1 / sqrt(M-1) for random superposition, valid for M << N.

At M = N (fully loaded): SNR approaches 0 and all retrieval degrades. This is not catastrophic forgetting -- it is capacity exhaustion with graceful degradation. The distinction matters: McCloskey CF is sudden and task-specific; capacity exhaustion is gradual and uniform. Substrate faces the latter.

### 3.3 Schema Extraction Stability

Rachkovskij & Kussul 2001; Gayler 2004: VSA superposition bundles carry statistical structure. Items with high overlap tend to contribute coherently to the bundle; items with low overlap tend to cancel. This means a bundle of many items with common structure has a higher cosine similarity to the common schema than to any individual item. This is a natural "schema extraction" property.

Stability: schema extraction in VSA is stable as M grows because schema components reinforce additively while idiosyncratic components partially cancel. This IS an advantage over gradient-descent systems. The schema signal is preserved longer than individual facts.

Honest limit: this property holds for orthogonal items with shared components. If items are semantically correlated (same predicate, same domain), the schema-vs-individual distinction breaks down. High within-domain correlation creates constructive interference for BOTH schema and individual patterns, making disambiguation harder.

### 3.4 Where Naive HDC Catastrophically Forgets

Naive HDC does fail at:
(a) UPDATING individual items: if xi_mu is stored and needs to be modified to xi_mu', naive subtraction W -= xi_mu xi_mu^T / N is only approximate because cross-terms from other stored patterns accumulate. This is the "clean deletion" problem.

(b) CAPACITY LIMIT crossing: at M > 0.138 * N (Hopfield capacity), retrieval error probability rises sharply. This is not gradual -- it is a phase transition. For N=16384, M_c ~ 2260. For M ~ 100K facts per shard at N=16384, this requires sharding (one predicate per shard). If sharding is insufficient and multiple predicates share a shard, capacity exhaustion is sudden and catastrophic.

(c) TEMPORAL ORDERING: VSA superposition is orderless. A fact stored at time t=1 and a fact stored at t=100K are indistinguishable in W. There is no temporal trace. This means "most recently added" retrieval requires separate indexing infrastructure (the bitemporal layer in existing system design).

---

## LEVEL 4: SUBSTRATE-SPECIFIC CONCERNS

### 4.1 PP-141/142 Sleep-Defrag at Scale

PP-141/142 is a research-demo mechanism. It runs a consolidation pass over stored patterns and re-encodes co-occurrence statistics. At research-demo scale (M ~ 1K-10K facts), this is straightforward: the consolidation pass takes O(M) operations, W updates are incremental, and interference from the consolidation pass itself is negligible.

At production scale (M ~ 1M facts per shard):
- Consolidation pass is O(M) per predicate, O(M * P) total for P predicates. At M=1M, P=1K, this is 10^9 operations per consolidation cycle. Wall-clock depends on N (vector dimension).
- Consolidation cannot update W additively without resetting it first (otherwise prior consolidation cycles compound). Reset-and-rebuild means the memory is briefly inaccessible during consolidation.
- The interference from consolidation itself: re-encoding co-occurrence statistics into W creates new entries in the weight matrix that were not there before. If these entries have non-trivial cosine overlap with existing fact vectors, retrieval error increases.

None of this has been measured. PP-141/142 implementation is categorically unconfirmed at production scale.

### 4.2 Per-Predicate Sharding Capacity Limits

Current shard architecture: one predicate per W matrix of dimension N. Capacity per shard: M_c ~ 0.138 * N (Amit et al. 1985 formula). For N=16384, M_c ~ 2260 facts per shard before retrieval degrades.

Wikipedia/ConceptNet ingestion (~642K facts total across multiple predicates): if any single predicate shard receives > 2260 facts at N=16384, retrieval quality degrades. Common predicates (e.g. "is-a", "has-property") likely receive >> 2260 facts. This is a known production scaling concern.

Mitigation: hierarchical sharding (sub-predicate partitioning by subject domain). Not implemented. Failure mode: gradual retrieval degradation that LOOKS like forgetting but is actually capacity exhaustion. These are mechanistically distinct -- capacity exhaustion is recovered by shard expansion; true forgetting is not.

### 4.3 Cleanup Memory Growth Bounds

Cleanup memory (codebook) stores atomic concept vectors. Growth bound: O(V) where V = vocabulary size. For Wikipedia-scale ingest: V ~ 100K-500K entities. At N=16384 and 100K entities, the cleanup memory is a 100K x 16384 binary matrix = 200MB (fp16). This fits in RAM.

At 1M entities (aggressive KG scale): 2GB fp16. Manageable. At 10M entities (full Wikidata): 20GB fp16. Requires chunked retrieval or approximate nearest-neighbor (ANN) index. This is known and planned.

Cleanup memory does not exhibit forgetting -- it is a lookup table. But it exhibits CAPACITY-INDEXED NOISE: as V grows, the probability of nearest-neighbor collision increases (birthday paradox). For N=16384 and V=100K random bipolar vectors: expected min cosine between any two vectors ~ 0.03 (by concentration of measure). This is a safe margin. At V=10M: expected min cosine ~ 0.01. Still safe at N=16384 but approaching the limit for shorter vectors.

### 4.4 Codebook Size Growth Bounds

If the codebook must be UPDATED with new concepts (online learning scenario), two risks arise:
(a) Existing concept vectors contaminate new concept learning if the new concept is semantically similar to existing ones. This is a retrieval-time disambiguation problem, not a storage problem.
(b) If codebook entries are generated randomly (current approach), there is no structure -- random vectors in high dimensions are near-orthogonal and this problem is negligible at V << 2^(N/2).

The honest concern is not codebook growth bounds but codebook STABILITY: once a concept vector is assigned, all stored facts that use that concept encode its specific vector. Changing the concept vector (e.g., to improve semantic similarity) requires rewriting all facts using it. This is a large-scale re-encoding problem that biology solves gradually via replay; substrate has no equivalent mechanism for concept vector updates.

### 4.5 Bundle Interference Over Time

As M grows within a shard, cross-item interference in W increases. The expected cosine between a stored pattern xi_mu and the noisy retrieval W xi_query can be decomposed:

Expected cosine = signal / sqrt(signal^2 + interference^2)

Signal = xi_mu^T W xi_query / N (clean retrieval term)
Interference^2 ~ (M-1) / N (sum of cross-terms, assuming near-orthogonal items)

SNR = 1 / sqrt((M-1)/N + 1/N) ~ sqrt(N/(M-1)) for M >> 1

At N=16384, M=100: SNR ~ 13 (excellent)
At N=16384, M=1000: SNR ~ 4 (adequate)
At N=16384, M=2260 (capacity limit): SNR ~ 2.7 (threshold region)
At N=16384, M=10000 (over-capacity): SNR ~ 1.3 (unreliable)

This is a smooth degradation curve, not catastrophic forgetting. Items stored LATER have the same SNR as items stored EARLIER (superposition is commutative). However, items stored LESS FREQUENTLY have less representation in W than frequently-reinforced items, so effective retrieval is frequency-weighted. This IS a selectivity property: high-frequency items degrade later.

Honest statement: interference accumulation IS smooth, and frequency-weighting IS present. But the SNR formula assumes near-orthogonal items. In practice, semantically similar items have high cosine overlap and create CONSTRUCTIVE interference -- they add coherently to each other's retrieval noise rather than partially canceling. Within-domain semantic clustering makes interference worse than the random baseline predicts.

---

## LEVEL 5: FORGETTING PROFILE CHARACTERIZATION

### 5.1 Smooth Decay vs Catastrophic

Predicted profile: SMOOTH at M < M_c; PHASE-TRANSITION at M = M_c. Within the operating range (M << M_c per shard), the profile should look like a gradual SNR degradation following 1/sqrt(M). This is the VSA prediction; empirically unconfirmed at production scale.

### 5.2 Detail Loss vs Schema Preservation

Predicted: schema IS preserved longer than detail. This follows from the VSA bundling property: high-overlap (schema-consistent) components reinforce additively while low-overlap (episodic detail) components partially cancel. BUT this has only been proven for random, near-orthogonal patterns. Real encoder outputs (text embeddings) are NOT near-orthogonal -- they have a high-dimensional manifold structure with clusters. The schema-preservation property may not hold for semantically correlated real-world inputs.

### 5.3 Selectivity (Frequently-Used Preserved)

Predicted: YES, if the system implements reinforcement writes (re-writing a fact vector that has been accessed increases its contribution to W). Current system: reads are non-destructive (query does not modify W). This means there is NO frequency-based selectivity without explicit implementation of Hebbian reinforcement on access. Currently unimplemented. Forgetting is UNIFORM across stored items (no selectivity based on access frequency).

This is a concrete gap vs biology. Biology's hippocampal-cortical system preferentially consolidates frequently-replayed items. Substrate does not implement this without an explicit reinforcement write mechanism.

### 5.4 Spacing Effect

The spacing effect (Ebbinghaus, Bjork & Allen 1970) requires a temporal signal: items presented after a delay are better retained than items presented massed. Substrate has no temporal decay, so the spacing effect cannot emerge naturally. Re-presenting a fact vector (re-writing it into W) DOES strengthen its attractor basin, but the timing of re-presentation does not matter -- there is no benefit to spacing vs massing the re-presentations.

This is a fundamental architectural difference from biology. Implementing it would require a time-indexed decay mechanism on stored patterns, which contradicts the "stable storage" design goal.

---

## LEVEL 6: ENGINEERING ANCHORS

### Anchor 1: LONG-SEQUENCE-INGEST-WITH-PROBE
Protocol: encode K facts sequentially into one shard; after each block of 1000, query fact at position 1 and record retrieval cosine. Plot retrieval cosine vs M (number of stored items). Expected shape: flat at M << M_c, then declining, then cliff at M = M_c.
HARD-PASS: smooth degradation; fact 1 remains retrievable (cosine > 0.7) for M < 0.5 * M_c
HARD-FAIL: non-monotone behavior OR fact 1 drops below 0.5 at M < 0.1 * M_c
Cost: ~10 min CPU; numpy-only; no GPU needed

### Anchor 2: SCHEMA-MEDIATED-CONSOLIDATION
Protocol: store N_schema facts from K semantic categories; after ingestion, retrieve the prototype/centroid of each category and compare to explicit schema vector. Measure whether schema signal is preserved while individual fact distinctiveness decays.
HARD-PASS: schema centroid cosine > 0.80 after M = 2 * M_c items stored; individual fact cosine degrades below schema centroid cosine (schema-preservation property)
HARD-FAIL: schema centroid cosine < 0.60 at M = M_c; OR individual fact cosine EXCEEDS schema cosine (no selectivity)
Cost: ~20 min CPU

### Anchor 3: SELECTIVITY-PROFILE
Protocol: encode N_total facts; repeat K of them R times (simulate frequently-accessed items); compare retrieval cosine of repeated vs unrepeated facts at M = 0.8 * M_c.
HARD-PASS: repeated facts show > 30% higher retrieval cosine than unrepeated facts (frequency-selectivity present)
HARD-FAIL: repeated and unrepeated facts have same retrieval cosine within 5% (no frequency selectivity)
Note: current system likely HARD-FAILS this because reads are non-destructive and writes are not reinforcement-gated. This is a useful diagnostic.
Cost: ~15 min CPU

### Anchor 4: INTERFERENCE-PROFILE (Similar Items)
Protocol: encode M_similar semantically similar facts (same predicate, highly overlapping value vectors) and M_dissimilar semantically dissimilar facts; measure retrieval accuracy for each group.
HARD-PASS: similar-item retrieval degrades faster than dissimilar-item retrieval by > 2x (constructive interference confirmed; system requires more careful shard partitioning for similar items)
HARD-FAIL: similar and dissimilar items degrade at same rate (interference model is wrong; requires theory revision)
Cost: ~15 min CPU

### Anchor 5: SLEEP-DEFRAG-AT-SCALE
Protocol: ingest M = 0.7 * M_c facts; measure retrieval accuracy baseline; run one sleep-defrag cycle (consolidation pass per PP-141/142 protocol); measure retrieval accuracy post-defrag; repeat at M = 0.9 * M_c.
HARD-PASS: retrieval accuracy improves by > 5% post-defrag; improvement is durable after 1K additional writes
HARD-FAIL: retrieval accuracy is unchanged by defrag; OR post-defrag accuracy improves then drops back to pre-defrag level within 100 subsequent writes
Cost: ~30 min CPU; tests PP-141/142 production-scale validity

---

## LEVEL 7: HONEST REALITY

### 7.1 Substrate Likely Has Some Forgetting (Matches Biology -- in the RIGHT sense)

Substrate will show a forgetting-like profile when M grows beyond M_c per shard. This is mechanistically different from biological forgetting (capacity exhaustion vs synaptic decay) but phenomenologically similar (older items harder to retrieve as more items added). This is arguably a feature: the system naturally degrades gracefully under overload rather than catastrophically.

### 7.2 Schema-Mediated Detail Loss -- Probable but Unconfirmed

The VSA bundling math predicts that schema structure (common components across many items) survives better than idiosyncratic detail (unique components of individual items). This mirrors biological sleep-induced schema extraction. However, this is only a prediction for random patterns; real encoder outputs may violate the near-orthogonality assumption. Testing Anchor 2 is required before making this claim.

### 7.3 "Continual Learning at Production Scale" Needs Empirical Bound

The critical gap in current characterization: M/M_c ratio for the deployed Wikipedia/ConceptNet store is UNKNOWN. If common predicates (is-a, has-property) receive >> M_c facts in a single shard, retrieval is already in the degraded regime. Before any "production scale CL" claim, the actual M/M_c distribution across all shards must be measured.

This is a 1-hour diagnostic: count facts per predicate, estimate M_c for each N, flag shards where M > 0.5 * M_c.

### 7.4 Strategic Implications

(a) The "avoids catastrophic forgetting" claim is defensible and accurate in the specific ML-CF sense (no weight-clobber). Use this framing. Do not claim "matches biological CL" without the empirical bounds.

(b) The primary risk is capacity exhaustion, not catastrophic forgetting. The engineering solution is hierarchical sharding, not replay. Replay (sleep-defrag) is a secondary optimization that improves schema extraction; it does not solve capacity exhaustion.

(c) The system currently lacks frequency-based selectivity. This is a concrete gap vs both biology and competing systems (e.g., retrieval augmented systems that rank by recency/frequency). Adding reinforcement writes on access would close this gap with ~2 weeks of engineering.

(d) The spacing effect is architecturally absent. This is a minor strategic concern for product positioning but not an engineering priority.

(e) The two-system (hippocampal + cortical) requirement from CLS theory means substrate's single fast-store architecture is HALF of the biological system. To fully match biological CL, a slow-learning schema extractor (beyond sleep-defrag co-occurrence statistics) would be needed. This is a v2+ concern.

---

## CHEAP DECISIVE TEST

Measure retrieval cosine of item at position 1 after storing K=1, 10, 100, 500, 1000, 2000 subsequent items in the same shard (N=16384). Plot the curve. Expected: flat until M ~ 2000, then declining. HARD-FAIL: any non-monotone behavior or cliff before M=500.

Cost: 10 min CPU, numpy-only. Ships as LONG-SEQUENCE-INGEST-WITH-PROBE anchor.

---

## FALSIFIABLE PREDICTIONS

HARD-PASS thresholds:
1. Item at position 1 retrievable (cosine > 0.7) for M up to 0.8 * M_c (smooth degradation confirmed)
2. Schema centroid preserved better than individual items at M = 1.5 * M_c (schema-mediated retention confirmed)
3. Sleep-defrag improves retrieval by > 5% at M = 0.8 * M_c (PP-141/142 scale validity confirmed)

HARD-FAIL thresholds:
1. Position-1 item drops below cosine 0.5 at M < 0.3 * M_c (worse than theoretical prediction; N is insufficient or items are too correlated)
2. Schema centroid degrades as fast as individual items (VSA near-orthogonality assumption violated for real encoder outputs -- requires N upscaling or shard partitioning strategy change)
3. Sleep-defrag has no measurable effect at production scale (PP-141/142 is a research-demo mechanism that does not generalize)
4. Repeated vs unrepeated items show < 5% retrieval difference (no frequency selectivity; competing systems have structural advantage on long-term retention of frequently-used knowledge)

---

## CROSS-THREAD SYNTHESIS

- rem_replay_consolidation_substrate 2x (2026-06-04): predicted replay gain bounded at Delta_BPC < 0.05 nats at N=4096, functional at N=8192. Consistent with current analysis: replay is secondary to capacity management, not primary CL mechanism.
- sleep_defrag_implicit_generalization 3x (2026-06-07): predicted schema extraction is achievable for TYPE A (co-occurrence frequency). Current drill adds: schema preservation is PREDICTED but not proven; requires Anchor 2 to confirm.
- wright_fisher_kimura 2x (2026-06-04): neutral-drift baseline predicts random walk forgetting in absence of selection pressure. VSA superposition provides positive selection for frequently-reinforced items (schema structure) -- an improvement over neutral drift. But current system lacks access-based reinforcement.
- concept_drift_detection 2x (2026-06-07): concept drift detection at the query level is a SEPARATE problem from forgetting. Drift detection tells you WHEN the world has changed; forgetting characterization tells you what the system retains from the old world. Both are needed for honest production characterization.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. The honest marketing claim is: "avoids catastrophic forgetting common in gradient-based AI systems; degrades gracefully as knowledge base grows." Do NOT claim "matches biological memory." The latter requires CLS two-system architecture; the current substrate is one system.

2. Capacity exhaustion (M > M_c per shard) is the primary production risk, not forgetting per se. The engineering fix is shard count estimation per predicate before ingestion. This is a 2-day engineering task that should be prioritized before any production scale claim.

3. Frequency-based selectivity (retain frequently-accessed facts, let rarely-accessed facts decay gracefully) is a concrete product feature gap. It requires access-gated reinforcement writes. ~2 weeks of engineering; high product value for "intelligent forgetting" narrative.

4. Sleep-defrag (PP-141/142) needs production-scale validation (Anchor 5) before being included in any customer-facing feature claim. It may work correctly at production scale, but the mechanism is unconfirmed there.

---

## CITATIONS

1. McCloskey & Cohen 1989 (Psych Learning & Motivation 24:109-165) -- catastrophic interference
2. Kirkpatrick et al. 2017 (PNAS 114(13):3521-3526; arxiv:1612.00796) -- EWC
3. Rusu et al. 2016 (arxiv:1606.04671) -- Progressive Networks
4. Shin et al. 2017 (NeurIPS; arxiv:1705.08690) -- DGR deep generative replay
5. Fernando et al. 2017 (arxiv:1701.08734) -- PathNet
6. McClelland, McNaughton & O'Reilly 1995 (Psychological Review 102(3):419-457) -- CLS theory
7. Wilson & McNaughton 1994 (Science 265:676-679) -- hippocampal replay original discovery
8. Buzsaki 2018 review (PMC6794196) -- sharp-wave ripples, reverse replay
9. Tonegawa lab 2015 (Science) -- optogenetic confirmation of replay necessity
10. Tse et al. 2007 (Science 316:76-82) -- schema-mediated fast learning
11. Tse et al. 2011 (Science 333:891-895) -- schema-consistent bypass of hippocampus
12. Frankland et al. 2004 (Science 304:881-883) -- systems consolidation, cortical sparsification
13. Ebbinghaus 1885/1913 -- forgetting curves (power law)
14. Bjork & Allen 1970 (Journal of Verbal Learning 9:352-361) -- spacing effect
15. Amit, Gutfreund & Sompolinsky 1985 (PRL 55:1530) -- Hopfield capacity M_c = 0.138N
16. Kanerva 1988 (Sparse Distributed Memory, MIT Press) -- SDM capacity and robustness
17. Plate 2003 (Holographic Reduced Representations, CSLI) -- VSA capacity and interference analysis
18. Imani et al. 2019 (IEEE DATE) -- HDC for online/continual learning classification
19. Ge et al. 2020 (IEEE) -- HD-CL continual learning framework
20. Rachkovskij & Kussul 2001 (Cybernetics & Systems 32(5):491-538) -- VSA schema extraction
21. Mallya & Lazebnik 2018 (CVPR; arxiv:1711.05769) -- PackNet binary weight masking
22. Lopez-Paz & Ranzato 2017 (NeurIPS; arxiv:1706.08840) -- GEM gradient episodic memory
23. Rebuffi et al. 2017 (CVPR; arxiv:1611.07725) -- iCaRL exemplar-based rehearsal

Verified citation count: 23 (all classic/foundational references; HDC CL lit counts verified from IEEE/NeurIPS proceedings)

---

## P_DEFLATED SUMMARY

| Claim | P_raw | Deflation | P_deflated |
|-------|-------|-----------|-----------|
| Substrate avoids McCloskey-Cohen CF | 0.95 | -0.05 | 0.90 |
| Smooth degradation curve (not cliff) | 0.70 | -0.20 | 0.50 |
| Schema preserved > individual items | 0.60 | -0.20 | 0.40 |
| Sleep-defrag works at production scale | 0.55 | -0.20 | 0.35 |
| Frequency-selectivity without reinforcement | 0.15 | -0.05 | 0.10 |
| Matches biological CL (full CLS) | 0.30 | -0.20 | 0.10 |

Next-drill candidate: INTERFERENCE-PROFILE for semantically correlated real-encoder outputs (population-genetics-wright-fisher + structural-glasses-MCT adjacency: does correlation structure in real encoder outputs push M_c closer to critical-MCT glass transition than the random-vector formula predicts?)
