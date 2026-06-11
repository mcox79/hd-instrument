# Pre-registration: active_inference_e1_e2_cpu_v1
**Date:** 2026-06-11  **Anchor:** active_inference_e1_e2_cpu_v1  **Queue:** local_cpu_queue  **N:** 8192
## Scientific question
Does E1 pragmatic_value (goal cosine on the predicted next state) + E2 boredom-gamma exploration let an active-inference agent
escape the low-surprise comfort basin and reach the goal, where epistemic-only F-minimization stalls? FPE substrate position kernel.
## Pre-registered bands
HARD-PASS error_drop > 30% AND goal_reach > 0.70. MIDDLE one of the two. HARD-FAIL error_drop <= 20% OR goal_reach <= 0.60.
## Calibration rationale
Epistemic-only baseline stalls in the comfort basin (error ~0.75). E1+E2 should both cut error >30% and reach goal (<0.1) >70%.
goal_reach near-misses likely reflect FPE-kernel sidelobes, not mechanism failure.
## N-suffix section
N=8192 complex64 FPE; numpy CPU, seconds. n=1 exploratory.
