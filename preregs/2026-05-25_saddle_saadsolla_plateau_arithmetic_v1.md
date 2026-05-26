# Pre-registration: Saad-Solla plateau arithmetic deeper analysis

**Experiment:** wave14_saddle_saadsolla_plateau_arithmetic_v1
**Script:** experiments/exp_wave14_saddle_saadsolla_plateau_arithmetic_v1.py
**Date:** 2026-05-25
**Queue:** local_cpu_queue
**Expected runtime:** <5s

## Motivation

wave14_betB_saddle_cascade_reanalysis_v1 returned CASCADE_PASS (delta_BIC=194.9, spacing_error=0.038). Now drilling into the specific Saad-Solla saddle-point arithmetic: do the 3 plateau heights satisfy equal-ANGLE spacing (via the cos^2 retention-overlap map), not just equal-HEIGHT spacing? Equal-angle spacing is the structural prediction of the Saad-Solla framework; equal-height spacing is only a first-order approximation.

## Hypothesis

The 3 plateau groups (G1=0.899, G2=0.804, G3=0.633) arise from equal-angular spacing in the mode-overlap space: theta_mid = (theta_top + theta_bottom) / 2 where theta = arccos(sqrt(retention)).

## Pre-registered outcomes

- **ANGLE_CONFIRMS_CASCADE**: angle gap ratio in [0.80, 1.25] AND height gap ratio NOT in [0.85, 1.15]. Strongest Saad-Solla confirmation.
- **BOTH_EQUAL**: both pass. Degenerate (small-angle regime); consistent with cascade.
- **NEITHER_EQUAL**: neither passes. Challenges saddle-cascade as mechanism.
- **CASCADE_ANGLE_PASS**: angle passes, height borderline. Consistent.

## Hard-pass / hard-fail bands

- **Hard-pass**: ANGLE_CONFIRMS_CASCADE OR BOTH_EQUAL
- **Hard-fail**: NEITHER_EQUAL with angle_gap_ratio outside [0.60, 1.40]
- **Middle-band**: angle_gap_ratio in [0.60, 0.80) but not all three tests failing

## Self-tests

1. theta(r=1.0) = 0 exactly
2. theta(r=0.25) = pi/3 exactly
3. Equal-angle midpoint arithmetic (0.1+0.3)/2 = 0.2
4. Round-trip: retention -> theta -> retention for r in {0.6, 0.75, 0.9}
