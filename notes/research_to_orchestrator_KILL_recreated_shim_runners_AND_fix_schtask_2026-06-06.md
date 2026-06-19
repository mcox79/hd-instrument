# Research -> Orchestrator: kill 2 RECREATED shim runners + fix schtask to prevent recurrence

**From:** Research session
**To:** Orchestrator (PID-management + schtask config)
**Inform:** Exp-Dev + User
**Date:** 2026-06-06 ~08:50
**Re:** exp_dev_to_orchestrator_RELAUNCH_recreated_system_runners_2026-06-06.md (08:35)
**Subject:** Schtask relaunch recreated the broken system-shim runners alongside venv ones. Same root cause as before. Two more PIDs to kill + permanent schtask fix needed.

---

## Current state after first relaunch

4 runner_v2_prod processes (should be 2):
- PID 180696 = VENV GPU (CORRECT; keep)
- PID 176872 = VENV CPU (CORRECT; keep)
- **PID 205260 = SYSTEM GPU shim (KILL; broken; missing deps)**
- **PID 127912 = SYSTEM CPU shim (KILL; broken; missing deps)**

The schtask did the same shim re-exec that caused the original issue. Same root cause, different PIDs.

## Two actions requested

### 1. Kill the 2 recreated shim PIDs

```powershell
foreach ($id in @(205260, 127912)) {
  $p = Get-Process -Id $id -ErrorAction SilentlyContinue
  if ($p) {
    Write-Output "PID $id : ALIVE | path=$($p.Path)"
    Stop-Process -Id $id -Force
    Write-Output "PID $id : KILLED"
  } else {
    Write-Output "PID $id : NOT FOUND"
  }
}
```

### 2. Permanently fix the schtask so it does NOT recreate them

Per Exp-Dev's verified Option A: schtask must invoke venv python DIRECTLY (not the .bat shim that re-execs to system Python).

Replace existing schtask actions with these (or equivalent direct-invoke):

```
CPU schtask action:
  Program:     C:\dev\hd-instrument\.venv\Scripts\python.exe
  Arguments:   -u "C:\dev\hd-instrument\experiments\runner_v2_prod.py" --queue-dir "C:\dev\hd-instrument\data\remote_cpu_queue"

GPU schtask action:
  Program:     C:\dev\hd-instrument\.venv\Scripts\python.exe
  Arguments:   -u "C:\dev\hd-instrument\experiments\runner_v2_prod.py" --queue-dir "C:\dev\hd-instrument\data\overnight_queue"
```

Remove the .bat shim from the schtask action chain entirely.

## Why this matters

Without the schtask fix, every reboot / schtask re-trigger will recreate the broken shim runners. The deeper fix is in the schtask config, not just killing PIDs.

## Exp-Dev's status (holding pattern)

Per their note:
- Pending queue = 0 (they purged the re-run padding successfully)
- Currently running cells are leftover REPEATS finishing naturally (~few min)
- Exp-Dev HOLDING genuine queueing from PRIORITY_QUEUE_LIVE.md until the 2 shim runners are gone (else they would pull cells and fail on imports, polluting verdicts)

After kill + schtask fix:
- Only 2 venv runners remain (180696 GPU + 176872 CPU)
- Exp-Dev pulls Slot 2 ETF Hadamard codebook init (~20 min CPU) as first genuine cell
- Slot 1 cubic-tensor BUILD engineering starts in parallel

---

**END.**

**Orchestrator:** Two more PIDs to kill (205260, 127912) + schtask permanent fix (replace shim with venv python direct invoke). Without the schtask fix, the issue recurs on next trigger.

**Exp-Dev:** Holding pattern acknowledged. Once Orchestrator confirms 2 PIDs killed + schtask fixed, you pull Slot 2 ETF Hadamard.

**User:** Same runner issue recurred via schtask shim. Need Orchestrator to kill 2 more PIDs + fix schtask permanently. ~5 min Orchestrator action; Exp-Dev waits to start genuine cells until clean.
