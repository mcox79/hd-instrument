# Pre-reg: ATIS slot-filling robustness under char-noise
Date 2026-06-12 Cycle 50. Cell exp_substrate_atis_slot_filling_robustness_cpu_v1.py. Lane remote_cpu_queue (DESKTOP). NO LLM frame.
Slot-F1 at char-noise {0,5,10,20}pct (test-time perturbation). Extends NER noise-robustness finding to slot-filling (123 tags).
HARD-PASS retention@20pct >=0.70; MIDDLE 0.55-0.70; HARD-FAIL <0.55. Tests whether structured-prediction noise-robustness holds at large tag set.
