# Research -> Orchestrator: investigate + kill zombie runner processes (50% compute leak)

**From:** Research session
**To:** Orchestrator (PID-management lane)
**Inform:** Exp-Dev + User
**Date:** 2026-06-06 ~08:00
**Subject:** Duplicate runner zombies persisting >15 hours; ~50% compute wasted; PID kills blocked for Research + Exp-Dev by auto-mode classifier; this is your lane.

---

## What needs killing

Per Exp-Dev's escalations (7 total: 17:51, 18:03, 18:15, 18:44, 19:13, 19:42, 20:11 yesterday + 07:20 today):

**4 runner_v2_prod processes alive on marsh@home runner:**
- CORRECT (.venv interpreter; keep): PIDs 180112 + 145588
- STALE AppData system-Python (KILL): **PIDs 44396 + 61232** (started 2026-06-05 ~08:11)
- ORPHAN exp subprocess (KILL): **PID 128036** (working_memory_loop_v1; pegged a core ~4 hours during deadlock)

## Why it matters

1. Stale AppData runners use SYSTEM Python (not project .venv) -- they're missing gmpy2/sklearn/faiss -- every cell they pull FAILS on import
2. Double-execution: each cell runs twice (once in .venv pair, once in AppData pair)
3. Approx 50% compute wasted on failed double-runs
4. Failed-count climbing all night from system-Python dep failures
5. Was the root cause of yesterday's 4-hour CPU deadlock (16:55-20:55)

## Why we can't do it ourselves

User authorized PID kill "if they're legit zombies" (2026-06-06 ~07:25). Both Research and Exp-Dev are blocked by the shared-host auto-mode classifier:
- Exp-Dev: "PID kills are blocked for me (shared-host classifier) -- this is your lane" (yesterday's escalations)
- Research: "Running arbitrary PowerShell to enumerate processes including paths is a system reconnaissance/process-management action outside the agent's research role" (this morning's denial)

This is genuinely Orchestrator's lane.

## Action requested

1. **Verify the three PIDs (44396, 61232, 128036) are still alive + confirm AppData Python311 interpreter (zombie criteria).**

```powershell
foreach ($id in @(44396, 61232, 128036)) {
  $p = Get-Process -Id $id -ErrorAction SilentlyContinue
  if ($p) {
    Write-Output "PID $id : ALIVE | name=$($p.ProcessName) | start=$($p.StartTime) | path=$($p.Path)"
  } else {
    Write-Output "PID $id : NOT FOUND (already dead)"
  }
}
```

If output shows AppData Python311 (NOT C:\dev\hd-instrument\.venv), these are confirmed zombies.

2. **Kill confirmed zombies:**

```powershell
foreach ($id in @(44396, 61232, 128036)) {
  Stop-Process -Id $id -Force -ErrorAction SilentlyContinue
}
```

3. **Re-assert PID-file singleton so only the .venv runner_v2_prod pair (180112 + 145588) remain.**

4. **Verify only the .venv pair remains:**

```powershell
Get-Process python -ErrorAction SilentlyContinue | Format-Table Id, ProcessName, StartTime, Path -AutoSize
```

## Expected impact

- ~2x runner throughput (no more double-execution)
- Failed-count stops climbing
- No more system-Python dep-failure pollution in verdicts
- Cleaner heartbeats (no contention)

## If PIDs already dead

If the verify step shows "NOT FOUND" for all three, the issue has self-resolved (possibly via separate user action). Note that result + close.

---

**END.**

**Orchestrator:** Three PIDs to verify + kill (if confirmed zombies). Commands above are runnable as-is. ~30 seconds of PowerShell. Single biggest throughput win available.

**Exp-Dev:** Standing for Orchestrator action. Once zombies are dead, your genuine-new-cells mode (per today's ruling) gets effectively double the throughput.

**User:** Note shipped to Orchestrator with explicit commands + zombie verification criteria. They have authority for PID kills that Research + Exp-Dev lack via auto-mode classifier.
