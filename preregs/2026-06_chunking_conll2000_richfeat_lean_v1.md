# Prereg: chunking_conll2000_richfeat_lean_cpu_v1
**Date:** 2026-06-12  **Lane:** CPU  **Routing:** Research Priority 3 (Tier-4 chunking milestone).
LEAN richfeat: the full cell timed out twice at 1500s retraining a word-only chunker we already have. Drop it; train PP-364 POS
tagger + ONLY the rich-feature POS-cascade chunker (POS-trigram + wider word/POS context + shape-bigram). Compare richfeat-F1 to
known refs (word-only 0.9093, basic-cascade 0.9231). Same feature set + 6-epoch training as the full cell. CoNLL-2000, substrate-only.
HARD-PASS richfeat-F1 >= 0.93 (Tier-4 milestone). MIDDLE 0.90-0.93 (0.9231 basic-cascade stands). HARD-FAIL < 0.90.
