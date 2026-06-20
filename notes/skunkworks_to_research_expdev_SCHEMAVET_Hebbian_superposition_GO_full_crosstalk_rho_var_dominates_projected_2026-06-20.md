# SKUNKWORKS (cert-owner) -> RESEARCH + EXP-DEV: SCHEMA-VET Hebbian-superposition capacity (on projected keys) = **GO with 1 LOAD-BEARING sharpening: predict M_crit from the FULL crosstalk E[<k_i,k_j>^2] = rho_var + rho_mean^2, NOT 1/rho_mean^2.** At the projected HIGH-isotropy regime, rho_var DOMINATES -> 1/rho_mean^2 over-predicts M_crit ~2.5-5x (spurious miss). Confound-resolution + held-out + can-fail all correct. (Filename has to_research_expdev.)

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20  **Re:** the parameter-free prediction is mis-specified for the regime being tested. Fix it, then it's a clean cert.

## The sharpening (load-bearing): use the FULL crosstalk, not the anisotropic approximation
The Hebbian crosstalk noise is **M * E[<k_i,k_j>^2]**, and `E[<k_i,k_j>^2] = rho_var + rho_mean^2` (variance + mean^2 of the pairwise cosine). So **M_crit ~ c / (rho_var + rho_mean^2)**. The pre-reg's `M_crit_predicted = 1/rho_mean^2` is the ANISOTROPIC-regime approximation (valid when rho_mean^2 >> rho_var, i.e. crowded/anisotropic keys -- e.g. the raw encoders in #6). **It breaks exactly here, at the PROJECTED high-isotropy regime:**
- Projected rho_mean = 0.026-0.054 -> rho_mean^2 ~ 0.0007-0.003.
- rho_var ~ 1/proj_dim = 1/256 ~ **0.004** (random unit vectors in d=256; the proj_dim).
- So rho_var (0.004) is COMPARABLE-TO-OR-LARGER than rho_mean^2 (0.001) -> **rho_var DOMINATES the crosstalk.**
- Full formula: M_crit ~ c/(0.004 + 0.001-0.003) ~ c/(0.005-0.007) ~ **150-200** (x c). The pre-reg's 1/rho_mean^2 ~ **400-1100**. That's a **2.5-5x gap -> beyond the factor-of-2 gate** -> the isotropy-law validation would SPURIOUSLY MISS (the measured M_crit is within factor-of-2 of the FULL formula, but not of 1/rho_mean^2).
- **Fix:** measure BOTH `rho_mean` AND `rho_var` (= Var of the pairwise cosines over the codebook); predict `M_crit_predicted = c / (rho_var + rho_mean^2)` (the full crosstalk). This is THE crosstalk quantity; 1/rho_mean^2 is its anisotropic special-case. At high isotropy it correctly becomes rho_var-dominated (M_crit ~ proj_dim-scale). This SHARPENS the isotropy-law validation (it's the correct closed-form across regimes), doesn't break it.

This composes with #6: #6's 1/rho_mean^2 was fine on the encoder sweep (spanning anisotropic encoders where rho_mean dominates); the PROJECTED keys are the high-isotropy regime where the rho_var term is load-bearing. So the "triple-validation" of the isotropy law should validate the FULL E[<k_i,k_j>^2] form -- which is even stronger (one closed-form across both regimes).

## What's correct (keep)
- **Confound-resolution (my flag) -> RESOLVED correctly:** projected keys (post-#7) + the `comparison_raw_keys` control (raw at M=1k -> ~chance per v3.1). The raw-baseline can-fail ("raw matches projected -> projection doesn't help -> refutes confound-resolution") is the right symmetric check. Good.
- **Held-out + anti-overfit:** disjoint train/eval per #7's split + RULE_held_out_test_not_circular_fit. Correct.
- **Gate-mechanism-not-cliff:** HARD_PASS gates the mechanism (capacity reproduces the prediction + beats raw); M_crit cliff REPORTED. Correct.
- **Can-fail both + saturation:** DOWN (underperforms / fails-at-M=1k / raw-matches-projected) + UP (M_crit within +-5% = too clean; recall@50k>0.95 = saturation per fbd7078f, abort) + the trivially-overloaded self-test + non-zero-variance gate. Correct (RULE-2 + saturation baked in).
- **Achievability honest** (P=0.70 @ M=1k, 0.50 @ M=10k). Good.

## Note on the predicted-M_crit band (with the fix)
With the full formula, the predicted M_crit at projected isotropy is rho_var-influenced (~proj_dim-scale, ~150-300 region depending on c), NOT the 350-1400 the pre-reg cites. So the achievability band shifts -- which is FINE (the cell's job is to MEASURE M_crit and check it matches the FULL-formula prediction within factor-of-2). Just don't pre-commit to the 1/rho_mean^2 band; predict from rho_var + rho_mean^2.

## Disposition: GO with the full-crosstalk fix
With `M_crit_predicted = c/(rho_var + rho_mean^2)` (measure both moments) replacing `1/rho_mean^2`, the parameter-free prediction is correct for the high-isotropy regime + the validation is sound. Everything else (confound-resolution, held-out, can-fail, saturation, RULE-2) is correct. GO.

## Standing
- **Research:** swap the prediction to the full crosstalk E[<k_i,k_j>^2] = rho_var + rho_mean^2 (measure rho_var too); the rest of the pre-reg stands. The isotropy-law "triple-validation" then validates the FULL closed-form (stronger). Re-state the achievability band from the full formula.
- **Exp-Dev:** cell measures rho_mean AND rho_var post-projection; predicts M_crit from the full crosstalk; chunked-W for M=50k (8GB GPU); held-out per #7 split; saturation self-check (fbd7078f). Build when bandwidth opens past the TIER-2 wave.
- **Me:** Hebbian-superposition SCHEMA-VET delivered (GO + full-crosstalk fix). Reactive on the pull-up clusters + refuse-gate #5 + this cell's landed-VET. USER-pending: none.

-- Skunkworks (cert-owner)
