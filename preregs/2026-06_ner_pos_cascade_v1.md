# Prereg: ner_pos_cascade_cpu_v1

**Date:** 2026-06-11
**Lane:** CPU (local_cpu_queue)
**Routing:** Research Path 3 (cascade NER via the substrate POS tagger).

## Motivation
NER feature levers: decoder (Path 1) -0.012; in-corpus Brown clusters (Path 2) +0.011. The NER feature set has NO POS feature,
yet POS is classically one of the strongest NER features and the substrate has a 0.95 POS tagger. Cascade predicted POS into NER.

## Method
Train structured-perceptron POS tagger on UD-EWT (17 universal tags); predict POS for every OntoNotes token; add POS features
(pos / prev-pos / next-pos / pos+shape) to NER emission. Train TWO NER models from identical base features: no-POS (= baseline
0.5817) vs +POS-cascade. Report lift. Substrate-only.

## Pre-registered verdict (NO defeat)
- HARD_PASS: F1 >= 0.62 AND lift >= 0.02 (POS cascade is a real lever).
- MIDDLE_BAND: lift in [0.005,0.02).
- HARD_FAIL: lift < 0.005.

Smoke (300 train): no-POS 0.466 -> +POS 0.544, lift +0.0785 -- strong; full run decisive.
