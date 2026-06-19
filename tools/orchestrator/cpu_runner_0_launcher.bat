@echo off
REM Launcher batch for cpu_runner_0, called by Windows Task Scheduler.
REM Task Scheduler will own the process; it survives SSH disconnect.
REM -X utf8 keeps PYTHONIOENCODING=utf-8 active (no cp1252 crashes).
REM /BELOWNORMAL caps runner + child priority so the desktop stays usable.
REM start /BELOWNORMAL /WAIT runs the python process at below-normal priority;
REM runner_v2_prod.py also passes BELOW_NORMAL_PRIORITY_CLASS creationflags
REM to every child experiment it spawns (defense-in-depth, covers both layers).
REM
REM SINGLETON LOCK: handled by runner_v2_prod.py PID-file guard (--singleton-pid-file).
REM If the PID file exists and the PID is alive, the Python process exits immediately
REM (exit code 0) so this schtask invocation produces no duplicate runner.
start "cpu_runner_0" /BELOWNORMAL /WAIT "C:\dev\hd-instrument\.venv\Scripts\python.exe" -X utf8 "C:\dev\hd-instrument\experiments\runner_v2_prod.py" --queue-dir "C:\dev\hd-instrument\data\remote_cpu_queue" --id cpu_runner_0 --idle-exit-minutes 240 --singleton-pid-file "C:\dev\hd-instrument\data\logs\cpu_runner_0.pid" >> "C:\dev\hd-instrument\data\logs\cpu_runner_0.log" 2>&1
