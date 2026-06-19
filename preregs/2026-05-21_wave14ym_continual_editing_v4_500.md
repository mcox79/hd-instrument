# Pre-registration: wave14ym_continual_editing_v4_500

Date: 2026-05-21
Status: Pre-registered, gated
Experiment: [exp_wave14ym_continual_editing_v4_500.py](../experiments/exp_wave14ym_continual_editing_v4_500.py)
Priority source: extreme stress test extending yc/yf/yj
Author: experiment_dev session, pipeline tick 22

## Why

yc (30 edits) HOLDS. yf (100), yj (200) test progressively more.
ym tests 500 edits. At 500 edits over M=4096 facts, ~12% of all facts
are edited. Cumulative drift across 500 anti-Hebbian + insert ops is
the extreme stress.

## Hypothesis

Kerdock arm holds 500 edits at >= 0.95 acc — substantively unbounded.

## Verdict labels

- `CONTINUAL_V4_HOLDS_TO_500`
- `CONTINUAL_V4_DECAYS_AT_<I>`
- `CONTINUAL_V4_BOTH_FAIL`
- `CONTINUAL_V4_INCONCLUSIVE`

## Operational definition

Reuses yc functions; N_EDITS = 500.

## Expected runtime: ~15-25 min on GPU (500 × per-edit ALL-fact query)
