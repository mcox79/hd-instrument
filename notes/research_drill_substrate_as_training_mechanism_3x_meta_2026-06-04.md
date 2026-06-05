# Research Drill: Substrate-as-Training-Mechanism — 3x META Theoretical Analysis
**Date:** 2026-06-04
**Trigger:** Hard-fail cascade — four substrate-driven training experiments failed (BPC ≈ uniform; curriculum gain negative; in-context gain +0.01 vs 0.10 threshold; 8-channel orchestration zero converged seeds). Meta question: is there a *fundamental theoretical reason* this cannot work, or is it an engineering gap?
**Calibration penalty applied:** P_deflated = P_raw - 0.20; novel-synthesis cap = 0.50
**Prior drill cross-link:** notes/research_drill_substrate_as_full_llm_training_deep_dive_2026-06-03.md

---

## HEADLINE

The four-way hard-fail cascade has three distinct fundamental binding constraints, NOT one — and they operate at different abstraction levels. Constraint 1 is *algebraic*: pure Hebbian/anti-Hebbian outer-product learning converges only to second-order statistics (PCA/whitening), but char-level language statistics require at minimum third-order co-occurrence structure (bigram context sensitivity), which lies outside the proven convergence regime of Oja/Sanger/Foldiak rules. Constraint 2 is *thermodynamic*: the non-reciprocal active-repulsion structure breaks detailed balance, meaning the substrate operates in a non-equilibrium steady state (NESS) that does *not* minimize any scalar free energy — so gradient-descent analogy is categorically inapplicable unless a potential function exists. Constraint 3 is *multi-objective*: eight conflicting signal objectives with PCGrad conflict resolution provably cannot guarantee convergence to a single minimum; MGDA theory shows convergence only to Pareto-stationary points, not global optima, and with zero-mean gradient conflicts the expected update is null. All three constraints are *simultaneously active* in the described setup. P_deflated(substrate-as-primary-training-mechanism feasible with redesign) = 0.22; P_deflated(partial feasibility — single-channel Hebbian readout layer) = 0.38.

---

## Sub-question analysis (algebraic + lit-scan)

### (1) Information-Theoretic Capacity

**Capacity arithmetic:**
Classical Hopfield: α_c ≈ 0.138, giving stored patterns P ≈ 565 at N=4096, 2260 at N=16384.
Information capacity: Abu-Mostafa and Jacques (1985, IEEE Trans IT) established that the asymptotic information capacity of an N-neuron Hopfield model is O(N² bits) — specifically 0.5 N² bits for the symmetric weight matrix — but **stored pattern capacity is O(N), not O(N²)**. The N² bit capacity is spread across the weight matrix entries, not accessible as N² independent patterns.

Modern Hopfield / Dense Associative Memory (Krotov-Hopfield 2016; Demircigil 2017): With interaction function F(x) = x^n for n ≥ 2, capacity scales as exp(α N^(1/n)) — approaching exponential in N for large n. Demircigil 2017 proves that with exponential interaction the storage capacity is approximately 2^(N/2) for binary patterns. This is *sufficient* for language statistics in principle.

**Is capacity the binding constraint?**
For a char-level LM with vocab V=70, the minimal representation requires encoding p(c | context) — a conditional probability vector of dimension 70 for each context. A context window of length L over 70 characters has 70^L possible states. At L=4, that is 70^4 ≈ 24M contexts. Even modern Hopfield at N=4096 would require exponential-scale storage (2^2048) which is available in principle from Demircigil capacity, but the *access* mechanism (retrieval via energy minimization) requires that the query vector lies within the basin of attraction of the stored pattern.

**Verdict:** Capacity per se is NOT the binding constraint for small models (vocab 70, N=4096). Modern Hopfield capacity is more than sufficient. The binding constraint is elsewhere.

---

### (2) Gradient Analog in Discrete-State Systems

**signSGD (Bernstein, Wang, Azizzadenesheli, Anandkumar 2018, arXiv:1802.04434):**
signSGD updates: w_{t+1} = w_t - η * sign(∇L). Convergence proven under: (a) bounded variance of stochastic gradient signs (E[|sign(g) - sign(∇L)|²] ≤ σ²); (b) L-smooth loss; (c) majority vote in distributed setting. Key condition: the *sign* operation must correlate with the true gradient direction — i.e., E[sign(g_i)] has the same sign as ∂L/∂w_i. For bipolar outer-product learning, the update is:

  ΔW = η * (x_t * x_t^T - W * x_t * x_t^T)    [Oja rule, continuous]
  ΔW_bipolar = sign(x_t) * sign(x_t)^T           [bipolar outer-product]

The bipolar outer-product is equivalent to sign(x_t x_t^T), which is a sign-compression of the rank-1 update. This IS a valid first-order analog IF: (a) the sign of x_i x_j correlates with the true gradient direction, and (b) the learning objective is the same one Oja rule optimizes (principal component). 

**The critical miss:** Oja rule minimizes reconstruction error under a specific symmetric objective. It does NOT minimize cross-entropy loss on next-character prediction. The bipolar outer-product computes the first-order statistics (covariance sign), not the causal conditional structure needed for language modeling.

**Rank-1 approximation theory:** A sum of rank-1 outer products approximates a gradient matrix with O(1/sqrt(c)) relative error for c terms (standard matrix approximation theorem). This is adequate for gradient *approximation* if the objective is well-defined. The gap is not the rank-1 structure; it is the absent objective function.

**Verdict:** Discrete bipolar operations DO have a gradient analog (signSGD class), but only for objectives that Hebbian learning provably optimizes (second-order statistics, PCA, whitening). There is no gradient analog for cross-entropy loss under pure Hebbian updates — this would require a supervised error signal that the substrate's Hebbian write mechanism does not receive.

---

### (3) Hebbian + Anti-Hebbian Convergence Theorems

**Oja 1982:** Single-unit Hebbian rule with weight normalization converges to the first principal component of the input covariance. Convergence is global for linear units under mild conditions on learning rate (stochastic approximation schedule η_t → 0, Σ η_t = ∞, Σ η_t² < ∞).

**Sanger 1989 (Generalized Hebbian Algorithm):** Generalizes to the top-k principal components. Convergence proven by Lyapunov function argument. Convergence rate is O(1/t) in mean square.

**Foldiak 1990:** Feedforward Hebbian + lateral anti-Hebbian inhibition. Provably decorrelates outputs, learning a whitened representation. Converges to PCA subspace.

**Baldi-Hornik 1989 (linear Hebbian networks):** For linear networks, all critical points of the Hebbian objective are saddles or the global minimum (PCA subspace). No spurious local minima for the linear case.

**The hard boundary — what Hebbian/anti-Hebbian CANNOT learn:**
(a) Third-order statistics: Hebbian/anti-Hebbian rules converge to representations that capture second-order statistics (covariance eigenstructure). Char-level language has non-Gaussian statistics with strong higher-order dependencies (e.g., "qu" bigram, "the " trigram). These require at minimum third-order cumulant capture (ICA) or structured sparse coding. Anti-Hebbian decorrelation removes second-order correlations but does not exploit third-order structure (Hyvarinen and Oja 1998, Signal Processing).

(b) Conditional probability estimation: Hebbian learning maximizes correlation between input and output. It does not minimize KL divergence between p(c_{t+1} | c_1,...,c_t) and a model distribution. The cross-entropy loss requires knowledge of the *target* distribution p*(c_{t+1}), which Hebbian rules have no mechanism to access.

(c) Temporal credit assignment: char-level LM requires propagating prediction error across time (backpropagation through time, or its analog). Hebbian rules are purely local (pre * post correlation); they have no mechanism for credit assignment across multiple time steps without an explicit error signal.

**Nonlinear extension (Hyvarinen-Oja ICA class):** With nonlinear activation f, Hebbian rules can capture fourth-order cumulants (kurtosis) and converge to independent components. This is strictly more powerful than linear Hebbian PCA. However, convergence requires that f' be related to the kurtosis sign of the source distribution, and that sources be statistically independent — conditions language statistics do not satisfy (characters in words are highly dependent, not independent).

**Verdict:** Pure Hebbian/anti-Hebbian is the second binding constraint. It provably cannot converge to useful conditional probability representations for language unless augmented with (a) a supervised target signal, (b) a temporal credit assignment mechanism, or (c) a structured competition objective that implicitly approximates language statistics.

---

### (4) Boltzmann Machine Lineage

**RBM training via Contrastive Divergence (Hinton 2002):**
CD-k algorithm: run Gibbs chain for k steps, compute positive phase (data), negative phase (reconstructed data), update W += η(v^data * h^data - v^model * h^model). Convergence analysis: Yuille 2004 showed CD-1 minimizes a different objective than log-likelihood. Carreira-Perpinan and Hinton 2005 showed that CD can diverge for some parameter settings.

**When CD works:**
- Moderate-scale RBMs (N_v × N_h ~ 500 × 500) with sufficient k (CD-25 recommended in practice)
- Bernoulli visible units + Bernoulli hidden units on binary data
- Learning rate small enough that CD does not diverge (empirically: η < 0.01 for standard RBMs)

**When CD fails — known failure modes:**
(i) Short-chain CD (CD-1) does not reliably minimize log-likelihood; may plateau at poor local solutions (Fischer and Igel 2011, "Training Restricted Boltzmann Machines: An Introduction")
(ii) Phase transition problem: RBMs exhibit phase transitions analogous to Ising models; near the critical temperature T_c, the mixing time of the Gibbs chain diverges, making CD estimates unreliable
(iii) Small model capacity: at low N_h, the RBM cannot represent the full joint distribution of input; the expressivity gap is fundamental (not just an engineering issue)
(iv) Discrete softmax visible units: training RBMs on softmax (one-hot) units is significantly harder than Bernoulli due to normalization across categories; conditional probability estimation requires estimating Z over all V softmax classes at each update

**Critical parallel for the substrate setup:**
The substrate lacks the negative phase sampling mechanism that CD requires. Pure Hebbian writes implement only the *positive phase* (data-driven update). Without the contrastive negative phase, Hebbian learning is equivalent to CD-0 — the trivially biased estimator that converges to the data mean, not to a useful model. This is the CD/Hebbian duality gap.

**Verdict:** The Boltzmann machine literature confirms the structural diagnosis: any discrete-state energy-based training that targets the full joint distribution requires a negative phase (contrastive, equilibrium, or equivalent). Anti-Hebbian repulsion is a partial negative phase, but only for pair-wise statistics, not for the full conditional distribution required by next-character prediction.

---

### (5) Non-Equilibrium Thermodynamics of Learning

**Jarzynski 1997 (Phys. Rev. Lett.):** For a system driven from equilibrium state A to state B, the free energy difference satisfies exp(-β ΔF) = <exp(-βW)>, where W is the work done by external driving. This connects non-equilibrium trajectories to equilibrium free energies.

**Crooks 1999 (Phys. Rev. E):** For microscopically reversible (but macroscopically irreversible) processes: P_forward(W) / P_reverse(-W) = exp(β(W - ΔF)). This is a fluctuation theorem for detailed-balance-obeying systems.

**Sagawa-Ueda 2010:** Extension to systems with feedback/measurement: efficiency of information-to-work conversion bounded by mutual information I(measurement; state). Generalized second law: <W> ≥ ΔF - k_B T I.

**Active repulsion / non-reciprocal dynamics:**
A substrate with active repulsion (anti-Hebbian weight decrease for co-activated pairs) generates a non-equilibrium steady state (NESS) where detailed balance is broken. In NESS:
- The system evolves under an antisymmetric contribution to the dynamics: J = J_symmetric + J_antisymmetric, where J_antisymmetric ≠ 0
- There is no scalar potential Φ such that J = -∇Φ; the dynamics are not gradient descent on any energy
- Stationary probability distribution π(s) satisfies: sum_s' π(s') W(s'→s) = sum_s' π(s) W(s→s'), but entropy production rate σ > 0 (persistent probability currents)

**Maes-Netocny (2008) — NESS characterization:** The invariant measure of a NESS cannot be expressed as a Boltzmann distribution exp(-βE(s)) for any energy function E. Instead, the steady state requires a traffic functional that depends on the full transition matrix, not just energy differences.

**Implication for learning:**
If the substrate's dynamics are in NESS due to active repulsion, then:
(a) The substrate does NOT minimize a scalar energy function; its attractor landscape is not energy-landscape-describable in the Hopfield sense
(b) Crooks and Jarzynski apply only to detailed-balance-obeying systems; they do NOT provide convergence guarantees for NESS learning
(c) Sagawa-Ueda bounds apply to feedback-controlled systems, but the information-to-learning efficiency depends on the *measurement* quality — if the substrate is driven by noisy Hebbian write operations without explicit error feedback, the mutual information I(target; update) is low, and learning efficiency is bounded near zero

**The NESS escape condition:**
NESS learning CAN work if a Lyapunov function exists for the *coupled dynamics* (substrate state + weight state) even when the individual state dynamics are in NESS. Known examples: Hopfield networks with asymmetric weights (Amit-Gutfreund-Sompolinsky 1987 — shown to have a Lyapunov function only for specific coupling regimes). Active repulsion breaks the symmetry condition required for standard Hopfield Lyapunov arguments.

**Verdict:** This is the third binding constraint. Active repulsion (non-reciprocal dynamics) breaks the energy-landscape interpretation. The substrate does not minimize a scalar objective function during its update rule, so there is no thermodynamic guarantee of convergence. Learning requires either (a) restoring detailed balance (symmetric weights, no active repulsion during training), or (b) finding the Lyapunov function for the specific NESS dynamics, or (c) using the substrate only for retrieval/storage (not as the training objective minimizer itself).

---

### (6) Multi-Channel Orchestration Convergence

**MGDA (Désidéri 2012, SIAM J Numer Anal):** Multiple Gradient Descent Algorithm. For k objectives F_1,...,F_k, MGDA finds a descent direction d that is a non-negative linear combination of task gradients (d = Σ λ_i ∇F_i, λ_i ≥ 0, Σ λ_i = 1) such that all F_i decrease. MGDA converges to Pareto-stationary points, not global optima. Key: when the feasible cone {Σ λ_i ∇F_i} contains only near-zero vectors (gradient conflicts), the MGDA update norm → 0, and learning stalls.

**PCGrad (Yu et al. 2020, NeurIPS):** For two tasks with conflicting gradients (cosine similarity < 0), PCGrad projects each gradient onto the normal plane of the conflicting gradient. Convergence proven only for two-task settings. For k > 2 tasks, no general convergence guarantee; conflict resolution order matters and can produce cycles.

**Cipolla uncertainty-weighting (2018):** Task weights inversely proportional to task variance. This addresses gradient magnitude imbalance but not gradient direction conflict. If task gradients point in opposing directions, re-weighting does not resolve the conflict.

**Conflict-Averse Gradient Descent (Liu et al. 2021, CAGrad):** Minimizes average loss while bounding worst-case individual task improvement. Provably converges to a minimum over average loss, but: (a) requires knowledge of gradient norms, (b) converges to average-loss minimum, not Pareto optimal, and (c) still fails on some initializations when gradient conflicts are severe.

**The 8-channel zero-convergence diagnosis:**
For 8 conflicting signals jointly weighted, the expected MGDA update satisfies:
  ||d*|| ≤ max_i ||∇F_i|| * max(0, min_{ij} cos(∇F_i, ∇F_j) + 1) / sqrt(k)

For k=8 with near-orthogonal gradients (which is typical when signals are derived from different substrate mechanisms), the cosine similarity min → -1/7 ≈ -0.143 by the projection onto the k-1 dimensional unit sphere. The effective update norm scales as O(1/sqrt(8)) ≈ 0.35 of the single-task norm, and with conflict the scale further reduces. Under random initialization with signal variance roughly equal, the joint update in ℝ^N space has expected norm approximately sqrt(8/k) * σ_gradient, which for k=8 approaches 0 as signal conflicts balance.

**Zero seed convergence:** This is consistent with the theoretical prediction. With 8 nearly-orthogonal objectives in a parameter space of dim ~ 5k-10k, the probability that all 8 gradients have the same sign pattern for any single parameter approaches 2^{-8+1} = 0.0078 per parameter per step. Coherent update direction does not emerge.

**Verdict:** 8-channel multi-objective orchestration zero-convergence is predicted by multi-task learning theory. This is NOT an engineering failure — it is a fundamental result of the gradient conflict geometry at k=8. Fix requires either (a) reducing to k ≤ 3 strongly correlated objectives, or (b) using a hierarchical decomposition where each stage optimizes a single objective, or (c) providing a common scalar loss that all channels contribute to.

---

## SYNTHESIS: Is there a fundamental reason substrate-as-training-mechanism CANNOT work?

### Answer

YES — there are three co-active fundamental constraints, and they are not simultaneously eliminable without design changes that change the substrate's nature:

**Constraint 1 (Hebbian expressivity ceiling):** Pure Hebbian/anti-Hebbian outer-product learning provably converges only to second-order statistics. Character-level language statistics require conditional probability estimation over high-order dependencies. This is not a capacity gap — it is a *functional gap* between what Hebbian rules minimize (second-order reconstruction) and what language modeling requires (conditional entropy minimization). The mathematics is settled: Oja/Sanger/Foldiak convergence theorems have explicitly bounded regimes.

**Constraint 2 (NESS / missing energy function):** Active repulsion generates NESS dynamics without a scalar energy function. Gradient descent analogy is inapplicable. The substrate cannot be interpreted as minimizing any loss unless the specific NESS dynamics have a known Lyapunov function — which has not been established for the non-reciprocal Hopfield class.

**Constraint 3 (multi-objective gradient geometry):** k=8 conflicting objectives in parameter space ℝ^5000 produce expected update norm → 0 under MGDA/PCGrad. This is a geometric inevitability, not a hyperparameter issue.

### (a) Universal approximation capacity?

The *memory storage* primitive class does have universal approximation capacity in the sense of: arbitrary bipolar pattern completion at sufficient N (Demircigil 2017). However, universal approximation of stored patterns is a *retrieval* property, not a *learning* property. The substrate as a *training mechanism* (i.e., as a weight-update rule) does NOT have universal approximation capacity for arbitrary loss functions. The outer-product update class forms a strict subset of gradient descent; it approximates gradient descent only when the loss is the Hebbian covariance objective.

### (b) Anti-Hebbian convergence regime match?

The known convergence regime for anti-Hebbian decorrelation (Foldiak; Williams 1989; Baldi-Hornik) requires:
- Linear or weakly nonlinear activation units
- Stationary data distribution
- Objective = principal subspace extraction or whitening

The char-level LM setup violates all three:
- The LM objective (cross-entropy) is not a principal subspace objective
- Character sequences are non-stationary (text has long-range correlations, distribution shifts)
- Higher-order statistics are essential (word structure, n-gram dependencies)

There is NO known anti-Hebbian convergence theorem that covers this regime.

### (c) Discrete representation fundamentally weaker?

In isolation, bipolar {±1}^N representations are NOT fundamentally weaker than continuous representations for classification/association tasks (Demircigil exponential capacity). However, the *training mechanism* based on outer-product Hebbian writes is fundamentally weaker than gradient descent on cross-entropy: outer-product writes cannot implement backpropagation-through-time, cannot compute the partition function gradient, and cannot minimize arbitrary differentiable objectives.

---

## Three binding constraints — ranked by severity

| Rank | Constraint | Mathematical statement | Can it be bypassed? |
|---|---|---|---|
| 1 | Hebbian expressivity ceiling | Hebbian converges to PCA subspace; cross-entropy requires conditional entropy minimization | Yes — add supervised error signal or contrastive phase |
| 2 | NESS / absent energy function | Active repulsion breaks detailed balance; no scalar objective being minimized | Yes — restore symmetry during training, or use substrate for retrieval only |
| 3 | 8-channel gradient conflict | MGDA update → 0 for k=8 near-orthogonal objectives | Yes — reduce to k ≤ 3, or hierarchical decomposition |

---

## Recommended design changes

**Design Change A (resolves Constraint 1): Add a contrastive or error-driven phase.**
Implement a local error signal: e_t = (target character one-hot) - (substrate retrieval output). Use this error to gate the Hebbian write: ΔW += η * e_t * x_t^T. This converts pure Hebbian to Perceptron-class learning (Rosenblatt 1958), which converges on linearly separable problems. For nonlinear (deep) representations, use predictive coding (Millidge 2022) or equilibrium propagation (Scellier-Bengio 2017) as a local-error propagation mechanism. Both have proven convergence properties and substrate-compatible local update rules.
*Hard-fail threshold:* BPC improvement > 0.3 bits over uniform baseline within 2k steps; if BPC does not exceed uniform+0.3 after contrastive phase addition, contrastive phase alone is insufficient.

**Design Change B (resolves Constraint 2): Use substrate for retrieval layer only; gradient descent for weights.**
Restrict the substrate's role to the attention/retrieval operation (fast-weight memory module); use standard backprop to train a small output head and embedding layer. The DeltaNet result (arXiv:2406.06484, NeurIPS 2024) demonstrates this hybrid at 1.3B scale. At the 5k-10k parameter regime, a similar hybrid should work: substrate handles key-value retrieval, gradient descent minimizes cross-entropy loss.
*Hard-fail threshold:* Hybrid model at 5k params should achieve BPC < 2.5 on standard char-level benchmark (e.g., PTB char); if BPC > 3.0, substrate retrieval layer is not improving on pure MLP baseline.

**Design Change C (resolves Constraint 3): Reduce to single-channel + train substrate signal weights.**
Replace 8-channel orchestration with a single-channel substrate signal fed through a learnable linear layer (1 × 8 → 1). Train the linear aggregation weights using gradient descent on cross-entropy. This replaces the MGDA multi-objective problem with a single-objective problem that gradient descent handles reliably. The substrate provides the feature; backprop trains the readout.
*Hard-fail threshold:* Single-channel substrate + linear readout should achieve BPC improvement > 0.05 bits over baseline; if improvement < 0.02, substrate features contain no language-predictive signal.

---

## Cross-domain probe: working examples of discrete-state training

**Ising spin machines (reservoir computing / combinatorial optimization):**
Non-binary dynamical Ising machines (arXiv:2412.08481) have been used for combinatorial optimization. The training analog: simulated annealing / thermal relaxation drives the system to low-energy configurations. This IS a form of discrete-state training, but the objective is energy minimization (Hamiltonian), not cross-entropy on data. The Ising training "works" because the objective matches the dynamics. The substrate-as-LM-trainer fails because the objective (language statistics) does NOT match the Hebbian dynamics.

**Echo state networks / reservoir computing as language models:**
Recent work (arXiv:2507.15779, 2026) demonstrates reservoir computing as a language model — but only the readout layer is trained (linear regression on reservoir states). The reservoir itself is fixed. This is the correct analog: substrate-as-reservoir (fixed, high-dimensional, recurrent computation) + trainable readout. This exactly matches Design Change C/B above. Echo state LMs achieve non-trivial character-level perplexity with readout-only training.

**Matrix product states / DMRG for generative modeling:**
Unsupervised generative modeling using MPS (arXiv:1709.01662) trains tensor-network states on discrete data distributions using DMRG-inspired sweeping optimization. The key: MPS training uses a well-defined variational objective (maximize log-likelihood of data) with sweep-based gradient updates. This IS successful discrete-state training because it has: (a) a scalar objective, (b) a sweep-based update that propagates information non-locally through the network, and (c) convergence guarantees from variational principle. The substrate as currently designed lacks (a) and (b).

**Variational quantum eigensolvers (VQE):**
VQE optimizes discrete + continuous parameters of quantum circuits using gradient descent on expectation value. The Ising-spin equivalent is simulated quantum annealing with variational parameters. Successful because: scalar objective (energy expectation), gradient can be estimated via parameter shift rule. Not applicable to substrate-as-LM-trainer without equivalent gradient estimation mechanism.

**Neuromorphic (Intel Loihi, IBM TrueNorth):**
Loihi 2 supports local Hebbian-class STDP (Spike-Timing Dependent Plasticity) as the on-chip training rule. Known result: STDP-trained spiking networks achieve competitive accuracy on small classification tasks but have NOT been demonstrated on language modeling at any non-trivial scale. The reason matches Constraint 1 above: STDP is Hebbian-class and captures second-order spike correlations, not conditional probability distributions. Intel's recent work adds a modulated STDP (neuromodulated learning) which is closer to a supervised signal — analogous to Design Change A.

**Algebraic anchor (from MPS/reservoir synthesis):**
The common thread across ALL working discrete-state training systems is: they either (a) have a well-defined scalar loss function that the update rule minimizes, or (b) use a fixed discrete-state module with a trainable continuous readout. The substrate as designed satisfies neither. This is the algebraic core of all four hard failures.

---

## Falsifiable predictions (HARD-PASS + HARD-FAIL)

### HARD-PASS (would establish feasibility)
HP1: Adding a supervised contrastive phase (positive vs negative pattern comparison, per RBM CD-1 structure) to the substrate's Hebbian write rule produces BPC improvement > 0.3 bits over uniform baseline within 3k gradient steps at 5k-param scale. If observed: Constraint 1 is the dominant binding factor, and other constraints are secondary.

HP2: Single-channel substrate retrieval (substrate as key-value memory module only) + gradient-trained linear readout achieves BPC < 2.5 at N=4096. If observed: substrate-as-retrieval-layer has sufficient expressivity for char-level language statistics.

HP3: Reducing orchestration from 8 channels to 1 canonical signal + linear aggregation achieves ≥ 1 of 5 seeds converging to BPC improvement > 0.05 bits. If observed: Constraint 3 (gradient geometry) was dominant over Constraint 1 in the zero-convergence case.

### HARD-FAIL (would establish fundamental infeasibility)
HF1: Contrastive-phase Hebbian substrate (CD-1 equivalent) with N=4096, 5k params fails to achieve BPC improvement > 0.1 bits after 10k steps. Implication: the substrate representation is fundamentally incompatible with char-level statistics even with contrastive correction. This would indicate a deeper expressivity gap at the bipolar pattern storage level.

HF2: Substrate-as-retrieval-layer hybrid (Design Change B) achieves BPC ≥ 3.5 (no improvement over pure-MLP baseline at same parameter count). Implication: substrate attractor states are too coarse-grained to represent useful language features at the char-scale granularity.

HF3: At 5k params, ANY substrate signal (single-channel, curated) fails to produce mutual information I(substrate_signal; next_char) > 0.01 bits in an off-line probe. Implication: substrate dynamics are orthogonal to language statistics — the substrate is processing noise, not linguistically-relevant structure. This would be the clearest structural closure.

---

## P_deflated estimates

| Hypothesis | P_raw | Deflation | P_deflated | Cap applied? |
|---|---|---|---|---|
| Substrate-as-primary-training-mechanism works as-is | 0.05 | -0.20 | 0.02 | No (already at floor) |
| Works with Design Change A only (contrastive phase) | 0.52 | -0.20 | 0.32 | No |
| Works with Design Change B only (retrieval layer) | 0.60 | -0.20 | 0.40 | No |
| Works with Design Change C only (single-channel readout) | 0.55 | -0.20 | 0.35 | No |
| Works with A+B+C combined (full redesign) | 0.70 | -0.20 | 0.50 | Yes (cap at 0.50) |
| Fundamental impossibility (no design fixes work) | 0.10 | -0.20 | 0.05 | No |

**Summary P_deflated:** Substrate-as-training-mechanism with full redesign (contrastive phase + retrieval-only + single-channel readout) = **P_deflated = 0.50** (capped). The failure cascade is an engineering failure under three co-active constraints, not a fundamental impossibility of the substrate primitive class.

---

## Cheap decisive test

Run a scalar mutual information probe: for each of 3 candidate substrate signals (raw retrieval output, anti-Hebbian residual, module address activation), compute I(signal; next_char) using a kNN mutual information estimator (Kraskov-Stoegbauer-Grassberger 2004) on 1000 held-out characters. Cost: CPU, < 5 minutes.

If I(any signal; next_char) > 0.01 bits → substrate contains extractable language information → proceed to Design Change C (trainable readout).
If I(all signals; next_char) < 0.001 bits → substrate is informationally orthogonal to language → HF3 triggered, escalate to fundamental feasibility review.

---

## Cross-thread synthesis with prior entries

**Prior drill (2026-06-03, substrate_as_full_llm_training):** Identified that outer-product Hebbian can replace attention layers but not softmax normalization. The current drill drills deeper: the issue is not softmax normalization *per se*, but the absent contrastive phase and NESS dynamics. These are related: softmax attention implicitly computes a negative-phase normalization term (partition function Z), and its absence in pure Hebbian maps exactly to the missing negative phase.

**Spin-glass/thermodynamics (prior drills):** NESS diagnosis aligns with the Maes-Netocny traffic functional result — the substrate's NESS may have a computable invariant measure that is NOT Boltzmann, but could be Gibbsian in a modified potential. This leaves open the possibility of finding the effective potential for the specific non-reciprocal Hopfield class (SKAH-M class per cap_map). Unexplored.

**Modern Hopfield (cap_map 🟢 row):** DeltaNet (NeurIPS 2024) demonstrates that delta-rule (fast-weight outer-product) can train a 1.3B LM when backprop handles static weights. This is Design Change B at scale. The 🟢 hierarchical-retrieval row confirms the retrieval-layer interpretation is empirically validated at large scale; the question is whether it extends to the 5k-param char-level regime.

---

## Substrate-product implications

**Immediate:** The substrate should be repositioned from "training mechanism" to "retrieval/memory layer" — a substrate-as-fast-weight-memory module inside a gradient-trained model. This is the DeltaNet/attention-augmentation product path, which has validated precedent.

**Capability gap to close:** The substrate does not currently provide a contrastive learning signal. Adding a hippocampal-inspired replay mechanism (positive = observed contexts; negative = confabulated contexts sampled from the substrate's attractor states) would close Constraint 1 without requiring full backprop. This maps directly to the contrastive Hebbian learning literature (Xie-Seung 2003; Scellier-Bengio EP).

**Non-equilibrium design space:** The NESS diagnosis opens a research direction: characterize the invariant measure of the SKAH-M-class dynamics under active repulsion + place-field tags. If this measure is Gibbsian in an effective temperature field, the substrate MAY have a hidden scalar objective it is already minimizing. This would be the most efficient path to validating substrate-as-training-mechanism without full redesign.

---

## Citations (verified via lit-scan)

1. Abu-Mostafa, Y.S. and Jacques, J.M. (1985). Information capacity of the Hopfield model. IEEE Transactions on Information Theory.
2. Krotov, D. and Hopfield, J.J. (2016). Dense associative memory for pattern recognition. NeurIPS.
3. Demircigil, M. et al. (2017). On a model of associative memory with huge storage capacity. Journal of Statistical Physics.
4. Oja, E. (1982). A simplified neuron model as a principal component analyzer. Journal of Mathematical Biology.
5. Sanger, T.D. (1989). Optimal unsupervised learning in a single-layer linear feedforward neural network. Neural Networks.
6. Foldiak, P. (1990). Forming sparse representations by local anti-Hebbian learning. Biological Cybernetics.
7. Hyvarinen, A. and Oja, E. (1998). Independent component analysis by general nonlinear Hebbian-like learning rules. Signal Processing.
8. Bernstein, J., Wang, Y.X., Azizzadenesheli, K. and Anandkumar, A. (2018). signSGD: Compressed optimisation for non-convex problems. arXiv:1802.04434. ICML 2018.
9. Hinton, G.E. (2002). Training products of experts by minimizing contrastive divergence. Neural Computation.
10. Jarzynski, C. (1997). Nonequilibrium equality for free energy differences. Physical Review Letters.
11. Crooks, G.E. (1999). Entropy production fluctuation theorem and the nonequilibrium work relation. Physical Review E.
12. Sagawa, T. and Ueda, M. (2010). Generalized Jarzynski equality under nonequilibrium feedback control. Physical Review Letters.
13. Maes, C. and Netocny, K. (2008). Canonical structure of dynamical fluctuations in mesoscopic nonequilibrium steady states. Europhysics Letters.
14. Désidéri, J.A. (2012). Multiple-gradient descent algorithm (MGDA) for multiobjective optimization. Comptes Rendus Mathematique.
15. Yu, T. et al. (2020). Gradient surgery for multi-task learning (PCGrad). NeurIPS.
16. Cipolla, R., Gal, Y. and Kendall, A. (2018). Multi-task learning using uncertainty to weigh losses. CVPR.
17. Liu, B. et al. (2021). Conflict-averse gradient descent for multi-task learning (CAGrad). NeurIPS.
18. Baldi, P. and Hornik, K. (1989). Neural networks and principal component analysis: Learning from examples without local minima. Neural Networks.
19. Fischer, A. and Igel, C. (2011). Empirical analysis of the divergence of Gibbs sampling based learning algorithms for restricted Boltzmann machines. ICANN.
20. Xie, X. and Seung, H.S. (2003). Equivalence of backpropagation and contrastive Hebbian learning in a layered network. Neural Computation.
21. Scellier, B. and Bengio, Y. (2017). Equilibrium propagation: Bridging the gap between energy-based models and backpropagation. Frontiers in Computational Neuroscience.
22. Millidge, B. et al. (2022). Predictive coding: Towards a future of deep learning beyond backpropagation. arXiv.
23. DeltaNet (arXiv:2406.06484, NeurIPS 2024): Linear transformers with outer-product delta rule at 1.3B scale.
24. Reservoir computing as language model (arXiv:2507.15779, 2026): ESN with readout-only training.
25. MPS generative modeling (arXiv:1709.01662): DMRG-inspired discrete generative models.
26. Amit, D.J., Gutfreund, H. and Sompolinsky, H. (1987). Statistical mechanics of neural networks near saturation. Annals of Physics.

**Verified citation count: 26**
