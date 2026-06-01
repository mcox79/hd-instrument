# Prereg: sparse_w_k2_capacity_v1

**Filed:** 2026-06-01
**Anchor:** sparse_w_k2_capacity_v1
**Queue:** remote_cpu_queue
**Script:** experiments/exp_sparse_w_k2_capacity_v1.py

## Hypothesis

Sparse-W with K=4 connections per neuron achieves higher retrieval accuracy than
dense-W at M/N=0.10 and shows a sharper capacity cliff (K^2 scaling).

## Pre-registered bands

- HARD-PASS: K=4 acc > 0.80 at M/N=0.10 AND cliff_sparse > 0.20 AND cliff_dense < 0.10 in >= 4/5 seeds.
- MIDDLE: K=4 higher than dense at M/N=0.10 but cliff not significantly sharper.
- HARD-FAIL: K=4 WORSE than dense at M/N=0.10 in >= 3/5 seeds.

Calibration probe: no prior anchor for sparse-W. Bands +-50% per policy.

## Design

N=2048, K in {1, 2, 4, 8, dense}. M/N in {0.01, 0.05, 0.10, 0.20, 0.30}.
50 queries per cell. 5 seeds.

## Timeout estimate

smoke_wall_s ~ 30s, timeout_s = 300 (floor).

## N-suffix note

No _nN suffix. Production N = 2048; K^2 capacity test at fixed N.
