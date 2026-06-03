# Pre-registration: hebbian_vs_gd_identity_v1_n1024

**Date:** 2026-06-02
**Anchor:** `hebbian_vs_gd_identity_v1_n1024`
**Queue:** remote_cpu_queue
**Script:** `experiments/exp_hebbian_vs_gd_identity_v1_n1024.py`
**Source:** v343 routing, Item 2 (Cluster A1); P_deflated=0.70+

## Hypothesis

One-shot Hebbian write W = Xi^T Xi / N achieves the same encoding fidelity as
gradient descent (MSE + Adam) for (key, value) memorization at N=1024, M=100
(alpha=0.098 << alpha_c=0.138), at orders-of-magnitude lower compute.

Algebraic basis: Hebbian write is the MSE-optimal one-step solution when alpha << alpha_c
(Hopfield 1982; Bishop 2006 ch.5). GD on MSE converges to the same fixed point W*.

## Pre-registered bands

**HARD-PASS** (all 3 required, 5-seed unanimous):
- HP1: Hebbian retrieval accuracy within +-2pp of GD accuracy
- HP2: wall-time speedup >= 100x
- HP3: FLOPs speedup >= 1000x

**MIDDLE**: accuracy within +-5pp OR speedup 10-100x

**HARD-FAIL**: Hebbian acc < 90% of GD accuracy OR speedup < 10x

## Formula self-tests (PROT-022)

1. Hebbian at alpha=0.098 N=256 M=25: acc > 0.85
   [Verified at module scope in _instrumentation_selftest()]
2. MSE loss at W*: mean_residual^2 < 0.20 for N=64, M=6
3. GD converges to Hebbian W: ||W_gd - W_hebb||/N^2 < 0.10 at N=64, M=6

## N-suffix

PROT-018 binding: anchor `_n1024`; script MUST have N=1024 in full config. Verified: `N = 1024`.

## Timeout estimate

Smoke: N=256, M=25, 2 seeds, GD_MAX_ITER=5000. Estimated smoke_wall ~30s.
Full: N=1024, M=100, 5 seeds, GD_MAX_ITER=20000. GD per seed ~60s (Adam 20k iters at N=1024).
timeout_s = ceil(1.5 * 30 * (1024/256)^1.0 * (5/2)) = ceil(1.5 * 30 * 4 * 2.5) = ceil(450) -> **600s**

Note: GD dominates wall time; scaling is ~linear in N^2 * iters. Using 600s with headroom.

## PROT-018 pre-ship audit

```
grep -E "(N\s*=|n\s*=)\s*1024" experiments/exp_hebbian_vs_gd_identity_v1_n1024.py
```
Expected match: `N = 1024`
