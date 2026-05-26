# Pre-registration: wave14zm_noise_robust

Date: 2026-05-21
Status: Pre-registered, gated
Priority: new dimension — graceful degradation under W perturbation
Author: experiment_dev session, pipeline tick 49

## Why
Substrate W is a sum of rank-1 outer products. Real-world deployment may include
floating-point noise, partial updates, quantization. Test: sweep gaussian noise
sigma added to W elements (relative to W's element std), measure retrieval
argmax_acc. At what sigma does retrieval start to fail?

This characterizes the substrate's noise floor and gives a quantization
budget for compression / fixed-point deployment.

## Verdict labels
- NOISE_ROBUST_KERDOCK_TOLERATES_SIGMA_<S>
- NOISE_ROBUST_BOTH_TOLERATE
- NOISE_ROBUST_KERDOCK_FAILS_AT_SIGMA_<S>
- NOISE_ROBUST_BOTH_FAIL_IMMEDIATELY
- NOISE_ROBUST_INCONCLUSIVE

## Runtime: ~3 min
