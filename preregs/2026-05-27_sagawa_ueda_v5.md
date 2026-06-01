# Prereg: sagawa_ueda_v5

**Date:** 2026-05-27
**Parent:** sagawa_ueda_v4 (TIMEOUT at 1200s), sagawa_ueda_deletion_cert_v2 (HARD_PASS N=4096)
**Script:** experiments/exp_sagawa_ueda_v5.py
**Queue:** remote_cpu_queue
**Version reason:** v4 was script-correct but timed out; v5 is identical with corrected timeout

## Hypothesis

At N=8192, erase_work >= su_bound (Sagawa-Ueda thermodynamic bound) for all stored patterns,
confirming the deletion certificate mechanism holds at the largest operationally relevant scale.

## Pre-registered thresholds

**HARD-PASS:**
- su_frac >= 0.70 in >= 4/5 seeds at N=8192
- AND excess_mean > 0 in all seeds

**HARD-FAIL:**
- su_frac < 0.40 in >= 3/5 seeds (SU bound breaks at N=8192)

**MIDDLE-BAND:**
- su_frac drops below 0.70 in 1-2 seeds only
- OR excess_mean turns negative in any seed

Prior anchor: v2 HARD_PASS at N=4096 with su_frac=1.0 (5/5 seeds). Bands NOT widened
to +-50% because prior anchor exists and this is a direct envelope extension.

## Timeout estimate

Timing from local benchmark:
- N=2048, M=256: outer-product construction 9.5s per seed
- N=8192, M=1024: scales as (8192/2048)^2 * (1024/256) = 64x -> ~608s per seed
- 5 seeds: ~3040s
- timeout_s = ceil(1.5 * 3040) = ceil(4560) -> 4800s

Flag: >2h run. Acceptable for decisive N=8192 SU-bound confirmation.
v4 failure: 1200s timeout was 4x too low.

## N-suffix

No _nN suffix in anchor name; production N = 8192 stated explicitly in script (N_FULL = 8192).

## Smoke result

- smoke su_frac=1.0000 at N=512 (1 seed, 0.8s)
- PASS: non-zero, non-sentinel; > 100ms
- Walk-back: smoke d >> 1.0 (su_frac=1.0 >> threshold 0.70); no walk-back needed
