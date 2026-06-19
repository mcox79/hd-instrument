# Pre-reg: combined A+E bge route fixes, full-stack (GPU/bge)
Date 2026-06-12. Cell exp_qa_self_knowledge_full_stack_AE_combined_gpu_v1.py. Lane overnight_queue (GPU, bge). NO generative LLM.
All 53 Qs; PROD (A=keyword-UNION-bge-top3, E=keyword-only) vs ALT (A=bge-top5, E=bge-cosine-threshold-0.70 over methodology).
B/C/D/G held fixed. Honest combined macro impact of the two validated route levers (E tau=0.70 FIXED, not re-tuned here).
HARD-PASS macro_delta>=+0.03. MIDDLE +0.005..0.03. HARD-FAIL <+0.005.
