# Pre-reg: E-axis (methodology) bge cue-alignment diagnosis (GPU/bge)
Date 2026-06-12. Cell exp_qa_self_knowledge_E_cue_alignment_diagnosis_gpu_v1.py. Lane overnight_queue (GPU, bge). NO generative LLM.
Same diagnostic as the A-cue cell, applied to the E (methodology) axis -- the OTHER weak axis (0.495). bge-encode the scenario,
cosine to gold methodology-rule atom, gold rank + in-top-3. CUE-BOUND if median best-gold cos<0.40 OR recall@3<0.60 (fix=query
encoding). CUE-ALIGNED if cos>=0.50 AND recall@3>=0.75 (fix=downstream ranking). MIDDLE mixed. UNKNOWN if bge/benchmark missing.
