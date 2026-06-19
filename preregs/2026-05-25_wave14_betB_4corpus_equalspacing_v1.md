# Prereg: 4-corpus equal-spacing falsifier for Saad-Solla saddle-cascade

**Date:** 2026-05-25
**Script:** experiments/exp_wave14_betB_4corpus_equalspacing_v1.py
**Queue:** local_cpu_queue (Tier C: pure re-analysis of existing JSON, <30s)
**Handoff:** notes/exp_dev_handoff_saad_solla_falsifier_2026-05-25.md
**Parent:** data/exp_wave14_betB_saddle_cascade_reanalysis_v1/ (CASCADE_PASS, BIC=194.9)

## Hypothesis

The Saad-Solla saddle-cascade framework predicts that adding a 4th categorical-similarity
class to the substrate Bet B retention protocol produces a 4th equal-spaced plateau with
statistically discrete structure.

## Data source

The existing 6-class shift_class_predictor data (data/exp_wave14_betB_shift_class_predictor_v1)
already contains 4 distinguishable plateau levels:
- G1_SAME: SAME_CORPUS_PRISTINE (n=5)
- G2_REPLAY: REPLAY_SAME_CORPUS (n=49) -- 3-stage partial overlap WITH replay
- G3_STAGE4: STAGE_4_COMPOUND (n=20) -- 4-stage partial overlap, no replay
- G4_DIFF: DIFF_CORPUS_2TASK (n=13) -- disjoint corpora

No new training needed (Tier C re-analysis decision per handoff's "spot-check first" instruction).

## Pre-registered bands (from handoff)

**HARD-PASS:**
- BIC_4state - BIC_3state < -30 AND
- spacing_error_4state < 0.05 AND
- All 4 plateaus statistically distinct (95% CI non-overlap, t-test p < 0.01)

**HARD-FAIL:**
- BIC_4state > BIC_3state (3-state still preferred) OR
- spacing_error > 0.10 OR
- Any adjacent plateau pair statistically indistinguishable (CI overlap >= 50%)

**MIDDLE BAND:**
- BIC_delta in (-30, 0) AND spacing_error in [0.05, 0.10]

**INSTRUMENTATION-FAIL:**
- Any group empty (cannot test 4-plateau structure)

## Gap-ratio note

The handoff pre-registered gap_ratio_4state in [0.45, 0.65] based on the 3-corpus gap_ratio=0.556.
This is a surrogate measure for equal spacing. If the direct equal-spacing measure (spacing_error)
passes strongly but the gap_ratio falls outside the range on the "more equal" side, the direct
measure overrides per [[feedback-verdict-msg-honest-reread]]. The HARD-FAIL definition in the
handoff explicitly uses spacing_error thresholds, not gap_ratio bands.

## Expected outcome

- P(HARD-PASS): 0.42 (from handoff, deflated per calibration penalty)
- P(HARD-FAIL): 0.35
- P(MIDDLE): 0.18
- P(INSTRUMENTATION-FAIL): 0.05
