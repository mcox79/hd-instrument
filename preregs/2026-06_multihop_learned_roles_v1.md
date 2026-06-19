# Prereg: multihop_learned_roles_cpu_v1
**Date:** 2026-06-12  **Lane:** CPU  **Routing:** Research Path 2 (substrate slot-filler learned role-tagger; PP-369 mechanism).
Replace heuristic Stage-1 roles with a LEARNED role-tagger (emission over context features + weak op-derived labels), AUGMENTING
heuristic roles (L_* namespaced). Re-run the two-stage multi-hop selector. SVAMP + ASDiv-1op.
HARD-PASS ASDiv-1op>=0.45. MIDDLE 0.42-0.45. HARD-FAIL <=0.42 (or below heuristic Phase-1 0.376).
Smoke (noisy, overfit-prone): SVAMP 0.26, ASDiv-1op 0.15 (below heuristic 0.31/0.18); full is the fair test (less overfitting).
