# Install hd_remote_run_watcher as a Windows scheduled task on the LAPTOP (C:).
# Standing self-service dispatcher: every 5 min it runs tools/remote_run_request_watcher.py, which
# auto-fulfills any NEW/CHANGED solver REMOTE_RUN_REQUEST (CPU or GPU) via fulfill_remote_run_request.py.
# So solvers queue their own runs by dropping a request file -- no strategy session in the loop.
# Hardening mirrors hd_metrics_sync: IgnoreNew (no pile-up), 30-min ExecutionTimeLimit, StartWhenAvailable,
# restart-on-transient, battery-safe.

$ErrorActionPreference = "Stop"

$taskName   = "hd_remote_run_watcher"
$py         = "C:/AI/hd-instrument/.venv/Scripts/pythonw.exe"   # windowless (no console popup); subprocesses use CREATE_NO_WINDOW
$scriptPath = "C:/AI/hd-instrument/tools/remote_run_request_watcher.py"

if (-not (Test-Path $py))         { Write-Error ("venv python not at " + $py); exit 1 }
if (-not (Test-Path $scriptPath)) { Write-Error ("watcher not at " + $scriptPath); exit 1 }

try { Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue } catch {}

$action = New-ScheduledTaskAction -Execute $py -Argument ("`"" + $scriptPath + "`"") -WorkingDirectory "C:/AI/hd-instrument"

$logonTrigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$startAt = (Get-Date).AddSeconds(60)
$repeatTrigger = New-ScheduledTaskTrigger -Once -At $startAt
$repeatTrigger.Repetition = (New-ScheduledTaskTrigger -Once -At $startAt -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 365)).Repetition

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30) `
    -RestartCount 2 `
    -RestartInterval (New-TimeSpan -Minutes 5) `
    -MultipleInstances IgnoreNew

$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger @($logonTrigger, $repeatTrigger) `
    -Settings $settings -Principal $principal -Description "Auto-dispatch solver REMOTE_RUN_REQUESTs to remote CPU/GPU (self-service)." | Out-Null

Write-Output ("Installed scheduled task: " + $taskName + " (every 5 min; runs the remote-run-request watcher).")
