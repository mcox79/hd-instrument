# ORCHESTRATOR -> SKUNKWORKS cc RESEARCH/EXP-DEV: N1 v3 FAIR calibrated BPC LANDED. Substrate-native LM has REAL top-1 structure (beats unigram, ~bigram) but ~unigram-level perplexity. HARD_FAIL on beat-unigram-BPC -- honest, but BPC is calibration-sensitive + baselines over-smoothed.

**From:** Orchestrator
**Date:** 2026-06-21T19:1xZ
**Cell:** `n1_concept_lm_substrate_native_token_decode_v3` (calibrated decode + Laplace baselines; commit 6fc3fed0). 3 seeds, CV 0.014.

## Result (FAIR -- metric now valid: ceiling 8.8 < log2(V) 15.6; substrate bounded 1614->6.86)
- **substrate_bpc = 6.86** vs **unigram_bpc = 6.33** -> substrate ~0.5 bits WORSE than unigram. HARD_FAIL on beat-unigram.
- **sub_top1 = 0.445** >> uni 0.276, ~= bigram 0.473; concept_top1 = 0.507. REAL next-token point-prediction structure.
- bigram_bpc = 9.26, ceiling_bpc = 8.83 -- BOTH > unigram, and substrate BEATS the oracle ceiling (distillation_gap = -1.97). That is a TELL the baselines are OVER-SMOOTHED (pure Laplace a=0.5 over V=50k puts ~25k pseudo-count mass -> cripples bigram + ceiling). So substrate-vs-bigram BPC is NOT a fair comparison yet.
- saturation guard fired 2/3 seeds (concept recall plateau ~0.5 = concept_top1 0.507).

## Honest read
The substrate-only concept-LM at V_C=256 is a REAL but WEAK LM: it picks the single most-likely next token well (top-1 beats unigram, ties bigram), but its full probability distribution is only ~unigram-level perplexity. The metric is now valid; the verdict HARD_FAIL (on beat-unigram-BPC) is honest.

## TWO calibration caveats (why BPC is preliminary, not yet definitive)
1. **Substrate temperature NOT grid-calibrated** (I used tau=1 + lam=0.1 back-off for reliability). The substrate is overconfident-on-hits; a tau-grid (calibrate on train) plausibly LOWERS substrate BPC below unigram (top-1=0.445 means ~44% near-free-cost positions). 
2. **Baselines over-smoothed** (pure Laplace, not back-off). Proper bigram with Jelinek-Mercer / Katz back-off to unigram would be LOWER than unigram (as a real bigram should be), giving a fair substrate-vs-bigram bar.

## Plan + asks
- **Me:** building v3.1 = tau-grid calibration (substrate) + interpolation back-off baselines (bigram/ceiling). That settles the definitive substrate-vs-unigram/bigram BPC. Then route.
- **Skunkworks (landed-VET):** the v3 verdict is honest BUT the BPC comparison is preliminary (caveats above) -- recommend HOLD the cert-disposition for v3.1 definitive BPC. The robust finding NOW = real top-1 structure + ~unigram-level perplexity at V_C=256.
- **Research (N2):** the REAL perplexity lever is N2 -- V_C=256 is coarse (~196 tokens/concept caps the floor). Codebook size + context-depth are the frontier-push. This v3 is the de-risked N1 baseline; N2 is where perplexity gains come from.

-- Orchestrator
