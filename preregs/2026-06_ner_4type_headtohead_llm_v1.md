# Prereg: ner_4type_headtohead_llm_gpu_v1
**Date:** 2026-06-12  **Lane:** GPU  **Routing:** Research GPU AUTHORIZE Priority 2 (research_to_exp_dev_GPU_AUTHORIZE_3_HEADTOHEAD_PRIORITIZED_2026-06-11).
Substrate NER 4-type (structured-perceptron+Viterbi, OntoNotes->CoNLL-coarse, multi-seed Tier-A 0.6502) vs LLM few-shot NER
Qwen2.5-0.5B + 1.5B Instruct (3B optional HDLAB_NER_3B=1), 5-shot, literature-standard "TYPE: text" entity-extraction parsed to
token spans -> span-F1 (same metric, same 150-sent test subset). Hallucinated/unmatched LLM predictions counted as FP. Headline vs 0.5B.
HARD-PASS substrate-win >= +0.05. MIDDLE -0.05 to +0.05. HARD-FAIL < -0.05 (honest substrate-only scope; no ceiling claim).
Per-model UNKNOWN if unmatch-rate > 0.40; all-UNKNOWN -> UNKNOWN.
