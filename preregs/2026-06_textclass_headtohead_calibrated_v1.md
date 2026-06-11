# Prereg: textclass_headtohead_calibrated_gpu_v1

**Date:** 2026-06-11
**Lane:** GPU (overnight_queue, marsh@home)

## Motivation
Generalize the calibrated classification head-to-head from binary sentiment (SST-2: substrate 0.767 >= calibrated-LLM 0.748)
to 4-class topic classification (AG-News). Tests whether the calibrated substrate-vs-LLM result holds beyond binary.

## Method
- Substrate: averaged-perceptron bag-of-words/bigram (discriminative weighting), bundled AG-News.
- LLM: Qwen2.5-0.5B-Instruct, label log-prob over 4 topic labels; raw (naive, diagnostic) and calibrated (PMI / contextual
  calibration: subtract content-free label log-prob averaged over "", "N/A", "nothing").

## Sanity gate (honesty)
4-class chance = 0.25. If calibrated LLM < 0.50, eval judged unreliable -> verdict UNKNOWN, NO claim.

## Pre-registered verdict
- llm_cal < 0.50 -> UNKNOWN.
- else: HARD_PASS substrate >= llm_cal | MIDDLE_BAND within 0.05 | HARD_FAIL substrate < llm_cal - 0.05.

Reports substrate_acc, llm_acc_raw, llm_acc_calibrated, latencies.
