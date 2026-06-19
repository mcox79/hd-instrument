# Pre-registration: wave14h_scale_K_v2 (correlated keys, scaling)

Date: 2026-05-20
Status: Pre-registered, gated, oracle-asserted
Experiment: [exp_wave14h_scale_K_v2.py](../experiments/exp_wave14h_scale_K_v2.py)

## Why v2

v1 used orthogonal keys and argmax recovery -> leak_reduction=0pp at all K
(argmax is magnitude-invariant; intermediate-alpha erase shrinks the value
but argmax still picks it). v2 uses correlated keys + alpha=1.0 to actually
test scaling.

## Hypothesis

At alpha=1.0 with rank_L = n_facts/4 (consistent correlation across K),
the erase mechanism gives leak_reduction>=30pp AND kept_recall>=75% at
every n_facts in {50, 200, 500, 1000}.

## Kill criterion

Even at n_facts=50 the mechanism fails (leak_reduction<30pp OR kept<75%) ->
test setup is wrong or anti-Hebbian is fundamentally inadequate at this
correlation level.

## Oracle assertions

1. `mean_pairwise_std in [0.03, 0.50]` at largest K (keys correlated)
2. `baseline_leak >= 0.70` at largest K (substrate stores facts)
3. `abs(baseline_leak - method_B_leak) >= 0.10` (mechanism actually fires)

## Operational definition

- N=4096, alpha=1.0, erase_frac=0.25
- For each n_facts in {50, 200, 500, 1000}:
  - rank_L = n_facts/4 (keeps correlation strength constant)
  - 5 seeds
  - Method A: no W edit
  - Method B: iteratively anti-Hebbian erase 25% of facts
  - Measure leak rate, kept recall

## Expected runtime

Smoke (N=512, K in {30,80}): ~3 sec
Full (N=4096, K up to 1000): ~3-5 min on GPU

## What product decision this enables

PASS_ALL -> "GDPR-grade erase scales linearly to 1000+ fact stores."
PASS_SMALL -> "Bounded scale (n_facts <= 200)."
FAIL -> Anti-Hebbian alone is inadequate; need extension.
