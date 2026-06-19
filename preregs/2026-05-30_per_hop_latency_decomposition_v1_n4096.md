# Pre-reg: per_hop_latency_decomposition_v1_n4096

**Date:** 2026-05-30
**Anchor:** per_hop_latency_decomposition_v1_n4096 (S1, E1.1)
**Script:** experiments/exp_per_hop_latency_decomposition_v1_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** Multi-hop op-timing breakdown for production scale.

## Hypothesis

Each multi-hop path mechanism (B/D/E) has a dominant bottleneck operation
that accounts for >50% of wall-time, AND that bottleneck is consistent
across the parameter sweep (M, depth, K_paths).

## Pre-registered bands

| Outcome      | Condition                                                                       |
|--------------|---------------------------------------------------------------------------------|
| HARD_PASS    | Each of B/D/E has a dominant op >=50% AND the modal op covers >=50% of cells    |
| HARD_FAIL    | No path has a stable dominant op (modal op < 50% of cells for all 3 paths)      |
| MIDDLE_BAND  | Some paths consistent, others not                                                |

## Self-test

- N == 4096 (PROT-018).
- TimingTrace.record dispatches multiple op-names per path.
- Smoke at N=1024, M=64, depth=3, K=20 produces non-zero dom_*_frac.

## Timeout estimate

Sweep = 4 (M) x 4 (depth) x 3 (K) x 5 (seeds) = 240 cells. Per-cell wall
roughly 200ms (B) + 1s (D) + 2s (E) at smoke -> ~3s. FULL 8x scaling:
240 cells x ~24s = ~5760s. **timeout_s = 21600** (per user spec; floor
applied to allow GPU compile + serialization overhead).

## Production config

N=4096, M in {512, 2048, 4096, 8192}, depth in {3, 5, 8, 12},
K_paths in {100, 500, 1000}, seeds = [7,17,23,31,41].

## N-suffix binding

_n4096 -> production N = 4096 (PROT-018).
