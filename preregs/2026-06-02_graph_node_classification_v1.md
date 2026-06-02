# Pre-registration: graph_node_classification_v1

**Date:** 2026-06-02
**Anchor:** graph_node_classification_v1
**Queue:** remote_cpu_queue

## Hypothesis
Substrate W_c prototype classifier (BSC channel model) achieves >= 80% accuracy
at rho_within=0.70 (cell A) and >= 60% at rho_within=0.60 (cell B) for 4-class
node classification at N=1024.

## Pre-registered thresholds
- HARD-PASS: acc_A >= 0.80 AND acc_B >= 0.60.
- MIDDLE: acc_A >= 0.65 AND acc_B >= 0.50.
- HARD-FAIL: acc_A < 0.65.

Calibration probe with BSC channel model; prototypes are random BSC +-1 vectors.

## Smoke result
N=1024, C=4, n_train=50/class, n_test=12/class, 2 seeds:
- cell_A acc=1.000 (rho=0.70, p_flip=0.15, HARD_PASS)
- cell_B acc=1.000 (rho=0.60, p_flip=0.20, HARD_PASS)
- Smoke wall: 0.5s

## Note
BSC channel with rho=0.60-0.70 at N=1024 with n_train=50/class gives very strong signal.
FULL may also show near-perfect accuracy. If so, the result confirms the mechanism soundly.

## Timeout estimate
Smoke wall: 0.5s / 2 seeds = 0.25s/seed.
Full: 5 seeds, n_train=125/class. wall = 1.5 * 0.25 * 5 * (125/50) = 4.7s. timeout=60s.
