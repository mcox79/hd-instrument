# Prereg: ner_brown_cluster_cpu_v1

**Date:** 2026-06-11
**Lane:** CPU (local_cpu_queue)
**Routing:** Research Action 2 (research_to_exp_dev_NER_PATH1_REFUTED_FEATURES_NEXT_2026-06-11) -- Path 2 features.

## Motivation
NER diagnostics: caps ~0.65 regardless of type granularity (18-type 0.582 / 4-type CoNLL 0.648 / single-type boundary 0.664);
decoder non-bottleneck (hard-BIO lift -0.012). Lever = FEATURES. Path 2: distributional word-cluster (Brown-style) features
computed IN-CORPUS (substrate-native, no external embeddings).

## Method
Word -> feature-hashed context vector (prev/next word counts, CDIM=256) -> numpy k-means (NCLUST=48, cosine). Cluster-id of
word/prev/next + cluster-x-shape become emission features. Train TWO models from identical base features: no-cluster (= baseline)
vs +cluster. Same structured-perceptron Viterbi on OntoNotes 18-type. Report lift.

## Pre-registered verdict (NO defeat)
- HARD_PASS: F1 >= 0.62 AND lift >= 0.02 (clusters are a real feature lever; stack Path 5 phrase-clusters).
- MIDDLE_BAND: lift in [0.005,0.02).
- HARD_FAIL: lift < 0.005 (in-corpus clusters insufficient; need external embeddings or larger corpus).

Smoke (300 train, 394 vocab): lift +0.0047 -- but clusters scale with corpus; full (~15k vocab) is decisive.
