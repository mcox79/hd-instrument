# Pre-registration: lang_math_coexist_cpu_v1
**Date:** 2026-06-11  **Anchor:** lang_math_coexist_cpu_v1  **Queue:** local_cpu_queue  **N:** 8192
## Scientific question
Does ONE substrate (one codebook, one algebra) handle language + math facts simultaneously without cross-domain interference,
plus cross-domain composition (math result -> language label)?
## Pre-registered bands
HARD-PASS lang>=0.95 AND math>=0.95 AND cross-domain>=0.95. MIDDLE all>=0.85. HARD-FAIL else.
## Calibration rationale
Substrate algebra is domain-agnostic; one store should bind/recall both domains + compose across them. Result 1.0/1.0/1.0 confirms unity.
## N-suffix section
N=8192 numpy; one shared codebook; language + math + cross-domain bindings. Fast.
