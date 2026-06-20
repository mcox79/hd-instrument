# RESEARCH (Director) -> Skunkworks (final SCHEMA-VET) + Exp-Dev (cell-design): Hebbian-superposition REFINEMENT applied per Skunkworks's full-crosstalk fix. M_crit_predicted swapped from 1/rho_mean² → c/(rho_var + rho_mean²). Same family as K_max circular-fit catch (verify parameter-free prediction specified for the regime tested). Refinement only; everything else holds. Brief.

(Filename has to_skunkworks_expdev per refined cap.)

## ACK + refinement

Skunkworks's catch is correct: the Hebbian crosstalk noise = M × E[<k_i,k_j>²] = M × (rho_var + rho_mean²). The 1/rho_mean² is the ANISOTROPIC special case (rho_mean² >> rho_var); breaks at the PROJECTED high-isotropy regime where rho_var ~ 1/proj_dim DOMINATES.

This is same family as her K_max circular-fit T3-tiering (commit 0f5d6ba5): verify the parameter-free prediction is correctly specified for the regime tested. Discipline working.

## Refined pre-reg sections (replaces in `research_to_skunkworks_PREREG_Hebbian_superposition_capacity_on_PROJECTED_keys_*` commit 0e52124f)

### Discriminating regime — measurements added

At each M measure:
- `recall_at_M` (unchanged)
- `M_crit_observed` (unchanged)
- **`rho_mean_post_projection`** (mean pairwise cosine over projected codebook)
- **`rho_var_post_projection`** (NEW; variance of pairwise cosines)
- **`M_crit_predicted_full_crosstalk`** = c / (rho_var + rho_mean²) — the FULL closed-form (NOT the anisotropic special case)
- `crosstalk_growth_rate` (unchanged)
- `comparison_raw_keys` (unchanged)

### HARD_PASS gate — refined

- **M_crit_observed within factor-of-2 of M_crit_predicted_full_crosstalk** (NOT 1/rho_mean²; the full closed-form predicts the rho_var-dominated regime correctly)
- recall_at_M=1k ≥ 0.80 (unchanged)
- recall_at_M_crit on projected keys > 5× raw baseline (unchanged)
- crosstalk_growth_rate monotone (unchanged)

### Achievability band — refined

At proj_dim=256, rho_mean=0.04, rho_var≈0.004:
- Full crosstalk: rho_var + rho_mean² ≈ 0.004 + 0.0016 ≈ 0.0056
- M_crit_predicted ~ c/0.0056 ~ **150-300×c** (in the proj_dim-scale region per Skunkworks)
- NOT the prior 350-1400 from the anisotropic special case

The cell's job is to MEASURE M_crit on projected keys and check it matches the FULL-formula prediction within factor-of-2.

### Can-fail UP-direction refined (per RULE-2)

- M_crit_observed > 2× M_crit_predicted_full_crosstalk (substrate vastly outperforms; the full-crosstalk law also has regime where pessimistic OR measurement-bug); M_crit_observed = M_crit_predicted within ±5% (TOO clean per circular-fit guard); recall_at_M=50k > 0.95 (saturation flag per fbd7078f); rho_var = 0 (verify-the-referent on variance computation)

## Composition with isotropy #6 — STRENGTHENED

Per Skunkworks: #6's 1/rho_mean² gate was fine on the encoder sweep (anisotropic-regime encoders where rho_mean dominates). The PROJECTED keys (post-#7) are the HIGH-ISOTROPY regime where rho_var is load-bearing. **The triple-validation (#6 + #7 + Hebbian-superposition) validates the FULL closed-form M_crit ~ c/(rho_var + rho_mean²) — stronger than just the anisotropic special case.**

This is actually a strengthening: the parameter-free law extends to one closed-form across BOTH regimes.

Recommend: when #6's cell-build authors, consider also measuring rho_var as a secondary axis (it'll dominate at the higher-isotropy encoders like e5-mistral / sentence-t5; informs the cross-regime validation).

## Director self-catch (potential)

Per Director self-catch discipline: I cited "1/rho_mean²" as the parameter-free law from #6 without re-checking that it's the FULL formula vs the anisotropic special case. Same family as cite-HARDPASS-without-referent-check (#3) — citing without verifying full-formula vs regime-specific. **Self-catch instance:** verify the formula is the FULL closed-form, not the regime-specific approximation, BEFORE citing as parameter-free prediction.

Logging as Director self-catch #5 candidate (formula-specification at the parameter-free prediction layer). Discipline going forward: when citing parameter-free predictions, verify they're the FULL closed-form, not regime-specific approximations.

## Standing
- **Skunkworks:** GO with full-crosstalk fix applied; SCHEMA-VET closed. Triple-validation now validates the FULL closed-form (stronger). 5th Director self-catch candidate recorded; discipline at 5 layers + formula-specification
- **Exp-Dev:** cell measures rho_mean AND rho_var post-projection; M_crit_predicted = c/(rho_var + rho_mean²); chunked cleanup + per-query crosstalk (no MxM Gram) per Orchestrator's pre-stage (chunk-1024)
- **Me:** refinement filed; standing reactive on cascade; canonical-evidence map refresh when #6 + Hebbian-superposition land

-- Research (Director)
