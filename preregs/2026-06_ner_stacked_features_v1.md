# Prereg: ner_stacked_features_cpu_v1

**Date:** 2026-06-11
**Lane:** CPU (local_cpu_queue)
**Routing:** complete NER feature program -- stack Path 2 (clusters) + Path 3 (POS) features.

## Motivation
Individually at full data: Brown clusters +0.011, POS cascade +0.013. Do the small gains ADD or saturate? Stack both on the
structured-perceptron NER for the best-achievable IN-CORPUS substrate NER. OntoNotes 18-type, substrate-only.

## Method
Train UD POS tagger + build in-corpus clusters; NER with base vs stacked (cluster-id + predicted-POS + pos*cluster) features.
A/B from identical base features. Report stacked F1 + lift vs 0.5817.

## Pre-registered verdict (NO defeat)
- HARD_PASS: F1 >= 0.62 AND lift >= 0.025 (gains add).
- MIDDLE_BAND: lift 0.01-0.025 (partial; features saturate; external resources needed to break ~0.66).
- HARD_FAIL: lift < 0.01 (full saturation).

Smoke (300 train): baseline 0.466 -> stacked 0.542 (+0.076); full run decisive (expect ~+0.02 = saturation).
