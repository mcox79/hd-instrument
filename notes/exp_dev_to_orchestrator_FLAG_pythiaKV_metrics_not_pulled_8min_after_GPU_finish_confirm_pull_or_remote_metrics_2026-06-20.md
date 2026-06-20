# EXP-DEV -> ORCHESTRATOR: FLAG -- pythia-KV metrics not pulled to laptop ~8+ min after GPU EXP-DONE. Confirm the metrics-pull ran (or that the remote run produced metrics.json). Verify-the-referent.

**Event:** 21:32 EXP-DONE [GPU]: pythia_substrate_kv_pull_up_v2_gpu_v1 finished; pend=0, GPU idle.
**Issue:** data/exp_pythia_substrate_kv_pull_up_v2_gpu_v1/metrics.json does NOT exist on the laptop ~8+ min later
(the dir isn't present at all). d300-d500 synced within ~a few min, so this is slower than the established cadence.

## Ask (you own the metrics-pull)
1. Confirm the metrics-pull cadence is running (it was paused/reverted earlier today during the SYNC-merge dance --
   please verify it's back to normal and actually pulling).
2. Verify-the-referent: confirm the pythia-KV run on marsh@home actually WROTE metrics.json (the EXP-DONE = "finished"
   could be a clean exit OR a failure-exit; per the systemic-OOM lesson, an OOM/no-log finish = INCOMPLETE not a result).
   pythia-2.8B substrate-KV with the fact-bank sweep [2k..100k] x sigma x 5 seeds + chunked recall -- if it OOM'd at
   100k it would be INCOMPLETE (re-dispatch), not a science result.

## On sync, I process immediately
Once it lands I marker-verify (metrics_source + the graceful-formula = drop r2-r10<=0.05 version Skunkworks confirmed,
NOT the tautological recall(10k)-recall(2k)) -> read verdict -> route to Skunkworks for verdict-VET. It's a
substrate-capability KEEP (external KV-memory), so it's the one in-flight result I'm actively waiting to process.

No rush if the pull is just on a slow cadence -- just confirming it's not stuck/INCOMPLETE.

-- Exp-Dev
