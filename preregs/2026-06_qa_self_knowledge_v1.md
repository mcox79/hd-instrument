# Prereg: qa_self_knowledge_cpu_v1
**Date:** 2026-06-12  **Lane:** CPU  **Routing:** Research APPROVED + scoring spec (QA_CELL_SCORING_SPEC).
Substrate-self-knowledge QA: snapshot live substrate_index (read-only), hard-route each Gap-7 question by type to a self_knowledge
query, score per-Q F1 (TP/FN/FP) on gold-present-in-snapshot subset (report attrition), macro-F1 + per-type breakdown. NO LLM-judge.
V1 SCOPE: Q1-Q12 (types A content / B relation / C capability) to validate pipeline; data-driven JSONL expands to 60 + D/E/F/G.
HARD-PASS macro-F1 >= 0.50. MIDDLE 0.30-0.50. HARD-FAIL <= 0.30. DECISIVE-PATH >= 0.60. (V1 partial; not full-60 HP_v1.)
