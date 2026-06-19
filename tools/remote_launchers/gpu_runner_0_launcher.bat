@echo off
REM gpu_runner_0 launcher for Task Scheduler - survives SSH disconnect
REM -X utf8 keeps PYTHONIOENCODING=utf-8 active
REM
REM EXPERIMENT-SCOPED caps (added 2026-05-29; do NOT cap the GPU hardware itself):
REM   /BELOWNORMAL        OS scheduler + NVIDIA driver yield to foreground apps;
REM                       runner + children see priority 6 (vs 8 for normal).
REM                       Affects this experiment process only, not user's desktop.
REM   /AFFINITY 3FF       Runner + children restricted to 10 of 12 logical CPUs
REM                       (binary 1111111111 = decimal 1023). User keeps all 12 cores;
REM                       only the experiment is limited.
REM   HDLAB_GPU_MEMORY_FRACTION  Each experiment process calls
REM                       torch.cuda.set_per_process_memory_fraction(0.9) to leave
REM                       VRAM headroom for user's apps. Per-process VRAM cap; does
REM                       NOT reduce GPU's total VRAM.
REM
REM SINGLETON LOCK: handled by runner_v2_prod.py PID-file guard (--singleton-pid-file).
REM If the PID file exists and the PID is alive, the Python process exits immediately
REM (exit code 0) so this schtask invocation produces no duplicate runner.

set HDLAB_GPU_MEMORY_FRACTION=0.9

start "gpu_runner_0" /BELOWNORMAL /AFFINITY 3FF /WAIT "C:\dev\hd-instrument\.venv\Scripts\python.exe" -X utf8 "C:\dev\hd-instrument\experiments\runner_v2_prod.py" --queue-dir "C:\dev\hd-instrument\data\overnight_queue" --id gpu_runner_0 --idle-exit-minutes 240 --singleton-pid-file "C:\dev\hd-instrument\data\logs\gpu_runner_0.pid" >> "C:\dev\hd-instrument\data\overnight_queue\runner_stdout6.log" 2>&1
