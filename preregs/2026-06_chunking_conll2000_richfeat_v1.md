# Prereg: chunking_conll2000_richfeat_cpu_v1
**Date:** 2026-06-12  **Lane:** CPU  **Routing:** Priority 3 follow-up -- richer chunk features to close 0.923->0.93 (Tier-4 HARD-PASS).
CoNLL-2000 chunking + PP-364 POS cascade + RICHER features (POS-trigram, wider word/POS context, shape-bigram, word x POS).
HARD-PASS chunk-F1>=0.93 (Tier-4 milestone). MIDDLE 0.92-0.93. HARD-FAIL <0.92.
Smoke (400 train): richfeat overfits (0.824 < basic 0.832); full (8936) tests if richer features help at scale or saturate.
