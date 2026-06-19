# Pre-registration: hippocampal_basin_fullscale_v2_n4096

**Date:** 2026-06-01
**Anchor:** hippocampal_basin_fullscale_v2_n4096
**Script:** experiments/exp_hippocampal_basin_fullscale_v2.py
**Queue:** overnight_queue
**N:** 4096 (_n4096 PROT-018 binding)

## Hypothesis

(A) Basin-radius scaling follows Treves-Rolls formula: empirical r_basin vs alpha
     has monotone decreasing relationship consistent with sqrt(1 - alpha/alpha_c).
     Measured by Pearson correlation between empirical and analytical values.
(B) Engram ablation: partial rank-1 removal W_abl = W - f * outer(pat0, pat0) / N
     produces linear decrease in retrieved cosine (Pearson r < -0.85).

## Pre-registered thresholds

- **HARD-PASS:** Pearson(empirical_r, analytical_r) > 0.85 AND abs(ablation_pearson) > 0.85,
  both in >= 80% of seeds
- **HARD-FAIL:** Pearson_A < 0.30 OR abs(ablation_pearson) < 0.40
- **MIDDLE-BAND:** everything else

## Smoke result (2026-06-01)

Smoke HARD_PASS: basin_pearson=0.999, ablation_pearson_abs=0.885. Wall ~50s at 2 seeds.
Expected FULL ~1200s (10 seeds, extended alpha/rho grid).

## Cap-map rows

- Hippocampal basin-radius scaling (Treves-Rolls confirmation at N=4096)
- Engram ablation / targeted deletion biophysics
