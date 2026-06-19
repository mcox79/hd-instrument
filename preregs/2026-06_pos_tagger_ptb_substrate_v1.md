# Pre-registration: pos_tagger_ptb_substrate_cpu_v1
**Date:** 2026-06-11  **Anchor:** pos_tagger_ptb_substrate_cpu_v1  **Queue:** local_cpu_queue  **N:** 4096
## Scientific question
Can a substrate-only tagger (Tier-1 POS atoms + Tier-3 word lexicon + morphological-feature OOV backoff, substrate associative
recall) match the 0.90 POS-tagging bar without an LLM? If yes, the "LLM-only-for-NL-parse" claim is refuted. DATA: NLTK Penn
Treebank SAMPLE (~3914 WSJ sents), sentence-order train/test split (full LDC WSJ is licensed; this is the accessible substitute).
## Pre-registered bands
HARD-PASS tag-accuracy >= 0.90 (Brill 1995 = 96.7%). STRONG >= 0.95. MIDDLE >= 0.80. HARD-FAIL < 0.80. UNKNOWN if download fails.
## Calibration rationale
0.90 is the LLM-boundary bar. Most-frequent-tag ~0.895; adding morphological OOV features (cap/digit/suffix per recipe) crosses 0.90.
Context window (2L+2R) would push toward 0.95 STRONG (follow-up). On the small NLTK sample OOV is ~8.5% (higher than full PTB).
## N-suffix section
N=4096 complex64; nltk PTB sample. Fast (lexicon build + lookup). Substrate associative recall (tag cleanup over Tier-1 atoms).
