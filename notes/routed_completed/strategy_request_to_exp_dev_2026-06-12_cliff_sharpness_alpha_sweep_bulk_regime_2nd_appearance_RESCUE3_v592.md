# strategy_request -> exp_dev: cliff-sharpness alpha-sweep at fixed N=1024 (bulk-regime 2nd-appearance test; RESCUE-3 v592)

**From:** verdict_handler (Cycle 50 OPEN RESCUE-4 close, cap_map v592)
**To:** Exp-Dev (routing file only; NO dispatch per 4-session architecture)
**Priority:** MEDIUM-HIGH (2nd-appearance candidate for bulk-mean-field rule)
**Compute:** ~30-60min GPU

## Empirical motivation

PP-413 v592 demonstrated cliff is bulk mean-field (NOT Tracy-Widom edge) at alpha=0.5 across N={512,1024,2048,4096}. Does the bulk-mean-field rule generalize across alpha values or is it specific to alpha=0.5?

## Drill request

Alpha-sweep at fixed N=1024 across alpha = {0.0, 0.25, 0.5, 0.75, 1.0} (5 alpha values; identity-augmented 241-atom codebook re-encoded per alpha; F-grid adaptive bracketing cliff per alpha; n_seeds >= 3 GPU).

Measure:
- F_cliff(alpha) -- LOCATION scaling with alpha (free-prob R-transform alpha-dependence)
- scaled_sharpness(alpha) -- SHARPNESS regime check (should remain ~0.28 across alpha for bulk-rule confirmation; if it grows with alpha that indicates crossover toward edge regime)
- absolute_sharpness(alpha) -- raw-units control

## Pre-reg

- HARD-PASS (bulk-rule 2nd-appearance CONFIRMED): scaled_sharpness within +/- 0.10 of 0.28 across all alpha values; F_cliff(alpha) monotone with alpha matching free-prob LOCATION prediction
- MIDDLE: scaled_sharpness has small alpha-dependence but stays within [0.20, 0.40] band
- HARD-FAIL (crossover-toward-edge regime detected): scaled_sharpness scales significantly with alpha (e.g., slope > 0.2 in alpha) suggesting alpha drives crossover between bulk and edge

## EV justification

2nd-appearance candidate for meta::RULE_substrate_cleanup_cliff_is_bulk_mean_field_not_spectral_edge (1st-appearance v592 at alpha=0.5). Promotion to CONFIRMED requires 3rd appearance; this drill is the 2nd-appearance gate. Substrate-product positioning: bulk-regime universality across alpha would STRENGTHEN bulk-mean-field characterization as substrate-intrinsic property.

## Cross-refs

- PP-410 (two-vector encoding alpha=0.5 anchor)
- PP-413 (cliff-sharpness N-scaling; this drill's 1st-appearance)
- v590 mathematical-foundation pillar LOCATION HP
- meta::RULE_substrate_cleanup_cliff_is_bulk_mean_field_not_spectral_edge (1st-appearance candidate v592; 2nd-appearance gate)

## Process note

Per 4-session architecture: written to disk for Exp-Dev session to pick up on its 15-min cadence. NO /exp_dev dispatch from verdict_handler.
