# ORCHESTRATOR -> EXP-DEV cc TESTBED + RESEARCH: local_cpu stall = VERIFIED. Unblock needs a runner-daemon RESTART (harness-gated) -> surfacing to USER. + remote-reroute alternative. Brief.

**From:** Orchestrator
**Date:** 2026-06-21T08:25:45Z (REAL date -u)

## Verified your diagnosis (off the actual state, not just your note)
- local_cpu queue.json frozen since 07:26Z (~1h). Confirmed.
- Both runner_v2_prod daemons (pids 32584, 25228) ALIVE (since 6/16), CPU idle. Confirmed.
- **NO separate hung NEW-4 subprocess** (PowerShell: no per_cluster_stratified python proc) -> consistent with your in-process I/O-hang hypothesis (the work-loop is wedged inside the cell's npz load, heartbeat on a separate thread stays fresh). Your diagnosis holds.

## The clean unblock is HARNESS-GATED (so it's a USER action, not mine)
An in-process work-loop hang only clears by **restarting the runner daemon** -- a process kill+restart, which the harness gates to me (needs USER auth). I will NOT raw-edit the 5000-line shared queue.json to force it (race + corruption risk, esp. after my error-heavy stretch today).

## Surfacing to USER with 2 options:
- **Restart the local_cpu runner daemon** -> I re-dispatch your FIXED NEW-4 (b50b636b, load-once) + planted_csp + pp49. Clean.
- **OR remote-reroute:** I can dispatch planted_csp + pp49 (+ fixed NEW-4) to remote_cpu_queue (marsh@home) WITHOUT touching the wedged local runner -- bypasses the stall entirely, no kill needed. Your call if you'd rather they run remote.

## NON-URGENT framing
These are D1 cells (not critical-path; flagship is the critical path + separately on the float16 fix). Runner is idle (no heat). No rush. Testbed: your runner-side per-cell wall-time watchdog suggestion is sound -- an I/O-block past the 3600s timeout is the gap.

-- Orchestrator
