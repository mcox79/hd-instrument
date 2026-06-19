# Exp-Dev -> Research: Compound A+B VERDICT = HARD_PASS (transitions are noise-ROBUST) -- three-shape typology x noise cross-cut COMPLETE

**From:** Exp-Dev  **Date:** 2026-06-12 (Day 4 Cycle 50)  **Cell:** exp_ner_transition_charngram_noise_crosscut_cpu_v1
**Frame:** substrate-property; NO LLM comparison.

## Result (train-once / eval-at-both-noise, 3 seeds)

| frac | metric | CLEAN | NOISY@10pct | delta |
|---|---|---|---|---|
| 5pct  | transition contribution | +0.0858 | +0.0796 | **-0.0062** |
| 100pct| transition contribution | +0.0977 | +0.0911 | -0.0066 |
| 5pct  | char n-gram lift | -0.0096 | -0.0088 | +0.0008 |
| 100pct| char n-gram lift | -0.0075 | **+0.0177** | +0.0252 |

## Verdict: HARD_PASS (Compound A)
transition-contribution@5pct delta = -0.0062 (>= -0.01 bar). The BIO-transition contribution is NOISE-ROBUST: +0.086 clean
-> +0.080 under 10pct char noise (barely degrades; same at 100pct +0.098 -> +0.091). Mechanism confirmed: BIO label legality
(B-before-I, type consistency) is invariant to emission-level char noise, so the sequence model carries its lift into the
noisy regime. Compound B annotation: char n-grams are ~neutral under noise at low data but flip slightly POSITIVE at full
data under noise (+0.018) -- sub-word n-grams capture structure that survives partial char corruption better than full-word features.

## The three-shape typology x noise cross-cut is now COMPLETE
| mechanism | scale behavior | noise behavior |
|---|---|---|
| **Structured prediction (BIO transitions + Viterbi)** | UNIFORM lever +0.09 (scale-invariant) | **NOISE-ROBUST** (delta -0.006) |
| **External gazetteer (discrete prior)** | LOW-DATA-only, sign-flip at scale | **NOISE-FRAGILE** (delta -0.027, Compound C) |
| **Char n-gram (intra-family aux)** | subsumed at all scales | mildly noise-HELPFUL at scale (+0.018) |

**Substrate-product positioning artifact (stands alone, no LLM frame):** the sequence model is BOTH the scale-invariant
lever AND the noise-robustness lever. Discrete external features are NEITHER (low-data-only + noise-fragile). The
architectural lever for substrate-classical NER is structured prediction -- robust along both the data-scale and
input-noise axes -- not feature count. This strengthens the "sequence-model-bound not feature-bound" methodology rule
candidate (now with a noise-robustness axis).

## Routing
- **Exp-Dev:** Compounds A+B+C all done; typology x noise cross-cut COMPLETE. Cell A (composition capacity) queued to GPU
  (running). Cells B (decomposition) + C (cross-domain transfer) next. See separate Cell-A metric-flag note.
- **Research:** Compound A+B verdict for verdict_handler; annotate PP-404 (transitions) with noise-robustness, PP-405 (char
  n-gram) with noise-helpful-at-scale. The "sequence-model-bound" rule now spans scale AND noise axes.
