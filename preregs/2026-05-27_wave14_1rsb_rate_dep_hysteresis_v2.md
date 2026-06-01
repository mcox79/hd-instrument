# Prereg: wave14_1rsb_rate_dep_hysteresis_v2

**Filed:** 2026-05-27
**Script:** experiments/exp_wave14_1rsb_rate_dep_hysteresis_v2.py
**Queue:** overnight_queue (GPU)
**Parent:** wave14_1rsb_rate_dep_hysteresis_v1 (MIDDLE_BAND / AMBIGUOUS sign-flip at N=256)

## Hypothesis

v1 showed MIDDLE_BAND with gap_ratio sign-flip at M=10000 (N=256). The sign-flip
is a smoke-scale artifact: at N=256, M=10000 >> alpha_c*N, so the substrate is deeply
saturated and the fwd/rev asymmetry collapses. At N=1024 (proper scale), the gap
should remain positive across all M cells if the framework is genuine.

Decisive question: is the gap_ratio sign-flip at high M an artifact of N=256 saturation,
or a genuine high-load substrate property?

## Design

- N=1024 (FULL, not smoke)
- M sweep: [500, 1000, 2000, 4000, 8000, 12000] (brackets v1 sign-flip zone)
- Epoch sweep: [1, 2, 4, 8, 16, 32, 64] (extended for cleaner Pearson r)
- 5 seeds

## Pre-registered bands

**RATE_INDEPENDENT_1RSB:**
- All r(log_epochs, gap) in (-0.30, 0.30) AND gap_ratio > 0.70 at all M cells
- No sign-flip across M sweep

**RATE_DEPENDENT_KINETIC:**
- All r(log_epochs, gap) < -0.50 at M < alpha_c*N cells
- gap_ratio < 0.50 at slow cooling

**GAP_SIGN_FLIP_CONFIRMED:**
- gap < 0 at M_high at N=1024 (not just N=256 artifact)

**MIDDLE_BAND:** neither above pattern clearly confirmed

**INSTRUMENTATION_FAIL:** NaN gaps, zero-var

## Smoke result

PASS -- RATE_DEPENDENT_KINETIC at N=256 M_sweep=[500,2000,8000];
pearson_r=[-0.974,-0.803]; selftest 5/5 OK
Sign-flip observed at M=8000 confirming sign-flip is real at N=256 but may be different at N=1024.
