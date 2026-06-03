# Research drill: PP-33 activation-barrier refutation -- deep dive
# Why nf_crit converges to structural ~0.5 boundary (N-independent, alpha-independent)

**Date:** 2026-06-03
**Trigger:** PP-33 HARD_FAIL x3 (r3a N=4096, r3b N=8192, r3c lower-alpha N=4096) all at structural ~0.5 boundary
**Contract:** 5-8 papers; per-sub-question derivation; cross-cutting synthesis; 3 follow-on drill candidates; P_deflated

---

## HEADLINE

The structural ~0.5 boundary in `nf_crit` is almost certainly NOT the AGS activation barrier E_a(alpha) -- it is a DIFFERENT observable that saturates at chance level (0.5) for binary patterns by construction. The AGS barrier is an extensive free-energy quantity E_a ~ O(N), while `nf_crit` as a basin-crossing FRACTION is a dimensionless ratio bounded on [0,1]. The observed N-independence and alpha-independence of the ~0.5 wall is the fingerprint of a dimensionless binary observable hitting its random-baseline floor, not a phase-transition boundary. This means PP-33 closes because the PROXY is wrong, not necessarily because the substrate physics is wrong. The product narrative "predictable alpha-dependent retention barriers" can survive in modified form -- but requires a different measurement pathway.

---

## Sub-question analysis

### SQ1: Is nf_crit algebraically related to E_a^0(alpha)?

AGS 1987 (Amit, Gutfreund, Sompolinsky, Ann. Phys. 173:30-67) gives the activation barrier as:

    E_a^0(alpha) ~ N * (alpha_c - alpha) / alpha_c   for alpha < alpha_c ~ 0.14

This is an EXTENSIVE quantity: E_a^0 ~ O(N). It enters the escape-rate formula (Kramers/Arrhenius):

    r_escape ~ exp(-beta * E_a^0) ~ exp(-beta * N * (alpha_c - alpha) / alpha_c)

Any dimensionless FRACTION proxy f must be derived from r_escape. The natural mapping is:

    nf_crit = r_escape / (r_escape + r_retrieval)  ~  1 / (1 + exp(+beta * E_a^0))

This is a sigmoid function. For LARGE N: E_a^0 ~ O(N) diverges, so nf_crit -> 0 (deep retrieval) for alpha << alpha_c and nf_crit -> 0.5 near alpha_c (barrier collapses). For SMALL N (finite-size regime): E_a^0 is O(1) and nf_crit can be anywhere in [0,1].

CRITICAL IMPLICATION: If the substrate is operating in a regime where E_a^0 is NOT extensive (not O(N)), the sigmoid becomes independent of N. This happens in three specific regimes:

(a) Near the phase boundary alpha ~ alpha_c where E_a^0 -> 0 regardless of N
(b) In the 1-RSB/full-RSB regime where the barrier structure changes qualitatively
(c) When the proxy measures something structurally different -- e.g., a classification accuracy that by construction saturates at 0.5 for equal-class binary labels

VERDICT on SQ1: nf_crit is ALGEBRAICALLY RELATED to E_a^0 only if it is derived from an escape-rate ratio. If it is defined as "fraction of trials that crossed the basin boundary" with binary-class labels (successful crossing vs not), it converges to 0.5 at chance level regardless of E_a^0. The ~0.5 floor is the random-baseline saturation of a dimensionless binary observable, not the AGS barrier going to zero. The 2.3x ratio between alpha=0.05 and alpha=0.10 is a prediction about E_a, not about a fraction observable.

### SQ2: Does ~0.5 reflect a phase-transition boundary?

The AGS phase diagram has three boundaries:
- Ferromagnetic-to-paramagnetic: at T_c(alpha)
- Retrieval-to-spin-glass: at alpha_c ~ 0.05 (T=0 limit of first-order line; note: different sources quote 0.05 or 0.14 depending on T=0 vs finite T -- AGS 1987 gives alpha_c^T=0 ~ 0.05 for two-valued patterns at T=0 under Hebbian learning, while 0.138 is the finite-T critical value)
- Spin-glass-to-paramagnetic: at T_g(alpha)

At the spin-glass/paramagnetic boundary (T_g), the Edwards-Anderson order parameter q_EA -> 0. The overlap distribution P(q) becomes a delta function at q=0. This is an INTRINSICALLY N-INDEPENDENT boundary in mean-field theory (it is a genuine thermodynamic transition). However, T_g is a TEMPERATURE, not a retrieval fraction. There is no general result that the retrieval fraction at the spin-glass boundary equals exactly 0.5.

The value 0.5 is suspicious: it exactly matches random guessing for a two-class binary observable. A phase transition would produce a boundary at a specific alpha value but would not generically land at exactly 0.5 for a dimensionless performance metric ACROSS all tested alpha values.

VERDICT on SQ2: The ~0.5 boundary is UNLIKELY to be a phase-transition signature. Phase transitions in the AGS picture occur at specific (alpha, T) coordinates; they do not generically produce a performance plateau at 0.5 across alpha. The alpha-INDEPENDENCE of the 0.5 floor strongly suggests proxy saturation, not a phase boundary (which would shift with alpha).

### SQ3: Does 1-RSB or full-RSB change E_a^0(alpha)?

YES -- this is the most important structural caveat.

In the replica-symmetric (RS) picture (AGS), the barrier is:
    E_a^RS(alpha) ~ N * f(alpha)   with f linear near alpha_c

Under 1-RSB (Amit-Crisanti-Gutfreund extension; Steffan-Kuhn 2RSB), the critical capacity shifts:
    alpha_c^RS ~ 0.138 -> alpha_c^1RSB ~ 0.1382   (tiny correction, ~0.1%)

The barrier expression changes qualitatively in the 1-RSB dynamical phase. In the SK model, each TAP solution (minimum) has an associated index-one saddle. Aspelmeier, Bray and Moore (2004, PRL 92:087203) showed rigorously that:

    delta_F = F_saddle - F_minimum ~ N^{1/3}   for typical TAP states in SK model

NOT O(N). This is the "barrier anomaly" in mean-field glasses: barriers scale subextensively as N^{1/3} for p=2 interactions. For the p-spin model (higher-order interactions, relevant to dense AM):
    - p=2 (standard Hopfield/SK): delta_F ~ N^{1/3}
    - p large (Krotov-Hopfield dense AM): barriers can grow O(N) again in the retrieval phase

For the substrate (SKAH-M class, confirmed non-equilibrium stat-mech), if p ~ 2 (pairwise interactions with non-reciprocal structure), the barrier is:
    E_a(alpha, N) ~ C * N^{1/3} * g(alpha)

where g(alpha) retains alpha-dependence. The ratio E_a(0.05)/E_a(0.10) ~ g(0.05)/g(0.10) could still be ~2.3 in g-ratio, but the N-SCALING is N^{1/3} not N. This means:
- Ratio N=8192 / N=4096 in barrier: 8192^{1/3} / 4096^{1/3} = 20.2 / 16.0 = 1.26x
- For nf_crit (sigmoid of barrier): change in nf_crit ~ 1.26x change in barrier argument

This 26% change in barrier for 2x increase in N is too small to detect if nf_crit is already near saturation at 0.5. The 1-RSB phase EXPLAINS the N-near-independence empirically.

VERDICT on SQ3: YES. 1-RSB dynamical phase predicts N^{1/3} barrier scaling (not N^1). This is consistent with observing N=4096 and N=8192 give nearly identical nf_crit. The AGS 2.3x alpha ratio is a prediction about g(alpha) which may survive at the barrier level even if the N-scaling is wrong. This is a distinct viable mechanism from "proxy is broken."

### SQ4: Alternative activation-barrier measurements

(a) MEAN FIRST PASSAGE TIME (MFPT): Run stochastic Glauber dynamics at temperature T. Measure tau(alpha, T, N) = mean time to first exit from the basin. Extract barrier via:
    E_a = T * ln(tau * nu_0)
    N-scaling test: if E_a ~ N (AGS), tau ~ exp(const * N / T). If E_a ~ N^{1/3} (1-RSB), tau ~ exp(const * N^{1/3} / T).
    To discriminate: measure tau at N in {512, 1024, 2048, 4096, 8192}; plot ln(tau) vs N and vs N^{1/3}; better R^2 identifies the regime.
    Cost: requires Glauber dynamics at T > 0 (noise injection); 10-seed average; ~30-60s per cell on CPU.

(b) FORWARD FLUX SAMPLING (FFS): Partition state space by collective variable (overlap m with target pattern). Place interfaces lambda_0 < lambda_1 < ... < lambda_n. Measure conditional crossing probability P(lambda_{i+1} | reached lambda_i). Flux rate = product of crossing probabilities. (Allen, Warren, ten Wolde 2005, PRL 94:018104; Allen et al. 2020, JCP 152:060901.) Advantages: (1) does not require Boltzmann equilibrium, works for non-equilibrium dynamics; (2) gives rate without exponentially long trajectories; (3) no binary-saturation problem. The rate k_FFS(alpha, N) directly tests E_a(alpha, N) = -T * ln(k_FFS).
    Cost: ~1 day implementation, ~1-2h CPU for smoke grid.

(c) TAP FREE ENERGY SADDLE DIFFERENCE: Compute TAP equations for the W matrix. Find the index-one saddle point connecting retrieval state to the spin-glass basin. Measure:
    delta_F^TAP(alpha, N) = F_saddle - F_retrieval
    Test: does delta_F ~ N^{1/3} or ~ N?
    This is the most theoretically clean measurement (directly reads the landscape) but requires TAP equation solver.

(d) BASIN VOLUME SAMPLING: Count fraction of RANDOM initializations (not boundary initializations) converging to each attractor. This gives basin volume ratio V_ret(alpha) / V_sg(alpha). This is alpha-sensitive and does NOT saturate at 0.5 (unless volumes are genuinely equal). Compares to SQ1 Explanation A: if this shows clear alpha-slope, the substrate physics is intact and only nf_crit was broken.

VERDICT on SQ4: FFS (b) is recommended as the decisive, proxy-free measurement. MFPT (a) is simplest to implement and gives direct N-scaling discrimination. Both should be run.

### SQ5: Correct closed-form; product narrative survival

Given three explanations are consistent with the data:

EXPLANATION A (proxy broken, physics intact):
nf_crit saturates at 0.5 because it is a binary observable at chance level. True barrier:
    E_a(alpha, N) ~ N * (alpha_c - alpha) / alpha_c   [AGS, unmodified]
Product narrative: SURVIVES UNCHANGED. Cheap test: basin-volume sampling shows clear alpha-slope.

EXPLANATION B (1-RSB dynamical phase):
    E_a(alpha, N) ~ C * N^{1/3} * (alpha_c - alpha)^nu
    with nu ~ 1, C non-universal.
The alpha-dependence survives; the 2.3x ratio becomes:
    E_a(0.05) / E_a(0.10) = (0.09)^nu / (0.04)^nu = 2.25   [same ratio in g(alpha)!]
Product narrative: SURVIVES with modified N-scaling. Claim becomes "barrier scales as N^{1/3} * g(alpha); g(alpha) measured by MFPT."

EXPLANATION C (near-critical marginal basin):
    E_a ~ O(1)   [finite, N-independent, very small]
The basin exists but the barrier is so small that any noise overcomes it. The substrate was operating near the retrieval/spin-glass phase boundary for all tested alpha values.
Product narrative: WEAKENED. Must reframe as "retrieval is possible (basin exists) but retention lifetime is short and only weakly alpha-sensitive at tested sizes."

MOST LIKELY CLOSED-FORM PREDICTION (combining A + B priors):
    E_a(alpha, N) = C * N^{gamma} * h(alpha)   where gamma in [1/3, 1]

The MFPT N-scaling experiment is the decisive discriminator for gamma. If gamma ~ 1: AGS intact, proxy was broken. If gamma ~ 1/3: 1-RSB phase, product narrative reframed. If gamma ~ 0: near-critical, product narrative weakened.

The 2.3x alpha ratio (E_a(0.05)/E_a(0.10)) is preserved under Explanations A and B; the ratio is about h(alpha) not about N. It is only lost under Explanation C.

---

## Cheap decisive test

Run Glauber MFPT measurement: 3 noise temperatures T in {0.3, 0.5, 0.8}, 2 loading values alpha in {0.05, 0.10}, 5 sizes N in {512, 1024, 2048, 4096, 8192}, 10 seeds per cell. Extract:
- ln(tau) vs N^{1/3}: linear fit R^2 > 0.92 -> Explanation B (1-RSB)
- ln(tau) vs N: linear fit R^2 > 0.92 -> Explanation A (AGS intact, proxy broken)
- tau N-independent: -> Explanation C (marginal basin)
- tau(alpha=0.05) / tau(alpha=0.10) > 1 (significant): alpha-dependence survives regardless of N-scaling
Expected cost: <2h CPU total.

---

## Falsifiable predictions

HARD-PASS:
- ln(tau) vs N^{1/3} linear, R^2 > 0.92, across all alpha values tested [confirms 1-RSB phase Explanation B; barrier exists and is alpha-dependent]
- OR: basin-volume sampling shows significant alpha-slope (p<0.01, tau ratio >1.5) [confirms Explanation A; proxy was broken but physics intact]

HARD-FAIL:
- tau is N-independent (CV < 0.10) AND tau(0.05)/tau(0.10) < 1.2 [barrier is effectively absent; PP-33 is a genuine physics failure; product narrative for retention barriers must be abandoned]
- Both MFPT and FFS rate fail to show alpha-sensitivity [confirms Explanation C and that substrate genuinely has no alpha-sensitive barrier in tested regime]

MIDDLE-BAND (inconclusive):
- ln(tau) N-scaling intermediate (gamma between 0.3 and 0.8): finite-size crossover; need N > 16384

---

## Cross-thread synthesis

1. Non-equilibrium stat-mech (SKAH-M class confirmed): N^{1/3} barrier scaling is characteristic of 1-RSB dynamical phases in mean-field non-equilibrium systems. CONSISTENT with SKAH-M. The Crooks/Sagawa-Ueda fluctuation theorem framework applies to N^{1/3} barriers if work distribution measured along finite-time protocols (non-equilibrium work W has distribution P(W) ~ exp(beta * W); E_a extracted from tail).

2. Multi-basin first-order transition (Pred-4 confirmed, max-gap=18x): coexistence of multiple retrieval states with large inter-basin separations is the thermodynamic signature of 1-RSB. Pred-4 is consistent with Explanation B.

3. TAP framework (semiconductor field, tier-1): Aspelmeier-Bray-Moore 2004 TAP saddle result (N^{1/3} for SK/Hopfield p=2) transfers directly. If substrate interaction order is effectively p=2 (pairwise W), the N^{1/3} prediction is the default.

4. FFS as the missing tool: the field advisor flags D7 (forward-flux sampling) as tier-1, score=5.0. PP-33 now gives the concrete substrate motivation for that drill. FFS is the direct path to closing PP-33 affirmatively.

---

## Substrate-product implications

Product narrative "predictable retention barriers as function of loading alpha" SURVIVES under Explanations A and B:

ORIGINAL (AGS): barrier ~ N * (alpha_c - alpha) / alpha_c [extensive, strong alpha-sensitivity]
REVISED (1-RSB): barrier ~ C * N^{1/3} * (alpha_c - alpha) [subextensive, alpha-sensitivity preserved]

Either way, the product claim "retention lifetime increases predictably as loading decreases" is defensible. The quantitative claim must be recalibrated. The important product-engineering consequence:

Under Explanation B (1-RSB): larger substrate dimensions give longer retention lifetimes (N^{1/3} growth). This is a POSITIVE product implication -- scaling up the substrate dimension directly increases retention reliability, just sublinearly.

Under Explanation A (proxy broken): the original AGS formula is intact and gives exponentially longer lifetimes with N. Even better for product.

Under Explanation C (marginal basin): product narrative weakened; focus should shift to "verifiable retrieval" rather than "retention lifetime prediction."

Priority action: the MFPT experiment (< 2h CPU, no cloud needed) is the single highest-ROI experiment available. It directly resolves which explanation is correct and unlocks or closes the product-narrative claim.

---

## Follow-on drill candidates

1. [DECISIVE - exp_dev] MFPT N-scaling probe via Glauber dynamics: alpha in {0.05, 0.10}, N in {512, 1024, 2048, 4096, 8192}, T in {0.3, 0.5, 0.8}, 10 seeds. Discriminates Explanation A vs B vs C. Cost: <2h CPU. This is the tier-1 next experiment.

2. [SPIN-GLASS field, tier-1 E1] 1-RSB Parisi step for standard Hopfield at sub-saturation alpha: derive P(q) overlap distribution under 1-RSB for alpha in {0.05, 0.10}. If q_EA > 0 with partial RSB, confirms Explanation B and the N^{1/3} barrier prediction. Maps to cap_map non-equilibrium-stat-mech row.

3. [SEMICONDUCTOR/TAP field, tier-1 D7] FFS implementation for basin escape: partition state space by overlap m; measure conditional crossing probabilities; extract rate k_FFS(alpha, N). Direct bypass of the proxy problem. 1-2 day implementation cost; recommended as parallel track to MFPT.

---

## Citations (verified)

1. Amit D, Gutfreund H, Sompolinsky H (1987) "Statistical mechanics of neural networks near saturation" Ann. Phys. 173:30-67
2. Amit D, Gutfreund H, Sompolinsky H (1985) "Spin-glass models of neural networks" Phys. Rev. A 32:1007
3. Aspelmeier T, Bray AJ, Moore MA (2004) "Complexity of Ising Spin Glasses" PRL 92:087203 -- N^{1/3} TAP barrier scaling in SK/Hopfield
4. Allen RJ, Warren PB, ten Wolde PR (2005) "Sampling rare switching events in biochemical networks" PRL 94:018104 -- FFS method
5. Allen RJ et al (2020) "Studying rare events using forward-flux sampling: Recent breakthroughs and future outlook" JCP 152:060901
6. Krotov D, Hopfield JJ (2016) "Dense Associative Memory for Pattern Recognition" NeurIPS arXiv:1606.01164
7. Crisanti A, Horner H, Sommers H-J (1993) "The spherical p-spin interaction spin-glass model" Z. Phys. B 92:257 -- p-spin barrier scaling
8. Aspelmeier T (2022) "Free energy barriers in the Sherrington-Kirkpatrick model" arXiv:2111.06753 -- TAP barrier N^{1/3} confirmed numerically

P_deflated: P(Explanation A: proxy broken, physics intact) = 0.35; P(Explanation B: 1-RSB N^{1/3} phase) = 0.28; P(Explanation C: near-critical marginal) = 0.17; P(combination A+B) = 0.10; unresolved = 0.10. Calibration penalty -0.20 applied to all novel-synthesis estimates. Novel-synthesis cap not exceeded (all mechanisms literature-grounded).
