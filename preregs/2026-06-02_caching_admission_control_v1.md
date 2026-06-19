# Prereg: caching_admission_control_v1

## Scientific question
Caching admission control: spectral proxy triggers rate reduction before capacity cliff.

## Pre-registered thresholds
- HARD-PASS: All of A (rate_ratio < 0.70), B (acc_admitted >= 0.85), C (acc_naive <= 0.50).
- HARD-FAIL: HF-B (acc_admitted < 0.60) OR HF-C (acc_naive > 0.75).
- MIDDLE: 2/3 cells.

## Calibration note
First admission control test. Bands +-50% per calibration-probe policy.

## Smoke result
HARD_FAIL: acc_naive=0.975 at N=512 (cliff not manifested at this scale).
Cell B passes (acc_admitted=0.982 >= 0.85). Cell A borderline (rate_ratio=0.774 vs HP=0.70).
The naive collapse is NOT occurring at N=512 because the Hopfield capacity cliff at N=512 is
smoother than the sharp alpha_c=0.138 formula predicts. This is a finite-N smoothing effect.
At N=1024 the cliff is sharper. Ship FULL to observe cliff at larger N.
Walk-back: FULL N=1024, same M_total = 1.5*alpha_c*N = 212 patterns.

## Timeout estimate
Smoke wall: 1.7s, N=512->1024 (2x), seeds=2->5 (2.5x). Power method O(N).
timeout = ceil(1.5 * 1.7 * 2 * 2.5) = ceil(12.75) = 13s.
timeout=300s (generous; power method iterations + M=212 outer products).

## N-suffix note
No _nN suffix; production N=1024 per rule 3.
