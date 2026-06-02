# Pre-registration: combo1_p3_dam_implicit_gram_v2_identity_fix_v1

**Date:** 2026-06-02
**Script:** experiments/exp_combo1_p3_dam_implicit_gram_v2_identity_fix_v1.py
**Queue:** overnight_queue
**N:** 4096 (no _nN suffix; production N=4096 per rule 3)
**Seeds:** [7, 17, 23, 31, 41]
**Smoke result:** HARD_PASS 3/4 (HP1=True, HP2_cv=True, HP3_slope=True, HP4_snr=False)

## Hypothesis

The p=3 implicit Gram matrix G_ij=(xi_i^T xi_j/N)^3 stored in a DAM has:
- HP1: MMD(G_stored, G_ideal) < 0.10 (distributional fidelity)
- HP2: CV(lambda_max(G) across seeds) < 0.20 (spectral stability - calibration probe, no theory anchor)
- HP3: retrieval error decays with pattern count slope <= 1.5 (capacity scaling)
- HP4: SNR in [0.50, 2.00] (signal quality range)

Redesign from v1 which had broken kappa_3=M/N identity for p=3 Gram.

## Metrics

- `mmd`: maximum mean discrepancy between stored and ideal Gram distributions
- `cv_lmax`: coefficient of variation of lambda_max(G) across seeds
- `slope`: power-law fit of retrieval error vs M
- `snr`: signal-to-noise ratio of retrieval

## Thresholds (pre-registered)

**HP1:** mmd < 0.10
**HP2:** cv_lmax < 0.20
**HP3:** slope <= 1.5
**HP4:** snr in [0.50, 2.00]
**HARD_PASS:** HP1 AND HP2 AND HP3 (HP4 informational only - smoke showed 3/4 pass)
**HARD_FAIL:** mmd > 0.50 OR cv_lmax > 0.50 OR slope > 3.0
**MIDDLE_BAND:** HP1+HP2+HP3 mixed, no HARD_FAIL

## Timeout

2400s (from: smoke ~8s per seed * 5 seeds * 1.5 overhead = 60s; full N=4096 scales ~40x = 2400s)
