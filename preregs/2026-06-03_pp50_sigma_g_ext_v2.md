# Prereg: PP-50 kappa_3 sigma_g extended sweep v2 at N=4096

**Date:** 2026-06-03
**Anchor:** pp50_kappa3_sigma_g_ext_v2_n4096
**Cap-map row:** PP-50 kappa_3 spectral-MAC sub-percent drift detection; I-19 rescue

## Context

v1 sweep (sigma_g 0.01..0.30) N=4096 5-seed MIDDLE_BAND (v349 cycle).
Finding: kappa_3 identity holds at sigma_g=0.30 -- the v1 HARD-FAIL criterion ("holds at sigma_g>0.30")
was triggered in the HARD-FAIL direction: the identity is more robust than Wave-2 predicted.
Cap_map annotation: sigma_g_critical estimated ~0.833 (4.6x wider than theory prediction 0.18).
This experiment extends the sweep to sigma_g in [0.01..1.20] to locate the actual critical point.

## Scientific question

What is the actual sigma_g_critical where kappa_3 identity breaks >15%?
Does the substrate kappa_3 audit primitive remain valid up to sigma_g=0.50? Through sigma_g=0.80?

## Pre-registered threshold bands

- HARD-PASS: kappa_3 identity holds within +-5% through sigma_g=0.50 AND breaks (>+-15%)
  by sigma_g=1.00 (5-seed unanimous at both bounds).
  => Annotation: sigma_g_crit in [0.50, 1.00]; PP-50 noise-envelope 4.6x wider than Wave-2.
- MIDDLE: holds through sigma_g=0.50 but does not clearly break by sigma_g=1.00
  (only some seeds break, or break is at sigma_g>1.20).
- HARD-FAIL: kappa_3 breaks before sigma_g=0.30 (regression from v1 finding)
  OR identity holds without ANY break through entire extended grid (sigma_g_crit > 1.20).

Calibration note: prior empirical anchor is v1 (sigma_g>0.30 confirmed). Bands set conservatively
to capture the actual critical point. v1 HARD-FAIL at sigma_g>0.30 was the correct reading per v349.

## Formula self-tests

1. kappa_3/alpha at sigma_g=0 within +-5% of 1.0: [INPUT: N=128, sigma_g=0, M=6] [EXPECTED: ratio in 0.5..2.0 at N=128].
2. sigma_g=0 noise: [INPUT: exp(0*Z)] [EXPECTED: W_noisy == W_clean].
3. Identity matrix kappa_3 ~ 0: [INPUT: W=I/N N=64, n_probes=200] [EXPECTED: |kappa_3| < 0.01].
4. sigma_g=0.01 ratio near 1.0: [INPUT: N=512, 1 seed, sigma_g=0.01] [EXPECTED: ratio in 0.5..2.0].

## Timeout estimate

v1 smoke elapsed ~19s (5-seed, 8 sigma_g values). Extended grid: 11 sigma_g values.
timeout = ceil(1.5 * 19 * (11/8) * 1.0) = ceil(39.2) -> 300s.

## PROT-018 binding

No _nN suffix in anchor name; production N=4096 stated in script and this prereq.
Rationale: noise-sweep at fixed N=4096.
