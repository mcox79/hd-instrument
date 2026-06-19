# Pre-registration: Item 21 capacity phase boundary at N=8192 (larger N)

**Date:** 2026-06-03
**Anchor:** `capacity_phase_boundary_larger_n_v2_n8192`
**Queue:** overnight_queue
**Trigger:** capacity_phase_boundary_under_rram_noise_v1_n4096 had MIDDLE_BAND smoke result
(small-N retrieval noise artifacts at N=512/1024). Extending to N=8192 on GPU to suppress
finite-N artifacts and get cleaner phase boundary detection.
**Priority:** PP-44/PP-50 hardware operating envelope; Wave-2 closed-form prediction test.

## Capability question

At N=8192, does substrate recall accuracy follow the Wave-2 free-probability closed-form phase
boundary: recall >= 0.90 below sigma_g_crit = sqrt(1/alpha - 1) and degrade above it?

## Scientific context

Wave-2 free-probability drill produced closed-form prediction:
  sigma_g_crit(alpha) = sqrt(1/alpha - 1)
  For alpha=0.05: sigma_g_crit = 4.36 (capacity robust to very high RRAM noise)
  For alpha=0.50: sigma_g_crit = 1.00 (capacity breaks at modest noise)

Testing at N=8192 suppresses finite-N retrieval noise artifacts that contaminated the N=4096 result.
GPU enables efficient computation with 256 MB W matrix per (seed, alpha).

## Pre-registered bands

### HARD-PASS
recall >= 0.90 for (alpha, sigma_g) with sigma_g^2 < (1/alpha - 1)
AND recall < 0.50 for sigma_g^2 > 2 * (1/alpha - 1);
phase boundary detected within +-20% across >= 2/4 alpha values (5 seeds).

### MIDDLE
Phase boundary detected but with >50% width OR detection in only 1/4 alpha values.

### HARD-FAIL
No clear phase transition detected OR substrate degrades at sigma_g < 0.5 * sigma_g_crit.

## Formula self-tests (PROT-022)

1. sigma_g_crit = sqrt(1/alpha - 1):
   [INPUT: alpha=0.05] [EXPECTED: 4.359]
   [INPUT: alpha=0.10] [EXPECTED: 3.000]
   [INPUT: alpha=0.20] [EXPECTED: 2.000]
   [INPUT: alpha=0.50] [EXPECTED: 1.000]
2. GPU memory > 0 after build.
3. >= 1 alpha value has below-boundary AND above-2x-boundary sigma_g in smoke sweep.

## Smoke result

N_ACTIVE=1024, 2 seeds, alpha=[0.10, 0.20], sigma_g=[0.5, 1.0, 2.0, 4.0]:
MIDDLE_BAND: below_violations=2/5, above_violations=0/1, alpha_transition=2/4.
Transition signal present; limited above-2x coverage at smoke N=1024 (grid coverage artifact).
Full N=8192 expected to show clean separation. Wall_s estimated 15-30s per seed.

## Timeout estimate

Smoke N=1024: ~0.5s per (alpha, sigma) cell. 2 alpha * 4 sigma = 8 cells, 2 seeds: ~8s total.
Full N=8192: (8192/1024)^2 = 64x matrix ops * (4/2) alpha * (5/5) sigma * (5/2) seeds.
timeout = ceil(1.5 * 8 * 64 * 2.0 * 1.0 * 2.5) = ceil(3840) = 3840s. Round to 4800s.

## Memory estimate

W matrix at N=8192: 8192^2 * 4 = 256 MB. Two copies (clean + noisy): 512 MB. Well within 8.6 GB.
