# Prereq: capacity_phase_boundary_fine_grid_v2_n4096

**Date:** 2026-06-02
**Anchor:** capacity_phase_boundary_fine_grid_v2_n4096
**Queue:** remote_cpu_queue
**Script:** experiments/exp_capacity_phase_boundary_fine_grid_v2_n4096.py

## Hypothesis

PP-50 RRAM capacity rescue R2: finer sigma_g grid to characterize transition zone.
Prior run (v1) found MIDDLE_BAND: transition zone wide (degradation starts well before sigma_g_crit).
Smoke result for v2: onset_frac ~0.365 of sigma_g_crit, universal across alpha=0.10 and 0.20 (range=0.03).
This FULL run characterizes onset_frac at all 4 alpha values at N=4096 5-seed.

SCIENTIFIC QUESTION: Is there a universal onset fraction relative to sigma_g_crit?
Smoke says yes (~0.365). FULL run tests universality across all 4 alpha at production N.

## PROT-022 Formula Self-tests

1. Phase boundary: sigma_g_crit = sqrt(1/alpha - 1)
   [alpha=0.05]: sqrt(19) = 4.359 [VERIFIED within 0.001]
   [alpha=0.10]: sqrt(9) = 3.000 [VERIFIED within 0.001]
   [alpha=0.20]: sqrt(4) = 2.000 [VERIFIED within 0.001]
   [alpha=0.50]: sqrt(1) = 1.000 [VERIFIED within 0.001]
2. Noise model: W_noisy = W * exp(sigma_g * Z) has non-zero variance. [VERIFIED in selftest]

## Pre-registered Bands

**HARD-PASS:** universal onset_frac in [0.30, 0.70] across all 4 alpha AND onset_range < 0.30
              (characterizes transition zone consistently; safe operating envelope confirmed)
**MIDDLE:** onset_frac varies by >= 0.30 across alpha (non-universal; alpha-dependent onset)
**HARD-FAIL:** fewer than 2 alpha onset_fracs defined (recall never drops below 0.90 even at sigma_g_crit)

## Smoke Result (N=512, 2 seeds, alpha=[0.10, 0.20])

Onset fracs: a0.10: 0.38, a0.20: 0.35 (mean=0.365, range=0.030)
Smoke verdict: HARD_PASS (universal onset_frac=0.365 in [0.30,0.70] range=0.03)
Strong directional signal: onset ~35-38% of sigma_g_crit, universal across 2 alpha values.

## Walk-back gate

Smoke HARD_PASS with tight range (0.03). Effect size strong (2 alpha values consistently in [0.30-0.40]). Proceeding to FULL.

## Timeout Estimate

- v1 elapsed: 96.6s at N=4096 5-seed (4 alpha * 5 sigma_g = 20 cells)
- v2: 4 alpha * 21 sigma_g_frac points = 84 cells (4.2x more cells than v1)
- v2 timeout = ceil(1.5 * 96.6 * 4.2) = ceil(609) = 900s
- Using 3600s for margin (matrix ops at N=4096 are slower; log-normal noise add cost).

## N-suffix

No _nN suffix (sigma_g sweep; N=4096 fixed in script).

## Cap_map Impact

- HARD-PASS: PP-50 operating envelope quantified: safe sigma_g = ~0.35*sigma_g_crit across all alpha; product documentation can specify this as hardware operating envelope.
- MIDDLE: non-universal onset; alpha-dependent safety margin; more nuanced operating envelope.
- HARD-FAIL: transition not characterizable at N=4096; need larger N.
