# Pre-reg: A-route cosine-threshold vs tuned UNION (GPU/bge)
Date 2026-06-12. Cell exp_qa_self_knowledge_A_threshold_route_gpu_v1.py. Lane overnight_queue (GPU, bge). NO generative LLM.
Motivated by cue-alignment diagnosis (gold cos ~0.77, small gold sets). Sweep A-route selection policies (prod kw-UNION-top3,
bge-top-k, cosine-threshold tau, kw-UNION-threshold) on 12 A-Qs; full-gold-set A-F1.
HARD-PASS best beats production by >=0.05. MIDDLE +0.02..0.05. HARD-FAIL <=+0.02 (tuned UNION near-ceiling, small-gold P-R wall).
