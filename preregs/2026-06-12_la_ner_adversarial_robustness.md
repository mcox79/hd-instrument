# Pre-registration: L-A substrate NER adversarial-robustness curve

Date: 2026-06-12
Status: Pre-registered, ready to launch
Experiment file: [exp_la_ner_adversarial_robustness_cpu_v1.py](../experiments/exp_la_ner_adversarial_robustness_cpu_v1.py)

## Hypothesis (H)
Substrate-classical NER degrades gracefully under char-level input noise (where LLMs collapse, Nature SciRep 2025). Operationalized:
report span-F1 across char-noise {0,5,10,20}% (mean +/- SD, 3 seeds); headline = retention at 20% = F1(20%)/F1(0%).

## Pre-registered outcomes (substrate half; LLM-0.5B head-to-head is the GPU follow-on)
- PASS: F1 >= 0.55 at 20% noise (robust)
- MIDDLE: 0.45-0.55 at 20%
- HARD-FAIL: < 0.45 at 20%

## Method
Subprocess the validated NER cell with HDLAB_TEST_NOISE + HDLAB_SEED; char swap/insert/delete perturbation of test tokens; CPU; no LLM-judge.
