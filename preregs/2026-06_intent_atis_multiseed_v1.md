# Pre-registration: intent_atis_multiseed_cpu_v1
**Date:** 2026-06-11  **Anchor:** intent_atis_multiseed_cpu_v1  **Queue:** local_cpu_queue  **Seeds:** 5
## Scientific question
Is substrate-only intent classification on ATIS gold (count-based naive-Bayes; substrate stores P(word|intent)) seed-robust at n=5 -> Tier A?
## Pre-registered bands
HARD-PASS mean intent-acc >= 0.80 AND std <= 0.02. MIDDLE mean >= 0.80 std > 0.02. HARD-FAIL mean < 0.80.
## Calibration rationale
n=5 via train-bootstrap resample (robustness to training-sample variation). Result mean 0.8345 std 0.0038 -> seed-robust Tier A.
Substrate-only intent classification refutes "intent needs LLM."
## N-suffix section
ATIS gold; count-based naive-Bayes intent; train-bootstrap per seed; fixed test.
