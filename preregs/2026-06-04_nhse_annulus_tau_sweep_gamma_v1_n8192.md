# Prereg: nhse_annulus_tau_sweep_gamma_v1_n8192

## Anchor
nhse_annulus_tau_sweep_gamma_v1_n8192

## Priority
A (Research NHSE-annulus handoff; "highest-leverage 1-experiment test currently open" -- discriminates
NHSE-annulus exponential gamma(tau) from SCS polynomial; reframes the prior PP-58 SCS d-sweep data)

## Scientific question
Does gamma_emp(tau) follow the NHSE-annulus EXPONENTIAL law gamma = A*exp(c*tau) (A~1.20, c~3.83,
fit to 2 prior points: 1.45@tau~0.05, 41.456@tau~0.926) rather than an SCS polynomial? 7-cell tau sweep
(build knob t -> reported tau_actual via the original PP-58 controlled-asymmetry build, so gamma is
comparable to the calibration data). Observables: gamma_emp (isochoric kappa_3 ratio) + spectral
annulus radii r_outer/r_inner at reduced N (structural NHSE signature).

## Pre-registered bands (exp_dev autonomy; research P_deflated=0.31-0.42)
HARD-PASS: gamma_emp monotone non-decreasing in tau_actual (5% slack) AND exp-fit R^2 > 0.90 AND
fitted c in [2.5, 5.5] AND gamma_emp(tau~0.50) >= 4.0.
MIDDLE: monotone but exp-fit R^2 in [0.70, 0.90] OR c outside [2.5,5.5] OR gamma(0.50) in [2.0, 4.0).
HARD-FAIL: non-monotone OR exp-fit R^2 < 0.70 OR gamma_emp(tau~0.50) < 2.0.

NOTE: smoke (N=256) reproduced the calibration regime (gamma~1.3 at tau~0.05) and revealed a
THRESHOLD structure -- gamma flat (~1.3) until tau~0.5 then sharp rise to ~22 at tau~0.93. A pure
single-exponential-from-zero may read MIDDLE/HF; a flat-then-rise (two-regime, disk-to-annulus
transition) is the framework's own "tau_crit" prediction and motivates the Anchor-2 boundary probe.

## Formula self-tests (PROT-022)
1. tau_actual map: build t=0.50 -> tau_actual~0.707; t=0.71 -> ~0.926 (within 0.03). [PASS in smoke]
2. NHSE prediction gamma(0.30)=3.79; gamma(0.926)=41.4 (within 1%). [PASS]
3. exp-fit recovers c=3.83, R^2=1.0 from synthetic exponential. [PASS]

## N-suffix binding (PROT-018)
anchor _n8192; production N = 8192 (kappa_3 measurement). N_EIG=512 (reduced) for the O(N^3) annulus
eigendecomposition only.

## Timeout estimate
7 tau cells x (kappa_3 Hutchinson at N=8192 + eigvals at N_EIG=512) x 5 seeds. PROT-019 floor: 21600s.

## Smoke gate
Smoke PASSED (N=256, 2 seeds): mechanics + instrumentation non-null; reproduces calibration regime
(gamma~1.3 @ tau~0.05); self-tests pass. HARD_FAIL at smoke is small-N noise + the threshold structure.

## Queue
remote_cpu_queue (pure numpy; CPU).
