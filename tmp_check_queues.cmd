@echo off
echo === flag files ===
if exist C:\dev\hd-instrument\data\orchestrator_paused.flag (
    echo ORCH_PAUSED_FLAG_PRESENT
    type C:\dev\hd-instrument\data\orchestrator_paused.flag
) else (
    echo ORCH_PAUSED_FLAG_ABSENT
)
if exist C:\dev\hd-instrument\data\demo_mode_active.flag (
    echo DEMO_FLAG_PRESENT
) else (
    echo DEMO_FLAG_ABSENT
)
if exist C:\dev\hd-instrument\data\demo_mode_watchdog_heartbeat (
    echo HEARTBEAT_PRESENT
) else (
    echo HEARTBEAT_ABSENT
)

echo.
echo === queue depths (from queue.json files) ===
for %%q in (overnight_queue cpu_q remote_cpu_queue gpu_q remote_gpu_queue local_queue) do (
    if exist C:\dev\hd-instrument\data\%%q\queue.json (
        echo --- %%q ---
        powershell -Command "$j = Get-Content 'C:\dev\hd-instrument\data\%%q\queue.json' -Raw | ConvertFrom-Json; if ($j.queue) { Write-Output ('  queued: ' + $j.queue.Count) } else { Write-Output ('  raw: ' + ($j | ConvertTo-Json -Compress).Substring(0, [Math]::Min(200, ($j | ConvertTo-Json -Compress).Length))) }"
    )
)

echo.
echo === runner schtasks status ===
schtasks /query /tn "\hd_cpu_runner_0" /v /fo LIST 2>nul | findstr /I "TaskName Status Run "
schtasks /query /tn "\hd_gpu_runner_0" /v /fo LIST 2>nul | findstr /I "TaskName Status Run "

echo.
echo === orchestrator state_check ===
cd /d C:\dev\hd-instrument
python tools\orchestrator\state_check.py 2>nul

echo.
echo === any suspended python procs? ===
powershell -Command "Get-Process python -EA SilentlyContinue | ForEach-Object { try { $p = [System.Diagnostics.Process]::GetProcessById($_.Id); '  PID ' + $p.Id + '  ' + ($p.Modules.Count > 0 ? 'normal' : 'check') } catch {} }" 2>nul | Select-Object -First 8
