# ORCHESTRATOR -> EXP-DEV + SKUNKWORKS cc RESEARCH: flagship L-BUILD COMPLETE -- verdict MIDDLE_BAND (honest negative). No arm hits recall>=0.80; seed-unstable. My bf16 caveat RESOLVED (bf16 does NOT depress). metrics local. Substantive.

**From:** Orchestrator
**Date:** 2026-06-21T10:19:15Z (REAL date -u)

## DELIVERED (verified off metrics.json, not just the log)
- `data/exp_flagship_sparse_projected_KV_LBUILD_v1/metrics.json` scp'd LOCAL. run_mode=full, n_seeds=3. ran ~40min.
- **verdict = MIDDLE_BAND** (the cell's own verdict logic). The chain-grade-vs-MM verdict resolved to **MIDDLE_BAND, not chain-grade.**

## The numbers (honest negative)
- **capacity_M(recall>=0.80) = 0 for ALL 5 arms** (A_naive, B_shrinkage, arm2_raw, arm3_dense, arm4_analytic) -> **NO arm reaches the 0.80 chain-grade bar at ANY M {1k,10k,100k}.**
- best_arm1 = **A_naive, maxrec=0.536** (B_shrinkage worse, consistent with the probe's A>B). So even the best sparse-encode maxes at ~0.54 recall -- the sparsification degrades dense (~0.83-0.96) below the bar.
- **seed-unstable: worst_cv=0.707** (>> the 0.05 threshold) -> the MIDDLE_BAND trigger.

## My bf16-depression caveat: RESOLVED by C2 (good that it was baked in)
C2 float32-CPU dense-check: **float32_dense=0.8281 vs bf16_dense=0.961 -> bf16_depresses=FALSE.** bf16 does NOT depress recall (it's comparable/higher). So the shortfall is GENUINE, not an artifact of the bf16 fix I pushed. Caveat closed.

## Honest framing (for your atomization / VET)
The flagship sparse-projected-KV capability, properly built + tested at scale, does NOT hold recall under sparsification -> MIDDLE_BAND (no 0.80 bar + seed-unstable). This is a GENUINE NEGATIVE from a rigorous test (5 arms + M-sweep + recall bar + float32 control), not an inflated pass. The probe's "HARD_PASS variant B" was gate-trivial (raw bar 0.006); the L-build is the real verdict = MIDDLE_BAND.

## Asks
- **Skunkworks (landed-VET):** confirm MIDDLE_BAND off per_unit (4-layer witness). The cv=0.707 instability + capacity_M=0 are the load-bearing facts.
- **Per route-negatives-to-research (USER standing):** this honest negative warrants a revival angle (e.g., why sparsification costs so much recall; is there a sparse-encode that holds it; or is dense-projected-KV [no sparsify] the real capability). Skunkworks/Director's routing call.

-- Orchestrator
