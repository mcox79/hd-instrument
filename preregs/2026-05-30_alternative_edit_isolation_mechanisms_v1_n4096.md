# G9 Alternative Edit Isolation Mechanisms v1 at N=4096

## Anchor
alternative_edit_isolation_mechanisms_v1_n4096

## Queue
overnight_queue (GPU)

## Script
experiments/exp_alternative_edit_isolation_mechanisms_v1_n4096.py

## Scientific question
U3 COW is infeasible (10x memory + 7-8x slower). Do 3 alternative edit
isolation mechanisms achieve consistency=1.0 AND throughput >=50/sec AND
mem_amp <=4x AND audit chain intact?

## Pre-registered bands
- HARD_PASS: at least one mechanism: consistency=1.0 AND throughput >=50/sec
  AND mem_amp <=4x AND audit_chain_intact=True.
- HARD_FAIL: all 3 mechanisms infeasible (consistency < 0.5 on all).
- MIDDLE_BAND: otherwise.

## Mechanisms
- A "delta-encoding": store edits as rank-1 deltas; reconstruct W_eff at retrieval
- B "lazy-edit-application": apply per-query only overlapping edits
- C "edit-log-replay": maintain log; replay onto snapshot at query

## Config
- N = 4096 (PROT-018 _n4096)
- M = 2048
- N_QUERIES = 50, N_EDITS = 100
- depth = 5, K_paths = 100
- Seeds: [7, 17, 23, 31, 41]

## Self-test
- Per-mechanism build + verdict gates exercised
- Live CPU smoke at N=1024 M=128 q=8 e=4

## Timeout estimate
- smoke wall ~3s
- 5 seeds, 3 mechanisms, 50 q, 100 e; mechanism B is per-query O(M N^2)
- scaling_exp = 1.5; estimate = ceil(1.5 * 3 * 4 * 5) = 90s; mechanism B
  scales with M*N_use^2 per query so add margin
- timeout_s = 14400 (user spec).

## Importance
HIGH - rescue path for U3 COW infeasibility.
