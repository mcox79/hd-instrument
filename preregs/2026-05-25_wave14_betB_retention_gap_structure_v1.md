# Pre-registration: Retention gap structure analysis

**Filed:** 2026-05-25
**Script:** experiments/exp_wave14_betB_retention_gap_structure_v1.py
**Queue:** local_cpu_queue
**Estimated runtime:** <15s

## Hypothesis

Aggregate all available Bet B retention_A values across all experiments and apply
unbiased 1D cluster analysis (gap statistic + K-means) to find the natural K without
assuming any taxonomy. Cross-validates against the dispatch-note 3-plateau model.

## Pre-registered outcomes

**STRUCTURE_FOUND:** optimal K in {2,3,4} via gap statistic AND >= 2 of 3 dispatch-note
plateaus (0.94, 0.74, 0.60) within 0.05 of a cluster center.

**STRUCTURE_BIMODAL:** optimal K = 2 (only HIGH vs LOW detectable).

**STRUCTURE_DIFFUSE:** optimal K >= 5 or < 2 of 3 plateaus matched.

## Data source

All data/exp_wave14_betB_*/metrics.json files with per_class.values or per_seed_pair
structure.

## Note

Wide collection expected (110+ unique values from 20+ experiments). Gap statistic
via 20-bootstrap uniform reference distribution. Merge threshold 0.04 for natural-break detection.
