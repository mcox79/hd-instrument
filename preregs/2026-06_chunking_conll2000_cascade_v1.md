# Prereg: chunking_conll2000_cascade_cpu_v1
**Date:** 2026-06-12  **Lane:** CPU  **Routing:** Research Priority 3 CLEAN (CoNLL-2000 bundled by Testbed; transfer P1 + Tier-4).
PP-364 POS-HMM tagger (structured-perceptron+Viterbi) -> chunking cascade on REAL CoNLL-2000 human chunks (8936/2012, 23 chunk
labels, Penn POS). POS is strong-but-imperfect feature (NOT circular). A/B word-only vs +predicted-POS-cascade.
HARD-PASS chunk-F1>=0.93. MIDDLE 0.90-0.93. HARD-FAIL<0.90.
Smoke (400 train): pos-acc 0.915, word-only 0.800 -> +cascade 0.832 (+0.032 CLEAN lift); full (8936) decisive.
