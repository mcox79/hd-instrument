# Pre-registration: PAC-Bayes KL extended corpus application

**Experiment:** wave14_pac_bayes_kl_extended_corpus_v1
**Script:** experiments/exp_wave14_pac_bayes_kl_extended_corpus_v1.py
**Date:** 2026-05-25
**Queue:** local_cpu_queue
**Expected runtime:** <5s

## Motivation

wave14_pac_bayes_laplace_selftests_v1: 7/7 self-tests PASS; Laplace violation is structurally expected (predicted ratio=1.00 > 0.5). The GPU v2 run is queued. This local probe applies the v1 KL-retention relationship (3 anchor cells) to the full 109-value Bet B corpus to characterize whether the PAC-Bayes floor formula is in the right regime (non-trivially tight vs loose vs violated).

## Hypothesis

With M=3000 tokens and KL_fisher in [10.77, 24.41] for retention in [0.80, 0.94], the PAC-Bayes floor should be in [0.9, 1.0] for all corpus classes, giving a valid but somewhat loose bound. The power-law extrapolation KL = A*(1-r)^B will inform whether GPU v2 needs a larger M to produce tight bounds.

## Pre-registered outcomes

- **FLOOR_VALID**: 0 violations AND tight_fraction >= 0.50
- **FLOOR_LOOSE**: 0 violations AND tight_fraction < 0.50 (M too small)
- **FLOOR_VIOLATED**: any floor > observed_retention (extrapolation failure)
- **FLOOR_THRESHOLD_INCONSISTENT**: partial violations

## Hard-pass / hard-fail bands

- **Hard-pass**: FLOOR_VALID (non-trivially tight, GPU v2 will give useful bounds)
- **Hard-fail**: FLOOR_VIOLATED with violation_rate > 50% (extrapolation unstable)
- **Middle-band**: FLOOR_LOOSE (valid but needs larger M in GPU v2)

## Calibration note

No prior empirical anchor for this extrapolation regime; bands reflect structural theory only. Per calibration-probe policy, this is an informational probe -- its outcome informs GPU v2 design, not a cap_map update trigger.

## Self-tests

1. pac_bayes_floor(KL=0, M=1000) = 1.0 exactly
2. pac_bayes_floor(KL=200, M=1000) = max(0, 1-sqrt(0.1)) = 0.684
3. Power-law fit on 3 known points: A>0, B finite
