# Pre-registration: wave14_betY_phase1_beta_calibration

Date: 2026-05-22
Status: Pre-registered, gated
Priority: Bet Y V2.D **Phase 1** — beta(N) = c/N empirical calibration

## Why

Per Strategy cycle 93 addendum + Lucibello-Mezard 2024 PRL 132:077301:
modern dense AM exponential capacity requires beta_net = O(1/N). Substrate's
fixed beta=32 collapses to winner-take-all at large N (beta=32 at N=65536
gives b=N*beta=2.1M, 6 orders too large).

Phase 1 calibrates the c constant in beta(N)=c/N via empirical sweep at
N in {4096, 8192, 16384}. Output c estimate feeds Phase 2 V2.D smoke at
N=65536 with beta(N=65536) = c/65536.

## Mechanism

For each N in {4096, 8192, 16384}:
  Test multiple beta values around the N-scaled prediction.
  Build random keys+values at high capacity (M = 8N).
  Modern dense AM retrieval at each beta; measure accuracy.
  beta_optimal[N] = argmax_beta(retrieval_acc).
Fit beta_optimal[N] vs 1/N: c = mean(beta_opt * N).

## Multi-probe success criteria

- beta_optimal exists (non-trivial maximum) at each N
- c estimate consistent across N (CV < 30%)
- Predicts beta_optimal at N=65536 = c/65536

## Verdict labels

- BETA_CALIBRATION_PASS (consistent c across N; CV < 30%)
- BETA_CALIBRATION_PARTIAL (CV 30-50%; usable but noisy)
- BETA_CALIBRATION_FAILED (no consistent c; >50% CV)
- BETA_CALIBRATION_INCONCLUSIVE

## Runtime: ~30-60 min
