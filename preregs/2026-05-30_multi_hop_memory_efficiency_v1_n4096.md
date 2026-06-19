# Pre-reg: multi_hop_memory_efficiency_v1_n4096

**Date:** 2026-05-30
**Anchor:** multi_hop_memory_efficiency_v1_n4096 (S3, E1.4)
**Script:** experiments/exp_multi_hop_memory_efficiency_v1_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** Memory cliff detection at production scale.

## Hypothesis

At production config (M=8192, depth=5, K_paths=1000), no path exceeds
4x single-hop peak memory. No within-op memory spikes >2x.

## Pre-registered bands

| Outcome      | Condition                                       |
|--------------|-------------------------------------------------|
| HARD_PASS    | max amp across all 3 paths <= 4.0               |
| HARD_FAIL    | max amp >= 10.0 (memory cliff)                  |
| MIDDLE_BAND  | 4.0 < max amp < 10.0                            |

## Self-test

- N == 4096 (PROT-018).
- _peak_mem_bytes returns non-zero from tracemalloc (CPU) or
  cuda.max_memory_allocated.
- Smoke at N=1024 M=256 measures amp triples for all 3 paths.

## Timeout estimate

5 seeds x 4 mem measurements per seed = 20 ops. Per op ~5s including
malloc + dealloc. ~100s baseline + GPU compile overhead.
**timeout_s = 14400** per user spec.

## Production config

N=4096, M=8192, depth=5, K_paths=1000, seeds=[7,17,23,31,41].

## N-suffix binding

_n4096 -> production N = 4096 (PROT-018).
