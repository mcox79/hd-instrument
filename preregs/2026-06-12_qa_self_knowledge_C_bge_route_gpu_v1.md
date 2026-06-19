# Pre-reg: C-route bge-semantic fallback vs what_serves (GPU/bge)
Date 2026-06-12. Cell exp_qa_self_knowledge_C_bge_route_gpu_v1.py. Lane overnight_queue (GPU, bge). NO generative LLM.
C-gold 89% reachable but route_C=what_serves depends on sparse serves_capability field. Sweep: prod (what_serves), bge-top-k
(cosine to capability vec), prod UNION bge, cosine-threshold; full C-F1. HARD-PASS best beats prod by >=0.05.
