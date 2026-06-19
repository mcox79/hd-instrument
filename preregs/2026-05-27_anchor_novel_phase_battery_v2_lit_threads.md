# Pre-registration: anchor_novel_phase_battery_v2_lit_threads

**Date:** 2026-05-27
**Script:** experiments/exp_anchor_novel_phase_battery_v2_lit_threads.py
**Queue:** overnight_queue (GPU; N=2048; ~1.5-2h)
**Trigger:** exp_anchor_novel_phase_battery_v1 returns DOCUMENTED_BUT_UNTESTED (>= 5/6 cells)

## Hypothesis

If substrate is in the documented-but-untested class, exactly which of the 3 lit threads
matches best: (A) Non-reciprocal Hopfield (arXiv:2501.00983), (B) Spatial-correlated DAM
(arXiv:2207.05218), or (C) Saddle-hierarchy DAM (arXiv:2508.19151)?

## Design

3-arm battery (N=2048, 5 seeds):
- Arm 1: Cooling-rate independence (Thread A signature)
- Arm 2: alpha_c shift -- random vs structured patterns (Thread B signature)
- Arm 3: Singular-value staircase alignment (Thread C signature)

## Pre-registered bands

- **THREAD_A_DOMINANT:** Arm1 |r| < 0.20 AND Arm2 delta_ret > -0.02 AND Arm3 max_diff > 0.12
- **THREAD_B_DOMINANT:** Arm1 |r| > 0.40 AND Arm2 delta_ret < -0.03
- **THREAD_C_DOMINANT:** Arm3 max_diff < 0.05 (spectral staircase alignment)
- **MIXED_EVIDENCE:** no arm dominates
