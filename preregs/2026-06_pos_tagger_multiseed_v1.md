# Pre-registration: pos_tagger_multiseed_cpu_v1
**Date:** 2026-06-11  **Anchor:** pos_tagger_multiseed_cpu_v1  **Queue:** local_cpu_queue  **Seeds:** 5
## Scientific question
Is substrate-only POS tagging (0.906 single-seed) seed-robust at n=5 -> Tier A? Cycles HDLAB_SEED over the substrate's
stochastic components (codebook init, OOV morphology, context binding).
## Pre-registered bands
HARD-PASS mean tag-acc >= 0.90 AND std <= 0.01 (Tier A). MIDDLE mean>=0.90 std>0.01. HARD-FAIL mean<0.90. UNKNOWN if corpus load fails.
## Calibration rationale
Lexicon/data split are deterministic; only the random tag codebook varies, so std should be tiny (~0.001). >=0.90 mean with
std<=0.01 confirms the categorical NL-boundary result is seed-stable, promoting PP-362 to Tier A.
## N-suffix section
Subprocesses validated pos_tagger cell at 5 seeds; corpus pre-cached (LVH-280 hardening). Per-seed checkpoint. ~5 min.
