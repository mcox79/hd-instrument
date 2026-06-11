# Prereg: classification_headtohead_3b_calibrated_gpu_v1

**Date:** 2026-06-11
**Lane:** GPU (overnight_queue, marsh@home)

## Motivation
Complete the size ladder for the calibrated classification head-to-head. Topic (AG-News) was a substrate win vs 0.5B (0.848 vs
0.647) and 1.5B (0.860 vs 0.670). The math north-star tested 0.5B/1.5B/3B; do the same for classification to settle whether the
TOPIC win is scale-invariant through 3B (6x larger) and how far the SENTIMENT boundary widens.

## Method
Same calibrated (PMI/contextual) protocol vs Qwen2.5-3B-Instruct on SST-2 + AG-News, 300 test each. Substrate = trained
averaged-perceptron.

## Sanity gate
Per task: SST-2 cal-LLM < 0.65 or AG-News cal-LLM < 0.50 -> that task UNKNOWN.

## Pre-registered verdict (per task, worst trustworthy overall)
HARD_PASS substrate >= cal-LLM | MIDDLE_BAND within 0.05 | HARD_FAIL substrate < cal-LLM - 0.05.
Expectation (not defeat): topic likely substrate win (scale-invariant); sentiment likely 3B win (boundary). Report honestly.
