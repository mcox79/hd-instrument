# Pre-reg: latency_accuracy_tradeoff_v1_n4096

**Date:** 2026-05-30
**Anchor:** latency_accuracy_tradeoff_v1_n4096 (S8, E2.2)
**Script:** experiments/exp_latency_accuracy_tradeoff_v1_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** Tunable substrate-op Pareto frontier.

## Hypothesis

Each of 4 tunable operations (cleanup_strength, multi_hop_K_paths,
audit_probe_count, multi_hop_depth) admits a Pareto frontier with >=3
distinct Pareto-optimal settings.

## Pre-registered bands

| Outcome      | Condition                                                |
|--------------|----------------------------------------------------------|
| HARD_PASS    | All 4 ops have Pareto frontier with >=3 optimal points   |
| HARD_FAIL    | No tradeoff visible on any op (1 Pareto pt) AND <=1 op pass |
| MIDDLE_BAND  | 2-3 of 4 ops have full Pareto frontiers                  |

## Sweep parameters

- cleanup_strength: [0.0, 0.25, 0.5, 1.0, 1.5, 2.0]
- multi_hop_K_paths: [50, 100, 250, 500, 1000]
- audit_chain_probe_count: [1, 5, 10, 25, 50]
- multi_hop_depth: [3, 5, 8, 12]

## Self-test

- N == 4096 (PROT-018).
- Smoke produces (acc, lat) tuples for 2-element subsets of each sweep.

## Pareto-counting algorithm

A point (a, l) is Pareto-optimal if no other point (a', l') dominates it
(a' >= a AND l' <= l AND at least one strict).

## Timeout estimate

5 seeds x sum of sweep lengths (6+5+5+4=20 settings) = 100 setting-runs.
Per setting ~3s. ~300s baseline + GPU compile + per-setting setup
overhead. **timeout_s = 21600** per user spec.

## Production config

N=4096, M=2048, seeds=[7,17,23,31,41], 4 sweep dims above.

## N-suffix binding

_n4096 -> production N = 4096 (PROT-018).
