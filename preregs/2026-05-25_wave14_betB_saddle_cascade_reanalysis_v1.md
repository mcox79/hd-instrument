# Pre-registration: Saddle-cascade plateau signature re-analysis

**Filed:** 2026-05-25
**Script:** experiments/exp_wave14_betB_saddle_cascade_reanalysis_v1.py
**Queue:** local_cpu_queue
**Estimated runtime:** <30s

## Hypothesis

Candidate (v) from research_alternative_theoretical_homes_2026-05-24.md (P=0.46):
Saad-Solla / Biehl-Schwarze saddle-cascade framework predicts retention plateaus
are fixed points of order-parameter ODEs, setting DISCRETE levels immune to continuous
parameter variation. Falsifier: discrete 3-state BIC < sigmoid BIC.

## Pre-registered outcomes

**CASCADE_PASS:** discrete 3-state BIC lower than sigmoid by delta_BIC > 2 AND
equal-spacing formula error < 0.05. Cascade framework is the better fit.

**CASCADE_FAIL:** sigmoid BIC lower by > 2. Continuous framework preferred.

**CASCADE_INCONCLUSIVE:** |delta_BIC| <= 2. Full GPU overlap-fraction sweep needed.

## Data source

data/exp_wave14_betB_shift_class_predictor_v1/metrics.json

## Note

This is the LOCAL re-analysis variant. Full GPU saddle-cascade test (5-teacher
overlap-fraction sweep) is in-flight as a separate experiment. These are independent
falsifiers: the local test uses EXISTING data, the GPU test generates new data.
