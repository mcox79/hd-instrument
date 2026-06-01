# Prereg: bid_order_parameter_v4_full

**Date:** 2026-05-27
**Parent:** bid_order_parameter_v3_full (TIMEOUT at 300s), bid_order_parameter_v2 (completed)
**Script:** experiments/exp_bid_order_parameter_v4_full.py
**Queue:** remote_cpu_queue
**Version reason:** v3 was script-correct but timed out at 300s; v4 corrects timeout to 1500s

## Hypothesis

Substrate's binary intrinsic dimension (BID, TwoNN estimator) lies outside all three known
Hopfield-class reference bands (retrieval [1,2.5], spin-glass [N/4,N/2], paramagnetic [N-5,N])
in >= 4/5 seeds at N=1024, and is stable (outside all bands) at all N in {1024,2048,4096,8192}.
This is the decisive H1-vs-H2 discriminator.

## Pre-registered thresholds

**HP1 (novel class by BID):**
- BID outside ALL 3 reference bands at N=1024 in >= 4/5 seeds
- => P(H1 novel class) >= 0.65

**HP1+HP3 (novel class + N-stable):**
- HP1 met AND BID outside all 3 bands at every N in sweep
- => BID is a thermodynamic invariant, not finite-N artifact

**HF2 (band-crossing at large N):**
- BID drifts INTO a Hopfield band at large N in >= 4/5 seeds
- => substrate class is N-dependent; prior rejections are tautological

**MIDDLE-BAND:**
- HP1 not met but not HF2; boundary cases

No prior anchor (v3 timed out, v1 failed on metrics format). Bands are NOT calibration
probes -- the reference bands come from published Hopfield-class characterization
(arxiv 2601.17427). Verdict gates are pre-specified.

## Timeout estimate (CORRECTED from v3)

v3 timed out at 300s -- W construction at N=8192 is ~130s/seed.
Local benchmark:
- N=1024: ~0.7s per seed
- N=2048: ~8.2s per seed
- N=4096: ~33s per seed (extrapolated)
- N=8192: ~130s per seed (extrapolated from N=2048 with (4096/2048)^2 = 4x)
Full sweep: (0.7 + 8.2 + 33 + 130) * 5 seeds = 860s.
timeout_s = ceil(1.5 * 860) = ceil(1290) -> 1500s.

## N-suffix

No _nN suffix; multi-N sweep over {1024, 2048, 4096, 8192}.

## Smoke result

- smoke BID=3.61 at N=256 (OUTSIDE_ALL_BANDS), BID=3.99 at N=512 (OUTSIDE_ALL_BANDS)
- PASS: BID > 0, finite, > 100ms
- Note: BID=3.61 is in retrieval band [1.0, 2.5]? No: 3.61 > 2.5 but also 3.61 < N/4=64
  (spin-glass) and 3.61 << N-5=251 (paramagnetic). Confirmed: OUTSIDE_ALL_BANDS at smoke scale.
- Walk-back: smoke already shows strong signal (BID well outside all bands). Full 5-seed
  at N=1024 needed for verdict resolution (smoke only ran 1 seed N=256/512).
