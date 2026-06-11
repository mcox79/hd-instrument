# Prereg: sentiment_headtohead_calibrated_gpu_v1

**Date:** 2026-06-11
**Lane:** GPU (overnight_queue, marsh@home)

## Motivation
Resolve the OPEN classification-head-to-head caveat. Prior LLM-eval paths were both broken: free-generation parsing gave
Qwen2.5-0.5B SST-2 = 0.58 and naive length-normalized label-logprob gave 0.485 -- both ~chance, implausible (real zero-shot
SST-2 for a 0.5B instruct model is ~0.8+). Known cause: surface-form bias -- naive label-logprob is dominated by the model's
prior P(" positive") vs P(" negative") rather than the review content.

## Method
- Substrate: averaged-perceptron bag-of-words/bigram classifier (discriminative weighting), bundled SST-2.
- LLM: Qwen2.5-0.5B-Instruct, three scorings:
  - raw: naive label log-prob (diagnostic, expected ~chance).
  - calibrated: contextual calibration / PMI (Zhao 2021, Holtzman 2021) -- score(label) = logP(label|prompt) - logP(label|content-free),
    averaging 3 content-free prompts ("", "N/A", "nothing"). This subtracts the surface-form prior.

## Sanity gate (honesty)
If the CALIBRATED LLM is still < 0.65 on SST-2, the eval is judged unreliable -> verdict UNKNOWN, NO substrate-vs-LLM claim.

## Pre-registered verdict
- llm_cal < 0.65 -> UNKNOWN (eval still broken).
- else: HARD_PASS substrate >= llm_cal | MIDDLE_BAND within 0.05 | HARD_FAIL substrate < llm_cal - 0.05.

Reports substrate_acc, llm_acc_raw, llm_acc_calibrated, latencies.
