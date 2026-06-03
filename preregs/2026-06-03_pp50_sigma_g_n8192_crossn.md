# Prereg: PP-50 kappa_3 sigma_g sweep cross-N second rung N=8192

**Date:** 2026-06-03
**Anchor:** pp50_kappa3_sigma_g_n8192_v1_n8192
**Queue:** overnight_queue (GPU)
**Cap map row:** PP-50 (kappa_3 noise-robustness, sigma_g envelope)

## Context

v1 sweep (sigma_g 0.01..0.30) at N=4096 5-seed: MIDDLE_BAND (v349, sigma_g_crit > 0.30 confirmed).
v2 sweep (sigma_g 0.01..1.20) at N=4096: SHIPPED v362 cycle; result pending.
This is the cross-N second rung at N=8192 to test whether sigma_g_critical is N-independent.
Cap_map annotation estimate: sigma_g_crit ~0.833 (4.6x wider than theory prediction 0.18).
W matrix at N=8192: 8192^2 * 4 = 268 MB -- well within 8 GB GPU.

## Hypothesis

kappa_3 sigma_g_critical is N-independent (algebraic structure of the Hutchinson trace identity
doesn't depend on N directly; sigma_g_crit determined by log-normal noise distribution properties).
Cross-N consistency: sigma_g_crit in [0.50, 1.00] at N=8192, matching N=4096 v2 prediction.

## Pre-registered bands

- HARD-PASS: kappa_3 identity holds within +-5% through sigma_g=0.50 AND breaks (>+-15%)
             by sigma_g=1.00 (5-seed unanimous at both bounds).
             => Cross-N consistency confirmed; sigma_g_crit in [0.50, 1.00] N-independent.
- MIDDLE: holds through 0.50 but does not clearly break by 1.00; OR sigma_g_crit shifts
          noticeably vs N=4096 (breaks before 0.30 would be regression).
- HARD-FAIL: breaks before sigma_g=0.30 (regression from N=4096 v1 finding)
             OR never breaks through sigma_g=1.20 (grid extension needed).

Calibration: prior empirical anchor is N=4096 v1 (>0.30 holds). This is cross-N rung, not
calibration probe. Bands match v2 exactly for direct comparison.

## Middle-band outcome plan

If MIDDLE: annotate PP-50 "sigma_g_crit appears N-dependent; N=8192 onset differs from N=4096."
File routing note to Strategy for interpretation. Do not close row.

## Timeout estimate

- smoke_wall_s: ~19s estimate (v2 N=4096 5-seeds 11 sigma_g values)
- N=8192 W matrix O(N^2) = 4x vs N=4096; Hutchinson probes O(N^2) per probe
- ceil(1.5 * 19 * 4.0 * 1.0) = ceil(114) = 300s
- PROT-019 floor applies: timeout_s = 14400s

## PROT-018 N-suffix binding

Anchor has `_n8192` suffix. Script has `N = 8192` at line 83. Assert `N == _N_SUFFIX = 8192`.

## PROT-021 checkpoint key

Keyed with run_mode in get_output_dir(ANCHOR_NAME). Anchor name includes n8192 (distinct from n4096 versions).

## Multi-scale smoke (PROT role contract)

sigma_g is a load-bearing axis. Script runs smoke at N_smoke=512. Multi-scale (N_smoke*4=2048) should be verified manually if suspicious. Smoke config: N_active=512, 2 seeds, 200 probes.

## Formula self-tests (PROT-022)

1. kappa3_theory = M/N check: |M/N - ALPHA| < 1/N
2. sigma_g=0 -> W_noisy == W_clean exactly
3. identity matrix kappa_3 < 0.01
4. sigma_g=0.01 at N_smoke=512: ratio in [0.85, 1.15]
5. validity filter: at least 1 of 2 low-sg values produces valid ratio (no 0-valid-cells)

## Outcome map

HARD_PASS -> PP-50 sigma_g_crit N-independent confirmed; band annotation lifts (sigma_g_crit in [0.50, 1.00]).
MIDDLE -> investigate N-dependence; N=8192 bands different from N=4096.
HARD_FAIL -> regression or extended grid needed; route to Strategy.
