@echo off
cd /d C:\dev\hd-instrument
if not exist logs\runners mkdir logs\runners
C:\dev\hd-instrument\.venv\Scripts\python.exe experiments\runner_v2_prod.py overnight_queue --id gpu_runner_0 --idle-exit-minutes 480 > logs\runners\gpu_runner_0.log 2>&1
