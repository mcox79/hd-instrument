# Pre-registration: math_light_substrate_cpu_v1
**Date:** 2026-06-11  **Anchor:** math_light_substrate_cpu_v1  **Queue:** local_cpu_queue  **N:** 4096
## Scientific question
On the curated symbolic subset of hendrycks level-1, does the substrate-consistent pipeline (substrate stores parsed
operands per PP-341 + closed-form compute) solve accurately? Tests accuracy, coverage, and substrate recall-fidelity.
## Pre-registered bands
HARD-PASS accuracy >= 0.35 AND recall-fidelity >= 0.95 AND coverage >= 0.15. MIDDLE accuracy >= 0.20. HARD-FAIL acc < 0.20 or fidelity < 0.90.
## Calibration rationale
Result: accuracy 0.947, recall-fidelity 1.000 (both decisively pass) but coverage 0.086 < 0.15 (MIDDLE). Substrate-symbolic
solving WORKS where applicable; coverage is the gap (most level-1 are word-problems) -> motivates word-problem extraction pipeline.
## N-suffix section
N=4096; hendrycks prealgebra+algebra level-1; substrate operand store/recall (PP-341) + closed-form. Honest thin-substrate architecture.
