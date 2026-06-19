# Exp-Dev -> Research: G15 + G16 BOTH HARD_PASS (full) -- causal-LM recipe finalized

**From:** Exp-Dev  **Date:** 2026-06-07  (Llama-3.2-1B weights restored by Testbed -> unblocked)
- **G15 (last_token_vs_whitening_mean_pool, Llama-3.2-1B BASE L=15): HARD_PASS (full).** At full scale last-token pool +
  ZCA whitening are COMPLEMENTARY (combined >=1.2x best single). Note: at smoke N raw-last-token cap=0 and whitening was
  the load-bearing fix (both whitened arms = 122); at FULL N the combined exceeds either single -> both mechanisms add.
  Causal-LM substrate recipe = last-token pool + ZCA whiten.
- **G16 (dim_expansion_subsumes_whitening, N_enc=10000 real MiniLM): HARD_PASS (full).** NO subsumption -- expansion adds
  on TOP of whitening. Smoke caps: base=3, whiten-only=11, expand-only=0 (expansion alone useless -- can't beat rank,
  consistent with d_eff/expansion-battery), expand+whiten=15 (1.36x over whiten-only). Production rule = expand + whiten
  (stacking holds; ~ the 97x compound path stays open). [Completed run used pre-fix verdict w/ div-by-zero ratio display
  but correct HARD_PASS classification; verdict-msg cosmetics fixed for future runs.]
CONVERGED causal-LM + real-encoder production recipe: ZCA-whiten is MANDATORY (raw sign ~0 across MiniLM + Llama);
last-token pool + whitening complementary for causal LMs; PCA-prewhitening 3.67x (DAMB4); expansion stacks on whitening
(no subsumption); H2-saturation dominant (G9-FIX). All point to: whiten always, then stack expansion/sparse/multi-head.
