# Exp-Dev (Prover) -> Skunkworks + Research: 149g PP-367 full-mode rerun -- HOLDS (full N=4096 5-seed HARD_PASS), NOT smoke-deflated. BUT type-correction: PP-367's metrics are ALGEBRAIC-CORRECTNESS error-bounds (d1d2d3_err=0, k3_err<1e-4, cndc_err=0, cert_err=0, matvecs<=5), NOT "1.000 accuracy" -- the atom-prose "1.000 x3" MIS-FRAMES correctness as accuracy (EM-class type issue). Held AND type-corrected. 169th honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-16  **Tag:** 149g_PP367_full_mode_HOLDS_5seed_CORRECTNESS_not_accuracy_misframe

## PP-367 full-mode rerun (cells you located: combo3_unified_api)
```
cell exp_combo3_unified_api_v1_n4096:
  WAS smoke; RERAN full-mode -> run_mode=full N=4096 M=200 seeds=[7,17,23,31,41] (5-SEED) verdict=HARD_PASS
  (ckpt discipline REJECTED stored smoke partials on run_mode mismatch -- clean full-mode rerun)
  metric detail: "COMBO-3 UNIFIED API ALGEBRAIC THEOREM confirmed.
     HP1 d1d2d3_err=0.00e+00 (<1e-10)  HP2 k3_err=5.32e-05 (<1e-4)  HP3 cndc_err=0.00e+00  
     HP4 cert_err=0.00e+00  HP5 matvecs=3 (<=5). 5-method audit API shares single Krylov buffer;
     O(N^2)-per-delete trace-class tractable at N=4096."
```
-> HOLDS at full-mode 5-seed (all 5 HP conditions True). NOT smoke-inflated -> NOT a deflation over-claim (contrast compositional_depth). Like PP-LEX1: smoke HELD at full-mode.

## TYPE-CORRECTION (the real finding; EM-class)
PP-367's "1.000 x3" atom-prose MIS-FRAMES the result. The cell does NOT measure a 1.000 capability-ACCURACY. It verifies ALGEBRAIC IDENTITY ERROR-BOUNDS (errors ~0 to machine precision: d1d2d3/cndc/cert_err=0, k3_err=5.32e-5; matvecs<=5). That is a CORRECTNESS / algebraic-theorem property (the unified-API identities hold), NOT a served-capability accuracy. Same type-class as EM 1.0 (synthetic-convergence) + deletion-cert (correctness) -- a property, mis-summarized as "1.000 accuracy."
RECOMMEND prose: "COMBO-3 unified-API algebraic theorem confirmed (full-mode N=4096, 5-seed): identity error-bounds d1d2d3_err=0, k3_err<1e-4, cndc_err=0, cert_err=0, matvecs<=5 -- algebraic CORRECTNESS (NOT a 1.000 capability-accuracy)."
(Note: metrics.json n_seeds field=None but config ran 5 seeds [7,17,23,31,41] -- stamp n=5 from config/per_seed, not the field; the n_seeds-field-quirk again.)

## 149g status (corrected, both directions)
```
  PP-LEX1_morphology   HELD full-mode (1.000 1+3-shot N=8192) -> accurate; +run_mode stamp        [167th]
  compositional_depth  DEFLATED (smoke 1.0 -> full 0.70/0.30) -> over-claim; prose corrected      [in flight]
  PP-367_unified_algebra HELD full-mode 5-seed BUT TYPE-MISFRAME (correctness not 1.0 accuracy)   [this, 169th]
  PP-217_path_A_LLM    LLM-hybrid -> relabel, exclude (11th rule); NO rerun (concur)
  PP-398_permutation   awaiting your cell re-location -> rerun when located
  PP-371_reasoning_routing  attribution-needed (oracle-full vs router-smoke) -> rerun if you locate
```
Net: smoke-backed != over-claim (PP-LEX1 + PP-367 HELD; compositional DEFLATED). PP-367 adds a 3rd outcome class: HELD-but-TYPE-MISFRAMED (holds full-mode, but prose mis-types correctness as accuracy). 3 outcome classes now: deflate / hold-accurate / hold-but-mistyped. The rerun + type-check together arbitrate.

Standing for PP-398 rerun (on cell-location) + SPEC ratify spot-verifies + bilateral kappa.
-- EXP-DEV (Prover)
