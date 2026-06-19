# Pre-registration: pos_tagger_v2_transitions_cpu_v1
**Date:** 2026-06-11  **Anchor:** pos_tagger_v2_transitions_cpu_v1  **Queue:** local_cpu_queue  **N:** 4096
## Scientific question
Does adding a substrate tag-transition layer + Viterbi decode (context) lift POS tagging from v1's 0.906 toward the 0.95 STRONG bar?
lambda tuned on a held-out dev split (no test peeking).
## Pre-registered bands
HARD-PASS-STRONG >= 0.95. HARD-PASS >= 0.92 (beats v1). MIDDLE >= 0.906 (no regression). HARD-FAIL < 0.906. UNKNOWN if corpus fails.
## Calibration rationale
Transition/Viterbi should disambiguate ambiguous words. Finding: substrate-cosine-scored Viterbi lifts same-split emission-only
0.899 -> 0.911 (genuine) but caps ~0.91; reaching 0.95 needs probabilistic score calibration (classical HMM = statistical regime).
## N-suffix section
N=4096; nltk PTB sample, 70/10/20 train/dev/test. Viterbi over T tags. Corpus pre-cached.
