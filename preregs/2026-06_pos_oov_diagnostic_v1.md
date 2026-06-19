# Pre-registration: pos_oov_diagnostic_cpu_v1
**Date:** 2026-06-11  **Anchor:** pos_oov_diagnostic_cpu_v1  **Queue:** local_cpu_queue
## Scientific question
Is the POS 0.929 ceiling a DATA/OOV limit or a METHOD limit? Splits accuracy by in-vocab vs OOV; projects to full-PTB OOV rate.
## Pre-registered bands
HARD-PASS in-vocab >= 0.95 AND projected@2.5%OOV >= 0.95 (STRONG achievable via full PTB; data-ceiling). MIDDLE in-vocab >= 0.93. HARD-FAIL < 0.93.
## Calibration rationale
Result: in-vocab 0.946, OOV 0.749, projected@2.5%OOV 0.941. STRONG (0.95) needs BOTH lower OOV (full PTB) AND in-vocab>0.96
(richer transitions/features) -- not purely a data ceiling. Refines the earlier data-ceiling hypothesis.
## N-suffix section
nltk PTB sample; v3-HMM tagger; accuracy split by training-vocab membership.
