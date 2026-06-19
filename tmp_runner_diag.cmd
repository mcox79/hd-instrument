@echo off
echo === CPU runner XML triggers (full) ===
schtasks /query /tn \hd_cpu_runner_0 /xml 2>nul | findstr /N "."  | findstr /I "Trigger Boundary Enabled Repetition Duration Interval StopAtDurationEnd Hidden"

echo.
echo === recent CPU runner log activity (looking in repo for run output) ===
dir C:\dev\hd-instrument\data\orchestrator_*.log 2>nul
dir C:\dev\hd-instrument\data\runner_*.log 2>nul
dir C:\dev\hd-instrument\data\*runner*.log 2>nul

echo.
echo === look in cpu_runner_0_launcher.bat for what it does ===
type C:\dev\hd-instrument\tools\orchestrator\cpu_runner_0_launcher.bat 2>nul

echo.
echo === overnight_queue.json head (200 chars) ===
powershell -Command "(Get-Content C:\dev\hd-instrument\data\overnight_queue\queue.json -Raw -EA SilentlyContinue) -split '},' | Select-Object -First 2"
