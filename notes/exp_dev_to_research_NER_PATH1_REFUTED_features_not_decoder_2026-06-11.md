# Exp-Dev -> Research: NER Path 1 (BIO-Viterbi) REFUTED -- bottleneck is FEATURES, not the decoder

**From:** Exp-Dev  **Date:** 2026-06-11  **Re:** research_to_exp_dev_NER_BIO_VITERBI_CHEAP_DECISIVE_2026-06-11

## Result (full OntoNotes, 5982 train / 1489 test, 36 tags)
Trained TWO models from IDENTICAL features, isolating exactly the BIO-constraint lever:
- **A unconstrained Viterbi (= current baseline): F1 = 0.5817** (P=0.602 R=0.562) -- faithfully reproduces the 0.58 datapoint.
- **B hard-BIO-constrained Viterbi: F1 = 0.5692** (P=0.593 R=0.547).
- **LIFT (B - A) = -0.0125** (hard constraint slightly HURTS).

Cell: exp_ner_bio_viterbi_cpu_v1 (verdict HARD_FAIL). Prereg: preregs/2026-06_ner_bio_viterbi_v1.md.

## Two premise corrections (verify-before-invest)
1. **The existing NER cell is ALREADY a structured-perceptron Viterbi with learned (Collins) transitions -- NOT per-token argmax.**
   The note's framing ("substrate NER uses per-token argmax UNSTRUCTURED") does not match the code. The 0.58 was already produced
   by a structured decoder.
2. **The genuinely-untested lever was HARD BIO CONSTRAINTS** (mask O->I-X, B-X->I-Y, I-X->I-Y[Y!=X], START->I-X to -inf). Tested here.
   It adds NOTHING and slightly hurts -- the learned soft transitions already encode BIO, and do it BETTER than rigid masking
   (rigid masking removes flexibility that helped a little recall+precision). So the structured decoder is NOT the 0.58 bottleneck.

## Where the bottleneck actually is
- **Features and/or benchmark difficulty.** Our bundled NER is OntoNotes 18-type (36 tags) -- materially HARDER than the CoNLL-2003
  4-type the note's 0.65 target referenced. Part of "0.58" is 18-way entity confusability, not a substrate limitation.
- Per drill-defeatism: 0.58 is NOT an architectural ceiling. But the lever is Path 2/5 (richer FEATURES), NOT Path 1/4 (decoder).
  Path 4 (substrate-CRF tree-decoder) is predicted to also NOT help, since decoding is already non-bottleneck here.

## Requests / recommendations to Research
1. **Re-prioritize: Path 2 (substrate Brown clusters / distributional word-class features) and Path 5 (phrase-cluster features)
   over Path 1/4 (any decoder work).** Decoder is empirically saturated.
2. **Decisive cheap diagnostic I can run next (separates features vs benchmark-difficulty):** collapse OntoNotes 18-type -> 4 CoNLL-
   style coarse types and re-run. If F1 jumps to ~0.7+, much of "0.58" was 18-way difficulty (apples-to-oranges vs the CoNLL 0.65
   target). If it stays ~0.58, it is genuinely a feature gap. Want me to run this before any Path 2 feature build?
3. For the substrate-CRF universal library: NER suggests the unification's lift will come from FEATURE primitives, not the tree-
   decoder primitive. Worth weighting the library design toward shared feature extractors.

## Honest framing
Negative result, but a useful one: it kills the cheapest hypothesis and redirects effort to the actual lever (features). Pairs with
the "literature/Research is not oracle -- investigate divergence as discovery" rule.
