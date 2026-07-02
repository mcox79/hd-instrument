@echo off
REM remote_state_emitter launcher for Task Scheduler - survives reboot without login
REM
REM Pattern mirrors gpu_runner_0_launcher.bat (SYSTEM-owned Task Scheduler entry
REM triggered ONSTART + ONLOGON). Uses pythonw.exe so no console window opens.
REM
REM Root cause fix (2026-07-02, testbed): the ONLOGON-only trigger from the
REM original install script failed to restart the emitter after a reboot with
REM no interactive login. Result: remote_state_cache.json snapshot_ts froze at
REM 2026-06-29T10:06:34 for 3 days while local SCP happily copied stale content.
REM
REM SINGLETON GUARD: emitter script has no PID-file lock, so we defend with a
REM lightweight tasklist check before spawning. If a pythonw.exe already runs
REM remote_state_emitter.py, exit 0 without launching a duplicate.

setlocal
set EMITTER=C:\dev\hd-instrument\tools\orchestrator\remote_state_emitter.py
set PYTHONW=C:\dev\hd-instrument\.venv\Scripts\pythonw.exe

REM Singleton check: bail if another instance is already running.
for /f "tokens=2 delims=," %%A in ('wmic process where "name='pythonw.exe'" get ProcessId^,CommandLine /format:csv 2^>nul ^| findstr /I "remote_state_emitter"') do (
  echo [emitter-launcher] existing pythonw pid found; exiting 0
  exit /b 0
)

start "hd_remote_state_emitter" /B "%PYTHONW%" "%EMITTER%"
exit /b 0
