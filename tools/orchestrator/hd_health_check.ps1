# hd-instrument cross-session health check (orchestrator owns).
# Runs every 15 minutes via scheduled task \hd_health_check.
# Auto-corrects drift; appends status lines to data/events/orchestrator.log only when action taken.
#
# Usage: hd_health_check.ps1 [-WhatIf]
#   -WhatIf : dry-run; log what WOULD be killed but do not actually Stop-Process.

param(
    [switch]$WhatIf
)

$ErrorActionPreference = 'Continue'
Set-StrictMode -Off

$root = 'd:/AI/hd-instrument'
$log = "$root/data/events/orchestrator.log"
$now = (Get-Date).ToString('HH:mm:ss')
$actions = @()

# 1. Singleton producer. The launcher cmd creates a parent wrapper + child loop (parent-child pair is normal).
# A "producer family" = one root bash + its descendants matching event_bus.sh. Multiple families = drift.
$producers = Get-CimInstance Win32_Process -Filter "Name='bash.exe'" |
    Where-Object { $_.CommandLine -like '*event_bus.sh*' }
if ($producers.Count -eq 0) {
    $actions += "$now HEALTH: producer DEAD; not auto-restarting (needs Bash shell to re-launch via tools/event_bus_launch.cmd)"
} else {
    # Group producers by their root ancestor: a producer is a "root" if its parent isn't also a producer.
    $producerPids = @{}
    foreach ($p in $producers) { $producerPids[$p.ProcessId] = $true }
    $roots = $producers | Where-Object { -not $producerPids[$_.ParentProcessId] }
    if ($roots.Count -gt 1) {
        # Multiple families — keep the oldest root, kill the rest (and their descendants)
        $keepRoot = $roots | Sort-Object CreationDate | Select-Object -First 1
        $killRoots = $roots | Where-Object { $_.ProcessId -ne $keepRoot.ProcessId }
        $killed = 0
        foreach ($r in $killRoots) {
            # Kill the root and any of its descendants in $producers
            foreach ($p in $producers) {
                if ($p.ProcessId -eq $r.ProcessId -or $p.ParentProcessId -eq $r.ProcessId) {
                    Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
                    $killed++
                }
            }
        }
        Set-Content -Path "$root/data/.event_bus.lock" -Value $keepRoot.ProcessId -NoNewline -ErrorAction SilentlyContinue
        $actions += "$now HEALTH: killed $killed duplicate-family producer processes; kept root PID $($keepRoot.ProcessId)"
    }
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

# 6. Orphan pythonw.exe sweeper (elevated / cmdline-invisible runaway processes)
# Root cause: scheduled tasks (hd_landing_notifier, hd_director_kb_continuous_ingest,
# hd_durability_cron) spawn python subprocesses that outlive their parent when the
# invocation stalls (e.g., sync-hang bug 2026-07-01). User can't Task Manager-kill
# easily since they're elevated. This sweeper finds + terminates them.
#
# Heuristic: pythonw.exe with EMPTY/null CommandLine (elevated invisibility) AND
# working-set > 100 MB AND age > 30 min AND ExecutablePath not in allowlist.
$allowlistPath = "$root/data/health_check_python_allowlist.json"
$sweepLog = "$root/data/orphan_python_sweep.log"
$allowedPaths = @()
$allowedPids = @()
if (Test-Path $allowlistPath) {
    try {
        $allowlist = Get-Content $allowlistPath -Raw | ConvertFrom-Json
        if ($allowlist.executable_paths) { $allowedPaths = @($allowlist.executable_paths) }
        if ($allowlist.pids) { $allowedPids = @($allowlist.pids) }
    } catch {
        $actions += "$now HEALTH: allowlist parse failed ($($_.Exception.Message)); skipping orphan sweep"
    }
}

$sweepFindings = @()
$orphanCandidates = Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'" -ErrorAction SilentlyContinue
foreach ($proc in $orphanCandidates) {
    # Skip if we CAN see the cmdline -- that's legitimate active work
    if ($proc.CommandLine -and $proc.CommandLine.Trim().Length -gt 0) { continue }
    # Skip if allowlisted by ExecutablePath (case-insensitive, normalize slashes)
    $exe = $proc.ExecutablePath
    if ($exe) {
        $exeNorm = $exe.ToLower().Replace('/', '\')
        $isAllowed = $false
        foreach ($ap in $allowedPaths) {
            if ($ap.ToLower().Replace('/', '\') -eq $exeNorm) { $isAllowed = $true; break }
        }
        if ($isAllowed) { continue }
    }
    # Skip if allowlisted by PID
    if ($allowedPids -contains $proc.ProcessId) { continue }
    # Working set check (>100 MB)
    $wsMB = [Math]::Round($proc.WorkingSetSize / 1MB, 1)
    if ($wsMB -le 100) { continue }
    # Age check (>30 min)
    $created = $null
    try { $created = [Management.ManagementDateTimeConverter]::ToDateTime($proc.CreationDate) } catch {}
    if (-not $created) { continue }
    $ageMin = [Math]::Round(((Get-Date) - $created).TotalMinutes, 1)
    if ($ageMin -le 30) { continue }

    # Match: orphan candidate
    $exeShort = if ($exe) { $exe } else { '(no exe path)' }
    $sweepFindings += [PSCustomObject]@{
        Pid = $proc.ProcessId
        Ppid = $proc.ParentProcessId
        WSMB = $wsMB
        AgeMin = $ageMin
        Exe = $exeShort
    }
}

if ($sweepFindings.Count -gt 0) {
    $tsIso = (Get-Date -Format 'yyyy-MM-ddTHH:mm:ss')
    $sweepLines = @()
    $killedPids = @()
    $failedPids = @()
    foreach ($f in $sweepFindings) {
        $mode = if ($WhatIf) { 'WOULD_KILL' } else { 'KILL_ATTEMPT' }
        $line = "$tsIso $mode pid=$($f.Pid) ppid=$($f.Ppid) ws=$($f.WSMB)MB age=$($f.AgeMin)min exe=$($f.Exe)"
        if (-not $WhatIf) {
            try {
                Stop-Process -Id $f.Pid -Force -ErrorAction Stop
                $killedPids += $f.Pid
                $line += ' result=killed'
            } catch {
                $failedPids += $f.Pid
                $line += " result=failed_needs_manual_kill err=$($_.Exception.Message)"
            }
        }
        $sweepLines += $line
    }
    Add-Content -Path $sweepLog -Value ($sweepLines -join "`n") -ErrorAction SilentlyContinue

    # Trim sweep log to last ~100 sweeps (~ generous cap of 2000 lines; each sweep <=~20 orphans max)
    try {
        $existing = Get-Content $sweepLog -ErrorAction SilentlyContinue
        if ($existing -and $existing.Count -gt 2000) {
            $trimmed = $existing | Select-Object -Last 2000
            Set-Content -Path $sweepLog -Value $trimmed -ErrorAction SilentlyContinue
        }
    } catch {}

    $summary = "$now HEALTH: orphan-sweep found $($sweepFindings.Count) pythonw candidate(s)"
    if ($WhatIf) { $summary += ' [WhatIf: no kills]' }
    else {
        if ($killedPids.Count -gt 0) { $summary += "; killed PIDs: $($killedPids -join ',')" }
        if ($failedPids.Count -gt 0) { $summary += "; MANUAL KILL NEEDED for PIDs: $($failedPids -join ',')" }
    }
    $actions += $summary
}

# Append all actions in one batch
if ($actions.Count -gt 0) {
    Add-Content -Path $log -Value ($actions -join "`n") -ErrorAction SilentlyContinue
}
