# Pre-registration: mode_coupling_theory_substrate_v1

Date: 2026-05-27
Experimenter: exp_dev (sub-agent)
Probe type: Orthogonal physics framework (Mode-Coupling Theory)

## Hypothesis

The approach to the capacity cliff in BSC substrate follows MCT critical slowing:
d(overlap)/d(K) diverges as a power law near K_c ~ 0.14*N. Power-law exponent
gamma ~ 1.0 (Kirkpatrick-Thirumalai p=2 universality).

## Scientific context

MCT predicts ergodicity breaking near glass transitions. For Hopfield-like networks
(p-spin models), this manifests as power-law divergence of relaxation times.
In our substrate: overlap vs K should show non-linear curvature near K_c.
This is an orthogonal lens to the 1-RSB hysteresis tests (different observable).

## Pre-registered thresholds (calibration probe)

HARD-PASS:
  - Power-law fit R^2 >= 0.80 in the K-near-K_c region
  - AND fitted gamma in [0.3, 3.0] (MCT-plausible range)
HARD-FAIL:
  - Linear fit R^2 > 0.95 (smooth, no critical slowing)
MIDDLE-BAND:
  - Power-law R^2 in [0.5, 0.80)

Calibration-probe policy: no prior anchor on power-law divergence in this substrate.
HARD-PASS = theoretical prediction. HARD-FAIL = null (linear).

## Timeout estimate

N=1024 8 K-values 5 seeds: ~40s.
timeout_s = ceil(1.5 * 40 * 1.0) = ceil(60) -> 300s.

## Smoke result

N=256 4 K-values 1 seed: linear_R^2=0.97 (HARD_FAIL at smoke).
NOTE: smoke HARD_FAIL is expected at N=256. The K_c~36 at N=256 is not well-probed
by K=[1,4,16,64] (only K=64 is near K_c=36; insufficient for power-law fit).
At FULL N=1024, K=[1,4,8,16,32,64,128,160,192] straddles K_c~143 with 4+ points.
Ship warranted: smoke HARD_FAIL is scale artifact, not instrumentation failure.
Metrics are valid (non-zero, non-sentinel, varied).

## N-suffix

No _nN suffix; production N = 1024 (standard, stated in script: `N_FULL = 1024`).
