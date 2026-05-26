# Prereg: wave14_1rsb_cascade_depth_v1

**Filed**: 2026-05-24 exp_dev
**Anchor**: Pred-5 (1-RSB diagnostic) -- Cascade-depth sensitivity
**Trigger**: k2_m1_hierreplay smoke HARD_PASS retA=0.888 vs 0.74 baseline;
             basin-discrete 1-RSB framing is the leading signal for why
             hierarchical replay breaks the 4-stage ceiling. This test
             probes whether retA vs chain depth has a DISCRETE cliff (1-RSB)
             or smooth linear degradation (RS).

## Hypothesis

1-RSB prediction: retention profile across depths {2,3,4,5} shows
plateau-cliff-plateau morphology -- discrete drop at a critical depth,
not smooth linear decay.
RS prediction: smooth monotone degradation (max consecutive step < 0.08).

## Design (exp_dev autonomy)

- N = 4096 (FULL), 1024 (smoke)
- Batch = 64 (FULL), 32 (smoke)
- Epochs = 5 (FULL), 1 (smoke)
- Phase-A epochs = 8 (FULL), 1 (smoke)
- Bytes = 200000 (FULL), 5000 (smoke)
- Seeds = {7, 17, 23, 31, 41} (FULL), {17} (smoke)
- Depths tested = {2, 3, 4, 5} (FULL), {2, 3, 4} (smoke)
- Chunk fraction = 0.5 (M1 mechanism)
- Queue: overnight_queue (GPU -- 5-stage chains require GPU)
- ETA: ~6-7 hours GPU

## Pre-registered falsifier bands (before FULL run)

- **HARD-PASS (1-RSB)**: Any consecutive depth pair with |delta_retA| >= 0.15 (cliff)
  AND at least one consecutive depth pair with |delta_retA| < 0.05 (plateau).
  -> CASCADE_DEPTH_1RSB_CONFIRMED: discrete cliff + plateau; 1-RSB cascade depth supported.

- **HARD-FAIL (RS)**: max |delta_retA| across ALL consecutive depth steps < 0.08
  AND variance of per-step deltas < 0.002.
  -> CASCADE_DEPTH_RS_SMOOTH: smooth monotone; 1-RSB NOT supported at depth axis.

- **MIDDLE**: anything between HARD-PASS and HARD-FAIL criteria.

## Self-test cells

(depth_profile: [(2,0.94),(3,0.93),(4,0.74),(5,0.73)]) -> CASCADE_DEPTH_1RSB_CONFIRMED
(depth_profile: [(2,0.94),(3,0.91),(4,0.88),(5,0.85)]) -> CASCADE_DEPTH_RS_SMOOTH
(depth_profile: [(2,0.94),(3,0.88),(4,0.74),(5,0.70)]) -> CASCADE_DEPTH_MIDDLE
({}) -> CASCADE_DEPTH_INCONCLUSIVE

All 4/4 self-test cases pass in script self_test_verdict().

## Queue entry

`queue=overnight_queue name=wave14_1rsb_cascade_depth_v1 script=experiments/exp_wave14_1rsb_cascade_depth_v1.py prereg=preregs/2026-05-24_wave14_1rsb_cascade_depth_v1.md timeout=28800`
