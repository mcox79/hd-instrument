# Pre-registration: arc_lirs_hybrid_v1

**Date:** 2026-06-02
**Anchor:** arc_lirs_hybrid_v1
**Queue:** remote_cpu_queue

## Hypothesis
ARC/LIRS hybrid (decay on WRITE + re-Hebbian boost on READ) elevates hot patterns 2x+
over cold patterns (raw dot product xi^T W xi).

## Pre-registered thresholds
- HARD-PASS: hot/cold discrimination ratio >= 2.0 at alpha=0.5.
- MIDDLE: 1.3 <= ratio < 2.0.
- HARD-FAIL: ratio < 1.3.

Calibration probe: no prior empirical anchor. Theory ~5x upper bound. HP=2.0 is 60% below theory.

## Smoke result
N=1024, gamma=0.95, k_reads=4, alpha_sweep=[0.2, 0.5], M=30, 2 seeds:
- ratio at alpha=0.5: 3.13 (HARD_PASS HP>=2.0)
- Smoke wall: 1.5s

## Timeout estimate
Smoke wall: 1.5s / 2 seeds = 0.75s/seed.
Full: 5 seeds, alpha=[0.1,0.2,0.5,1.0], M=60.
wall = 1.5 * 0.75 * 5 * (4/2) * 2 = 22.5s. timeout=120s.
