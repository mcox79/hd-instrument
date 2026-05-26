# Prereg: wave14_betM_logforget_fitform_v1

**Filed**: 2026-05-24 exp_dev
**Anchor**: Bet M log-forgetting fit-form selection HARNESS (methodology validation)
**Source**: hand-off v193 optional anchor 6 (Wickelgren 1972 / Wixted-Ebbesen 1991)

## Per [[feedback-rehabilitation-after-rejection]] / [[feedback-ship-before-dependency-verified]]

Bet M Allen-Cahn t^(1/2) REJECTED v193 (slope=0.069 outside [0.3,0.7]). Bet M reframes via Wickelgren/Wixted log-forgetting family. The hand-off proposed running a fit on existing Bet B data, but local-disk data is smoke-only (2 t-points, insufficient for fit). PIVOT: ship the methodology HARNESS as a self-contained analyzer. Once validated, re-point at real data when remote Bet B t-sweep ships.

## Hypothesis

Among 5 candidate retention-decay forms (power-law, log, sqrt, exponential, saturating-log), BIC-based model selection on synthetic data correctly identifies the generating form on >=4 of 5 cases with substantial Kass-Raftery evidence (BIC gap >= 4).

## Design

- 5 candidate forms: A_powerlaw, B_log, C_sqrt, D_exp, E_satlog
- t_grid = [1, 2, 3, 5, 8, 13, 21, 34, 55] (Fibonacci-spaced, 9 points)
- 30 synthetic replicates per generating form
- Noise: Gaussian, std=0.02
- Grid-search nonlinear fit (no scipy dependency); BIC for model comparison
- 5 seeds: [7, 17, 23, 31, 41]

## Falsifier bands (pre-registered)

- **HARD-PASS — harness validated; ready for real-data apply**: >=4 of 5 forms correctly identified (mean correct_rate across seeds) AND median BIC gap to runner-up >= 4.
- **HARD-FAIL — harness REJECTED; redesign needed**: <=2 of 5 forms correct OR median BIC gap < 2.
- **MIDDLE**: any intermediate; report bands.

## Smoke result (5 replicates, 5-point t_grid, 1 seed)

`BETM_LOGFORGET_HARD_FAIL_HARNESS_REJECTED` at smoke (3/5 correct, median BIC gap 1.92). Under-resolved smoke (only 5 replicates and 5 t-points). FULL at 30 replicates × 9 t-points × 5 seeds is the actual test.

## Self-test

`verdict self-test passed (4/4 cases)`.

## Queue

`queue=local_cpu_queue name=wave14_betM_logforget_fitform_v1 script=experiments/exp_wave14_betM_logforget_fitform_v1.py prereg=preregs/2026-05-24_wave14_betM_logforget_fitform_v1.md timeout=600`
