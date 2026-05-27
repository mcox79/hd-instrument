# Prereg: wave14_betB_replay_hA_direct_v2

**Date:** 2026-05-26
**Parent:** wave14_betB_replay_hA_direct_v1 HA_MIDDLE (lift=0.028 at N=4096)
**Question:** Does H-A inter-phase replay lift sharpen at N=8192?

## Hypothesis
v1 showed weak positive signal (lift=0.028). N=8192 should give sharper separation
between Arm1 (inter-phase replay) and Arm2 (no replay) if H-A consolidation is a real mechanism.

## Design
- N=8192; 5 seeds; 3 arms (inter-phase, no-replay, intra-phase replay)
- GPU (overnight_queue)

## Pre-registered bands
- **HARD_PASS**: ret(Arm1) - ret(Arm2) >= 0.05 (5pp lift; same as v1)
- **HARD_FAIL**: lift < 0.01 at N=8192
- **MIDDLE_BAND**: lift in [0.01, 0.05)

## Calibration
v1 lift=0.028 (MIDDLE). Bands unchanged from v1 prereg. Walk-back: if N=8192 still MIDDLE, pre-register N=16384.
