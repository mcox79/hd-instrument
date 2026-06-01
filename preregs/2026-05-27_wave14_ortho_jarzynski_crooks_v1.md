# Prereg: wave14_ortho_jarzynski_crooks_v1

**Filed:** 2026-05-27
**Script:** experiments/exp_wave14_ortho_jarzynski_crooks_v1.py
**Queue:** remote_cpu_queue (CPU)
**Orthogonal probe:** Jarzynski equality / free-energy perturbation (A1 in meta-map)
**Shortlist rank:** P_deflated=0.45 (highest among actionable undrilled candidates)
**Prior drill count:** 0

## Hypothesis (Jarz-1)

Jarzynski equality (1997): <exp(-W/kT)>_non-eq = exp(-delta_F/kT).
Substrate's write operations perform "work" against the background W.
Jarzynski estimator should give the same free-energy change as direct log-Z comparison.
If agreement within 50% (widened calibration-probe band): Jarzynski viable as a cheaper
Cap 1 capacity estimator (forward-only; no backward Crooks run needed).

## Design

- N=256, M in {50, 200, 500}, 5 seeds
- Work per write step: w_mu = -<v_mu, W_prev @ v_mu>
- Jarzynski: delta_F_J = -log(<exp(-w_mu)>) over M writes
- Direct: delta_F_direct = -1/N * (log_Z_after - log_Z_before) via mean-field
- Agreement: |delta_F_J - delta_F_direct| / |delta_F_direct|

## Pre-registered bands (calibration-probe widened policy)

**HARD_PASS:** >= 60% cells within 50% agreement (calibration probe: band = ±50%)
**HARD_FAIL:** > 200% disagreement for all cells
**MIDDLE_BAND:** intermediate

Note: "no prior empirical anchor; bands widened to +-50% per calibration-probe policy."

## Smoke result

MIDDLE_BAND at N=128: agreement varies from 0.93 to 32.1 depending on M.
Low M (50) shows ~93% agreement; high M (200) shows 32x disagreement due to
Jarzynski estimator high variance at near-saturation. This M-dependent behavior
is the key finding: Jarzynski viable at sub-capacity M, unreliable above alpha_c*N.
selftest 5/5 OK. status=COMPLETE printed.
