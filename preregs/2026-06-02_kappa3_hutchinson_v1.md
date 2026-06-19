# Pre-registration: kappa3_hutchinson_v1

**Date:** 2026-06-02
**Anchor:** kappa3_hutchinson_v1
**Script:** experiments/exp_kappa3_hutchinson_v1.py
**Queue:** remote_cpu_queue
**Timeout:** 3600s

## Scientific question (Q-C3)

Does the kappa_3 free-cumulant Hutchinson estimator discriminate Hopfield from
GOE matrices by sigma_sep >= 4.0 at N=4096, confirming the free-Poisson
fingerprint?

## Bands (pre-registered)

**HARD-PASS (HP):**
- min sigma_sep >= 4.0 across all M values
- theory_ratio (measured / predicted) in [0.05, 20.0] (calibration probe: wide band)

**MIDDLE:**
- min_sep in [2.0, 4.0] OR theory_ratio outside [0.05, 20.0] but within [0.01, 100.0]

**HARD-FAIL (HF):**
- min_sep < 2.0 (Hopfield and GOE statistically indistinguishable at 2-sigma)

## Smoke result
HARD_PASS: min_sigma_sep=12.5, mean=344.0 (HP>=4.0), theory_ratio=12.59 (within 20.0x).
Wall time: near instant (2 seeds). FULL estimate: ~600s (5 seeds, M=[100,200,500,1000]).

## Notes
Calibration probe: no prior anchor. Bands set +-50% of theoretical prediction is
not applicable here as the metric is sigma_sep (unit-free). HP_THEORY_MATCH_FACTOR=20.0
allows for normalization correction in the Hutchinson estimator.

## PROT-018
No _nN suffix. Production N=4096 declared in script.
