# Pre-reg: sparse_w_edit_heavy_v1_n4096

**Date:** 2026-05-30
**Anchor:** sparse_w_edit_heavy_v1_n4096
**Script:** experiments/exp_sparse_w_edit_heavy_v1_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** T4.1a (sparse-W under edit-heavy workload)

## Hypothesis

Sparse-W maintains retrieval AND memory savings AND KF-2 isolation under
a sustained edit storm (5000 edits over M_init=512 facts at N=4096).

## Pre-registered bands

| Outcome      | Condition                                                                   |
|--------------|-----------------------------------------------------------------------------|
| HARD_PASS    | retention >= 0.90 AND mem_savings >= 8x AND KF-2 max_iso <= 0.05 in >=3/5 seeds |
| HARD_FAIL    | retention <= 0.70 OR sparse_over_dense > 0.5 (within 2x of dense) in >=3/5 seeds |
| MIDDLE_BAND  | otherwise                                                                   |

## Calibration

Sparse-W envelope HP confirmed under static storage. Edit operations
preserve M (positions overwrite); sparse representation should not bloat.
HP at 0.90 retention is 5% tighter than steady-state HP_RET=0.95 to allow
for edit-induced drift. HF at 0.70 is decisive degradation.

## Self-test

- N == 4096 (PROT-018).
- Verdict gates HARD_PASS / HARD_FAIL on synthetic.
- Forward pass at N=1024 M_init=32 n_edits=50 returns retention,
  kf2_max_iso, mem_savings_ratio all non-null.

## Timeout estimate

smoke_wall_s ~ 0.2s. FULL: 5 seeds x 5000 edits + KF2 spot-check.
scaling_exp=1.5. Estimated ~750s.
**timeout_s = 14400**

## Production config

N=4096, M_init=512, n_edits=5000, seeds=[7,17,23,31,41].

## N-suffix binding

_n4096 -> production N = 4096 (PROT-018).
