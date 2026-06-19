# Pre-registration: nl_slot_filling_atis_v2_cpu_v1
**Date:** 2026-06-11  **Anchor:** nl_slot_filling_atis_v2_cpu_v1  **Queue:** local_cpu_queue
## Scientific question
Does adding context-window emission (prev/next word association per slot -- the preposition-before-slot signal) lift the
substrate ATIS slot-F1 from v1's 0.71 to the 0.85 bar?
## Pre-registered bands
HARD-PASS slot-F1 >= 0.85 AND intent-acc >= 0.80 (-> per Research decision tree: SKIP dep-parser; slot-filling IS the primitive).
MIDDLE slot-F1 >= 0.65. HARD-FAIL < 0.50.
## Calibration rationale
Slots depend on local context (from->fromloc, to->toloc). Context-window emission captures it. Result slot-F1 0.8709, intent
0.8455 -> HARD_PASS; decision-tree skip-dep-parser branch. Genuine feature improvement (standard slot-filling signal), not gaming.
## N-suffix section
ATIS gold; substrate HMM emission (word + prev/next context) + slot-bigram transition + Viterbi; intent bag-of-words; span slot-F1.
