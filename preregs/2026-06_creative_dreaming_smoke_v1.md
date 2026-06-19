# Pre-registration: creative_dreaming_smoke_cpu_v1
**Date:** 2026-06-11  **Anchor:** creative_dreaming_smoke_cpu_v1  **Queue:** local_cpu_queue  **N:** 8192
## Scientific question
Does substrate offline-replay (DREAMING) generate novel + coherent concept recombinations (role-filler) without an LLM?
## Pre-registered bands
HARD-PASS >= 5/20 novel AND coherent. MIDDLE >= 2. HARD-FAIL < 2.
## Calibration rationale
Coherence = recalled filler type-consistent with role AND substrate reconstructs the recombination via cleanup (no-LLM,
substrate-checkable). Result 19/20. Existence proof (substrate recombines + reconstructs novel type-consistent concepts);
honest caveat: not a deep semantic-interestingness judgment.
## N-suffix section
N=8192 numpy; 100 role-filler concepts; offline recombination + cleanup reconstruction.
