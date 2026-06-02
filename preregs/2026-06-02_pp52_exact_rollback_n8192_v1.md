# Prereg: pp52_exact_rollback_n8192_v1

**Date:** 2026-06-02
**Anchor:** pp52_exact_rollback_n8192_v1
**Queue:** overnight_queue

## Scientific question
At N=8192, does W_rollback = W' - (1/N) xi xi^T return within relative Frobenius error < 1e-6 of W_original?

## Pre-registered thresholds
- HP1: relative error < 1e-6 (fp32 precision) in >= 4/5 seeds.
- HP2: retrieval accuracy >= 0.95 after rollback in >= 4/5 seeds.
- HP3: rollback wall-time < 1.0 second in all seeds.
- HARD-PASS: all 3 HP in >= 4/5 seeds.
- HARD-FAIL: relative error > 1e-3.
- MIDDLE: relative error in [1e-6, 1e-3] OR accuracy drop 1-5pp.

## Timeout estimate
smoke_wall_s ~ 20s at N=1024 2-seed. FULL N=8192, 5 seeds: timeout_s = ceil(1.5 * 20 * 8^2 * 2.5) = ceil(4800) = **5400s**.
Flag: >2h; long run but algebraically simple so fp32 is fast.

## GPU memory
W_orig + W' + W_rollback: 3 * 268 MB = 804 MB. Safe.

## PROT-018
anchor _n8192; production N = 8192. Verified.
