# Register hd_wake_stopped_sessions scheduled task.
# Runs wake_stopped_claude_sessions.ps1 every 30 min to auto-wake stopped fleet sessions.
# REQUIRES UAC + user opt-in (run only after testing with -DryRun).

$TaskName = "hd_wake_stopped_sessions"
$ScriptPath = "C:\AI\hd-instrument\tools\wake_stopped_claude_sessions.ps1"

if (-not (Test-Path $ScriptPath)) {
    Write-Host "FAIL: wake script not found at $ScriptPath" -ForegroundColor Red
    exit 1
}

# Confirm USER opt-in
Write-Host "This will register $TaskName to auto-wake stopped Claude Code sessions every 30min."
Write-Host "RISK: SendKeys may inject input mid-task in rare cases."
Write-Host "Have you tested with -DryRun first? (Y/N)"
$confirm = Read-Host
if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "Aborted. Test first with:" -ForegroundColor Yellow
    Write-Host "  powershell.exe -ExecutionPolicy Bypass -File $ScriptPath -DryRun"
    exit 1
}

# Remove existing
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Note: cannot use S4U for SendKeys (needs interactive desktop access)
# Must use Interactive logon type so the task can interact with USER's windows.
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ScriptPath`""

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date)
$trigger.Repetition = New-CimInstance -ClientOnly -ClassName MSFT_TaskRepetitionPattern -Namespace 'root/Microsoft/Windows/TaskScheduler' -Property @{
    Interval = "PT30M"
    Duration = ""
    StopAtDurationEnd = $false
}

# Interactive principal (needed for SendKeys to reach user's desktop)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

$settings = New-ScheduledTaskSettingsSet `
    -Hidden `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 5) `
    -MultipleInstances IgnoreNew

Register-ScheduledTask -TaskName $TaskName `
    -Action $action -Trigger $trigger `
    -Principal $principal -Settings $settings `
    -Description "Auto-wake stopped Claude Code sessions via SendKeys (USER opt-in; Testbed-built 2026-06-21)." | Out-Null

Write-Host "OK: $TaskName registered" -ForegroundColor Green
Write-Host "Disable anytime: schtasks /Change /TN $TaskName /DISABLE"
Write-Host "Test now: schtasks /Run /TN $TaskName"
