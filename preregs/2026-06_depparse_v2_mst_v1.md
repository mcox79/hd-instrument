# Pre-registration: depparse_v2_mst_cpu_v1
**Date:** 2026-06-11  **Anchor:** depparse_v2_mst_cpu_v1  **Queue:** local_cpu_queue  **N:** 8192
## Scientific question
Do MST cycle-breaking tree-decode + head-context transition features lift the substrate dep-parser past the v1 gate (UAS 0.60)?
## Pre-registered bands
HARD-PASS UAS >= 0.85. MIDDLE >= 0.70. HARD-FAIL < 0.70.
## Calibration rationale
Result UAS 0.5689 -- naive MST cycle-breaking + head-context additions did NOT lift (vs v1 lexical 0.596). Confirms (2nd time):
cheap incremental dep-parser improvements plateau ~0.57-0.60; reaching 0.85 needs the full graph-based parser (rich features +
discriminative training = the multi-day build). Naive feature/decode additions are insufficient.
## N-suffix section
N=8192; NLTK dependency_treebank; POS+lexical+head-context arc-scoring + cycle-breaking tree decode.
