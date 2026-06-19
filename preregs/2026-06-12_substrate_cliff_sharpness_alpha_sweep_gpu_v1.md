# Pre-registration: cliff-sharpness alpha-sweep at fixed N=1024 (bulk-regime 2nd appearance)

**Date:** 2026-06-12 Cycle 50. Cell: exp_substrate_cliff_sharpness_alpha_sweep_gpu_v1.py. Lane: overnight_queue (GPU). NO LLM frame.
Routing: strategy_request cliff_sharpness_alpha_sweep_bulk_regime v592.

## Design
PP-413 found (N-sweep, alpha=0.5) the cleanup cliff is BULK MEAN-FIELD (F_cliff~N slope 0.99; scaled sharpness N-invariant
~0.28). This tests bulk-regime generality ACROSS alpha at fixed N=1024: alpha in {0,0.25,0.5,0.75,1.0}; identity-augmented
241-atom codebook per alpha; wide F-grid {8..100} bracketing the cliff for all alpha; 3 seeds. Per alpha: F_cliff (interp),
abs + SCALED sharpness (transition-band linear fit).

## Bands (v592)
- HARD-PASS (bulk 2nd appearance): scaled sharpness within +/-0.10 of 0.28 across ALL alpha AND F_cliff(alpha) monotone.
- MIDDLE: scaled sharpness alpha-dependent but in [0.20,0.40].
- HARD-FAIL (edge crossover): scaled sharpness leaves [0.20,0.40] across alpha.
- UNKNOWN if corpus load fails. (alpha=0 is collision-influenced; reported honestly.)
