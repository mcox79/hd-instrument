@echo off
REM Launcher for the dashboard supervisor. Intended as the hd_dashboard task action
REM (Program/script = this .bat), replacing the direct `pythonw -m uvicorn ...`
REM action -- see the elevated repoint command in the testbed report.
REM
REM 2026-07-04 ROOT-CAUSE FIX (testbed):
REM  Before: hd_dashboard ran uvicorn DIRECTLY (no supervisor, no auto-restart of a
REM  dead worker) while a supervisor.py was ALSO started manually -> two divergent
REM  launch paths = the duplicate-accumulation setup. A duplicate worker whose SSH
REM  poller died then served BLANK gpu_util/last_poll_ok while holding port 8765.
REM
REM  Now: ONE task -> this launcher -> supervisor.py -> uvicorn worker. This .bat is
REM  intentionally TRIVIAL: it does NOT do the singleton kill itself, because the
REM  batch/wmic kill was the unreliable part (a `for /f` trailing-CR broke taskkill;
REM  concurrent wmic calls failed). ALL dedup now lives in ONE reliable place --
REM  supervisor.py._enforce_singleton (netstat + tasklist + PID-file) -- so there is
REM  a single, race-free authority. Pattern mirrors remote_state_emitter_launcher.bat:
REM  `start /B pythonw ...` then `exit /b 0` so the task action exits clean with the
REM  supervisor orphaned-alive.

set PYTHONW=D:\AI\hd-instrument\tools\dashboard\.venv\Scripts\pythonw.exe
if not exist "%PYTHONW%" set PYTHONW=D:\AI\hd-instrument\tools\dashboard\.venv\Scripts\python.exe

start "hd_dashboard_supervisor" /B "%PYTHONW%" "D:\AI\hd-instrument\tools\dashboard\supervisor.py" --host 0.0.0.0 --port 8765
exit /b 0
