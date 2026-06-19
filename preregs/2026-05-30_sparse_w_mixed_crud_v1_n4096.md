# Pre-reg: sparse_w_mixed_crud_v1_n4096

**Date:** 2026-05-30
**Anchor:** sparse_w_mixed_crud_v1_n4096
**Script:** experiments/exp_sparse_w_mixed_crud_v1_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** T4.1b (sparse-W under mixed CRUD workload)

## Hypothesis

Sparse-W maintains retrieval AND killer features under a sustained
10000-op mixed CRUD workload (40% store / 30% query / 20% edit / 10% delete)
starting from M_init=128 at N=4096.

## Pre-registered bands

| Outcome      | Condition                                                                   |
|--------------|-----------------------------------------------------------------------------|
| HARD_PASS    | retention >= 0.90 AND KF-2 <= 0.05 at all 4 checkpoints (every 2500 ops) in >=3/5 seeds |
| HARD_FAIL    | retention drops <= 0.70 at any checkpoint OR KF-2 > 0.10 at any checkpoint in >=3/5 seeds |
| MIDDLE_BAND  | otherwise                                                                   |

## Calibration

Sparse-W static envelope HP confirmed. Mixed-CRUD adds growth (stores)
and contraction (deletes); KF-2 spot-check at each 2500-op boundary
detects accumulating interference. HP at 0.90 retention with 0.05 KF-2 is
the integrated product target. HF at 0.70 or KF-2 > 0.10 is decisive
degradation.

## Self-test

- N == 4096 (PROT-018).
- op_mix sums to 1.0.
- Verdict gates HARD_PASS / HARD_FAIL on synthetic.
- Forward pass at N=1024 M_init=16 n_ops=200 produces checkpoints with
  retention, kf2 non-null.

## Timeout estimate

smoke_wall_s ~ 0.6s for 200 ops. FULL: 5 seeds x 10000 ops x ~0.05s/op
+ 4 checkpoints x KF2 = ~1500s. scaling_exp=1.5.
**timeout_s = 21600**

## Production config

N=4096, M_init=128, n_total_ops=10000, op_mix=(0.4, 0.3, 0.2, 0.1),
checkpoints at 2500, 5000, 7500, 10000, seeds=[7,17,23,31,41].

## N-suffix binding

_n4096 -> production N = 4096 (PROT-018).
