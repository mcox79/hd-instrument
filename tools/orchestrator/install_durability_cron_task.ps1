# Install hd_durability_cron as a Windows scheduled task on the LAPTOP (canonical Store host).
# M3 durability cron (Exp-Dev tools/substrate_durability_cron_v1.py; Skunkworks SCHEMA-VET PASS + 4th-layer re-VET PASS).
# v1 = DETECTION LAYERS daily: local 8MB scoped snapshot (excl derivable caches) + invariant-check (cert-FLOOR)
#      + manifest-gap (A5 flag-not-fix) + remote-reconcile-state (--check-remote ssh; the drift-catcher that would
#      have caught the June-12 remote-consumer-broken incident) + prune keep-7.
# DEFERRED to v1.1: off-machine --push (pure-git 8MB scoped snapshot -> origin/snapshots branch; mechanics TBD).

$ErrorActionPreference = "Stop"

$taskName = "hd_durability_cron"
$pythonExe = "D:/AI/hd-instrument/.venv/Scripts/python.exe"
$scriptPath = "D:/AI/hd-instrument/tools/substrate_durability_cron_v1.py"

if (-not (Test-Path $scriptPath)) { Write-Error ("durability cron not at " + $scriptPath); exit 1 }
if (-not (Test-Path $pythonExe)) { Write-Error ("venv python not at " + $pythonExe); exit 1 }

try { Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue } catch {}

# v1: detection layers + remote-reconcile-state + prune. No --push (v1.1).
$action = New-ScheduledTaskAction `
    -Execute $pythonExe `
    -Argument ("`"" + $scriptPath + "`" --check-remote --keep-snapshots 7") `
    -WorkingDirectory "D:/AI/hd-instrument"

# Daily at 04:10 local + StartWhenAvailable (catches a missed run if the laptop was asleep).
$dailyTrigger = New-ScheduledTaskTrigger -Daily -At 4:10AM

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
    -RestartCount 2 `
    -RestartInterval (New-TimeSpan -Minutes 5) `
    -MultipleInstances IgnoreNew

$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Limited

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $dailyTrigger `
    -Settings $settings `
    -Principal $principal | Out-Null

Write-Output ("REGISTERED " + $taskName)
Write-Output "Cadence: daily 04:10 (StartWhenAvailable)"
Write-Output "Args: --check-remote --keep-snapshots 7 (detection layers + remote-reconcile-state + prune; --push DEFERRED to v1.1)"
