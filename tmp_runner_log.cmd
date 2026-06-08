@echo off
echo === cpu_runner_0.log tail (50 lines) ===
powershell -Command "Get-Content C:\dev\hd-instrument\data\logs\cpu_runner_0.log -Tail 30 -EA SilentlyContinue"
echo.
echo === is runner_v2_prod alive? (python processes with that script) ===
powershell -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { $_.CommandLine -match 'runner_v2_prod' } | Select-Object ProcessId, CreationDate | Format-Table -AutoSize"
echo.
echo === remote_cpu_queue size ===
powershell -Command "$j = Get-Content C:\dev\hd-instrument\data\remote_cpu_queue\queue.json -Raw -EA SilentlyContinue | ConvertFrom-Json; if ($j.experiments) { '  experiments queued: ' + $j.experiments.Count } else { '  no experiments property; raw size: ' + (Get-Item C:\dev\hd-instrument\data\remote_cpu_queue\queue.json).Length + ' bytes' }"
echo.
echo === overnight_queue size ===
powershell -Command "$j = Get-Content C:\dev\hd-instrument\data\overnight_queue\queue.json -Raw -EA SilentlyContinue | ConvertFrom-Json; if ($j.experiments) { '  experiments queued: ' + $j.experiments.Count } else { '  no experiments property; raw size: ' + (Get-Item C:\dev\hd-instrument\data\overnight_queue\queue.json).Length + ' bytes' }"
echo.
echo === FINAL: any pause flags? ===
if exist C:\dev\hd-instrument\data\orchestrator_paused.flag (echo PAUSED) else (echo NORMAL)
