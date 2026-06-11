# Prereg: pos_headtohead_llm_gpu_v1

**Date:** 2026-06-11
**Lane:** GPU (overnight_queue, marsh@home)

## Motivation
North-star extension to the substrate's STRONGEST capability: structured prediction. Classification head-to-heads done (topic
substrate win scale-invariant; sentiment boundary). The substrate is far stronger at POS tagging (0.95) than classification. Can a
comparable-size LLM match the tiny substrate POS tagger zero/few-shot?

## Method
- Substrate: discriminative structured-perceptron + Viterbi on UD-EWT, 17 universal POS tags. Token accuracy on test.
- LLM: Qwen2.5-1.5B-Instruct, few-shot (2 examples) tagging; output space-separated tags aligned to tokens by position.

## Robust eval + sanity gate
Align LLM tag list to gold tokens by position; count missing/extra as wrong (honest penalty); track per-sentence token-count
mismatch rate. If mismatch rate > 0.40, eval unreliable -> UNKNOWN (cannot align).

## Pre-registered verdict
- UNKNOWN if mismatch rate > 0.40 or load fails.
- else: HARD_PASS substrate >= LLM | MIDDLE_BAND within 0.03 | HARD_FAIL substrate < LLM - 0.03.

Reports substrate acc, LLM acc, mismatch rate, latency.
