# Prereg: pp58_bbp_discrete_fallback_v1_n16384

**Date:** 2026-06-03
**Anchor:** pp58_bbp_discrete_fallback_v1_n16384
**Script:** experiments/exp_pp58_bbp_discrete_fallback_v1_n16384.py
**Queue:** remote_cpu_queue (CPU)
**Cap_map row:** PP-58 BBP spectral-gap audit criterion

## Hypothesis

BBP discrete-pattern fallback: adding k_noise random +-1 patterns to W (discrete noise)
produces the same audit_crit/cap_crit/ratio as adding Gaussian noise at sigma_g by MP universality.
sigma_g_equiv = sqrt(k_noise / N). ratio_discrete ~= ratio_continuous ~= 4.13 at alpha=0.05.

## Prior results

pp58_bbp_spectral_gap_calibration_v1_n16384: completed (continuous Gaussian sigma_g sweep).
This is the discrete-universality companion test.

## Pre-registered bands

Calibration probe with no prior empirical anchor for discrete eigenspectrum; bands +-50% per policy.
Theoretical BBP prediction: ratio_discrete ~= 4.13 at alpha=0.05.

- **HARD-PASS:** ratio in [2.0, 6.0] (+-50% of 4.13) AND audit_crit_k < cap_crit_k
               (ordering preserved) AND at least one k_noise value shows measurable merging.
               Strategic: founds discrete-universality sub-property of PP-58 row.
- **MIDDLE:** ratio in [1.5, 2.0) or (6.0, 7.0] (borderline range).
- **HARD-FAIL:** ratio < 1.0 OR > 8.0 OR no merging detected at any k_noise (audit_crit=None).

## Configuration

- N = 16384 (production; _n16384 suffix binding)
- alpha = 0.05, M_sig = 819 signal patterns
- k_noise sweep: [0, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1200, 1500, 2000]
- SEEDS = [7, 17, 23, 31, 41] (5 seeds)

## PROT-018

Anchor _n16384; script N=16384. Verified from docstring: `N = 16384`.

## PROT-021

run_mode=full, n_seeds=5. Seed checkpoints keyed with run_mode.

## Formula self-tests (PROT-022)

1. BBP sigma_g_audit_crit formula: 1 - sqrt(0.05) - 0.05 = 0.7264 at alpha=0.05.
   [INPUT: alpha=0.05] [EXPECTED: 0.7264 within 0.001]
2. k_noise_audit_crit_expected = (0.7264)^2 * 16384. [EXPECTED: ~8627]
3. sigma_g_equiv at k_noise=819: sqrt(819/16384) = sqrt(0.05) = 0.2236.
   [INPUT: k_noise=819, N=16384] [EXPECTED: 0.2236 within 0.001]
4. M at alpha=0.05, N=16384: int(0.05 * 16384) = 819. [EXPECTED: M=819]

## Timeout estimate

Smoke 5 k_noise * 2 seeds ~ 10 eigendecomp calls * 2s = 20s.
FULL 15 k_noise * 5 seeds = 75 calls * 2s = 150s + overhead.
ceil(1.5 * 20 * (15/5) * (5/2)) = ceil(225) = 300s.
With 3x walk-back margin (first discrete BBP test): timeout=900s.

**timeout_s = 900**

## OOM check

W on CPU: 16384^2 * 4 / 1e9 = 1.07 GB. Fine (remote 16+ GB RAM).
Xi_sig: 819 * 16384 * 4 / 1e6 = 53.7 MB. Xi_noise: 2000 * 16384 * 4 / 1e6 = 131 MB. Fine.

## Dependency check

No upstream data dependencies. Script is self-contained (pure numpy).

## Ship rationale

RESUME: script existed but queue_add failed mid-cycle due to API ConnectionRefused.
Tests BBP universality for discrete substrate patterns; confirms audit criterion applies to
substrate's actual discrete +-1 operating mode.
