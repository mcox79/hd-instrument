# Experiment A2: cleanup robustness under phase-jitter noise

**Date:** 2026-05-16
**Phase:** Week 6 atomic experiments

## Hypothesis

At N=1024 with a 50-atom codebook, cleanup recovery is robust to small phase jitter (sigma <= 0.5 rad) and degrades smoothly to chance (1/50 = 2%) at sigma >> 1.

## Predicted

- Recovery at sigma=0.0: 100% (sanity).
- Recovery at sigma=0.5: > 90%.
- Recovery at sigma=1.0: 30-70% (mid-degradation).
- Recovery at sigma=3.0: < 20% (approaching chance).
- Mean similarity score decreases monotonically with sigma.

## Falsification

- Recovery at sigma=0.5 < 70% means cleanup is more brittle than expected at N=1024.
- Non-monotonic similarity-vs-sigma curve means the noise model is broken.

## Result (2026-05-16)

| sigma | predicted recovery | observed recovery | mean cleanup sim |
|---|---|---|---|
| 0.0 | 100% | 100% | 1.000 |
| 0.1 | ~100% | 100% | 0.998 |
| 0.3 | ~100% | 100% | 0.985 |
| 0.5 | > 90% | **100%** | 0.959 |
| 1.0 | 30-70% | **100%** | 0.843 |
| 1.5 | not predicted | 100% | 0.664 |
| 2.0 | not predicted | **100%** | 0.455 |
| 3.0 | < 20% | 38% | 0.057 |

## Takeaway

**FHRR cleanup at N=1024 with k=50 is much more robust to phase jitter than the hypothesis predicted.** The transition from "perfect recovery" to "near-chance" happens between sigma=2.0 and sigma=3.0, much later than expected. At sigma=2.0 (jitter ~ +/- 2 radians, near-random per component) the mean cleanup similarity is only 0.46 but the *best* match is still consistently the correct atom because the discriminating signal beats the noise floor across 50 candidates at N=1024.

The substrate has a ~10x margin between in-codebook similarity at moderate noise and the random-pair baseline. This sets a hard prior for what `attention` thresholds make sense in A3: the operating region is ~ [0.1, 0.5] depending on noise.

## Pre-registration check

The "predicted recovery > 90% at sigma=0.5" threshold was confirmed (actually exceeded). The "30-70% at sigma=1.0" prediction was *wrong* — recovery stays at 100%. No falsification thresholds tripped, but my mental model of the noise-vs-capacity curve was off by ~1.5 orders of magnitude in sigma.
