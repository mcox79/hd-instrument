# Pre-registration: RESCUE-3 cross-domain NER transfer (CoNLL-2003 -> OntoNotes)

**Date:** 2026-06-12 (Day 4 Cycle 50)
**Cell:** experiments/exp_substrate_crossdomain_transfer_conll2003_ontonotes_ner_cpu_v1.py
**Routing:** strategy_request RESCUE-3 (2nd-appearance hook, cross-domain discriminative-weighting rule). Substrate-quality-first; NO LLM frame.
**Lane:** local_cpu_queue (CoNLL-2003 via raw GitHub mirror; env-gated UNKNOWN if download fails).

## Design
Train discriminative_perceptron (structured perceptron + Viterbi) NER on CoNLL-2003 (Reuters news, source) -> warm-start
transfer to OntoNotes NER (mixed-genre, target) vs train-from-scratch, at target fractions {1,2.5,5,10,100}pct, 3 seeds. Both
collapsed to the same 4-type CoNLL scheme (PER/ORG/LOC/MISC) -> shared feature + tag space for warm-start. Caps: 3000 src,
3000 tgt-train, 1000 tgt-test. Reports transfer F1, scratch F1, ratio, + zero-shot CoNLL-on-OntoNotes F1.

## Pre-registered bands (RESCUE-1 methodology: steepest slope 1-5pct; headline = ratio@2.5pct)
- **HARD-PASS:** ratio@2.5pct >= 1.20 (positive cross-domain NER transfer; discriminative lever generalizes NER across domain -- non-sentiment 2nd appearance).
- **MIDDLE:** ratio 0.95-1.20.
- **HARD-FAIL:** ratio < 0.95 (negative transfer).
- **UNKNOWN:** CoNLL-2003 download fails.

## Substrate-product artifact (stands alone, no LLM frame)
Whether the substrate discriminative_perceptron primitive shows positive cross-domain transfer on a NON-SENTIMENT
sequence-labeling task (NER, Reuters -> mixed-genre), as a 2nd-appearance hook for the cross-domain low-data-lever rule.
