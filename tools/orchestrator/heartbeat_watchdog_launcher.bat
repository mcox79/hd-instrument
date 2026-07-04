@echo off
REM Launcher for heartbeat_watchdog, invoked by Task Scheduler (task hd_heartbeat_watchdog).
REM
REM This daemon SCPs marsh@home:C:/dev/hd-instrument/data/remote_state_cache.json
REM to local data/remote_state_cache.json (per its config). Without it, get_metrics
REM across sessions returns stale data.
REM
REM 2026-07-04 ROOT-CAUSE FIX (testbed):
REM  Reference pattern = tools/remote_launchers/remote_state_emitter_launcher.bat
REM  (bat's last line does `start /B pythonw ...` then `exit /b 0`, so the task
REM   action exits clean with the daemon orphaned-alive; the prior version ran
REM   pythonw SYNCHRONOUSLY, keeping the launcher cmd alive as a grand-orphan the
REM   task job object could kill on cmd exit -> unreliable auto-restart).
REM  (1) SINGLETON FIX: the prior `wmic ... /format:csv | findstr ... tokens=2`
REM      loop grabbed `-X` (from `-X utf8` in the cmdline) instead of the PID, so
REM      it NEVER killed a stale instance -> duplicates accumulated. Corrected to
REM      `get ProcessId /value | findstr [0-9]` + `tokens=2 delims==`, which
REM      extracts the real PID (validated against live PIDs 2026-07-04).
REM  (2) pythonw.exe (windowless) per the USER 2026-06-28 windowless mandate.
REM  Logging: heartbeat_watchdog.py.emit() writes directly to its own log file, so
REM  no `>> log` redirect is needed here (mirrors the emitter reference).
REM
REM  NOTE: the redundant task hd_orchestrator_watchdog (direct pythonw, no singleton)
REM  was DISABLED 2026-07-04 to remove the dual-task duplicate source. This launcher
REM  is now the single canonical restarter, and its singleton kills any stale daemon
REM  before spawning exactly one.

setlocal
set PYTHONW=D:\AI\hd-instrument\.venv\Scripts\pythonw.exe
set SCRIPT=D:\AI\hd-instrument\tools\orchestrator\heartbeat_watchdog.py

REM Singleton: kill any existing heartbeat_watchdog python/pythonw processes
REM (correct PID extraction) so exactly one fresh instance runs after launch.
for /f "tokens=2 delims==" %%a in ('wmic process where "(name='python.exe' or name='pythonw.exe') and CommandLine like '%%heartbeat_watchdog%%'" get ProcessId /value 2^>nul ^| findstr /r "[0-9]"') do taskkill /F /PID %%a >nul 2>&1

REM Launch fresh daemon detached; the started process is orphaned-alive when this
REM launcher exits, so Task Scheduler's action completes clean.
start "hd_heartbeat_watchdog" /B "%PYTHONW%" -X utf8 "%SCRIPT%"
exit /b 0
