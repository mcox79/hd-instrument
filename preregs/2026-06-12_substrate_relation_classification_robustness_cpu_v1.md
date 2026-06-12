# Pre-reg: RE robustness contrast (non-structured vs structured-prediction noise-robustness)
Date 2026-06-12 Cycle 50. Cell exp_substrate_relation_classification_robustness_cpu_v1.py. Lane remote_cpu_queue (DESKTOP). NO LLM frame.
SemEval RE (multiclass, NO Viterbi/transitions) under char-noise {0,5,10,20}pct. CONTRAST vs structured-prediction NER/slot
(~64-68pct retention@20pct). HARD-PASS (hypothesis confirmed) ret<0.55 (RE less robust -> structured prediction is the source);
MIDDLE 0.55-0.65; HARD-FAIL >=0.65 (robustness not structured-prediction-specific). Isolates the noise-robustness mechanism.
