# Pre-registration: subgraph_cardinality_trace_v1

**Date:** 2026-06-01
**Anchor:** subgraph_cardinality_trace_v1
**Script:** experiments/exp_subgraph_cardinality_trace_v1.py
**Queue:** remote_cpu_queue
**N:** 4096, N_NODES=50, N_EDGES=200

## Hypothesis

Matrix power trace T(v,r,k) = xi_v^T W_r^k xi_v correlates with subgraph counts.
k=2: correlates with 2-path (length-2 walk) counts from each node.
k=3: correlates with triangle counts.
Pearson correlation between T(v) values and exact subgraph counts.

## Pre-registered thresholds (calibration probe, first empirical anchor)

±50% of theoretical prediction 0.70:
- **HARD-PASS:** mean Pearson r > 0.65 for both k=2 and k=3
- **HARD-FAIL:** mean Pearson r < 0.20 for either k=2 or k=3
- **MIDDLE-BAND:** Pearson in [0.20, 0.65] for either

## Smoke result (2026-06-01)

Smoke HARD_PASS: k=2 r=0.996, k=3 r=0.994 >> HP=0.65. Wall ~8.6s.

## Cap-map rows

- Graph introspection: trace-based subgraph cardinality estimation
- Knowledge graph analytics capability
