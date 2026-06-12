# Pre-registration: NER feature ablation (L-B mechanism deepening, Ablations 1+2)

**Date:** 2026-06-12 (Day 4)
**Cell:** experiments/exp_ner_feature_ablation_cpu_v1.py
**Routing:** research_to_exp_dev_L_B_REROUTE...MECHANISM_DEEPENING (substrate-quality-first; NO LLM frame)
**Lane:** local_cpu_queue (laptop CPU; dashboard-visible)

## Honest correction to routing premise
Research's Ablation 1 assumed the substrate NER is "memoryless emissions". It is NOT: the harness already
has tag-bigram transition features tt(prev,tag) + full Viterbi. So Ablation 1 is reframed as a
TRANSITION-CONTRIBUTION ablation (transitions ON vs OFF). Ablation 2 (char-CNN) -> substrate-classical
discrete char 3/5-gram membership features.

## Variants (paired at each fraction, same subset/seed)
- baseline: emit-features + tt transitions + Viterbi
- no_transition: emissions only, independent per-token argmax (memoryless)
- char_ngram: baseline + char 3-gram and 5-gram features inside each word
Fractions {5pct, 10pct, 100pct} x 3 seeds. 4-type CoNLL collapse (comparable to L-B curve 0.404/0.501/0.644).

## Pre-registered verdict bands (substrate-property; no LLM comparison)
- **Transition contribution:** HP if baseline - no_transition >= +0.05 at 5pct (structured-prediction is a real low-data lever).
- **Char n-gram (headline):** HARD-PASS char_ngram F1@5pct >= 0.43 (+0.03 over baseline) AND lift@5pct > lift@100pct (low-data-win).
  MIDDLE 0.40-0.43. HARD-FAIL < 0.40. UNKNOWN if data load fails.

## Substrate-product artifact (stands alone, no LLM frame)
(1) What the existing BIO-transition structure contributes to substrate-classical NER, especially at low data;
(2) whether discrete char n-gram morphology features are a low-data lever or are subsumed by existing shape/affix features.
