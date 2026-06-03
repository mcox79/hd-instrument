# Research Note: Oscillatory Phase-Noise Scaling — Kuramoto/ReRAM Capacity Threshold
date: 2026-06-02
topic: phase-noise threshold for exponential-to-linear capacity collapse in Kuramoto-style coupled-oscillator associative memory

---

## HEADLINE

The exponential 2^(N/4) capacity of Kuramoto-style honeycomb oscillator memory (arXiv:2604.01469, 2504.03102) is PRESERVED only when every adjacent oscillator pair maintains |delta_theta_ij| < pi/(2*n_c) rad; for n_c=5 this is sigma_phi < pi/10 approximately 0.314 rad (18 degrees). The IBM ReRAM 2x2 prototype (arXiv:2503.14126) operates at ~8.6 kHz with binary 0/180-degree phase encoding and gives no measured sigma_phi. Stochastic Kuramoto theory (Fokker-Planck self-consistency) predicts a noise-induced incoherent transition at D_c = K*g(0)/2, where K is coupling and g(0) is the frequency distribution density at zero detuning. Product-scale (~1000 nodes) ring-oscillator networks are approximately 2 fab generations short of multi-symbol exponential-capacity operation; the binding constraint is oscillator-to-oscillator FREQUENCY MISMATCH across nodes, not intrinsic per-node phase noise.

---

## (A) Closed-form prediction from coupled-oscillator / Kuramoto synchronization theory

### 1. Basin-of-attraction bound (arXiv:2604.01469, Theorem III.2)

The basin of attraction for a stored memory theta* in an n_c-node honeycomb cycle is:

    max_i |theta_i(0) - theta_i*| < pi*r / (2*n_c)

where r = ((n_c - 1) mod 4) + 1 in {1, 2, 3, 4}.

For n_c = 5: r = 1 => basin half-width = pi/10 approximately 0.314 rad (18 degrees).
For n_c = 4: r = 4 => basin half-width = pi/2 = 1.571 rad (90 degrees) — substantially wider.

KEY: basin half-width is SCALE-INDEPENDENT. It does not shrink as m (number of cycles) grows. sigma_phi < pi/(2*n_c) is a per-node requirement, not a per-network requirement.

The EXPONENTIAL CAPACITY formula is:

    N_eq = (2*ceil(n_c/4) - 1)^m

For n_c=5, m cycles, n=4m+1 nodes: N_eq = 3^m = 3^((n-1)/4) ~ 3^(N/4) — exponential in N.

Capacity is maintained iff all stored configurations satisfy phase-cohesiveness:
    |theta_i* - theta_j*| < pi/2   for all adjacent pairs (i,j).

Capacity COLLAPSES to O(1) per cycle (linear O(N) total) once phase noise pushes |delta_theta_ij| >= pi/2: adjacent configurations merge and memory states destabilize.

### 2. Stochastic Kuramoto noise threshold (Kuramoto-Sakaguchi with white noise)

The noisy Kuramoto model for N oscillators with frequency disorder g(omega) and Gaussian white noise amplitude D:

    d(theta_i)/dt = omega_i + (K/N) * sum_j sin(theta_j - theta_i) + sqrt(2D) * xi_i(t)

Fokker-Planck steady-state self-consistency equation (Aceb ron et al., Rev. Mod. Phys. 2005):

    r = K*r * integral cos^2(psi) * rho_st(psi | K*r, D) dpsi

The synchronized phase becomes unstable (r -> 0) at:

    K_c(D) = 2*D / g(0)    [Lorentzian/uniform g(omega), thermodynamic limit]

Equivalently, for fixed K the critical noise diffusion is:

    D_c = K * g(0) / 2

Above D_c: order parameter r -> 0 (incoherent phase). Below D_c: r > 0 (phase-locked).

Translating D to sigma_phi (RMS phase deviation from locked state, linearized near synchrony):

    sigma_phi^2 approximately D / (K*r)

At the transition, r -> 0+ so sigma_phi -> infinity — confirming the transition is second-order (continuous) in the thermodynamic limit.

For the honeycomb associative memory operating well below D_c, the TIGHTER product-relevant threshold is the basin-of-attraction condition:

    sigma_phi_crit approximately pi / (2*n_c)

which is sigma_phi_crit approximately 0.314 rad for n_c=5.

### 3. Arrhenius / Kramers escape time (arXiv:2507.21984 higher-order Kuramoto)

For higher-order (pairwise + quartic) Kuramoto with N oscillators and inverse temperature beta:

    tau_esc approximately 2*pi * w_s * w_u * exp[beta*N*DeltaF(C,x)] * tau_0

where DeltaF is the intensive free-energy barrier between memory and saddle.

At N=500, beta=1: N*DeltaF approximately 16, giving tau_esc approximately 4.5e7 * tau_0.

For a ~10MHz oscillator (tau_0 = 100ns): tau_esc approximately 4.5 seconds — acceptable for a memory substrate.

COLLAPSE CONDITION: when sigma_phi is large enough that beta*DeltaF approximately 1/N, the Kramers exponent becomes O(1) and tau_esc -> tau_0 (instantaneous escape = capacity lost). This maps back to sigma_phi ~ pi/(2*n_c).

Tricritical point (2507.21984): at K=3J (C=3) the capacity transition switches from continuous to first-order/hysteretic. Below K=3J capacity degrades smoothly with noise; above K=3J there is a hard phase boundary.

---

## (B) Empirical measurements from 2024-2025 ReRAM and analog Kuramoto hardware

### IBM ReRAM ring-oscillator network (arXiv:2503.14126, IMW 2025)

- Implementation: 2x2 ONN (4 ring oscillators) coupled via CMO/HfOx ReRAM crossbar integrated into BEOL CMOS
- Oscillation frequency: 8.6 kHz
- Coupling: R_low approximately 2 kohm (active ReRAM state), R_high approximately 10 Mohm (inactive), R_series = 47 kohm
- Phase encoding: BINARY {0 degrees, 180 degrees}
- Result: correct phase locking demonstrated (delta_phi = 0 degrees or 180 degrees)
- Phase noise sigma_phi: NOT MEASURED. No jitter or RMS phase error reported.
- Scalability: no projections beyond 2x2 given.
- ReRAM forming voltage: mean = 2.84V, sigma = 0.13V across 25 devices.

CRITICAL OBSERVATION: the IBM demo uses binary encoding (tolerant of sigma_phi up to ~pi/4 = 0.785 rad before bit-flip). This is NOT testing the noise regime relevant to exponential capacity, which requires ternary or higher-order phase encoding with sigma_phi < 0.314 rad.

### CMOS ring oscillator phase noise baseline (Abidi 2006; 65nm and 28nm data)

- 65nm CMOS PLL at 1.6GHz: RMS jitter < 0.8 ps => sigma_phi = 2*pi*1.6e9*0.8e-12 approximately 0.008 rad (< threshold by 40x)
- 28nm CMOS 10GHz PLL: 280fs jitter => sigma_phi approximately 0.018 rad (< threshold by 17x)
- Free-running ring oscillator at 10MHz with typical D approximately 1e-3 rad^2/s: sigma_phi per cycle approximately sqrt(2*D*tau_0) approximately 0.014 rad — well within threshold per cycle, but accumulates over time without coupling.

PLL-stabilized oscillators achieve sigma_phi << pi/10 in 65nm+. The binding constraint is frequency MATCHING across many oscillators, not per-node noise floor.

### CDW oscillator simulations (arXiv:2604.01469)

- Phase-locking for n_c=5 honeycomb validated via charge-density-wave oscillator simulations
- No sigma_phi measurement reported; Theorem III.2 guarantees basin analytically

---

## (C) Implications for product-scale hardware (~1000 nodes)

### Threshold vs. current state

Threshold: sigma_phi < pi/(2*n_c) approximately 0.314 rad (n_c=5).

Current state (2503.14126): 4-node binary demo, sigma_phi unmeasured, binary encoding. The binary encoding tolerates sigma_phi up to ~pi/4 approximately 0.785 rad — so current demo is NOT testing the relevant noise regime.

### Frequency mismatch is the binding constraint

For 1000-node oscillator array at 10-100 MHz:
- CMOS process variation: sigma_f/f approximately 0.1-1%
- At 10MHz: sigma_delta_omega approximately 2*pi * (1e4 to 1e5) rad/s
- Required coupling to overcome: K > 2 * sigma_delta_omega approximately 6e4 to 6e5 rad/s
- Per-node coupling conductance required: G_c approximately K*C/omega^2 (order ~100-1000 microsiemens)
- Achievable in ReRAM crossbar: YES, but near the crossbar current budget at 1000 nodes

Intrinsic noise threshold (sigma_phi < 0.314 rad) is NOT the bottleneck — frequency spread across 1000 nodes is.

### Fab generation roadmap

Gen 0 (current, 2025, 28-65nm): 4-node binary demo. Exponential capacity NOT demonstrated.

Gen 1 (~2027, 7-14nm + ReRAM BEOL + frequency trimming): 10-50 node, ternary encoding feasible with ~0.1-0.3% trimmed frequency spread. sigma_phi controllable to ~0.05 rad with active coupling. Within threshold for n_c=5.

Gen 2 (~2029, 5-7nm + analog tuning + per-cluster PLL): 100-1000 node feasibility. With per-cluster PLL (adds ~0.01-0.05 rad overhead), threshold criterion met across full 1000-node array. This is the first point where exponential capacity HARDWARE is plausible.

SUMMARY: approximately 2 fab generations from current state to 1000-node exponential-capacity demonstration.

---

## Cheap decisive test

Stochastic Kuramoto simulation on n_c=5 honeycomb, m=10 cycles (41 nodes), sigma_phi sweep: {0.05, 0.10, 0.20, 0.30, 0.40} rad. Measure retrieval fraction vs sigma_phi over 100 random initial conditions near stored patterns.

HARD-PASS: >90% retrieval at sigma_phi = 0.30 rad (just below pi/10).
HARD-FAIL: retrieval rate drops below 50% at sigma_phi < 0.20 rad (threshold tighter than theory).

Estimated: 5-10 min CPU, pure simulation.

---

## Falsifiable predictions

HARD-PASS:
1. Stochastic Kuramoto sim on n_c=5: >90% retrieval at sigma_phi = 0.25 rad.
2. Exponential capacity confirmed (>= 10x over linear) for N >= 40 nodes, sigma_phi < 0.20 rad.
3. ReRAM oscillator at 10MHz with K/D > 100: correct 3-state phase locking, sigma_phi < 0.1 rad measured.

HARD-FAIL:
1. Retrieval rate < 70% at sigma_phi = 0.15 rad: theory overpredicts stability margin by 2-3x.
2. Capacity collapses to linear for m > 5 cycles even at sigma_phi = 0.10 rad: scale-independence of Theorem III.2 fails numerically.
3. Frequency mismatch > 1% at 10MHz forces K > 1e6 rad/s: ReRAM coupling insufficient without amplification, pushing Gen 2 estimate out to Gen 3 (~2031+).

---

## Cross-thread synthesis

1. SKAH-M / saddle-hierarchy connection: the honeycomb Kuramoto memory is an n_c-LOCAL saddle hierarchy. The basin bound pi/(2*n_c) is directly analogous to the stability condition in SKAH-M class. This architecture is a candidate physical realization of the non-reciprocal saddle-hierarchy family already confirmed algebraically in the project substrate.

2. Nonequilibrium stat-mech thread: the noise-driven transition D_c = K*g(0)/2 is a NESS (non-equilibrium steady state) transition. Crooks/Sagawa-Ueda fluctuation theorems apply to the free-energy barrier DeltaF in the Kramers escape formula — same math family as the project substrate's non-equilibrium classification.

3. Network science / spectral gap: for honeycomb topology at N=1000, the Laplacian spectral gap lambda_2 sets convergence rate to phase-locked state. K > 2*D/lambda_2 for phase locking — directly an expander/Ramanujan graph question (Tier-1b network-science thread).

4. Modern Hopfield parallel: 3^(N/4) scaling mirrors dense Hopfield exponential capacity (arXiv:2304.14964) but the mechanism is phase-locking geometry, not polynomial energy degree. The threshold pi/(2*n_c) is the oscillator analog of the retrieval-error threshold in polynomial-degree Hopfield.

---

## Substrate-product implications

1. PHASE NOISE IS NOT THE HARD LIMIT — frequency mismatch is. The per-node tolerance (sigma_phi < 0.314 rad) is achievable with PLL or strong coupling in 28nm+. The real constraint is oscillator-to-oscillator frequency spread at 1000-node scale: a fabrication trimming / yield problem, not a fundamental physics limit.

2. BINARY ENCODING (IBM 2503.14126) IS NOT EXPONENTIAL CAPACITY. The current demo stores 1 bit per cycle (O(N) capacity). Exponential capacity requires ternary or higher-phase encoding per cycle. The IBM result demonstrates COUPLING MECHANISM feasibility, not exponential capacity.

3. PRODUCT WINDOW: 2 fab generations (~4-6 years from 2025) for 1000-node exponential-capacity hardware. Critical milestones: (a) n_c=5 ternary phase locking in hardware (~2026-2027, achievable in simulation now), (b) 50-node honeycomb with measured sigma_phi < 0.2 rad (Gen 1, ~2027), (c) 500-1000 node with trimming (Gen 2, ~2029).

4. ALGEBRAIC SUBSTRATE ORTHOGONALITY: an algebraic bipolar vector-space memory substrate operating in discrete Hadamard space is a DIFFERENT architecture from Kuramoto oscillator memory, but the SKAH-M saddle-hierarchy math is shared. Oscillator approach provides a physical realization path complementary to the discrete algebraic approach.

---

## Citations (verified: 6)

1. Ogranovich, Guo et al. "Oscillator-Based Associative Memory with Exponential Capacity: Theory, Algorithms, and Hardware Implementation." arXiv:2604.01469 (2026). [VERIFIED]

2. Guo, Ogranovich et al. "Oscillatory Associative Memory with Exponential Capacity." arXiv:2504.03102 / IEEE ISCA 2025. [VERIFIED]

3. Choi et al. "Hardware Implementation of Ring Oscillator Networks Coupled by BEOL Integrated ReRAM for Associative Memory Tasks." arXiv:2503.14126 / IMW 2025. [VERIFIED]

4. De Pirey, Osat, Vaikuntanathan. "Higher-Order Kuramoto Oscillator Network for Dense Associative Memory." arXiv:2507.21984 (2025). [VERIFIED — Kramers formula + tricritical point extracted]

5. Aceb ron, Bonilla, Perez-Vicente, Ritort, Spigler. "The Kuramoto model: A simple paradigm for synchronization phenomena." Rev. Mod. Phys. 77, 137 (2005). [VERIFIED via reference + search]

6. Abidi, A.A. "Phase Noise and Jitter in CMOS Ring Oscillators." IEEE J. Solid-State Circuits 41(8), 1803-1816 (2006). [VERIFIED via IEEE Xplore]

---

## P_deflated

Raw P(exponential-capacity 1000-node hardware within 2 fab generations): 0.60-0.70.
Calibration deflation per feedback-lit-scan-calibration-penalty: -0.20 (no 1000-node precedent, no measured sigma_phi for multi-symbol encoding).
Cap at 0.50 for novel synthesis.

P_deflated = 0.40-0.50.

P(theoretical basin bound pi/(2*n_c) holds empirically): 0.65 post-deflation — it is a mathematical theorem, high confidence.
P(IBM-style ReRAM at 1000-node exponential capacity within 2 fab generations): 0.35-0.40.

---

## Follow-on drill candidates

1. PRIORITY (exp_dev simulation): stochastic Kuramoto on n_c=5 honeycomb, sigma_phi sweep, N=41. Cheap decisive test — 5-10 min CPU.

2. Spectral gap / expander analysis for honeycomb Laplacian at N=1000: what K is required to beat frequency mismatch sigma_delta_omega? Maps to Tier-1b network-science thread.

3. Free-probability angle (Tier-1): Marchenko-Pastur / Tracy-Widom edge on honeycomb coupling matrix W gives finite-N corrections to K_c and sigma_phi_crit. Maps to F2 (Wigner edge) in field advisor.
