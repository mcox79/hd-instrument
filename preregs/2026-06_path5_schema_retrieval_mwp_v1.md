# Prereg: path5_schema_retrieval_mwp_cpu_v1
**Date:** 2026-06-12  **Lane:** CPU  **Routing:** Research operand-selection drill HANDOFF Path 5 (hippocampal schema retrieval, cheap-first).
Prior solved MWP scenarios (train = solution-history) stored as schema vectors (cue+structural feats); test problem retrieves k-nearest
schemas; transfers operation + operand-order. vs discriminative ~0.39 plateau + naive majority-op baseline. Brain analogue Tse 2007.
HARD-PASS acc>=0.49 (+0.10). MIDDLE 0.45-0.49. HARD-FAIL <0.43 (<+0.04 -> 4th triangulation angle = corpus-bound at operand level).
