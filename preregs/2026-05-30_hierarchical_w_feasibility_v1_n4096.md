# Prereg: hierarchical_w_feasibility_v1_n4096

Date: 2026-05-30
Anchor: hierarchical_w_feasibility_v1_n4096
Script: experiments/exp_hierarchical_w_feasibility_v1_n4096.py
N-suffix: _n4096 -> production N = 4096 (PROT-018)

## Question

2-level hierarchical substrate: 16 summary atoms (W1: summary_key -> summary_id),
each summary has 16 leaf atoms (W2[s]: leaf_key -> leaf_value).
Query: argmax(W1 @ k) selects summary; then argmax(W2[s] @ k) selects leaf.

Does hierarchical addressing maintain >= 90% accuracy at >= 5x effective
capacity vs flat substrate (heuristic flat_capacity = N/4 = 1024)?

## Pre-registered bands

- **HARD_PASS**: hierarchical_acc >= 0.90 AND capacity_ratio >= 5.0.
- **HARD_FAIL**: hierarchical_acc <= 0.60 (>= 30% degradation vs full=1.0).
- **MIDDLE_BAND**: otherwise.

## Effective capacity definition

`effective_capacity = n_summaries * n_leaves_per_summary = 16 * 16 = 256`.
`flat_capacity_heuristic = N / 4 = 1024`. capacity_ratio = 256/1024 = 0.25.
Note: at production sizes (16*16=256) capacity_ratio is bounded BELOW 1.0; HP
requires capacity_ratio >= 5.0 which would need bigger n_sum / n_lps. Per spec
this is intentional — the test characterizes whether hierarchy holds up at
ratios where it OUGHT to confer capacity advantage. At 16*16 we'll measure
acc and report capacity_ratio as-observed; the HARD_PASS may be unreachable
at this n_sum/n_lps config (expected outcome: MIDDLE_BAND with acc info).

## Sweep

N=4096; 16 summaries * 16 leaves = 256 leaves total; 5 seeds.

## Timeout estimate

User specified 21600s. scaling_exp=1.5.
