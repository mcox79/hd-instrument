# Prereg: pos_headtohead_llm_v3_gpu_v1
**Date:** 2026-06-12  **Lane:** GPU  **Routing:** Research GPU AUTHORIZE Priority 1 (research_to_exp_dev_GPU_AUTHORIZE_3_HEADTOHEAD_PRIORITIZED_2026-06-11).
Fix v2 (failed=timeout). Substrate POS structured-perceptron+Viterbi (UD-EWT 17-tag, 0.951 multi-seed Tier-A) vs LLM scale ladder
Qwen2.5-0.5B + 1.5B Instruct (3B optional via HDLAB_POS_3B=1), 5-shot, greedy. 150 test sents, robust tag-token parse, honest
count-mismatch penalty. Headline verdict = substrate vs 0.5B.
HARD-PASS substrate-win >= +0.10. MIDDLE +0.03 to +0.10. HARD-FAIL < +0.03. Per-model UNKNOWN if mismatch-rate > 0.40; all-UNKNOWN -> UNKNOWN.
