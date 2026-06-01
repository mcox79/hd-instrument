# Pre-registration: hatano_sasa_v4_glauber

**Date:** 2026-05-27
**Anchor:** hatano_sasa_v4_glauber
**Script:** experiments/exp_hatano_sasa_v4_glauber.py
**Queue:** remote_cpu_queue
**Timeout:** 1200s

## Hypothesis

Stochastic Glauber (Metropolis) dynamics on the HDC substrate at finite temperature T>0
will exhibit genuine non-equilibrium steady-state (NESS) cost: sigma_hk > 0 and
the Hatano-Sasa identity hs_identity_val = <exp(-W_ex)> = 1.0 in stationarity.

Parent: hatano_sasa_v3_n8192_multiseed (MIDDLE_BAND: sigma_hk=0 due to deterministic dynamics;
v4 fix: stochastic Glauber at T=1.0).

## Configuration

- N: 512 (N_FULL)
- M: int(ALPHA_RATIO * N) patterns
- Dynamics: Glauber flip probabilities P(flip_i) = 1/(1 + exp(2*beta*h_i*v_i)), beta=1.0
- n_traj: 400 (FULL), 80 (SMOKE)
- n_steps: 20 per trajectory
- Seeds: [7, 17, 23, 31, 41] (FULL), [17] (SMOKE)

## Metrics

- hs_identity_val: <exp(-W_ex)> -- should equal 1.0 for proper NESS stationarity
- sigma_hk: housekeeping entropy production = max(0, total_var - |mean_W_ex|)

## Pre-registered bands (calibration probe; stochastic dynamics; no prior empirical anchor)

**HARD_PASS:**
- hs_identity_val in [0.50, 2.0] in >= 3/5 seeds (wider for stochastic noise)
- AND sigma_hk > 0.01 in >= 4/5 seeds (genuine NESS cost)

**HARD_FAIL:**
- hs_identity_val < 0.10 or > 10.0 in >= 3/5 seeds (HS identity violated)
- OR sigma_hk = 0 in ALL seeds (dynamics are still effectively deterministic)

**MIDDLE_BAND:** otherwise

NOTE: calibration probe, bands widened to +-50% per calibration-probe policy.
Theoretical prediction: at T > T_c (paramagnetic phase), hs_identity = 1.0 exactly.

## Timeout estimate

Smoke: N=128, 1 seed, n_traj=80, n_steps=20 -> 0.24s elapsed.
FULL: N=512, 5 seeds, n_traj=400, n_steps=20.
N-scale: (512/128)^1.5 = 8x. Traj-scale: (400/80) = 5. Seeds: 5.
But N-scale and traj are coupled (inner loop is n_traj * n_steps * N).
Estimate: 0.24 * 8 * 5 * 5 = 48s. Safety 25x: 1200s.
timeout_s = 1200.

## Downstream

- PASS: non-eq stat-mech row corroborated via Glauber NESS. Cap_map row stays 45-60%.
- FAIL (sigma_hk=0 again): Glauber dynamics DO satisfy detailed balance for this W.
  This would be a genuine finding: HDC Hopfield W satisfies detailed balance even with
  stochastic updates, meaning the substrate is not NESS at the STATIONARY phase.
  The NESS cost is only during the WRITING phase.
- Middle: partial NESS evidence; investigate temperature dependence.
