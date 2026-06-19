# Pre-reg: latency_crossover_analysis_v1_n4096

**Date:** 2026-05-30
**Anchor:** latency_crossover_analysis_v1_n4096 (S2, E1.3)
**Script:** experiments/exp_latency_crossover_analysis_v1_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** Mechanism selection for LLM orchestration.

## Hypothesis

Each of B/D/E has at least one (depth, K, M) cell where it has minimum
latency at >=95% of best-cell accuracy. Distinct crossover boundaries
exist across the three dimensions.

## Pre-registered bands

| Outcome      | Condition                                                            |
|--------------|----------------------------------------------------------------------|
| HARD_PASS    | All 3 paths have at least one cell where they are min-latency winner |
| HARD_FAIL    | Only 1 mechanism wins all cells (no crossover; selection trivial)    |
| MIDDLE_BAND  | 2 of 3 paths have winning cells                                       |

## Self-test

- N == 4096 (PROT-018).
- AUC is mapped to acc-like space via (auc-0.5)*2 so cross-mechanism
  comparison is fair (B/D in [0,1]; E in [0.5,1] -> [0,1]).
- Smoke at N=1024 M=128 depth=3 K=50 produces valid lat triples.

## Timeout estimate

Sweep = 3 (M) x 6 (depth) x 5 (K) x 5 (seeds) = 450 cells. Per cell ~3s.
~1350s baseline + GPU compile overhead. **timeout_s = 21600** per user
spec.

## Production config

N=4096, M in {512, 2048, 8192}, depth in {3,5,8,12,16,20},
K_paths in {100, 500, 1000, 2000, 5000}, seeds = [7,17,23,31,41].

## N-suffix binding

_n4096 -> production N = 4096 (PROT-018).
