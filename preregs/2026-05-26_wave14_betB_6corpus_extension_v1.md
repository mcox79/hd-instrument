# Prereg: wave14_betB_6corpus_extension_v1

**Date:** 2026-05-26
**Parent:** wave14_betB_5corpus_noreplay_fix_v1 (in-flight; 4-class Saad-Solla taxonomy)
**Trigger:** ship when 5corpus_noreplay_fix_v1 returns HARD_PASS (BIC_4vs3 < -30 AND spacing_err < 0.05)
**Question:** Does the Saad-Solla equal-spacing prediction extend to 6 corpora?

## Hypothesis
If the 4-class plateau structure is confirmed, adding 5th and 6th phases should produce
additional discrete plateaus (not smoothing), since the Saad-Solla fixed-point structure
predicts one plateau per distinct overlap class.

## Design
- 6 phases: A (native), B (shuffled A), C (independent), D (shuffled C), E (shuffled B), F (independent 2)
- 20 seeds, N=4096, GPU overnight_queue (~4-6 hrs)
- Primary: retention_A after each phase (5 retention measurements)
- BIC test: 5-state vs 4-state vs 3-state
- Equal-spacing error of the 5 post-B retention values

## Pre-registered bands
- **HARD_PASS**: BIC_5vs4 < -25 AND spacing_error < 0.05 AND retentions monotone non-increasing
- **HARD_FAIL**: BIC_5vs4 > 0 (4-state preferred) OR spacing_error > 0.10
- **MIDDLE_BAND**: BIC_5vs4 in (-25, 0) OR spacing_error in [0.05, 0.10)
- **INSTRUMENTATION_FAIL**: non-finite retentions OR BIC computation fails

## Calibration
Prior anchor: v1 4-class BIC_4vs3 ~ -30 (to be confirmed by 5corpus_noreplay_fix_v1).
BIC_5vs4 threshold of -25 is 83% of the prior 4-state threshold; reasonable if 5th plateau is weaker.

## Middle-band outcome plan
If HARD_FAIL (framework limit at 4 classes): accept 4-class taxonomy as the Saad-Solla limit.
Route to: per-phase temporal analysis to understand WHY 5th class doesn't emerge (interference vs capacity).
