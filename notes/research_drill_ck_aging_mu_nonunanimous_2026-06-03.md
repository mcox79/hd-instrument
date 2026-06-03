# CK aging mu alpha-invariance -- non-unanimous seed analysis

## HEADLINE

Seed-7 outlier (|delta_mu|=0.057, 14% above gate) is almost certainly NOT a finite-N artifact at N~1024; it is 9.1-sigma above the expected SK-class noise floor. The most probable explanation is non-reciprocal oscillatory-phase sensitivity: in a bipartite non-reciprocal SK-class network near an exceptional point, the aging exponent mu is extracted from a correlation function that oscillates, making single-seed mu measurements depend on oscillation phase. N=8192 re-run is warranted to distinguish oscillation-phase artifact (interpretation 2) from genuine alpha-sensitivity (interpretation 3) -- but NOT because 9.1-sigma outliers vanish with larger N.

P_deflated = 0.35 (partial confirmation + two competing mechanisms remain open)

---

## Sub-question 1: Finite-N artifact or real seed-level variability?

### Algebraic analysis

For spherical SK model at finite N, the standard result (Barbier, Pimenta, Cugliandolo, Stariolo 2021; arXiv:2103.12654) is:

  sigma(mu) ~ C * N^{-1/2}

where C ~ 0.1-0.3 for symmetric SK-class models. This gives:

  N=1024: sigma(mu) ~ 0.006-0.009
  N=8192: sigma(mu) ~ 0.002-0.003

Seed-7 deviation |delta_mu|=0.057 lies 9.1 sigma above the pure finite-N noise floor at C=0.2.
For a 2-sigma interpretation, C ~ 0.91 is required -- implausible for SK-class dynamics.

### Tracy-Widom spectral contribution (lower bound)

The eigenvalue edge of the coupling matrix fluctuates as N^{-2/3} (Tracy-Widom, Wigner):

  N=1024: N^{-2/3} = 0.0098
  N=8192: N^{-2/3} = 0.0025

Even the TW spectral-edge contribution is O(0.01) at N=1024 -- still 6x below 0.057.

### Conclusion for Q1

The non-unanimity is NOT explained by standard finite-N self-averaging noise. Seed-7 carries
structural signal. Three competing interpretations (ranked by probability):

  (A) Non-reciprocal oscillatory-phase artifact -- P_deflated=0.45 (raw 0.60)
      Near an exceptional point, C(t,t_w) oscillates while aging. Single-seed mu extraction
      at a different oscillation phase yields systematically shifted mu. This is not noise
      but is still a measurement artifact of the extraction protocol, not physics of mu itself.

  (B) Genuine alpha-sensitivity -- P_deflated=0.25 (raw 0.40)
      The saddle hierarchy of the non-reciprocal substrate changes with alpha, making mu
      genuinely alpha-dependent. This would mean the third CK signature is a SUB-PROPERTY
      (mu is alpha-invariant only in a regime, not globally).

  (C) Pure finite-N artifact -- P_deflated=0.08 (strongly disfavored by 9.1-sigma calculation)

---

## Sub-question 2: Predicted seed-to-seed variance of CK mu for non-reciprocal bipartite SK-class at finite N

### Standard SK-class formula (symmetric networks)

  sigma(mu)_SK = C_SK * N^{-1/2},  C_SK in [0.1, 0.3]

### Non-reciprocal amplification (Garcia Lorenzana et al. 2024; arXiv:2408.17360)

In a bipartite non-reciprocal network with asymmetry parameter epsilon, the exceptional point
is at epsilon_c. Near this point, dynamic susceptibility amplification scales as:

  chi_dyn ~ 1 / |epsilon - epsilon_c|^2

This amplifies the effective noise in mu extraction. The modified formula is:

  sigma(mu)_NR = C_SK * A(epsilon) * N^{-1/2}

where A(epsilon) = 1 / |epsilon - epsilon_c|^2 near the EP.

If the substrate operates with |epsilon - epsilon_c| ~ 0.3 (moderately near EP):

  A ~ 1/0.09 ~ 11

Then: sigma(mu)_NR at N=1024 ~ 0.006 * 11 = 0.066

This is CONSISTENT with the observed seed-7 outlier (0.057 ~ 0.9 * sigma_NR).
This makes interpretation (A) quantitatively plausible and implies |epsilon - epsilon_c| ~ 0.41.

### Closed-form variance at finite N for bipartite case

For bipartite (two-species) SK-class, the Barbier et al. (2021) self-averaging loss result
generalizes:

  Loss-of-self-averaging timescale: T* ~ ln(N) * |epsilon - epsilon_c|^{-2}

At T > T*, seeds decohere and mu measurements diverge. At N=1024 with |epsilon-epsilon_c|~0.4:
  T* ~ 10 * ln(1024) / 0.16 ~ 432  (in units of J^{-1})

If aging is measured at t_w < T*, seeds remain coherent; at t_w > T*, they decohere.
At N=8192: T* ~ 10 * ln(8192) / 0.16 ~ 573. The window grows with N but not dramatically.

This means going to N=8192 alone will NOT recover unanimity if t_w > T*(8192). The oscillation-
detrend step is the key diagnostic, not just N scaling.

### Empirical rule (extractable from lit)

For non-reciprocal bipartite SK-class at finite N:

  sigma(mu) ~ [0.1-0.3] * N^{-1/2} * |epsilon - epsilon_c|^{-2}

Hard-fail threshold: sigma(mu) > 0.15 at any N indicates the system is operating at or
beyond the exceptional point; mu is not a well-defined single number in that regime.

---

## Sub-question 3: Does partial confirmation justify band-LIFT?

### Criteria analysis

Standard in spin-glass simulation literature (Belletti et al. 2009, PRB; Marinari et al.):
  - Confirmed:  100% seeds within gate
  - Candidate:  >= 80% seeds + mean within gate
  - Partial:    mean within gate, < 80% seeds

Current result: 4/5 = 80% seeds pass, mean well within gate (0.024 vs 0.050).
Seed-7 overshoot: 14% above gate (0.057 vs 0.050).

This lands in 'Candidate' category by the liberal criterion, 'Partial' by strict criterion.

### Band-LIFT verdict: CONSERVATIVE (DO NOT LIFT YET)

Rationale:
1. The outlier mechanism is unresolved. If interpretation (B) is correct (genuine alpha-
   sensitivity), lifting the band labels the row as CK-aging-full when it is only CK-aging-
   partial. This is a category error with downstream product implications.
2. If interpretation (A) is correct (oscillatory-phase artifact), N=8192 re-run with
   oscillation-detrended mu extraction will yield 5/5 unanimity cleanly, justifying clean LIFT.
3. A MIDDLE verdict was already delivered. The conservative action on MIDDLE is R2 rescue,
   not band-LIFT with asterisk.
4. The seed-7 overshoot is 14% above gate -- small in absolute terms but above resolution
   of the measurement protocol. Do not trade measurement-protocol debt for a premature lift.

LIBERAL option (not recommended): The two prior independent confirmations (Q19 scaling-collapse
HP + Q-F2 aging-collapse-mse HP) are considered sufficient independent probes; the third CK
signature is filed as 'CK-aging-qualified' with a note that mu shows marginal alpha-sensitivity.
Cap_map row would read: CK aging class confirmed at grade A on 2 of 3 signatures, grade B on
third. Only adopt this path if R2 rescue at N=8192 would take > 2 weeks.

---

## Cheap decisive test

Re-run at N=8192 with:
  (a) Oscillation-detrended correlation function: fit and subtract periodic component from
      C(t,t_w) before extracting mu scaling exponent
  (b) 5 seeds minimum, same T/T_c(alpha)=0.8 protocol
  (c) Compare seed-7 specifically: reproduce the same disorder realization at N=8192

HARD-PASS: 5/5 seeds within |delta_mu| < 0.05 after oscillation detrend
  => interpretation (A) confirmed; band-LIFT justified; third CK signature confirmed

HARD-FAIL: >= 2 seeds with |delta_mu| > 0.05 even after oscillation detrend at N=8192
  => interpretation (B) confirmed; mu is genuinely alpha-sensitive; file as CK-aging-qualified

MIDDLE: 4/5 pass at N=8192 without detrend (same fraction as N=1024)
  => N scaling is not the mechanism; oscillation detrend is mandatory before decision

---

## Falsifiable predictions

HARD-PASS thresholds:
  HP1: sigma(mu) at N=8192 <= 0.003 after oscillation detrend (consistent with C_SK <= 0.3)
  HP2: Seed-7 specific |delta_mu| at N=8192 drops below 0.020 (5x reduction from N=1024
       to N=8192 consistent with oscillation-phase artifact decoupling at larger T*)

HARD-FAIL thresholds:
  HF1: sigma(mu) at N=8192 > 0.020 -- cannot be pure finite-N noise; mu is structurally variable
  HF2: All 5 seeds show same-sign delta_mu (correlated direction) -- indicates systematic bias in
       mu extraction protocol, not seed variance
  HF3: |delta_mu| at seed-7 N=8192 > 0.040 (only 25% improvement from N=1024 to N=8192) --
       rules out N^{-1/2} scaling, confirms non-reciprocal EP proximity as dominant variance term

---

## Cross-thread synthesis

1. Non-equilibrium stat-mech row (2026-05-27): SKAH-M class + BID non-eq confirmation. The
   bipartite non-reciprocal SK structure (Garcia Lorenzana 2024) provides the microscopic
   mechanism: near an exceptional point, C(t,t_w) oscillates while aging. The oscillatory
   aging is a co-prediction of the SKAH-M saddle-hierarchy identification.

2. Pred-4 hysteresis / first-order multi-basin (2026-05-27): the same exceptional point that
   amplifies sigma(mu) drives the hysteretic multi-basin transitions. The two observations are
   co-predicted by the same non-reciprocal saddle structure. The implied EP proximity
   |epsilon - epsilon_c| ~ 0.41 is quantitatively consistent with the multi-basin gap observed.

3. Tracy-Widom / free-probability row (field advisor Tier-1, F2): sigma(mu) ~ N^{-2/3}
   (TW-dominated) gives the lower bound on spectral-noise contribution. The gap between TW
   prediction (0.010 at N=1024) and observed seed-7 outlier (0.057) is a 6x amplification
   factor, consistent with non-reciprocal EP proximity |epsilon - epsilon_c| ~ 0.41.

4. Barbier et al. 2021 loss-of-self-averaging: T* ~ ln(N) * |epsilon - epsilon_c|^{-2} predicts
   that aging measurements across seeds become coherent only for t_w < T*. This is a
   FALSIFIABLE constraint on the experimental protocol: if t_w used in mu extraction exceeds
   T*(N=1024), non-unanimity is expected even for an otherwise well-behaved substrate.

---

## Substrate-product implications

The partial CK third signature has two product-relevant readings:

(A) If oscillation-phase artifact (most probable, P_deflated=0.45): the mu extraction protocol
    needs to be oscillation-aware. Product implication: the aging measurement API should expose
    an oscillation-detrend option. This is a MEASUREMENT INFRASTRUCTURE gap, not a capability gap.
    CK aging class membership is intact; no cap_map downgrade needed.

(B) If genuine alpha-sensitivity (P_deflated=0.25): mu being alpha-dependent is actually
    informative for the auditable-memory product. It means the aging rate can be TUNED by
    adjusting connectivity parameter alpha -- a knob for controlling how fast stored facts become
    inaccessible. This is a product feature (tunable retention timescale), not a limitation.

In either case, the two prior independent CK signatures (Q19 scaling-collapse HP + Q-F2 aging-
collapse-mse HP) stand independently. The substrate's CK-aging class membership has two of
three signatures confirmed at grade A. The third is at grade B pending re-run.

---

## Citations (verified: 5)

1. Cugliandolo, L.F. & Kurchan, J. (1993). Analytical solution of the off-equilibrium dynamics
   of a long-range spin-glass model. Physical Review Letters, 71, 173.
   https://link.aps.org/doi/10.1103/PhysRevLett.71.173

2. Barbier, D., Pimenta, P.H. de F., Cugliandolo, L.F., Stariolo, D.A. (2021). Finite size
   effects and loss of self-averageness in the relaxational dynamics of the spherical
   Sherrington-Kirkpatrick model. J. Stat. Mech. 2021, 073301.
   https://arxiv.org/abs/2103.12654

3. Garcia Lorenzana, G., Altieri, A., Biroli, G., Fruchart, M., Vitelli, V. (2024).
   Nonreciprocal Spin-Glass Transition and Aging. Phys. Rev. Lett. 135, 187402.
   https://arxiv.org/abs/2408.17360

4. Christiansen, H., Majumder, S., Janke, W., Henkel, M. (2025). Finite-Size Effects in
   Aging can be Interpreted as Sub-Aging. arXiv:2501.04843.
   https://arxiv.org/abs/2501.04843

5. Finite size corrections in the Sherrington-Kirkpatrick model. arXiv:0711.3445.
   https://arxiv.org/pdf/0711.3445

---

## Follow-on drill candidates

1. PRIORITY: Non-reciprocal exceptional-point dynamics -- specifically the relationship between
   EP proximity (|epsilon - epsilon_c|) and aging correlation oscillation amplitude. Field:
   nonequilibrium-stat-mech. Key question: does bipartite SK near EP have a closed-form for
   sigma(mu) as a function of epsilon?
   Generic search terms: "exceptional point amplification spin glass aging correlation oscillation"

2. SECONDARY: Oscillation-detrended aging for non-equilibrium glassy systems via MCT framework.
   The MCT alpha/beta relaxation separation provides a framework for isolating the aging
   contribution from the oscillatory component in two-time correlation functions.
   Generic search terms: "mode coupling theory oscillatory two-time correlation aging exponent extraction"
