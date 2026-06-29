# Local CPU runner needs USER admin to recover — queue is staged + ready

**Status as of 2026-06-29 ~02:25Z (orchestrator agent).**

## What's done (no admin needed; auto-completed overnight)

- **Queue rewritten atomically:** seed_7 lock_in_amp v2 zombie-running → pending. All 13 entries now `pending`. Queue ready to drain the moment a fresh runner is alive.
- **Singleton PID file cleared:** `data/logs/cpu_runner_local.pid` deleted; no longer blocks a fresh runner from starting.
- **Stale heartbeat files cleared:** `heartbeat.cpu_runner_local.json` + `heartbeat.json` — but PID 5776 is still alive and has re-touched them (see below).
- **Backup of pre-cleanup queue.json:** `data/local_cpu_queue/queue.json.bak_zombie_clear_2026-06-29` if rollback ever needed.

## What's stuck (needs USER admin)

PID 5776 (python.exe; created 2026-06-24 09:52 EDT; 3MB RSS; 2 threads; 0 CPU) is wedged in a partial state:
- It heartbeats every ~30-90s (touches `heartbeat.cpu_runner_local.json`)
- But it has not progressed its claimed cell (`substrate_lock_in_amp_phase_diagram_v2_seed_7`) for 3+ hours
- It was launched under S4U/Task-Scheduler lineage — **cannot be killed without admin** (`taskkill /F /T /PID 5776` returned "Access is denied")
- `schtasks /end /tn "\hd_cpu_runner_local"` "succeeded" but did not actually kill the process
- `schtasks /run ...` reports SUCCESS but no new python.exe spawns — Task Scheduler's MultipleInstancesPolicy=IgnoreNew blocks a second instance while PID 5776 lives

PID 5776's parent chain: 5776 (python.exe) → 7628 (python.exe; also wedged) → 8808 (cmd.exe; wedged) → 2552 (unknown; was the legacy launcher pre-schtasks-fix).

## Recovery in the morning (~30 sec USER admin)

```powershell
# 1. Open elevated PowerShell (Run as Administrator)
# 2. Kill the wedged tree (only admin can do this; processes are in S4U lineage)
taskkill /F /T /PID 5776
taskkill /F /T /PID 7628
# 3. Verify dead
Get-Process -Id 5776,7628 -ErrorAction SilentlyContinue
# 4. Start fresh runner via scheduled task (lineage-safe per schtasks-fix doc)
schtasks /run /tn "\hd_cpu_runner_local"
# 5. Verify new runner alive (should see new python.exe with high RSS + heartbeat content updating to fresh ts)
Get-Content "D:/AI/hd-instrument/data/local_cpu_queue/heartbeat.cpu_runner_local.json"
python D:/AI/hd-instrument/tools/runner_status.py --local
```

Within ~30s of the schtasks /run, the new runner should claim one of the 13 pending cells and start work. Lock-in v2 cells x3, task-vector K-cliff x3, schema-family x3, pc-binding-family x3, plus the cortex-hippo bottleneck diagnostic.

## Why this happened (root cause TBD)

The `feedback_runner_zombie_ssh_disconnect_root_cause_FIXED_2026-06-28.md` fix landed earlier today and addressed `start /b python.exe` via SSH. PID 5776 was created 2026-06-24 — predates the fix. Its `start_desktop_runners.cmd` invocation was the old `start /b` pattern from SSH. The schtasks-lineage fix shipped at ~12:43 PDT today; restarts after that point should be SSH-immune. PID 5776 is the last legacy-launched runner; once killed + re-launched via schtasks, future zombies should not recur.

## Verification expected post-recovery

- `python tools/runner_status.py --local` should show `cpu_runner_local OK pid=<new>` with fresh heartbeat
- `data/local_cpu_queue/queue.json` should show 1 entry transitioning to `running` within ~30s
- Within ~30-60 min, first cell should complete and second cell claimed (cells are ~10-15 min each for smoke + ~30-60 min for FULL based on earlier dispatches)

—orchestrator agent
