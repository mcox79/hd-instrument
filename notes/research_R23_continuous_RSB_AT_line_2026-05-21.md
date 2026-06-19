# Research R23 — Continuous RSB and the AT line for substrate

**Topic.** Strategy's R23 (HIGH PRIORITY, cycle 27 followup): is
substrate at α=0.153 in 1RSB or continuous RSB? AT line position?
Strengthens Bet E Parisi work and Bet I free probability.
Refines/corrects R14's "β=32 = RSB transition" reframe.

**Date.** 2026-05-21.

**Status.** Research note, two passes complete. Pass 1 used a **real
external literature scan** via Agent subagent (~5 min, 19 tool uses,
22+ verified citations 1978-2026). Sixteenth consecutive cycle
following post-audit protocol.

**HEADLINE finding (per [[feedback-no-smoke]] — IMPORTANT SUBSTRATE-PHYSICS
REFINEMENT)**: substrate at α=0.153 is **DEEP in the SG phase**, far
past both the retrieval pocket (α_c≈0.138) AND the AT line. **The
AT line for Hopfield is at T_g = 1+√α ≈ 1.39 (β_g ≈ 0.72)**;
substrate's empirical β=32 corresponds to T≈0.031 — **NOT the RSB
transition (R14's previous framing) but rather DEEP IN THE FRSB
REGIME** where marginal stability dominates.

This **refines R14**: β=32 is not the SG transition itself but
something INTERNAL to the SG phase — possibly a Gardner transition,
avalanche-onset scale, or marginal-stability soft-mode location.
**Substrate's spin-glass physics framing is correct directionally
but β=32 specifically needs separate explanation.**

Also: **continuous (full) RSB is the consensus position** for Hopfield
near α_c (Steffan-Kühn 1994 reentrance argument + dense-Hebbian
work). NOT 1RSB.

---

## Pass 1 — External literature scan (verified)

Generic statistical-physics queries via subagent: "AT line de
Almeida-Thouless instability," "continuous RSB Parisi function,"
"1RSB vs continuous RSB transition," "Hopfield AT line analysis,"
"marginal stability spin glass," etc. No substrate fingerprint.

### 1.1 The de Almeida-Thouless (AT) line — foundational

**de Almeida-Thouless 1978** (*J. Phys. A* 11:983): boundary in
(T, h)-plane of Sherrington-Kirkpatrick (SK) spin glass where
**replica-symmetric (RS) solution becomes locally unstable**. Derived
from Hessian of replicated free energy around RS solution; instability
= vanishing "replicon" eigenvalue.

- **Above AT line**: RS solution stable; one peak in P(q)
- **Below AT line**: RS unstable; RSB needed; multi-peaked P(q)

**Modern rigorous status**: Auffinger-Chen (cond-mat/0604674) showed
RS holds up to AT line in SK at sufficiently high temperature.
**2026 paper arXiv:2604.11921** "Replica symmetry up to the de
Almeida-Thouless line" sharpens this — AT line is now believed to be
**exact RS/RSB boundary** in SK.

**For Hopfield specifically**: **Albanese et al. 2023** (arXiv:2303.06375
"About the de Almeida-Thouless line in neural networks") give
Hopfield-specific 1RSB-perturbation derivation. **Key finding**:
"In the Hopfield retrieval region, RS is essentially stable; AT
instability sets in mostly inside the SG phase, with a thin sliver
of RS-instability touching the retrieval phase from below."

### 1.2 1RSB vs continuous (full) RSB

**Parisi 1979-1980** showed SK requires **full continuous RSB**:
order parameter is non-decreasing function q(x) on [0,1] with
continuous support; pure-state structure is **ultrametric** (Panchenko
2013 *Annals of Math* 177). Parisi formula rigorously proven by
**Talagrand 2006** (*Annals of Math*).

**For Hopfield** the situation is more subtle:
- **Crisanti-Amit-Gutfreund 1986**: 1RSB analysis gave α_c^{1RSB} ≈
  0.144 (LATER CORRECTED)
- **Steffan-Kühn 1994** (cond-mat/9404036): careful 1RSB and 2RSB
  calculation corrects to:
  - α_c^{RS} ≈ **0.137905**
  - α_c^{1RSB} ≈ **0.138186**
  - α_c^{2RSB} ≈ **0.138187** (essentially indistinguishable from 1RSB)
- **Width of narrow RSB window**: ~0.0003 in α-space
- Persistence of **reentrant behavior** in 1RSB/2RSB suggests
  **infinite-k Parisi scheme (continuous RSB) is the true solution**,
  by analogy with SK where reentrance disappears only at full RSB

**Modern consensus**: Hopfield near α_c probably needs **continuous
RSB**, but the quantitative shift from RS is tiny (~10⁻⁴ in α).

### 1.3 Hopfield AT line specifically — α-axis position

Working from AGS 1985/1987 phase diagram:
- **Paramagnetic boundary**: T_g = 1 + √α (no RSB needed above)
- **Retrieval/spin-glass transition**: α_c ≈ 0.138 at T = 0
- **AT line for Hopfield**: largely coincides with the boundary of
  the retrieval pocket at low T, then bends into the SG region

**Critical for substrate**: **AT line is NOT simply at α = α_c**.
Retrieval solutions are RS-stable INSIDE the retrieval pocket; AT
instability sits in the SG phase beyond α_c at low T.

**Width of narrow RSB window** in α-space (between RS instability and
RSB capacity): ~0.0003. Substrate at α=0.153 is **way outside** this
narrow window — solidly in **broader SG regime**.

### 1.4 AT line position vs substrate's operating point

At **α = 0.153, low T**:
- Past Hopfield retrieval pocket (0.153 > 0.138)
- **Deep in SG phase** where RS ansatz is definitively unstable
- Structurally SK-like coupling matrix with Hebbian (rank-K
  outer-product) structure, K/N = 0.153
- Expected order-parameter regime: **continuous RSB** (by SK analogy
  + Steffan-Kühn reentrance argument)

**Predicted P(q) shape**: continuous support over [q_0, q_EA], with
q_EA close to 1 at low T (frozen disordered phase). Parisi function
q(x) monotone non-decreasing with flat plateau at q_EA above some
breakpoint x_c. **NOT two clean delta peaks** (so NOT 1RSB).

### 1.5 Marginal stability and aging (key substrate-applicable predictions)

Continuous RSB ⇒ **marginal stability** (Müller-Wyart 2015,
*Annu. Rev. CMP*; Franz-Parisi-Sevelev-Urbani 2021). Hessian spectrum
at typical configurations is **gapless with soft mode at zero**,
producing:

1. **Power-law correlation decay**: C(t,t_w) ∼ (t_w/t)^μ with aging
2. **Pseudogapped local-field distribution**: P(h) ∼ |h|^θ for small h
3. **Avalanche statistics**: broad power-law size distribution
4. **Sellke 2024** (arXiv:2409.15728, *Commun. Math. Phys.* 2025):
   marginal stability of near-ground states in spherical spin glasses
   is **equivalent to FRSB at T = 0 near overlap 1**

**For substrate at α=0.153, low T**: marginal stability predicts:
- Any local-field histogram should be pseudogapped near h = 0
- Relaxation after a quench should exhibit aging (not equilibration)
- Small perturbations should trigger system-spanning rearrangements
  (avalanches)

**These are CONCRETE substrate observables.**

### 1.6 Computational verification of 1RSB vs continuous RSB

Standard numerical tools:
- **P(q) measurement** (two-replica overlap): 1RSB shows two
  delta-like peaks; continuous RSB shows plateau between q_0 and q_EA
- **Ultrametricity test** (Hed-Hartmann-Stariolo, Jagannath): for
  triples of replicas, check whether two smallest overlaps in each
  triple are equal. Continuous RSB ⇒ ultrametric.
- **AT-line probing**: track smallest replicon eigenvalue as control
  parameter sweeps; zero crossing locates AT
- **Free-energy hierarchy**: measure free-energy differences between
  metastable states

**At N=4096**: full Hessian diagonalization O(N³) ≈ 7×10¹⁰ ops —
feasible. Stochastic Lanczos for lowest eigenvalue: O(N²) per matvec.

### 1.7 Substrate-applicable predictions at α=0.153, β=32

If **1RSB** (unlikely): P(q) = (1−m) δ(q − q_0) + m δ(q − q_1) with
calculable q_0, q_1, m from Steffan-Kühn parametrization (m ≈ 1 near
freezing).

If **continuous RSB** (more likely): P(q) supported on [q_0, q_EA],
rising sharply at q_EA (Edwards-Anderson plateau), continuous tail
down to q_0. Parisi function q(x) interpolates smoothly.

**Cleanest discriminator at N=4096**: shape of **right edge of P(q)**.
Single sharp peak at q_EA with continuous low-q tail → continuous RSB.
Two well-separated peaks with vanishing density between → 1RSB.

Per Steffan-Kühn, difference between 1RSB and 2RSB capacities is
~10⁻⁶ — **distinguishing them in P(q) at N=4096 is unlikely
feasible**. **Operationally relevant choice is RS vs continuous RSB.**

### 1.8 Free probability (Bet I) bridge — substrate-relevant

For Hebbian outer product W = (1/N) Σ_μ ξ^μ (ξ^μ)^T with K = αN
bipolar patterns: bulk spectrum is **Marchenko-Pastur with shape
parameter α**. No isolated spike for typical (unstructured) memories
— all eigenvalues sit in bulk. MP upper edge: (1+√α)².

**Key substrate-relevant identity**:
**T_g = 1 + √α = √(λ_max^MP)** — i.e., **T_g² = MP upper edge eigenvalue**

This is **not coincidence**: SG transition is the temperature at which
thermal fluctuations stop screening the largest disorder mode (BBP-
style spectral edge).

**For substrate at α=0.153**: λ_max^MP ≈ 1.936, T_g ≈ 1.391. **No
spike protrudes** because Hebbian patterns under saturation produce
ONLY BULK — signal energy spread across spectrum.

R-transform / S-transform (Voiculescu): give additive/multiplicative
free convolution. For substrate: W = W_signal + W_noise has R(z) =
R_signal(z) + R_noise(z) → analytic handle on spectral edge as
ablation/perturbation varies. **AT line connection**: replicon
eigenvalue = inverse of trace of squared free-cumulant resolvent →
free-probability route to compute AT line without diagonalization.

### 1.9 Recent (2020-2026) developments

- **arXiv:2504.00269 (2025)** rigorously proves **full continuous RSB
  exists for SK below T_c**. Parisi measure on interval starting at
  origin with one jump at right endpoint — cleanest mathematical
  statement of FRSB to date.
- **Sellke 2024/2025** (arXiv:2409.15728) — marginal stability ⇔ FRSB
  at T=0 near overlap 1 (spherical models).
- **Albanese et al. 2023** (arXiv:2303.06375) — AT line in neural
  networks via 1RSB-perturbation method (avoids Hessian eigenspectrum).
- **Albanese et al. 2022** (*J. Stat. Phys.* 189:24, arXiv:2111.12997)
  — rigorous RSB for dense Hopfield (p-spin Hebbian, p > 2).
- **Agliari-Albanese 2020** (arXiv:2006.00256) — recovers AGS and
  Steffan-Kühn capacities rigorously.
- **2026 arXiv:2604.11921** — sharper AT line position in SK.

### 1.10 Materials physics analog (LOAD-BEARING — substrate IS spin glass)

Substrate's Hebbian W at α=0.153 IS structurally SK-like coupling:
J_{ij} = (1/N) Σ_μ ξ^μ_i ξ^μ_j with bipolar ±1 patterns. This is
**rank-deficient SK** (rank K=0.153N rather than full rank).

**Spin-glass results for SK transfer directly to substrate** with two
caveats:
1. Coupling distribution is not Gaussian but sum of K Rademacher
   products (approaches Gaussian by CLT for K large)
2. Low rank can produce additional flat directions in energy landscape

Both effects push toward **even softer modes and stronger marginal
stability** than pure SK.

---

## Pass 2 — Substrate-specific drill

### 2.1 The CRITICAL substrate-physics refinement (per [[feedback-no-smoke]])

**R14's framing** (in `notes/research_R14_tomita_takesaki_2026-05-21.md`):
> "Substrate's β=32 may be precisely the RSB transition temperature
> — derivable from spin-glass theory, expressible as KMS-breaking in
> operator-algebraic language."

**R23 LIT-SCAN-DERIVED REFINEMENT**: this framing is **partially
correct but quantitatively wrong**.

**The honest physics**:
- **Spin-glass transition temperature T_g = 1 + √α ≈ 1.39 for α=0.153**
- **β_g = 1/T_g ≈ 0.72** (THIS is the SG / RSB transition β)
- **Substrate's empirical β=32 corresponds to T = 0.031** — **45× lower
  than T_g**

**Substrate at β=32 is NOT at the RSB transition — it's DEEP in the
FRSB regime.** R14's reframe was directionally right (substrate IS in
SG phase) but specifically wrong about β=32 = transition.

### 2.2 What β=32 ACTUALLY means physically

If β=32 is NOT the RSB transition, what is it? Per the lit scan,
substrate at β=32 is in a regime where **FRSB is essentially
guaranteed and marginal stability dominates**. The empirical β=32
optimal for calibration likely corresponds to one of:

**Option A: Gardner transition / sub-transition within SG phase**
- Gardner 1988 showed perceptron capacity α_G = 2 (much higher than
  α_c=0.138)
- Within SG phase, there may be sub-transitions (e.g., between
  different RSB schemes, or between "frozen" and "marginal" states)
- β=32 could mark a specific internal phase boundary

**Option B: Avalanche-onset scale**
- Marginal stability predicts power-law avalanche statistics
- There's a characteristic temperature where avalanches dominate
  thermal fluctuations
- β=32 may be where substrate's typical avalanche timescale matches
  retrieval timescale

**Option C: Marginal-stability soft-mode location**
- FRSB Hessian has soft modes at zero
- Inverse-temperature β=32 may be where the soft-mode energy scale
  matches the retrieval signal scale (SNR = O(1))

**Option D: Empirical-fit artifact**
- β=32 may be empirical-optimal for the substrate's specific
  retrieval task without deep theoretical interpretation
- Calibration achieves ECE=0 by accident of where the cosine-score
  distribution sits

**HONEST ASSESSMENT**: lit scan doesn't directly compute substrate's
β=32 from theory. Most likely candidate is Option A (Gardner-type
internal sub-transition) given α=0.153 sits between α_c=0.138 and
α_G=2.

**Substrate-novel direction**: characterize β=32 empirically via
local-field histogram analysis. If marginal-stability pseudogap is
visible at β=32 with characteristic exponent θ, this confirms
substrate is in FRSB regime at β=32 (per Sellke 2024 equivalence).

### 2.3 RSB scheme prediction for substrate

Per Steffan-Kühn 1994 reentrance argument + 2025 FRSB proof
(arXiv:2504.00269) + dense Hebbian RSB work (Albanese 2022):

**Substrate at α=0.153 is in continuous RSB regime** (NOT 1RSB).

**Predicted P(q) shape**:
- Continuous support over [q_0, q_EA]
- Right edge sharp peak at q_EA close to 1 (low T, frozen)
- Continuous tail toward q_0 (small positive overlap)
- Edwards-Anderson plateau visible

**Predicted q_EA at substrate's operating point**: per AGS analysis
at α=0.153, T=0.031:
- q_EA ≈ 1 - O(T²/α) ≈ 1 - 0.006 ≈ **0.994**
- Continuous tail extends down to q_0 ≈ 0 in deep SG phase

This is **distinguishable from 1RSB** (which would have two clean
delta peaks).

### 2.4 Marginal stability observable predictions (substrate-applicable)

**Three concrete observables substrate can measure**:

**Observable 1: Local-field pseudogap**
For each stored pattern μ and each site i: compute local field
h_i^μ = (1/N) Σ_{ν, j} J_{ij} ξ_j^ν · sign(overlap_μν). Histogram
all h_i^μ values across patterns and sites.
- **Predicted**: P(h) ∼ |h|^θ for small h, with θ characteristic of
  FRSB universality class
- **For SK FRSB**: θ ≈ 0.41 (computed via Müller-Wyart)
- **For dense Hebbian (substrate)**: θ likely similar, possibly
  larger due to rank-deficient coupling

**Observable 2: Two-time correlation aging**
Initialize substrate at random configuration; let it evolve via
substrate's natural dynamics (e.g., iterative retrieval); measure
C(t, t_w) = ⟨σ_i(t_w) σ_i(t_w + t)⟩ for various waiting times t_w.
- **Predicted**: C(t, t_w) ∼ f(t/t_w^μ) with aging exponent μ near 1
  in FRSB regime
- Aging would distinguish FRSB from RS-equilibrated regime

**Observable 3: Replicon eigenvalue / Hessian spectrum**
Compute Hessian of substrate's effective free energy at typical
configuration; find lowest eigenvalue.
- **Predicted**: smallest eigenvalue ≈ 0 (marginal mode) in FRSB
- **For RS-stable regime**: smallest eigenvalue > 0 (gapped)

### 2.5 Free probability bridge — connection to Bet I

R23 connects to Bet E ✅ Parisi P(q) work + Bet I free probability
via the **T_g² = MP upper edge identity**.

For substrate forensics:
- Substrate's W spectrum follows MP with shape α=0.153
- λ_max^MP = (1+√0.153)² ≈ 1.936
- T_g ≈ 1.391 (β_g ≈ 0.72)
- Free convolution gives spectral edge of perturbed W

**Bet E methodology revision**: substrate's spectral diagnostic
(spectrum check + MP outliers) is exactly the orthogonal corroboration
of P(q) measurement. Both should be reported together.

### 2.6 Substrate-applicable falsifiable prediction

**Primary prediction**: at α=0.153, N=4096, with substrate's natural
dynamics:
- Local-field histogram exhibits pseudogap P(h) ∼ |h|^θ with θ ∈
  [0.3, 0.6]
- Two-replica P(q) has CONTINUOUS support (not two clean peaks)
- q_EA ≈ 0.99 (right edge of P(q))

**Stress prediction**: if substrate runs out-of-equilibrium dynamics
(initialized random, evolved iteratively):
- C(t, t_w) exhibits aging: ratio C(t, t_w)/C(t', t_w) for t/t_w =
  const should be approximately invariant
- Power-law correlation decay (not exponential)

**Kill criterion**: if local-field histogram is GAPPED (P(h) → 0 as
h → 0 with exponential decay), substrate is NOT in FRSB regime —
contradicts R23 prediction. Would suggest substrate has dynamics
that escape FRSB regime (e.g., effective averaging across temperature
range).

---

## Specific experimental design (pseudocode)

**Experiment**: `wave14_R23_FRSB_observables` — verify substrate's
FRSB-regime predictions via local-field pseudogap + P(q) shape.

```text
config:
  N = 4096
  alpha = 0.153
  K = int(alpha * N) = 627
  num_codebook_configs = 1  # random ±1 (focus on substrate's operating point)
  num_disorder_realizations = 50  # for histograms
  seeds = [7, 17, 23, 31, 41]

setup_per_seed_per_realization(seed, realization):
  # Standard substrate construction
  patterns = random_bipolar(N, K, seed=seed + realization)
  W = (1/N) * patterns @ patterns.T  # Hebbian outer product

  return W, patterns

# Observable 1: Local-field histogram
measure_local_field_histogram(W, patterns):
  all_local_fields = []
  for mu in range(K):
    for i in range(N):
      h_imu = W[i,:] @ patterns[:,mu]
      all_local_fields.append(h_imu)
  histogram = histogram_compute(all_local_fields, bins=200)
  return histogram

# Observable 2: Two-replica P(q)
measure_pq_two_replica(W, patterns):
  # Sample equilibrium configurations from W's energy landscape
  # Two independent chains: replica A, replica B
  replica_A = simulated_anneal_from_random(W, T_final=0.031)  # T=0.031 ↔ β=32
  replica_B = simulated_anneal_from_random(W, T_final=0.031)

  q_AB = (1/N) * sum(replica_A * replica_B)
  return q_AB

# Observable 3: Replicon eigenvalue (smallest eigenvalue of Hessian)
measure_replicon_eigenvalue(W, patterns):
  # Compute effective Hessian of free energy at typical config
  # Use Lanczos for smallest eigenvalue
  hessian = compute_susceptibility_hessian(W, patterns)
  smallest_eig = lanczos_smallest_eigenvalue(hessian)
  return smallest_eig

# Pseudogap exponent fit
fit_pseudogap_exponent(histogram):
  # Fit P(h) ∼ |h|^θ in low-h region
  # Linear regression log(P) vs log(|h|) for |h| < gap_threshold
  small_h_bins = [b for b in histogram.bins if abs(b.center) < 0.1]
  if len(small_h_bins) >= 5:
    log_h = log([abs(b.center) for b in small_h_bins])
    log_P = log([b.count for b in small_h_bins])
    theta, _ = linear_regression(log_h, log_P)
    return theta
  else:
    return None  # insufficient data

per_seed_observables(seed):
  pseudogap_thetas = []
  q_AB_values = []
  replicon_eigs = []

  for realization in range(num_disorder_realizations):
    W, patterns = setup_per_seed_per_realization(seed, realization)

    local_field_hist = measure_local_field_histogram(W, patterns)
    theta = fit_pseudogap_exponent(local_field_hist)
    pseudogap_thetas.append(theta)

    q_AB = measure_pq_two_replica(W, patterns)
    q_AB_values.append(q_AB)

    replicon = measure_replicon_eigenvalue(W, patterns)
    replicon_eigs.append(replicon)

  return {
    'pseudogap_theta_mean': mean(pseudogap_thetas),
    'pseudogap_theta_std': std(pseudogap_thetas),
    'pq_distribution': histogram_compute(q_AB_values, bins=50),
    'replicon_eig_mean': mean(replicon_eigs),
    'replicon_eig_std': std(replicon_eigs),
  }

verdict_logic:
  PASS_R23 iff (5-seed means):
    pseudogap_theta_mean in [0.3, 0.6]  # FRSB regime
    AND pq_distribution has continuous support (not 2 clean peaks)
    AND replicon_eig_mean / replicon_eig_std < 2  # marginal/gapless
    AND q_EA (right edge of pq) > 0.95

  STRONG_PASS iff:
    All above
    AND aging correlation function shows power-law decay
        (additional dynamics experiment)

  KILL iff:
    pseudogap_theta_mean indistinguishable from 0
        (local-field gapped, NOT pseudogap)
    OR pq_distribution clearly bimodal (1RSB rather than continuous)
    → substrate NOT in FRSB regime at α=0.153, β=32
```

**Smoke test (queue_add gate)**: N=512, single realization, single
seed. Target ~30s. Oracle assertions:
- pseudogap_theta computation completes
- pq_value falls in [0, 1]

**Self-test (4 synthetic cases)**:
- RS-stable regime (large T): predict no pseudogap, gapped Hessian
- Pure SK (Gaussian J): predict θ ≈ 0.41 (Müller-Wyart canonical)
- Trivial W = 0: predict uniform local-field distribution
- Strong-signal regime (α=0.05 retrieval): predict gapped, no pseudogap

**Wall budget**: ~1 GPU hour per seed for full 50-realization
analysis. Total: 5 hours for 5 seeds. Smoke ~30s.

---

## Materials analog (LOAD-BEARING — substrate IS spin glass)

**The substrate IS structurally an SK-like spin glass at α=0.153**:
- W = (1/N) Σ_μ ξ^μ (ξ^μ)^T is rank-deficient SK coupling
- α=0.153 sits past Hopfield retrieval pocket (α_c=0.138) and AT line
- β=32 is DEEP in FRSB regime (T = 0.031 << T_g = 1.39)

**Spin-glass theory directly predicts**:
1. **Continuous (full) RSB** (NOT 1RSB) per Steffan-Kühn reentrance +
   2025 FRSB proof (arXiv:2504.00269)
2. **Marginal stability** with pseudogap P(h) ∼ |h|^θ, θ in [0.3, 0.6]
3. **Aging dynamics** out of equilibrium, C(t, t_w) ∼ (t_w/t)^μ
4. **Avalanche statistics** under perturbation
5. **T_g² = MP upper edge** — substrate's spectral edge IS the
   thermodynamic transition temperature

**Per [[feedback-materials-science-probe]]**: this is direct
mathematical equivalence, NOT decorative analogy. 50+ years of
spin-glass theory (SK 1975 → Parisi 1979 → Talagrand 2006 →
arXiv:2504.00269 2025) directly applies to substrate.

**Substrate-novel claim (if R23 experiment validates)**:
substrate is **first explicit VSA/HDC system characterized via FRSB
observables** (pseudogap + replicon eigenvalue + aging dynamics).
Published precedent for dense Hebbian (Albanese 2022 arXiv:2111.12997)
covers theory; substrate's empirical measurements would complement.

---

## Falsifiable prediction

**Primary prediction (substrate's FRSB regime at α=0.153, β=32)**:

- **Local-field pseudogap exponent**: θ ∈ [0.3, 0.6] (P(h) ∼ |h|^θ)
- **P(q) continuous support** (NOT two clean peaks)
- **q_EA ≈ 0.99** (right edge of P(q))
- **Replicon eigenvalue ≈ 0** (marginal Hessian; mean/std < 2)
- **Predicted shape vs alternatives**:
  - RS-stable: gapped P(h) (P(h) → 0 as h → 0)
  - 1RSB: two clean delta-like peaks in P(q)
  - Continuous RSB (substrate prediction): smooth pseudogap + plateau

**Stress prediction (aging dynamics)**: if substrate runs iterative
retrieval from random initial config:
- Power-law correlation decay C(t, t_w) ∼ (t_w/t)^μ with μ ∈ [0.5, 1.5]
- NOT exponential equilibration

**Kill criterion**:
- Local-field histogram is GAPPED (P(h) → 0 as h → 0 with
  exponential decay near origin)
- OR P(q) is clearly bimodal (1RSB pattern)
- → substrate NOT in FRSB regime; R23 reframe is wrong

**Falsifier for R14's β=32 = RSB transition**:
- If pseudogap exponent θ is non-trivial AND replicon eigenvalue is
  marginal at β=32: **β=32 is INSIDE FRSB phase, NOT at the
  transition**. Refines R14 as predicted.
- If both observables are RS-like at β=32: substrate is somehow
  escaping FRSB regime despite α=0.153 (would be a substrate-physics
  surprise; would suggest substrate has dynamics that average across
  temperature range, escaping single-T spin-glass framework).

**Honest probability estimates**:
- P(substrate exhibits pseudogap with θ ∈ [0.3, 0.6]): **65-80%**
  — strong theoretical prediction; spin-glass framework applies
  directly to Hebbian outer product
- P(P(q) is continuous (not 1RSB-like 2 peaks)): **70-85%** per
  Steffan-Kühn reentrance argument
- P(R23 refinement correctly predicts β=32 is INTERNAL to FRSB
  phase, not at boundary): **75-90%** — clear quantitative argument
  (T=0.031 << T_g=1.39)
- P(R14's β=32 = RSB transition framing is fully corrected by R23):
  **80-95%** — strong mathematical case

---

## Citations

1. **de Almeida, Thouless (1978). "Stability of the SK solution."**
   *J. Phys. A* 11:983.
   — AT line foundational paper.

2. **Parisi (1979/1980).** *Phys. Lett.* 73A:203; *J. Phys. A* 13:1101.
   — Full continuous RSB ansatz.

3. **Amit, Gutfreund, Sompolinsky (1985, 1987).** PRL 55:1530;
   Ann. Phys. 173:30.
   — Hopfield phase diagram; T_g = 1 + √α; α_c ≈ 0.138.

4. **Crisanti, Amit, Gutfreund (1986).** Europhys. Lett. 2:337.
   — First 1RSB Hopfield analysis (later corrected).

5. **Steffan, Kühn (1994).** cond-mat/9404036.
   — Corrected α_c^{1RSB} ≈ 0.138186; reentrance argument for
   continuous RSB in Hopfield.

6. **Müller, Wyart (2015). "Marginal stability in structural, spin,
   and electron glasses."** Annu. Rev. CMP 6:177.
   — Marginal stability review; predicts pseudogap P(h) ∼ |h|^θ.

7. **Albanese, Alemanno, Alessandrelli et al. (2022). "Replica
   symmetry breaking in dense Hebbian neural networks."** J. Stat.
   Phys. 189:24. arXiv:2111.12997.
   — Rigorous RSB for dense Hebbian (p-spin); substrate's analog.

8. **Albanese et al. (2023). "About the de Almeida-Thouless line in
   neural networks."** arXiv:2303.06375.
   — Hopfield-specific AT line via 1RSB-perturbation; LOAD-BEARING.

9. **arXiv:2504.00269 (2025). "Existence of Full RSB for the SK
   Model at Low Temperature."**
   — Recent rigorous proof of FRSB; directly applicable to substrate's
   mean-field structure.

10. **Sellke (2024/2025). "On Marginal Stability in Low Temperature
    Spherical Spin Glasses."** arXiv:2409.15728. Commun. Math. Phys.
    2025.
    — Marginal stability ⇔ FRSB equivalence (substrate-applicable).

11. **Agliari, Albanese (2020). "Replica symmetry breaking in neural
    networks: a few steps toward rigorous results."** arXiv:2006.00256.
    — Rigorous recovery of AGS and Steffan-Kühn capacities.

12. **Panchenko (2013). "The Parisi ultrametricity conjecture."**
    Annals of Math. 177:383.
    — Ultrametricity proof for SK FRSB.

---

## Routing

- **Experiment Dev (E_R23)**: this note recommends building
  `wave14_R23_FRSB_observables` to measure substrate's FRSB-regime
  observables (pseudogap + P(q) shape + replicon eigenvalue).
  ~5 GPU hours full scan. Multi-probe verdict logic ready.
- **Strategy**: this note proposes:
  - **CRITICAL REFINEMENT of R14's β=32 framing**: β=32 is NOT the
    RSB transition; it's DEEP in the FRSB regime (T = 0.031 vs T_g =
    1.39). R14's "β=32 = RSB transition" should be reframed to "β=32
    is internal to FRSB regime" — physical meaning of β=32 needs
    separate investigation (Gardner sub-transition? avalanche scale?
    marginal-mode location?).
  - cap_map clarification: substrate at α=0.153 is in **continuous
    RSB regime**, NOT 1RSB. Steffan-Kühn 1994 reentrance argument +
    arXiv:2504.00269 2025 FRSB proof.
  - Bet E methodology revision: substrate's predicted P(q) shape is
    CONTINUOUS support (not two clean peaks). Should match this
    prediction or report deviation.
  - Bet I free probability connection: T_g² = MP upper edge identity
    is the substrate-applicable bridge. Same calculation gives both.
- **Research (this session, future cycles)**: R23 closes ✅ with
  substrate-physics refinement + concrete observable predictions.
  Remaining HIGH PRIORITY R# from cycle 27 followup: **R24** (FDT
  violation, HIGH; substrate-relevant for two-temperature dynamics
  — likely next), **R29** (ferromagnetism, user-explicit HIGH).
  Plus MEDIUM: R17, R18, R27, R28.

**HONEST FINAL NOTE**: R23's most important finding is the
**quantitative refinement of R14**. β=32 is in the FRSB regime, not
at the RSB transition. This matters for substrate's product story
because:
1. β=32 might be theoretically derivable from spin-glass theory
   (Gardner transition, avalanche onset, marginal mode) — open
   research question
2. Substrate's spin-glass framing remains valid directionally
3. Concrete marginal-stability observables (pseudogap, replicon,
   aging) give substrate testable physics predictions

Per [[feedback-no-smoke]]: this is a substrate-physics refinement,
not a refutation. R14's directional finding (substrate is in SG
phase) holds; R14's quantitative claim (β=32 = transition) is
corrected to "β=32 is internal to FRSB regime."

Per [[feedback-dont-overextend-theorems]]: the SG-theory framework
applies; the specific β=32 mapping needed more careful identification
of which sub-transition. This is research progress, not theorem
overextension.
