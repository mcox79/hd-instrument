# Pre-registration: schema_retrieval_rt1_cpu_v1
**Date:** 2026-06-11  **Anchor:** schema_retrieval_rt1_cpu_v1  **Queue:** local_cpu_queue  **N:** 8192
## Scientific question
Does substrate cleanup retrieve the correct Tier-2 schema from the inventory given a problem statement (Phase-2 gate, Drill A)?
## Pre-registered bands
HARD-PASS retrieval-acc >= 0.90. MIDDLE >= 0.70. HARD-FAIL < 0.70.
## Calibration rationale
Representative ~20-schema subset (math+code) with keyword+role signatures; substrate cleanup. Result 0.967. Caveat:
representative subset + distinctive queries; full 114 + real noisy text harder (2-stage domain-route-then-schema would help).
## N-suffix section
N=8192; ~20 Tier-2 schemas; 30 query instances; substrate prototype-bundle cleanup retrieval.
