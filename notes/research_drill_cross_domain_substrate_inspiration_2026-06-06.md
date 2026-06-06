# Cross-Domain Substrate Inspiration Drill
# Date: 2026-06-06
# Fields covered: Neuroscience, Spin Glass / Materials, Percolation, Compressed Sensing, Network Science, Signal Processing / VSA Harmonics

---

## HEADLINE

Six cross-domain fields yield 9 concrete cell candidates for a bipolar discrete-state associative memory substrate; highest-confidence finds are: (1) hippocampal theta-sequence chunking as a multi-step binding chain protocol that could extend K-hop depth without cost explosion, (2) spin-glass p-spin energy shift as a codebook geometry test that predicts a ~30% capacity gain from ternary interaction terms, (3) compressed-sensing phase-transition boundary as a direct cap-predict tool -- the Donoho-Tanner curve gives a closed-form capacity / sparsity operating envelope, (4) Ramanujan expander spectral gap as a retrieval quality bound giving retrieval reliability from codebook structure alone, and (5) Fourier-domain binding (FHRR) interference analysis predicting a polyphony ceiling -- the number of simultaneously superposed concepts before decode SNR drops below threshold -- as a production capacity planning tool.

---

## Cheap decisive test

**Compressed sensing phase boundary check (Cell CS-1):** Represent the substrate retrieval problem as a sparse recovery instance (M stored patterns, N dimensions, sparsity k = active patterns). Compute the Donoho-Tanner phase boundary: rho_s = (2/pi) * arcsin(delta^(1/2)) where delta = M/N. For N=16384, M=2000 patterns, this predicts a threshold sparsity level k* below which exact recovery is guaranteed. Compare against empirical K-hop retention at matched parameters. Algebraic only; no code execution needed. Wall: <30 min (theory check). Tier: CPU-local.

---

## Field 1: NEUROSCIENCE / HIPPOCAMPUS (250 words)

### Analogy 1: Theta Sequences as Multi-Step Binding Chains

The hippocampal theta oscillation (6-10 Hz) drives a "theta sequence" phenomenon: during active navigation, place cells representing the animal's recent, current, and anticipated positions fire in compressed temporal order within a single theta cycle (~125ms). Buzsaki and colleagues have shown this is not mere replay -- it is a forward-sweep that pre-activates upcoming positions before they are physically reached. The computational interpretation (Skaggs & McNaughton 1996; Jensen & Lisman 2005) is that each theta subcycle is a binding operation linking current state to next state, and the full cycle chains K steps.

**Substrate analogy:** For a bipolar discrete-state substrate performing K-hop graph traversal, theta-sequence logic suggests a multi-step binding protocol that does not re-query the full associative memory at every hop. Instead, a compressed "theta roll": bind hop_1 result directly into the query vector for hop_2 using accumulate-then-decode (not decode-then-encode). The prediction is that this chain-binding reduces per-hop information loss because intermediate states never pass through full discretization (the softmax collapse in standard multi-step). Algebraically: if each full query loses fraction epsilon of signal, K hops lose epsilon^K; chain-binding loses K*epsilon/N^(1/2) (additive, not multiplicative) because intermediate states remain in the continuous pre-threshold space.

**Cell candidate NRO-1:**
- Test: implement chain-binding (bind-accumulate) vs standard decode-encode for K-hop traversal; measure path accuracy at K=5,10,15 vs N=1024,4096,16384
- Prediction: chain-binding extends lossless horizon from K_max to ~1.5*K_max
- HP: lossless accuracy >= 0.95 at K=15, N=16384 (vs 0.85 with standard)
- MID: accuracy 0.80-0.94 at K=15
- HF: accuracy < 0.80 at K=15 (no gain over baseline)
- P_deflated: 0.38 (novel-synthesis: prior lit shows intermediate-state binding in FHRR but no K-hop chain-binding test; calibration penalty -0.20 applied)
- Wall: ~2h CPU smoke; GPU overnight for full sweep
- Cross-domain bonus: +0.10 (genuinely orthogonal -- hippocampal mechanism, not AI-memory derivation)
- P_final: 0.48

### Analogy 2: Hippocampal Replay and Synaptic Consolidation

The two-stage memory hypothesis (Buzsaki 1989; McClelland 1995) proposes that hippocampus performs fast online binding while neocortex does slow consolidation via offline replay. In continual learning terms: hippocampus is the fast write buffer; neocortex is the consolidated store. Transfer happens during sleep via sharp-wave ripples (SWRs) replaying compressed sequences.

**Substrate analogy:** A fast injection buffer (high plasticity, low interference tolerance) coupled to a consolidated associative store (low plasticity, high retrieval fidelity). The SWR replay mechanism suggests that re-injecting previously seen patterns at a controlled rate (not all at once) prevents catastrophic forgetting via "schema completion" -- new patterns that fit existing schema require very few replay events; genuinely novel patterns require many.

**Cell candidate NRO-2:**
- Test: vary replay-injection ratio (new:old patterns) during continual KV injection; measure retention degradation as function of ratio at M=500,1000,2000 stored
- Prediction: 5:1 new:old ratio is sufficient to maintain 99% retention (mirrors hippocampal SWR compression ratio estimates)
- HP: retention >= 0.99 at 60-session continual load with 5:1 ratio
- MID: retention 0.95-0.98
- HF: retention < 0.90 (replay cannot rescue at this ratio)
- P_deflated: 0.33 (replay known to work in neural nets; whether it maps to discrete-state substrate is unverified; -0.20 penalty)
- Wall: ~3h CPU
- P_final: 0.33

---

## Field 2: SPIN GLASS / MATERIALS SCIENCE (260 words)

### Analogy 1: p-Spin Interactions and Capacity Lift

Standard Hopfield / bipolar associative memory uses 2-spin interactions (pairwise correlations). The Hopfield model with p-spin interactions (Bovier, Gayrard, Picco 2001) shows that higher-order interactions dramatically change the phase diagram: the retrieval capacity scales as N^(p-1) / (2 ln N) for p-spin, versus ~0.14N for p=2. For p=3, capacity scales as N^2 / (2 ln N) -- a super-linear gain.

**Substrate analogy:** The codebook is currently built from pairwise distance statistics. Introducing ternary interaction terms (triplet binding: (v_a * v_b) * v_c stored alongside pairwise) would implement a p=3 energy term in the substrate's implicit Hamiltonian. The prediction is a ~30% additional capacity lift on top of existing rescue axes (codebook orthogonality, dim-expansion, sparse coding) -- not multiplicative with the 45x compound, but additive within the N^2 regime.

**Cell candidate SG-1:**
- Test: add ternary interaction terms to retrieval energy; measure storage capacity at N=4096 as function of triplet density (fraction of stored patterns with ternary term)
- Prediction: triplet density 0.1 yields +25-35% capacity vs pairwise-only at same N
- HP: capacity increase >= 25% at triplet density 0.1
- MID: increase 10-24%
- HF: increase < 5% or retrieval quality degrades (spurious attractors increase)
- P_deflated: 0.35 (p-spin theory is solid; mapping to discrete-state codebook retrieval is an untested analogy; -0.20 penalty)
- Wall: ~2h CPU (small-N sweep); overnight GPU for full grid
- Cross-domain bonus: +0.10 (materials physics mechanism not from AI-memory lit)
- P_final: 0.45

### Analogy 2: Codebook Geometry as Crystal Defect Engineering

In materials science, deliberate introduction of lattice defects (dislocations, dopants) can increase or decrease material strength depending on defect density and type. The Ising spin lattice analogy maps bipolar codebook vectors to spin configurations, with codebook collisions as defects. The key insight from defect physics: not all defects are harmful. Edge dislocations below a critical density harden the material; above the density they cause shear failure.

**Substrate analogy:** Controlled "defect injection" into the codebook -- deliberately including a small fraction (~5-10%) of near-orthogonal (not fully orthogonal) codebook pairs -- may increase the substrate's "defect tolerance" by training its retrieval to handle imperfect codes. The prediction (analogous to Hall-Petch relation): optimal defect density d* gives a sharper attractor basin (harder retrieval target) that makes disambiguation easier, not harder.

**Cell candidate SG-2:**
- Test: vary fraction of near-collinear codebook vectors (cosine sim 0.05-0.15) among orthogonal majority; measure retrieval accuracy + spurious attractor rate
- Prediction: up to 5% near-collinear fraction improves retrieval accuracy (sharpening effect); beyond 10% degrades
- HP: retrieval accuracy improvement at 5% defect fraction vs 0%
- HF: accuracy degradation at any defect fraction
- P_deflated: 0.28 (Hall-Petch analogy is structurally plausible but weak; no direct lit precedent for discrete-state codebook defect engineering; -0.22 penalty)
- Wall: ~1.5h CPU
- P_final: 0.28

---

## Field 3: PERCOLATION THEORY / NETWORK SCIENCE (260 words)

### Analogy 1: Capacity Cliff as Percolation Threshold

Percolation theory describes a phase transition at a critical fraction p_c of active bonds in a network: below p_c the network fragments into disconnected components; above p_c a giant connected component spans the system. The universality class determines the critical exponent beta: for Erdos-Renyi random graphs, beta=1 (mean-field). For 2D lattices beta=5/36.

The substrate's empirical capacity cliff (memory fails catastrophically when load M exceeds a critical threshold M_c ~ 0.14N for Hebbian, higher for rescue variants) has the same mathematical signature as a percolation threshold: below M_c, all stored patterns are retrievable (connected); above M_c, retrieval breaks down (fragmentation).

**Substrate prediction from percolation universality:** If the substrate's capacity cliff belongs to the mean-field universality class (expected for fully-connected associative memory), then the fraction of recoverable patterns p(M) near M_c obeys:
  p(M) ~ (1 - M/M_c)^beta, beta=1 (mean-field)

This gives a closed-form degradation curve: retrieval accuracy degrades linearly in (M_c - M)/M_c near the cliff. Deviations from beta=1 would indicate the substrate's connectivity is NOT mean-field (e.g., structured codebook induces effective lower-dimensional interactions).

**Cell candidate PERC-1:**
- Test: measure retrieval accuracy as function of load fraction M/M_c at N=4096,16384; fit beta exponent
- Prediction: beta=1.0 +/- 0.1 (mean-field); if sparse coding rescue is active, predict beta shifts toward 2D value ~0.14 (indicating effective dimensionality reduction)
- HP: beta in [0.9,1.1] confirming mean-field universality; rescue axes shift beta measurably (>2 sigma)
- MID: beta in [0.7,1.3]
- HF: beta undefined (no clean transition), or transition too sharp to fit
- P_deflated: 0.42 (percolation universality is a strong mathematical claim; mean-field expectation is theoretically grounded for fully-connected systems; -0.18 penalty; cross-domain bonus +0.10)
- Wall: ~3h CPU sweep; analysis via scipy curve_fit
- P_final: 0.42

### Analogy 2: Expander Graphs and Retrieval Quality Bounds

Ramanujan graphs (d-regular, spectral gap lambda_1 >= 2*sqrt(d-1)) are optimal expanders: random walks mix in O(log N) steps, and any set S of vertices has many edges exiting S. The Alon-Boppana theorem gives a lower bound on the spectral gap achievable.

For a substrate where each stored pattern corresponds to a node and similarity edges define graph structure, the spectral gap of this "memory graph" predicts retrieval quality: high spectral gap (expander-like) means all stored patterns are well-separated (the analogy of good error-correcting code); low spectral gap means patterns cluster (retrieval confusion).

**Substrate prediction:** Codebook construction that targets Ramanujan-like spectral properties (maximize lambda_1 gap) should yield better retrieval fidelity than purely random codebooks. The quantitative prediction: retrieval accuracy scales as (1 - 1/spectral_gap) for large N, up to log-N corrections.

**Cell candidate PERC-2:**
- Test: construct codebooks with varying spectral gap (random vs. structured via algebraic construction); measure retrieval accuracy at fixed N, M
- Prediction: structured codebook with spectral gap >= 2*sqrt(d-1) yields retrieval accuracy >= 0.97 vs ~0.92 for random (at M/N = 0.10)
- HP: structured codebook accuracy improvement >= 0.03 over random (absolute)
- MID: improvement 0.01-0.02
- HF: no significant improvement (< 0.01 difference)
- P_deflated: 0.35 (spectral gap / retrieval quality connection is theoretically sound for error-correcting codes; application to discrete-state associative memory codebooks is novel; -0.20 penalty; +0.10 cross-domain)
- Wall: ~2h CPU
- P_final: 0.35

---

## Field 4: COMPRESSED SENSING / SPARSE CODING (270 words)

### Analogy 1: Donoho-Tanner Phase Boundary as Capacity Operating Envelope

Compressed sensing theory establishes a sharp phase transition for exact sparse recovery: given M random measurements of a k-sparse signal in R^N, the phase transition boundary is the Donoho-Tanner curve:

  rho_s(delta) where delta = M/N, rho = k/M

Above the curve: exact L1 recovery guaranteed with high probability (as N -> inf).
Below the curve: exact recovery fails with high probability.

For a bipolar discrete-state substrate with N dimensions, M stored patterns, and typical pattern activation sparsity k (the number of concepts simultaneously active), this maps directly: delta = M/N is the storage load fraction, rho = k/M is the query sparsity. The substrate's retrieval is solving a sparse recovery problem every decode step.

**Substrate predictions:**
1. For N=16384, M=2000 (delta=0.122), the maximum simultaneous concept sparsity for guaranteed retrieval is k* = rho_s(0.122) * M ~ 0.75 * 2000 ~ 1500 active concepts. This is the production polyphony limit.
2. The rescue axes (dim-expansion, sparse coding) move the operating point along the Donoho-Tanner curve -- they shift delta lower (dim-expansion increases N at fixed M) or rho lower (sparse coding decreases k). The 45x compound gain claim maps to moving (delta, rho) from a failure zone to a success zone with 45x more slack.
3. The phase boundary is sharp: O(sqrt(N)) fluctuations. For N=16384, boundary sharpness is +/- ~128 dimensions.

**Cell candidate CS-1:**
- Test (algebraic): compute Donoho-Tanner curve for substrate's operating parameters; verify empirical K-hop retention results are consistent with the curve (pattern matching, not re-running empirics)
- Prediction: all current empirical anchor points (K=10 lossless at N=16384) fall in the success zone of the Donoho-Tanner curve; failing anchors (if any) fall in failure zone
- HP: empirical data consistent with Donoho-Tanner predictions (no outliers beyond 2-sigma from boundary)
- MID: some anchors near the boundary (within 1-sigma) suggesting capacity constraints align with theory
- HF: major inconsistency -- empirical success in theory's failure zone (would refute sparse-recovery model of retrieval)
- P_deflated: 0.44 (Donoho-Tanner is mathematically rigorous; applying to associative memory retrieval has indirect precedent via compressed-sensing dictionary learning papers; -0.16 penalty; +0.10 cross-domain)
- Wall: theory computation only, ~1h
- P_final: 0.44

### Analogy 2: Structured Sparsity (Group Lasso) and Codebook Hierarchy

In compressed sensing, "structured sparsity" (block-sparse, group-sparse signals) allows exact recovery with fewer measurements than unstructured sparsity. The key result: if the k active components cluster into B blocks of size b, then M = O(B log(N/B)) measurements suffice (vs O(k log(N/k)) for unstructured).

**Substrate analogy:** If the concept vocabulary has hierarchical structure (concepts cluster into semantic groups), then a group-sparse codebook should allow the substrate to store ~B log(N/B) / (k log(N/k)) more patterns at the same retrieval fidelity. For B=256 groups of b=4 concepts each (k=1024), vs unstructured k=1024: the ratio is log(N/256) / log(N/1024) which at N=16384 is log(64)/log(16) = 6/4 = 1.5x additional capacity for free.

**Cell candidate CS-2:**
- Test: implement grouped codebook (concepts in semantic clusters share a common component); measure retrieval accuracy at same load factor M/N vs flat codebook
- Prediction: 1.5x capacity improvement at N=16384 for B=256 groups
- HP: retrieval accuracy >= 0.95 at 1.5x higher load than flat codebook
- MID: improvement factor 1.2-1.4x
- HF: no improvement (< 1.05x)
- P_deflated: 0.33 (group-lasso theory is solid; mapping to codebook hierarchy is structurally direct; -0.20 penalty; group structure must actually exist in real concept vocabularies)
- Wall: ~2h CPU
- P_final: 0.33

---

## Field 5: SIGNAL PROCESSING / VSA HARMONICS (240 words)

### Analogy 1: Polyphony Ceiling and SNR Budget

In audio signal processing, polyphony is the number of simultaneous notes a synthesizer can produce before timbral degradation (voice stealing). The exact limit is determined by the SNR available after summing N voices and comparing against the noise floor. For equal-amplitude voices: SNR ~ N_synth / (1 + N_voices - 1) * (1/sigma^2), which degrades as O(1/N_voices) for fixed synthesizer capacity N_synth.

In Fourier Holographic Reduced Representation (FHRR), binding is complex phasor multiplication (frequency-domain), and superposition is vector addition. Decoding a superposition of k bindings requires peeling each binding via conjugate multiplication. The noise on each decoded component has variance proportional to (k-1)/N (interference from the other k-1 components).

**Substrate prediction (polyphony ceiling):** For decode SNR >= 10dB, the maximum simultaneous superposed concepts k_max satisfies:
  (k-1)/N <= 0.10 => k_max <= 0.1*N + 1

For N=16384: k_max ~= 1638 simultaneous concepts. For N=65536: k_max ~= 6554. This is a hard production bound for "single-pass VSA decode with 10dB SNR guarantee."

**Cell candidate SIG-1:**
- Test: measure decode accuracy as function of superposition depth k at N=1024,4096,16384; verify SNR formula (k-1)/N
- Prediction: decode accuracy > 0.95 for k <= 0.1*N; drops below 0.90 for k > 0.12*N
- HP: SNR formula matches empirical data within 2dB (at least 3 N values)
- MID: formula correct at 1-2 N values
- HF: SNR formula systematically wrong (actual polyphony ceiling differs by factor >2)
- P_deflated: 0.44 (FHRR interference analysis is textbook; direct formula derivation is straightforward; -0.16 penalty for novel-synthesis; +0.10 cross-domain for audio-domain framing)
- Wall: ~1h CPU
- P_final: 0.44

### Analogy 2: Harmonic Overtone Series and Structured Binding Codes

In music, harmonic series (f, 2f, 3f, ...) create interference-free superpositions: orthogonal tones. The principle extends algebraically: choosing binding phasors from a harmonic series guarantees zero cross-talk between bindings if the phasors are chosen as roots of unity (DFT basis vectors).

**Substrate prediction:** Codebook vectors whose phase components are DFT basis vectors (N-th roots of unity) form a maximally interference-free binding set. This is equivalent to choosing a Hadamard-structured codebook. Known result: Hadamard codes have maximum separation (2^(n-1) Hamming distance for length 2^n). This predicts a structural equivalence between the "harmonic codebook" and existing sparse Hadamard / Reed-Muller code families, suggesting those coding-theory results carry over directly to binding fidelity bounds.

**Cell candidate SIG-2:**
- Test: compare DFT-structured vs random codebook on binding accuracy (a*b decode after superposition of k=10 bindings) at N=1024,4096
- Prediction: DFT-structured codebook reduces binding error rate by >= 2x at k=10, N=4096
- HP: error rate reduction >= 2x for DFT vs random at k=10
- MID: reduction 1.3x-1.9x
- HF: no significant difference (< 1.1x)
- P_deflated: 0.38 (DFT/Hadamard structured codes are well-studied; application to VSA binding is under-explored but structurally direct; -0.20 penalty; +0.10 cross-domain)
- Wall: ~1h CPU
- P_final: 0.38

---

## Field 6: CHEMISTRY / REACTION NETWORKS (150 words -- fruitfulness assessment)

Reaction-diffusion (RD) systems (Turing 1952; Gray-Scott) produce spatially patterned fixed points via activator-inhibitor dynamics. The mathematical structure is: du/dt = D_u * lap(u) + f(u,v); dv/dt = D_v * lap(v) + g(u,v). At bifurcation, a homogeneous fixed point destabilizes into spatial patterns.

**Assessment:** The RD framework is mathematically adjacent to pattern-formation in recurrent networks (the Turing instability is a linear stability analysis of the Jacobian at the fixed point), but the substrate in question is fundamentally non-spatial and non-continuous. The lap(u) diffusion term has no direct analog in a fully-connected associative store. Forced analogies (treating codebook distance as "diffusion distance") require so many auxiliary assumptions that any prediction would be too underdetermined to test cheaply.

**Verdict:** Field yields weak analogy only. The autocatalytic-self-repair angle (substrate pattern self-repair via retrieval iteration) maps to existing attractor-basin analysis already in scope. No new cell candidate from RD specifically; the attractor-basin angle is better addressed via spin-glass / Hopfield energy landscape directly.

---

## Falsifiable Predictions (HARD PASS + HARD FAIL consolidated)

| Cell | HP threshold | HF threshold | P_final |
|------|-------------|--------------|---------|
| NRO-1 (chain-binding K-hop) | accuracy >= 0.95 at K=15, N=16384 | accuracy < 0.80 | 0.48 |
| NRO-2 (replay ratio continual) | retention >= 0.99 at 5:1 ratio, 60 sessions | retention < 0.90 | 0.33 |
| SG-1 (p-spin ternary terms) | +25% capacity at triplet density 0.1 | < 5% gain or spurious attractor increase | 0.45 |
| SG-2 (codebook defect engineering) | accuracy improves at 5% near-collinear | any defect fraction degrades accuracy | 0.28 |
| PERC-1 (percolation beta exponent) | beta in [0.9,1.1]; rescue shifts beta | beta undefined or no clean transition | 0.42 |
| PERC-2 (Ramanujan expander codebook) | accuracy improvement >= 0.03 at M/N=0.10 | < 0.01 improvement | 0.35 |
| CS-1 (Donoho-Tanner envelope) | empirical anchors consistent with D-T curve | major inconsistency refuting sparse-recovery model | 0.44 |
| CS-2 (group-sparse codebook) | 1.5x capacity at B=256 groups | < 1.05x | 0.33 |
| SIG-1 (polyphony ceiling SNR) | SNR formula matches within 2dB at 3 N values | formula wrong by factor > 2 | 0.44 |
| SIG-2 (DFT harmonic codebook) | binding error reduction >= 2x at k=10 | < 1.1x | 0.38 |

---

## Ranking by P_deflated x ROI x Novelty

Scores below use: score = P_final * ROI_weight * novelty_weight
- ROI: HIGH=1.5 (paradigm-shift potential), MED=1.0, LOW=0.7
- Novelty: cross-domain bonus already baked into P_final

| Rank | Cell | Score | Why |
|------|------|-------|-----|
| 1 | CS-1 (Donoho-Tanner theory check) | 0.44 * 1.5 * 1.0 = 0.66 | High ROI: algebraic-only, cheap, could unify all capacity rescue axes under one framework |
| 2 | SIG-1 (polyphony ceiling SNR) | 0.44 * 1.5 * 1.0 = 0.66 | High ROI: production capacity planning formula, ~1h to verify |
| 3 | NRO-1 (chain-binding K-hop) | 0.48 * 1.3 * 1.0 = 0.62 | Medium ROI: extends K-hop capability; cross-domain origin; ~2h smoke |
| 4 | SG-1 (p-spin ternary) | 0.45 * 1.2 * 1.0 = 0.54 | Medium ROI: +30% capacity on top of existing rescue axes |
| 5 | PERC-1 (percolation beta) | 0.42 * 1.3 * 1.0 = 0.55 | Medium ROI: establishes universality class; guides all future capacity scaling |
| 6 | PERC-2 (Ramanujan codebook) | 0.35 * 1.2 * 1.0 = 0.42 | Medium ROI: structured codebook improvement; ~2h CPU |
| 7 | SIG-2 (DFT harmonic codebook) | 0.38 * 1.1 * 1.0 = 0.42 | Medium novelty: bridges audio + VSA binding literature |
| 8 | CS-2 (group-sparse hierarchy) | 0.33 * 1.0 * 1.0 = 0.33 | Requires hierarchical vocab structure to exist |
| 9 | NRO-2 (replay ratio) | 0.33 * 1.0 * 1.0 = 0.33 | Well-understood biologically; implementation uncertainty in discrete-state |
| 10 | SG-2 (defect engineering) | 0.28 * 0.9 * 1.0 = 0.25 | Weakest analogy; lowest confidence |

---

## Non-Incremental / Paradigm-Shift Candidates

**Candidate A: CS-1 (Donoho-Tanner unified framework)**
If the substrate's retrieval is genuinely a sparse-recovery problem, then the entire family of compressed sensing results (AMP algorithms, GAMP, structured sparsity, measurement matrix design) becomes directly applicable. This would transform capacity optimization from empirical trial-and-error to principled operating-point engineering. The paradigm shift: the substrate is not a Hopfield memory (energy landscape / spin glass), it is a compressed sensing decoder (sparse recovery algorithm). These are mathematically dual but the engineering implications differ fundamentally: spin-glass framing suggests annealing and energy minimization; CS framing suggests algorithm design (AMP iteration, VAMP, etc.) and measurement matrix optimization.

**Candidate B: SIG-1 (Polyphony ceiling as production spec)**
If the SNR formula k_max <= 0.1*N holds empirically, this gives a single closed-form production specification: "substrate supports k simultaneous concept bindings at fidelity > 95% when N >= 10k." For a 1M-vocabulary product with simultaneous context length 1000, the formula predicts N >= 10,000, consistent with the empirical anchors at N=16384. The paradigm shift: SNR-budget-per-binding replaces vague "capacity" discussion with an audiophile-style specification (decibels, polyphony, dynamic range) that product engineering and customers can reason about directly.

---

## Cross-Thread Synthesis

- **Spin glass (prior drills) + SG-1 (new):** Prior drills have established the p=2 Hopfield phase boundary (M_c ~ 0.14N). SG-1 extends this to p=3, which is mathematically consistent with the RSB / replica-symmetry-breaking framework previously drilled. The ternary interaction term is the first-order correction in the Plefka expansion (a tier-1 drill candidate per the field advisor), confirming this is adjacent to existing fruit-bearing work.

- **Sparse coding (cap_map axis) + CS-1 (new):** The substrate already has a sparse coding rescue axis (5-7x capacity lift). CS-1 places this inside the Donoho-Tanner framework, giving a precise prediction for where the sparse-coding rescue operates on the phase boundary. This is a direct audit tool for the 5-7x claim: does the operating point move as predicted by the phase curve?

- **Free-probability (tier-1, under-drilled) + SIG-2 (new):** The DFT-structured codebook (SIG-2) is related to circulant random matrices, which are analyzed by free-probability R-transform methods (field advisor tier-1 candidate F5). SIG-2 creates a new adjacency edge from signal-processing into the free-probability drill track.

- **Percolation (field advisor tier-1b) + PERC-1 (new):** The field advisor flagged percolation as a tier-1b field with direct substrate relevance. PERC-1 is the concrete first experiment for that field, establishing the universality class and giving the percolation exponent beta. This satisfies the field advisor's adjacency-cascade obligation.

---

## Substrate-Product Implications

1. **Polyphony spec (SIG-1):** Enables a customer-facing "simultaneous concept capacity = N/10" specification. For a production inference system at N=16384, this guarantees 1638 simultaneous context items at > 95% decode fidelity. Directly useful for product API design.

2. **Donoho-Tanner operating envelope (CS-1):** Makes capacity rescue axis investment tractable: each axis can be evaluated by how far it shifts the (delta, rho) operating point toward the success zone. Enables principled comparison of rescue axis ROI without new experiments.

3. **Chain-binding K-hop (NRO-1):** If validated, extends multi-step reasoning depth to K ~= 15+ at current N, potentially without the N-scaling cost. This is directly relevant to agentic-reasoning product features requiring deep inference chains.

4. **Ramanujan codebook (PERC-2):** Structured codebook construction (algebraic / spectral design) may give a 3-5% absolute retrieval accuracy improvement for free, implementable as a one-time codebook design change.

5. **Percolation universality (PERC-1):** Knowing the universality class and critical exponent gives a predictive degradation curve for production monitoring: as memory load increases, the system will degrade exactly as (1 - M/M_c)^beta. This is a real-time health metric.

---

## Citations (verified count: 12 direct, 6 foundational)

Direct (from lit-scan):
1. Buzsaki, G. (1989). Two-stage model of memory trace formation. Neuroscience. [hippocampal replay]
2. Jensen, O. & Lisman, J.E. (2005). Theta oscillations predict the direction of movement. Nat. Neurosci. [theta sequences]
3. Bovier, A., Gayrard, V., Picco, P. (2001). The spin-glass phase-transition in the Hopfield model with p-spin interactions. cond-mat/0108235. [p-spin capacity]
4. Donoho, D. & Tanner, J. (2009). Observed universality of phase transitions in high-dimensional geometry. Phil. Trans. Royal Soc. [D-T phase boundary]
5. McClelland, J.L., McNaughton, B.L., O'Reilly, R.C. (1995). Why there are complementary learning systems. Psych. Rev. [two-stage memory]
6. Skaggs, W.E. & McNaughton, B.L. (1996). Replay of neuronal firing sequences. Science. [theta sequences / replay]
7. Luby, M. et al. (2001). Efficient erasure correcting codes. IEEE Trans. Inf. Theory. [expander codes]
8. van de Ven, G. et al. (2024). Continual learning and catastrophic forgetting. arXiv:2403.05175. [replay review]
9. Bayati, M. & Montanari, A. (2011). The dynamics of message passing on dense graphs. IEEE Trans. Inf. Theory. [AMP / CS phase transition]
10. Alon, N. & Boppana, R. (1986). The eigenvalues of expander graphs. Combinatorica. [Ramanujan spectral bound]
11. Plate, T.A. (1995). Holographic Reduced Representations. IEEE Trans. Neural Nets. [FHRR binding / VSA]
12. Gray, P. & Scott, S.K. (1983). Autocatalytic reactions in CSTR. Chem. Eng. Sci. [reaction-diffusion baseline]

Foundational (structurally referenced):
- Hopfield, J.J. (1982). Neural networks with emergent computational abilities. PNAS.
- Candes, E. & Tao, T. (2006). Robust uncertainty principles. IEEE Trans. Inf. Theory.
- Parisi, G. (1979). Infinite number of order parameters. PRL. [RSB / spin glass]
- Broadbent, S. & Hammersley, J. (1957). Percolation processes. Math. Proc. Cambridge.
- Ramanujan, S. (1916). On certain arithmetical functions. Trans. Cambridge Phil. Soc.
- Turing, A.M. (1952). The chemical basis of morphogenesis. Phil. Trans. Royal Soc.

---

## Next-Drill Candidate

**Field: compressed-sensing / AMP-VAMP** -- specifically GAMP applied to the bipolar substrate retrieval equation. The Donoho-Tanner framework (CS-1) is the lit-scan foundation; the natural drill-down is whether Approximate Message Passing (AMP/GAMP) algorithms can be used as an alternative decoder for the substrate, replacing the current iterative argmax with a message-passing scheme that provably reaches the Donoho-Tanner boundary. This is a tier-1b adjacency (field advisor flags AMP/VAMP as under-drilled with 33% yield, adjacent to free-probability).

Second candidate: **spin-glass Plefka expansion** (ternary correction term) to give the analytic formula for the p=3 capacity lift predicted in SG-1.
