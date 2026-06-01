# Prereg: tr_w1w2_set_intersect_v1

**Filed:** 2026-06-01
**Anchor:** tr_w1w2_set_intersect_v1
**Queue:** remote_cpu_queue
**Script:** experiments/exp_tr_w1w2_set_intersect_v1.py

## Hypothesis

The identity tr(W1 W2) = K + (M1*M2 - K)/N holds empirically at M=50, N=2048,
where K is the set-intersection cardinality of two stored pattern sets.

## Pre-registered bands

- HARD-PASS: Pearson r > 0.9999 AND MAE < 0.5 cardinality units.
- MIDDLE: 0.999 <= r <= 0.9999 OR 0.5 <= MAE <= 2.0.
- HARD-FAIL: r < 0.999 OR MAE > 2.0.

## Design

N=2048, M1=M2=50. K in {0, 5, 10, 20, 30, 40, 50}. 5 seeds, 3 trials/K.

## Formula self-tests

- K=0: tr(W1 W2) ~ M1*M2/N = 50*50/2048 ~ 1.22
- K=50 (full overlap): tr(W1 W2) ~ M1*M2 = 2500
- K=10: tr(W1 W2) ~ 10 + (2500-10)/2048 ~ 11.22

## Timeout estimate

smoke_wall_s ~ 2s, FULL same scale. timeout_s = 300 (floor).

## N-suffix note

No _nN suffix. Production N = 2048; fixed-N algebraic identity check.
