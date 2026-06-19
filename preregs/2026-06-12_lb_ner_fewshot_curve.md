# Pre-registration: L-B substrate NER few-shot transfer curve

Date: 2026-06-12
Status: Pre-registered, ready to launch
Experiment file: [exp_lb_ner_fewshot_curve_cpu_v1.py](../experiments/exp_lb_ner_fewshot_curve_cpu_v1.py)

## Hypothesis (H)

Substrate-classical NER (structured perceptron + Viterbi) reaches usable F1 from little labeled data -- the low-data-optimal claim.
Operationalized: report the F1 curve across train fractions {1,5,10,50,100}% (mean +/- SD over 3 seeds); flag F1 at 5% data.

## Pre-registered outcomes (substrate half; LLM crossover is the GPU follow-on)
- PASS: F1 >= 0.55 at 5% data (strong low-data signal)
- MIDDLE: 0.40-0.55 at 5%
- HARD-FAIL: < 0.40 at 5%

## Method
Subprocess the validated NER cell with HDLAB_TRAIN_FRAC + HDLAB_SEED; parse span-F1; CPU; no LLM-judge.
