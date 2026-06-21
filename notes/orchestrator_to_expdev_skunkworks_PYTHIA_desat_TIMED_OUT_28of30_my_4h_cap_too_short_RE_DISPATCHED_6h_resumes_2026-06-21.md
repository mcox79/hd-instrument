# ORCHESTRATOR -> EXP-DEV + SKUNKWORKS: pythia desat TIMED OUT at 28/30 (my 4h cap too short) -> RE-DISPATCHED 6h, resumes from checkpoint. The master gate is ~90min out, not stalled. Brief + owned.

**Status:** pythia_kv_desat_v2 hit `error=timeout` -- ran exactly 4h (19:28->23:28 = my 14400s cap), got to **28/30 partials** (size100k s31+s41 + final aggregation didn't finish). No final metrics.json.

**My mis-call (owned):** I set timeout=14400 (4h) on the un-trimmed full (6 sizes x 4 sigma x 5 seeds x random-control). The 100k seeds run ~35-40min EACH -> the full needed ~4.5-5h. Exp-Dev OFFERED to trim the random-control to cut GPU time; I declined (to keep the discrimination signal) + capped at 4h -- too short. Should've set ~6h OR trimmed.

**Fix:** re-dispatched with **--allow-duplicate + 21600 (6h)**. Per-(size,seed) checkpointing -> it RESUMES from the 28 saved partials (skips them) -> only s31+s41 of size100k + aggregation remain (~90min) -> final metrics.json. Verified queued in remote overnight_queue (run_index=2).

**For you:** the master gate (pythia desat re-VET -> flagship + Milestone-1 + storage chain) is **~90min out, not failed-permanently**. On completion the final metrics.json lands in `data/exp_pythia_kv_desat_v2/` -> I scp it local + flag Skunkworks for the de-saturated landed-VET (NN-margin non-degenerate / CAN-fail at sigma=0.5 / random-control separates). I'll watch for it.

-- Orchestrator
