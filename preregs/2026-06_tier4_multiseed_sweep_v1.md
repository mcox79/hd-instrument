# Pre-registration: tier4_multiseed_sweep_cpu_v1
**Date:** 2026-06-11  **Anchor:** tier4_multiseed_sweep_cpu_v1  **Queue:** local_cpu_queue  **Seeds:** 5  **Anchors:** 4
## Scientific question
Are the 4 new Tier-4 passes (Crystallized, ExcitabilityGated, code2-adversarial, key-rotation-10K) seed-robust at n=5 -> Tier C?
## Pre-registered bands
HARD-PASS all 4 PROMOTE_C (>=4/5 HARD_PASS). MIDDLE 2-3/4. HARD-FAIL <2.
## Calibration rationale
Each passed n=1 at FULL params. NOTE: full-params required (smoke uses smaller K/writes that under-stress the cliff -> smoke
under-reports excitability/crystallized; verified full-params seed 2,3 = HARD_PASS). Run is FULL mode (not smoke).
## N-suffix section
Meta-runner; 4 numpy cells x 5 seeds at full params. Per-anchor checkpoint. ~10-15 min.
