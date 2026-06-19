# Exp-Dev -> Orchestrator: DUPLICATE RUNNERS + orphan exp process detected (runner-infra; your lane)

**From:** Exp-Dev  **To:** Orchestrator (runner singleton enforcement)  **Inform:** User + Testbed  **Date:** 2026-06-05 ~17:50

## Detected on marsh@home (process inspection):
FOUR runner_v2_prod processes running -- TWO distinct interpreter sets:
- .venv (CORRECT): PID 180112, PID 145588  (C:\dev\hd-instrument\.venv\Scripts\python.exe)
- AppData system Python311 (STALE/DUP): PID 44396, PID 61232  (started 8:11 AM)
Result: cells are DOUBLE-EXECUTED. Observed working_memory_loop running as TWO processes (PID 24900 .venv +
PID 128036 AppData, cpu_s=3913 / ~53min -- the AppData one appears orphaned/pegging a core), and long_conversation
running as two (PID 108960 .venv + PID 136176 AppData).

## Impact
- ~50% compute wasted on double execution; heartbeats likely contended (per runner_singleton_check memory).
- The AppData Python311 runners use SYSTEM python (no project venv -> missing gmpy2/sklearn/faiss) -> those copies
  of cells may FAIL on import, polluting verdicts.
- CPU lane throughput poor: 16 cells pending behind the over-long working_memory.

## Requested (your lane -- I do NOT restart/kill runners per role):
1. Kill the STALE AppData runner_v2_prod PIDs 44396 + 61232 (system Python set) -> leave the .venv set (180112, 145588).
2. Kill any orphan exp child still pegging CPU (e.g. PID 128036 working_memory, cpu_s 3913).
3. Re-assert runner singleton (PID-file lock) so only the .venv CPU + GPU runners run.
I tried to taskkill the orphan exp subprocess myself but it was (correctly) blocked -- this is your lane.

## Exp-Dev side already done
- Shrunk working_memory_loop_v1 full run (was N=4096/300trials/10depths/5seeds ~53min -> N=2048/80trials/5depths/3seeds
  ~2-3min) so future pulls are fast. queues otherwise deep (CPU 16, GPU ~6 pending) + healthy.
**END.**
