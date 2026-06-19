# Pre-registration: transition-contribution & char-n-gram UNDER char-noise (Compound A+B)

**Date:** 2026-06-12 (Day 4 Cycle 50)
**Cell:** experiments/exp_ner_transition_charngram_noise_crosscut_cpu_v1.py
**Routing:** strategy_request_to_exp_dev_2026-06-12_LB_complete_three_shape_typology (Cycle 243 v578, Research-invited Compounds A+B). Substrate-quality-first; NO LLM frame.
**Lane:** local_cpu_queue (laptop CPU; dashboard-visible)

## Hypotheses
- **Compound A (valuable):** the PP-404 BIO-transition contribution (+0.09 scale-invariant clean) PRESERVES or GROWS under
  char-level test noise, because BIO label legality (B-before-I, type consistency) is invariant to emission-level char noise.
  If so, the sequence model is BOTH the scale-invariant lever AND the noise-robustness lever -- while the gazetteer lift
  SHRINKS under noise (PP-403 RESCUE-1 cross-cut, HARD_FAIL delta -0.027). Discrete features are neither; the sequence model is both.
- **Compound B:** the PP-405 char-n-gram lift (~0 clean, subsumed) goes MORE negative under noise (5-gram membership is
  high-precision/low-recall and noise-sensitive): subsumed-clean -> harmful-under-noise.

## Design
variants {baseline, no_transition, char_ngram} x noise {clean, 10pct} x frac {5pct, 100pct}, 3 seeds. EFFICIENT: train ONCE
per (variant, frac, seed) on CLEAN text; evaluate the SAME model at both noise levels (training is the cost; noise is
test-time only). Fixed noise realization per (frac,seed) -> paired. 4-type CoNLL collapse.

## Pre-registered verdict bands (headline = Compound A: trans_contrib@5pct delta = noisy - clean)
- **HARD-PASS:** delta >= -0.01 (transition contribution preserved/grows under noise -> sequence model is the noise-robustness lever)
- **MIDDLE:** delta in [-0.03, -0.01)
- **HARD-FAIL:** delta < -0.03 (transitions degrade like lexical features)
- Compound B (char-n-gram lift clean vs noisy): reported as annotation, not gated.
- **UNKNOWN:** data load fails

## Substrate-product artifact (stands alone, no LLM frame)
Whether substrate-classical NER's primary lever (structured prediction) carries its advantage into the noisy-text regime,
completing the three-shape typology x noise cross-cut (gazetteer noise-fragile; transitions noise-robust?; char n-gram harmful).
