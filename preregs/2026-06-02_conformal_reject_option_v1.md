# Pre-registration: conformal_reject_option_v1

**Date:** 2026-06-02
**Anchor:** conformal_reject_option_v1
**Script:** experiments/exp_conformal_reject_option_v1.py
**Queue:** remote_cpu_queue
**Timeout:** 1800s

## Scientific question (Q24)

Does split conformal prediction provide the promised distribution-free coverage
guarantee (1-alpha) for the Hopfield refusal threshold?

Coverage = P(score >= tau_cp) >= 1 - alpha for test queries.

## Key correction
Original script used upper-quantile threshold (90th percentile) giving coverage=8%.
Fixed to use alpha-th quantile (LOW end) = floor((n+1)*alpha) which gives the
minimum threshold below which only alpha fraction of calibration queries fall.

## Bands (pre-registered)

**HARD-PASS (HP):**
- frac_pass >= 0.80 (80% of alpha/seed combos achieve correct coverage)
- tau_ok = tau_cp in [0.01, 0.99] (non-trivial threshold)
- mean_gap = empirical_coverage - (1-alpha) in [-0.05, +0.20]

**MIDDLE:**
- frac_pass in [0.40, 0.80)

**HARD-FAIL (HF):**
- frac_pass < 0.40 (coverage guarantee systematically violated)

## Smoke result
HARD_PASS: min_frac_pass=1.00 (HP>=0.80), mean_gap=+0.008.
alpha=[0.05,0.10,0.20] all pass. Wall time: <5s. FULL estimate: ~400s (5 seeds).

## PROT-018
No _nN suffix. Production N=4096 declared in script.
