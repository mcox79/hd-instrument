# Pre-registration: kf4_drift_detect_v1
**Filed:** 2026-05-27  
**Anchor:** kf4_drift_detect_v1  
**Queue:** overnight_queue (GPU)

## Scientific Question
During sequential edits, do spectral gap and bundle-norm-var track drift amplitude?
Product relevance: early-warning drift detection before retention falls.

## Bands
- HARD_PASS: r_drift >= 0.90 in >= 2/3 seeds AND r_spectral or r_bnv >= 0.50
- HARD_FAIL: r_drift < 0.50 in all seeds (no drift accumulation)
- MIDDLE_BAND: drift tracks but spectral proxies weak

## Timeout Estimate
smoke_wall_s=0.3, conservative 2700s
