# Pre-registration: wave14_betB_nscaling_v1

Date: 2026-05-26
Experiment file: experiments/exp_wave14_betB_nscaling_v1.py
Queue: overnight_queue

## Context
v206 4-corpus equal-spacing HARD_PASS at N=4096 (BIC_delta=-121.3, spacing_error=0.0035,
REPLAY Cohen's d=13.3). Saad-Solla saddle-cascade arithmetic corroborated. v207 Alt 3 
PAC-Bayes closed. This is an envelope-expansion probe: does 4-class taxonomy hold at N=8192?

## Design
- N_FULL=8192, 5 seeds (7,17,23,31,41)
- 4-stage M1 hierreplay training (same as v206 infrastructure)
- Extract retention_A (corpus A after 4 stages), retention_B (corpus B after 4 stages)
- Test equal-spacing on {G4_floor=0.633, G3=ret_A, G2=ret_B, G1_ref=0.941}
- BIC delta (4-state equal-spacing vs 3-state), spacing_error, Cohen's d (REPLAY axis)

## Pre-registered bands (envelope-expansion of v206)
HARD-PASS: BIC_delta < -30 AND spacing_error < 0.05 AND all 4 plateaus statistically distinct
           AND REPLAY Cohen's d >= 5.0 (weaker than v206's 13.3 allowed for larger N range)
HARD-FAIL: BIC_delta > 0 OR spacing_error > 0.10 OR fewer than 3 distinct plateau levels
MIDDLE: BIC passes but spacing_error in [0.05, 0.10]; plateaus not fully distinct

## Falsifiable predictions
- If 4-class taxonomy is a thermodynamic-limit property: spacing_error should decrease vs v206
  (sharper plateaus at larger N, consistent with saddle-cascade continuous-limit structure)
- If finite-N artifact: spacing_error should increase or become inconsistent at N=8192
- Cohen's d for REPLAY axis should remain large (>5.0) if structural separation is real

## Walk-back gate
If N=8192 Cohen's d < 3.0 (< v206 value), pre-register N=16384 before closure.
Smoke at N=512 showed retention values non-null and separation forming (ret_A=0.943, ret_B=0.939).
Walk-back gate confirmed: N=1024 also non-null (ret_A=0.992, ret_B=0.924).

## Self-test inputs/outputs
- bic_equal_spacing([0.6, 0.7, 0.8, 0.9]) -> spacing_error=0.0 (perfect equal-spacing)
- cohen_d_two_groups([1,1,1], [0,0,0]) -> large d > 1.0
- N_FULL=8192 (envelope expansion of v206 N=4096)
