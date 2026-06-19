# Pre-registration: phase4_math_integration_v2_cpu_v1
**Date:** 2026-06-11  **Anchor:** phase4_math_integration_v2_cpu_v1  **Queue:** local_cpu_queue  **N:** 8192
## Scientific question
Does keyword-anchored slot-binding (number nearest its role-cue) + more schemas lift Phase-4 MATH end-to-end past v1's 0.05?
## Pre-registered bands
HARD-PASS accuracy >= 0.20. MIDDLE >= 0.10. HARD-FAIL < 0.05.
## Calibration rationale
Result: acc-on-covered 0.183->0.243 (precision UP from anchoring) but coverage 0.271->0.167 (stricter -> answers fewer);
net end-to-end ~0.041 (flat). Empirically confirms: heuristic slot-binding hits a precision/coverage tradeoff; reaching 0.20
needs full role-parsing (accurate binding on ALL problems) + schema expansion = the multi-day build (now empirically justified).
## N-suffix section
N=8192; hendrycks level-1; keyword-anchored slot-binding + linear-eq schema added.
