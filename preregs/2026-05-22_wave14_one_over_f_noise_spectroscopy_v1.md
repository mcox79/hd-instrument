# Pre-reg: Wave 14 1/f Noise Spectroscopy v1

**Filed:** 2026-05-22
**Source:** Research 13:55 Entry 140 #4 (P=0.75).

## Question

At α=0.15 (substrate operating point), what is the power-spectral-density exponent γ of substrate's per-neuron activation trace under Glauber MC dynamics?

Per Cugliandolo-Kurchan 1993 spin-glass dynamics, γ ∈ [0.5, 1.5] indicates classical 1/f noise (glassy slow modes). γ < 0.3 = white noise (paramagnetic). γ > 1.7 = Brownian (trapped).

## Hypothesis

H_glassy: γ ∈ [0.5, 1.5] — substrate has glassy slow modes (third-family observability signature, alongside C_ij eigvals and P(h) from observability suite v1).

H_white: γ < 0.3 — substrate is paramagnetic at this α.

## Pre-declared verdicts

- `ONE_F_GLASSY` — γ ∈ [0.5, 1.5] (r² ≥ 0.5).
- `ONE_F_WHITE` — γ < 0.3.
- `ONE_F_BROWNIAN` — γ > 1.7.
- `ONE_F_INTERMEDIATE` — 0.3 ≤ γ < 0.5 OR 1.5 ≤ γ ≤ 1.7.
- `ONE_F_INCONCLUSIVE` — r² < 0.5 (bad fit).

## Method

1. Build Hopfield W from M=⌈αN⌉ random ±1 patterns (zero diagonal).
2. Glauber MC at β_mc=2.0; burn-in n_burn sweeps; record activation trace for first n_traced_neurons spins over n_sweeps subsequent sweeps.
3. Per neuron: PSD via real FFT, magnitude-squared.
4. Average PSD across neurons.
5. Log-log linear fit to middle frequency band (skip DC + Nyquist).
6. γ = −slope.

## Acceptance thresholds

- 0.5 r² threshold = "fit decent enough to call γ".
- [0.5, 1.5] glassy band matches Cugliandolo-Kurchan 1993 / Mydosh 1993 spin-glass dynamical literature.

## Config

- N=256 smoke, 1024 full.
- α=0.15, β_mc=2.0.
- n_burn=200, n_sweeps=512 full.
- n_traced_neurons=100 full.

## Pre-declared interpretation

- **GLASSY**: third-family observability cross-certification (alongside C_ij eigvals + P(h) bimodality). cap_map promotion: substrate-physics characterization sharpens to "RS phase at α=0.15 with glassy slow-mode signatures detectable via per-neuron PSD".
- **WHITE**: PSD-family disagrees with C_ij and P(h) — substrate-physics inconsistency; investigate.
- **BROWNIAN**: extremely slow / trapped — would suggest substrate is in deeper glass than RS — but RS certified already, so probably fit artifact.

## Not in scope

- Multi-α sweep (single α=0.15).
- Multi-β_mc temperature sweep.
- Spatially-resolved PSD (single global γ).
