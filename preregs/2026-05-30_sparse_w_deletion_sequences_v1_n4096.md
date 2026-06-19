# Pre-reg: sparse_w_deletion_sequences_v1_n4096

**Date:** 2026-05-30
**Anchor:** sparse_w_deletion_sequences_v1_n4096
**Script:** experiments/exp_sparse_w_deletion_sequences_v1_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** T4.1c (sparse-W + deletion certificate chain)

## Hypothesis

Sparse-W maintains correct retrieval semantics, generates valid deletion
certificates, and preserves an auditable cert chain over a 500-delete
sequence (50% deletion rate from M_init=1000 facts at N=4096).

## Pre-registered bands

| Outcome      | Condition                                                                |
|--------------|--------------------------------------------------------------------------|
| HARD_PASS    | 100% cert generation AND audit chain valid AND deleted_gone_rate >= 0.95 AND surviving_present_rate >= 0.95 AND KF-2 <= 0.05 in >=3/5 seeds |
| HARD_FAIL    | cert_rate < 1.0 OR audit chain corrupts OR deleted_gone_rate < 0.80 OR surviving_present_rate < 0.80 in >=3/5 seeds |
| MIDDLE_BAND  | otherwise                                                                |

## Calibration

Deletion certificate chain is a killer feature 3 capability. Cert chain
is SHA-256 hash chain over (key_id, val_id, op_id) -- structurally
correct cert generation means 100% rate. Retrieval semantics (deleted
gone, surviving preserved) at >=95% allows for spillover noise from
crowded rank-1 retractions at high deletion rates.

## Self-test

- N == 4096 (PROT-018).
- Verdict gates HARD_PASS / HARD_FAIL.
- Forward pass at N=1024 M_init=32 n_deletes=16 confirms cert_rate=1.0
  audit_valid=True deleted_gone_rate >= 0.5 surviving_present_rate >= 0.5.

## Timeout estimate

smoke_wall_s ~ 0.1s. FULL: 5 seeds x (M_init=1000 store + 500 deletes
+ retrieval checks + KF2) = ~250s. scaling_exp=1.5.
**timeout_s = 14400**

## Production config

N=4096, M_init=1000, n_deletes=500, seeds=[7,17,23,31,41].

## N-suffix binding

_n4096 -> production N = 4096 (PROT-018).
