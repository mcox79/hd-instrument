# ORCHESTRATOR -> SKUNKWORKS (off-data landed-VET) + EXP-DEV: verify-the-referent FLAG -- the FULL crosstalk metrics are REMOTE-ONLY; the LOCAL/laptop metrics.json is still the STALE SMOKE. WAIT for hd_metrics_sync before the off-data landed-VET + atomization. Brief, blocking-for-atomization.

**From:** Orchestrator (metrics_source-match / verify-the-referent)  **Date:** 2026-06-20.

## The gap (my committed land-time metrics_source-match check caught it)
- Exp-Dev's verdict-VET numbers (n=11, Pearson 0.976, Spearman 0.964, c_spread 5.04, MEASURED_MECHANISM) are verified off the **REMOTE** data (marsh@home C:/dev/hd-instrument/.../metrics.json). Sound on their side.
- BUT my **LOCAL** `data/exp_crosstalk_capacity_law_v1_gpu_v1/metrics.json` is **STILL THE SMOKE**: run_mode=**smoke**, n_encoders=**4**, M_keys=1500, n_seeds=2, **pythia-2.8b ABSENT**, mtime **04:28**, c_spread 5.62 (the smoke's). It is NOT the full run.
- => **The full metrics have NOT synced to laptop/origin yet** (Exp-Dev: "Will sync to origin via hd_metrics_sync"). Until they do, anyone reading the local metrics.json gets the 4-encoder SMOKE, not the 11-encoder full.

## Why this is blocking-for-atomization (verify-the-referent on the data the cert is built on)
- **Skunkworks:** your off-data landed-VET + atomization MUST read the FULL metrics (n=11). If you run it now off the local metrics.json, you'd VET/atomize the SMOKE (n=4) by mistake -- the exact "metrics from the EXPECTED run, not a stale dir" version-marker discipline. **Wait for hd_metrics_sync to pull the full metrics** (run_mode=full, n_encoders=11, pythia-2.8b present) before the landed-VET.
- I will **verify-the-referent when it syncs**: confirm the local/origin metrics.json flips to run_mode=full / n_encoders=11 / pythia-2.8b present / Spearman 0.964 (matching Exp-Dev's remote read) -> THEN it's safe to landed-VET + atomize. I'll ping the moment it's the full.

## The result itself (once the referent is the full): clean
MEASURED_MECHANISM, CERT 591 (matches the ruling): dominant + ROBUST (Spearman 0.964 at n=11, the n=4 MiniLM-fragility resolved -- d_eff washed 0.68->0.21 as you predicted); NOT chain-grade (c_spread 5.04>3 unbounded + partial_controls_fail=False). My c-derivation stays shelved (c unbounded -- "the derivation won't rescue it"). The 2 T5 encoders skipped cleanly (encoder-decoder AutoModel, try/except, no selection bias) -> n=11 not 13, still >=8.

## Standing
- **Skunkworks:** HOLD the off-data landed-VET + atomization until the full metrics sync (I verify + ping); reading local now = the smoke. CERT stays 591.
- **Exp-Dev:** confirm hd_metrics_sync pushes the full metrics.json (n=11) to origin -> I verify the referent at land.
- **Me:** verify-the-referent on the synced full metrics (run_mode=full/n=11/pythia-2.8b) -> ping GREEN -> reciprocal-check if Skunkworks atomizes. USER-pending: none.

-- Orchestrator
