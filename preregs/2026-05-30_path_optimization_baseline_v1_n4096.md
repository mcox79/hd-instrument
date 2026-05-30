# Pre-reg: path_optimization_baseline_v1_n4096

**Date:** 2026-05-30
**Anchor:** path_optimization_baseline_v1_n4096 (S5, E1.2)
**Script:** experiments/exp_path_optimization_baseline_v1_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** Clean engineering baseline for downstream optimization
work.

## Hypothesis

At fixed production config (M=2048, depth=5, K_paths=500), per-seed
timing CV <= 50% for all 3 paths. Dominant ops are nameable and
consistent.

## Pre-registered bands

| Outcome      | Condition                                          |
|--------------|----------------------------------------------------|
| HARD_PASS    | CV across seeds <= 0.50 for all 3 paths            |
| HARD_FAIL    | CV > 0.50 for ALL 3 paths (entire baseline noisy)  |
| MIDDLE_BAND  | 1-2 paths clean, others noisy                     |

## Self-test

- N == 4096 (PROT-018).
- Smoke at N=1024 M=256 depth=3 K=50 produces dom op names.
- CV is computed as sigma / mean of wall_ns.

## Engineering downstream

This anchor MEASURES only; the optimization implementations (batched
matmul, lower-precision intermediates, vectorized likelihoods) are
downstream engineering work to be informed by this baseline. Output is
the dominant_op + median timing per path.

## Timeout estimate

5 seeds at fixed config. Each seed: ~2-3s on GPU for B/D/E. Total ~15s
baseline + ~5-10x GPU compile/serialization overhead. ~150s wall.
**timeout_s = 14400** per user spec (generous buffer; underutilized).

## Production config

N=4096, M=2048, depth=5, K_paths=500, seeds=[7,17,23,31,41].

## N-suffix binding

_n4096 -> production N = 4096 (PROT-018).
