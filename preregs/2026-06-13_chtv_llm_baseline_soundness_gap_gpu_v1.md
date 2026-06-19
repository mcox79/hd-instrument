# Pre-reg: CH-P6 substrate-vs-LLM soundness gap (Research-endorsed capstone) -- GPU remote
Date 2026-06-13. Cell exp_chtv_llm_baseline_soundness_gap_gpu_v1.py. Lane overnight_queue (GPU). LLM=Qwen2.5-0.5B+1.5B-Instruct (baseline only; substrate=ground truth).
24 trials (12 valid real chains + 12 invalid plausible-fab last edge) built on laptop clean graph. Substrate verifier: 0 false-accepts.
HARD-PASS LLM accepts >=1/12 invalid as valid (hallucination -> soundness gap). MIDDLE 0 false-accept but false-rejects. HARD-FAIL LLM exact-matches substrate.
