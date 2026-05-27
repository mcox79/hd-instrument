# Prereg: wave14_betB_rd_perturbation_recovery_v2

**Date:** 2026-05-26
**Parent:** wave14_betB_rd_perturbation_recovery_v1 RD_HARD_FAIL (delta=0.217, no recovery)
**Question:** Does a SMALLER perturbation (k_perturb=1 vs v1's k=3) show partial recovery?

## Hypothesis
v1 perturbation was very large (delta=0.217, shifted from 0.74 to ~0.52). This may have
pushed the system past the basin boundary. A smaller perturbation (k_perturb=1, expected
delta ~ 0.05-0.10) may stay within the basin and show RD-terrace restoring force.

## Design
- N=1024; 3 seeds; k_perturb=1 (vs v1 k=3); same recovery window
- CPU (remote_cpu_queue); ~20-40 min

## Pre-registered bands
- **HARD_PASS (RD-terrace confirmed)**: fit_R2 > 0.7 AND lambda > 0 AND |R_inf - 0.74| < 0.05
- **HARD_FAIL (saddle-cascade confirmed)**: monotone drift, fit_R2 < 0.3
- **MIDDLE_BAND**: fit_R2 in [0.3, 0.7]
- **INSTRUMENTATION_FAIL**: perturbation delta < 0.03 (too small to perturb)

## Calibration
v1 had delta=0.217 (too large). v2 targets delta in [0.03, 0.10]. If HARD_FAIL again,
the RD-terrace hypothesis is closed across both small and large perturbation regimes.
