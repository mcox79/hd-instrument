# Install hd_index_refresh as Windows scheduled task on REMOTE.
# Cadence: hourly (the script's internal N-delta + daily floor logic
# decides whether to actually run the heavy encode; cheap to invoke).

$ErrorActionPreference = "Stop"

$taskName = "hd_index_refresh"
$pythonExe = "C:/dev/hd-instrument/.venv/Scripts/python.exe"
$scriptPath = "C:/dev/hd-instrument/tools/hd_index_refresh.py"

if (-not (Test-Path $scriptPath)) {
    Write-Error ("hd_index_refresh.py not at " + $scriptPath)
    exit 1
}
if (-not (Test-Path $pythonExe)) {
    Write-Error ("venv python not at " + $pythonExe)
    exit 1
}

try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
} catch {}

$action = New-ScheduledTaskAction `
    -Execute $pythonExe `
    -Argument $scriptPath `
    -WorkingDirectory "C:/dev/hd-instrument"

$logonTrigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME

$startAt = (Get-Date).AddMinutes(5)
$repeatTrigger = New-ScheduledTaskTrigger -Once -At $startAt
$repeatTrigger.Repetition = (New-ScheduledTaskTrigger -Once -At $startAt -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 365)).Repetition

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
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
Write-Output "Cadence: at logon + every 60 min (script decides actual encode via N-delta / daily floor)"
Write-Output "ExecutionTimeLimit 2h (covers heavy bge encode)"
