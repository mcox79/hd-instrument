# Prereg: wave14_1rsb_pq_retained_v3

**Date:** 2026-05-26
**Parent:** wave14_1rsb_pq_retained_v2 PQ_RETAINED_MIDDLE at N=4096 (binder=0.534)
**Question:** Does N=8192 with 30 seeds produce a stronger binder cumulant signal?

## Hypothesis
v2 binder=0.534 is above 0.30 threshold but below the level needed for clear P(q) bimodality.
N=8192 with 30 seeds provides both larger effective sample and tighter statistics.

## Design
- N=8192; 30 seeds; KDE_BW=0.01 (tighter)
- GPU (overnight_queue)

## Pre-registered bands
- **HARD_PASS**: binder > 0.30 AND n_peaks >= 2 AND mean_q_sig > 5 (same as v2)
- **HARD_FAIL**: binder < 0.10 at N=8192, 30 seeds
- **MIDDLE_BAND**: binder in [0.10, 0.30)

## Calibration
v2 at N=4096 binder=0.534. Bands unchanged from v2 prereg. This is an envelope-expansion.
No prior empirical anchor at N=8192; bands widened per policy (N=8192 is uncharted territory for this metric).
