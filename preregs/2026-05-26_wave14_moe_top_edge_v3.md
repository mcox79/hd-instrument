# Prereg: wave14_moe_top_edge_v3

**Date:** 2026-05-26
**Parent:** wave14_moe_top_edge_v2 FREE_ADDITIVE_FORMULA_ERROR (offset=0.61)
**Question:** Does the corrected structural ratio formula (ratio_predicted=1.0) match empirical data?

## Hypothesis
v1/v2 formula was comparing raw sigma_top values without accounting for MP scaling.
The correct structural claim: sigma_top_shift / (K * sigma_top_partition_mean) ~ 1.0 (free-additive independence).
The empirical ratio at v1/v2 was ~0.5-0.61, suggesting K experts do NOT add up linearly in top SV.

## Design
- K sweep: {2, 4, 8}; N=4096; M_mult=[0.5, 1.0, 2.0]; 5 seeds
- Corrected formula: ratio_predicted = 1.0 (structural independence)
- GPU (overnight_queue)

## Pre-registered bands
- **HARD_PASS**: mean ratio_empirical in [0.85, 1.15] (within 15% of 1.0) across >= 80% of seeds at K in {2,4}
- **HARD_FAIL**: mean ratio_empirical < 0.70 at K in {2,4} (structural independence FAILS)
- **FORMULA_CONFIRMED**: ratio within 15% - free-additive independence holds
- **MIDDLE_BAND**: ratio in [0.70, 0.85] - partial alignment

## Calibration
v1 offset was ~0.50, v2 was ~0.61. Corrected formula predicts 1.0; test if empirical matches.
