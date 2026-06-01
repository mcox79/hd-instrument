# Prereg: ne3_crooks_kl_drift_v1

**Date**: 2026-06-01
**Anchor**: ne3_crooks_kl_drift_v1
**Queue**: remote_cpu_queue
**Script**: experiments/exp_ne3_crooks_kl_drift_v1.py
**Source**: notes/research_round5_7_drills_synthesis_2026-06-01.md (NE-3, Crooks C2)

## Hypothesis

Crooks Candidate 2 (KL-divergence drift detection): forward/reverse retrieval
trajectory KL_div(F||R) increases >= 3-sigma above pre-drift baseline at a
synthetic drift point, with <5% false-alarm rate. Crooks FT is FINITE-N EXACT
(symmetric Hebbian W satisfies microreversibility).

## Design

- N = 1024, M_A = 64 pre-drift patterns, M_drift = 32 added at drift event
- 50 forward + 50 reverse trajectories per phase, 20 Glauber steps each
- 10 pre-drift baseline windows; histogram KL estimator (20 bins)
- 5 seeds

## Pre-registered thresholds (LOAD-BEARING)

**HARD-PASS**: KL_div(F||R) at drift point >= 3.0 sigma above pre-drift
baseline AND false-alarm rate <= 5%; in >= 4/5 seeds.

**HARD-FAIL**: KL_div at drift point < 1.0 sigma above baseline in >= 4/5 seeds
OR false-alarm rate > 20% in >= 4/5 seeds.

**MIDDLE-BAND**: 1.0-3.0 sigma (weak signal); or 3-4/5 seeds pass.

## No prior empirical anchor

First Crooks trajectory test on substrate. Bands widened per calibration-probe
policy. Histogram KL at N=50 trajectories has known variance; full 5-seed run
needed to measure signal/noise robustly.

## Smoke result

Smoke (2 seeds): sigma_above = 0.03-0.06 (very weak signal at smoke scale).
MIDDLE_BAND. The histogram KL estimator has high variance at N=50 traj.
Full run with 5 seeds may show clearer signal. If still < 1-sigma at FULL:
route back to Strategy for higher-N trajectory count.

## Timeout estimate

smoke_wall_s = 100s; 5/2 seeds; linear scaling.
timeout_s = ceil(1.5 * 100 * 2.5) = ceil(375) = 600s.

## N-suffix

No _nN suffix. Production N = 1024; stated per PROT-018 rule 3.
