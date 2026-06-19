$ErrorActionPreference = 'SilentlyContinue'
$procs = Get-CimInstance Win32_Process | Where-Object {
    $_.Name -like 'python*' -and $_.CommandLine -like '*mini_lm_readout_fix_nsweep*'
}
if ($procs) {
    foreach ($p in $procs) { Write-Output ("KILL PID=" + $p.ProcessId); Stop-Process -Id $p.ProcessId -Force }
} else { Write-Output "no mini_lm_nsweep process found" }
Start-Sleep -Seconds 3
$f = 'C:\dev\hd-instrument\data\remote_cpu_queue\queue.json'
$j = Get-Content $f -Raw | ConvertFrom-Json
$e = $j.experiments | Where-Object { $_.name -eq 'substrate_trained_mini_lm_readout_fix_nsweep_v1' }
Write-Output ("mini_lm entry status now = " + $e.status)
$run = @($j.experiments | Where-Object { $_.status -eq 'running' })
Write-Output ("cpu running now = " + (($run | ForEach-Object { $_.name }) -join ', '))
