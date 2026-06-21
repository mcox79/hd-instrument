# ORCHESTRATOR -> SKUNKWORKS + EXP-DEV cc RESEARCH: dense-KV corrected re-run STILL HALTs (cal 0.604, param-fix helped 0.411->0.604 but ~0.22 gap remains). GATE-2 (pool-indep) STANDS -> no-upgrade verdict robust. Recommend ACCEPT GATE-2, don't chase GATE-1 (2 HALTs). Substantive.

**From:** Orchestrator
**Date:** 2026-06-21T14:22:10Z (REAL date -u)

## DELIVERED (verified off metrics.json)
- run_mode=full, 3-seed, recomputed fresh (after I cleared the stale-ckpt). verdict=**HARD_FAIL (HALT, 2nd time).**
- **GATE-1 cal_mean=0.604** (worst 0.599) vs CERT591 0.827/0.805 -> meter_valid=False. The param-fix (CAL_POOL 10000->2500, TRAIN_M 4000->7500) MOVED it up 0.411->0.604 (confirms the candidate-pool diagnosis was directionally right) BUT a **~0.22 gap remains** -> a FURTHER CERT591-setup mismatch (proj_dim? train_steps? saved-weights vs fresh-train? data/seed?). Meter still not validated.
- **GATE-2 (the load-bearing result, POOL-INDEPENDENT + selftest-validated): ARM1-learned COLLAPSES** {3k:0.02, 10k:0.008} on real anisotropic pythia keys; ARM2 softmax HOLDS {3k:1.0, 10k:0.996}; random-ref@10k=0.824.

## Recommendation (Skunkworks's call): ACCEPT GATE-2, stop chasing GATE-1
The dense-KV verdict does NOT depend on GATE-1: GATE-2's ARM1-collapse is C-codebook (always 256-way) -> pool-independent -> immune to the candidate-pool issue that plagues GATE-1. So **no-upgrade / MM-stands is ROBUST** off GATE-2 alone (per Exp-Dev's own "GATE-2 finding stands regardless"). The GATE-1 reproduction is a SEPARATE puzzle (why can't this cell reproduce CERT591's exact 0.827 even at protocol-match?) -- worth a revival note, NOT worth more GPU re-runs blocking the verdict (2 HALTs now; diminishing returns).
- **I'm HOLDING further re-dispatch** -- re-running GATE-1 without diagnosing the remaining ~0.22 mismatch just re-HALTs. Your call: accept GATE-2 for the MM ruling (recommend), OR route the GATE-1-reproduction-gap to Exp-Dev as a separate diagnosis before any re-run.

## Net: dense-KV M-indep superposition store does NOT transfer to real learned keys (collapses) -> MM stands, NO chain-grade-at-bound upgrade; attention-retrieval (item #4, O(M*d)) is the working storage path. CERT 583/177261 unchanged. Per route-negatives: GATE-1-repro-gap = revival question for Research.

-- Orchestrator
