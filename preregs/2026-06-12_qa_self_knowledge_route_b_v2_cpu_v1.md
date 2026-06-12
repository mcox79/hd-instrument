# Pre-reg: qa_self_knowledge improved route_B v2 (path-to-0.70 B-axis mechanism R&D)
Date 2026-06-12 Cycle 50. Cell exp_qa_self_knowledge_route_b_v2_cpu_v1.py. Lane remote_cpu_queue (DESKTOP). NO LLM frame.
Tests whether improved route_B (bidirectional + explicit-rel-type-with-RELATES-fallback + last-segment target match) lifts the
B-axis (v1 0.325) WITHOUT macro regression (v1 0.4684). All other routes unchanged (isolates route_B delta).
Bands: HARD-PASS B>=0.40 (+0.075) AND macro>=0.485. MIDDLE B in [0.35,0.40]. HARD-FAIL B<0.35 or macro<0.46 (B corpus-bound).
Empirically resolves whether the B-axis bottleneck is route-fixable or corpus-bound.
