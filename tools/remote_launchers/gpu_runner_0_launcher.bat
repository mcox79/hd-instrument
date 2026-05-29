@echo off
REM gpu_runner_0 launcher for Task Scheduler - survives SSH disconnect
REM -X utf8 keeps PYTHONIOENCODING=utf-8 active
REM
REM Desktop-usability caps (added 2026-05-29):
REM   nvidia-smi -pl 194  caps GPU power to ~90% of 216W max (was 160W default)
REM   /BELOWNORMAL        OS scheduler prefers foreground apps; runner + children
REM                       see priority 6 (vs 8 for normal); covers CPU side too
REM   /AFFINITY 3FF       10 of 12 logical CPUs (one physical core free for user);
REM                       binary 1111111111 = decimal 1023
REM
REM SINGLETON LOCK: handled by runner_v2_prod.py PID-file guard (--singleton-pid-file).
REM If the PID file exists and the PID is alive, the Python process exits immediately
REM (exit code 0) so this schtask invocation produces no duplicate runner.

REM Re-apply GPU power cap on every launch (some drivers reset on reboot).
nvidia-smi -pl 194 >nul 2>&1

start "gpu_runner_0" /BELOWNORMAL /AFFINITY 3FF /WAIT "C:\dev\hd-instrument\.venv\Scripts\python.exe" -X utf8 "C:\dev\hd-instrument\experiments\runner_v2_prod.py" --queue-dir "C:\dev\hd-instrument\data\overnight_queue" --id gpu_runner_0 --idle-exit-minutes 240 --singleton-pid-file "C:\dev\hd-instrument\data\logs\gpu_runner_0.pid" >> "C:\dev\hd-instrument\data\overnight_queue\runner_stdout6.log" 2>&1
