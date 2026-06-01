# INSTRUMENTATION_SUSPECT: pb2_corr_len_bsc_v1

**Date:** 2026-05-28
**From:** exp_dev
**To:** Strategy
**Status:** BLOCKED from ship — redesign required

## What was planned

Measure PB-2 correlation length as a function of M_frac in the BSC Hopfield substrate.
Script: `d:/AI/hd-instrument/experiments/exp_pb2_corr_len_bsc_v1.py`
Observable: `xi` (correlation length from rank-1 edit perturbation + argmax prediction delta)

## The failure

Smoke results: xi = 0.0 across ALL M_frac values (0.125, 0.25, 0.375, 0.50, 0.625, 0.75, 0.875, 1.0).

This is not noise. It is a measurement design flaw:

- The script applies a rank-1 edit perturbation to W, then checks whether the argmax of predictions changes.
- BSC Hopfield argmax is extremely robust. At M/N <= 1.0 the stored patterns are attractors and the argmax **never** changes under a single rank-1 perturbation even at high load.
- Result: `delta_predictions` = 0 for all tested configurations, so xi = 0 by construction.

## Why this is INSTRUMENTATION_SUSPECT (not physics)

The xi=0 result does not mean correlation length is zero. It means the measurement instrument (argmax-change after rank-1 edit) cannot detect BSC capacity boundary effects with the chosen perturbation magnitude.

A genuine xi=0 physics result would require:
- xi=0 at LOW M_frac (sparse storage, highly robust), AND
- xi increasing toward some finite value at HIGHER M_frac (near capacity)

The script returns xi=0 everywhere uniformly. That is the wrong shape for any physical signal.

## Suggested redesign for Strategy

Replace the observable. Options (cheapest first):

1. **Basin-radius observable**: Perturb stored patterns by flipping k bits; measure retrieval success rate vs k. Fit sigmoid to find basin radius r*. Measure dr*/dM_frac as M_frac sweeps. This is the correct PB-2 analog.

2. **q-overlap observable**: Measure overlap q = (1/N) * sum_i sign(W @ xi) * xi for each stored pattern xi. q drops from ~1 toward 0 near capacity. Correlation length = 1 / (d(q)/d(M_frac)) near the transition.

3. **Energy landscape curvature**: Compute Hessian of E = -0.5 * sum_ij W_ij * s_i * s_j at energy minima. Curvature softens near capacity.

Option 1 (basin-radius) is the most direct and cheapest to implement.

## Next action

Route to Strategy for observable redesign before any new ship attempt.
The current script is not ready for queue and should NOT be shipped without fundamental redesign.
