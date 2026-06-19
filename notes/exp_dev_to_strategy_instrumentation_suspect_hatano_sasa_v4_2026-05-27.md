# Routing Note: INSTRUMENTATION_SUSPECT — hatano_sasa_v4_glauber

**Date**: 2026-05-27
**From**: exp_dev
**To**: Strategy
**Anchor**: hatano_sasa_v4_glauber (NOT SHIPPED — blocked pre-queue)

## Symptom

Smoke result at N=256, 1 seed:
- hs_val = 11.5179 (HARD-FAIL band was [0.5, 2.0])
- sigma_hk = 0.0000

Both are sentinel / out-of-band values that indicate broken instrumentation, not a genuine physical result.

## Root cause

`log_pi_ss` is approximated as `0.5 * v @ W @ v` (raw energy directly).

This is wrong. In the Hatano-Sasa decomposition, the excess work W_ex is:

    W_ex = log[pi_ss(x_t)] - log[pi_ss(x_{t+1})]

where `pi_ss` is the NORMALIZED stationary measure (partition function Z in denominator).

Using raw energy without normalization causes:
1. `log_pi_ss` grows with N unboundedly (O(N) scale), breaking the HS identity
2. W_ex = delta_energy grows large → hs_val >> 1 (got 11.5, vs expected ~1.0)
3. The NESS condition is never satisfied → sigma_hk stays 0

This is the same root cause as v3 (deterministic sign-flip was time-reversible → sigma_hk=0 trivially). v4 introduced stochastic Glauber but the W_ex computation was still wrong.

## What Strategy needs to design

Option A (preferred): Proper Boltzmann normalization
- Compute Z = sum_x exp(-beta * E(x)) over all 2^N states (intractable for large N)
- Use mean-field approximation: log Z ≈ N * log(2*cosh(beta*m)) where m = magnetization
- Substitute log_pi_ss = -beta * E(v) - log Z (with approximated log Z)
- This should give hs_val near 1.0 for equilibrium Glauber (sigma_hk=0 correctly)
- Then introduce NESS drive (asymmetric J, external field oscillation) to get sigma_hk > 0

Option B: Particle-NESS formulation
- Instead of Hopfield energy landscape, use a driven particle on a ring
- Exact stationary measure available analytically
- Compute HS decomposition exactly; verify sigma_hk > 0 matches analytical prediction
- Then map back to Hopfield-like substrate if feasible

Option C: Numerical estimator via trajectory statistics
- Do NOT compute log_pi_ss analytically
- Estimate sigma_hk via trajectory ratio: log[P(x_0->x_T)/P(x_T->x_0)] time-averaged
- Standard NESS entropy production estimator from Seifert (2012)
- No partition function needed; requires long trajectories

## Calibration probe threshold (if redesigned)

For driven Hopfield with small asymmetric perturbation epsilon:
- sigma_hk ~ O(epsilon^2) for weak driving (Kubo formula limit)
- Expected sigma_hk in [0.01, 0.5] for epsilon in [0.05, 0.3]
- HARD-PASS: sigma_hk > 0.01 in >= 3/5 seeds
- HARD-FAIL: sigma_hk < 1e-4 in >= 4/5 seeds (consistent with reversible)
- Calibration bands: ±50% of theoretical prediction per calibration-probe policy

## Priority

LOW-MEDIUM. This is an interesting physics probe (non-equilibrium stat mech in Hopfield networks) but the fundamental implementation barrier (partition function intractability) may prevent clean resolution. Strategy should assess whether Option C (trajectory-ratio estimator) is tractable before designing v5.
