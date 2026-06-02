# Pre-registration: q23_capacity_cliff_fine_alpha_v1

**Date:** 2026-06-02
**Anchor:** q23_capacity_cliff_fine_alpha_v1
**Queue:** remote_cpu_queue

## Hypothesis
Fine alpha sweep near alpha_c shows smooth, gradual degradation: max accuracy drop
between adjacent alpha values < 0.15, and regression slope is significantly negative.

## Pre-registered thresholds
- HARD-PASS: max_step < 0.15 AND regression slope significantly negative (p < 0.05).
- MIDDLE: max_step in [0.15, 0.20] or slope not significant.
- HARD-FAIL: max_step >= 0.20 (sharp cliff).

Prior: capacity_cliff_graceful_full_v3 HARD_PASS at coarse grid. This verifies fine-grid smoothness.

## Smoke result
N=1024, alpha=[0.09, 0.12, 0.138, 0.16, 0.20, 0.24], 2 seeds, M_eval=50:
- max_step=0.0024 (HP<0.15)
- slope=-0.0386, p=0.0007 (sig negative)
- HARD_PASS smoke. Smooth degradation confirmed at N=1024.
- Smoke wall: 0.3s.

## Timeout estimate
Smoke wall: 0.3s / (2 seeds * 6 alpha) = ~0.025s per cell.
Full: 5 seeds * 15 alpha = 75 cells * 0.025s = 1.9s.
wall = 1.5 * 1.9 = 2.9s. timeout=60s.
