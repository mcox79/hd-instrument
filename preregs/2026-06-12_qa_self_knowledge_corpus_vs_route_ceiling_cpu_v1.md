# Pre-reg: per-axis corpus-vs-route ceiling (CPU/local)
Date 2026-06-12. Cell exp_qa_self_knowledge_corpus_vs_route_ceiling_cpu_v1.py. NO LLM. PartitionedStore + relations + gold; numpy-free.
Classify each gold item: ABSENT (atom missing -> ingest), PRESENT_UNREACHABLE (B: no edge to target -> edge ingest), PRESENT_REACHABLE (route-fixable).
Tests the capstone "corpus-bound" claim. HARD-PASS clean split (>=60% one side). MIDDLE mixed.
