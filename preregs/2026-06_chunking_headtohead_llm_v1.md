# Prereg: chunking_headtohead_llm_gpu_v1
**Date:** 2026-06-12  **Lane:** GPU  **Routing:** Research GPU AUTHORIZE Priority 3 (research_to_exp_dev_GPU_AUTHORIZE_3_HEADTOHEAD_PRIORITIZED_2026-06-11). HOLD-queue until richfeat lands (substrate's best chunker).
Substrate chunker = PP-364 POS tagger -> rich-feature POS-cascade chunker (structured-perceptron+Viterbi, 0.923+ transfer-validated)
vs LLM few-shot bracketed chunking Qwen2.5-0.5B + 1.5B (3B optional HDLAB_CHK_3B=1), 5-shot, "[NP the dog] [VP runs]" parsed by
sequential cursor to token spans -> span-F1 (same metric, same 150-sent test subset). Unmatched bracket phrases counted FP. Headline vs 0.5B.
HARD-PASS substrate-win >= +0.10. MIDDLE +0.03 to +0.10. HARD-FAIL < +0.03. Per-model UNKNOWN if unmatch-rate>0.40.
