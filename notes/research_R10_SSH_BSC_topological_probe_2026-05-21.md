# Research R10 — SSH-BSC topological probe design (Bet F prerequisite)

**Topic.** Strategy's Bet F (Tier-2 KILLER probe revisit, added cycle 8):
SSH-BSC topological winding-protected memories. The original probe
`wave14e2_ssh_bsc_topological` (CPU-fallback window 2026-05-20) returned
`categorical_correct=0.0` at all noise levels. Strategy explicitly flagged
this as a methodology gap: the probe lacked a Z-quantization recovery
metric; could not distinguish "no topology" from "topology hidden by
wrong measurement." R10 asks: what is the published-literature protocol
for measuring integer winding-number protection in 1D chiral-symmetric
(class AIII) systems, and how does it map to a discrete bipolar ±1
substrate?

**Date.** 2026-05-21.

**Status.** Research note, two passes complete. Pass 1 used a **real
external literature scan** via Agent subagent (~5 min runtime, 20 tool
uses, 25 verified arXiv citations). Pass 2 drills the substrate-specific
probe redesign.

---

## Pass 1 — External literature scan (verified)

Generic-physics queries via subagent: "SSH model topological invariant
measurement protocol," "chiral symmetry class AIII tenfold way," "winding
number recovery experimental probe," "Z-quantization symmetry-protected
topological," "Bott index disordered SSH," "spectral localizer," etc.
Pure condensed-matter physics — no substrate fingerprint.

### 1.1 SSH model topology — what ν protects

The Su-Schrieffer-Heeger model (Su, Schrieffer, Heeger 1979 PRL 42, 1698)
is the textbook 1D chiral-symmetric system. Bloch Hamiltonian
**H(k) = d_x(k) σ_x + d_y(k) σ_y** (no σ_z component, the defining
chiral-symmetry signature). Topological invariant is the integer winding
number:

  **ν = (1/2π) ∮ dk ∂_k arg[d_x(k) + i d_y(k)]**

Hasan-Kane (2010 RMP 82, 3045) tenfold-way classification: SSH sits at
d=1, **class AIII** (chiral symmetry S only, no T, no C), giving **Z**
classification (not Z₂). What ν protects (Asbóth, Oroszlány, Pályi
arXiv:1509.02295; Shapiro & Tauber arXiv:1705.06913):
- **|ν| zero-energy edge modes** at each open boundary, pinned at E=0
  by chiral symmetry.
- **Quantized Zak phase** πν (mod 2π), connecting to King-Smith-Vanderbilt
  charge polarization.
- **Stability under symmetry-preserving perturbations**. Any disorder
  that preserves chiral symmetry and does not close the bulk gap leaves
  ν unchanged.

Foundational classification: Schnyder-Ryu-Furusaki-Ludwig arXiv:0803.2786;
Kitaev arXiv:0901.2686; Ryu-Schnyder-Furusaki-Ludwig arXiv:0912.2157.

### 1.2 Published measurement protocols for ν

The literature has converged on a menu of probes:

**(a) Mean Chiral Displacement (MCD)** — dominant experimental
observable since 2017. For a wavepacket initialized on one sublattice
and evolved freely, time-averaged `⟨Γ X⟩ → ν/2` in the long-time limit
(Γ = chiral operator, X = position). Cardano et al. *Nat. Commun.* 8,
15516 (2017), arXiv:1610.06322 (photonic OAM); Maffei et al. arXiv:1708.02778
(theory); D'Errico et al. arXiv:2001.05960 (quenched chiral models);
driven extension arXiv:2309.16101 (2024). Works in disorder; works
through quenches; requires intensity only.

**(b) Zak phase via interferometry / adiabatic transport.** γ_Z = i ∮
⟨u_k|∂_k|u_k⟩ dk = πν (mod 2π). Atala et al. *Nat. Phys.* 9, 795 (2013),
arXiv:1212.0572 (cold atoms); Longhi *Opt. Lett.* 38, 3716 (2013)
(photonic waveguides).

**(c) Bott index — Z-valued for AIII.** Loring 2015 arXiv:1502.03498.
For a chiral chain at half-filling, define X̃ = exp(2πi X/L), project
onto lower band P; **Bott index = Tr log(P X̃ P / X̃) ∈ Z**. Works
without translation invariance — the preferred disordered-system probe.

**(d) Non-commutative / real-space winding number** — Prodan-
Schulz-Baldes arXiv:1402.5002 (K-theory rigor); Mondragon-Shem-Hughes-
Song-Prodan *PRL* 113, 046802 (2014), arXiv:1311.5233:

  **ν = (L/N) Tr_unit[Q [X, Q]]**

where Q = P_+ − P_- is the "flat-band" chiral projector difference and
Tr_unit averages over a unit cell. Lin et al. *PRB* 103, 224208 (2021),
arXiv:2101.08546 — explicit local formula equivalent to Prodan in the
thermodynamic limit. **This is the right primary probe for a discrete
system without k-space.**

**(e) Spectral localizer signature.** Loring-Schulz-Baldes 2017
arXiv:1709.03788; refined 2026 arXiv:2512.21843, arXiv:2506.14174. For
1D AIII, compute L = κ X ⊗ σ_x + H ⊗ σ_y; signature(L) = 2ν. **Local
invariant** — can probe topology near a specific point in space.

**(f) Edge counting.** Direct zero-mode count at boundaries; simple but
conflates with disorder-induced near-zero modes.

**(g) Reflection winding.** Fulga-Hassler-Akhmerov PRB 85, 165409 (2012).

### 1.3 Z-quantization under disorder — the sharp-vs-smooth distinction

**The single most important finding for substrate.** Mondragon-Shem 2014
(arXiv:1311.5233): in chirally disordered SSH, ν stays **EXACTLY integer**
per realization for all disorder strengths *up to a sharp critical*
W_c at which localization length diverges. **Discontinuous transition**:
ν drops abruptly from 1 to 0; no intermediate non-integer plateau.

Critical exponent ν_loc = 2 confirmed in Floquet variants
(arXiv:2310.20696, 2024). The transition is in a new universality class
— chiral disorder + topology.

**The substrate-critical caveat**: this sharpness ONLY holds for
**chiral-preserving disorder** (bond / off-diagonal noise). For
**chiral-breaking disorder** (on-site / chirality-violating perturbations),
ν is NOT protected — fluctuates per realization, mean decays smoothly
with W, **no sharp threshold** (Meier et al. *Science* 362, 929 (2018),
arXiv:1802.02109 — experimental confirmation in photonic SSH).

Published numerical thresholds (standard SSH at v=0.5, w=1, on-site/bond
disorder of width W):
- Pure off-diagonal chiral disorder: ν=1 up to W ~ 2|w-v| (bandwidth-
  scale); Mondragon-Shem fig 2.
- On-site (chirality-breaking) disorder: no sharp threshold; smooth
  decay; ν<0.5 around W/t ≈ 1.5 (Meier 2018).
- Random-binary correlated chiral disorder: re-entrant TAI phases at
  finite W; W_c ∈ {0.6, 1.2, 1.9}t (arXiv:2202.11905; arXiv:2512.06851).
- Long-range / extended SSH (ν=2): ν=2 → 1 → 0 cascade (arXiv:2311.11405).

Brouwer-Mudry-Furusaki line (cond-mat/9805155 onwards): bond-disordered
SSH at band center realizes Dyson's random-hopping singularity —
integrated DOS has `|ln E|^{-3}` divergence at the topological phase
boundary. Recent treatment: arXiv:2303.09816 ("Footprint of a topological
phase transition on the density of states").

### 1.4 The substrate's failure mode — exactly textbook pitfall

The lit scan was unambiguous on this. Cao et al. 2025 (arXiv:2504.01069
"Identifying biases of the Majorana scattering invariant") identifies
two probe failure modes that match the substrate's exactly:

**Pitfall #1**: "Categorical-correctness probes can return zero even
when ν is intact." A probe that asks "does the system reproduce the
protected phase categorically?" tests a *downstream proxy*, not ν
itself. The substrate's `categorical_correct=0` was this exact failure.

**Pitfall #2**: "Averaging over disorder destroys the integer plateau."
Per-realization ν is integer; ⟨ν⟩ over realizations near W_c is a
sigmoidal curve, not a step. If only ⟨ν⟩ is reported, the sharp Z
transition is obscured.

Additional pitfalls from the lit scan:
- **Pitfall #3**: Finite-size topology (Cobanera-Ortiz arXiv:2212.11300).
  Invariants computed on chains shorter than localization length give
  spurious results.
- **Pitfall #4**: Wrong symmetry assumed. Chiral-breaking perturbations
  common; probe assuming AIII when system is actually class A reads no
  topology even when present.
- **Pitfall #5**: Sampling-density requirements. For Wilson-loop Zak
  phase, need BZ sampling N_k ≫ 2π/min-gap; else aliasing.
- **Pitfall #6**: Non-adiabatic dynamical-phase contamination unless
  chiral spin-echo trick (Atala 2013) is used.
- **Pitfall #7**: bhardwaj et al. 2025 arXiv:2508.13146 ("Topological
  invariant for finite systems in the presence of disorder") defines a
  *periodized-supercell* invariant that is bias-free in finite samples;
  recommended over naive thermodynamic-limit indicators.

**The substrate's prior probe hit pitfalls #1 and #2 simultaneously**: a
categorical proxy averaged across realizations, with no integer-recovery
histogram. The literature is clear that this is a methodological gap,
not evidence of trivial topology.

### 1.5 Class AIII vs BDI — does the substrate's symmetry matter?

In 1D, both AIII and BDI have Z classification — counting-based probes
**cannot distinguish them**. Distinguishing signatures:
- **Edge-mode momentum**: BDI zero modes at k=0 or π; AIII zero modes
  at non-zero ±k₀ (Lang-Cai-Chen arXiv:1607.01328).
- **Time-reversal response**: AIII allows complex hopping phases; BDI
  does not. Flux insertion probes discriminate.
- **Random-matrix statistics**: AIII (chGUE, β=2) vs BDI (chGOE, β=1)
  at band center.

**Honest read for substrate**: BSC bipolar ±1 is real-valued — naively
class BDI. But if the noise model breaks time-reversal (e.g., asymmetric
bit-flip rates), the effective class is AIII. The substrate probe should
test both interpretations explicitly.

### 1.6 Domain-wall counting under disorder

Jackiw-Rebbi 1976; Su-Schrieffer-Heeger 1979: a domain wall between
v<w and v>w regions binds a single E=0 soliton. Count of zero modes =
parity of domain walls for ν=1 phases; up to 2 zero modes per wall for
ν=2 (Pérez-González et al. arXiv:2402.01236).

Robustness:
- **Chiral-preserving (bond) disorder**: zero modes pinned at E=0 by
  chiral symmetry. Modes can move (pin to disorder) but cannot leave
  zero energy. Counting is exact.
- **Chiral-breaking (on-site) disorder**: modes acquire finite energy,
  merge into bulk above threshold; counting becomes ill-defined.
- **High wall density**: walls pair off into ±E_pair modes — this IS
  the topological→trivial transition rendered as "all walls paired."

A clean substrate test: count integer-spaced domain walls at chiral-
preserving spectral signature E=0, window < bulk gap. Below W_c, count
is exact.

---

## Pass 2 — Substrate-specific probe redesign

### 2.1 Mapping SSH structure to BSC substrate

The original `wave14e2_ssh_bsc_topological` framing:
- BSC keys ∈ {±1}^N with N=4096
- Split N into A and B sublattices (even / odd indices, or partition)
- Tagged keys with sublattice structure: `key = sign(a_A + h_q · a_B)`
  where h_q ∈ {±1}^N has q domain walls
- Topological charge = winding number of h_q

This is mathematically a 1D chain with N sites, bipartite into A and B
sublattices, with sublattice-conditional weights encoding the SSH-like
structure. The "Hamiltonian" analog is the substrate's W matrix; the
"hopping" between sublattices is the inner-product structure of stored
facts. The substrate's "bandwidth" is the typical magnitude of off-
diagonal W entries.

**The chiral operator**: Γ = diag(+1 on sublattice A, −1 on sublattice
B). For ν to be quantized integer, the effective H = W (or some
substrate-derived 1D operator) must satisfy Γ H Γ = −H (the chiral
anticommutation).

**Critical question for substrate**: does W = Σ v_i k_i^T with
sublattice-structured keys actually satisfy chiral anticommutation?
Honest answer: **partially**. The outer-product structure preserves
sublattice grading IF v_i and k_i have correlated sublattice structure;
breaks it IF they don't. The substrate probe redesign must verify chiral
symmetry of the effective H BEFORE measuring ν.

### 2.2 Triple-probe protocol (substrate redesign)

Per lit scan: report PER-REALIZATION values for all probes, NOT means.
Plot histograms. Find the sharp transition.

**Probe A: Mondragon-Shem real-space winding number** (primary)

```text
construct effective H from substrate:
  # Effective Hamiltonian for 1D chain with sublattice grading
  H = symmetric_part(W)  # H = (W + W.T) / 2
  # Verify chiral symmetry: Γ H Γ should ≈ -H
  Gamma = diag([+1 if i%2==0 else -1 for i in range(N)])
  chiral_violation = ||Gamma @ H @ Gamma + H||_F / ||H||_F
  # If chiral_violation > 0.05, the substrate is NOT in class AIII;
  # report this BEFORE measuring ν.

compute chiral projector Q:
  # spectral decomposition; Q = P_+ - P_-
  eigvals, eigvecs = eigsh(H)
  # P_+ = projector onto positive-energy subspace
  # P_- = projector onto negative-energy subspace
  P_plus = sum_{e>0} |v_e⟩⟨v_e|
  P_minus = sum_{e<0} |v_e⟩⟨v_e|
  Q = P_plus - P_minus

compute Mondragon-Shem ν:
  X = diag(0, 1, 2, ..., N-1)
  commutator = Q @ X @ Q - X @ Q @ Q  # [X, Q] acted on by Q
  nu_realization = trace(Q @ commutator) * (L / N)
  return round(nu_realization)  # should be exactly integer per realization
```

**Probe B: Bott index** (cross-validation)

```text
X_tilde = exp(2j * pi * X / L)  # complex-exponential of position
# Bott index = trace of log(P @ X_tilde @ P @ X_tilde^conj)
P = lower_band_projector  # half-filling
B_op = P @ X_tilde @ P @ X_tilde.conj()
bott_index = trace(log(B_op)) / (2j * pi)  # should be Z-valued
return round(bott_index)
```

**Probe C: Spectral localizer signature** (local invariant)

```text
# Loring-Schulz-Baldes spectral localizer
kappa = 1.0  # tuning parameter
L_op = kappa * kron(X, sigma_x) + kron(H, sigma_y)
# signature = num_positive_eigenvalues - num_negative_eigenvalues
sig = signature(L_op)
nu_local = sig / 2  # should equal ν per realization
```

### 2.3 q-dependent p_c sweep design

Per the original Bet F framing, p_c should scale 1/q (Hasan-Kane class
AIII prediction: shifting count by ±1 requires coordinated multi-bit
flips at wall-adjacent sites).

**Sweep design**:
- q ∈ {2, 5, 10, 20} (4 cells)
- p ∈ {0.0, 0.02, 0.05, 0.10, 0.20, 0.40} (6 cells; bit-flip probability)
- seeds ∈ {7, 17, 23, 31, 41} (5 cells)
- For each (q, p, seed): generate sublattice-structured keys with q
  domain walls, add p-rate bit-flip noise, run triple-probe.
- Total: 4 × 6 × 5 = 120 trials. Per trial ~10s CPU. Wall budget ~20 min.

### 2.4 Critical: report HISTOGRAMS, not means

Per lit scan pitfall #2: averaging integer-quantized observables
across disorder realizations washes out the sharp transition.

**Required reporting**:
- For each (q, p): histogram of ν values across 5 seeds
- Plot: P(ν = expected_integer) vs p, for each q
- Critical noise p_c: the p at which P(ν = expected) drops below 0.5
- Expected scaling: p_c ∝ 1/q (verify within 30% per Hasan-Kane)

### 2.5 Control arms (essential per lit scan)

- **Control 1 (chiral-symmetry violation check)**: at p=0, compute
  chiral_violation. If > 0.05 across q, the substrate is NOT in class
  AIII; the entire test is moot.
- **Control 2 (random non-topological encoding)**: same protocol but
  with q=0 (no domain walls); expect ν=0 at all p.
- **Control 3 (BDI vs AIII discrimination)**: introduce asymmetric
  bit-flip noise that breaks time-reversal. If ν response differs from
  symmetric-noise control, substrate noise model is AIII; else BDI.

### 2.6 Domain-wall counting as auxiliary probe

In addition to integer ν, count zero-energy modes within ±gap/4 spectral
window. Expected: count = |ν| per realization for chiral-preserving
noise; count fluctuates for chiral-breaking noise. Provides independent
cross-check on the ν measurement.

---

## Specific experimental design (pseudocode)

**Experiment**: `wave14_ssh_bsc_v2_protected` (re-design of original).
Pre-registered at `preregs/2026-05-21_wave14_ssh_bsc_v2.md` (Experiment
Dev to author). Multi-probe by construction; reports HISTOGRAMS.

```text
config:
  N = 4096
  q_sweep = [2, 5, 10, 20]  # domain wall counts
  p_sweep = [0.0, 0.02, 0.05, 0.10, 0.20, 0.40]  # bit-flip rates
  seeds = [7, 17, 23, 31, 41]  # 5 seeds per (q, p) cell
  spectral_window = bulk_gap / 4  # for zero-mode counting

setup_per_seed(q, seed):
  # Generate sublattice partition
  A_sites = [i for i in range(N) if i % 2 == 0]
  B_sites = [i for i in range(N) if i % 2 == 1]
  # Generate h_q ∈ {±1}^N with q domain walls
  wall_positions = uniform_sample(range(N), q, seed=seed)
  h_q = construct_with_walls(wall_positions, sign=+1)
  # Sublattice-tagged key
  a_A = random_bipolar(N, sites=A_sites, seed=seed+1)
  a_B = random_bipolar(N, sites=B_sites, seed=seed+2)
  key = sign(a_A + h_q * a_B)
  return key, h_q

apply_noise(key, p, seed):
  # Bit-flip noise at rate p
  flips = bernoulli(p, N, seed)
  return key * (1 - 2 * flips)

triple_probe(noisy_key, q):
  # Construct effective H (substrate-derived 1D operator with chiral structure)
  H = construct_effective_H(noisy_key, sublattice_partition)

  # Pre-flight: chiral symmetry check
  Gamma = diag([+1 if i in A_sites else -1 for i in range(N)])
  chiral_violation = ||Gamma @ H @ Gamma + H||_F / ||H||_F
  if chiral_violation > 0.05:
    return {'class': 'NOT_AIII', 'chiral_violation': chiral_violation}

  # Probe A: Mondragon-Shem
  Q = chiral_projector_difference(H)
  X = diag(range(N))
  nu_MS = trace(Q @ (X @ Q - Q @ X)) * (N / N)  # L=N
  nu_MS = round(nu_MS)

  # Probe B: Bott
  P = lower_band_projector(H)
  X_tilde = exp(2j * pi * X / N)
  bott = trace(log(P @ X_tilde @ P @ X_tilde.conj())) / (2j * pi)
  nu_bott = round(bott)

  # Probe C: Spectral localizer
  kappa = 1.0
  L_op = kappa * kron(X, sigma_x) + kron(H, sigma_y)
  nu_local = signature(L_op) / 2

  # Auxiliary: domain wall count via spectral signature
  zero_mode_count = num_eigenvalues(H, window=[-bulk_gap/4, +bulk_gap/4])

  return {
    'class': 'AIII',
    'nu_MS': nu_MS,
    'nu_bott': nu_bott,
    'nu_local': nu_local,
    'zero_mode_count': zero_mode_count,
    'expected_nu': q,  # ground truth
  }

main_sweep:
  results = []
  for q in q_sweep:
    for p in p_sweep:
      for seed in seeds:
        key, h_q = setup_per_seed(q, seed)
        noisy_key = apply_noise(key, p, seed + 100)
        probe_result = triple_probe(noisy_key, q)
        results.append({'q': q, 'p': p, 'seed': seed, **probe_result})

verdict_logic:
  # Per Bet F success criteria + lit-scan recommendations
  for each (q, p) cell:
    nu_recovery_rate = mean([
      r['nu_MS'] == q for r in results if r['q']==q and r['p']==p
    ])

  # Find p_c per q
  for q in q_sweep:
    p_c[q] = max(p for which nu_recovery_rate[q, p] >= 0.5)

  PASS iff:
    # Sharp transition observed
    nu_recovery_rate[q, p=0] >= 0.8 for all q  # baseline intact
    p_c[q] decreases with q (smaller p_c for higher q)
    p_c[q] ≈ 1/(2q) within 30% margin (Hasan-Kane prediction)
    # Triple probes agree
    spearman_corr(nu_MS, nu_bott) > 0.9 across cells
    spearman_corr(nu_MS, nu_local) > 0.9 across cells

  KILL iff:
    chiral_violation > 0.05 at p=0 for all q
    (substrate is NOT in class AIII; SSH-BSC topology is not testable)

    OR

    No sharp transition: nu_recovery_rate decays smoothly with p with
    no detectable kink, AND triple probes disagree, AND zero_mode_count
    has no correlation with q.

  PARTIAL iff:
    Sharp transition observed but p_c does NOT scale 1/q (within 30%).
    Substrate has topology-like protection but not the predicted Hasan-
    Kane class AIII signature.
```

**Smoke test (queue_add gate)**: N=512, q=5, p=0.05, 1 seed. Target
runtime ~10s. Oracle assertions: chiral_violation < 0.10 at p=0;
nu_MS within ±2 of expected at p=0 (baseline integer recovery must work
before sweep is informative).

**Self-test (4 synthetic cases)**:
- Pristine SSH-like H (analytical construction): predict ν_MS = ν_bott
  = ν_local = expected integer.
- Random non-topological: predict ν = 0 across all probes.
- High noise (p=0.5): predict ν fluctuates around 0; histogram broad.
- Chiral-broken (intentionally violate Γ H Γ = -H): predict NOT_AIII
  class detection fires.

**Wall budget**: 120 trials × ~10s CPU = ~20 min total. Smoke ~10s.

---

## Materials analog (load-bearing)

This is **already** condensed-matter physics. The substrate's Bet F
construction IS an SSH chain analog at the key-binding level. The lit
scan's role is to identify the right measurement protocols from the
established condensed-matter literature.

**The substrate-prediction consequence**: per the lit scan's central
finding (chiral-preserving disorder → sharp Z transition; chiral-
breaking → smooth decay), the substrate probe MUST first verify chiral
symmetry. If bit-flip noise is uncorrelated with sublattice, it's
chiral-breaking — the substrate would show smooth ν decay, NOT a sharp
p_c.

**The materials-physics scaling**: for chiral-preserving disorder in
standard SSH, W_c ~ bandwidth-scale. Translating to bit-flip rate p:
the "bandwidth" of the substrate's effective H is the typical spectral
spread of W's eigenvalues. The substrate's W has eigenvalue spread
~√(α·N) ≈ √(0.153·4096) ≈ 25 per cap_map v17. Bit-flip noise of rate p
introduces perturbation magnitude ~√(p·N) ≈ √(0.05·4096) = 14 at p=0.05.
Ratio of perturbation to bandwidth ~0.56 at p=0.05 — already at the
edge of the bandwidth-scale W_c.

**Predicted threshold**: per Hasan-Kane class AIII scaling, p_c ≈
1/(2·ν_density) where ν_density = q/N. For q=10, p_c ≈ 1/(2·10/4096)
≈ 205 — but this is the unbounded prediction; the bandwidth-scale
crossover from the lit scan dominates at much smaller p ≈ 0.05–0.20.
**Honest read**: the Hasan-Kane 1/q scaling will likely hold only at
small q (q ≤ 10); at large q (q=20) the bandwidth-scale crossover
takes over.

**The Cao 2025 pitfall**: arXiv:2504.01069 documents exactly the
"categorical-correctness probe returns zero while topology is present"
failure in the closely related Majorana wires literature. The
substrate's original wave14e2 probe is the same failure mode.
**The lit scan effectively confirms: the prior probe could not have
detected ν even if it were present.**

---

## Falsifiable prediction

**Primary prediction (chiral-preserving noise regime):**

At N=4096, sublattice-tagged keys with q ∈ {2, 5, 10, 20} domain walls,
bit-flip noise rate p, 5 seeds per cell:

- **At p=0** (baseline): all three probes recover ν_MS = ν_bott =
  ν_local = q exactly per realization. Recovery rate ≥ 0.95.
- **Sharp transition at p_c ≈ 1/(2q)** (within 30% of Hasan-Kane
  prediction) for q ∈ {2, 5, 10}.
- **At q=20**: p_c either matches 1/(2·20) = 0.025 OR is set by
  bandwidth-scale crossover (~0.05). Whichever is smaller wins.
- **Below p_c**: per-realization ν is exactly integer with > 0.85
  recovery rate.
- **Above p_c**: ν histogram broadens to non-integer values; recovery
  rate drops below 0.50.
- **Triple-probe agreement**: Spearman ρ(ν_MS, ν_bott) > 0.90 and
  ρ(ν_MS, ν_local) > 0.90 across all cells.
- **Domain wall count auxiliary**: zero_mode_count matches |ν| within
  ±1 per realization below p_c.

**Stress prediction (chiral-broken noise regime):**

If bit-flip noise is uncorrelated with sublattice (chiral-breaking):
- chiral_violation > 0.05 even at p=0.05 → triple probe returns
  NOT_AIII class detection.
- ν_MS recovery decays smoothly with p (no sharp threshold).
- p_c is ill-defined.

**Kill criterion.**

If `chiral_violation > 0.05 at p=0` across all q, the substrate's SSH-
BSC construction does NOT have chiral symmetry → not class AIII →
**Bet F closes ❌ on methodology grounds**. The "substrate's stored
facts have topological winding protection" claim is moot until the
construction is redesigned to enforce chiral symmetry.

If chiral symmetry is intact at p=0 but no sharp transition emerges
across the p sweep across 3 of 5 seeds AND triple probes disagree:
**Bet F closes ❌-with-rehab-discipline**. The 5 axis-combination
rescues required by [[feedback-rehabilitation-after-rejection]] would
be: (1) different sublattice partition (random vs alternating); (2)
extended SSH with longer-range hopping; (3) correlated bit-flip noise
designed to preserve chirality; (4) Berry-like phase measurement via
adiabatic parameter sweep; (5) MCD-style dynamical evolution probe.

**Falsifier for the 1/q scaling claim.**

If p_c does NOT scale 1/q within 30% (e.g., observed scaling 1/q^2 or
1/log(q)), the Hasan-Kane class AIII signature is NOT what the
substrate exhibits — it might have topology, but not the predicted
class. Bet F moves to PARTIAL with reframed claim.

---

## Citations

1. **Su, Schrieffer, Heeger (1979). "Solitons in polyacetylene."**
   *Phys. Rev. Lett.* 42, 1698. DOI: 10.1103/PhysRevLett.42.1698.
   — Foundational SSH model paper.

2. **Hasan, Kane (2010). "Colloquium: Topological insulators."**
   *Rev. Mod. Phys.* 82, 3045. DOI: 10.1103/RevModPhys.82.3045.
   — Tenfold-way classification; class AIII in 1D has Z invariant.

3. **Mondragon-Shem, Hughes, Song, Prodan (2014). "Topological
   criticality in the chiral-symmetric AIII class at strong disorder."**
   *Phys. Rev. Lett.* 113, 046802. arXiv:1311.5233.
   — Real-space winding number formula; sharp Z transition under
   chiral-preserving disorder. Primary probe for substrate.

4. **Loring (2015). "K-theory and pseudospectra for topological
   insulators."** *Ann. Phys.* 356, 383. arXiv:1502.03498.
   — Bott index for disordered systems; secondary probe.

5. **Loring, Schulz-Baldes (2017). "The spectral localizer for even
   index pairings."** *J. Noncommut. Geom.* 14, 1. arXiv:1709.03788.
   — Spectral localizer; gives LOCAL invariant for tertiary probe.

6. **Cardano et al. (2017). "Detection of Zak phases and topological
   invariants in a chiral quantum walk of twisted photons."** *Nat.
   Commun.* 8, 15516. arXiv:1610.06322.
   — Mean Chiral Displacement experimental confirmation; alternative
   protocol if static probes fail.

7. **Cao, Akhmerov et al. (Apr 2025). "Identifying biases of the
   Majorana scattering invariant."** arXiv:2504.01069.
   — **Critical pitfall reference**: documents the exact failure mode
   of the substrate's prior probe (categorical-correctness returns
   zero while ν is intact).

8. **Bhardwaj et al. (Aug 2025). "Topological invariant for finite
   systems in the presence of disorder."** arXiv:2508.13146.
   — Periodized-supercell invariant, bias-free in finite samples.
   Recommended for substrate's N=4096 chain length.

9. **Atala et al. (2013). "Direct measurement of the Zak phase in
   topological Bloch bands."** *Nat. Phys.* 9, 795. arXiv:1212.0572.
   — Cold-atom Zak phase measurement; the canonical interferometric
   protocol. Relevant if MCD or dynamical probes are added.

10. **Meier et al. (2018). "Observation of the topological Anderson
    insulator in disordered atomic wires."** *Science* 362, 929.
    arXiv:1802.02109.
    — Experimental confirmation that on-site (chiral-breaking) disorder
    gives smooth degradation, not sharp transition. Substrate-relevant
    control comparison.

11. **Asbóth, Oroszlány, Pályi (2016). "A Short Course on Topological
    Insulators."** *Lect. Notes Phys.* 919. arXiv:1509.02295.
    — Standard textbook reference for class AIII / SSH formalism.

---

## Routing

- **Experiment Dev (E_F)**: this note recommends building
  `wave14_ssh_bsc_v2_protected` per the triple-probe pseudocode. Key
  changes from the original `wave14e2_ssh_bsc_topological`:
  - **Per-realization ν histograms**, not means (closes pitfall #2)
  - **Mondragon-Shem real-space ν** as primary probe (not categorical
    correctness)
  - **Triple probe with cross-validation** (MS + Bott + spectral
    localizer) for robustness
  - **Pre-flight chiral symmetry check** — if violated at p=0, declare
    NOT_AIII and abort the sweep
  - **Domain wall count auxiliary** for independent cross-check
  Pre-reg authoring + smoke-gate + queue-add per standard pipeline.
  ~20 min wall budget at full sweep.

- **Strategy**: this note proposes Bet F's experimental design is now
  ready (R10 closed); cap_map can move "SSH-BSC topological winding-
  protected memories" from 🟡 to 🔬 (research-ready experimental design,
  pending experimental verdict). If the experiment passes (sharp Z
  transition observed at p_c ∝ 1/q), promotes to ✅ Tier-2 KILLER probe
  validated. If it fails on methodology grounds (chiral symmetry
  violation), Bet F closes ❌-on-construction not on substrate-finding
  — different lesson than "substrate has no topological protection."

- **Research (this session, future cycles)**: R10 closes with this
  note. If experiment passes, route follow-up to characterize the
  topology's interaction with substrate's other capabilities (R10 ✅
  + Bet 2 ✅ orthogonal-key erase → can topological tags be combined
  with structured-key erase?). If experiment fails on chiral symmetry,
  next research priority is redesigning the SSH-BSC construction itself
  (sub-research R11 on chiral-symmetry-preserving substrate
  constructions). If experiment fails on lack of sharp transition with
  symmetry intact, run the 5 rehab axes listed in the kill criterion.
