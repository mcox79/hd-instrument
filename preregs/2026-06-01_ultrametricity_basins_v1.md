# Prereq: ultrametricity_basins_v1

## Scientific question
Does substrate exhibit ultrametric basin organization (FRSB signature)?
Ultrametricity ratio R = q_(2)/q_(3) should be ~1 in FRSB, bimodal in 1-RSB.

## Pre-registered bands
HARD-PASS: mean ratio > 0.80 in >= 4/5 seeds. P(q) has continuous support.
MIDDLE: mean ratio > 0.60.
HARD-FAIL: mean ratio < 0.50 in >= 3/5 seeds.
Calibration probe; +-50% per policy. HP at 0.80; HF at 0.50.

## Walk-back gate
Smoke shows mean_ratio~0.63 (borderline). FULL n_starts doubled to 30 (from smoke 10) per walk-back rule.

## N-suffix
No _nN suffix; production N=2048; rationale: ultrametricity test GPU budget.

## Timeout estimate
smoke_wall_s=0.1 (CPU). GPU ~5x faster. ceil(1.5 * 0.1 * (2048/512)^1.5 * (5/2)) = ceil(6.5) -> timeout_s=900 (conservative GPU overhead).

## Date
2026-06-01
