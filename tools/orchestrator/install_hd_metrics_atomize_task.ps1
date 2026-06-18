# Install hd_metrics_atomize as Windows scheduled task on REMOTE.
# Substrate-mutating; --apply ENABLED per Skunkworks dry-run sample VET PASS 18:46.
# Cadence: hourly (script has its own internal trigger logic).

$ErrorActionPreference = "Stop"

$taskName = "hd_metrics_atomize"
$pythonExe = "C:/dev/hd-instrument/.venv/Scripts/python.exe"
$scriptPath = "C:/dev/hd-instrument/tools/hd_metrics_atomize.py"

if (-not (Test-Path $scriptPath)) {
    Write-Error ("hd_metrics_atomize.py not at " + $scriptPath)
    exit 1
}
if (-not (Test-Path $pythonExe)) {
    Write-Error ("venv python not at " + $pythonExe)
    exit 1
}

try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
} catch {}

# --apply per Skunkworks dry-run sample VET PASS 18:46
$action = New-ScheduledTaskAction `
    -Execute $pythonExe `
    -Argument ("`"" + $scriptPath + "`" --apply") `
    -WorkingDirectory "C:/dev/hd-instrument"

$logonTrigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME

$startAt = (Get-Date).AddMinutes(5)
$repeatTrigger = New-ScheduledTaskTrigger -Once -At $startAt
$repeatTrigger.Repetition = (New-ScheduledTaskTrigger -Once -At $startAt -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 365)).Repetition

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
    -Trigger @($logonTrigger, $repeatTrigger) `
    -Settings $settings `
    -Principal $principal | Out-Null

Write-Output ("REGISTERED " + $taskName + " (--apply enabled per Skunkworks VET PASS)")
Write-Output "Cadence: at logon + every 60 min"
Write-Output "ExecutionTimeLimit 1h"
