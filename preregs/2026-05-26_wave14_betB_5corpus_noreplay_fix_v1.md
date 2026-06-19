# Prereg: wave14_betB_5corpus_noreplay_fix_v1

**Date:** 2026-05-26
**Parent:** wave14_betB_5corpus_fullscale_v1 HARD_FAIL (monotone order violated: G4_NOREPLAY=0.557 < G5_DIFF=0.633)
**Question:** Does the correct 4-class taxonomy (without the NOREPLAY axis confusion) show clean Saad-Solla equal-spacing?

## Hypothesis
The NOREPLAY_SAME_CORPUS class is on a DIFFERENT axis (intervention axis) than the 4 overlap-ordered classes.
Removing it and running the pure 4-class overlap taxonomy (SAME/REPLAY/STAGE4/DIFF) should show clean equal-spacing.

## Design
- 4 classes: G1_SAME, G2_REPLAY, G3_STAGE4, G4_DIFF
- N=4096; 20 seeds; GPU (overnight_queue)

## Pre-registered bands
- **HARD_PASS**: BIC_4vs3 < -30 AND spacing_error < 0.05 AND ordered AND all adjacent distinct
- **HARD_FAIL**: BIC_4vs3 > 0 OR spacing_error > 0.10 OR not ordered
- **MIDDLE_BAND**: BIC in (-30, 0), spacing in [0.05, 0.10]
- **INSTRUMENTATION_FAIL**: monotone violated (if G4_DIFF > G3_STAGE4)

## Calibration
Parent 4-corpus HARD_PASS (BIC_delta=-121.3 at N=4096, spacing_error=0.0035). 
This test re-confirms with a cleaner protocol (20 seeds, correct 4-class design).
