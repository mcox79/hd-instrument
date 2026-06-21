# Register the hd_substrate_snapshot scheduled task.
# Regenerates data/substrate_snapshot.json every 20 minutes for the 3D dashboard tab.
# REQUIRES UAC (S4U logon registration needs admin). Run from elevated PowerShell.

$TaskName = "hd_substrate_snapshot"
$LauncherPath = "D:\AI\hd-instrument\tools\substrate_snapshot_cron.bat"

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

# Trigger: every 20 minutes, starting now, indefinite
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date)
$trigger.Repetition = New-CimInstance -ClientOnly -ClassName MSFT_TaskRepetitionPattern -Namespace 'root/Microsoft/Windows/TaskScheduler' -Property @{
    Interval = "PT20M"
    Duration = ""
    StopAtDurationEnd = $false
}

# Principal: S4U (no UI, no interactive logon required, no popups)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Limited

# Settings: hidden, allow start on battery, no time limit, restart on failure
$settings = New-ScheduledTaskSettingsSet `
    -Hidden `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 5) `
    -MultipleInstances IgnoreNew

Register-ScheduledTask -TaskName $TaskName `
    -Action $action -Trigger $trigger `
    -Principal $principal -Settings $settings `
    -Description "Regenerate data/substrate_snapshot.json every 20min for the 3D dashboard tab (popup-free; pythonw + S4U + Hidden)." | Out-Null

Write-Host "OK: $TaskName registered" -ForegroundColor Green
Get-ScheduledTask -TaskName $TaskName | Format-List TaskName, State, @{N='Logon';E={$_.Principal.LogonType}}, @{N='Hidden';E={$_.Settings.Hidden}}

# Trigger first run immediately so the snapshot is fresh
Write-Host "Triggering first run now (asynchronously)..." -ForegroundColor Cyan
Start-ScheduledTask -TaskName $TaskName
Write-Host "Done. Check data/logs/substrate_snapshot_cron.log + data/substrate_snapshot.json mtime in ~30s."
