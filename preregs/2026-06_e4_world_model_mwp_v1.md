# Prereg: e4_world_model_mwp_cpu_v1
**Date:** 2026-06-12  **Lane:** CPU  **Routing:** Research E4 design sketch (world-model mechanism class beyond discriminative).
Schema-simulation MWP solver: scenario cues -> canonical schema (EQUAL_GROUPS/COMBINE/CHANGE_ADD/CHANGE_SUB/COMPARE/SHARE/TIMES),
each carries its operation as world knowledge (zero-shot, no training); simulate with extracted numbers. ASDiv-1op vs discriminative ~0.39.
Per brain-can-do-it: test the mechanism, do not pre-accept the 0.39 plateau. HARD-PASS >=0.50 (breaks plateau). MIDDLE 0.40-0.50.
HARD-FAIL <=0.40 (~= discriminative -> plateau is comprehension/selection-bound NOT mechanism-bound; honest evidence for corpus ingestion).
