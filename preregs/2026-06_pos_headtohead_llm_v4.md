# Prereg: pos_headtohead_llm_v4_gpu_v1
**Date:** 2026-06-12  **Lane:** GPU  **Routing:** Research GPU AUTHORIZE Priority 1 (fix v3 UNKNOWN).
v3 completed but UNKNOWN: LLM bare-tag output mismatch>0.96. v4 uses robust "word/TAG" pairs (self-aligning) + cursor alignment to
gold words. Substrate POS structured-perceptron+Viterbi (UD-EWT 17-tag, 0.951 Tier-A) vs Qwen2.5-0.5B+1.5B 5-shot. 150 test. Headline vs 0.5B.
HARD-PASS substrate-win>=+0.10. MIDDLE +0.03-0.10. HARD-FAIL <+0.03. Per-model UNKNOWN if unaligned-rate>0.40.
