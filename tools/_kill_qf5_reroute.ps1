$ErrorActionPreference = 'SilentlyContinue'
# 1. Kill the q_f5 experiment subprocess (by command line), NOT the runner.
$procs = Get-CimInstance Win32_Process | Where-Object {
    $_.Name -like 'python*' -and $_.CommandLine -like '*q_f5_oscillating_envelope_v2*'
}
if ($procs) {
    foreach ($p in $procs) {
        Write-Output ("KILL PID=" + $p.ProcessId)
        Stop-Process -Id $p.ProcessId -Force
    }
} else {
    Write-Output "no q_f5 experiment process found (may have already exited)"
}
Start-Sleep -Seconds 3
# 2. Report overnight_queue status for q_f5 + what is running now.
$f = 'C:\dev\hd-instrument\data\overnight_queue\queue.json'
$j = Get-Content $f -Raw | ConvertFrom-Json
$qf5 = $j.experiments | Where-Object { $_.name -eq 'q_f5_oscillating_envelope_v2_n8192' }
Write-Output ("q_f5 entry status now = " + $qf5.status)
$running = @($j.experiments | Where-Object { $_.status -eq 'running' })
$pending = @($j.experiments | Where-Object { $_.status -eq 'pending' })
Write-Output ("overnight running = " + (($running | ForEach-Object { $_.name }) -join ', '))
Write-Output ("overnight pending = " + (($pending | ForEach-Object { $_.name }) -join ', '))
