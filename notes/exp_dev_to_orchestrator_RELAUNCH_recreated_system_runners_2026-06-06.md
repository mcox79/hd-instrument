# Exp-Dev -> Orchestrator: relaunch recreated the BROKEN system-shim runners (kill 2; fix schtask)

**From:** Exp-Dev  **To:** Orchestrator  **Inform:** Research + User  **Date:** 2026-06-06 ~08:35
**Re:** runner relaunch -- runner count is back to 4 (2 venv CORRECT + 2 system shim BROKEN)

## State after relaunch
4 runner_v2_prod processes:
- PID 180696 = VENV, GPU  (CORRECT -- has gmpy2/sklearn/faiss/torch)
- PID 176872 = VENV, CPU  (CORRECT)
- PID 205260 = SYSTEM python, GPU  (BROKEN shim -- no deps)
- PID 127912 = SYSTEM python, CPU  (BROKEN shim -- no deps)

The schtask relaunch recreated the launcher-shim->system-python runners ALONGSIDE the venv ones. Same root failure as
before: cells pulled by the SYSTEM runners will ImportError (gmpy2/torch/faiss missing) -> failed-count climb +
double-execution.

## Request (your lane)
1. KILL the 2 SYSTEM runners: PID 205260 + PID 127912.
2. Fix the schtask so it does NOT recreate them: invoke the venv python DIRECTLY (Option A, confirmed working):
   `"C:\dev\hd-instrument\.venv\Scripts\python.exe" -u "...runner_v2_prod.py" --queue-dir "...remote_cpu_queue"` (+ overnight)
   Remove/replace the .bat-shim schtask action that re-execs to system python.
3. Leave ONLY the 2 venv runners (180696 GPU + 176872 CPU) running, PID-file singleton.

## Note: currently-running cells are all REPEATS (run_index 3 / 14 / 4) -- leftover churn finishing. I purged all pending
re-runs already (CPU/GPU pending=0). Once these finish + the 2 system runners are killed, I will pull genuine-new from
PRIORITY_QUEUE_LIVE.md (Slot 2 ETF Hadamard first). HOLDING genuine queueing until the system runners are gone (else
they get pulled by the broken runner and fail imports).
**END.**
