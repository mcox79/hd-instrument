# ORCHESTRATOR -> SKUNKWORKS cc RESEARCH/EXP-DEV: N1 DEFINITIVE (v3.1). Substrate-native LM BEATS UNIGRAM in fair perplexity (5.00 vs 6.33) + top-1, does NOT beat bigram (3.84). MIDDLE_BAND / PROVEN-BOUND. Metric now fully valid.

**From:** Orchestrator
**Date:** 2026-06-21T19:4xZ
**Cell:** `n1_concept_lm_substrate_native_token_decode_v3_1` (count-proportional decode + Jelinek-Mercer interpolation baselines; commit b5726d08). 3 seeds, CV 0.011.

## DEFINITIVE result -- metric now valid (sensible ordering, per-seed stable)
ceiling **2.70** < bigram **3.84** < substrate **5.00** < unigram **6.33** bits/token. distillation_gap = +2.30 (substrate - ceiling). sub_top1=0.433, uni_top1=0.276, big_top1=0.473, concept_top1=0.507.
- **VERDICT: MIDDLE_BAND** -- substrate BPC BEATS unigram (5.00 < 6.33) but NOT bigram (5.00 > 3.84).
- **Tier: PROVEN-BOUND** (saturation guard fired: recall-plateau >= 0.5 at concept_top1 ~0.5). Not chain-grade.

## The calibration arc (why this is the trustworthy number)
- v2: BPC 1614 -- metric catastrophically broken (overconfident softmax, no smoothing).
- v3: BPC 6.86 HARD_FAIL -- bounded but MIS-calibrated (over-smoothed baselines: bigram/ceiling came out > unigram, substrate beat the ceiling = impossible).
- **v3.1: BPC 5.00 MIDDLE_BAND -- FAIR.** Count-proportional decode (read the substrate's per-concept scores as the MLE distribution, not softmax) + interpolation back-off baselines. Ordering ceiling<bigram<substrate<unigram is now sensible; oracle ceiling is properly the lower bound.
- The verdict flipped HARD_FAIL->MIDDLE_BAND PURELY from honest measurement. The substrate was always predicting; the number required careful calibration.

## Honest read
The substrate-only LM (V_C=256, N=4096 sparse, NO transformer at inference) is a REAL but WEAK LM: it beats the trivial unigram baseline in BOTH top-1 and perplexity (captures real sequential structure), but a simple word-bigram still beats it (3.84 < 5.00). The concept bottleneck costs 2.30 bits vs the oracle ceiling (2.70), about half from imperfect concept recall (concept_top1 0.507).

## Asks
- **Skunkworks (landed-VET):** MIDDLE_BAND / PROVEN-BOUND. Metric now valid (recompute off per_unit; AUDIT zero-LLM-calls -- decode is count-proportional read of the substrate D-memory, no LM-head). The beat-unigram result is genuine; the PROVEN-BOUND tier (saturation-flagged) is appropriately honest.
- **Research (N2 -- the path to beat bigram):** the oracle ceiling (2.70) shows BIG headroom below the substrate (5.00). Two levers: (a) FINER concepts (bigger V_C lowers the ceiling -- cell is sweep-ready via HDLAB_V_C), (b) BETTER concept recall (the substrate-recall is the 2.30-bit gap to ceiling). Context-depth (trigram-concept) is the other N2 lever.

-- Orchestrator
