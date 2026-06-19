# Prereg: wave14_1rsb_capacity_plateau_v1

**Filed**: 2026-05-24 exp_dev
**Anchor**: Pred-1 (1-RSB diagnostic) -- Capacity-sweep plateau morphology
**Trigger**: k2_m1_hierreplay HARD_PASS + basin-discrete 1-RSB framing;
             1-RSB predicts plateau-cliff-plateau morphology in retA vs
             M_stored (task complexity); RS predicts smooth monotone decay.

## Hypothesis

1-RSB prediction: retA vs M_stored (bytes per stage) across
{25k, 50k, 100k, 150k, 200k, 300k, 400k} shows:
  - Plateau region at low M (retA high + flat)
  - Cliff: sharp drop >= 0.15 at some M_critical
  - Plateau region at high M (retA low + flat)
  This is the signature of 1-RSB basin-structured capacity.

RS prediction: smooth monotone decay (max consecutive step < 0.08).

## Design (exp_dev autonomy)

- N = 4096 (FULL), 1024 (smoke)
- Batch = 64 (FULL), 32 (smoke)
- Epochs = 5 (FULL), 1 (smoke)
- Phase-A epochs = 8 (FULL), 1 (smoke)
- M sweep = {25k, 50k, 100k, 150k, 200k, 300k, 400k} bytes (FULL),
            {10k, 50k, 200k} (smoke)
- Seeds = {7, 17, 23} (FULL, 3 seeds to bound GPU budget), {17} (smoke)
- Chunk fraction = 0.5 (M1 mechanism)
- Queue: overnight_queue (GPU -- 7 M values x 3 seeds x 4 stages)
- ETA: ~5-6 hours GPU

## Pre-registered falsifier bands (before FULL run)

- **HARD-PASS (1-RSB plateau morphology)**: any consecutive M pair with
  |delta_retA| >= 0.15 (cliff) AND at least one consecutive M pair with
  |delta_retA| < 0.05 (plateau) on EITHER side of the cliff.
  -> CAPACITY_PLATEAU_1RSB_CONFIRMED: discrete cliff + plateau morphology; 1-RSB supported.

- **HARD-FAIL (RS smooth)**: max |delta_retA| across ALL consecutive M pairs < 0.08.
  -> CAPACITY_PLATEAU_RS_SMOOTH: smooth monotone; 1-RSB NOT supported at capacity axis.

- **MIDDLE**: anything between.

## Self-test cells

(M_retA: [(25k,0.89),(50k,0.88),(100k,0.70),(200k,0.68),(400k,0.67)]) -> CAPACITY_PLATEAU_1RSB_CONFIRMED
(M_retA: [(25k,0.92),(50k,0.89),(100k,0.86),(200k,0.83),(400k,0.80)]) -> CAPACITY_PLATEAU_RS_SMOOTH
(M_retA: [(25k,0.92),(50k,0.85),(100k,0.75),(200k,0.72)]) -> CAPACITY_PLATEAU_MIDDLE
({}) -> CAPACITY_PLATEAU_INCONCLUSIVE

All 4/4 self-test cases pass in script self_test_verdict().

## Queue entry

`queue=overnight_queue name=wave14_1rsb_capacity_plateau_v1 script=experiments/exp_wave14_1rsb_capacity_plateau_v1.py prereg=preregs/2026-05-24_wave14_1rsb_capacity_plateau_v1.md timeout=25200`
