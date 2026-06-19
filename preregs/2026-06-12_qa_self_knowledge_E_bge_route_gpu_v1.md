# Pre-reg: E-route bge selection vs keyword-only (GPU/bge)
Date 2026-06-12. Cell exp_qa_self_knowledge_E_bge_route_gpu_v1.py. Lane overnight_queue (GPU, bge). NO generative LLM.
E-cue diagnosis: E-gold methodology atoms at bge rank ~0.0; current route_E is keyword-only (no bge). Sweep E-route policies
(prod keyword-only, bge-top-k over meta/methodology corpus, keyword UNION bge-top-k, cosine-threshold); full E-F1.
HARD-PASS best beats keyword-only by >=0.05 E-F1. MIDDLE +0.02..0.05. HARD-FAIL <=+0.02.
