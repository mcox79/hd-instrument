# Queue Health decisions — 2026-05-22

## Cycle 197 (07:52) — overnight catch-up + 6h gap noted

**Observed:**
- Snapshot fresh (ts 07:51:50, gpu.heartbeat.ts 07:51:43). GPU pid 7760 alive, running `wave14d_multi_task_cl_v11_per_batch_ema` started 07:23:21 (wall ~28m).
- Pending dropped 14 -> 6 overnight (runner consumed 8 experiments while I was looping at 5-min cadence — chat was hot enough that I never saw the transitions in a single cycle, just the cumulative drop).
- Visible 5-line GPU log shows: NUMFACTS_1000 DONE 01:22:47 (170s), multihop_depth_200 DONE 01:23:21 (34s), continual_8N_5000edits START 01:23:21, then v11_per_batch_ema START 07:23:21. **6-hour gap between continual_8N_5000edits START and the next START with no visible DONE/FAIL line.**
- CPU unchanged (exited since 09:56 yesterday, pending=0, invariant n/a).

**Decision: no action.**
- Runner has a 4h experiment timeout. Expected behavior at ~05:23: kill continual_8N_5000edits, mark outcome, claim next. The 2-hour residual gap (~05:23 -> 07:23) is unexplained by the 5-line window — either (a) the runner sat idle waiting for queue items that weren't ready (unlikely, pending was 14+), (b) intermediate log lines (DONE/FAIL for continual_8N_5000edits + idle polls) scrolled out of the recent_log_lines window, or (c) the experiment legitimately ran ~6h because the timeout wasn't enforced.
- (b) is most likely — recent_log_lines is capped at 5 entries; with 3+ events between 05:23 and 07:23 (FAIL line, possible idle polls, new START), the FAIL would have rolled off.
- Current GPU state is healthy: new experiment claimed, heartbeat fresh, wall well under 4h. No alert.
- Not in scope to dig into runner queue logs to verify (would require SSH; not warranted for past-event diagnostic when current state is clean).

**Lesson noted (not memory-worthy yet):** my 5-min cycle granularity + the snapshot's 5-line log window means multi-event sequences within a single cycle window are invisible. If I see queue_pending_count drop by N>1 between cycles, the intermediate experiment outcomes are in metrics/event files but not in the snapshot — for Queue Health that's fine (I care about runner liveness, not verdict content), but worth flagging if I ever need to confirm an experiment actually ran to completion vs was killed.

PROT compliance this cycle: PROT-001/002/003 already done. PROT-004 through PROT-008 apply to Strategy, not Queue Health. notes/active_protocols.md unchanged from yesterday's read.
