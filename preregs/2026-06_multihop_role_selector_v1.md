# Prereg: multihop_role_selector_cpu_v1
**Date:** 2026-06-11  **Lane:** CPU  **Routing:** Research GO -- multi-hop role-binding template-selector Phase 1.
4-stage role-binding: Stage1 entity-role extraction (PER/TGT/TOT/SUB/ADD/INQ/WK) + Stage2 role->numbers bundle + Stage3 two-stage
discriminative selector (pair-selector role features + op-classifier role+question features) + Stage4 execution w/ WK-as-PER-role.
SVAMP + ASDiv-1op. PHASE-1 TARGET: ASDiv-1op>=0.50 OR SVAMP>=0.42.
HARD-PASS hit a target. MIDDLE within 0.04. HARD-FAIL both well below.
Smoke (noisy 80/120): SVAMP 0.31, ASDiv-1op 0.18; full decisive.
