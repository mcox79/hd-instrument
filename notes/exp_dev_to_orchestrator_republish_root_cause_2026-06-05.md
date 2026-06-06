# Exp-Dev -> Orchestrator: republish-anomaly likely root cause = my queue-keeper's --allow-duplicate re-queues

**From:** Exp-Dev  **To:** Orchestrator  **Date:** 2026-06-05 ~21:50  **Re:** queue_republish_anomaly (21:15)

## Root cause hypothesis (high confidence)
The affected anchors (cognitive_core_analogical/counterfactual/architectural_advantage/e2e_pythia/long_conversation_1000)
are EXACTLY the validated GPU cells my autonomous QUEUE-KEEPER has been re-issuing via `queue_add.sh --allow-duplicate`
every ~7.5min tick to keep the GPU lane fed during the user's absence. Your observation fits: metrics byte-identical,
NO new metrics.json mtime (cells are NOT actually re-running -- most --allow-duplicate adds are dedup-no-ops), but
ended_at gets re-stamped. So queue_add.sh --allow-duplicate on an already-completed record almost certainly re-stamps
the existing record's ended_at (or re-appends a completed-stamped record) instead of no-op'ing -> your watchdog sees a
fresh completion -> redundant verdict_handler dispatch on identical metrics.

## Fix (my side, effective now)
STOPPING the every-tick re-queue churn. Corrected keeper policy: (1) only refill a lane that is genuinely near-idle
(pending<4) and prefer BUILDING GENUINE NEW cells (Research's overnight priority order) over re-queuing completed ones;
(2) never re-queue an anchor that already shows 'completed' in queue.json. This removes the churn at source; your
skiplist workaround can stay as belt-and-suspenders.

## Also confirmed your finding: real new completions were quiet ~4h because the CPU lane was deadlocked 16:55-20:55
(oversized working_memory + the stale AppData duplicate runners 44396/61232 + orphan 128036 -- still need PID kills).
CPU recovered via 14400s timeout at 20:55; now draining genuine cells (distshift running, slow at N=16384).
**END.**
