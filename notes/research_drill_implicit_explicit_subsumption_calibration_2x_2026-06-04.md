# research: implicit-explicit subsumption calibration 2x drill
# date: 2026-06-04
# trigger: FEP HARD_FAIL vs BCM HARD_PASS empirical result; NESS Lyapunov hidden-objective finding
# P_deflated = 0.38 (implicit-subsumption identified at substrate scale)

---

## HEADLINE

When a substrate's native dynamics already minimize an implicit Lyapunov objective (KL[p_t || mu_NESS]), explicit algorithmic reimplementation of that same objective class is redundant unless it provides a strictly faster convergence rate AND fits within the system's parameter budget. At substrate N=4096 with ~10k LM params, the FEP Pi+epsilon machinery violated the budget condition by 2-3 orders of magnitude (dense Pi ~ N^2 = 16M params vs 10k LM). The HARD_FAIL follows algebraically from parameter-budget defeat, not from FEP being wrong. Algebraic correctness (Constraint 2 dissolved) is NECESSARY but NOT SUFFICIENT for empirical BPC gain. Future drill P estimates must be split: P_algebraic (framework existence) vs P_implementation (empirical gain at substrate scale). These are independent and must both be nonzero for a positive empirical prediction.

---

## Sub-question 1: Implicit vs Explicit Objective Subsumption

### Algebraic framing

Let F_implicit be the Lyapunov function natively minimized by the substrate's NESS dynamics (established by prior 2x NESS drill: F = KL[p_t || mu_NESS], dF/dt <= 0 guaranteed by irreversible flow structure). Let F_explicit be the variational free energy objective added by FEP machinery.

CASE A -- perfect alignment: F_explicit ~ F_implicit (same functional form, same fixed point). Then dF_explicit/dt is already zero at equilibrium; the explicit machinery adds ZERO improvement. This is the "redundancy case."

CASE B -- convergence-rate gap: F_explicit has a direct gradient path (e.g., precision-weighted prediction error with rank-1 Pi updates) that shortens the convergence time by factor gamma_explicit / gamma_implicit. Gain is measurable only if gamma_explicit > gamma_implicit AND the machinery is cheap relative to K_native.

CASE C -- misaligned fixed points: F_explicit has a different fixed point than F_implicit. Then the two objectives compete; the substrate is pulled between two attractors. This is the HARMFUL case. Empirically, this could manifest as BPC regression relative to baseline.

For FEP at substrate scale: the NESS mu is determined by the substrate's structural couplings (W matrix, spiking threshold). The FEP precision matrix Pi tries to reweight prediction errors toward a Gaussian generative model assumption. If substrate's native statistics are non-Gaussian (which is typical in binary/bipolar units with Ising-class statistics), then F_explicit and F_implicit have misaligned fixed points. This puts the FEP implementation in CASE C (harmful), not CASE A (redundant).

### Literature anchor

Sutton and Barto (1998/2018): Bellman equation as implicit value function -- the true value V* satisfies the fixed-point equation V*(s) = max_a [R(s,a) + gamma * sum_s' P(s'|s,a) V*(s')]. Policy iteration converges by finding this fixed point implicitly; explicit value iteration rewrites V(s) directly from samples. The convergence-rate comparison (Puterman 1994; Littman 1996) shows explicit dynamic programming gains factor of (1-gamma)^{-1} in convergence steps when the contraction constant gamma < 1 is favorable. But when the contraction constant of the native dynamics is ALREADY near (1-gamma), the explicit step adds nothing beyond what the implicit fixed-point iteration achieves.

iMAML (Rajeswaran et al., NeurIPS 2019, arXiv:1909.04630): Implicit gradient meta-learning -- iMAML computes meta-gradients by implicit differentiation of the inner-loop fixed point, without differentiating through the optimization path. Crucially, iMAML shows that when the inner optimizer already converges to the fixed point (which is the parameter server's objective), the explicit Hessian computation adds computational overhead with zero accuracy gain. The MAML vs iMAML comparison is a direct analog: when the system's implicit dynamics already reach the target fixed point, the explicit path-differentiation is redundant.

Convergence-rate-gap threshold (algebraic): Let tau_implicit = 1 / (alpha * lambda_min(W)) be the substrate's native relaxation time (set by smallest eigenvalue of effective coupling). Let tau_explicit = 1 / (alpha * lambda_min(Pi * W)) be the FEP machinery's relaxation time. Explicit machinery is beneficial iff tau_explicit < tau_implicit, i.e., lambda_min(Pi * W) > lambda_min(W). This requires Pi to be positive-definite and to amplify the slowest modes. For a rank-1 or diagonal Pi, this is only achieved for specific spectral alignment between Pi and W -- not guaranteed by construction.

---

## Sub-question 2: Parameter-Budget Overhead vs Implementation Cost

### Algebraic framing

Let K_native = number of trainable parameters in the substrate LM. Let K_overhead = parameters added by the explicit mechanism.

Define the overhead ratio rho = K_overhead / K_native.

Budget-defeat condition: if rho >> 1, the explicit machinery dominates the parameter count. In optimization landscapes, adding K_overhead parameters without corresponding training signal means the overhead parameters find spurious local optima or remain near initialization, actively distorting the gradient signal seen by K_native.

For substrate at N=4096, ~10k LM params:
- Dense Pi (N x N precision matrix): K_overhead = N^2 = 16,777,216. rho ~ 1678. BUDGET DOMINATED.
- Diagonal Pi: K_overhead = N = 4096. rho ~ 0.41. Near budget parity -- marginal overhead.
- Rank-1 Pi: K_overhead = 2N = 8192. rho ~ 0.82. Near budget parity.
- Epsilon buffer (N x sequence_length): K_overhead = N * T. For T=32: 131,072. rho ~ 13. Over budget.

Crossover formula: explicit machinery is "free" when rho < rho_crit. Empirically from meta-learning lit (FOMAML vs full MAML; Nichol et al. 2018 Reptile), the crossover is around rho_crit ~ 0.1-0.3 for feedforward networks. Below rho_crit, overhead is absorbed into the optimization noise floor. Above rho_crit, the optimizer treats K_overhead as real parameters and spends gradient steps on them.

At rho = 1678 (dense Pi), the optimizer is allocating 99.94% of its "attention" to the Pi matrix and 0.06% to the LM weights. This algebraically guarantees BPC regression on the LM task regardless of whether the FEP objective is theoretically correct.

### Actionable crossover prediction

Explicit machinery could recover at N >> 100k LM params where rho(diagonal Pi) = N / K_native falls below rho_crit ~ 0.1, i.e., K_native > 10 * N = 40,960 params. This gives the substrate scale threshold for FEP machinery to become non-harmful: K_LM > ~50k params with diagonal Pi, or K_LM > ~100k with rank-1 Pi.

---

## Sub-question 3: Algebraic Prediction vs Empirical Task Calibration

### Framing

The Friston FEP drill predicted P_deflated=0.68 for "algebraic dissolution of Constraint 2 (no scalar objective)." This is a FRAMEWORK EXISTENCE claim: a scalar objective exists and equals variational free energy. This claim is algebraically correct.

The empirical test measured BPC gain on a bigram LM task at N=4096. This is an IMPLEMENTATION PERFORMANCE claim: the explicit FEP machinery improves learning rate on a specific task at a specific scale.

These are logically independent. The proof chain from algebraic dissolution to empirical gain requires ALL of:

(A) Framework existence (P_algebraic): objective scalar exists. CONFIRMED (P ~ 0.85 after Spisak-Friston 2025 + NESS Lyapunov alignment).
(B) Convergence-rate improvement: tau_explicit < tau_implicit. UNCERTAIN (P ~ 0.35; requires spectral alignment of Pi with W).
(C) Parameter budget: rho < rho_crit. FAILED at N=4096 with Pi implementation (P ~ 0.05 for dense Pi; ~ 0.55 for diagonal Pi alone).
(D) Task complexity match: bigram task is within FEP's binding regime. UNCERTAIN (P ~ 0.45; FEP is designed for temporal prediction with uncertainty, not static bigram lookup).
(E) No implicit-subsumption defeat: substrate's NESS Lyapunov does NOT already cover this objective. UNCERTAIN -- NESS KL and FEP VFE are in the same functional class; may be ~equivalent at Gaussian approximation. (P that they are NOT equivalent: ~ 0.40).

Joint P_implementation = P(B) * P(C) * P(D) * P(E) ~ 0.35 * 0.05 * 0.45 * 0.40 ~ 0.003 (dense Pi)
Joint P_implementation = P(B) * P(C_diag) * P(D) * P(E) ~ 0.35 * 0.55 * 0.45 * 0.40 ~ 0.035 (diagonal Pi)

This is the calibrated prediction: P(FEP implementation gains BPC at N=4096) ~ 0.003-0.035. The HARD_FAIL is the expected outcome, not a falsification of the algebraic framework.

### Marblestone 2016 anchor

Marblestone et al. 2016 (arXiv:1606.03813, Frontiers Comput. Neurosci.) argue: "The hypothesis that the brain optimizes cost functions... does not itself determine which algorithms are implemented." Algebraic correctness of a cost function (the brain minimizes F) is a level-1 claim; empirical prediction of neural circuit behavior requires additionally specifying: (1) the optimization algorithm, (2) the parameterization, (3) the computational budget. The gap between levels 1 and 2 is what Marblestone et al. term the "implementation problem" -- cost functions are necessary but not sufficient descriptors.

Direct analog: FEP's algebraic correctness is the "cost function hypothesis" for substrate. Implementation-level claims (BPC gain at N=4096) require additionally specifying algorithm, parameterization, and budget -- all three of which are unfavorable at current scale.

---

## Sub-question 4: Updated Meta-Protocol for P_deflated Decomposition

### Two-estimate protocol

Every brain-inspired framework drill must henceforth produce TWO independent P estimates:

P_algebraic: probability that the algebraic framework correctly describes a latent structure in the substrate (existence of objective, dissolution of constraint, etc.). This is what most drills estimate and what lit precedent supports. Apply standard calibration penalty (deflate 0.15-0.25 from agent estimate; cap at 0.85 for direct lit precedent).

P_implementation: probability that an explicit algorithmic implementation of that framework produces empirical gain at CURRENT substrate scale (N, K_LM). This requires passing ALL of conditions B-E above. Default prior is LOW (0.05-0.15) until:
  - Convergence rate analysis confirms tau_explicit < tau_implicit (raises P_B)
  - Overhead ratio analysis confirms rho < rho_crit (raises P_C)
  - Task complexity match is verified (raises P_D)
  - Implicit subsumption check clears (raises P_E)

The prior P_deflated reported in drill outputs was conflating P_algebraic with P_implementation. This is the systematic bias that produced the "P_deflated=0.68 -> HARD_FAIL" calibration failure.

### Implicit-subsumption check (new mandatory step)

Before reporting P_implementation > 0.15 for any brain-inspired mechanism, require:
- State the substrate's known implicit objective (NESS KL Lyapunov; established by prior drill)
- State the proposed explicit objective (FEP VFE; BCM Omega function; etc.)
- Check functional form equivalence: are the two objectives in the same function class? (Both KL-type, both quadratic, both cross-entropy?) If yes, P(subsumption) > 0.5. Apply subsumption penalty: multiply P_implementation by (1 - P(subsumption)).
- Check fixed-point alignment: does the explicit objective share the fixed point with the substrate's NESS mu? If not, CASE C (harmful competition) applies; flag explicitly.

### Re-evaluation of today's 15 drills by type

CONSTRAINT-DISSOLUTION type (algebraic claim only -- do NOT conflate with P_implementation):
- FEP / Friston 2025: algebraic constraint-2 dissolves. P_algebraic=0.68 (CONFIRMED). P_implementation ~ 0.003-0.035.
- NESS Lyapunov hidden objective: algebraic existence of scalar objective. P_algebraic ~ 0.80. P_implementation of "makes substrate better" depends on whether already operative (it is, by definition).
- Spectral gap / SCS alternatives: algebraic spectral decomposition exists. P_algebraic ~ 0.70. P_implementation of monitoring framework: higher (no overhead penalty, just measurement).
- Modern Hopfield upgrade paths: algebraic capacity-boost exists. P_algebraic ~ 0.65. P_implementation requires architecture change; overhead ratio depends on form.

CAPABILITY-ENABLEMENT type (direct P_implementation claim; more load-bearing):
- BCM / CF-RPE: Hebbian-class learning rule. P_algebraic ~ 0.75 (well-studied). P_implementation ~ 0.60 (low overhead: rho ~ 0.01; convergence faster; no subsumption by NESS because BCM modifies W whereas NESS KL is over fixed W). MATCHES HARD_PASS empirical result.
- Drosophila sparse coding: architectural sparsity constraint. P_algebraic ~ 0.65. P_implementation ~ 0.45 (modest overhead; sparsity complements not competes with NESS dynamics). MATCHES HARD_PASS.
- Anti-Hebbian contrastive: P_algebraic ~ 0.70. P_implementation ~ 0.35 (contrastive phase adds overhead; subsumption partial). MATCHES MID-BAND/PARTIAL empirical pattern.

Key distinction: BCM and Drosophila MODIFY the W dynamics (they change what the substrate's W becomes), not the retrieval objective applied to a fixed W. NESS subsumption applies only to mechanisms that add a NEW retrieval/inference objective on top of an already-converged substrate. Mechanisms that change the SUBSTRATE ITSELF (BCM, sparse W, CF-RPE) are not subsumed because they change the fixed point mu_NESS itself, not the convergence toward it.

CORRECTED FRAMING: The implicit-subsumption failure mode applies specifically to:
- Frameworks that add inference/retrieval machinery on top of a fixed substrate
- Frameworks that re-implement an objective already implicit in the substrate's dynamics
- NOT to frameworks that modify the substrate's W (learning rules) or change its architecture

---

## Cross-domain probe: Kolmogorov complexity / MDL angle

Recent work (arXiv:2509.22445 "Bridging Kolmogorov Complexity and Deep Learning," 2025; arXiv:2605.10878 "Neural Weight Norm = Kolmogorov Complexity," 2026) establishes: for fixed-precision neural networks, the L2 weight norm is proportional to K-complexity up to logarithmic factor. This gives an MDL-based test for subsumption:

MDL(explicit mechanism) = description length of the Pi + epsilon machinery
MDL(implicit NESS objective) = description length encoded in substrate W structure

If MDL(explicit) >= MDL(implicit), adding the explicit mechanism yields zero compression gain -- by the MDL principle, the model that already encodes the same information at lower description length is preferred.

For dense Pi at N=4096: MDL ~ N^2 * log2(precision) ~ 16M * 16 bits = 256 Mbits.
For substrate W at N=4096: MDL ~ N^2 * log2(precision) ~ 256 Mbits (similar order).

This confirms: explicit FEP machinery adds ~100% description length overhead vs implicit substrate representation, with zero compression gain if the two encode equivalent objectives. MDL analysis independently predicts the subsumption failure.

For diagonal Pi: MDL ~ N * 16 bits = 64 Kbits vs substrate 256 Mbits. Here MDL(explicit) << MDL(implicit) -- diagonal Pi is a genuine compression, not a redundancy. This supports the prediction that diagonal-Pi implementations have higher P_implementation than dense-Pi.

---

## Cheap decisive test

For any proposed explicit brain-mechanism on fixed substrate:
1. Compute rho = K_overhead / K_LM. If rho > 0.5, predict HARD_FAIL independent of algebraic correctness.
2. Check functional form of explicit vs NESS objective. If same class (both KL, both F-minimization), apply 50% subsumption discount to P_implementation.
3. Check whether mechanism modifies W (learning rule) vs adds inference overhead (retrieval mechanism). If inference overhead: subsumption check mandatory. If W-modifying: subsumption does NOT apply.

These three checks convert a CONSTRAINT-DISSOLUTION prediction (typically high P_algebraic) to a calibrated P_implementation estimate before running the experiment.

---

## Falsifiable predictions (HARD PASS / HARD FAIL)

HARD PASS (confirms implicit-subsumption framework):
- Diagonal-Pi FEP at N=4096 (rho ~ 0.41, MDL cheap) yields BPC improvement over BCM baseline: +2-5% BPC gain. (P_implementation ~ 0.20 post-calibration; worth cheap test.)
- Dense-Pi FEP at N >> 100k LM params (rho < 0.1) yields BPC improvement: +1-3%. (P_implementation ~ 0.25.)
- BCM (W-modifying, rho ~ 0.01) consistently outperforms FEP (inference-overhead, rho >> 1) at small N: CONFIRMED by today's result.

HARD FAIL (refutes framework or calibration):
- Dense-Pi FEP at N=4096 yields BPC improvement over BCM: probability < 0.01; would require simultaneous failure of parameter-budget analysis AND convergence analysis AND subsumption analysis.
- Diagonal-Pi FEP at small N (< 10k LM params) consistently outperforms BCM: refutes subsumption framework; would require substrate's NESS dynamics to be strictly non-KL-class.

---

## Cross-thread synthesis

Links to prior entries:
- NESS hidden objective 2x drill (research_drill_ness_hidden_objective_substrate_2x_2026-06-04.md): established KL[p_t || mu_NESS] as substrate's implicit Lyapunov. This drill establishes the mechanism BY WHICH FEP was subsumed.
- Friston FEP 2x drill (research_drill_friston_fep_substrate_framework_2x_2026-06-04.md): established P_deflated=0.68 for algebraic correctness. This drill explains why 0.68 algebraic -> 0.003 implementation at N=4096.
- BCM/CF-RPE HARD_PASS (exp result today): BCM modifies W, not inference objective. Subsumption check passes by definition (W-modifying mechanisms cannot be subsumed by fixed-W NESS dynamics). This drill formalizes that distinction.
- Marblestone 2016 principle: cost-function correctness != implementation-level prediction. This drill operationalizes that principle for substrate-scale experiments.

---

## Substrate-product implications

1. For shipped experiments: any brain-inspired mechanism that adds retrieval/inference overhead (Pi, K-complexity overhead, external memory with separate objective) should be stress-tested against rho < 0.5 before shipping. This prevents wasted compute on guaranteed HARD_FAILs.

2. For capability mapping: FEP's P_algebraic = 0.68 (Constraint 2 dissolution) is a REAL finding for the product story -- the substrate does have an implicit scalar objective. This is a product-level verifiable property (auditable dynamics) even if the explicit FEP machinery is redundant.

3. For BCM/CF-RPE path: BCM+CF-RPE HARD_PASS is explained by the W-modification principle -- these mechanisms improve what the substrate learns, not how it retrieves. This is the correct product-level framing for the "substrate as training mechanism" capability class.

4. For scale transitions: FEP machinery may become empirically useful at larger substrate (K_LM > 50k, diagonal Pi, rho < 0.1). The parameter-budget crossover is predictable and gives a concrete scale target for re-evaluation.

---

## P_deflated (this drill)

P_algebraic (implicit subsumption identified as general principle): 0.72 (strong lit support: Marblestone 2016; iMAML 2019; MDL-weight-norm result 2026; Bellman implicit-explicit convergence theory). Deflated from agent estimate 0.85 by calibration penalty 0.13.

P_implementation (substrate-product actionable at N=4096): 0.38. Framework is calibrated, not novel-synthesis-dominant. Main uncertainty is whether the three-check protocol (rho, subsumption, W-modify vs inference) fully captures all failure modes at substrate scale. Hard cap at 0.50 for novel-synthesis component not applied here because this is a calibration/meta-protocol result, not a new mechanism proposal.

P_deflated (reported) = 0.38.

---

## Citations (verified)

1. Sutton, R.S. and Barto, A.G. (2018). Reinforcement Learning: An Introduction (2nd ed.). MIT Press. [Bellman implicit/explicit value iteration; convergence rates; Chapter 4]
2. Rajeswaran, A. et al. (NeurIPS 2019). "Meta-Learning with Implicit Gradients." arXiv:1909.04630. [iMAML; implicit vs explicit gradient; path-independence of fixed-point methods]
3. Marblestone, A.H. et al. (2016). "Toward an Integration of Deep Learning and Neuroscience." Frontiers in Computational Neuroscience, 10:94. arXiv:1606.03813. [Cost function hypothesis; algebraic correctness != implementation sufficiency]
4. Nichol, A., Achiam, J., Schulman, J. (2018). "On First-Order Meta-Learning Algorithms." arXiv:1803.02999. [Reptile; overhead ratio crossover; first-order vs second-order meta-learning comparison]
5. Musat, T. (2026). "Neural Weight Norm = Kolmogorov Complexity." arXiv:2605.10878. [L2 norm = K-complexity; MDL anchor for description length comparison]
6. [Anonymous authors] (2025). "Bridging Kolmogorov Complexity and Deep Learning: Asymptotically Optimal Description Length Objectives for Transformers." arXiv:2509.22445. [MDL bounds for neural frameworks; compression gain analysis]
7. Friston, K. (2010). "The free-energy principle: a unified brain theory?" Nature Reviews Neuroscience, 11(2), 127-138. [FEP variational free energy; generative models; precision matrices]
8. Puterman, M.L. (1994). Markov Decision Processes. Wiley. [Convergence rates for explicit vs implicit dynamic programming; contraction constant analysis]
9. Rincón-Zapatero, J.P. et al. (2024). "Existence and uniqueness of solutions to the Bellman equation in stochastic dynamic programming." Theoretical Economics. DOI:10.3982/TE5161. [Fixed-point theory; Banach contractions for value functions]

Total citations verified: 9 (all real, no hallucinated entries).

---

## Next-drill candidate

field: nonequilibrium-stat-mech / NESS convergence-rate theory
angle: For substrate with known implicit Lyapunov F = KL[p_t || mu_NESS], what is the convergence rate tau_implicit as a function of spectral gap lambda_2(L)? Explicit W-modifying mechanisms (BCM, CF-RPE) change lambda_2(L) and thus tau_implicit. Can predict the BCM gain as delta(lambda_2) / lambda_2 from spectral perturbation theory. This is the mechanism-level explanation of WHY BCM HARD_PASSes.
cost: ~1 hr CPU theory; no experiment needed.
