$ErrorActionPreference = 'SilentlyContinue'
$j = Get-Content 'C:\dev\hd-instrument\data\overnight_queue\queue.json' -Raw | ConvertFrom-Json
$pp = $j.experiments | Where-Object { $_.name -eq 'pp50_transition_zone_n_sweep_tw_vs_hadamard_v2_gpu' }
Write-Output ("pp50 status=" + $pp.status + " started=" + $pp.started_at)
$run = @($j.experiments | Where-Object { $_.status -eq 'running' })
Write-Output ("overnight running = " + (($run | ForEach-Object { $_.name }) -join ', '))
Write-Output "---python processes (cmdline tail)---"
Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'python*' } | ForEach-Object {
    $c = $_.CommandLine
    if ($c.Length -gt 90) { $c = $c.Substring($c.Length - 90) }
    Write-Output ("PID=" + $_.ProcessId + "  ..." + $c)
}
Write-Output "---pp50 data dir---"
$d = 'C:\dev\hd-instrument\data\exp_pp50_transition_zone_n_sweep_tw_vs_hadamard_v2_gpu'
if (Test-Path $d) { Get-ChildItem $d | Select-Object Name, LastWriteTime | Format-Table -AutoSize | Out-String }
else { Write-Output "no pp50 data dir yet" }
Write-Output "---runner log tail (newest *runner* or *overnight* log)---"
$log = Get-ChildItem 'C:\dev\hd-instrument\logs\*' -ErrorAction SilentlyContinue | Sort-Object LastWriteTime | Select-Object -Last 1
if ($log) { Write-Output $log.FullName; Get-Content $log.FullName -Tail 6 } else { Write-Output "no logs dir" }
