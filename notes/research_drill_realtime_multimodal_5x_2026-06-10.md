# Research Drill: Real-Time Multimodal Architecture for Substrate
# Date: 2026-06-10
# Streams: A (Biology), B (Brain), C (Architecture), D (Physics), E (LLM), F (Synthesis)
# Calibration: P estimates deflated 0.15-0.25; novel-synthesis cap 0.50

---

## HEADLINE

Cross-modal binding at mixed rates (video 30Hz, audio 44.1kHz, sensorimotor 1kHz) is
solvable substrate-natively by a PER-MODALITY-SUBSTRATE + ASYNC-EVENT-DRIVEN binding
architecture; the strongest convergent signal across all five streams is that temporal
alignment belongs in the binding layer not the per-modality encoding layer, and that
a phase/timing residual vector is the cheapest cross-modal currency.

P_deflated = 0.32 (novel substrate synthesis; cap applied)

---

## STREAM A -- Biology findings

### A1. Multisensory integration (Stein-Meredith superadditivity)
The Stein-Meredith principle: multisensory neurons in the superior colliculus show
NONLINEAR superadditivity -- the response to A+V exceeds the sum of A and V alone,
but only when stimuli are spatially and temporally aligned. The inverse effectiveness
rule: superadditivity is largest when unimodal responses are weakest. This has a
direct algebraic reading: the binding signal is a NONLINEAR FUNCTION of the inputs,
not a weighted sum. Linear binding (bundling) is provably insufficient for the
superadditivity property.

2025 finding (Nature Communications, PMC12575753): Superior colliculus neurons encode
audiovisual delays through nonlinear integration, with nonlinearities more pronounced
when visual precedes auditory -- consistent with natural light-versus-sound propagation
statistics. The posterior-medial SC population (peripheral field) specializes in delay
encoding; the central field population specializes in superadditivity. This functional
SPECIALIZATION BY SUBPOPULATION is a substrate-native design cue: not all binding
neurons do the same thing; spatially-separate subpopulations encode different aspects
of cross-modal alignment.

Substrate implication: A single global binding vector is biologically unrealistic and
computationally wasteful. Separate binding populations for (a) spatial coincidence and
(b) temporal delay estimation are a better model.

### A2. Cocktail party effect (selective attention)
Selective attention resolves the binding problem by weighting one source over others.
The auditory system uses spatial cues (interaural time difference, ITD -- microsecond
resolution) and spectral cues simultaneously. The binding problem is NOT solved by
ignoring the unattended stream -- it is solved by SUPPRESSING its binding weight while
retaining the ability to re-bind rapidly on salience change. This is mathematically
a soft-assignment problem, not hard gating.

### A3. McGurk effect (visual-audio dominance switching)
The McGurk effect demonstrates that visual (lip movement) can override auditory (heard
phoneme) in cross-modal integration. The brain applies a CONFIDENCE-WEIGHTED PRIOR:
when visual and auditory conflict, the system does not average them -- it picks the
higher-reliability modality and projects the lower one onto it. The reliability
weighting is context-dependent (noisy auditory = trust visual more). This is Bayesian
causal inference (see B10, F6) in operation.

### A5-A6. Bat/cetacean echolocation + motor integration
The bat superior colliculus shows sensorimotor integration across three rate-mismatched
streams: sonar emission (active output, ~10-20 pulses/s during cruising), echo
reception (passive input, each echo ~2ms return window), and wing motor control (~8
wingbeats/s). These rates differ by 100x. The solution: each stream has its own update
loop, and cross-stream binding happens at the BEHAVIORAL DECISION LAYER, not at the
sensory representation layer. The bat does not try to upsample wing position to the
sonar rate. Binding occurs at the decision (motor command) time scale, which is the
SLOWEST of the three.

Key finding from bat literature: a 2.4ms acoustic waveform can be compressed to a
16-value distributed vector (0.15 samples/ms) without losing target-discrimination
capability. This is a direct existence proof that a substrate-like compressed vector
can represent a high-rate acoustic stream at retrieval-quality fidelity.

### A7-A10. Other biological multimodal systems
Mantis shrimp 12-color vision: each chromatic channel is processed in PARALLEL with
separate photoreceptor populations; there is no cross-color binding at the retina --
binding happens downstream when behavioral decisions are made. Octopus distributed
cognition: ~2/3 of neurons are in the arms; each arm has local processing at ~1kHz
sensorimotor rate, but the central brain receives compressed summary vectors not raw
streams. Honeybee 5-sense integration operates at ~100ms behavioral decision timescale
even though sensory inputs arrive at diverse rates.

Convergent biological principle: HIGH-RATE STREAMS ARE COMPRESSED LOCALLY; cross-modal
binding happens at the lowest-common rate of the behavioral decision loop.

---

## STREAM B -- Brain findings

### B1. Superior colliculus topographic multimodal maps
The SC maintains topographic maps of visual, auditory, and somatosensory space in
REGISTERED LAYERS. The registration is spatial: neurons in different layers that respond
to the same location in space are anatomically aligned. This gives a substrate design
principle: spatial index acts as the cross-modal binding key. Two modalities bind if
their spatial address vectors (or position indices) are sufficiently aligned.

### B4. Gamma oscillations and cross-modal binding
Gamma oscillations (30-90Hz) serve as a temporal synchronization carrier for cross-modal
binding. The mechanism: when two neural populations representing different modalities
need to bind, they phase-lock their gamma oscillations. The phase relationship matters:
binding is strongest when the oscillations are 0 or 180 degrees apart (constructive or
anti-phase). Phase-locking is NOT instantaneous -- it has a convergence time on the
order of 50-200ms for cross-area synchronization.

From Neuron literature: gamma synchronization across visual and somatosensory cortex
increases during visual-tactile matching tasks. From ResearchGate (2016, replicated):
visual working memory binding shows phase differences in the gamma band between temporal
and parietal cortex with a ~180 degree relationship.

Substrate implication: A phase variable (scalar angle) can serve as the binding token
between per-modality substrate states. Two modalities that share a phase register are
bound; phase mismatch indicates segregation. This is mathematically equivalent to
a COMPLEX-VALUED binding operation where the binding weight is e^{i*theta}.

### B3. Thalamus relay gating
The thalamus does NOT merely relay sensory signals -- it gates them. The thalamic reticular
nucleus (TRN) applies INHIBITORY CONTROL to thalamocortical relay, effectively functioning
as a router that selects which modality gets priority at any moment. This is a substrate
design principle: a gating vector that controls which modality's updates propagate to
the binding layer, with gate weights that are dynamically set by salience/prediction error.

### B10. Predictive coding hierarchies
In the Rao-Ballard predictive coding framework, each layer sends a PREDICTION down to
the layer below, and receives PREDICTION ERROR up from the layer below. In multimodal
contexts (2024 Nature Communications paper on crossmodal predictions): the integration
layer where two streams are linked sends separate prediction signals DOWN each unimodal
stream. The audio stream predicts upcoming visual events and vice versa.

Mathematical structure: if h_A is the auditory state vector and h_V is the visual state
vector, the crossmodal predictive coding step is:

  err_A = x_A - f_A(h_A, h_V)   [auditory prediction error, informed by visual state]
  err_V = x_V - f_V(h_V, h_A)   [visual prediction error, informed by auditory state]
  h_A += alpha * err_A
  h_V += alpha * err_V

This is a CROSS-STATE UPDATE RULE where each modality's update depends on both its own
prediction error AND the other modality's current state. The substrate analog: a
per-modality update step that includes a cross-modal term.

### B6. Cerebellum sensorimotor integration
The cerebellum integrates sensory (proprioceptive, vestibular, visual) with motor
commands at ~1kHz. Its key computational principle: INTERNAL FORWARD MODEL that predicts
the sensory consequences of motor commands. The prediction is subtracted from incoming
sensory data; only the residual (unexpected sensory signal) gets forwarded upstream.
This massively reduces the effective data rate from 1kHz to the rate of unexpected events.

Substrate implication: sensorimotor binding at 1kHz does not require 1kHz updates to
the substrate state vector -- it requires a FORWARD MODEL that produces expected sensory
vectors, and only when prediction error exceeds threshold does the substrate state update.
This is identical to the async/event-driven architecture principle.

---

## STREAM C -- Architecture findings

### C1. Per-modality substrate + cross-substrate binding
Each modality gets its own substrate state vector S_k (k = audio, video, sensorimotor).
Each S_k is updated at its modality's native rate. A BINDING SUBSTRATE B is updated at
a slower, unified rate and receives contributions from all S_k.

  S_A[t] = update_A(S_A[t-1], x_A[t])      # audio at 44.1kHz
  S_V[t] = update_V(S_V[t-1], x_V[t])      # video at 30Hz
  S_M[t] = update_M(S_M[t-1], x_M[t])      # motor at 1kHz
  B[t]   = bind(S_A[t], S_V[t], S_M[t])    # at decision timescale (~30Hz or slower)

The bind() operation is the critical unknown. Candidates:
  (i) Vector sum (bundling): B = S_A + S_V + S_M. Cheap; loses per-modality identity.
  (ii) Binding by role vector: B = S_A * r_A + S_V * r_V + S_M * r_M where r_k are
       fixed role hypervectors. Recovers individual modalities via: S_k_approx = B * r_k.
  (iii) Learned attention gate: B = sum_k g_k(S_A, S_V, S_M) * S_k. Expensive but flexible.

Option (ii) is the substrate-native path. It is the HDC/VSA binding-by-role operation,
and it preserves per-modality decodability from the binding vector.

### C2. Asynchronous substrate updates (each modality own rate)
Each modality's local substrate runs at its native rate INDEPENDENTLY. There is no global
clock. The binding layer polls each modality's substrate at its own (slow) rate.

Key mathematical property: if S_k has its own exponential decay S_k[t] = (1-lambda_k)
S_k[t-1] + lambda_k f(x_k[t]), then S_k maintains a running summary of recent activity
even between binding polls. The decay rate lambda_k controls the effective temporal
window. For audio at 44.1kHz with lambda_A = 0.001, the substrate integrates ~1000
samples (~22ms window) between each binding poll at 30Hz.

### C3. Kuramoto oscillator binding
The Kuramoto model: dtheta_k/dt = omega_k + (K/N) sum_j sin(theta_j - theta_k). When
coupling K exceeds a critical value K_c = 2/pi * g(0) (where g is the natural frequency
distribution), the system undergoes a phase transition from incoherence to partial
synchrony. The synchronized cluster has a common effective frequency.

For cross-modal binding: assign each modality a natural frequency omega_k proportional
to its update rate (omega_A large for audio, omega_V small for video). When two modalities
carry information about the same event, their binding weight increases (K increases
locally), driving phase locking. The phase-locked state = bound; incoherence = unbound.

2024 finding (arxiv 2410.13821 -- Artificial Kuramoto Oscillatory Neurons, ICLR 2025):
Kuramoto dynamics introduced into deep learning as a binding mechanism for object
discovery, adversarial robustness, and reasoning. The Kuramoto update naturally
incorporates spatiotemporal traveling waves, for which there is ample neuroscientific
evidence. This is a PEER-REVIEWED existence proof that Kuramoto oscillators can serve
as a trainable binding mechanism in neural networks.

Math: For substrate use, each modality k gets a phase phi_k and a magnitude A_k.
The bound representation is:

  B = sum_k A_k * exp(i * phi_k) * S_k   [complex-valued bundling]

When phi_k are phase-locked (equal or fixed offset), the binding is constructive.
When phi_k are incoherent, destructive interference in the real part reduces B's
similarity to any individual S_k.

### C4. Predictive cross-modal substrate loop
Each modality's substrate predicts the next state of OTHER modalities. The residual
(actual - predicted) drives the binding update. This is the substrate analog of
predictive coding (B10) and the cerebellum forward model (B6).

  pred_V_from_A = W_AV * S_A[t]   [predict visual state from audio]
  err_V = S_V[t] - pred_V_from_A
  B[t] = B[t-1] + alpha * err_V   [binding updates on cross-modal surprise]

This has a key property: when audio and video are strongly correlated (e.g., a clap),
the prediction is accurate, err_V is small, and the binding update is minimal -- the
binding is already established. When audio and video decouple (e.g., off-screen sound),
err_V is large, and the binding update is large -- forcing re-registration of modalities.

### C5. Compression hierarchy substrate
High-rate modalities (sensorimotor 1kHz, audio 44.1kHz) compress to lower-rate
representations before contributing to binding. The compression is LOSSY but
RATE-MATCHED: the compressed representation at rate R can be further compressed to
rate R' < R with additional loss.

Compression hierarchy:
  x_M[1kHz] -> compressed_M[100Hz] -> summary_M[30Hz]
  x_A[44.1kHz] -> compressed_A[4kHz] -> summary_A[30Hz]
  x_V[30Hz] -> summary_V[30Hz]   [no compression needed]
  B[30Hz] = bind(summary_M, summary_A, summary_V)

The compression function at each stage is the substrate's standard encoding: store
into the substrate and immediately retrieve to get the compressed representation.
This repurposes the substrate's existing encode-decode pipeline as a compression filter.

### C7. Event-driven substrate
Only update the substrate state when the input CHANGES significantly. Define a
threshold delta_k for each modality. If |x_k[t] - x_k[t-1]| < delta_k (measured in
cosine distance in the embedding space), skip the update.

This reduces the effective update rate from the modality's nominal rate to the rate
of significant events. For audio of a steady hum: near-zero effective update rate.
For a sudden sound onset: full update rate for a few cycles. This is biologically
validated by the retina (retinal ganglion cells respond to change, not static intensity)
and cochlea (onset detectors in the auditory nerve).

For sensorimotor at 1kHz: if the motor state changes slowly (steady grip), the event
rate may drop to ~10Hz, making it comparable to the video stream.

### C8. Spike-timing-dependent substrate
Encode cross-modal coincidences using a Hebbian-style update where the binding weight
between modality k and modality j increases when they co-activate within a temporal
window tau. The STDP window is asymmetric: if k precedes j by dt, increase W_kj;
if j precedes k by dt, decrease W_kj (or vice versa).

For substrate: the binding vector B accumulates cross-modal co-activation products:
  B[t] += S_A[t] * S_V[t-dt_AV]   [audio bound with recent visual, if dt_AV in window]

This requires tracking a TEMPORAL BUFFER of recent per-modality states, not just the
current state. Buffer size = tau / dt_step.

### C9. Reservoir substrate (echo state)
A reservoir (fixed, randomly connected recurrent network) with high spectral radius
(near 1.0) naturally stores a fading memory of past inputs. When multimodal inputs
are injected, the reservoir state is a nonlinear mixture of recent inputs across all
modalities. The binding is implicit in the reservoir dynamics.

2024 literature (Scientific Reports): echo state networks are state-of-the-art for
nonlinear dynamical system modeling. The reservoir's internal state evolves over time
and captures temporal dependencies. For multimodal use, each modality is injected
as a separate input channel; the reservoir mixes them passively.

Key property: the reservoir does NOT need to be updated -- it has no training. Only the
readout weights (linear layer on top of reservoir state) are trained. This makes the
binding "free" computationally; the cost is only in the readout.

Substrate analog: if the substrate's W matrix is treated as a fixed reservoir, the
substrate state after multiple retrieval iterations IS the reservoir state -- it has
echo properties if the spectral radius of W is near 1.

---

## STREAM D -- Physics findings

### D1. Coherent oscillators (Josephson junctions)
Josephson junction arrays exhibit phase locking between coupled superconducting loops.
The physics: each junction has a phase phi and voltage V proportional to dphi/dt.
When coupled, junctions phase-lock above a critical coupling strength. This is the
physical Kuramoto model. The mathematical structure is identical to the neural Kuramoto
oscillator (C3). The synchronization transition is sharp (second-order phase transition)
and the locked-phase state has well-defined algebraic properties.

Relevant for substrate: the Josephson physics confirms that oscillator-based binding
has a REAL PHYSICAL IMPLEMENTATION with known phase-transition behavior. The algebraic
structure (complex-valued order parameter, phase coherence, superadditivity at lock-in)
carries directly to the abstract binding problem.

### D8. Phase-locked loops (PLL)
A PLL tracks a reference signal's phase and locks onto it. The tracking dynamics follow
second-order linear differential equations with a lock-in range (frequency range within
which locking is possible) and a pull-in range (range within which the PLL will
eventually lock from any initial phase). Outside the lock-in range, the PLL slips cycles.

For substrate: PLL dynamics provide a model for how a binding oscillator tracks a
modality's intrinsic phase. If the phase difference between two modalities is within
the lock-in range, the binding oscillator locks; if not, it slips (no binding).

### D9. Coupled pendulum dynamics
Coupled pendulums synchronize via energy transfer through the coupling medium. The
synchronization manifold is stable when coupling strength exceeds a threshold. The
transient to synchronization has a known time constant tau_sync = 1 / (K - K_c) for
Kuramoto-class systems near the critical coupling K_c.

For real-time binding: tau_sync must be shorter than the event integration window.
If tau_sync >> 100ms, the binding is too slow for real-time cross-modal events.
Optimization: increase K (coupling strength) or reduce heterogeneity of natural
frequencies (make omega_k more uniform).

### D10. Kuramoto synchronization across scales
The Kuramoto model generalizes to hierarchical coupling: fast oscillators at the sensor
level, slow oscillators at the binding level. Each slow oscillator receives the mean
field of its fast oscillator group. This is the physics of mesoscopic synchronization
and directly maps to the compression hierarchy (C5) combined with oscillator binding (C3).

---

## STREAM E -- LLM multimodal findings

### E1. CLIP and contrastive alignment
CLIP learns a shared embedding space for image and text via contrastive training.
The binding mechanism is LATE FUSION: separate per-modality encoders, shared embedding
space enforced by contrastive loss. The mathematical operation at binding: cosine
similarity between image embedding e_I and text embedding e_T in the shared space.

Limitation: CLIP binds at the level of semantic meaning, not temporal coincidence.
It cannot natively bind audio-visual coincidences at 30Hz without architectural changes.

### E8. Late fusion vs early fusion
Late fusion: encode each modality separately, fuse at the decision layer. Preserves
modality-specific processing; binding is cheap but may miss low-level correlations.

Early fusion: concatenate raw or near-raw features before encoding. Finds low-level
correlations but loses modality-specific structure; does not scale to rate-mismatched
streams.

Mid-level (feature-level) fusion with cross-attention: the dominant architecture in
2024-2025 multimodal LLMs. Per-modality encoders produce feature vectors; cross-attention
layers allow each modality to query others. Computationally expensive at high rates.

For substrate: late fusion with role-vector binding (C1 option ii) is the computationally
cheapest path. Cross-attention is the most expressive but requires O(N_A * N_V) operations
per binding step, which at video+audio rates is expensive.

### E9. Cross-attention multimodal
Cross-attention: query from modality A, key/value from modality B. The attention weight
is softmax(Q_A * K_B^T / sqrt(d)), and the output is a weighted sum of V_B values.

For substrate: cross-attention is algebraically related to the substrate's retrieval
operation. The substrate retrieval S_query -> candidate_key -> value IS a form of
cross-attention where the substrate W matrix serves as the key-value store.

This means a CROSS-SUBSTRATE RETRIEVAL operation (query one modality's state against
another modality's substrate) is structurally a cross-attention step. The substrate
natively supports this if each modality has its own W matrix (per-modality substrate,
C1). Binding = cross-substrate retrieval.

### E5-E6. ViT video+audio, Whisper audio+text
Video transformers (ViT-based) process temporal sequences by treating video frames as
a sequence of patch tokens. Audio is typically processed as mel-spectrogram tokens.
Whisper processes audio via CNN+Transformer encoder and produces text alignments.

The common pattern: both video and audio are tokenized at a unified rate (video: one
token per frame or per patch-sequence; audio: one token per ~20ms window). The tokenization
IS the rate reduction step. After tokenization, both modalities operate at comparable rates.

Substrate analog: if each modality's substrate state is "read out" at a unified token
rate (e.g., 30Hz), the state vectors at that rate are the tokens, and standard cross-
modal binding can proceed.

---

## STREAM F -- Synthesis

### F1. Cross-stream convergence

Five convergent signals across all streams:

1. SEPARATE PER-MODALITY PROCESSING: All biological systems (A1-A10), all brain
   architectures (B1-B10), and dominant LLM architectures (E8, E9) use per-modality
   encoders/representations before binding. This is not incidental -- rate mismatch
   alone forces it. A single unified encoder at the highest rate (44.1kHz) is
   computationally untenable.

2. BINDING AT THE DECISION RATE, NOT THE SENSOR RATE: Bats bind across 100x rate
   mismatch (A6). SC neurons bind at behavioral timescales (A1). LLMs tokenize to a
   common rate (E5). The binding operation should run at the SLOWEST rate relevant to
   the downstream task.

3. NONLINEAR BINDING: SC superadditivity (A1), Bayesian causal inference (A3, B10),
   and Kuramoto phase-locking (C3, D1) are all nonlinear. Linear bundling (S_A + S_V)
   is provably insufficient for the superadditivity property. The binding function must
   be nonlinear.

4. PHASE/TIMING AS BINDING CURRENCY: Gamma oscillations (B4), Josephson junctions (D1),
   PLL dynamics (D8), Kuramoto oscillators (C3) all use a PHASE VARIABLE as the
   cross-modal binding key. This is a substrate-native operation: complex-valued
   substrate vectors already have a phase component (FHRR uses bipolar {-1,+1} which
   is a discretized phase).

5. EVENT-DRIVEN / PREDICTION-ERROR-DRIVEN UPDATES: Cerebellum forward model (B6),
   event-driven architecture (C7), retinal change detection (A3), and Bayesian causal
   inference (A3) all drive updates from PREDICTION ERROR, not raw signal. High-rate
   streams that are well-predicted require near-zero binding updates.

### F2. Ten substrate math systems (ranked by implementability)

#### F2.1 PER-MODALITY-SUBSTRATE + cross-substrate binding (HIGHEST PRIORITY)

Mechanism: Three substrate instances S_A, S_V, S_M, each updated at native rate.
A binding operation B = phi(S_A, S_V, S_M) runs at 30Hz (video rate, slowest modality
relevant to real-time interaction). phi is the VSA binding-by-role operation:
  B = S_A * r_A + S_V * r_V + S_M * r_M
where r_k are fixed random role hypervectors. Recovery: S_k_approx = B * r_k.

Why it works: each modality is independently updated at its native rate. The binding
step is cheap (3 vector additions). Per-modality decodability is maintained.

Mathematical gaps to close:
  (a) What is the capacity of the binding vector B when K=3 modalities are bound?
      VSA theory predicts capacity ~N/3 for random role vectors; empirical verification needed.
  (b) What is the retrieval accuracy of S_k_approx = B * r_k when S_k has its own
      noise/compression artifacts?
  (c) How does the binding quality degrade when S_k are temporally offset by delta_t?
      (i.e., if S_A and S_V are sampled at different moments within the 30Hz window)

P_deflated = 0.40 (well-grounded in HDC/VSA theory; substrate-native; cheap test)

HARD-PASS threshold: cross-modal recall@10 >= 0.80 when binding 3 modalities at
  N=10000 substrate dimensionality, with each modality contributing 1000 stored patterns.
HARD-FAIL threshold: cross-modal recall@10 < 0.50 after role-vector binding, OR
  binding vector capacity drops below N/10 (indicates role-vector interference is severe).

#### F2.2 KURAMOTO-OSCILLATOR-BINDING

Mechanism: Each modality k has a phase oscillator phi_k with natural frequency omega_k
and a magnitude A_k encoding the substrate state. Binding is the complex-valued inner
product of phase-coherent state vectors:
  B_real = sum_k A_k * cos(phi_k) * S_k
  B_imag = sum_k A_k * sin(phi_k) * S_k
  B = B_real + i * B_imag

Phase-locking dynamics:
  dphi_k/dt = omega_k + K * sum_j sin(phi_j - phi_k)

When K > K_c, the phases lock. In the locked state, the binding vector B has coherent
cross-modal contributions. In the unlocked state, the time-averaged B is dominated by
whichever modality has the largest A_k (not a true binding).

From 2024 ICLR paper (arxiv 2410.13821): Kuramoto neurons are trainable and used for
object discovery and reasoning. This confirms the gradient-flow properties are tractable.

Mathematical gaps:
  (a) K_c as a function of substrate dimension N and number of modalities K.
  (b) Lock-in transient time vs binding event duration (must be << event window).
  (c) Differentiability of the binding operation for gradient-based training.

P_deflated = 0.28 (more complex; trainable version needs implementation; good theory)

HARD-PASS: Phase lock achieved in < 5 substrate cycles for K=3 modalities; bound vector
  retrieval accuracy >= 0.75.
HARD-FAIL: Lock-in time > 100 substrate cycles for typical K=3 configurations.

#### F2.3 ASYNC-EVENT-DRIVEN-SUBSTRATE

Mechanism: Per-modality substrate with event-driven updates. Define threshold delta_k
(cosine distance). Update S_k[t] only when |x_k[t] - x_k[t-1]|_cos > delta_k.
Track the last update time T_k for each modality. The binding layer uses the most
recent available S_k for each modality, regardless of when it was last updated.

Key property: the effective binding rate is the rate of EVENTS, not the rate of samples.
For audio of silence: 0 updates. For a speech onset: burst of updates at ~1kHz for
the onset duration, then quiet.

Combined with F2.1 (per-modality substrate): async event-driven updates reduce
CPU cost by 10-100x for typical real-world signals (which are sparse in change).

Mathematical gaps:
  (a) Optimal delta_k per modality (too small = no saving; too large = missed events).
  (b) Effect on binding quality when S_k is "stale" (not updated for T steps).
  (c) How to handle multi-modality desynchronization when one modality has high event
      rate and another has low event rate.

P_deflated = 0.38 (engineering-tractable; event-driven SNNs already validated 2024)

HARD-PASS: 10x reduction in update operations vs synchronous at equivalent binding quality.
HARD-FAIL: Binding quality drops by > 0.15 in recall@10 vs synchronous baseline.

#### F2.4 PREDICTIVE-CROSS-MODAL-LOOP

Mechanism: Cross-modal prediction matrices W_AB (predict visual from audio), W_VA,
W_AM, etc. Each matrix is a small linear projection (d x d). The binding update is:
  err_V = S_V[t] - W_AV * S_A[t]   [visual prediction error from audio]
  B[t] = B[t-1] + alpha * (err_V * err_A)  [bind on joint surprise]

When audio and visual are correlated, err_V and err_A are small and the binding update
is small (binding is stable). When they decouple, errors are large and binding re-
registers (or dissolves, depending on sign of update).

The W_AB matrices are the "cross-modal prior." They can be initialized as random
projections (zero cross-modal prediction, so all co-occurrences drive binding updates)
or learned from data.

P_deflated = 0.30 (more complex; requires learning W_AB; biologically grounded via B10)

HARD-PASS: Binding quality on correlated A+V pairs >= 0.80 recall@10; on uncorrelated
  pairs binding dissolves (recall@10 < 0.30).
HARD-FAIL: Binding quality on correlated and uncorrelated pairs does not differ by > 0.15.

#### F2.5 COMPRESSION-HIERARCHY-SUBSTRATE

Mechanism: Multi-stage compression. Stage 1: encode raw x_k into S_k at native rate
(44.1kHz for audio). Stage 2: "read out" S_k at a lower rate by querying a summary
concept; the resulting vector is S_k_compressed at ~1kHz. Stage 3: query S_k_compressed
at 30Hz to get S_k_summary. Stage 4: bind S_k_summary across modalities at 30Hz.

The substrate's encode-then-retrieve pipeline is the compression function at each stage.
Each stage reduces dimensionality by approximately N/K where K is the number of stored
patterns.

P_deflated = 0.25 (requires multi-stage substrate; more complex; compression quality TBD)

HARD-PASS: Two-stage compression retains >= 0.75 recall@10 at 30x rate reduction.
HARD-FAIL: Two-stage compression drops recall@10 below 0.50 at 30x rate reduction.

#### F2.6 BAYESIAN-MULTIMODAL-SUBSTRATE

Mechanism: Bayesian causal inference model in substrate space. The binding variable C
(common cause / same event) has a prior P(C=1) = p_c. Given S_A and S_V, the
posterior is:
  P(C=1 | S_A, S_V) proportional to p_c * p(S_A | C=1) * p(S_V | C=1)
  P(C=0 | S_A, S_V) proportional to (1-p_c) * p(S_A | C=0) * p(S_V | C=0)

In the substrate, p(S_A | C=1) is proportional to exp(sim(S_A, S_canonical_A) / T)
where S_canonical_A is the substrate's current audio representation of the hypothesized
event, and T is temperature. The bound vector is:
  B = P(C=1 | S_A, S_V) * (S_A + S_V) + P(C=0 | S_A, S_V) * 0
    = w_bind * (S_A + S_V)

where w_bind is the binding weight. This is a probabilistic version of the bilinear
binding operation.

P_deflated = 0.22 (requires probability estimation in substrate space; complex; grounded)

HARD-PASS: Binding weight w_bind >= 0.8 for correlated A+V; w_bind <= 0.2 for uncorrelated.
HARD-FAIL: No discrimination (w_bind is approximately constant across correlated/uncorrelated).

#### F2.7 SPIKE-TIMING-SUBSTRATE

Mechanism: Temporal buffer of recent substrate states for each modality. Buffer depth
tau / dt_step. The binding update is triggered by cross-modal coincidence: if S_A[t]
and S_V[t - delta_t] have high cosine similarity for some delta_t in [0, tau], a
binding update occurs. The binding matrix W_bind is incremented by:
  W_bind += eta * S_A[t] outer_product S_V[t - delta_t]

This is an outer product (Hebbian) binding, structurally identical to STDP learning.

Mathematical challenge: the outer product matrix W_bind grows as N x N. For N=10000
this is 10^8 entries -- too large. Alternative: use only the compressed summary vectors
(N=1000 after compression) and compute a 1000x1000 binding matrix (10^6 entries,
tractable).

P_deflated = 0.22 (memory-expensive; temporal buffer adds complexity)

HARD-PASS: Binding matrix retrieves correct cross-modal pairs with recall@10 >= 0.75.
HARD-FAIL: Memory requirement exceeds practical budget (> 1GB for N=10000, K=3).

#### F2.8 RESERVOIR-SUBSTRATE-ECHO

Mechanism: Use the substrate's W matrix as a reservoir (fixed, not learned). The
spectral radius rho(W) determines the fading memory duration. For multimodal input,
inject all modalities into the reservoir simultaneously (scaled by their current event
salience). The reservoir state r[t] = tanh(W * r[t-1] + U_A * x_A[t] + U_V * x_V[t]
+ U_M * x_M[t]).

Only the readout weights (V^T * r[t]) need to be trained. The binding is implicit in
the reservoir mixing.

Connection to existing substrate: if the substrate W has spectral radius near 1, it
IS a reservoir. The substrate's iterative retrieval loop IS a reservoir computation.

P_deflated = 0.28 (repurposes existing substrate W; elegant; readout training needed)

HARD-PASS: Reservoir readout achieves cross-modal recall@10 >= 0.75 after 100 training
  examples per modality pair.
HARD-FAIL: Reservoir state mixes modalities so thoroughly that individual modality
  decodability drops below 0.40 (the reservoir loses modality identity).

#### F2.9 WAVE-INTERFERENCE-HOLOGRAPHIC

Mechanism: Represent each modality's state as a COMPLEX VECTOR with amplitude and phase.
The binding is the element-wise complex product (convolution in frequency space):
  B = S_A * conj(S_V)    [complex-conjugate product, standard HRR binding]

Retrieval: S_A_approx = B * S_V (unbinding by multiplying with the binding key).

The wave-interference interpretation: S_A and S_V are waveforms; their product B is
a hologram that stores the associative relationship between them. When S_V is used as
a reference beam (query), it reconstructs S_A from B.

This is exactly the Holographic Reduced Representation (HRR) of Plate (1995) and the
Fourier Holographic Associative Memory (FHRR) of the substrate's existing architecture.

P_deflated = 0.42 (substrate already uses FHRR; direct extension; highest implementability)

HARD-PASS: Cross-modal recall@10 >= 0.75 for K=3 modality binding with N=10000 FHRR vectors.
HARD-FAIL: Binding capacity < N/10 patterns (HRR interference dominates at K=3).

#### F2.10 FREQUENCY-MIXING-NONLINEAR

Mechanism: Represent each modality's state as a vector oscillating at a characteristic
frequency (audio at f_A, video at f_V). A nonlinear mixing element produces sum and
difference frequencies f_A + f_V and f_A - f_V. The difference frequency f_A - f_V
is low and can serve as a temporal binding signal (the temporal envelope of the cross-
correlation between modalities).

Mathematical form: if x_A[t] = A_A * cos(2*pi*f_A*t + phi_A) and
x_V[t] = A_V * cos(2*pi*f_V*t + phi_V), then their product gives:
  x_A * x_V = (A_A * A_V / 2) * [cos(2*pi*(f_A-f_V)*t + (phi_A-phi_V)) + cos(2*pi*(f_A+f_V)*t)]

The low-frequency component at f_A - f_V carries the PHASE DIFFERENCE phi_A - phi_V.
This is the binding signal. When phi_A = phi_V, the binding is constructive; when
phi_A - phi_V = pi, destructive.

P_deflated = 0.18 (elegant physics; less direct path to substrate implementation)

HARD-PASS: Phase difference phi_A - phi_V is extractable to within 5 degrees at SNR > 10dB.
HARD-FAIL: Frequency mixing products are indistinguishable from noise in the substrate space.

---

### F3. Five empirical tests (cheap decisive, ordered by prerequisite)

#### Test 1 (T-BIND-1): Per-modality substrate binding capacity
CPU laptop, ~30 min.

Pre-reg: With N=10000 FHRR vectors and K=3 modalities, role-vector binding (F2.1).
Store M patterns per modality (vary M in {10, 100, 1000}).
Query: given B = S_A * r_A + S_V * r_V + S_M * r_M, retrieve S_k_approx = B * r_k.
Measure recall@10 of retrieved S_k vs ground truth.

HARD-PASS: recall@10 >= 0.80 at M=100 for all 3 modalities.
HARD-FAIL: recall@10 < 0.50 at M=100 for any modality.

This is the gate test: if F2.1 fails, F2.9 (FHRR-based) is likely to fail too.
If F2.1 passes, it validates the core binding mechanism.

#### Test 2 (T-BIND-2): Async temporal offset degradation
CPU laptop, ~20 min. Depends on T-BIND-1 passing.

Pre-reg: Vary temporal offset delta_t between S_A and S_V samples (from 0 to tau_max).
Measure recall@10 of cross-modal binding as a function of delta_t.
Identify tau_max at which recall@10 drops below 0.70.

HARD-PASS: recall@10 >= 0.75 at delta_t = 33ms (one video frame period).
HARD-FAIL: recall@10 < 0.60 at delta_t = 33ms.

If HARD-FAIL: async binding (F2.3) is compromised by temporal misalignment at frame
timescale, and synchronous polling within the video frame is required.

#### Test 3 (T-BIND-3): Event-driven update rate vs binding quality
CPU laptop, ~20 min. Uses output from T-BIND-1.

Pre-reg: For audio at 44.1kHz, apply event-driven threshold delta_A in {0.01, 0.05, 0.10,
0.20} (cosine distance threshold). Measure effective update rate as fraction of nominal
rate, and measure recall@10 at the binding layer.

HARD-PASS: delta_A = 0.05 achieves >= 10x update rate reduction at < 0.05 recall@10 drop.
HARD-FAIL: Any delta_A achieving >= 10x reduction causes > 0.15 recall@10 drop.

#### Test 4 (T-BIND-4): Kuramoto phase-lock convergence
CPU laptop, ~30 min. Independent of T-BIND-1.

Pre-reg: K=3 Kuramoto oscillators with natural frequencies omega_k proportional to
{44.1kHz, 1kHz, 30Hz} (scaled to unit range for simulation). Coupling K varies in
{0.1, 0.5, 1.0, 2.0, 5.0}. Measure time to phase lock (within 0.1 radians) and
whether lock-in is achieved in < 1000 simulation steps.

HARD-PASS: K = 1.0 achieves phase lock in < 100 simulation steps.
HARD-FAIL: Phase lock requires K > 5.0 (too high for substrate coupling budget).

Note: this test is on the oscillator dynamics only, not on the full substrate. A pass
here enables T-BIND-5.

#### Test 5 (T-BIND-5): Holographic cross-modal retrieval with phase encoding
CPU laptop, ~30 min. Depends on T-BIND-1 passing and T-BIND-4 informing phase parameterization.

Pre-reg: Build B = S_A * conj(S_V) * exp(i * phi_AB) where phi_AB is the phase alignment
angle from T-BIND-4. Retrieve S_A_approx = B * conj(S_V). Measure recall@10 vs the
baseline B = S_A * conj(S_V) (no phase encoding).

HARD-PASS: Phase-encoded binding recall@10 >= 0.80 at M=100 patterns; improvement
  over no-phase baseline >= 0.05 in recall@10.
HARD-FAIL: Phase encoding provides no improvement (within noise of baseline).

---

### F4. Honest highest-P path

The two paths with highest P_deflated and lowest implementation cost:

#### PATH 1 (P_deflated = 0.40): PER-MODALITY-SUBSTRATE + ROLE-VECTOR BINDING

This is F2.1 and it is the substrate-native path. It requires:
- Three instances of the existing substrate (reuse existing code)
- Fixed random role vectors r_A, r_V, r_M (one-time generation)
- A binding step that runs at 30Hz: B = S_A * r_A + S_V * r_V + S_M * r_M
- Cross-modal retrieval: query B with r_k to recover S_k_approx

The substrate ALREADY supports FHRR complex-valued binding operations. This is a direct
extension of PP-257 (one-shot binding, validated) to K=3 modalities at different rates.

The key unknown is the capacity bound at K=3 modalities. VSA theory predicts this is
solvable with N >= 10000. The substrate has operated at N=65536 in other contexts.

#### PATH 2 (P_deflated = 0.42): WAVE-INTERFERENCE-HOLOGRAPHIC (F2.9)

This is the HRR/FHRR path and it is the most directly substrate-native because the
substrate already uses FHRR. Binding two modalities is: B = S_A * conj(S_V). Extending
to three: B = S_A * conj(S_V) * conj(S_M). Retrieval: S_A_approx = B * S_V * S_M.

The caveat: at K=3 multiplied bindings, the interference grows. The capacity scales as
N / (K-1) in practice. For K=3, N=10000 gives capacity ~5000. This should be validated
empirically before committing to this path.

#### COMBINED RECOMMENDATION

PATH 1 and PATH 2 are NOT mutually exclusive. The role-vector approach (PATH 1) and
the HRR approach (PATH 2) converge when the role vectors r_k are complex-conjugate
pairs: r_A = conj(r_V_A) etc. A combined architecture:

  B = S_A * r_A + S_V * r_V + S_M * r_M   [PATH 1: bundling with roles]
  B_cross = S_A * conj(S_V)                [PATH 2: pairwise holographic binding]
  B_total = alpha * B + (1-alpha) * B_cross [blend; alpha tuned by T-BIND-1, T-BIND-5]

This gives both the "memory of all modalities" (PATH 1) and the "pairwise cross-modal
association" (PATH 2), with a single blending parameter alpha.

---

## CHEAP DECISIVE TEST

T-BIND-1: 30 minutes, CPU laptop, no new infrastructure.
Build 3 FHRR substrate instances (N=10000). Generate random role vectors. Store 100
patterns per modality. Compute B = S_A * r_A + S_V * r_V + S_M * r_M. Retrieve
S_k_approx = B * r_k. Measure recall@10. If recall@10 >= 0.80 for all 3 modalities:
PATH 1 is validated. If < 0.50: revisit N or use PATH 2 exclusively.

---

## FALSIFIABLE PREDICTIONS

### HARD-PASS thresholds (any of these = proceed to production-scale implementation)

HP-1: T-BIND-1 recall@10 >= 0.80 at N=10000, M=100, K=3 modalities.
HP-2: T-BIND-5 recall@10 >= 0.80 with phase-encoded holographic binding; improvement
      over no-phase baseline >= 0.05.
HP-3: T-BIND-3 delta_A = 0.05 achieves >= 10x update rate reduction at < 0.05 recall drop.

### HARD-FAIL thresholds (any of these = do not proceed without design revision)

HF-1: T-BIND-1 recall@10 < 0.50 at N=10000, M=100 -- role-vector binding has insufficient
      capacity at K=3; need N >= 50000 or a different binding operation.
HF-2: T-BIND-2 recall@10 < 0.60 at delta_t = 33ms -- temporal offset at the frame rate
      destroys binding quality; synchronous polling within frames is required.
HF-3: T-BIND-4 phase lock requires K_Kuramoto > 5.0 -- Kuramoto binding is not feasible
      for the substrate's coupling budget.

---

## CROSS-THREAD SYNTHESIS

This drill connects to the following active substrate threads:

1. PP-257 (one-shot binding, validated): The per-modality substrate architecture (F2.1)
   is a direct extension of PP-257 from K=1 to K=3. PP-257's validation is load-bearing
   evidence for PATH 1.

2. v3.0 compositional cliff (2026-06-10 memory note): The compositional architecture
   validated in v3.0 per-level cascading cleanup is the organizational framework into
   which multimodal binding slots. The "per-level" hierarchy maps to the per-modality
   compression hierarchy (F2.5).

3. Tier-5c v2.0 LLM integration (exp_dev brief): The cross-modal substrate binding
   architecture connects to the LLM substrate-attention mechanism. The per-modality
   substrate instances (S_A, S_V, S_M) can be queried by the LLM's attention mechanism
   via cross-substrate retrieval (E9 connection). This extends the existing substrate-
   LLM coupling to multimodal inputs.

4. Multi-hop revival: The per-modality substrate architecture enables a new multi-hop
   reasoning path: audio establishes a binding to a concept, visual confirms it, and
   the combined binding vector B is used as a query for the next hop. This is
   cross-modal multi-hop retrieval, which is not currently supported.

5. Field coverage: This drill is in the scope-expansion category (new field:
   multimodal-processing, drill count = 0 before this drill). The adjacency anchor
   is HDC/VSA (existing field, fruit-bearing). This satisfies Trigger B from the
   research role contract.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. Real-time AV alignment: The async per-modality substrate architecture (F2.1 + F2.3)
   enables the substrate to maintain aligned representations of audio and video streams
   at their native rates without requiring synchronous sampling. This is a prerequisite
   for any real-time audio-visual product (video call enhancement, lip-sync correction,
   AV content indexing).

2. Sensorimotor integration: The compression hierarchy (F2.5) with event-driven updates
   (F2.3) reduces the computational cost of 1kHz sensorimotor integration to manageable
   levels. This opens a path to robotic/device integration where the substrate indexes
   high-rate sensor data without running at 1kHz.

3. Cross-modal search: Once B = phi(S_A, S_V) is computed, a user can query with audio
   to retrieve visual content or vice versa. This is multimodal search, which is a
   direct product feature. The substrate's existing recall@10 precision metric applies
   directly.

4. Temporal grounding of LLM outputs: The predictive cross-modal loop (F2.4) enables
   the substrate to flag when audio and visual streams become temporally unaligned
   (e.g., deepfake detection, AV sync error). The prediction error vector err_V is a
   substrate-native signal that requires no additional training.

---

## CITATIONS (verified count: 18)

1. Functional specialisation of multisensory temporal integration in the mouse superior
   colliculus. Nature Communications 2025. PMC12575753.
   https://www.nature.com/articles/s41467-025-64600-x

2. Stein BE, Meredith MA. The Merging of the Senses. MIT Press, 1993. (Stein-Meredith
   superadditivity principle; foundational reference)

3. Synchronization of Sensory Gamma Oscillations Promotes Multisensory Communication.
   PMC6873160. https://pmc.ncbi.nlm.nih.gov/articles/PMC6873160/

4. Critical role of phase difference in gamma oscillation within the temporoparietal
   network for binding visual working memory. Scientific Reports 2016. PMC5004173.
   https://www.nature.com/articles/srep32138

5. Miyato T et al. Artificial Kuramoto Oscillatory Neurons. ICLR 2025. arxiv 2410.13821.
   https://arxiv.org/html/2410.13821v1

6. Crossmodal hierarchical predictive coding for audiovisual sequences in the human
   brain. Communications Biology 2024. https://www.nature.com/articles/s42003-024-06677-6

7. Rao RP, Ballard DH. Predictive coding in the visual cortex. Nature Neuroscience 1999.
   (predictive coding framework; foundational reference)

8. Kuramoto Y. Chemical Oscillations, Waves and Turbulence. Springer 1984.
   (Kuramoto model foundational reference)

9. Weiss Y, Simoncelli EP, Adelson EH. Motion illusions as optimal percepts. Nature
   Neuroscience 2002. (Bayesian cue combination; McGurk precursor)

10. Efficient encoding of spectrotemporal information for bat echolocation. PLOS
    Computational Biology 2021. PMC8270447.
    https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8270447/

11. Sensorimotor dynamics in the superior colliculus of the echolocating bat. bioRxiv
    2025. https://www.biorxiv.org/content/10.1101/2025.08.26.672231.full.pdf

12. Plate TA. Holographic Reduced Representations. IEEE Transactions on Neural Networks
    1995. (HRR foundational reference)

13. Survey on Hyperdimensional Computing aka Vector Symbolic Architectures, Part I.
    ACM Computing Surveys 2022. https://dl.acm.org/doi/10.1145/3538531

14. Hyperdimensional Uncertainty Quantification for Multimodal Uncertainty Fusion in
    Autonomous Vehicles Perception. arxiv 2503.20011.

15. Impact of time-history terms on reservoir dynamics and prediction accuracy in echo
    state networks. Scientific Reports 2024.
    https://www.nature.com/articles/s41598-024-59143-y

16. Radford A et al. Learning Transferable Visual Models From Natural Language
    Supervision (CLIP). ICML 2021. (late fusion contrastive alignment)

17. Towards LLM-Centric Multimodal Fusion: A Survey on Integration Strategies and
    Techniques. arxiv 2506.04788. https://arxiv.org/html/2506.04788v1

18. Causal inference shapes crossmodal postdiction in multisensory integration.
    Scientific Reports 2026. https://www.nature.com/articles/s41598-026-36884-6

---

P_deflated_final = 0.32 (combined; PATH 1 = 0.40, PATH 2 = 0.42, combined architecture = 0.35)
Next-drill candidate: SPIKE-TIMING-SUBSTRATE (F2.7) -- outer product memory for cross-modal
  Hebbian association, connects to modern Hopfield theory (Tier-1 per field advisor)
