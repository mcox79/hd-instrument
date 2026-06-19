# Prereg — Bet M R3 logarithmic-forgetting LONGER-T fit

**Anchor**: `wave14_betM_logforget_longt_v1`
**Queue**: remote_cpu_queue (pure CPU; single-config long-running)
**Filed**: 2026-05-24 by exp_dev

## Hypothesis

BETM_LOGFORGET_MIDDLE_BAND at v195 — 4/5 BIC fits log-form at borderline gap
2.23. v192 R3 rescue extends t-grid from {1..21} to {1..200} to resolve
log vs exponential form decisively.

## Pre-registered falsifiers (BEFORE FULL run)

- **HARD-PASS**: best-fit BIC gap >= 6 (strong evidence per Kass-Raftery)
  AND winning form consistent across >=4 of 5 seeds. -> closed-form retention
  predictor identified.
- **HARD-FAIL**: best-fit BIC gap <= 1 OR no consistent winner across seeds.
  -> Bet M form unresolved.
- **MIDDLE-BAND**: any intermediate.

## Parameters (exp_dev autonomy)

- T grid = {1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 200} FULL
- N = 4096 FULL / 512 smoke
- M per task = 200 FULL / 30 smoke
- Seeds = {7, 17, 23, 31, 41} FULL

## ETA

Remote CPU FULL ~10-30 min.

## Smoke outcome

Smoke at N=512 t in {1,5,21,89} 30 pairs: best form = C_sqrt with BIC gap
4.86. Short t-grid still inconclusive — this is the FULL's job.
