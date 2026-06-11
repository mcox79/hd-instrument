# Prereg: sentiment_headtohead_calibrated_multiseed_gpu_v1

**Date:** 2026-06-11
**Lane:** GPU (overnight_queue, marsh@home)

## Motivation
The calibrated SST-2 head-to-head was substrate 0.767 vs calibrated-LLM 0.748 -- a narrow 0.019 edge on ONE substrate seed.
Honesty check: is the edge real or within substrate seed-noise? Determines whether we say "substrate beats 0.5B" or "matches".

## Method
- Substrate averaged-perceptron over 5 seeds (mean +/- std), bundled SST-2, 400 test.
- Calibrated LLM (Qwen2.5-0.5B, PMI / contextual calibration) computed ONCE (deterministic greedy logprob).

## Pre-registered verdict
- Sanity gate: llm_cal < 0.65 -> UNKNOWN.
- HARD_PASS (robust win): substrate (mean - std) >= llm_cal.
- MIDDLE_BAND (match, edge within noise): mean >= llm_cal but mean - std < llm_cal.
- HARD_FAIL: mean < llm_cal - 0.02.

Reports substrate mean/std/vals, llm_acc_calibrated, llm_acc_raw.
