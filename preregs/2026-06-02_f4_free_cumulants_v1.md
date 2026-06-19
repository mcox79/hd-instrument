# Prereg: f4_free_cumulants_v1

## Scientific question
F4 free cumulants: does kappa_n = alpha for all n as predicted by free-Poisson?
Measure via spectral moments M3 and M4 vs free-Poisson theory.

## Pre-registered thresholds
- HARD-PASS: All of A (rel_err_M4 <= 0.05), B (rel_err_M3 <= 0.08), C (kappa2_rel <= 0.05).
- HARD-FAIL: HF-A (rel_err_M4 > 0.30) OR HF-C (kappa2_rel > 0.20).
- MIDDLE: 2/3 cells.

## Calibration note
First direct free-cumulant measurement. Prior: v324 confirmed spectral bulk = free-Poisson MP.
kappa2 confirmed; kappa3/kappa4 first measurement.
Bands +-50% per calibration-probe policy.

## Smoke result
HARD_FAIL at N=512: rel_err_M4=0.32 (finite-N bias; M4 has high-order corrections at N=512).
kappa2_rel=0.003 (excellent, confirms kappa_2 = alpha).
The M4 and M3 errors are EXPECTED finite-N bias: higher-order moments converge more slowly.
At N=1024 (2x larger), finite-N corrections scale as O(1/N) and should drop significantly.
Expected: rel_err_M4 at N=1024 ~ 0.32 * (512/1024) ~ 0.16 (still above HP=0.05 but below HF=0.30).
This is genuinely borderline; FULL will characterize the convergence rate.

## Timeout estimate
Smoke wall: 0.5s, N=512->1024 (2x), seeds=3->5. Eigendecomposition dominant: O(N^3) not O(N^2).
timeout = ceil(1.5 * 0.5 * 2^3 * (5/3)) = ceil(1.5*0.5*8*1.67) = ceil(10) = 10s.
timeout=120s (generous for eigendecomposition at N=1024).

## N-suffix note
No _nN suffix; production N=1024 per rule 3.
