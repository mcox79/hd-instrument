# Pre-reg: full-stack A/B -- bge-top5 A-route vs production keyword-UNION-top3 (GPU/bge)
Date 2026-06-12. Cell exp_qa_self_knowledge_full_stack_A_top5_ab_gpu_v1.py. Lane overnight_queue (GPU, bge). NO generative LLM.
Run all 53 Qs (route_B v3 + candidate edges held fixed); compute macro under A=keyword-UNION-bge-top3 (prod) vs A=bge-top5 (alt).
Validates whether the A-subset +0.043 (bge-top5 finding) yields a real FULL-STACK macro lift with no other-axis regression.
HARD-PASS macro_delta>=+0.005. HARD-FAIL <=-0.005 (keyword union helps full benchmark). MIDDLE neutral (simplification only).
