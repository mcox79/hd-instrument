# Prereg: wave14_1rsb_pq_retained_v4

**Date:** 2026-05-26
**Parent:** wave14_1rsb_pq_retained_v3 (in-flight; N=8192, 30 seeds)
**Trigger:** ship when v3 returns HARD_PASS (binder > 0.30 AND n_peaks >= 2 at N=8192)
**Question:** Does the 1-RSB signal strengthen at N=16384 (consistent with genuine multi-basin)?

## Hypothesis
If v3 shows genuine 1-RSB basin structure, the signal should grow with N because the
noise floor drops as 1/(N*N) for the W weight-overlap distribution. A UV-problem artifact
would show constant or decreasing binder at larger N.

## Design
- N = 16384 (2x v3)
- 20 seeds (same as v3 for direct comparison)
- KDE bandwidth: 0.005 (tighter for N=16384)
- Required peak separation: 3sigma (vs v3's 2sigma)
- Required binder: > 0.40 (vs v3's > 0.30)
- GPU overnight_queue (~3-4 hrs)

## Pre-registered bands
- **HARD_PASS**: binder > 0.40 AND n_peaks >= 2 AND sep >= 3sigma AND mean_q > 5*noise_floor
- **HARD_FAIL**: binder <= 0.10 OR n_peaks <= 1 at N=16384 (weaker than v3 HARD_PASS)
- **UV_PROBLEM_CONFIRMED**: binder < 0 at N=16384 (persists from v1 at N=2048)
- **MIDDLE_BAND**: binder in (0.10, 0.40) OR sep < 3sigma
- **INSTRUMENTATION_FAIL**: all binder values None OR KDE fails

## Calibration
Prior anchor: v3 (N=8192) HARD_PASS binder ~0.30+. Expected at N=16384 under genuine 1-RSB:
binder should grow toward 2/3 (1-RSB asymptote). Threshold of 0.40 = 2/3 of asymptote as lower bound.

## Middle-band outcome plan
If MIDDLE_BAND: dispatch ultrametric triple probe to independently confirm basin structure
(exp_wave14_1rsb_ultrametric_triple_v1 -- different observable, complementary 1-RSB confirmation).
