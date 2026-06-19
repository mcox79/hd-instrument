# Pre-reg: algebra coverage-gap diagnosis (CPU/local)
Date 2026-06-12. Cell exp_substrate_algebra_coverage_gap_diagnosis_cpu_v1.py. NO LLM. PartitionedStore stats, local-safe.
Classify the 1501 uncovered atoms into HISTORY (by-design bge-served) vs STRUCTURED (algebra-backfillable); surface T1 high-value subset.
HARD-PASS gap decomposes cleanly (history majority, 0 history-algebra, defined structured remainder). MIDDLE structured dominates. HARD-FAIL covered mostly history.
