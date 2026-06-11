# Pre-registration: wave2_rescue_multiseed_sweep_cpu_v1
**Date:** 2026-06-11  **Anchor:** wave2_rescue_multiseed_sweep_cpu_v1  **Queue:** local_cpu_queue  **Seeds:** 5  **Anchors:** 3
## Scientific question
Are the 3 passing Wave-2 rescues (CLS, multidrive VSA-H3, code2 template-conditional) seed-robust at n=5? Promotes D/E->Tier C.
## Pre-registered bands
HARD-PASS all 3 PROMOTE_C (>=4/5 HARD_PASS). MIDDLE 2/3. HARD-FAIL <2.
## Calibration rationale
Each passed cleanly at n=1; n=5 confirms not a lucky seed (>=4/5). Smoke (n=3) showed 3/3 PROMOTE_C.
## N-suffix section
Meta-runner; underlying cells N=8192 numpy. Per-anchor checkpoint. Fast (~minutes).
