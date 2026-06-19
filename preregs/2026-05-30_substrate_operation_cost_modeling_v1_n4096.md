# C6 Substrate Operation Cost Modeling v1 at N=4096

## Anchor
substrate_operation_cost_modeling_v1_n4096

## Queue
remote_cpu_queue

## Script
experiments/exp_substrate_operation_cost_modeling_v1_n4096.py

## Scientific question
Build cost model for substrate operations at production scale. Required for
customer capacity planning. Do per-operation cost models fit power-law with
R^2 >= 0.90 AND model predictions match empirical within 20%?

## Pre-registered bands
- HARD_PASS: power-law fits with R^2 >= 0.90 for all 5 operations AND model
  predictions match empirical within 20% (median across seeds).
- HARD_FAIL: model fits R^2 < 0.50 (no clean scaling) OR predictions miss
  by > 50%.
- MIDDLE_BAND: otherwise.

## Operations
[store, retrieve, edit, delete, multi_hop]

## Config
- N = 4096 (PROT-018 _n4096)
- M sweep [128, 512, 2048, 8192]
- N_OPS_PER_MEASURE = 20 repeated ops per (M, op) cell
- depth = 5, K_paths = 100, N_STARTS = 16
- Seeds: [7, 17, 23, 31, 41]

## Power-law fit
Model: latency_s = a * M^b (log-log linear regression). Reports a, b, R^2,
max_pred_err.

## Output
notes/substrate_cost_model_v1_2026-05-30.md - power-law params per op +
deployment capacity recommendations.

## Self-test
- Verdict gates HP/HF/MB exercised
- Power-law fit self-check on (x, 2x) sequence -> b=1.0, R^2=1.0
- Live CPU smoke at N=1024 M_sweep=[64, 128]

## Timeout estimate
- smoke wall ~5s
- 5 seeds * 5 ops * 4 M-points * 20 repeats; multi_hop is heavy (~30s/measurement)
- scaling_exp = 1.5; estimate = ceil(1.5 * 5 * 4 * 5 * 20 / 5) ~ 600s + multi_hop tail
- timeout_s = 14400 (user spec).

## Importance
HIGH - production capacity planning; required for customer deployment SLAs.
