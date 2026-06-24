# Pre-registration: substrate_cfrpe_n_steps_curve_v1

**Date:** 2026-06-23
**Anchor:** substrate_cfrpe_n_steps_curve_v1
**Motivation:** Skunkworks VET (skunkworks_to_all_BATCH_VET_4_recent_negatives_2026-06-23.md) recommends determining the cf-RPE asymptote. Meta-LR cell (N_STEPS=2000) achieved BPC=7.0642 vs heterogeneous_plasticity (N_STEPS=1000) BPC=7.1052 -- learning is still improving at 2000 steps. Need convergence curve to find asymptote and potentially update chain-grade anchor.

## Design

- cf-RPE delta rule: exact rule from heterogeneous_plasticity fair_harness
  `delta_W = (E[t+1] - E[t] @ W^T)^T @ E[t] / batch`
- ARM_HEBBIAN_BASELINE: one-pass batched Hebbian (fair_harness ref BPC=7.3065)
- N_STEPS sweep: {500, 1000, 1500, 2000, 3000, 5000} x 3 seeds x text8
- N_DIM=8192, N_TRAIN=100k, CFRPE_LR=0.5, INGEST_BATCH=64, SPARSE_BIPOLAR_F=0.05
- LAMBDA_GRID: [0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0] -- C7 META: NO 0.0

## Pre-registered Threshold Bands

| Band | Condition | Verdict |
|------|-----------|---------|
| HARD_PASS_NEW_ANCHOR | lift at N_STEPS=max >= +0.25 bits over Hebbian baseline | HARD_PASS |
| CHAIN_GRADE_BONUS | lift at N_STEPS=max >= +0.30 bits | CHAIN_GRADE_BONUS |
| ASYMPTOTE_CONVERGED | delta(lift, last 2 steps) < 0.02 bits | ASYMPTOTE_CONVERGED |
| ASYMPTOTE_OPEN | delta(lift, last 2 steps) >= 0.03 bits | ASYMPTOTE_OPEN (need bigger sweep) |
| HARD_FAIL | lift at max steps < +0.05 OR no monotonic increase across N_STEPS | HARD_FAIL |
| MIDDLE_BAND | lift in [0.05, 0.25) | MIDDLE_BAND (inconclusive) |

Calibration basis: heterogeneous_plasticity N_STEPS=1000 -> lift=+0.201 bits; meta_lr N_STEPS=2000 -> lift=+0.241 bits. Extrapolating, +0.25 at N_STEPS=5000 is reachable (conservative calibration probe bands at +-50% of theoretical).

## Smoke Results (2026-06-23)

- N_DIM=512, N_STEPS_GRID=[50,100,200], seed=[0], device=cpu
- ARM_HEBBIAN_BASELINE: BPC=5.2043
- N50_cfrpe: BPC=5.0158 (lift=0.1885)
- N100_cfrpe: BPC=4.8675 (lift=0.3368)
- N200_cfrpe: BPC=4.7932 (lift=0.4111)
- ASYMPTOTE_OPEN: lift@200 - lift@100 = 0.0743 >= 0.03 (consistent with still-converging at full N_STEPS)
- All 9 instrumentation self-tests PASS
- SUSPICIOUS_RESULT_GATE: PASS (non-zero metrics, monotonic improvement, >100ms)

## Routing Decision

Routing to overnight_queue (NOT remote_cpu_queue as originally spec'd).
Reason: numpy at N_DIM=8192 measured 1.798s/step on remote CPU (i5-12400F). Full run = ~39000 steps = 19+ hours (infeasible). Fix #22 rule: N_DIM >= 8192 -> overnight_queue. Rewritten to torch for GPU utilization.

## C7 META Compliance

LAMBDA_GRID excludes 0.0. Post-hoc LAMBDA_ZERO_COLLAPSE flag detects if grid minimum selected as best (diagnostic, not FAIL).
