# Register the hd_autorefill_watcher scheduled task.
# Runs tools/autorefill_cron.bat every 5 minutes to check for an idle remote
# GPU/CPU runner + empty queue, and dispatch-on-idle from the ready-pool
# (data/autorefill_pool.json) or the fallback cell (data/autorefill_fallback_
# cell.json). See tools/autorefill_watcher.py module docstring for full design.
#
# REQUIRES UAC (S4U logon registration needs admin) -- same precedent as
# register_substrate_snapshot_task_elevated.ps1. Run from elevated PowerShell.
#
# NOTE: registering this task does NOT activate the watcher. The watcher itself
# stays a no-op until data/autorefill_enabled.flag is created (see
# tools/autorefill_watcher.py docstring "ENABLE"). Registering the task just
# means "check every 5 min whether it's turned on."

$TaskName = "hd_autorefill_watcher"
$LauncherPath = "D:\AI\hd-instrument\tools\autorefill_cron.bat"

if (-not (Test-Path $LauncherPath)) {
    Write-Host "FAIL: launcher not found at $LauncherPath" -ForegroundColor Red
    exit 1
}

# Remove any prior registration
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Removing prior $TaskName registration..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Action: run the launcher via cmd /c start /b (suppresses console even more)
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c start `"`" /b `"$LauncherPath`""

# Trigger: every 5 minutes, starting now, indefinite
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date)
$trigger.Repetition = New-CimInstance -ClientOnly -ClassName MSFT_TaskRepetitionPattern -Namespace 'root/Microsoft/Windows/TaskScheduler' -Property @{
    Interval = "PT5M"
    Duration = ""
    StopAtDurationEnd = $false
}

# Principal: S4U (no UI, no interactive logon required, no popups)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Limited

# Settings: hidden, allow start on battery, bounded execution time (SCP+SSH
# dispatch can take up to a couple minutes; DISPATCH_TIMEOUT_S in the script is
# 300s, give the task itself headroom above that), restart on failure,
# IgnoreNew so overlapping runs never stack.
$settings = New-ScheduledTaskSettingsSet `
    -Hidden `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 8) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 2) `
    -MultipleInstances IgnoreNew

Register-ScheduledTask -TaskName $TaskName `
    -Action $action -Trigger $trigger `
    -Principal $principal -Settings $settings `
    -Description "Dispatch-on-idle auto-refill for overnight_queue/remote_cpu_queue (popup-free; pythonw + S4U + Hidden). No-ops unless data/autorefill_enabled.flag exists." | Out-Null

Write-Host "OK: $TaskName registered (every 5min)" -ForegroundColor Green
Get-ScheduledTask -TaskName $TaskName | Format-List TaskName, State, @{N='Logon';E={$_.Principal.LogonType}}, @{N='Hidden';E={$_.Settings.Hidden}}

Write-Host ""
Write-Host "Task is registered but the WATCHER ITSELF is still disabled." -ForegroundColor Yellow
Write-Host "Enable it with:"
Write-Host "  New-Item -ItemType File -Force D:\AI\hd-instrument\data\autorefill_enabled.flag"
Write-Host "Disable anytime (no task-scheduler surgery needed) by deleting that file."
Write-Host "Manage the task: schtasks /Query /TN $TaskName /FO LIST   |   schtasks /End /TN $TaskName   |   schtasks /Delete /TN $TaskName /F"
