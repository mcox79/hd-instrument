# Pre-registration: kappa3_noise_robustness_sigma_g_sweep_v1_n4096

**Date:** 2026-06-02
**Anchor:** `kappa3_noise_robustness_sigma_g_sweep_v1_n4096`
**Queue:** overnight_queue (GPU)
**Script:** `experiments/exp_kappa3_noise_robustness_sigma_g_sweep_v1_n4096.py`
**Source:** v343 routing, Item 20 (Wave-2 free-probability prediction test); P_deflated=0.65

## Hypothesis

The substrate's kappa_3 = alpha free-Poisson identity survives multiplicative log-normal
weight noise sigma_g, with empirical breakdown matching Wave-2 closed-form prediction:
sigma_g_critical ~ 0.18.

Wave-2 free-probability drill derived: capacity collapses at sigma_g^2 = 1/alpha - 1;
kappa_3 = alpha identity breaks at sigma_g > 0.18 (kappa_3 audit-primitive is more
noise-sensitive than raw capacity).

## Pre-registered bands

**HARD-PASS** (5-seed unanimous across both bounds):
- kappa_3/alpha within +-5% for sigma_g <= 0.15
- kappa_3/alpha breaks (>+-15% deviation) by sigma_g = 0.25

**MIDDLE**: identity envelope sigma_g_critical in [0.10, 0.25] (within order-of-magnitude)

**HARD-FAIL**:
- Identity breaks at sigma_g < 0.05 (more fragile than predicted)
- OR holds at sigma_g > 0.30 (more robust than predicted)
- Wave-2 free-probability prediction wrong by >2 orders

No prior empirical anchor at this noise regime. Bands set per calibration-probe policy
(theoretical prediction +-50% per role contract).

## Formula self-tests (PROT-022)

1. kappa_3_theory(M=204, N=4096) = M/N = 0.0498 ~ alpha=0.05. At sigma_g=0, ratio ~ 1.0 (+-5%).
2. W_noisy at sigma_g=0 equals W_clean exactly.
3. Hutchinson on W = I/N at N=128: kappa_3 ~ 1/N^2 (< 0.01).
   [All verified at module scope in _instrumentation_selftest()]

## N-suffix

PROT-018 binding: anchor `_n4096`; script MUST have N=4096 in full config. Verified: `N = 4096`.

## Timeout estimate

Smoke: N=4096, n_probes=200, 2 seeds, 8 sigma_g values.
Full: N=4096, n_probes=2000, 5 seeds, 8 sigma_g values.
Smoke wall estimate: ~10-15s (GPU, batched matmul).
timeout_s = ceil(1.5 * 15 * (2000/200)^1.0 * (5/2)) = ceil(1.5 * 15 * 10 * 2.5) = ceil(562) -> **600s**

## PROT-018 pre-ship audit

```
grep -E "(N\s*=|n\s*=)\s*4096" experiments/exp_kappa3_noise_robustness_sigma_g_sweep_v1_n4096.py
```
Expected match: `N = 4096`
