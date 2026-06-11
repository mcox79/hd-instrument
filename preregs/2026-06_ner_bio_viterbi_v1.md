# Prereg: ner_bio_viterbi_cpu_v1

**Date:** 2026-06-11
**Lane:** CPU (local_cpu_queue)
**Routing:** research_to_exp_dev_NER_BIO_VITERBI_CHEAP_DECISIVE_2026-06-11 (NER Path 1)

## Motivation
Research hypothesis: NER 0.58 F1 is an unstructured-decode FLOOR; a BIO-constrained structured decoder lifts it (target >=0.65).
HONEST CORRECTION (verify-before-invest): the existing NER cell ALREADY uses structured-perceptron Viterbi with learned (Collins)
transitions -- NOT per-token argmax. The genuinely untested lever is HARD BIO CONSTRAINTS (mask illegal transitions to -inf).

## Method
Train TWO models from IDENTICAL features on bundled OntoNotes (18-type, 35 tags; harder than the note's CoNLL-2003 4-type):
- A: unconstrained Viterbi (= current baseline, expect ~0.58 at full data).
- B: hard-BIO-constrained Viterbi (O->I-X, B-X->I-Y, I-X->I-Y[Y!=X], START->I-X all masked to -inf).
Isolates exactly the BIO-constraint lever. Report B's F1 and lift = B - A.

## Pre-registered verdict (decisive; NO pre-registered defeat per drill-defeatism)
- HARD_PASS: B >= 0.65 (BIO-constraint is the missing lever; stack Path 2-5).
- MIDDLE_BAND: B in [0.58,0.65) OR lift >= 0.03.
- HARD_FAIL: B < 0.58 (constraint broke emissions) OR |lift| < 0.01 (soft transitions already encode BIO; bottleneck is
  features/benchmark, report back to Research and pursue Path 2 richer features).

Smoke (300 train) preview: A=0.466, B=0.457, lift=-0.009 -- preliminary "soft transitions already encode BIO"; full run decisive.
