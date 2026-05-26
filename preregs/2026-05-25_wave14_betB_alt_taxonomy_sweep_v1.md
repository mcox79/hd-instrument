# Pre-registration: Alt taxonomy sweep for Bet B retention

**Filed:** 2026-05-25
**Script:** experiments/exp_wave14_betB_alt_taxonomy_sweep_v1.py
**Queue:** local_cpu_queue
**Estimated runtime:** <20s

## Hypothesis

The 6-class shift taxonomy walked back at FULL replication. The 3-class coarse taxonomy
HARD-PASSED. This sweep tests all plausible 2/3/4/5/6-class variants simultaneously
using silhouette width (the unbiased, unsupervised metric) to identify the canonical
optimal taxonomy for Bet B retention predictability.

## Pre-registered outcomes

**HARD-PASS:** best taxonomy silhouette >= 0.60 AND all K cluster CIs non-overlapping
AND KW p < 0.01. Interpretation: canonical taxonomy identified at that K.

**HARD-FAIL:** best silhouette < 0.40. No taxonomy achieves CI-level separation beyond
the omnibus KW signal.

**MIDDLE:** best silhouette in [0.40, 0.60) or CI overlap at some pair.

## Input data

- data/exp_wave14_betB_shift_class_predictor_v1/metrics.json (primary, 5 seeds)
- data/exp_wave14_betB_shift_class_full_replication_v1/metrics.json (fresh_seeds only)

## Taxonomies swept (8 total)

2class_highlow, 3class_standard (existing), 3class_nosplit, 4class_splithi,
4class_plateau (0.94/0.84/0.73/0.63), 4class_noreplay_isolated, 5class_fine,
6class_original (existing, walked back)

## No prior empirical anchor for silhouette threshold

Calibration-probe policy: threshold 0.60 set based on standard silhouette interpretation
(>0.5 = reasonable structure, >0.7 = strong structure). No substrate-specific prior.
