# Prereg: chunking_pos_cascade_cpu_v1
**Date:** 2026-06-12  **Lane:** CPU  **Routing:** Research Priority 3 (Drill 2 P1 transfer + Tier-4 milestone).
PP-364 POS-HMM (structured-perceptron+Viterbi) -> chunking cascade: predict POS, use predicted-POS as chunk features. UD-EWT
(benchmark-agnostic transfer test; chunks derived from gold POS). A/B word-only vs +POS-cascade.
HARD-PASS chunk-F1>=0.93. MIDDLE 0.90-0.93. HARD-FAIL <0.90.
Smoke (300 train): pos-acc 0.866, word-only 0.841 -> +cascade 0.848 (+0.006); full (3000) decisive.
