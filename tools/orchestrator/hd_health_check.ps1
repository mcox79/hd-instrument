# hd-instrument cross-session health check (orchestrator owns).
# Runs every 15 minutes via scheduled task \hd_health_check.
# Auto-corrects drift; appends status lines to data/events/orchestrator.log only when action taken.

$ErrorActionPreference = 'Continue'
Set-StrictMode -Off

$root = 'd:/AI/hd-instrument'
$log = "$root/data/events/orchestrator.log"
$now = (Get-Date).ToString('HH:mm:ss')
$actions = @()

# 1. Singleton producer (exactly one event_bus.sh)
$producers = Get-CimInstance Win32_Process -Filter "Name='bash.exe'" |
    Where-Object { $_.CommandLine -like '*event_bus.sh*' }
if ($producers.Count -eq 0) {
    $actions += "$now HEALTH: producer DEAD; not auto-restarting (needs Bash shell to re-launch via tools/event_bus_launch.cmd)"
} elseif ($producers.Count -gt 1) {
    $oldest = $producers | Sort-Object CreationDate | Select-Object -First 1
    $extras = $producers | Where-Object { $_.ProcessId -ne $oldest.ProcessId }
    foreach ($p in $extras) { Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue }
    Set-Content -Path "$root/data/.event_bus.lock" -Value $oldest.ProcessId -NoNewline -ErrorAction SilentlyContinue
    $actions += "$now HEALTH: killed $($extras.Count) duplicate producers; kept PID $($oldest.ProcessId); lock file fixed"
}

# 2. Duplicate tails per session
$sessions = @('orchestrator', 'exp_dev', 'research', 'testbed', 'skunkworks')
foreach ($s in $sessions) {
    $tails = Get-CimInstance Win32_Process -Filter "Name='tail.exe'" |
        Where-Object { $_.CommandLine -like "*events/$s.log*" -or $_.CommandLine -like "*events\$s.log*" }
    if ($tails.Count -gt 1) {
        $newest = $tails | Sort-Object CreationDate -Descending | Select-Object -First 1
        $stale = $tails | Where-Object { $_.ProcessId -ne $newest.ProcessId }
        foreach ($t in $stale) { Stop-Process -Id $t.ProcessId -Force -ErrorAction SilentlyContinue }
        $actions += "$now HEALTH: killed $($stale.Count) duplicate $s tails; kept PID $($newest.ProcessId)"
    }
}

# 3. NORMAL-priority hd-instrument python processes -> downgrade to BELOWNORMAL
$rogue = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.Priority -eq 8 -and ($_.CommandLine -like '*hd-instrument*' -or $_.CommandLine -like '*hdlab*') -and $_.CommandLine -notlike '*uvicorn*' }
foreach ($r in $rogue) {
    try {
        (Get-Process -Id $r.ProcessId).PriorityClass = 'BelowNormal'
        $cmd = $r.CommandLine.Substring(0, [Math]::Min(80, $r.CommandLine.Length))
        $actions += "$now HEALTH: downgraded PID $($r.ProcessId) to BELOWNORMAL ($cmd)"
    } catch {}
}

# 4. Notes dir size alert (>4000 files = archive recommended)
$noteCount = (Get-ChildItem "$root/notes/" -File -ErrorAction SilentlyContinue | Measure-Object).Count
if ($noteCount -gt 4000) {
    $actions += "$now HEALTH: notes/ has $noteCount files; consider archiving older notes to notes/archived/"
}

# 5. Producer staleness (event log not touched in >2 min)
$producerLog = Get-Item "$root/data/events/orchestrator.log" -ErrorAction SilentlyContinue
if ($producerLog) {
    $ageMin = [Math]::Round(((Get-Date) - $producerLog.LastWriteTime).TotalMinutes, 1)
    if ($ageMin -gt 2.5) {
        $actions += "$now HEALTH: orchestrator.log stale (${ageMin}min); producer may be hung"
    }
}

# Append all actions in one batch
if ($actions.Count -gt 0) {
    Add-Content -Path $log -Value ($actions -join "`n") -ErrorAction SilentlyContinue
}
