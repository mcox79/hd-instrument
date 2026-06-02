# Pre-registration: hippocampal_place_field_extended_n8192_v1

**Date:** 2026-06-02
**Script:** experiments/exp_hippocampal_place_field_extended_n8192_v1.py
**Queue:** remote_cpu_queue
**N:** 8192 (PROT-018 _n8192 suffix)
**Seeds:** [7, 17, 23, 31, 41]
**Smoke result:** HARD_PASS (cosine=0.879, spearman=0.879, acc=1.0; wall=0.02s at N=1024)
**Timeout:** 600s (N=8192 K=409; O(N^2*K) retrieval; 5 seeds)

## Hypothesis

PP-47 hippocampal place-field extension to N=8192 for multi-N evidence and EXPLORATORY->CONFIRMED promotion.
Prior: N=4096 HARD_PASS (v333).

## Metrics

- `mean_cosine`: mean retrieval cosine across K locations
- `spearman_rho`: Spearman correlation between location distance and -pattern_cosine
- `acc_K`: fraction of patterns retrieved with cosine > 0.5

## Thresholds

HARD-PASS: cosine>=0.80 AND rho>=0.60 AND acc>=0.75 for >=4/5 seeds.
HARD-FAIL: any metric below HF (cosine<0.40, rho<0.20, acc<0.40).
MIDDLE: 2/3 conditions.
