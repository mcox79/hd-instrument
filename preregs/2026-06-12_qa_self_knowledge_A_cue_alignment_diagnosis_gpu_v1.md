# Pre-reg: A-axis bge cue-alignment diagnosis (GPU/bge)
Date 2026-06-12. Cell exp_qa_self_knowledge_A_cue_alignment_diagnosis_gpu_v1.py. Lane overnight_queue (GPU, bge). NO generative LLM.
For the 12 A-axis answerable-with-gold Qs (gap7_benchmark_v1): bge-encode query topic, cosine to gold atom semantic vec, gold rank + in-top-3.
Tests the trilogy's free-text-path prediction (A-axis is cue-bound). DECISIVE either way:
CUE-BOUND if median best-gold cos<0.40 OR recall@3<0.60 (lever = bge query encoding). CUE-ALIGNED if cos>=0.50 AND recall@3>=0.75
(lever = downstream ranking/UNION, not cue). MIDDLE mixed. UNKNOWN if bge/benchmark unavailable.
