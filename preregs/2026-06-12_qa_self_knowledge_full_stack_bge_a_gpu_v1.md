# Pre-reg: qa_self_knowledge FULL STACK (route_B v3 + candidate edges + bge semantic A-route)
Date 2026-06-12 Cycle 50. Cell exp_qa_self_knowledge_full_stack_bge_a_gpu_v1.py. Lane remote_cpu_queue (DESKTOP; bge). NO LLM frame.
Stacks ALL Exp-Dev path-to-0.70 levers: route_B v3 (accept-all-reltypes) + 10 candidate edges (in-memory) + bge semantic A-route
(replaces keyword route_A; A-content is text-topical -> semantic ranking is the A lever). Measures combined macro vs:
- v1 baseline 0.4684; route_B v3 0.4973; route+edges 0.5248. Headline: A-axis bge lift + combined macro toward 0.70.
Bands: HARD-PASS macro >= 0.55 (A bge lifts on top of B/D). MIDDLE 0.50-0.55. HARD-FAIL < 0.50. UNKNOWN if bge unavailable.
