# Research Drill: Real-Time Multi-Modal Integration -- Biology and Substrate Paths
Date: 2026-06-09
Drill level: 3x (biological mechanisms + predictive coding + engineering anchors)
Filed by: research sub-agent

---

## HEADLINE

Biology solves real-time multi-modal integration through a cascade of four interacting mechanisms: (1) early subcortical binding in the superior colliculus (~50ms, nonlinear audiovisual summation), (2) hierarchical predictive coding in cortex (Rao-Ballard + Friston free energy, top-down predictions suppress bottom-up errors), (3) continuous-parameter representation via theta-phase coding and attractor dynamics (place/grid cells as biological fractional-power encoders), and (4) cerebellar forward models as fast sub-cortical predictors that compensate for afferent delays. Each of these four mechanisms has a concrete algebraic analog in FHRR-based discrete-binding substrate, suggesting that the gap between substrate's discrete bindings and biology's continuous-time integration is bridgeable without exotic operations -- it requires fractional-power binding rotations, hierarchical prediction-error propagation, and a fast lookup layer functioning as a cerebellar forward model.

P_deflated (overall): 0.38 (deflated 0.20 from raw estimate; novel synthesis capped at 0.50)

---

## HARD-PASS / HARD-FAIL thresholds (pre-registered)

HARD-PASS on engineering anchors:
- PREDICTIVE-SUBSTRATE-1: prediction accuracy > chance on next fact given context sequence, measured on held-out temporal chains; specifically p_correct > 0.60 on k=5 step lookahead
- CONTINUOUS-BINDING-FHRR-ROTATIONS: cosine similarity decay < 0.1 per 10-degree rotation step; decoding MSE < 0.05 over 100 continuous-parameter steps
- CROSS-MODAL-CONSISTENCY: contradiction detection precision > 0.80, recall > 0.70 on held-out conflicting (vision, audio) fact pairs
- HTM-IN-SUBSTRATE: anomaly score AUC > 0.75 on temporal sequence disruptions vs baseline
- FORWARD-MODEL-CEREBELLUM: latency < 1ms for prediction lookup on N=1024 substrate; < 5ms for N=65k

HARD-FAIL:
- PREDICTIVE-SUBSTRATE-1: p_correct <= 0.35 (at chance; prediction encoding adds no information)
- CONTINUOUS-BINDING-FHRR-ROTATIONS: cosine similarity below 0.5 at 100 continuous steps (rotations decorrelate before useful range)
- CROSS-MODAL-CONSISTENCY: precision < 0.55 (worse than majority-class baseline)
- FORWARD-MODEL-CEREBELLUM: latency > 50ms (negates the purpose of a fast forward model)

---

## Level 1: Biological Real-Time Multi-Modal Integration

### 1.1 Superior Colliculus: First Integration Gate (~50ms)

The superior colliculus (SC) is the earliest site of audiovisual integration in the mammalian brain. 2025 recordings of 5000+ neurons in awake mice (Nat. Commun. 2025, PMC12575753) show:

- Multisensory neurons receive approximately half their local input from other multisensory neurons -- a specialized recurrent subnetwork, not a simple feedforward sum
- Integration is nonlinear: superadditive when auditory-precedes-visual, subadditive when visual-precedes-auditory -- consistent with natural propagation statistics of light vs sound
- Posterior-medial SC populations specialize in temporal discriminability of audiovisual delays
- Temporal binding window in SC: approximately 50-100ms effective window; neurons with distinct preferred delays tile this range

Mechanistic model: the SC implements a nonlinear weighting function W(delta_t) where delta_t is the audiovisual stimulus onset asynchrony. The weight function is asymmetric around delta_t=0, reflecting a Bayesian prior that light arrives before sound for distant events. This is NOT a simple temporal coincidence detector -- it is a prior-weighted integration kernel.

Computational implication: the SC does not require a global clock. It implements local coincidence detection with recurrent amplification. This suggests the minimal temporal binding mechanism is a recurrent subnetwork with asymmetric delay kernels.

### 1.2 MST/V5: Motion + Form Integration

Area MST (medial superior temporal, part of MT+ complex) integrates optic flow (from V5/MT) with heading signals from vestibular input. MST neurons have large receptive fields and respond to complex motion patterns including rotation, expansion, and contraction. Key property: MST implements a reference-frame transform from retinal coordinates to body-centered coordinates via gain modulation -- the same computation posterior parietal cortex uses for full multimodal binding.

### 1.3 Posterior Parietal Cortex: Cross-Modal Reference Frames

The PPC (areas VIP, LIP, MSTd) integrates visual, vestibular, auditory, and somatosensory signals into a body-centered representation. Critically, it does NOT use a single global reference frame -- different subregions (PIVC, MSTd, VIP) use frames intermediate between head-centered, eye-centered, and body-centered. This graduated frame progression is computationally equivalent to a chain of affine transforms applied sequentially, each stage resolving one degree of freedom.

2024 bioRxiv work (biorxiv 2024.11.25.625309) shows this can be implemented by additive feed-forward networks -- no recurrence required for the reference-frame transforms themselves. The recurrence serves temporal prediction, not spatial binding.

### 1.4 Cross-Modal Plasticity

When one sensory modality is deprived (blindness, deafness), cortical areas normally dedicated to that modality are recruited for remaining modalities with enhanced performance. This demonstrates that multi-modal integration is fundamentally allocatable -- the binding is not hardwired to specific cortical loci but is implemented in a flexible distributed computation. For engineering: modality-specific encoders feeding a shared binding layer (rather than modality-specific retrieval stacks) is the biologically supported design.

### 1.5 Predictive Coding Across Modalities

Friston's Free Energy Principle (Friston 2009, PMC2666703) extends Rao-Ballard hierarchical predictive coding to all sensory modalities. The message-passing scheme is:
- Error units receive inputs from states in the same level and the level above (bottom-up prediction errors)
- State units are driven by error units in the same level and the level below (top-down predictions)
- Superficial pyramidal cells carry prediction errors forward; deep pyramidal cells carry predictions backward

The key insight: cross-modal binding happens by sharing a common higher-level generative model. If vision predicts "dog approaching" and audio predicts "barking," both predictions derive from the same top-level cause representation. Binding is not a separate operation -- it emerges from joint free energy minimization over a shared generative model.

Mathematical form: Free energy F = sum_l E_pred(l) + E_complexity(l), where E_pred(l) is prediction error at level l (weighted by precision), and E_complexity penalizes model complexity. Cross-modal binding minimizes total F across the joint hierarchy.

### 1.6 Temporal Binding via Neural Synchrony

The neural synchrony hypothesis (Engel, Singer, Uhlhaas) proposes that cross-modal binding is implemented by phase-locked oscillations in gamma (30-80 Hz) and beta (12-30 Hz) bands. The effective temporal binding window -- approximately 50-200ms -- corresponds to the period of the oscillation (gamma: ~15-33ms; beta: ~33-80ms). Objects are "bound" when their neural representations fire in synchrony across areas.

However, synchrony is now understood as one of multiple mechanisms, not the unique solution. SC's recurrent integration does not require global synchrony. Synchrony may be downstream readout mechanism rather than the binding operation itself.

### 1.7 Active Inference for Action Selection

In active inference (Friston's extension of predictive coding), the agent selects actions to minimize expected free energy -- the expected prediction error under future states. The agent does not respond to current prediction error; it preemptively acts to steer sensory input toward expected outcomes. This is a mathematically clean formulation of goal-directed behavior: expected precision-weighted prediction error minimization over a finite planning horizon.

Implementation: at each time step, the agent simulates K candidate actions, computes expected free energy for each, and selects the action with lowest expected future surprise. This naturally handles uncertainty (high entropy future states are avoided).

### 1.8 Temporal Binding Window: 50-200ms

The psychophysical temporal binding window for audiovisual events is approximately 50-200ms (Vatakis and Spence 2007; van Wassenhove et al. 2007). Factors affecting the window:
- Familiarity: known AV pairs (speech) bind more easily than unfamiliar pairs
- Causal expectation: events with high prior probability of co-occurring bind more readily
- Spatial congruence: spatially co-located stimuli have wider binding windows
- Unisensory reliability: less reliable modalities weight toward the more reliable one (Bayesian causal inference model, Shams and Beierholm 2010)

The Bayesian causal inference model (BCIM) explains temporal binding windows as a Bayesian posterior over two hypotheses: same-cause (one event) vs different-cause (two events). When P(same-cause | delta_t) exceeds threshold, binding occurs.

---

## Level 2: Causal Video Understanding -- Biology

### 2.1 V5/MT: Motion Processing

Area MT (V5) contains direction-selective neurons that respond to motion with approximately 30-50ms latency after V1 response. MT neurons receive direct projections from LGN (M-pathway), bypassing V1, enabling fast motion detection independent of form processing. This dual-route architecture (fast subcortical + slower cortical) is biology's solution to the latency-vs-accuracy tradeoff.

### 2.2 Causal Perception (Michotte)

Michotte (1946) demonstrated that humans perceive causation directly from motion patterns -- a moving ball contacting a stationary one causes a percept of "launching" even in pure geometric displays. This is not inferred; it is perceived at latencies consistent with fast visual processing (~150ms). Neural correlates: posterior STS (superior temporal sulcus) responds to apparent causal interactions over pure motion sequences (Keysers et al. 2010, Fugelsang et al. 2005).

The key computational property: causal perception requires detecting contingent change -- object B moves only after object A contacts it. This is a conditional temporal derivative: d_B/dt is nonzero conditional on contact event at t_contact. The brain implements this as a difference-of-forward-models: if the actual trajectory of B matches the prediction of a forward model conditioned on the contact event, causation is inferred.

### 2.3 Counterfactual Reasoning in Development

Infants as young as 10-12 months distinguish causal from non-causal events (Spelke 1994; Leslie and Keeble 1987). This suggests causal perception is not learned from extensive experience but emerges from core object knowledge plus a forward-model that predicts object trajectories. The counterfactual test (would B have moved if A had not contacted it?) is implemented implicitly, not explicitly.

### 2.4 Predictive Coding for Video

Predictive coding applied to video sequences: higher visual areas predict the next frame given current context. Prediction error signals in V1/V2 respond strongly to unexpected motion. fMRI studies show anterior temporal cortex represents abstract event structure ("what is happening") while posterior visual cortex represents specific frame-level predictions. The hierarchy naturally separates temporal scales: slow abstract dynamics at the top, fast pixel-level dynamics at the bottom.

### 2.5 Hierarchical Temporal Memory (Hawkins, Numenta)

HTM formalizes the neocortex as a sequence memory system. Core architectural features:
- Sparse Distributed Representations (SDRs): ~2% active bits at any time, high-dimensional (~2048 bit)
- Sequence memory via column-level dendritic prediction: a cell fires in "predicted" state when its dendritic segment matches context from previous timestep
- Online continual learning via Hebbian-like synapse updates (no separate training phase)
- Temporal pooling: higher levels fire only when lower-level patterns persist, automatically extracting slower dynamics

Key property for substrate: HTM does not require a global clock or explicit time-step counter. Time is implicit in the sequence of active SDRs. Prediction of the next SDR is the model's function.

### 2.6 Forward Models in Motor Cortex (Wolpert)

Wolpert's MOSAIC model (Modular Selection And Identification for Control, 1998) proposes a set of paired forward + inverse models. Each forward model predicts sensory consequences of an action; responsibility signals weight each forward model's contribution based on recent prediction accuracy. The system learns which forward model applies to the current context by tracking prediction errors.

MOSAIC is directly applicable to multi-modal integration: a forward model for "visual object falling" predicts both visual trajectory AND expected impact sound. The multi-modal prediction is checked against observation; mismatch generates prediction error that triggers model selection or model update.

### 2.7 Cerebellar Prediction

The cerebellum (PMC6671847) predicts the timing and magnitude of sensory events, not just motor commands. Lobule VII crus I activates specifically when a temporal-spatial model is required for perceptual prediction. The cerebellum-putamen-cortex loop serves as the brain's fast forward model for both motor and perceptual prediction.

Key quantitative fact: cerebellar prediction latency is approximately 10-20ms (Miall and Wolpert 1996; Wolpert 1997), compared to 150-200ms for cortical feedback loops. This ~10x speed advantage is why the cerebellum can compensate for afferent delays in motor control. For engineering: a fast lookup layer (sub-ms retrieval) can serve the same function.

### 2.8 Optical Flow and Temporal Derivatives

Optical flow algorithms (Lucas-Kanade, Horn-Schunck) compute instantaneous velocity fields from consecutive frames. Biology computes a sparser but more efficient version via direction-selective cells in MT. The biological computation prioritizes boundaries and objects over background, consistent with attention gating. Dense optical flow is not computed -- sparse event-driven flow (similar to neuromorphic event cameras) is biologically plausible.

---

## Level 3: Predictive Coding Architecture

### 3.1 Rao-Ballard Hierarchical Predictive Coding

Rao and Ballard (1999, Nature Neuroscience) proposed the foundational hierarchical predictive coding model for visual cortex. Architecture:
- Each cortical level maintains an estimate of causes (r) and a prediction error signal (e)
- Feedforward connections carry prediction errors (e = input - prediction)
- Feedback connections carry top-down predictions
- Learning updates generative model weights to minimize prediction error energy

The model predicts end-stopping (V1 responses to line ends), extra-classical receptive field suppression (V1 response reduced when context is predictable), and mismatch negativity (MMN; auditory ERP to deviant sounds). All three have been experimentally confirmed.

### 3.2 Friston Free Energy Principle

Friston's extension (2009, 2010) places Rao-Ballard in a variational Bayesian framework. Free energy F is an upper bound on log-surprise (negative log-evidence): F >= -log P(observation | model). Minimizing F is equivalent to maximizing model evidence -- i.e., the brain acts as an approximate Bayesian inference engine.

The generative model has the form: P(x, psi) = P(x | psi) P(psi), where x is sensory data and psi are hidden causes. Prediction error is the precision-weighted residual: epsilon = precision * (x - g(psi)), where g is the generative mapping.

Critically for multi-modal integration: each modality has its own precision weight. If one modality is unreliable (noisy visual input in darkness), its precision is low and the other modality dominates the joint estimate. This is optimal Bayesian combination, implemented via precision-weighted prediction errors.

### 3.3 Active Inference + Action

In active inference, actions minimize expected free energy G over future time steps:
G = sum_tau [ KL[Q(o_tau | pi) || P(o_tau)] + H[Q(o_tau | pi)] ]

The first term penalizes divergence from preferred observations (goal-seeking); the second term penalizes entropy (uncertainty reduction). Actions that both achieve goals AND reduce uncertainty are preferred. This gives a principled treatment of exploration vs exploitation without ad-hoc reward shaping.

### 3.4 Prediction Error Minimization vs Coding Efficiency

Two interpretations of predictive coding coexist:
(a) Efficient coding (Barlow): remove redundancy; send only surprise
(b) Bayesian inference (Friston): compute posterior via variational inference

These are mathematically equivalent in the linear Gaussian case but diverge in nonlinear regimes. For substrate engineering, interpretation (a) is operationally cleaner: encode only events that deviate from prediction; store the prediction implicitly.

---

## Level 4: Continuous-Time Bindings

### 4.1-4.3 Place Cells, Grid Cells, Theta Phase

Place cells (hippocampus) fire at specific spatial locations; grid cells (entorhinal cortex) fire in hexagonal lattices. The key computational property: these are biological implementations of continuous-parameter binding.

Continuous attractor network (CAN) model: a persistent "bump" of activity in a recurrently connected sheet represents current position continuously. As the animal moves, the bump translates via asymmetric connections that read out velocity. Mathematical representation: population activity vector z(t) traces a smooth trajectory in high-dimensional state space; the "position" is read out by projection onto a codebook of reference vectors.

This is directly analogous to FHRR fractional power encoding (FPE): position (x,y) encoded as V_x * V_X^x * V_Y^y, where V_X, V_Y are base phasors. Continuous movement is a smooth rotation of the phase vector. Decoding via cosine similarity to codebook recovers continuous coordinates with MSE ~ 0.17/100 steps (Grid-Cell-VSA, arXiv 2503.08608).

### 4.3 Theta Phase Coding

Theta phase precession (O'Keefe and Recce 1993): as an animal traverses a place field, the place cell fires progressively earlier phases of the 8 Hz theta oscillation. This compresses the spatial sequence (~250ms traverse) into one theta cycle (~125ms), achieving approximately 2x temporal compression. Across multiple place cells, the sequence within one theta cycle encodes a "virtual trajectory" from past through present to future location.

This is a biological implementation of temporal compression for predictive look-ahead: each theta cycle is a compressed simulation of the upcoming trajectory. The compression ratio is approximately 10-20x relative to real-time traversal (Dragoi and Tonegawa 2013).

### 4.5 Hippocampal Time Cells

Time cells (Macdonald et al. 2011; Howard and Eichenbaum 2013) fire at specific times within a delay interval, with sequential activation spanning the interval. A set of ~100 time cells can represent a 10-second interval with approximately 100ms resolution. This provides the neural substrate for "what happened when" representations needed for causal reasoning.

Time cells are mathematically equivalent to a delay-line register: the "time since event X" is represented as a population vector that evolves continuously across the cell assembly. Decoding via template matching recovers time-since-event continuously.

### 4.6 Cerebellar Internal Clock

The cerebellum implements interval timing via climbing fiber and parallel fiber interactions. Purkinje cells learn to suppress their resting inhibitory output at a trained interval after a conditioned stimulus, enabling precise temporal discrimination in the ~100ms-10s range. The cerebellar clock is NOT a dedicated timer -- it is a learned forward model that predicts when outcomes occur.

### 4.7 FHRR Rotations as Continuous Binding

FHRR's component-wise complex multiplication is phase addition: if V = r * exp(i*theta), then V^t = r * exp(i*theta*t). Continuous time t maps to continuous phase rotation. A temporal sequence (t=0, 1, 2, ...) is a sequence of uniformly spaced phasors. A query for "event at time t" is decoding via cosine similarity between the query phasor and the stored bundle.

Key property from arXiv 2503.08608: locality is preserved -- nearby phasors have high cosine similarity -- enabling approximate temporal lookup without exact match. This makes continuous-time binding algebraically tractable in FHRR without any new primitives.

---

## Level 5: Hallucination Detection in Multi-Modal Systems

### 5.1 Cross-Modal Consistency Check

When vision reports "person A speaking" and audio reports "voice of person B," the prediction error from the shared-cause hypothesis (same person) is large. The brain resolves this via the Bayesian causal inference model: high P(different cause) triggers perceptual decoupling (visual and auditory percepts processed separately). This is why ventriloquism and the McGurk effect work: causal inference is manipulated by spatial and temporal statistics.

Cross-modal inconsistency is computable as: Inconsistency(v, a) = ||phi(v) - phi_hat(a)||_2, where phi(v) is the visual embedding and phi_hat(a) is the predicted visual embedding given the audio embedding. High inconsistency signals mismatch.

### 5.2 Prediction-Error Spike as Hallucination Signal

The P300 ERP (P3b) and Mismatch Negativity (MMN) are large-amplitude brain potentials (~5-20 uV) that occur approximately 300ms and 150ms post-stimulus respectively when sensory input violates predictions. These are neural correlates of "surprise." Crucially, MMN occurs even without attention (the subject can be engaged in another task), suggesting automatic hallucination/inconsistency detection at the cortical level.

Computationally: MMN-like detection is implemented by a maintained predictive model. When the current input has low probability under the model, a large prediction-error signal is generated. This signal can trigger model update (learning) or alert (behavioral relevance response).

### 5.3 Hippocampal Novelty Detection

The hippocampus (CA1 region) implements sequence completion: given a partial context, CA1 pattern-completes to the stored episode. When the observed continuation violates the completed pattern, a mismatch signal is generated (Kumaran and Maguire 2006, PMC1661685). Recent 2025 work (PNAS 2025, doi:10.1073/pnas.2503535122) confirms hippocampal mismatch signals are tied to episodic memories specifically -- they fire when the CURRENT episode deviates from the STORED episode, not from schema.

For multi-modal hallucination: if modality A activates an episodic memory that predicts modality B should show X, but modality B shows Y, the hippocampus fires a mismatch signal. This is the biological analog of a cross-modal consistency check.

### 5.4 Top-Down Validation

Higher-level areas (prefrontal cortex, anterior cingulate) generate top-down predictions that gate lower-level activity. When a top-down prediction is consistent with sensory input, bottom-up activity is suppressed (explaining repetition suppression in fMRI). When inconsistent, the area "releases" bottom-up processing, effectively flagging the inconsistency for further processing. This is a two-pass validation: fast bottom-up sweep followed by top-down gating.

### 5.5 Algebraic Consistency Check via Substrate

Substrate's existing contradiction-detection (PP-180 extension) can be extended to cross-modal: if modality-A binding and modality-B binding are stored in the same substrate, and the binding of their cross-modal prediction (A predicts B) is also stored, then consistency check is:
cos_sim(stored_prediction(A->B), actual_B_binding) > threshold_consistent

This is a dot-product query on the existing substrate with no new primitives. The algebraic property that makes this work: in FHRR, the prediction A->B is encoded as V_A * V_AB_relation, and actual B is V_B. Cosine similarity of the two is cos(angle(V_A * V_AB_relation, V_B)). If the relation is correct, this should be near 1. If A and B are inconsistent (different causes), this will be near 0 or random.

---

## Level 6-7: Engineering Paths -- Ranked Anchors

The following 8 anchors are ranked by (a) mechanistic support from biology, (b) implementation difficulty on existing substrate, (c) product-relevant capability unlocked.

### Anchor 1 (HIGHEST): CROSS-MODAL-CONSISTENCY (PP-180 extended)

Mechanism: hippocampal mismatch + cross-modal Bayesian causal inference
Biology support: HIGH (PNAS 2025, PMC1661685, Shams & Beierholm 2010)
Implementation: extend PP-180 contradiction check to cross-modal pairs; requires two modal embeddings + a cross-modal relation binding; pure algebraic dot-product
P_deflated: 0.45 (strong biological analog; algebraically clean; no new primitives needed)
Product capability: multi-modal hallucination detection, cross-source fact verification

### Anchor 2: PREDICTIVE-SUBSTRATE-1 (substrate predicts next fact)

Mechanism: HTM sequence memory + cerebellar forward model
Biology support: HIGH (Hawkins/Numenta HTM; Wolpert MOSAIC; cerebellar timing PMC6671847)
Implementation: store (context, next_fact) bindings in substrate; query by context to retrieve predicted next fact; prediction error = distance(predicted, observed)
P_deflated: 0.38 (requires sequential encoding protocol not currently in substrate; manageable extension)
Product capability: temporal fact chains, predictive retrieval, sequence completion

### Anchor 3: CONTINUOUS-BINDING-FHRR-ROTATIONS

Mechanism: grid cell / place cell continuous attractor + FHRR FPE
Biology support: HIGH (O'Keefe/Recce theta precession; arXiv 2503.08608 grid-cell-VSA)
Implementation: encode continuous parameters (time, position, temperature) via fractional phasor rotation V^t; decode via codebook cosine lookup; proven MSE 0.17/100 steps
P_deflated: 0.42 (directly supported by published FHRR FPE; no biological gap; engineering is incremental)
Product capability: continuous temporal indexing, time-since-event queries, smooth interpolation

### Anchor 4: FORWARD-MODEL-CEREBELLUM (fast prediction lookup)

Mechanism: cerebellar forward model + Wolpert MOSAIC
Biology support: HIGH (PMC6671847; Wolpert 1997)
Implementation: a "fast lane" substrate query that returns the predicted next state given current state; implemented as a second codebook of (state, predicted_next_state) pairs; lookup is sub-ms at existing N
P_deflated: 0.40 (implementation is a codebook addition; key question is whether prediction accuracy is useful vs naive baseline)
Product capability: low-latency state prediction; causal chain reasoning without LLM call

### Anchor 5: ACTIVE-INFERENCE-LLM-VERIFIER

Mechanism: active inference hypothesis-then-verify loop (Friston 2010)
Biology support: MEDIUM (active inference is well-specified; LLM-as-oracle is novel composition)
Implementation: substrate generates N candidate "next cause" hypotheses via bounded search; LLM assigns probability to each; loop selects hypothesis with lowest expected free energy; iterate
P_deflated: 0.28 (biology supports the loop; but LLM-in-loop adds latency inconsistent with real-time goal; product niche unclear; HARD-FAIL if loop requires > 3 LLM calls for convergence)
Product capability: hypothesis-driven reasoning; active question answering

### Anchor 6: HIERARCHICAL-TEMPORAL-MEMORY (HTM-in-substrate)

Mechanism: Hawkins HTM sparse distributed representations + temporal pooling
Biology support: MEDIUM (HTM is biologically motivated; direct substrate implementation has no precedent)
Implementation: represent sequences as stacked substrate bindings at multiple timescales; fast layer (1-5 steps ahead), slow layer (10-50 steps ahead); prediction error propagates upward
P_deflated: 0.30 (HTM principles are sound; mapping to FHRR algebra requires non-trivial engineering; HTM's SDR sparsity constraint (2% active) may conflict with FHRR dense phasors)
Product capability: multi-scale temporal reasoning; slow + fast dynamics

### Anchor 7: REAL-TIME-VIDEO-SUBSTRATE (event-driven binding)

Mechanism: MT direction-selective cells + sparse optical flow + SC temporal binding
Biology support: MEDIUM (biology is well-characterized; substrate encoding of video frames is novel)
Implementation: encode video frames as temporal sequence of FHRR phasors; motion is encoded as fractional rotation between frames; causal events are detected as sharp rotation discontinuities
P_deflated: 0.22 (major gap: current substrate assumes static discrete facts; video encoding at 30fps requires 30 bindings/second with temporal indexing; feasibility unclear at scale)
Product capability: causal video understanding; event detection from video streams
HARD-FAIL criterion: if throughput < 5fps at N=1024, route to separate architecture

### Anchor 8: NOVELTY-DETECTION (prediction-error spike)

Mechanism: hippocampal mismatch + MMN cortical surprise
Biology support: HIGH (PMC1661685; PNAS 2025; ERP literature is extensive)
Implementation: each query returns a prediction-confidence score; low-confidence queries (novel inputs) trigger an alert signal; implemented as distance from nearest codebook vector
P_deflated: 0.45 (algebraically trivial; distance-to-nearest-neighbor IS prediction error; already partially implemented in similarity search; extension is metadata flagging)
Product capability: anomaly detection, out-of-distribution flagging, surprise-triggered attention

---

## Level 8: Theoretical Considerations

### 8.1 Biology's Parallelism vs Substrate's Sequential Access

Biology integrates 5+ modalities in ~100ms via massive parallelism: ~86 billion neurons, each computing simultaneously. Substrate's PTIME operations are sequential in the classical sense but can be sharded. The key architectural constraint is not computational complexity but memory bandwidth: each modality lookup is an independent dot-product operation, so multi-modal fusion is embarrassingly parallel if shards are assigned per modality.

Sharding prescription: assign one substrate shard per modality (vision, audio, text, sensor). Each shard computes its own similarity score in parallel. Fusion is a weighted sum of scores (precision-weighted per Friston). This is the architectural analog of SC's multisensory subnetworks.

### 8.2 Predictive Coding Compression Ratio

Predictive coding is an efficient code when the world is predictable. If the next fact in a chain has P(correct prediction) = 0.8, the information content of the prediction is 0.32 bits; storing the full fact costs log2(|vocab|) bits. For a vocabulary of 10^6 facts, full storage costs ~20 bits; prediction costs 0.32 bits. Compression ratio ~60x for predictable chains.

For substrate: storing prediction (context -> next_fact_binding) and only transmitting prediction errors reduces the effective storage requirement for temporal chains by a factor equal to the compression ratio. This is the biological motivation for PREDICTIVE-SUBSTRATE-1.

### 8.3 Causality Requires Forward Models (Pearl)

Pearl's causal hierarchy (association, intervention, counterfactual) requires level-3 (counterfactual) reasoning to answer "would Y have happened if X had not occurred." Biology implements this via forward models: simulate the counterfactual trajectory by running the forward model without the intervention event. The causal judgment is the comparison between the two simulated outcomes.

Substrate analog: causal query = query for (context_without_event, predicted_outcome) vs (context_with_event, predicted_outcome). If the predicted outcomes differ, the event is causal. This requires storing forward-model predictions separately for the two contexts -- a novel but algebraically tractable extension.

### 8.4 Continuous vs Discrete: the Core Gap

Substrate's current bindings are discrete: each fact is a distinct hypervector. Biology's continuous-attractor representation is continuous: position is a bump of activity that can take any value in a manifold. The gap is bridged by FHRR FPE (fractional power encoding), which maps continuous parameters to phasor rotations. The remaining gap is in INTERPOLATION: substrate can lookup the nearest stored vector, but cannot naturally interpolate between stored vectors unless the FPE protocol is used consistently.

Prescription: for any continuous parameter (time, position, intensity), use FPE encoding at write time. This ensures that the stored hypervectors form a smooth manifold in the high-dimensional space, enabling approximate continuous-parameter queries.

---

## Level 9: Engineering Anchor Summary (Ranked)

Rank 1: CROSS-MODAL-CONSISTENCY -- P_deflated=0.45, LOW engineering effort (PP-180 extension), HIGH product value (hallucination detection)
Rank 2: NOVELTY-DETECTION -- P_deflated=0.45, MINIMAL effort (distance-to-nearest already exists), HIGH product value (anomaly flagging)
Rank 3: CONTINUOUS-BINDING-FHRR-ROTATIONS -- P_deflated=0.42, MEDIUM effort (new encoding protocol), HIGH capability value (continuous temporal indexing)
Rank 4: FORWARD-MODEL-CEREBELLUM -- P_deflated=0.40, MEDIUM effort (codebook extension), MEDIUM product value (fast state prediction)
Rank 5: PREDICTIVE-SUBSTRATE-1 -- P_deflated=0.38, MEDIUM-HIGH effort (sequential encoding protocol), HIGH capability value (fact chain prediction)
Rank 6: HTM-IN-SUBSTRATE -- P_deflated=0.30, HIGH effort (SDR-to-FHRR mapping), MEDIUM value (multi-scale temporal)
Rank 7: ACTIVE-INFERENCE-LLM-VERIFIER -- P_deflated=0.28, HIGH effort (inference loop), UNCLEAR value (LLM latency conflicts with real-time)
Rank 8: REAL-TIME-VIDEO-SUBSTRATE -- P_deflated=0.22, VERY HIGH effort (streaming binding architecture), DEFERRED until scale validated

Cheap decisive test (lowest-cost gate): implement NOVELTY-DETECTION (Anchor 8, rank 2) as a 1-hour CPU experiment measuring prediction-error-as-distance on held-out temporal sequences. If AUC > 0.75, the prediction-error mechanism is working. This gates PREDICTIVE-SUBSTRATE-1 and indirectly validates the hierarchical predictive coding path.

---

## Cross-Thread Synthesis

Prior research (evening brief 2026-06-07, memory): substrate has sub-ms retrieval, whitening + pseudoinverse universal, bf16 N=65k validated, LoRA hurts retrieval. The multi-modal integration work builds directly on these:
- Sub-ms retrieval = cerebellar forward model speed is already met
- Pseudoinverse universal = the reference-frame transforms in PPC (linear maps) are computable via pseudoinverse
- Whitening = isotropic representations in the query space ensure the precision-weighting in Friston's formulation is well-conditioned
- LoRA-hurts-retrieval aligns with biology: the retrieval operation (hippocampal pattern completion) should NOT be further regularized; low-rank approximations degrade the binding fidelity

Prior ZKL research: the encoder isotropy issue identified in ZKL drilling is DIRECTLY relevant to multi-modal integration. If encoder outputs are anisotropic (cone-clustered), then precision-weighted fusion will be miscalibrated because modalities along the cone axis will be over-weighted. The SRHT/mean-centering fixes for ZKL serve double duty as fixes for multi-modal integration calibration.

Tier-5c LLM results (EXP-DEV brief 2026-06-09): multi-layer substrate-attention improves perplexity +15-20% on Pythia/Qwen. This is consistent with the predictive coding view: the substrate layer is functioning as a top-down prediction generator that reduces the LLM's effective prediction burden (lower perplexity = better prediction = free energy minimization). The substrate-as-predictive-prior interpretation has direct biological support in this drill.

---

## Substrate-Product Implications

1. Hallucination detection is achievable as a pure substrate operation (no LLM call). CROSS-MODAL-CONSISTENCY (Anchor 1) + NOVELTY-DETECTION (Anchor 8) together give a two-tier consistency check: algebraic inconsistency (fast, < 1ms) + prediction-error spike (requires stored predictions, ~1-5ms). This is a differentiating product feature relative to pure LLM RAG.

2. Temporal fact chains are an underexploited product surface. Biology encodes "this happened, then that happened" in place cell / time cell sequences. Substrate currently retrieves facts without temporal ordering. PREDICTIVE-SUBSTRATE-1 + CONTINUOUS-BINDING-FHRR-ROTATIONS together would enable temporal fact queries ("what was true 3 minutes ago given current context").

3. Multi-modal fusion (vision + text + structured data) is architecturally simple given substrate's existing algebra. Each modality gets its own embedding; cross-modal prediction bindings are stored; fusion is precision-weighted dot products. No new inference machinery needed.

4. The LLM-in-the-loop architecture is validated biologically: LLM is the prefrontal cortex (slow, high-level), substrate is the hippocampus + SC + cerebellum (fast, pattern completion, forward modeling). The current architecture (substrate hypothesizes, LLM verifies) maps correctly onto active inference with LLM as the top of the hierarchy.

---

## Citations (verified count: 22)

1. Rao RP, Ballard DH (1999). Predictive coding in the visual cortex: a functional interpretation of some extra-classical receptive-field effects. Nature Neuroscience 2(1):79-87.
2. Friston K (2009). Predictive coding under the free-energy principle. Phil Trans R Soc B 364(1521):1211-1221. PMC2666703.
3. Friston K (2010). The free-energy principle: a unified brain theory? Nature Reviews Neuroscience 11:127-138.
4. PMC12575753 / Nat Commun 2025: Functional specialisation of multisensory temporal integration in the mouse superior colliculus.
5. Wolpert DM, Miall RC (1996). Forward models for physiological motor control. Neural Networks 9(8):1265-1279.
6. Wolpert DM, Kawato M (1998). Multiple paired forward and inverse models for motor control. Neural Networks 11(7-8):1317-1329.
7. PMC6671847: The cerebellum predicts the timing of perceptual events. J Neurosci 2019.
8. PMC6517560: Neural evidence of the cerebellum as a state predictor.
9. O'Keefe J, Recce ML (1993). Phase relationship between hippocampal place units and the EEG theta rhythm. Hippocampus 3(3):317-330.
10. Dragoi G, Tonegawa S (2013). Development of schemas revealed by prior experience and NMDA receptor knock-out. eLife 2:e01326.
11. PMC10208522: Learning to predict future locations with internally generated theta sequences.
12. Macdonald CJ et al. (2011). Hippocampal "time cells" bridge the gap in memory for discontiguous events. Neuron 71(4):737-749.
13. Kumaran D, Maguire EA (2006). An unexpected sequence of events: mismatch detection in the human hippocampus. PLOS Biology 4(12):e424. PMC1661685.
14. PNAS 2025 doi:10.1073/pnas.2503535122: Hippocampal mismatch signals are based on episodic memories.
15. Shams L, Beierholm UR (2010). Causal inference in perception. Trends in Cognitive Sciences 14(9):425-432.
16. Michotte A (1946/1963). The Perception of Causality. Basic Books (translated edition 1963).
17. Hawkins J, Ahmad S (2016). Why neurons have thousands of synapses: a theory of sequence memory in neocortex. Frontiers in Neural Circuits 10:23.
18. arXiv 2503.08608: A Grid Cell-Inspired Structured Vector Algebra for Cognitive Maps.
19. arXiv 2604.25939: qFHRR: Rethinking Fourier Holographic Reduced Representations through Quantized Phase and Integer Arithmetic.
20. Plate TA (1995). Holographic reduced representations. IEEE Trans Neural Netw 6(3):623-641.
21. bioRxiv 2024.11.25.625309: Multisensory integration across reference frames with additive feed-forward networks.
22. arXiv 2512.01924: Real-World Robot Control by Deep Active Inference With a Temporally Hierarchical World Model.

---

## Next-drill candidate

Field: continuous-attractor-network-dynamics (adjacent to existing place-cell/grid-cell line)
Specific angle: Theta phase precession as temporal compression codec -- can FHRR reproduce the 10-20x compression ratio seen in hippocampal theta sequences without explicit oscillator?
Rationale: CONTINUOUS-BINDING-FHRR-ROTATIONS (Anchor 3) gates on this; if the compression is algebraically achievable, this becomes the cheapest path to continuous temporal indexing.
