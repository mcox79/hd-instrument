# Pre-registration: reasoning_routing_oracle_cpu_v1
**Date:** 2026-06-11  **Anchor:** reasoning_routing_oracle_cpu_v1  **Queue:** local_cpu_queue  **N:** 8192
## Scientific question
Does a substrate-as-classifier (prototype-bundle cleanup) route problem instances to the right reasoning primitive (6 classes:
deductive/Bayesian/causal/counterfactual/temporal/analogical)? Phase-3 extraction->reasoning bridge (Drill B oracle).
## Pre-registered bands
HARD-PASS routing_acc >= 0.75 AND answer_acc >= 0.60. MIDDLE routing_acc >= 0.60. HARD-FAIL < 0.60.
## Calibration rationale
30 synthetic instances (5/class) with class signature keywords; substrate cleanup over 6 class prototypes. Result routing_acc
0.967, answer_acc 0.892 (routing x validated-primitive-rate). Caveat: clean-signature instances; real-text routing noisier.
## N-suffix section
N=8192; 6-class taxonomy (Drill B) -> PP-343/291/307/280/348/360/362/275; substrate prototype-bundle classifier.
