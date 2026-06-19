# Install hd_metrics_sync as a Windows scheduled task on LAPTOP.
# Recurring infrastructure task; not bounded (runs indefinitely; pull-on-demand).
# Hardening:
#   - MultipleInstances IgnoreNew (no CPU pile-up)
#   - ExecutionTimeLimit 10min (any hung run is killed)
#   - StartWhenAvailable (catches missed triggers if laptop was asleep)
#   - RestartCount 2 + RestartInterval 5min (handles task-engine transients)
#   - LogonTrigger + Repetition every 20 min (canonical recurring infra cadence)
#   - AllowStartIfOnBatteries + DontStopIfGoingOnBatteries (battery-safe)

$ErrorActionPreference = "Stop"

$taskName = "hd_metrics_sync"
$scriptPath = "D:/AI/hd-instrument/tools/orchestrator/local_metrics_sync.ps1"

if (-not (Test-Path $scriptPath)) {
    Write-Error ("sync script not at " + $scriptPath)
    exit 1
}

# Uninstall any existing instance
try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
} catch {}

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument ("-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"" + $scriptPath + "`"")

# Trigger 1: at logon (catches resume from sleep + login)
$logonTrigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME

# Trigger 2: every 20 min indefinitely
$startAt = (Get-Date).AddSeconds(30)
$repeatTrigger = New-ScheduledTaskTrigger -Once -At $startAt
$repeatTrigger.Repetition = (New-ScheduledTaskTrigger -Once -At $startAt -RepetitionInterval (New-TimeSpan -Minutes 20) -RepetitionDuration (New-TimeSpan -Days 365)).Repetition

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10) `
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
    -Trigger @($logonTrigger, $repeatTrigger) `
    -Settings $settings `
    -Principal $principal | Out-Null

Write-Output ("REGISTERED " + $taskName)
Write-Output "Triggers: at logon + every 20 min indefinitely"
Write-Output "MultipleInstances IgnoreNew (no CPU pile-up)"
Write-Output "ExecutionTimeLimit 10min (any hung run killed)"
Write-Output "Battery-safe; SSH-failure-tolerant; idempotent merge preserves local files"
Write-Output "Logs: data/.metrics_sync/sync.log; Status: data/.metrics_sync/status.json"
Write-Output "Coverage gap alert: data/.coverage_gap (writes if gap persists >=3 runs)"
