@echo off
echo === hd_cpu_runner_0 full XML ===
schtasks /query /tn \hd_cpu_runner_0 /xml 2>nul | findstr /I "Triggers Boundary Enabled Repetition Duration Interval"
echo.
echo === hd_gpu_runner_0 full XML ===
schtasks /query /tn \hd_gpu_runner_0 /xml 2>nul | findstr /I "Triggers Boundary Enabled Repetition Duration Interval"
echo.
echo === full task list pattern ===
schtasks /query /fo LIST /v 2>nul | findstr /I "TaskName Schedule" | findstr /I "runner queue dispatch hd_"
echo.
echo === recent activity in queue dirs ===
dir C:\dev\hd-instrument\data\overnight_queue 2>nul | findstr /I "queue.json"
dir C:\dev\hd-instrument\data\remote_cpu_queue 2>nul | findstr /I "queue.json"
dir C:\dev\hd-instrument\data\remote_gpu_queue 2>nul | findstr /I "queue.json"
echo.
echo === overnight_queue.json head ===
powershell -Command "Get-Content C:\dev\hd-instrument\data\overnight_queue\queue.json -Raw -EA SilentlyContinue | Select-Object -First 1000"
