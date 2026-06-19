# Pre-registration: wave14zo_alpha_sweep

Date: 2026-05-21
Status: Pre-registered, gated
Priority: parametric sweep — anti-Hebbian erase strength alpha
Author: experiment_dev session, pipeline tick 51

## Why
All prior edit-then-query tests (yb, yc, zh, zi, zj, zk, zl, zn) fixed alpha=1.0
(full erase). What if partial erase (alpha < 1) preserves kept facts better
while still pushing edit_acc high enough? Or what if alpha > 1 ("over-erase")
adds robustness?

Sweep alpha in {0.5, 0.8, 1.0, 1.2, 1.5}. Measure edit_argmax_acc and kept_acc
at each. Find the operating point that maximizes min(edit, kept).

## Verdict labels
- ALPHA_OPT_AT_<A>
- ALPHA_DEFAULT_BEST (alpha=1.0 wins)
- ALPHA_FLAT (all alphas perform within tolerance)
- ALPHA_INCONCLUSIVE

## Runtime: ~3 min
