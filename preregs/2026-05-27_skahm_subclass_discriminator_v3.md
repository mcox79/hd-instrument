# Pre-registration: skahm_subclass_discriminator_v3

**Date**: 2026-05-27
**Anchor**: skahm_subclass_discriminator_v3
**Script**: experiments/exp_skahm_subclass_discriminator_v2.py (rerun as v3)
**Queue**: remote_cpu_queue
**Parent**: skahm_subclass_discriminator_v2 (MIDDLE_BAND; smoke only 1 seed ran)

## Hypothesis

Sharpening ratio d_transition(N=4096) / d_transition(N=512) >= 1.5 in >= 3/5 seeds.
(Saddle-hierarchy N-scaling prediction.)

## Pre-registered bands (same as v2)

- HARD-PASS: sharpening ratio > 1.5 in >= 3/5 seeds
- HARD-FAIL: sharpening ratio < 1.1 (flat) in >= 4/5 seeds OR decreases in >= 3/5 seeds
- MIDDLE-BAND: ratio in [1.1, 1.5)

## Timeout estimate

smoke_wall_s = 0.38s, smoke_N in [128,512], FULL_N in [512,4096], seeds 1->5.
timeout_s = ceil(1.5 * 0.38 * (4096/512)^1.0 * (5/1)) = ceil(1.5 * 0.38 * 8 * 5) = ceil(22.8) -> 1200s (margin for all seeds and f-sweep).
