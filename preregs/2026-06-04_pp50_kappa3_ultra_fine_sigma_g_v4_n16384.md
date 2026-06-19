# Prereg: pp50_kappa3_ultra_fine_sigma_g_v4_n16384

**Date:** 2026-06-04
**Anchor:** pp50_kappa3_ultra_fine_sigma_g_v4_n16384
**PROT-018:** _n16384 suffix; production N = 16384.
**PROT-021:** seed checkpoints keyed with run_mode + N + sigma_g_grid.

## Context

PP-50 v3 HARD_FAIL (v372): sigma_sep monotonically rising sg=0.1:983.5->sg=0.9:24025.0.
Theory sigma_g_crit=0.833 marks entry boundary (onset), not exit boundary (no plateau).
v4 PURPOSE: ultra-fine bracket around sigma_g_crit=0.833 to characterize the onset SHAPE.
sigma_g = {0.83, 0.85, 0.87, 0.9, 1.0, 1.5, 2.0}.

## Pre-registered bands

Empirical anchors from v3: sigma_sep(sg=0.7)=6679.9, sigma_sep(sg=0.9)=24025.0.
No prior anchor at sg=0.83 specifically. Bands at sg=0.83: [1000, 20000] per +-50% calibration.

- HARD-PASS: sigma_sep(sg=0.83) >= 1000 AND monotone increase across bracket
             AND sigma_sep(sg=2.0) > sigma_sep(sg=0.83) * 5 (>= 5x amplification).
- MIDDLE: sigma_sep measurable at all brackets but not meeting all HP criteria.
- HARD-FAIL: sigma_sep(sg=0.83) < 100 OR sigma_sep flat between sg=0.83 and sg=0.9.

## Formula self-tests (PROT-022)

1. NLO sigma_g_crit: sqrt(ln(1 + 0.15/(3*0.05))) = 0.8326. [EXPECTED: 0.8326 within 0.001]
2. M_base = int(0.05 * 16384) = 819. [EXPECTED: 819]
3. sigma_g grid [0.83, 0.85, 0.87, 0.9, 1.0, 1.5, 2.0] strictly increasing.
4. kappa_3 at sg=0.83 non-NaN at smoke scale. sigma_sep > 0 at smoke scale.

## Multi-scale smoke

sigma_g is load-bearing; smoke at N=512 and N=2048.

## Timeout estimate

v3 elapsed ~300s (75 cells). v4 has 35 cells (7 sigma_g * 1 d * 5 seeds).
Estimate: 300 * 35/75 = 140s. ceil(1.5 * 140) = 210s -> 300s. Use PROT-019 floor: 21600.
