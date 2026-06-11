# Pre-registration: phase4_math_integration_cpu_v1
**Date:** 2026-06-11  **Anchor:** phase4_math_integration_cpu_v1  **Queue:** local_cpu_queue  **N:** 8192
## Scientific question
Do the validated pipeline pieces (schema-retrieve + slot-fill + constraint-solve) COMPOSE on real hendrycks MATH level-1 end-to-end?
## Pre-registered bands
HARD-PASS accuracy >= 0.20. MIDDLE >= 0.10 (beats shallow 0.023 substantially). HARD-FAIL < 0.05.
## Calibration rationale
Result 0.050 (2x the shallow word-problem gate 0.023). Pieces compose but end-to-end low: schema-coverage 27% (5/114 schemas)
+ slot-binding acc 0.183 on covered (which number->which role; asked-quantity-ID). Path to 0.20: full schema coverage +
dep-parse/role-parsing for math slot-binding (re-justifies dep-parser for MATH specifically, vs ATIS where slot-fill skipped it).
## N-suffix section
N=8192; hendrycks prealgebra+algebra level-1 (n=221); 5 solvable schemas + keyword-proximity slot-bind + constraint-solve.
