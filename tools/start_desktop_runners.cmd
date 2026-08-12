@echo off
REM Start both desktop runners (GPU + remote-CPU) via Task Scheduler.
REM
REM HISTORY 2026-06-28: previous version used `start "" /b .venv\Scripts\python.exe ... > out.log 2>&1`
REM which has TWO load-bearing bugs on Windows when invoked via SSH:
REM   1. `python.exe` (not pythonw.exe) inherits the parent cmd.exe console.
REM   2. When the ssh-launched parent cmd.exe exits, the `start /b` child receives
REM      CTRL_CLOSE_EVENT and dies within seconds (heartbeat froze at T+0, cell log
REM      stopped at T+6s on multiple 2026-06-28 episodes).
REM
REM FIX: delegate to the scheduled tasks `\hd_gpu_runner_0` and `\hd_cpu_runner_0`
REM which already exist (calendar trigger 3am daily + logon trigger). Task Scheduler
REM owns the process tree (Services-session lineage) so SSH disconnect does NOT
REM kill the runner. The launcher bats use pythonw equivalence via -X utf8 and
REM properly detached process startup; we know this path works (verified
REM 2026-06-28 12:41: schtasks /run produced PID 28840 that survived ssh disconnect
REM and heartbeated within 30s).
REM
REM Singleton guard in runner_v2_prod.py (--singleton-pid-file) still protects
REM against the case where the scheduled task is already running.

schtasks /run /tn "\hd_gpu_runner_0"
schtasks /run /tn "\hd_cpu_runner_0"
