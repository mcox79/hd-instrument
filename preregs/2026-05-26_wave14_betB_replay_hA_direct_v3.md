# Prereg: wave14_betB_replay_hA_direct_v3

**Date:** 2026-05-26
**Parent:** wave14_betB_replay_hA_direct_v2 (in-flight; H-A consolidation direct probe at N=8192)
**Trigger:** ship when v2 returns HARD_PASS (inter-phase replay > intra-phase by >= 0.05)
**Question:** What is the temporal resolution of H-A consolidation? Phase boundary, recency, or fixed interval?

## Hypothesis
If H-A consolidation is confirmed, the mechanism requires specificity about WHEN replay occurs.
Three competing hypotheses tested by 5-arm comparison:
- H-A1: phase boundary is specific (only boundary replay works)
- H-A2: recency gradient (recent patterns benefit most)
- H-A3: fixed interval suffices (any short-interval replay matches boundary replay)

## Design
- 5 arms: INTER_BOUNDARY (v2 baseline), INTRA_RANDOM (v2 control), INTRA_RECENT (last 20%),
         INTRA_FIXED_INTERVAL (every 100 steps), NO_REPLAY (zero)
- N=8192, 5 seeds, GPU overnight_queue (~3-4 hrs)
- Same training parameters as v2

## Pre-registered bands
- **H_A1_CONFIRMED**: INTER - FIXED >= 0.04 AND INTER - INTRA_RANDOM >= 0.04
- **H_A2_CONFIRMED**: INTRA_RECENT >= INTER AND RECENT - INTRA_RANDOM >= 0.05
- **H_A3_CONFIRMED**: |INTER - FIXED| < 0.02 AND both > INTRA_RANDOM by >= 0.04
- **AMBIGUOUS**: max gap across arms < 0.03
- **INSTRUMENTATION_FAIL**: non-finite retention in any arm

## Calibration
Prior anchor: v2 HARD_PASS INTER - INTRA_RANDOM >= 0.05 (pending). H-A1 gap threshold of 0.04
is 80% of the v2 consolidation effect (conservative; 5 arms spreads signal vs 3-arm v2).

## Middle-band outcome plan
AMBIGUOUS result: increase N to 16384 or add 10 more seeds to resolve.
