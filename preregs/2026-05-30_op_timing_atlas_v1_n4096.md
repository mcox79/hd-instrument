# Pre-reg: op_timing_atlas_v1_n4096

**Date:** 2026-05-30
**Anchor:** op_timing_atlas_v1_n4096 (S7, E2.1)
**Script:** experiments/exp_op_timing_atlas_v1_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** Substrate operation timing atlas; product
characterization input.

## Hypothesis

All 10 operations exhibit p99/median ratio < 5 (Gaussian-like
distribution; no extreme outliers). Throughput rates are documented.

## Pre-registered bands

| Outcome      | Condition                                                  |
|--------------|------------------------------------------------------------|
| HARD_PASS    | All 10 ops with p99/median <= 5                            |
| HARD_FAIL    | >=2 ops with p99/median > 50 (instability) OR any crash    |
| MIDDLE_BAND  | 8-9 ops clean, 1-2 noisy                                    |

## Operations measured

1. standard_store
2. batched_store_B16
3. standard_retrieve
4. batched_retrieve_B16
5. single_edit
6. single_delete (with cert)
7. audit_chain_verify
8. checkpoint_save (W bytes to disk)
9. checkpoint_load
10. multi_hop_pathB_d5

## Self-test

- N == 4096 (PROT-018).
- 1000 ops per cell at FULL for p99 stats; 50 at smoke (sufficient gate).
- Smoke at N=1024 M=256 produces all 10 op stats non-zero.

## Timeout estimate

5 seeds x 10 ops x 1000 samples = 50000 ops at production. Per-op median
~0.5ms = ~25s baseline. Hash + checkpoint ops are slower (~50ms each, 50
samples). ~1500s + GPU compile + disk I/O overhead.
**timeout_s = 21600** per user spec.

## Production config

N=4096, M=2048, beta=10, 1000 ops/cell, seeds=[7,17,23,31,41].
Operations 7-9 capped at 100/50 samples (their per-call cost dominates).

## N-suffix binding

_n4096 -> production N = 4096 (PROT-018).
