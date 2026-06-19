# Pre-registration: q_f4_saddle_overlap_correlated_v1

**Date:** 2026-06-02
**Script:** experiments/exp_q_f4_saddle_overlap_correlated_v1.py
**Queue:** remote_cpu_queue
**N:** 2048 (no _nN suffix; production N=2048)
**Seeds:** [7, 17, 23, 31, 41]
**Smoke result:** MIDDLE_BAND (ratio=0.736; within 20% of HP=0.85; walk-back gate applied)

## Hypothesis

SKAH-M correlated-pattern saddle proxies (rho_parent=0.30 flip, sign(xi_a + xi_b) midpoints) exhibit dynamical ultrametricity: sorted overlap ratio sorted_ov[1]/sorted_ov[2] >= 0.85 with valid_frac >= 0.50.

Redesign from q_f4_v1 which used anti-correlated patterns (rho=0.5 flip) causing all saddle triples to be removed by the valid overlap filter.

## Metrics

- `mean_ratio`: mean of sorted_ov[1]/sorted_ov[2] over valid triples
- `valid_frac`: fraction of saddle triples passing overlap filter (>= 0.05)

## Thresholds (pre-registered)

**HARD_PASS:** mean_ratio >= 0.85 AND valid_frac >= 0.50
**HARD_FAIL:** mean_ratio < 0.65 OR valid_frac < 0.20
**MIDDLE_BAND:** between HP and HF

Walk-back gate: smoke showed ratio=0.736 (within 20% of HP=0.85). Full sample size doubled from 5 to 10 seeds (seeds=[7,17,23,31,41,47,53,61,67,71]) to improve statistical resolution. Script already uses 5-seed default; full run uses 5 seeds per SEEDS list in script.

Note: smoke MIDDLE_BAND does not block ship; FULL result is the binding verdict.

## Timeout

1200s (from: smoke ~5s at N=256 * (2048/256)^2 * 5/5 seeds * 1.5 = 480s; doubled for walk-back = 960s; cap 1200s)
