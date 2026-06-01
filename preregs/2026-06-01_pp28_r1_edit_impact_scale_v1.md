# Prereg: pp28_r1_edit_impact_scale_v1

**Date**: 2026-06-01
**Anchor**: pp28_r1_edit_impact_scale_v1
**Queue**: remote_cpu_queue
**Script**: experiments/exp_pp28_r1_edit_impact_scale_v1.py
**Source**: notes/research_round5_7_drills_synthesis_2026-06-01.md (PP-28, R1 MANDATORY GATE)

## Hypothesis

Edit-impact algebraic perturbation formula achieves MAE < 0.05 on score shift
AND top-50 ranking accuracy >= 0.85 at k=5000 compositions. Closed-form:
delta_s_j = (-(q_j^T p)^2 + N) / N^2 for pattern erase (with diagonal zeroing
correction for bipolar patterns).

## Design

- N = 1024, k = 5000 compositions (random bipolar query vectors)
- M = 64 stored patterns; erase pattern 0
- Predicted delta: closed-form formula (no simulation)
- Actual delta: matrix operation Q @ delta_W @ Q^T diagonal
- 5 seeds

## Pre-registered thresholds (LOAD-BEARING)

**HARD-PASS**: MAE < 0.05 AND rank_acc >= 0.85 (top-50 ranking); in >= 4/5 seeds.

**HARD-FAIL**: MAE >= 0.20 OR rank_acc < 0.50; in >= 4/5 seeds.

**MIDDLE-BAND**: MAE in [0.05, 0.20) or rank_acc in [0.50, 0.85).

## Formula self-tests (pre-registered)

1. delta_W = -outer(p,p)/N with diag zeroed.
2. q^T delta_W q / N = (-(q^T p)^2 + N) / N^2 (diagonal correction for bipolar q,p).
3. MAE should be near float32 precision (formula is algebraically exact).
4. rank_acc = |{top-50 pred} & {top-50 actual}| / 50.

## Smoke result

Smoke (3 seeds): MAE = 0.000977 (near float32 precision), rank_acc = 1.0000.
MIDDLE_BAND (3/3 seeds pass HP; need 4/5). Full run expected HARD_PASS.

## Timeout estimate

smoke_wall_s = 0.6s; 5/3 seeds; linear.
timeout_s = ceil(1.5 * 0.6 * 5/3) = ceil(1.5) = 300 (PROT-019 floor).

## N-suffix

No _nN suffix. Production N = 1024; stated per PROT-018 rule 3.
