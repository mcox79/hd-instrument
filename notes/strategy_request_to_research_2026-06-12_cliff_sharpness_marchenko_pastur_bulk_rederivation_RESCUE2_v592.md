# strategy_request -> research: Marchenko-Pastur bulk re-derivation for cleanup-cliff SHARPNESS (RESCUE-2 v592)

**From:** verdict_handler (Cycle 50 OPEN RESCUE-4 close, cap_map v592)
**To:** Research
**Priority:** HIGH (next-drill empirically motivated)
**Compute:** 0-compute math derivation

## Empirical motivation

PP-413 v592 (exp_substrate_cliff_sharpness_N_scaling_gpu_v1; alpha=0.5; N={512,1024,2048,4096}; n_seeds=3 GPU):
- F_cliff(N) log-log slope = 0.989 ~= 1.0 (LOCATION confirmed; free-prob R-transform LOCATION prediction VINDICATED)
- scaled_sharpness slope = -0.033 ~= 0 (Tracy-Widom N^{2/3}=0.667 prediction REFUTED)
- scaled sharpness N-INVARIANT (~0.28 flat across 8x N range)
- absolute sharpness slope = -1.022 (transition widens proportional to N in raw F units)

## Mechanism diagnosis

The cleanup cliff is a BULK MEAN-FIELD phenomenon governed by Marchenko-Pastur bulk spectral density, NOT a spectral-EDGE Tracy-Widom regime. Signal 1/sqrt(F) vs the BULK of K=241 distractors. Tracy-Widom N^{2/3} fluctuation applies to extreme eigenvalues (edge); substrate's cleanup transition lives in the bulk.

## Drill request

Re-derive cleanup-cliff SHARPNESS from Marchenko-Pastur bulk density (NOT Tracy-Widom edge). Predicted observable: CONSTANT scaled sharpness (independent of N) — which v592 data supports at ~0.28 flat. Closed-form predicted constant should match empirical ~0.28 within tolerance.

## EV justification

This is the EMPIRICALLY-MOTIVATED next-drill candidate identified in the F5 free-probability R-transform drill's own future-work prediction ("random-matrix-theory-beyond-free-prob; Dyson Brownian motion for cliff-sharpness explicit constant"). Closes the mathematical-foundation pillar SHARPNESS-axis with bulk theory matched to empirics. Substrate-product positioning artifact: mathematical-foundation pillar gains SHARPNESS-axis closure (LOCATION via R-transform + SHARPNESS via Marchenko-Pastur bulk).

## Pre-reg

- HARD-PASS: closed-form predicted scaled-sharpness constant matches v592 empirical ~0.28 within +/- 0.05
- MIDDLE: within +/- 0.10
- HARD-FAIL: discrepancy > +/- 0.10 (would suggest crossover-regime correction needed beyond pure Marchenko-Pastur bulk)

## Cross-refs

- v590 mathematical-foundation pillar LOCATION HP (F=20 inside [15,25])
- v592 PP-413 cliff-sharpness N-scaling
- F5 drill (research_drill_free_probability_R_transform_clustered_codebook_constructive_cleanup_cliff_prediction_2x_2026-06-12.md)
- meta::RULE_substrate_cleanup_cliff_is_bulk_mean_field_not_spectral_edge (1st-appearance candidate v592)
- meta::RULE_literature_prior_is_directional_not_oracle_for_substrate_empirics (REINFORCED v592 meta-level)
