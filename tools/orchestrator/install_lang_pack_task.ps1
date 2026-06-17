# Install hd_lang_pack_download scheduled task; HARDENED.
# - MultipleInstances IgnoreNew: prevents CPU pile-up
# - ExecutionTimeLimit 15min: any hung instance is killed
# - StartWhenAvailable: catches missed triggers if PC was off
# - RestartCount 2 + RestartInterval 5min: handles transient task-engine failures
# - LogonTrigger + Repetition every 5min for 6 hours: bounded scheduled lifetime
# - download script itself enforces MAX_TOTAL_RUNS=5 budget
#
# Net effect: at most ~5 actual download attempts; max 1 process at a time;
# self-unregisters when packs land OR after budget exhausted.

$ErrorActionPreference = "Stop"

$taskName = "hd_lang_pack_download"
$scriptPath = "C:/Users/marsh/lang_dl.ps1"

# Verify script exists
if (-not (Test-Path $scriptPath)) {
    Write-Error ("download script not at " + $scriptPath)
    exit 1
}

# Uninstall any existing instance to ensure clean slate
try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
} catch {}

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument ("-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"" + $scriptPath + "`"")

# Trigger: once at install + repetition every 5 min for 6 hours (bounded; script has MAX_TOTAL_RUNS=5 anyway)
$startAt = (Get-Date).AddSeconds(30)
$trigger = New-ScheduledTaskTrigger -Once -At $startAt
$trigger.Repetition = (New-ScheduledTaskTrigger -Once -At $startAt -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Hours 6)).Repetition

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 15) `
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
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal | Out-Null

Write-Output ("REGISTERED " + $taskName)
Write-Output "Trigger: once+repeat 5min for 6 hours (bounded)"
Write-Output "MultipleInstances IgnoreNew (no CPU pile-up)"
Write-Output "ExecutionTimeLimit 15min (any hang is killed)"
Write-Output "Download script MAX_TOTAL_RUNS=5 budget (no infinite retry)"
Write-Output "Self-unregisters on success (PROVENANCE.md) or budget exhaust (FINAL_FAILURE.md)"
