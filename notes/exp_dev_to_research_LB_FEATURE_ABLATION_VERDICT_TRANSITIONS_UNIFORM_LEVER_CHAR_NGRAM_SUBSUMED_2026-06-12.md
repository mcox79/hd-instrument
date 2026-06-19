# Exp-Dev -> Research: L-B Ablations 1+2 VERDICT -- BIO transitions are a UNIFORM +0.09 lever (HARD-PASS); char n-grams are SUBSUMED (no lift)

**From:** Exp-Dev  **Date:** 2026-06-12 (Day 4 Cycle 50)  **Cell:** exp_ner_feature_ablation_cpu_v1  **Lane:** local_cpu_queue (done)
**Frame:** substrate-property; NO LLM comparison.

## Result (paired variants, 4-type CoNLL, 3 seeds)

| train frac | baseline | no_transition | char_ngram | transition contrib | char n-gram lift |
|---|---|---|---|---|---|
| 5pct  | 0.4120 | 0.3262 | 0.4024 | **+0.0858** | -0.0096 |
| 10pct | 0.4915 | 0.3999 | 0.4819 | **+0.0916** | -0.0096 |
| 100pct| 0.6441 | 0.5464 | 0.6366 | **+0.0977** | -0.0075 |

## Verdict
- **Ablation 1 (transition contribution): HARD-PASS.** baseline - no_transition = +0.086 / +0.092 / +0.098 -- all well above
  the pre-reg +0.05@5pct bar. The existing BIO->BIO transition features + Viterbi decoding contribute ~+0.09 F1.
- **Ablation 2 (char n-gram): HARD-FAIL (negative lift).** char_ngram - baseline = -0.0096 / -0.0096 / -0.0075 at every
  fraction. Char 3/5-gram features are SUBSUMED by the existing shape + prefix3 + suffix1-4 features; adding them injects
  redundant, slightly-harmful signal. (The cell's absolute-band verdict reads MIDDLE only because 0.4024 lands in 0.40-0.43;
  the LIFT is negative -- the honest read is char n-grams do not help.)

## The finding that matters: two CONTRASTING mechanism profiles
This ablation suite + the gazetteer ablation give three distinct substrate-property mechanism shapes:
1. **BIO transitions / Viterbi structured prediction: UNIFORM lever.** ~+0.09 at 5pct, 10pct, AND 100pct -- contribution
   does NOT shrink with data (if anything grows slightly +0.086 -> +0.098). Structured prediction is a scale-invariant
   architectural lever, not a low-data crutch. Removing it (memoryless emissions) costs ~0.09-0.10 F1 everywhere.
2. **External gazetteer: LOW-DATA lever, liability at scale.** +0.044 @5pct -> -0.037 @100pct (sign flip). Discrete
   external prior knowledge helps only when learned lexical features are still sparse.
3. **Char n-grams: SUBSUMED.** no lift at any scale -- redundant with existing shape/affix features.

Substrate-product positioning (stands alone, no LLM frame): "Substrate-classical NER's lift comes from STRUCTURED
PREDICTION (Viterbi + learned BIO transitions, ~+0.09 F1 scale-invariant), not from feature piling. Discrete external
features (gazetteers) are a low-data-only lever that inverts at scale; sub-word char n-grams are subsumed by shape/affix
features. The architectural lever is the sequence model, not the feature count."

## L-B mechanism-deepening: COMPLETE (3 of 3 ablations done)
- Ablation 3 external gazetteer: MIDDLE, low-data-win sign-flip (separate note).
- Ablation 1 transitions: HARD-PASS uniform +0.09 lever (this note).
- Ablation 2 char n-gram: HARD-FAIL subsumed (this note).

## Routing
- **Exp-Dev:** L-B mechanism deepening COMPLETE. gap4v2 280-atom done (0.2966 MIDDLE, caveated). C-D4 deferred (path c).
  No authorized GPU work pending (gap4v2 was the GPU pick; batch-2 re-measure gated on Testbed ingest). Standing by.
- **Research:** 3 ablation verdicts for verdict_handler. Methodology candidate: substrate NER lift is sequence-model-bound,
  not feature-bound -- feature engineering past shape/affix/transitions has diminishing-to-negative return.
