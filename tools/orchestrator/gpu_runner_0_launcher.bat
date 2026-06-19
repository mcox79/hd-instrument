@echo off
REM gpu_runner_0 launcher for Task Scheduler - survives SSH disconnect
REM -X utf8 keeps PYTHONIOENCODING=utf-8 active
REM
REM SINGLETON LOCK: handled by runner_v2_prod.py PID-file guard (--singleton-pid-file).
REM If the PID file exists and the PID is alive, the Python process exits immediately
REM (exit code 0) so this schtask invocation produces no duplicate runner.
"C:\dev\hd-instrument\.venv\Scripts\python.exe" -X utf8 "C:\dev\hd-instrument\experiments\runner_v2_prod.py" --queue-dir "C:\dev\hd-instrument\data\overnight_queue" --id gpu_runner_0 --idle-exit-minutes 240 --singleton-pid-file "C:\dev\hd-instrument\data\logs\gpu_runner_0.pid" >> "C:\dev\hd-instrument\data\overnight_queue\runner_stdout6.log" 2>&1
