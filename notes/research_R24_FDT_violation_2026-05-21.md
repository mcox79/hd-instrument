# Research R24 — FDT violation + two-temperature substrate dynamics

**Topic.** Strategy's R24 (HIGH PRIORITY, cycle 27 followup): does
substrate exhibit measurable FDT violation, and does the FDT-derived
effective temperature T_eff correspond to substrate's empirical β=32?
Grounds Bet G ✅ TEMPSCALE in spin-glass theory. Extends R23's
marginal-stability framework (aging IS the out-of-equilibrium
signature predicted by FRSB).

**Date.** 2026-05-21.

**Status.** Research note, two passes complete. Pass 1 used a **real
external literature scan** via Agent subagent (~5 min, 20 tool uses,
26+ verified citations 1957-2026). Seventeenth consecutive cycle
following post-audit protocol.

**HEADLINE finding (per [[feedback-no-smoke]])**: FDT violation IS
substrate-measurable in principle (direct Hopfield-aging precedent:
Iguain-Cannas 2001, Almeida-Iguain-Cannas cond-mat/0007036). **BUT**:
the substrate-specific claim that β=32 corresponds to a parameter-
free FDT-derived T_eff is an **empirical hypothesis**, NOT a
theorem. Substrate's deterministic retrieval requires noise
calibration to measure absolute T_eff; otherwise only the X(C) ratio
is measurable. T_eff at substrate's exact α=0.153 is not pre-computable
in closed form from existing literature — needs the explicit Parisi
function for Hebbian Hopfield.

R24 produces a **measurement protocol** the substrate can implement
to test the β=32 ↔ T_eff hypothesis, NOT a derivation of β=32 from
first principles.

---

## Pass 1 — External literature scan (verified)

Generic statistical-physics queries via subagent: "Fluctuation-
Dissipation Theorem violation glassy," "Cugliandolo-Kurchan effective
temperature," "two-temperature thermodynamics," "aging dynamics SK
model," "Crisanti-Ritort FDT violation review," etc. No substrate
fingerprint.

### 1.1 FDT — foundational

**Kubo 1957** *J. Phys. Soc. Japan* 12:570: equilibrium fluctuation-
dissipation theorem relates linear response χ(t,t_w) to two-time
correlation C(t,t_w):

  **T · ∂χ(t,t_w)/∂t_w = − ∂C(t,t_w)/∂t_w**

Equivalently: χ(t,t_w) = (1/T)[C(t,t) − C(t,t_w)] in equilibrium.

Rests on: (a) time-translation invariance (TTI), (b) detailed balance.

**Cugliandolo-Kurchan 1993** (arXiv:cond-mat/9311016, PRL 71:173;
J. Phys. A 27:5749): for slowly relaxing systems that never
equilibrate (mean-field spin glasses, structural glasses, coarsening),
**TTI is broken at long times**, and FDT must be generalized.

**Crisanti-Ritort 2003** (arXiv:cond-mat/0212490, J. Phys. A 36:R181):
canonical review of FDT violation in glasses.

### 1.2 The FDT ratio X(C, t, t_w)

Generalized FDT:
  **T · ∂χ/∂t_w = − X(t,t_w) · ∂C/∂t_w**

- X = 1: FDT recovered (equilibrium)
- X < 1: FDT violated (aging regime)

**Cugliandolo-Kurchan 1994** showed for SK and spherical p-spin that
asymptotically X depends on two times only through correlation:
**X(t,t_w) → X(C(t,t_w))**.

**Effective temperature**: T_eff(C) = T_bath / X(C).

For 1RSB models: X(C) piecewise constant (X=1 above q_EA, X=m below).
For continuous (full) RSB (SK, FRSB): X(C) continuous function — the
inverse of Parisi function q(x).

**Franz-Mézard-Parisi-Peliti 1998** (arXiv:cond-mat/9803108) proved
within RSB field theory:

  **x(q) = ∫_{−1}^q P(q') dq'**

So **off-equilibrium X(C) is rigorously linked to the static cumulative
overlap distribution**. FDT ratio is a direct dynamical probe of the
static Parisi q(x).

### 1.3 Cugliandolo-Kurchan foundational results

**Cugliandolo-Kurchan 1993** analyzed spherical p-spin model in
thermodynamic limit. Below T_d (dynamical transition), relaxation
splits:

**Stationary regime** (t − t_w ≪ t_w):
- C and χ are TTI
- Equilibrium FDT holds
- C decays from 1 to q_EA

**Aging regime** (t and t_w both large with t/t_w fixed):
- TTI broken
- FDT replaced by **χ − C ≈ x · (q_EA − C)/T_bath**
- x is the 1RSB breakpoint

**For SK with continuous RSB** (Cugliandolo-Kurchan 1994 +
Franz-Mézard Europhys. Lett. 26:209 1994):
- Aging regime has hierarchy of timescales
- X(C) varies continuously
- dX/dC = dq^{-1}/dC (reflects Parisi function q(x))

**Cugliandolo-Kurchan-Peliti 1997** PRE 55:3898: interpret X(C)
thermodynamically:
- At each timescale system equilibrates with thermometer reading T_eff(C)
- Heat flows from "hotter" slow modes to colder modes
- T_eff has operational properties of thermodynamic temperature

**Kurchan 2005** *Nature* 433:222: modern overview.
**Cugliandolo 2011** *J. Phys. A* 44:483001 (arXiv:1104.4901): canonical
comprehensive treatment.

### 1.4 Recent rigorous status

**Bernaschi-Billoire-Maiorano-Parisi-Ricci-Tersenghi 2020** PNAS
117:17522 (arXiv:1906.11195): large-scale simulation showed
**Cugliandolo-Kurchan weak ergodicity breaking (WEB) assumption is
violated in SK and Viana-Bray at finite N** — aging trapped in
confined region. **Strong ergodicity breaking**.

**Folena-Franz-Ricci-Tersenghi 2023** PRL: extended to mixed p-spin
models.

**Substrate-relevant caveat**: at substrate's N=4096, asymptotic
Cugliandolo-Kurchan predictions may not apply quantitatively.
Qualitative picture (T_eff > T_bath, X(C) related to RSB structure)
survives; quantitative predictions for finite N are NOT yet settled.

### 1.5 Two-temperature thermodynamics

For aging glasses below T_d, TWO temperatures coexist:
- **T_bath**: actual heat-bath temperature (thermostat)
- **T_eff(C) = T_bath / X(C)**: temperature governing slow modes

For C > q_EA (fast modes, FDT plateau): T_eff = T_bath.
For C < q_EA (slow aging modes): **T_eff > T_bath** — system is
"hotter" than environment in slow modes.

**Cugliandolo-Kurchan-Peliti 1997**: T_eff has thermodynamic-
temperature properties:
1. Controls direction of heat flow between coupled subsystems with
   overlapping timescales
2. Acts as thermalization criterion for "thermometer" degrees of
   freedom whose intrinsic timescale matches slow modes
3. Observable-independent within given timescale sector

**Berthier-Barrat 2002** (*J. Chem. Phys.* 116:6228; PRL 89:095702):
verified T_eff thermodynamic properties in sheared supercooled
liquids.

### 1.6 Standard FDT-violation measurement protocol — Crisanti-Ritort 2003

**FD plot protocol** (Crisanti-Ritort §3):

1. Prepare system, quench at t=0.
2. At waiting time t_w, apply small perturbing field h.
3. Measure integrated response χ(t,t_w) for t > t_w; measure
   unperturbed correlation C(t,t_w).
4. **Parametric plot**: χ(t,t_w) vs C(t,t_w) with t as curve parameter,
   fixed t_w large.
5. **Slope of parametric curve**:
   - −1/T_bath in stationary FDT plateau (C > q_EA)
   - **−1/T_eff(C)** in aging branch

**For FRSB**: FD plot below q_EA is continuously curved arc whose
slope traces −1/T · dx/dq → reconstructs Parisi function via
dχ/dC = −x(q(C))/T_bath.

**For 1RSB**: FD plot has single straight kink at q_EA.

**First experimental FD plot** (Hérisson-Ocio 2002 PRL 88:257202,
arXiv:cond-mat/0112378): CdCr_{1.7}In_{0.3}S_4 spin glass.

**Janus Collaboration 2017** PNAS 114:1838 (arXiv:1610.01418):
extracted X(C) in 3D Edwards-Anderson; constructed statics-dynamics
dictionary mapping aging X(C) to equilibrium P(q).

### 1.7 Substrate-applicable observables and protocol

Translating to vector outer-product associative memory at α=0.153:

**System variable σ_i**: each component (bipolar HD vector entry)
plays role of Ising spin.

**Correlation C(t, t_w)** = (1/N) Σ_i ⟨σ_i(t) σ_i(t_w)⟩ across
iterative-retrieval trajectories from fixed initial query, t indexing
retrieval steps and t_w a chosen "age" step.

**Response**: perturb stored memory pattern ξ^μ at time t_w by small
field h conjugate to σ along that pattern (add ε ξ^μ_i to local
field). Measure trajectory deflection: χ(t,t_w) = (1/N) Σ_i
∂⟨σ_i(t)⟩/∂h|_{h=0}.

**If substrate's iterative-retrieval dynamics violates TTI** (which
any aging system in FRSB must), one can construct FD parametric plot
exactly as in Crisanti-Ritort 2003 §3. Protocol is in-principle
measurable: no exotic equipment, only paired runs with and without
perturbation.

**CRITICAL CAVEAT (per [[feedback-no-smoke]])**: standard FDT-violation
protocol presumes thermal Langevin/Glauber process with bath at known
T_bath. **If substrate's iterative update is DETERMINISTIC (greedy
retrieval), there is no T_bath; X(C) is ill-defined in usual sense.**

Empirical β=32 must therefore be defined operationally:
- As inverse temperature of effective noise injected (or implicit) in
  retrieval step
- OR via CKP operational definition: couple slow auxiliary degree of
  freedom and measure its temperature from its own FDT

### 1.8 Direct Hopfield precedents

**Iguain-Cannas 2001** *Physica A* 296:39 ("Aging in the retrieval
phase of the Hopfield model"): studied aging C(t,t_w) and χ(t,t_w) in
Hopfield at α above and below AGS retrieval boundary.

**Almeida-Iguain-Cannas** (arXiv:cond-mat/0007036, "Out of Equilibrium
Dynamics of the Hopfield Model in its spin-glass phase"): confirmed
that for **α > α_c (in SG phase)**, Hopfield shows SK aging
phenomenology, with TTI broken and non-trivial X(C).

**Substrate-applicable**: α=0.153 > α_c=0.138 → substrate IS in SG
phase where these results apply.

### 1.9 Connection to SGD effective noise (ML analog)

**Mignacco-Urbani 2022** arXiv:2112.10852 "The effective noise of SGD":
in under-parametrized regime, SGD reaches steady state with T_eff
defined via FDT from DMFT. **T_eff quantifies SGD algorithmic noise.**

**Mignacco-Krzakala-Urbani-Zdeborová 2020** PNAS / NeurIPS: dynamical
mean-field theory of SGD as Langevin process with memory kernel.

**Substrate-applicable**: substrate's iterative delta-rule training
IS a high-D SGD; Mignacco-Urbani framework directly applies if
substrate has any stochasticity (random batch sampling, dropout, etc.)

### 1.10 Recent (2020-2026) developments

- **arXiv:2506.14214 (2025)**: FDT violation during domain growth in
  long-range Ising model — super-universal scaling of X(C)
- **arXiv:2501.00338 (2025)**: universal activated aging framework
- **Berthier-Kurchan 2013** Nat. Phys. 9:310: nonequilibrium glass
  transitions in driven/active matter
- **Petrelli et al. 2018** EPJ E 41:128: operational T_eff in active
  fluids

### 1.11 Materials physics analog (LOAD-BEARING)

Substrate at α=0.153 IS rigorously a Hopfield-type disordered Ising
model on complete graph with Hebbian couplings:
  J_{ij} = (1/N) Σ_μ ξ^μ_i ξ^μ_j

At α=0.153 couplings have **SK-like marginal statistics in the
spin-glass phase**. Crisanti-Sommers-style FRSB applies (per R23
findings).

**BSC bipolar atoms ↔ Ising spins** is exact mapping.

Spin-glass / aging theory applies directly:
- Parisi q(x), Crisanti-Sommers free energy functional
- Pankov low-T asymptotics (cond-mat/0512253)
- Auffinger-Chen rigorous FRSB existence at low T (arXiv:2504.00269)

**For substrate**: FDT-violation prediction inherits SK results,
**modified by Hopfield-specific eigenvalue spectrum** (Marchenko-
Pastur with patterns).

---

## Pass 2 — Substrate-specific drill

### 2.1 The honest reframe of R24's question

R24's question ("does FDT violation correspond to β=32?") has **NO
pre-determined answer from existing literature**.

Specifically:
- **In closed form, T_eff at α=0.153 for Hopfield is not computed**
  in published papers. Would require explicit Parisi function for
  Hebbian Hopfield in SG-dominant phase (Steffan-Kühn 1994 framework
  extended with specific aging analysis).
- **The hypothesis that β=32 = T_eff^{-1}** is **empirical, not
  theoretical**. To test, substrate must perform FD plot measurement.
- **Substrate's deterministic retrieval lacks T_bath** — measurement
  needs noise calibration step OR CKP thermometer-coupling protocol.

**Per [[feedback-no-smoke]]**: I should NOT manufacture a derivation
of β=32 from FDT that doesn't exist. The honest answer:
- FDT violation IS predicted (substrate in FRSB phase per R23)
- T_eff > T_bath in slow modes
- Specific T_eff value requires substrate-specific measurement
- β=32 ↔ T_eff connection is testable hypothesis, not theorem

### 2.2 Substrate-applicable measurement protocol

**Step 1: Noise calibration** (mandatory for absolute T_eff)

Substrate's deterministic retrieval lacks T_bath. Inject explicit
Gaussian noise of known temperature T_inject:

```text
Modified substrate retrieval:
  current = current + sqrt(2 T_inject) * gaussian_noise(N)
  next = argmax(W @ current)  # or softmax sampling at β=32
```

Now T_bath = T_inject is well-defined.

**Step 2: Paired-trajectory measurement**

```text
For each trial (5 seeds):
  Initialize: query_initial = random_bipolar(N, seed)

  Trajectory A (unperturbed):
    for t in range(num_steps):
      sigma_A[t] = substrate_retrieve(query_initial, W, noise=T_inject)

  Trajectory B (perturbed):
    apply h ε * pattern_μ at time t_w
    for t in range(t_w, num_steps):
      sigma_B[t] = substrate_retrieve(perturbed_state, W, noise=T_inject)

  C_t_tw = (1/N) Σ_i sigma_A[i, t] * sigma_A[i, t_w]
  chi_t_tw = (1/(N ε)) Σ_i (sigma_B[i, t] - sigma_A[i, t]) * pattern_μ[i]
```

**Step 3: FD plot**

Parametric plot χ(t, t_w) vs C(t, t_w) with t curve parameter, t_w
fixed:
- Stationary plateau (C > q_EA): slope = −1/T_bath (calibration check)
- Aging branch (C < q_EA): slope = −1/T_eff(C)

**Step 4: Extract T_eff**

For FRSB: continuous curve in aging branch. Fit slope at characteristic
overlap (e.g., C=0.5 or C→0).

For substrate: report T_eff(C) curve, compare to T_inject baseline.

### 2.3 The β=32 hypothesis test

**Substrate-relevant hypothesis**: substrate's empirical optimal β=32
(per Bet G ✅ TEMPSCALE) corresponds to FDT-violation-derived T_eff.

**Test**:
1. Run protocol above at T_inject = 0.5 (well above T_g ≈ 1.39
   wait that's wrong — T_g is HIGH, β_g is LOW)

Actually let me re-check: T_g = 1.39 → β_g = 0.72 = SG transition.
β=32 → T = 0.031 (much lower than T_g).

So we need T_inject << 1.39 to be in SG phase. Try T_inject = 0.1.

```text
T_inject_sweep = [0.05, 0.1, 0.2, 0.5, 1.0]  # all below T_g ≈ 1.39
                                              # substrate in SG phase

for T_inject in T_inject_sweep:
  T_eff_aging = measure_T_eff_from_FD_plot(T_inject)

  # Hypothesis: T_eff is approximately constant ≈ 0.031 = 1/32
  # regardless of T_inject (within FRSB universality class)
```

**Strong test**: if T_eff at various T_inject ALL converge to ≈ 0.031
(= 1/32), substrate's β=32 IS the FDT-violation effective temperature.

**Weak test**: T_eff grows with T_inject (no universal value); β=32
is empirical-fit not FDT-derived.

### 2.4 Substrate-novel publishable contribution

Per the lit scan, **no published FDT-violation measurement exists for
outer-product associative memory at substrate's specific α, N**.

Iguain-Cannas 2001 and Almeida-Iguain-Cannas 2000 covered Hopfield
aging at different α; substrate's α=0.153 specifically is unexplored
for FDT violation in this published literature.

**Substrate-novel claim opportunity** (if R24 experiment succeeds):
- First published FD plot for Hebbian Hopfield at α=0.153, N=4096
- First substrate-specific T_eff measurement
- Test of β=32 = T_eff hypothesis

**Per [[feedback-no-papers-product-only]]**: publishability is
side-effect. Product-relevance: identifies whether β=32 has
parameter-free physical origin (T_eff) or is empirical tuning.

### 2.5 Strong-ergodicity-breaking caveat (Bernaschi 2020)

**Bernaschi-Billoire-Maiorano-Parisi-Ricci-Tersenghi 2020** PNAS:
**Cugliandolo-Kurchan WEB assumption violated at finite N in SK**.
Substrate at N=4096 may exhibit this.

**Substrate-relevant implication**:
- Asymptotic Cugliandolo-Kurchan FDT-violation predictions may not
  apply quantitatively
- T_eff(C) might be ill-defined as asymptotic limit
- Empirical FD plot may show structure but not match Parisi-prediction
  exactly

**Honest assessment**: substrate's T_eff measurement is empirical
characterization; rigorous theoretical interpretation depends on
whether substrate exhibits strong-ergodicity-breaking (folder
exploration) or weak-ergodicity-breaking (free wandering).

### 2.6 Independent ranking of FDT-related research questions

Strategy framed R24 as "does FDT violation correspond to β=32?"

Per the lit scan, my refined ranking of substrate-applicable R24 sub-
questions:

1. **Does substrate exhibit FDT violation at all?** (Aging vs
   equilibrium): predicted YES per R23 FRSB regime + Almeida-
   Iguain-Cannas Hopfield-SG-phase results. P ≈ 80-90%.

2. **Is X(C) substrate-measurable?** YES in principle with noise
   calibration. Standard Crisanti-Ritort 2003 protocol. P ≈ 90%.

3. **Does T_eff(C) match β=32?** Untested hypothesis. P ≈ 30-50%
   (no theoretical pre-prediction; substrate-specific measurement
   required).

4. **Is T_eff parameter-free identification of substrate's optimal
   calibration?** Even weaker; requires hypothesis #3 to hold AND
   T_eff to be universal across T_inject. P ≈ 15-30%.

5. **Does substrate exhibit strong ergodicity breaking?** Bernaschi
   2020-style. Could distinguish substrate dynamics regime.
   P ≈ 40-60% (substrate at finite N=4096 may exhibit this).

---

## Specific experimental design (pseudocode)

**Experiment**: `wave14_R24_FDT_violation_v1` — measure substrate's
FDT-ratio X(C) via FD plot protocol.

```text
config:
  N = 4096
  alpha = 0.153
  K = int(alpha * N) = 627
  num_steps = 10000  # iterative retrieval steps
  t_w_sweep = [100, 500, 1000, 5000]  # waiting times
  T_inject_sweep = [0.05, 0.1, 0.2, 0.5]
  num_perturbation_trials = 100  # for averaging χ
  seeds = [7, 17, 23, 31, 41]
  perturbation_strength = 0.01  # small h

setup_per_seed(seed):
  patterns = random_bipolar(N, K, seed=seed)
  W = (1/N) * patterns @ patterns.T
  return W, patterns

trajectory_with_noise(W, query_initial, num_steps, T_inject, seed):
  trajectory = zeros(num_steps, N)
  trajectory[0] = query_initial
  for t in range(1, num_steps):
    # Noisy retrieval step
    noise = sqrt(2 * T_inject) * gaussian(N, seed=seed+t)
    pred = W @ trajectory[t-1] + noise
    trajectory[t] = sign(pred)  # bipolar threshold
  return trajectory

measure_correlation(traj_A, t, t_w):
  return (1/N) * sum(traj_A[t] * traj_A[t_w])

measure_response(traj_A_unperturbed, traj_A_perturbed, pattern_mu,
                  perturbation_strength):
  diff = traj_A_perturbed - traj_A_unperturbed
  chi = (1/(N * perturbation_strength)) * sum(diff * pattern_mu)
  return chi

per_seed_FD_plot(seed, T_inject, t_w):
  W, patterns = setup_per_seed(seed)
  query_initial = random_bipolar(N, seed=seed+100)

  # Unperturbed trajectory
  traj_A = trajectory_with_noise(W, query_initial, num_steps, T_inject,
                                  seed=seed+200)

  # Perturbed trajectory: apply h * patterns[mu] at t_w
  pattern_mu = patterns[0]  # use first stored pattern
  perturbed_state = traj_A[t_w] + perturbation_strength * pattern_mu
  traj_B = trajectory_with_noise(W, perturbed_state, num_steps - t_w,
                                  T_inject, seed=seed+300)

  # Compute C and χ at various t
  C_values = []
  chi_values = []
  for t in range(t_w + 1, num_steps):
    C = measure_correlation(traj_A, t, t_w)
    chi = measure_response(traj_A[t_w:t], traj_B[:t-t_w],
                           pattern_mu, perturbation_strength)
    C_values.append(C)
    chi_values.append(chi)

  return C_values, chi_values

main:
  results = {}
  for T_inject in T_inject_sweep:
    for t_w in t_w_sweep:
      for seed in seeds:
        C, chi = per_seed_FD_plot(seed, T_inject, t_w)
        results[(T_inject, t_w, seed)] = (C, chi)

  # FD plot analysis
  for T_inject in T_inject_sweep:
    # Aggregate across seeds at large t_w
    C_all, chi_all = aggregate(results, T_inject, t_w_max)

    # FD plot: chi vs C parametric in t
    plt.plot(C_all, chi_all)

    # Fit slope in aging branch (C < q_EA)
    aging_indices = [i for i, c in enumerate(C_all) if c < 0.5]
    slope_aging = linear_regression_slope(C_all[aging_indices],
                                           chi_all[aging_indices])
    T_eff = -1 / slope_aging

    # Hypothesis test: does T_eff converge to ≈ 0.031 (= 1/32)?
    convergence_check[T_inject] = T_eff

verdict_logic:
  PASS_R24 iff (5-seed means):
    # FDT violation observed
    aging_branch_exists  # X(C) < 1 for some C

    # FD plot has structure consistent with FRSB
    slope_in_aging_branch is finite and negative

    # Substrate-specific β=32 hypothesis
    abs(T_eff_extracted - 0.031) / 0.031 < 0.5  # within 50% of 1/32

  STRONG_PASS iff:
    All above
    AND T_eff converges to ≈ 0.031 across T_inject_sweep (universal)

  KILL iff:
    No FDT violation observed (substrate in equilibrium)
    OR T_eff inconsistent with β=32 by >5×
    → substrate's β=32 is NOT FDT-derived; empirical tuning instead

  PARTIAL iff:
    FDT violation observed but T_eff doesn't match β=32
    → FDT-violation framework applies but β=32 has different origin
```

**Smoke test (queue_add gate)**: N=512, single T_inject=0.1, single
t_w=100, 1 seed. Target ~30s. Oracle: C(t, t_w) decreases with t;
chi(t, t_w) increases with t.

**Self-test (4 synthetic cases)**:
- T_inject=0 (deterministic retrieval): predict no FDT violation
  (system is at "zero temperature equilibrium")
- T_inject>>T_g (paramagnetic regime): predict X(C)=1 everywhere
  (no aging)
- T_inject<<T_g (deep SG): predict X(C)<1 in aging branch (FRSB)
- α=0.05 retrieval regime: predict X(C)=1 (no aging in retrieval
  pocket)

**Wall budget**: ~2 GPU hours per seed for full sweep (4 T_inject × 4
t_w × 100 trajectories). Total: 10 hours for 5 seeds. Smoke ~30s.

---

## Materials analog (LOAD-BEARING — substrate IS aging system)

Per R23: substrate at α=0.153, β=32 is in **FRSB regime**. Per the
spin-glass literature: FRSB ⇒ aging dynamics ⇒ FDT violation.

**Substrate IS structurally a Hopfield-type Ising model on complete
graph with Hebbian couplings**:
- J_{ij} = (1/N) Σ_μ ξ^μ_i ξ^μ_j with bipolar ±1 patterns
- α=0.153 places substrate past retrieval pocket, in SG phase
- At low T (β=32 → T=0.031), substrate IS in deep FRSB regime

**FDT violation IS predicted to occur** per Cugliandolo-Kurchan 1994
SK analysis. Specifically:
- Two relaxation regimes: stationary FDT plateau + aging branch
- X(C) continuous function (FRSB)
- T_eff > T_bath in slow modes

**Substrate-relevant direct precedent**: **Almeida-Iguain-Cannas
cond-mat/0007036** ("Out of Equilibrium Dynamics of the Hopfield
Model in its spin-glass phase") confirmed for α > α_c (substrate's
regime), Hopfield shows SK aging phenomenology with TTI broken and
non-trivial X(C).

**Per [[feedback-materials-science-probe]]**: this is direct
mathematical applicability, NOT decorative analogy. 30+ years of
spin-glass FDT-violation theory (Cugliandolo-Kurchan 1993 → Crisanti-
Ritort 2003 → Cugliandolo 2011 → recent rigorous proofs) applies
directly to substrate.

**However** (per [[feedback-no-smoke]]): the **quantitative connection
to substrate's β=32 is NOT pre-determined** by theory. Substrate must
measure X(C) and extract T_eff empirically; the β=32 ↔ T_eff
hypothesis is testable, not theorem-derived.

---

## Falsifiable prediction

**Primary prediction (FDT violation existence)**:

At α=0.153, N=4096, T_inject < T_g = 1.39:
- **FDT violation observed**: X(C) < 1 in some C range
- **Aging regime exists**: TTI broken for C < q_EA
- **FD plot has structure consistent with FRSB**: continuous curve
  in aging branch (not 1RSB kink)

P(FDT violation observed) ≈ **80-90%** — direct prediction from R23
FRSB regime + Almeida-Iguain-Cannas Hopfield precedent.

**Stress prediction (β=32 hypothesis test)**:

For T_inject = 0.1 (moderately below T_g):
- T_eff(C) in aging branch should fall in range [0.05, 0.5]
- If hypothesis holds: T_eff ≈ 0.031 (= 1/32) at characteristic C
- If hypothesis fails: T_eff > 0.1 (no special relation to β=32)

P(T_eff matches β=32 within factor-of-2) ≈ **30-50%** — untested
hypothesis; substrate-specific calculation required.

P(T_eff universal across T_inject — STRONG match) ≈ **15-30%**.

**Kill criterion**:
- If no FDT violation observed across all T_inject < T_g: substrate
  is in unexpected equilibrium regime (contradicts R23 FRSB
  prediction)
- OR if T_eff is inconsistent with β=32 by >5×: substrate's β=32 is
  empirical tuning, NOT FDT-derived

**Falsifier for R23/R24 spin-glass framework**:
- If substrate exhibits NO aging at all (TTI holds for all t_w):
  substrate is escaping FRSB regime despite α=0.153. Would suggest
  substrate has dynamics that average across temperature range,
  invalidating single-T spin-glass framework. Major substrate-
  physics finding.

---

## Citations

1. **Kubo (1957). "Statistical-Mechanical Theory of Irreversible
   Processes."** J. Phys. Soc. Japan 12:570.
   — Foundational FDT.

2. **Cugliandolo, Kurchan (1993). "Analytical solution of the
   off-equilibrium dynamics of a long-range spin-glass model."**
   PRL 71:173. arXiv:cond-mat/9311016.
   — Foundational FDT-violation in p-spin / SK.

3. **Cugliandolo, Kurchan, Peliti (1997). "Energy flow, partial
   equilibration, and effective temperatures in systems with slow
   dynamics."** PRE 55:3898.
   — Operational T_eff definition and thermodynamic interpretation.

4. **Franz, Mézard, Parisi, Peliti (1998). "Measuring equilibrium
   properties in aging systems."** PRL 81:1758.
   arXiv:cond-mat/9803108.
   — X(C) = static x(q) identification.

5. **Crisanti, Ritort (2003). "Violation of the FDT in glassy systems:
   basic notions and numerical evidence."** J. Phys. A 36:R181.
   arXiv:cond-mat/0212490.
   — Canonical review; FD plot protocol.

6. **Almeida, Iguain, Cannas. "Out of equilibrium dynamics of the
   Hopfield model in its spin-glass phase."** arXiv:cond-mat/0007036.
   — **Direct Hopfield precedent**: confirms SK aging phenomenology
   at α > α_c (substrate's regime).

7. **Hérisson, Ocio (2002). "Fluctuation-Dissipation Ratio of a Spin
   Glass in the Aging Regime."** PRL 88:257202.
   arXiv:cond-mat/0112378.
   — First direct experimental FD plot in spin glass.

8. **Cugliandolo (2011). "The effective temperature."** J. Phys. A
   44:483001. arXiv:1104.4901.
   — Canonical comprehensive review.

9. **Bernaschi, Billoire, Maiorano, Parisi, Ricci-Tersenghi (2020).
   "Strong ergodicity breaking in aging of mean-field spin glasses."**
   PNAS 117:17522. arXiv:1906.11195.
   — Cugliandolo-Kurchan WEB violated at finite N (substrate-relevant
   caveat).

10. **Janus Collaboration (2017). "A statics-dynamics equivalence
    through the FDR provides a window into the spin-glass phase from
    nonequilibrium measurements."** PNAS 114:1838. arXiv:1610.01418.
    — Statics-dynamics dictionary mapping X(C) to P(q).

11. **Mignacco, Urbani (2022). "The effective noise of SGD."**
    J. Stat. Mech. arXiv:2112.10852.
    — SGD as FDT-violating dynamics; ML analog.

12. **Kurchan (2005). "In and out of equilibrium."** Nature 433:222.
    — High-level T_eff overview.

---

## Routing

- **Experiment Dev (E_R24)**: this note recommends building
  `wave14_R24_FDT_violation_v1` to measure substrate's X(C) via FD
  plot protocol. **Requires noise calibration step** (T_inject) since
  substrate's deterministic retrieval lacks T_bath. ~10 GPU hours
  full scan. Multi-probe verdict logic ready.

- **Strategy**: this note proposes:
  - cap_map row: "Substrate FDT violation / two-temperature dynamics"
    at 🔬 (experimental design ready; ~10 GPU hours to verdict)
  - HONEST framing: β=32 = T_eff hypothesis is **empirical, not
    theorem**. Test required; literature doesn't pre-determine
    answer.
  - On STRONG PASS: substrate-novel publishable finding (first FD
    plot for Hebbian Hopfield at α=0.153); β=32 has parameter-free
    physical interpretation via FDT.
  - On PARTIAL PASS (FDT violation but T_eff ≠ 1/32): substrate
    physics framework applies but β=32 has different origin.
  - On KILL: substrate is escaping FRSB regime; major substrate-
    physics finding requiring R23 reconsideration.

- **Research (this session, future cycles)**: R24 closes ✅ with
  measurement protocol + honest hypothesis framing. Remaining HIGH
  PRIORITY R# from cycle 27 followup: **R29** (ferromagnetism /
  magnetic domains, user-explicit HIGH). Plus MEDIUM: R17, R18, R27,
  R28.

**HONEST FINAL NOTE (per [[feedback-no-smoke]])**: R24's most important
contribution is **NOT a derivation of β=32 from FDT theory** (no such
derivation exists in literature without explicit Hopfield Parisi
function computation). It's a **measurement protocol** substrate can
implement to test whether β=32 has parameter-free physical
interpretation.

Per [[feedback-no-smoke]]: I am NOT manufacturing a connection that
doesn't exist. The hypothesis is testable but not theoretical.
Substrate's FDT-violation measurement would be substrate-novel
publishable (first for outer-product associative memory at substrate's
exact α=0.153, N=4096) regardless of whether β=32 matches T_eff.

Per [[feedback-dont-overextend-theorems]]: spin-glass theory predicts
FDT violation in FRSB regime (substrate qualifies). It does NOT
predict T_eff = 1/32 specifically. That's empirical, not theorem.
