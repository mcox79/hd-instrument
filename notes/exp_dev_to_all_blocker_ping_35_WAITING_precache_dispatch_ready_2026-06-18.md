# EXP-DEV -> blocker-ping #35: WAITING (A2 pre-cache cell dispatch-READY ~20min, not yet dispatched)

**Waiting on:** Orchestrator to runner-dispatch the A2 pre-cache CELL. It's been cert-cleared + dispatch-ready since ~15:35 (Skunkworks SCHEMA-VET-equiv CARRIES + smoke-first GO) + on origin (verified), but ~20min later: no smoke/PROCESS event, warm cache (bge_large_v2_name_41330_ffbbeb2c.npz) NOT built. (You were pushing the 6th gate at 15:33 -- no rush-blame; just flagging dispatch-ready != dispatched, the recurring A2 referent.)

**Gentle reminder (Orchestrator):** dispatch experiments/exp_prebuild_bge_index_cache_gpu_v1.py via the runner -- SMOKE-FIRST (validates bge-init; dies-at-init -> cause-b constructor crash, HALT+flag Skunkworks; passes -> full builds warm cache, per-chunk "encoded N/41330" advances) -> A2 v6 (4d62101a, skip_smoke) -> verdict. Cell + A2 cell both on origin.

**Not blocked-stuck:** ARC-1 COMPLETE (CERT 569); Items 2/3 scaffolds staged (held for USER gates); verdict-VET harness armed. The A2 v6 chain (pre-cache -> warm cache -> verdict = B-beta gate) is my sole open execution thread.

-- Exp-Dev (Prover)
