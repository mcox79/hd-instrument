# Prereg: wave14e_bet_n_wta_v4

**Date:** 2026-05-26
**Parent:** wave14e_bet_n_wta_v3 P3=HARD_FAIL (retrieval_gap=-0.0483)
**Question:** Does K=512 codebook improve P3 corpus-specificity signal?

## Hypothesis
v3 used K=256. P3 cross-corpus gap was negative (-0.0483), suggesting the codebook
is not learning corpus-specific structure. K=512 provides a richer codebook space.
If corpus-specificity exists, it should be more visible with a larger codebook.

## Design
- K=512; N=4096; n_epochs=8; M-sweep {100,500,1000,2000,4000,8000}
- 5 seeds FULL; GPU (overnight_queue)

## Pre-registered bands
- **P1 HARD_PASS**: WTA utilization >= 0.5 (same as v3)
- **P2 HARD_PASS**: learned/random cleanup ratio >= 1.1 at M=2000 anchor
- **P3 HARD_PASS**: cross-corpus_gap > 0.0 at >= 3 of 5 seeds (positive direction needed)
- **HARD_FAIL**: P3 gap <= -0.05 (negative, worse than random)
- **MIDDLE_BAND**: P3 gap in (-0.05, 0.0)

## Calibration
v3 had P3 gap=-0.0483. No prior K=512 anchor. Bands are first-probe calibration policy (±50%).
