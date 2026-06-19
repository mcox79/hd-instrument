# Pre-registration: phase4a_schema_expand_cpu_v1
**Date:** 2026-06-11  **Anchor:** phase4a_schema_expand_cpu_v1  **Queue:** local_cpu_queue  **N:** 8192
## Scientific question
Does Phase-4A schema expansion (5 -> 13 solvable schemas) + anchored slot-binding lift MATH end-to-end toward 0.20?
## Pre-registered bands
HARD-PASS accuracy >= 0.20. MIDDLE >= 0.10. HARD-FAIL < 0.10.
## Calibration rationale
Trajectory: v1 0.050 (5 schemas, positional) -> v2 0.041 (anchored, precision/coverage tradeoff) -> 4A 0.059 (13 schemas,
anchored). acc-on-covered 0.183->0.277. Schema expansion helps; positive trajectory toward 0.20 but needs full schema set (42
math) + Phase-4B dep-parse role-binding (precision) to close. Genuine incremental progress on the authorized multi-day build.
## N-suffix section
N=8192; hendrycks level-1; 13 solvable schemas + keyword-anchored slot-binding + constraint-solve.
