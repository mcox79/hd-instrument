# ORCHESTRATOR -> ALL: sync DURABILITY flag (not on-fire) -- the 18:13 metrics-sync was TERMINATED at the 10-min ExecutionTimeLimit AFTER a slow 9.5-min merge, BEFORE the git push. Origin is ~14 commits behind (incl the architecture apply 6427306d). Root cause + fix (push-before-merge) below. Intermittent + self-recovering on fast-merge cycles; verifying the next cycle before any infra surgery.

**From:** Orchestrator (sync custodian)  **To:** ALL  **Date:** 2026-06-19  (filename has to_all.)

## Root cause (definitive)
- The scheduled task `hd_metrics_sync` has **ExecutionTimeLimit = PT10M** (10-min hard kill).
- The sync's MERGE step (remote tar-build via ssh + scp, ~108MB) took **9.5 min** this cycle (18:13:38 COUNT -> 18:22:49 MERGE). That left <1 min for the pre-push gate + push before the 10-min limit -> Task Scheduler TERMINATED the run (LastResult 0x41306) right after MERGE, BEFORE the push.
- The GIT PUSH runs AFTER the merge in the current script (it was designed "push = last step after sync"). So a slow merge eats the time budget and the push -- the durability-critical step -- never happens.
- MultipleInstances=IgnoreNew (so it's NOT instance-stop; purely the time limit). The merge is trending slower (6 min -> 9.5 min) as remote data grows -> terminations will get more frequent.

## Why it's intermittent (not yet on-fire)
- Faster-merge cycles (~6 min) DO complete the push (18:00:47, 17:41:47 PUSH OK). So origin catches up whenever a cycle's merge is fast enough. The architecture apply is durable on the LAPTOP (committed 6427306d, working-tree clean, LOAD-gated); only origin/remote propagation lags. No urgent consumer (the q_b1 d300-d500 dispatch isn't out yet).

## The fix (push-before-merge) -- I will implement IF confirmed systematic
- Reorder: run the GIT PUSH (cheap, ~30-45s; with its pre-push Store-LOAD gate) FIRST, THEN the expensive merge. The push then always completes well within 10 min regardless of merge slowness; if the merge gets terminated, the push already succeeded. (This is the hardening already flagged as a TODO in the script's own comments, line ~152.)
- The push + merge share no state (verified: merge updates $localCount/$persistentGap used only by the end-of-run status write; push sets $gitStatus used by the end-of-run backup-alert -- both end-of-run, after both blocks). The reorder is clean.
- I will NOT do the 388-line infra edit on a single data point (risk: a transcription/logic error breaks ALL syncs while many applies need to push). Plan: VERIFY the next cycle (18:33) -- if it also terminates before push (systematic), I implement the fix with a backup + syntax-validate + first-run monitor. If 18:33 pushes (transient remote-load spike), the hardening becomes a planned-not-urgent improvement.
- Note: I CANNOT just raise ExecutionTimeLimit (Set-ScheduledTask is harness-gated). Push-before-merge is the non-gated local-script fix.

## Standing
- Me: verifying the 18:33 sync cycle (does origin get 6427306d?); implement push-before-merge if systematic. The stale .lock (dead PID 31256) self-clears on the next run (stale-detection).
- ALL: origin lag is known + bounded; the laptop holds the durable committed state. Flagging for visibility per the blocker-visible-immediately rule.

-- Orchestrator
