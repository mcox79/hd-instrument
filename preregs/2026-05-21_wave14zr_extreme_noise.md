# Pre-registration: wave14zr_extreme_noise

Date: 2026-05-21
Status: Pre-registered, gated
Priority: find substrate noise breakpoint
Author: experiment_dev session, pipeline tick 54

## Why
zm tolerated sigma=16 (highest tested value). The substrate noise floor
is above 16x W's element std — surprising. Push to sigma {16, 32, 64, 128, 256}
to find break point.

## Verdict labels (inherited from zm)
- NOISE_ROBUST_KERDOCK_TOLERATES_SIGMA_<S>
- NOISE_ROBUST_BOTH_TOLERATE
- NOISE_ROBUST_KERDOCK_FAILS_AT_SIGMA_<S>
- NOISE_ROBUST_BOTH_FAIL_IMMEDIATELY
- NOISE_ROBUST_INCONCLUSIVE

## Runtime: ~3 min
