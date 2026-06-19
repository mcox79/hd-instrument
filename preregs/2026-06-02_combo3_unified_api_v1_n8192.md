# Pre-registration: combo3_unified_api_v1_n8192

Date: 2026-06-02
Anchor: combo3_unified_api_v1_n8192
Queue: overnight_queue
Seeds: [7, 17, 23, 31, 41]
N: 8192

## Hypothesis
5-method unified audit API (kappa_3 update, CNDC composition, cert signature, Krylov
buffer primitives) at N=8192. Tests N-scaling curve fill between n4096 and n32768.
All 5 methods should maintain zero error at production scale.

## Pre-registered Thresholds
HARD-PASS: n_fails=0 AND all 5 method errors = 0.0 AND matvec >= 1 (>=60% seeds).
HARD-FAIL: n_fails >= 3 (majority of methods broken).
MIDDLE: 1-2 failures.

## Calibration Source
n4096 HARD_PASS (all 5 methods, 0 errors). N=8192 is exact 2x scale; algebraic
methods should be N-invariant.

## Smoke Result
HARD_PASS: n_fails=0, all errors=0.0, matvec=2 (N=8192, 2 seeds).
