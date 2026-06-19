# Prereg: wave14_betB_nscaling_v2

**Date:** 2026-05-26
**Parent:** wave14_betB_nscaling_v1 MIDDLE at N=8192 (BIC_delta=-0.0036, near zero)
**Question:** At N=4096 with 25 seeds, does the 4-class BIC cross -30 cleanly?

## Hypothesis
v1 at N=8192 with 5 seeds had BIC_delta=-0.0036 (essentially zero). The issue may be
insufficient seeds for BIC power. N=4096 (where v206 HARD_PASS was BIC=-121.3) with
25 seeds should replicate the HARD_PASS result.

## Design
- N=4096; 25 seeds; 4-stage M1 hierreplay protocol; GPU (overnight_queue)

## Pre-registered bands  
- **HARD_PASS**: BIC_4vs3 < -30 AND spacing_error < 0.05 (same as v206/v1)
- **HARD_FAIL**: BIC_4vs3 > 0
- **MIDDLE_BAND**: BIC in (-30, 0)

## Calibration
v206 at N=4096 5seeds: BIC_delta=-121.3. Expect similar with 25 seeds. If MIDDLE, escalate to N=16384.
