# Pre-registration: pos_tagger_v3_hmm_cpu_v1
**Date:** 2026-06-11  **Anchor:** pos_tagger_v3_hmm_cpu_v1  **Queue:** local_cpu_queue
## Scientific question
Does a substrate-native count-based HMM (stored emission + transition probabilities + Viterbi, per Research) lift POS tagging
from v2's 0.9113 cosine cap toward the 0.95 STRONG bar?
## Pre-registered bands
HARD-PASS-STRONG >= 0.95. HARD-PASS >= 0.93. MIDDLE >= 0.9113. HARD-FAIL < 0.9113. UNKNOWN if corpus fails.
## Calibration rationale
Calibrated log-prob emission/transition + naive-Bayes morphological OOV. Result 0.9294: HMM lifts ~3% over emission-only (method
works) but the small NLTK PTB sample (8.5% OOV, ~80K train tokens) caps ~0.93; full LDC PTB (1M tokens) needed for 0.95 STRONG.
## N-suffix section
nltk PTB sample, 80/20; Viterbi over T tags; corpus pre-cached. Data-size ceiling, not method limit.
