# META → Strategy: materials-science substrate-physics gaps + recommended experiments

**Sender**: META session (session 6)
**Recipient**: Strategy session (session 1)
**Date**: 2026-05-23 ~07:00 EDT
**Topic**: Materials-science perspective on substrate-physics gaps post cycle-78 CULMINATION + cycle-89 SHORT-cycle refinement; recommended experiments to convert qualitative substrate-novel finding into quantitative substrate-physics characterization.
**Trigger**: user request "from a mat sci perspective, what are the things we haven't yet proven that we need to" (~06:55 EDT).
**Reference**: `feedback_materials_science_probe` (BSC atoms = Ising spins; always include crystal/spin-glass math).

## Context

Substrate-physics characterization at cap_map v142:
- Substrate IS deterministic dynamical system with SHORT limit cycles (median 2-8 hops; 100% codewords cycle; 54% period ∈ [2, 100]; N-INVARIANT; weakly K-dependent)
- Forward-lossy + reverse-invertible
- 28-element endpoint structure at N=65536 K=100
- RS / paramagnet thermodynamic phase at α=0.15 operating point (4 cross-family anchors)
- RSB-capable W structure (Hessian VDOS soft-modes 85%)
- Localized eigenvectors (Kerdock AMP universality refuted)
- 5/5 mechanism diagnoses refuted → POSITIVE characterization via direct measurement

**Open question per materials-science framing**: substrate-physics characterization is QUALITATIVE (substrate-novel dynamical class identified). Materials science offers TWO standard upgrades to QUANTITATIVE: critical exponents at phase transitions + order parameters distinguishing phases.

## TIER 1 — Load-bearing for substrate-physics QUANTITATIVE positioning

### Gap 1 — Critical exponents at the Bet S K-ceiling

**What's unproven**: substrate's accuracy degrades as K → K_crit ≈ 205 at N=4096. Decay law unknown — power-law, exponential, or discontinuous?

**Why it matters**: critical exponents define substrate's *universality class*. Substrate is currently positioned as "beyond published RS theory at 57× AGS bound" — a GAP claim. With critical exponents, the claim upgrades to "substrate is in [universality class X] with [α, β, γ] exponents" — a CLASS claim.

**Recommended experiment**: `wave14_K_ceiling_critical_exponents_v1`
- Scan K ∈ [25, 50, 100, 150, 175, 190, 200, 210, 220, 250] at N=4096
- Measure accuracy + per-K variance across 5 seeds
- Fit power-law, exponential, discontinuous models
- Extract critical exponent β (accuracy decay rate) + ν (correlation length / cycle period divergence)
- Compare to known universality classes (mean-field, Ising, Heisenberg)
- **Cost**: 30-60 GPU-min single experiment
- **Pass criteria**: power-law fit r² > 0.85 → identifies universality class

### Gap 2 — Order parameter for limit-cycle structure

**What's unproven**: substrate has structure (28-element endpoint partition + SHORT cycles) but no order parameter distinguishing phases. Spin glasses use Parisi q(x); substrate equivalent missing.

**Why it matters**: phase identification requires an order parameter. Cycle 88-131's 5 mechanism hypothesis cycle was partly because we lacked a substrate-physics order parameter to constrain candidate frameworks. The limit-cycle period (median 2-8) is one statistic; we need the DISTINGUISHING statistic that tells you which phase substrate is in.

**Recommended experiment**: `wave14_substrate_order_parameter_v1`
- For each codeword c, run forward chain to L=50; identify cycle phase ϕ(c) ∈ [0, period-1] (which cycle state codeword sits in at L=50)
- Compute order parameter candidates:
  - φ_distribution: histogram of ϕ values across codewords
  - q_overlap = (1/K) Σ_i,j δ(ϕ_i, ϕ_j) — Parisi-like overlap
  - C_endpoint = correlation between input codeword and endpoint position
- Test which candidate is invariant under perturbations (small W noise, codeword random subset)
- **Cost**: 30-60 GPU-min single experiment
- **Pass criteria**: at least one candidate gives stable distribution across re-runs (cycle 142 reproducibility holds)

### Gap 3 — Phase diagram across α (load fraction)

**What's unproven**: substrate certified RS at α=0.15 (4 cross-family anchors at single operating point). ZERO data on substrate behavior at α=0.05, 0.30, 0.50, 0.95. Phase boundaries unmapped.

**Why it matters**: substrate-product positioning at α=0.15 is robust IFF substrate doesn't sit at a phase boundary. Materials science routinely maps T-vs-disorder phase diagrams; substrate's α-axis is unmapped.

**Recommended experiment**: `wave14_substrate_alpha_phase_diagram_v1`
- At fixed N=4096, scan α ∈ [0.05, 0.10, 0.15, 0.20, 0.30, 0.50, 0.75, 0.95]
- Re-run 4 cross-family RS-cert probes (C_ij + P(h) + 1/f noise + χ'(ω)) at each α
- Identify α range where ALL 4 agree on RS (substrate-product safe operating range)
- Identify α range where probes diverge (RS-RSB boundary candidate)
- **Cost**: 60-120 GPU-min (8 α values × 4 probes; each probe ~2-5 min at N=4096)
- **Pass criteria**: substrate-physics phase diagram with α boundaries identified

### Gap 4 — Energy landscape topology (TAP complexity)

**What's unproven**: Hessian VDOS soft-mode density 0.850 (85% near-zero eigenvalues — extreme softness). What does this MEAN structurally? Number of local minima? Barrier height distribution? Substrate's energy landscape is a black box with one measurement.

**Why it matters**: per `feedback_materials_science_probe`: BSC atoms = Ising spins; energy landscape is THE central substrate-physics object for spin-glass-class systems. TAP complexity Σ(f) was Family IV in cycle 109 observability suite but never extracted at FULL.

**Recommended experiment**: `wave14_substrate_TAP_complexity_v1`
- Generate random initial states; gradient-descent or single-spin-flip relax to local minima
- Count distinct local minima via clustering
- Histogram of TAP free-energy values f at each minimum
- Compute log Σ(f) = TAP complexity as function of f
- Compare to known spin-glass complexity curves (SK model, mean-field, Heisenberg)
- **Cost**: 60-120 GPU-min (single experiment, multiple random starts)
- **Pass criteria**: complexity curve Σ(f) measured + classified vs known shapes

## TIER 2 — Substrate-product distinctive, lower priority

5. **Hysteresis / encoding-order dependence** — does substrate have spin-glass memory effects (aging, rejuvenation)? Test by training {A,B,C} vs {C,B,A} and comparing endpoint structure.

6. **Relaxation timescale spectrum** — full β(α, N) characterization (smoke cycle 119 β=1.160; FULL cycle 121 β=0.553; never reconciled).

7. **Universality class identification** — closely tied to Gap 1 critical exponents; once exponents known, class follows.

8. **Cluster basin hierarchy (ultrametric vs random vs lattice)** — 28-element endpoint structure organization. Cycle 145 cluster_identity_diagnostic "DIFFUSE" small sample.

## TIER 3 — Speculative, low priority

9. Nonlinear susceptibility χ_3 (field-response).
10. Spatial correlation length analog.
11. Thermodynamic-limit N → ∞ extrapolation (currently have N=4096-262K data).
12. Quench vs anneal protocols (does substrate formation order matter?).

## Strategy decision points

**If you pursue only ONE**: Gap 1 (critical exponents at K-ceiling). Converts "beyond published RS theory" GAP claim into "substrate is in [universality class X]" CLASS claim. Single experiment, 30-60 GPU-min. Substrate-physics-distinctive positioning gain.

**If you pursue TWO**: add Gap 2 (order parameter). Materials-science-standard pair: critical exponents + order parameter together identify universality class. Two experiments, 60-120 GPU-min total.

**If you pursue ALL of TIER 1 (4 experiments)**: substrate-physics characterization upgrades from QUALITATIVE ("substrate-novel deterministic dynamical-system class with SHORT limit cycles") to QUANTITATIVE ("substrate is [universality class X] with critical exponents [Y], order parameter [Z], phase diagram [W], landscape topology [Σ(f)]"). Total ~3-5 GPU-hours.

## What I'm NOT recommending

- 6th-attempt mechanism hypothesis research (5/5 refuted; user signal "may be LAST"; substrate-physics POSITIVE characterization already achieved at v141/v142).
- Going deeper on the 28-element endpoint structure mechanism (per cycle 138 + 145 ENDPOINT_COLLAPSED already confirmed at FULL).
- Pure theoretical work (per `feedback_no_papers_product_only`: substrate-product oriented).

## Per session-self-coordinate

This is META→Strategy routing only; no user coordination needed.
Strategy decides priority + queues experiments per Strategy session
process. META's job is to flag gaps + recommend; Strategy commits
the substantive-batch.

## Per feedback_value_creation_not_competition

Materials-science gaps identified are substrate-physics-distinctive
positioning gains. Critical exponents + order parameter + phase
diagram + energy landscape topology are STANDARD spin-glass-class
characterization. Substrate fitting into (or distinguishing from)
known classes is substrate-product-distinctive substrate-physics
finding.

## Per terminology rule

Each gap claim has substrate-level reason in description (critical
exponents define universality class; order parameter distinguishes
phases; phase diagram maps operating envelope; TAP complexity is
central substrate-physics object for spin-glass-class systems).

EOF marker.
