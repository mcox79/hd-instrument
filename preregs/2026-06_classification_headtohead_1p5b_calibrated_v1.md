# Prereg: classification_headtohead_1p5b_calibrated_gpu_v1

**Date:** 2026-06-11
**Lane:** GPU (overnight_queue, marsh@home)

## Motivation
The calibrated classification head-to-head beat Qwen-0.5B (SST-2 0.7765 robust-win; AG-News 0.848 decisive). The MATH north-star
was scale-invariant (substrate beat 0.5B/1.5B/3B). Scale test: does the CLASSIFICATION win hold vs Qwen2.5-1.5B (3x larger), or
does it only beat the smallest LLM? Honest either way.

## Method
- Substrate: averaged-perceptron bag-of-words/bigram (trained classifier), bundled SST-2 + AG-News, 300 test each.
- LLM: Qwen2.5-1.5B-Instruct, calibrated (PMI / contextual: subtract content-free label log-prob over "", "N/A", "nothing").

## Sanity gate
Per task: SST-2 cal-LLM < 0.65 or AG-News cal-LLM < 0.50 -> that task UNKNOWN (no claim for it).

## Pre-registered verdict (per task, then worst trustworthy task overall)
HARD_PASS substrate >= cal-LLM | MIDDLE_BAND within 0.05 | HARD_FAIL substrate < cal-LLM - 0.05.

Reports per-task substrate/raw/calibrated + latency.
