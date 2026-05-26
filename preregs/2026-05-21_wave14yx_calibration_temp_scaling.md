# Pre-registration: wave14yx_calibration_temp_scaling

Date: 2026-05-21
Status: Pre-registered, gated
Priority: temperature-scaling calibration sweep follow-up to yd
Author: experiment_dev session, pipeline tick 31

## Why
yd tested calibration at fixed BETA=8. yx sweeps BETA in {1, 2, 4, 8, 16, 32}
and finds the post-hoc temperature that minimizes ECE. Standard post-hoc
calibration fix (Guo 2017).

## Verdict labels
- TEMPSCALE_RESCUES_AT_BETA_<B>: best ECE < 0.05 found at BETA=B
- TEMPSCALE_MARGINAL_AT_BETA_<B>: best ECE in [0.05, 0.15)
- TEMPSCALE_NO_RESCUE: all BETAs give ECE >= 0.15
- TEMPSCALE_INCONCLUSIVE

## Runtime: ~1-2 min
