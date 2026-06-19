# Pre-reg: substrate-classical ATIS slot filling (NEW Tier-A NLU capability)
Date 2026-06-12 Cycle 50. Cell exp_substrate_atis_slot_filling_cpu_v1.py. Lane remote_cpu_queue (DESKTOP). NO LLM frame.
discriminative_perceptron (structured perceptron + Viterbi) over BIO slot tags on ATIS (4978/893, ~120 slot labels). Span-level
slot-F1. NEW Tier-A capability (slot filling / NLU sequence labeling). HARD-PASS slot-F1>=0.88; MIDDLE 0.78-0.88; HARD-FAIL <0.78.
Smoke (400 train) = 0.85. Same universal discriminative-weighting lever as POS/NER/chunking.
