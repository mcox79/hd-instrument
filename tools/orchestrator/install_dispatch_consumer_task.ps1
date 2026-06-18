# Install hd_dispatch_consumer as a Windows scheduled task on REMOTE.
# Recurring infrastructure: every 60s pull git + process dispatch_requests.

$ErrorActionPreference = "Stop"

$taskName = "hd_dispatch_consumer"
$scriptPath = "C:/dev/hd-instrument/tools/orchestrator/remote_dispatch_consumer.ps1"

if (-not (Test-Path $scriptPath)) {
    Write-Error ("dispatch consumer script not at " + $scriptPath)
    exit 1
}

try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
} catch {}

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument ("-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"" + $scriptPath + "`"")

# Trigger 1: at logon
$logonTrigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME

# Trigger 2: every 60s indefinitely (capped at 365 days for task XML)
$startAt = (Get-Date).AddSeconds(30)
$repeatTrigger = New-ScheduledTaskTrigger -Once -At $startAt
$repeatTrigger.Repetition = (New-ScheduledTaskTrigger -Once -At $startAt -RepetitionInterval (New-TimeSpan -Minutes 1) -RepetitionDuration (New-TimeSpan -Days 365)).Repetition

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10) `
    -RestartCount 2 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
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
Write-Output "Triggers: at logon + every 60s indefinitely"
Write-Output "MultipleInstances IgnoreNew (no CPU pile-up)"
Write-Output "ExecutionTimeLimit 10min"
Write-Output "Watches: C:/dev/hd-instrument/data/dispatch_requests/*.json"
Write-Output "Processed manifests moved to dispatch_requests/processed/"
Write-Output "Failed manifests moved to dispatch_requests/failed/"
