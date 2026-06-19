# Pre-registration: nl_slot_filling_atis_cpu_v1
**Date:** 2026-06-11  **Anchor:** nl_slot_filling_atis_cpu_v1  **Queue:** local_cpu_queue
## Scientific question
Does substrate frame-role binding (BIO slot-tagging via the PP-364 HMM mechanism + intent classification) do NL slot-filling
on the gold-annotated ATIS benchmark? (Verify-before-invest: real gold, not circular auto-derived math/code gold.)
## Pre-registered bands
HARD-PASS slot-F1 >= 0.85 AND intent-acc >= 0.80. MIDDLE slot-F1 >= 0.65. HARD-FAIL < 0.50.
## Calibration rationale
Result slot-F1 0.7125, intent 0.8455: intent PASSES; slot-F1 MIDDLE. Per Research decision tree, slot-F1 in 0.65-0.85 ->
hybrid (slot-filling base + dep-parser enrichment). Substrate slot-filling viable on real gold; 0.85 needs richer features.
## N-suffix section
ATIS (tuetschek/atis) gold intent+BIO slots; substrate HMM emission/transition/Viterbi + bag-of-words intent; span-level slot-F1.
