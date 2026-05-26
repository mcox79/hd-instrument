# Pre-registration: MoE alpha_c formula verification

**Filed:** 2026-05-25
**Script:** experiments/exp_wave14_moe_alpha_c_formula_verify_v1.py
**Queue:** local_cpu_queue
**Estimated runtime:** <5s

## Hypothesis

research_substrate_alpha_c_anomaly_2026-05-24.md recalibrated the alpha_c band to
[0.40, 0.70] using the correct reference class: linear heteroassociator with
alpha_c(tau) = 1/tau^2 - 1 (not autoassociative Hopfield alpha_c ~ 0.138).

This probe verifies: (1) the formula is numerically correct, (2) the smoke data
matches the formula at all 4 grid points, (3) the predicted alpha_c(0.80) = 0.5625
falls inside the corrected band, (4) M_per_expert recommendation is valid.

## Pre-registered outcomes

**FORMULA_VERIFIED:** formula matches known value (alpha_c(0.80) = 0.5625, error < 1e-4)
AND smoke data matches formula within 0.005 at all 4 points
AND alpha_c(0.80) in [0.40, 0.70].

**FORMULA_MISMATCH:** formula deviation > 0.01. Revisit derivation.

**BAND_MISMATCH:** formula correct but outside [0.40, 0.70].

## Self-test anchors (from research note)

Smoke data at N=512:
- M=50: predicted cos=0.955, measured=0.954
- M=100: predicted cos=0.917, measured=0.916
- M=200: predicted cos=0.847, measured=0.845
- M=400: predicted cos=0.752, measured=0.750

No prior empirical anchor: bands widened per calibration-probe policy.
