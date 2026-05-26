# Pre-registration: 2-tier vs 3-tier vs 4-tier taxonomy contrast

**Experiment:** wave14_taxonomy_contrast_retention_sep_v1
**Script:** experiments/exp_wave14_taxonomy_contrast_retention_sep_v1.py
**Date:** 2026-05-25
**Queue:** local_cpu_queue
**Expected runtime:** <5s

## Motivation

wave14_betB_alt_taxonomy_sweep_v1 found 4class_noreplay_isolated is the best single taxonomy (sil=0.584), just below PASS threshold 0.60. This analysis contrasts all three tier levels (K=2, K=3, K=4) on silhouette, F-ratio, incremental efficiency, product clarity, and Saad-Solla compatibility, to determine which taxonomy to use for the substrate-product framing.

## Hypothesis

The 4-tier taxonomy wins on silhouette (absolute) but the 3-tier taxonomy wins on F-ratio per class (efficiency). The Saad-Solla cascade predicts K=3 natural states; the empirical data may show K=4 as better-fitting due to the NO_REPLAY / STAGE4 split.

## Pre-registered outcomes

- **FOUR_TIER_WINS**: 4-tier strictly dominates on both silhouette AND F-ratio
- **THREE_TIER_OPTIMAL**: 3-tier has better incremental gain per class than 4-tier
- **TWO_TIER_SUFFICIENT**: 2-tier F-ratio >= 80% of 4-tier F-ratio (small marginal gains)
- **TAXONOMY_MIXED**: different metrics point to different optima

## Hard-pass / hard-fail bands

- **Hard-pass**: FOUR_TIER_WINS (clear recommendation for 4-tier product framing)
- **Hard-fail**: none applicable (this is a classification/recommendation probe)
- **Middle-band**: TAXONOMY_MIXED or THREE_TIER_OPTIMAL

## Saad-Solla compatibility check

If cascade predicts K=3 but best silhouette is at K=4, the cascade framework needs extending to 4-state cascades. This is pre-registered as a falsifiable sub-test.

## Self-tests

1. F-ratio for clearly separated 3 groups (means 1,5,9): F >> 100
2. F-ratio for identical groups: F ~ 0
3. Silhouette for 2 perfectly separated groups: sil > 0.8
4. Silhouette for 1 group: sil = 0.0
