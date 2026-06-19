# Pre-registration: external-gazetteer x char-noise cross-cut (RESCUE-1)

**Date:** 2026-06-12 (Day 4 Cycle 50)
**Cell:** experiments/exp_ner_gazetteer_noise_crosscut_cpu_v1.py
**Routing:** strategy_request_to_exp_dev_2026-06-12_gazetteer_char_noise_cross_cut (PP-403 cap_map v577). Substrate-quality-first; NO LLM frame.
**Lane:** local_cpu_queue (laptop CPU; dashboard-visible)

## Hypothesis
External-gazetteer binary membership features are MORE noise-robust than char-surface lexical/affix features, so the
gazetteer LIFT (gaz - baseline) should hold up or GROW under char-level test noise -- compounding the PP-403 low-data-win
with a noisy-text robustness story.
Honest caveat: gazetteer membership is EXACT-MATCH on the (noised) lowercased token, so it ALSO degrades when noise
corrupts a gazetteer word. The empirical question is whether it degrades SLOWER than the features it supplements.

## Design
{baseline, +ext-gazetteer} x {clean, noisy@10pct char-perturb} x {5pct, 100pct} train fraction, 3 seeds. Test-time char
noise (L-A _char_perturb) with a FIXED noise realization per (frac,seed) so baseline and gaz see the same perturbed test
(clean paired lift). Training on clean text (noise is adversarial test-time only). 4-type CoNLL collapse. Gazetteers
identical to PP-403 (PER=198/LOC=207/ORG=129).

## Pre-registered verdict bands (headline = lift@5pct delta = lift_noisy - lift_clean)
- **HARD-PASS:** lift@5pct_noisy >= lift@5pct_clean + 0.02 (gazetteer compounds with noise robustness)
- **MIDDLE:** delta in [-0.02, +0.02] (gazetteer noise-invariant; robust but not compounding)
- **HARD-FAIL:** delta < -0.02 (gazetteer degrades under noise; robustness claim refuted)
- **UNKNOWN:** data load fails

## Substrate-product artifact (stands alone, no LLM frame)
Whether substrate's discrete external-feature-library lever extends to the noisy-text regime, and the interaction
between the low-data-win and char-noise robustness of discrete membership features vs surface lexical features.
