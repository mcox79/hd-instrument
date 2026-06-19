# Pre-reg: Wave 14 AC Susceptibility χ'(ω) v1

**Filed:** 2026-05-22
**Source:** Research 13:55 Entry 140 #5 (P=0.70). Canonical spin-glass freezing diagnostic.

## Question

At α=0.15 (substrate operating point), does substrate's linear response χ'(ω) to oscillating external field h(t)=h₀·sin(ωt)·probe_dir exhibit a peak at a finite freezing frequency ω_freeze?

Per Mydosh 1993 / spin-glass dynamical literature: peak in χ'(ω) at ω_freeze = inverse relaxation timescale.

## Hypothesis

H_freezing: χ'(ω) peak amplitude ≥ 1.5× baseline mean over ω ∈ [0.05, 2.0]. Substrate has finite relaxation timescale.

H_flat: χ' is monotone or non-peaked — substrate is in paramagnetic regime where response decays without peak.

## Pre-declared verdicts

- `CHI_FREEZING` — peak-to-baseline ratio ≥ 1.5.
- `CHI_FLAT` — ratio < 1.5.
- `CHI_INCONCLUSIVE` — metric collection error.

## Method

1. Build Hopfield W from M=⌈αN⌉ random ±1 patterns; zero diagonal.
2. Probe direction = patterns[0] (canonical embedded direction).
3. For each ω ∈ {0.05, 0.1, 0.2, 0.5, 1.0, 2.0}:
   - Burn-in n_burn sweeps with no field.
   - Drive Glauber MC under h(t) = h₀·sin(ωt)·probe_dir for n_cycles cycles, 8 samples per cycle.
   - χ'(ω) = ⟨m(t)·sin(ωt)⟩ / h₀ over second half of trace.
4. Find peak ω_freeze; ratio = peak / mean of other ω values.

## Acceptance thresholds

- 1.5× peak-to-baseline = "freezing peak detectable above noise".

## Config

- N=256 smoke, 1024 full.
- α=0.15, β=2.0, h₀=0.5.
- ω_grid full: [0.05, 0.1, 0.2, 0.5, 1.0, 2.0].
- n_cycles=12, n_burn=200 full.

## Pre-declared interpretation

- **FREEZING**: substrate has finite relaxation timescale = 1/ω_freeze. 4th-family observability cross-cert (alongside C_ij eigvals, P(h), VDOS, muSR G(t), 1/f noise PSD). Strengthens substrate spin-glass characterization.
- **FLAT**: substrate is in paramagnetic regime at α=0.15 with no characteristic freezing timescale. Contradicts Bet E ✅ Parisi P(q) RSB finding — investigate methodology divergence.

## Not in scope

- Multi-α sweep.
- χ''(ω) (out-of-phase / dissipative component).
- Probe direction variation (single direction = pattern[0]).
