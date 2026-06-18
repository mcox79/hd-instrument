# Install hd_blocker_ping as Windows scheduled task on LAPTOP.
# Per USER directive 2026-06-18 "your 30 minute reminder should survive compaction".
# Cadence: every 30 min (one-shot bash script + scheduled-task RepetitionInterval).
# Writes notes/blocker_ping_to_all_<TS>_n<N>.md each cycle; v5 monitors pick up via _all_ filter.

$ErrorActionPreference = "Stop"

$taskName = "hd_blocker_ping"
$bashExe = "C:\Program Files\Git\bin\bash.exe"
$scriptPath = "/d/AI/hd-instrument/tools/blocker_ping_once.sh"
$winScriptPath = "D:\AI\hd-instrument\tools\blocker_ping_once.sh"
$workingDir = "D:\AI\hd-instrument"

if (-not (Test-Path $winScriptPath)) {
    Write-Error ("blocker_ping_once.sh not at " + $winScriptPath)
    exit 1
}
if (-not (Test-Path $bashExe)) {
    Write-Error ("bash.exe not at " + $bashExe)
    exit 1
}

try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
} catch {}

$action = New-ScheduledTaskAction `
    -Execute $bashExe `
    -Argument $scriptPath `
    -WorkingDirectory $workingDir

# 30-min cadence: at-logon trigger + 30-min repetition starting in 1 min from install
$logonTrigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME

$startAt = (Get-Date).AddMinutes(1)
$repeatTrigger = New-ScheduledTaskTrigger -Once -At $startAt
$repeatTrigger.Repetition = (New-ScheduledTaskTrigger -Once -At $startAt -RepetitionInterval (New-TimeSpan -Minutes 30) -RepetitionDuration (New-TimeSpan -Days 7)).Repetition

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 2) `
    -RestartCount 1 `
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
Write-Output "Cadence: at logon + every 30 min (1-min initial delay; 7-day duration window)"
Write-Output "ExecutionTimeLimit: 2 min (one-shot script; exits immediately after writing ping note)"
Write-Output "Survives: session close + compaction + laptop sleep (StartWhenAvailable)"
