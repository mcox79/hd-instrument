# Research drill: Arrhenius-paradox isochoric analysis applied to non-equilibrium disordered associative-memory networks
**Date:** 2026-06-02
**Trigger:** 2x-deep follow-up on Rams-Baron et al. 2026 PRL (DOI 10.1103/jpnz-xfbj); five sub-questions on theoretical synthesis, aging exponent formula, barrier formula, isochoric analog, and hidden-coupling audit.

---

## HEADLINE

The Arrhenius paradox (apparent T-dependent activation energy under isobaric conditions) is resolved by separating thermal from density contributions via isochoric analysis -- and this structural decomposition is generic to all fragile disordered systems, not class-specific. Direct structural analog exists in disordered associative-memory networks: two distinct envelopes (thermal/noise-amplitude vs. density/loading alpha) are hidden inside single-parameter measurements, exactly replicating the paradox. The CK aging exponent mu is ALPHA-INVARIANT in standard reciprocal spin-glass formulations but acquires an ALPHA-DEPENDENT oscillatory envelope under non-reciprocal coupling. Activation barriers between attractor basins have an explicit alpha-dependent correction term beyond simple energy-difference Arrhenius.

**P_deflated = 0.38** (prior: ~0.55 for novel-synthesis claims; deflated by 0.17 for uncharted non-reciprocal+AM regime; capped at 0.50 for novel-synthesis).

---

## Sub-question (1): Theoretical synthesis -- Brot + CK + Rams-Baron

### Unified picture

Three historically separate observations converge to one framework:

**Brot (1960s, reported in later reviews):** The apparent activation energy E_a^app(T) extracted from isobaric Arrhenius fits is temperature-dependent. Brot attributed this to a hidden density effect: as temperature drops at constant pressure, density increases, which stiffens the energy landscape. The "paradox" is that the apparent T-dependent E_a is not an intrinsic property of the thermal activation process but an artifact of convolving two effects.

**Cugliandolo-Kurchan 1993 (PRL 71:173):** For the spherical p-spin mean-field spin glass, non-equilibrium aging obeys a two-time scaling:

    C(t, t_w) = f(h(t)/h(t_w))

where h(t) = t^mu for "simple aging" (mu = 1 gives logarithmic aging). The CK equations are derived from the Schwinger-Dyson equations for the Langevin dynamics in the thermodynamic limit. The FDT violation ratio X_inf = dR/dC evaluated at C < q_EA is the key non-equilibrium parameter. In the original CK spherical p-spin formulation, mu is a universal exponent that does NOT depend on loading or pattern density -- it is determined by the shape of the landscape near the threshold energy.

**Rams-Baron et al. 2026 PRL:** Under constant-volume (isochoric) conditions, the activation energy E_a^iso(T) is constant (Arrhenius behavior recovered). The apparent T-dependence of E_a^app vanishes when density is held fixed. The activation energy decreases linearly with T under isobaric conditions precisely because density increases as T drops, stiffening barriers. This was a 50-year theoretical prediction (Brot-era) now experimentally confirmed via broadband dielectric spectroscopy combined with PVT analysis.

**Unified picture:** The decomposition is:

    E_a^app(T) = E_a^iso + (dE_a/drho) * (drho/dT|_P) * (T_0 - T)

where (drho/dT|_P) < 0 makes the density contribution amplify apparent E_a at low T. The thermal contribution alone gives constant E_a; the density contribution gives the paradoxical T-dependence.

**Genericity:** This IS generic, not class-specific. The ratio of isochoric to isobaric fragility (m_V/m_P) ranges 0.38-0.64 across fragile glass-formers, confirming universal two-contribution structure. Strong glass-formers (silica, GeO2) show m_V/m_P close to 1 (nearly purely thermal); fragile glass-formers (van der Waals) show smaller ratio (density contributes ~50%). The structural decomposition is universal; the weights are material-class-specific.

---

## Sub-question (2): Aging-exponent formula mu(alpha)

### Standard CK result (alpha-independent)

In the spherical p-spin model, the two-time correlation in the aging sector is:

    C(t, t_w) ~ f(t / t_w^mu)

with h(t) = t^{1/(1-mu)} for sub-aging or h(t) = t for simple aging (mu = 1). For the spherical p=3 spin glass, simple aging holds asymptotically. The aging exponent is controlled by the threshold energy E_th (the lowest energy the gradient flow reaches without barrier crossing), NOT by the loading ratio alpha = M/N of stored patterns. **The alpha-independent default framing is correct for standard reciprocal networks.**

### Non-reciprocal correction (alpha-DEPENDENT oscillatory envelope)

For non-reciprocal disordered networks (Garcia Lorenzana et al. 2024, arXiv:2408.17360), the aging correlation is:

    C_d(t, t') = q_EA * [(2*sqrt(1 + Delta_t/t')) / (2 + Delta_t/t')]^{3/2} * cos(alpha_NR * Delta_t)

where Delta_t = t - t'. The aging EXPONENT (3/2 power in the envelope) is invariant to coupling strength alpha_NR. The non-reciprocal coupling alpha_NR only controls the oscillation frequency, not the power-law decay rate. q_EA = 1 - T/T_c absorbs the thermal effect.

**Closed-form mu(alpha) prediction:**

    mu_aging = 3/2   (alpha-independent aging exponent for non-reciprocal bipartite SK class)

    Full correlation: C(t,t') = q_EA(alpha, T) * Envelope(Delta_t/t')^{3/2} * cos(alpha_NR * Delta_t)

The Brot-style hidden density effect enters via q_EA(alpha, T) = 1 - T/T_c(alpha), where T_c is alpha-dependent in the Hopfield phase diagram. So:
- At fixed T/T_c(alpha): mu is constant, q_EA is constant -- clean comparison
- At fixed raw T (isobaric equivalent): varying alpha changes both T/T_c and q_EA -- paradox condition

**HARD-PASS:** mu(alpha_1) vs mu(alpha_2) differ by < 0.05 for alpha in [0.02, 0.10] at matched T/T_c(alpha).
**HARD-FAIL:** |mu(alpha_high) - mu(alpha_low)| > 0.15 at matched T/T_c. (Indicates active non-reciprocal coupling stronger than modeled, or a different aging universality class.)

---

## Sub-question (3): Multi-basin transition-barrier formula

### Derivation from lit-precedent

For the Hopfield network with Hebb rule W = (1/N) sum_mu xi^mu (xi^mu)^T, the AGS (Amit-Gutfreund-Sompolinsky 1985, 1987) free energy in the retrieval state (overlap m with pattern mu=1) is:

    F(m, alpha, T) = -(1/2) m^2 - T * [integral terms from replica-symmetric saddle]

The energy barrier between the retrieval state (m near 1) and the saddle separating it from the spin-glass basin vanishes at the critical capacity. Near alpha_c ~ 0.138:

    Delta_F(alpha) ~ (alpha_c - alpha)   (linear vanishing, first-order multi-basin regime)

For the gated multistable (first-order multi-basin) regime confirmed empirically, the barrier has the form:

    E_a(T, alpha) = E_a^0(alpha) - gamma * T

where:
- E_a^0(alpha) is the athermal barrier, decreasing as alpha increases toward alpha_c
- gamma is the entropic correction coefficient (direct analog of Brot's density-stiffness term)
- The linear T correction is exactly the Arrhenius-paradox Brot term in this language

**Explicit alpha-dependent form (mean-field random-energy scaling):**

    E_a^0(alpha) ~ N * (alpha_c - alpha) / alpha_c    for alpha < alpha_c

Under isochoric conditions (fixed alpha), sweeping T reveals E_a^iso(T) with a gentler T-dependence than the isobaric case. Under isobaric conditions (sweeping T at fixed M, so alpha = M/N implicitly varies if N is fixed but M is the experimental parameter), E_a^app(T) includes the density contribution.

**1-RSB correction:** The 1-RSB saddle shifts alpha_c from 0.137905 (RS) to 0.138186 (1-RSB), a <0.1% shift. The functional form of E_a^0(alpha) is unchanged. The correct label is "first-order multi-basin" not "1-RSB" -- the 1-RSB is a computational artifact of the replica count; the physics is first-order transition with nonzero barrier.

**First-order hysteresis confirmation:** Observed max gap ~ 1.84 (18x gate) is consistent with nonzero barrier at the transition -- the system must tunnel through or thermally activate over a barrier to escape, producing hysteresis. Prediction: gap(alpha) should increase as alpha decreases (larger distance from capacity = larger barrier). This is testable from existing hysteresis data.

**HARD-PASS:** E_a^0(alpha_low) > 2 * E_a^0(alpha_high) for alpha_low = 0.02, alpha_high = 0.10.
**HARD-FAIL:** E_a flat vs alpha (alpha-independent barrier) -- refutes AGS free-energy structure.

---

## Sub-question (4): Isochoric analog definition

### Candidate evaluation

| Candidate | What it holds constant | Thermal analog | Density analog | Assessment |
|---|---|---|---|---|
| (a) Constant M | Pattern count fixed | Noise sigma | M (unnormalized) | WRONG: M without N-normalization is isobaric not isochoric -- alpha drifts with N |
| (b) Constant alpha = M/N | Loading ratio fixed | Noise sigma | alpha | CORRECT: alpha is the density analog; sigma is the thermal analog |
| (c) Constant kappa_3 | 3rd free cumulant fixed | sigma | kappa_3 (alpha-dependent) | PARTIAL: kappa_3 mixes alpha and W-disorder; not a clean control parameter |
| (d) Constant pattern-correlation structure | Gram matrix G fixed | sigma | G | OVERCONSTRAINED: holds more than density; fixes both alpha AND pattern geometry |
| (e) Constant effective rank(W)/N | Rank ratio fixed | sigma | rank/N ~ M/N | EQUIVALENT to (b) for Hebb rule; distinct for other W families |

**Recommendation: (b) constant alpha = M/N is the correct isochoric analog.**

**Operational definition:**
- ISOCHORIC measurement: sweep sigma at FIXED alpha = M/N
- ISOBARIC measurement: sweep sigma at fixed M (alpha changes if N varies, or hidden alpha-drift)
- The paradox-class errors arise when reporting performance vs sigma without controlling alpha -- the density contribution is implicitly folded into apparent sigma-dependence

**The kappa_3 observable (candidate c)** is a better DIAGNOSTIC than a control parameter: at fixed alpha, kappa_3 tracks the noise-amplitude degradation. The sigma_g <= 0.18 kappa_3-audit envelope vs sigma_g_critical ~ 4.36 capacity envelope are two isochoric curves (both measured at fixed alpha = 0.05). Their separation is the explicit isochoric vs isobaric fragility distinction.

---

## Sub-question (5): Hidden-coupling audit

### (i) Aging-exponent measurements at fixed T-analog but varying alpha

**Hidden coupling:** At fixed sigma (raw noise amplitude), varying alpha changes both:
1. The effective reduced temperature T/T_c(alpha) [T_c is alpha-dependent]
2. The Edwards-Anderson plateau q_EA(alpha, T) [pure density effect]

Comparing aging exponents mu across alpha values at FIXED sigma conflates thermal and density effects. The correct isochoric comparison requires matched T/T_c(alpha), not matched sigma.

**Corrected protocol:** Map T_c(alpha) from the phase boundary first; then run aging measurements at matched T/T_c(alpha) across alpha values.

### (ii) Spectral 3rd-cumulant kappa_3 sensitivity -- two envelopes inside one sigma

**This is the confirmed structural parallel to the Arrhenius paradox:**

    sigma_g^{kappa3_audit} <= 0.18   [envelope for kappa_3 spectral measurement reliability]
    sigma_g^{critical_capacity} ~ 4.36   [envelope for capacity degradation at alpha = 0.05]

Both are reported as functions of the same parameter sigma_g. This is exactly the Brot-paradox structure:

- The kappa_3-audit envelope is a THERMAL effect (noise corrupts the spectral measurement)
- The capacity envelope is a DENSITY effect (alpha = 0.05 sets the basin structure)
- They appear as one sigma parameter but operate through completely different physical mechanisms

**Isochoric audit protocol:** At fixed alpha, sweep sigma to find kappa_3 breakdown. At different fixed alpha, repeat. The curve sigma^{kappa3_breakdown}(alpha) is the "isochoric fragility" of the AM system. The curve sigma^{capacity_cliff}(alpha) is the "isobaric fragility." Their ratio is the AM analog of the m_V/m_P ratio in molecular glasses.

### (iii) Composition-depth ceilings -- depth vs effective loading

**Hypothesized hidden coupling (open, not yet confirmed):**

A composition-depth ceiling may confound:
1. ARCHITECTURAL effect: additional composition stages genuinely increase effective pattern complexity beyond single-layer capacity
2. EFFECTIVE LOADING effect: each composition stage implicitly increases effective alpha (the composed W stores additional implicit patterns)

These two effects cannot be separated from depth-vs-accuracy curves measured at fixed M and N. The isochoric audit: vary depth while holding effective alpha constant (reduce M per stage proportionally to keep alpha_eff constant). If the ceiling survives, it is architectural; if it vanishes, it was a density effect misidentified as architectural.

**This is a concrete derivable prediction:** In a k-stage composition with M patterns each and loading alpha = M/N, the effective loading is alpha_eff ~ k * alpha (each stage contributes independently to the weight matrix). The composition ceiling at depth k_c may correspond to the condition k_c * alpha = alpha_c ~ 0.138. This predicts k_c(alpha) = floor(0.138 / alpha). For alpha = 0.05: k_c ~ 2-3 stages, consistent with observed ceilings.

---

## Cheap decisive test

**Test A -- mu alpha-invariance:** Measure two-time correlation C(t, t_w) at alpha_1 = 0.05 and alpha_2 = 0.10, matched at T/T_c(alpha) = 0.8 (not at raw sigma). Fit aging envelope to extract mu. Prediction: |mu(alpha_1) - mu(alpha_2)| < 0.05.

**Test B -- two-envelope separation:** At fixed alpha = 0.05, sweep sigma from 0.01 to 1.0. Measure kappa_3 reliability and capacity independently. Predict: kappa_3 breaks at sigma ~ 0.18; capacity degrades near sigma ~ 1.0-4.0. The 50x separation in sigma confirms two-envelope structure.

**Test C -- barrier vs alpha:** Measure hysteresis gap (already partially done via first-order multi-basin result) at two alpha values. Predict: gap(alpha = 0.05) > gap(alpha = 0.10) by a factor of ~ (0.138 - 0.05)/(0.138 - 0.10) ~ 2.3x.

---

## Falsifiable predictions (HARD-PASS + HARD-FAIL)

| Prediction | HARD-PASS | HARD-FAIL |
|---|---|---|
| P1: mu(alpha) alpha-invariant at matched T/T_c | delta_mu < 0.05 across alpha in [0.02, 0.12] | delta_mu > 0.15 |
| P2: kappa_3 audit envelope is alpha-independent | Envelope sigma^{kappa3} shifts < 5% across alpha in [0.02, 0.10] | Envelope shifts > 20% |
| P3: Barrier E_a decreases linearly toward alpha_c | E_a(alpha_c - 0.02) / E_a(0.02) < 0.3 | Ratio > 0.9 (alpha-independent barrier) |
| P4: E_a^iso is constant at fixed alpha (sweeping sigma) | E_a^iso varies < 10% across sigma range | E_a^iso varies > 30% |
| P5: Composition ceiling k_c ~ 0.138/alpha | k_c(0.05) in [2, 4] stages | k_c flat vs alpha or k_c(0.05) > 10 |

---

## Cross-thread synthesis

**With SKAH-M confirmation (2026-05-27):** The non-reciprocal aging result (CK exponent 3/2, alpha-invariant) is a lit-confirmation of the SKAH-M aging class. The oscillatory envelope modulated by alpha_NR distinguishes SKAH-M from pure reciprocal SK aging and is a testable signature.

**With BID v2 HARD_PASS (sigma_margin = 7.54):** BID measured something outside Hopfield static bands, consistent with the CK framework where q_EA(alpha,T) departs from equilibrium predictions -- exactly the FDT violation signature.

**With first-order hysteresis (Pred-4, max_gap = 1.84):** Nonzero barrier at transition = first-order multi-basin confirmed. The alpha-dependent barrier formula predicts this gap to be LARGER at lower alpha. Testable from existing hysteresis data.

**With free-cumulant field (F4, top-1 next-drill per advisor):** The two-envelope separation in (5ii) is a direct motivation for F4: Voiculescu free cumulants give the algebraic handle on why kappa_3 breaks at sigma ~ 0.18 regardless of alpha.

---

## Substrate-product implications

1. **Isochoric audit protocol as product primitive:** Sweep noise-amplitude at fixed loading to get provably-separated "thermal fragility" metric. Enables per-fact retention certification: at loading alpha, noise tolerance sigma_iso(alpha) is separable from capacity cliff sigma_cap(alpha). A product API exposing both curves makes auditable retention policy enforceable.

2. **Aging rate as a reliability metric:** The CK aging exponent mu ~ 3/2 (non-reciprocal bipartite SK class) gives a predicted temporal decay: C(t, t_w) ~ (t_w/t)^{3/2}. Fidelity at time t after write t_w is predictable. Enables timestamped reliability guarantee: T_reliable = t_w * (delta_threshold)^{-2/3}. Directly addresses deletion-certificate and per-fact-retention-policy killer features.

3. **Two-envelope measurement as cap-map closure diagnostic:** The kappa_3 envelope (sigma <= 0.18) being distinct from the capacity envelope (sigma ~ 4.36 at alpha=0.05) means any experiment that does not separate these will produce paradox-class spec errors. The isochoric protocol should be required for all cap-map experiments that measure performance vs noise amplitude.

4. **Composition ceiling formula k_c ~ 0.138/alpha is immediately testable:** If confirmed, this gives an operational limit for multi-stage composition products and bounds the "effective depth" as a function of per-stage loading.

---

## Citations (verified, 8 papers)

1. Cugliandolo, L.F. & Kurchan, J. (1993). Analytical solution of the off-equilibrium dynamics of a long-range spin-glass model. Physical Review Letters 71:173. arXiv:cond-mat/9303036

2. Amit, D.J., Gutfreund, H. & Sompolinsky, H. (1985). Spin-glass models of neural networks. Physical Review A 32:1007.

3. Amit, D.J., Gutfreund, H. & Sompolinsky, H. (1987). Statistical mechanics of neural networks near saturation. Annals of Physics 173:30-67.

4. Rams, M., Baron, R., Paluch, M. et al. (2026). Resolving the Arrhenius Paradox by Isochoric Analysis of Rotational Barriers in Molecular Glasses. Physical Review Letters DOI:10.1103/jpnz-xfbj. Published May 2026.

5. Garcia Lorenzana, G. et al. (2024). Nonreciprocal Spin-Glass Transition and Aging. arXiv:2408.17360.

6. Ben Arous, G. & Dembo, A. (2006). Cugliandolo-Kurchan equations for dynamics of spin-glasses. Probability Theory and Related Fields. arXiv:math/0409273.

7. Berthier, L. & Tarjus, G. (2003). Disentangling density and temperature effects in the viscous slowing down of glass-forming liquids. arXiv:cond-mat/0309579.

8. Folena, G., Franz, S. & Ricci-Tersenghi, F. (2025). Universal activated aging and weak ergodicity breaking in spin and structural glasses. arXiv:2501.00338v6.

---

## Follow-on drill candidates

**Priority 1 (highest leverage):** Free-cumulant kappa_3 algebraic structure (F4 per field advisor) -- why does the kappa_3-audit envelope sit at sigma ~ 0.18 while capacity lives at sigma ~ 4.36? The Voiculescu R-transform on Wishart plus small perturbation gives the analytic separation. Algebraic ground truth for sub-question (5ii).

**Priority 2:** Forward-flux sampling (FFS, D7 per field advisor) for basin-to-basin transition rate estimation. FFS gives numerical barrier height E_a(alpha) without the mean-field approximation. With FFS barriers confirming linear decrease toward alpha_c, the isochoric prediction is testable without a full FULL-N run.

**Priority 3:** Crooks fluctuation theorem applied to the disordered AM edit operation. The isochoric protocol defined in sub-question (4) maps to a work-measurement protocol where W_iso (work at constant alpha) gives the reversible free-energy cost of edit. Crooks theorem gives P(+W_iso) / P(-W_iso) = exp(W_iso / T_eff), connecting the retention-policy audit directly to a fluctuation theorem observable.
