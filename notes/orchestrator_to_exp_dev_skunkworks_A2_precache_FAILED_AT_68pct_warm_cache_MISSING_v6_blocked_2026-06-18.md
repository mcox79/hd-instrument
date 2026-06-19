# Orchestrator -> Exp-Dev + Skunkworks: A2 pre-cache FAILED at 68% (NOT complete). USER caught me about to dispatch v6; the actual state is the cache is MISSING and v6 would hit the same v4/v5 hang.

VERIFIED STATE (just now via direct ssh):
- Pre-cache log mtime: 6/18/2026 7:37:06 PM (= ~3h ago) -- frozen at chunk_27
- Last log line: "encoded 28000/41330 (68%) chunk_27 83.3s"
- NO further progress; NO PASS verdict line; NO save_cache line
- Cache file bge_large_v2_name_41330_ffbbeb2c.npz: MISSING (only written at end of all 42 chunks)
- Cell metrics.json: NOT WRITTEN
- Runner heartbeat: status=idle, current=null (moved on)

So between chunk_27 and chunk_28, the pre-cache cell died or got killed. Hypotheses:
(a) Runner_v2_prod's per-cell timeout fired (the dispatch had 3600s = 60 min; the pre-cache started ~18:37 UTC + chunks averaged 100s each + by chunk_27 wall time was ~50 min in -- close to timeout?)
(b) Memory exhaustion mid-encode
(c) Some other silent exit between chunks

The "EXP-DONE 16:38" Exp-Dev mentioned in chat likely reflects the RUNNER releasing the slot (after its timeout killed the cell), NOT the cell succeeding. The runner heartbeat going idle + current=null is consistent with runner-side termination.

V6 BLOCKED until pre-cache completes:
- Dispatching A2 v6 now -> cell hits rebuild_index_cached -> cache MISSING -> cold rebuild -> SAME HANG as v4/v5
- Cannot proceed until warm cache is built

NEXT STEPS:
1. Verify hypothesis (a) by checking the timeout-vs-elapsed math + the runner_v2_prod side
2. Re-dispatch pre-cache with LONGER timeout (~7200s = 2h to cover the 70+ min estimated runtime)
3. THEN dispatch A2 v6

SELF-CATCH on the bjeiibu35 poll: my regex was `PASS\b|HARD_FAIL|warm cache built|encoded 41330/41330|Traceback|ERROR` — but the actual end-of-cell marker (Exp-Dev's verdict line) wasn't in my filter. So the poll never fired even though the cell died. Compounded with the silent runner-side termination = silent gap. The verify-running-PERIODICALLY discipline caught 44% + 68% but missed COMPLETION because the regex didn't match the actual death signature.

Standing for Exp-Dev/Skunkworks guidance on next step (re-dispatch with longer timeout vs investigate cell behavior).

-- Orchestrator (Custodian)
