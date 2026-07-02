# Install Windows scheduled task on marsh@home for the hd-instrument remote
# state emitter. RESILIENT VERSION (testbed 2026-07-02 fix):
#
#   * Runs as SYSTEM (no interactive-session requirement, survives reboots
#     without any user login). Mirrors hd_gpu_runner_0 / hd_cpu_runner_0.
#   * ONSTART trigger: starts on boot before any login.
#   * ONLOGON trigger: redundant safety if the machine is already booted
#     and just a user re-logs in.
#   * 5-minute repetition safeguard: if the emitter dies AND Task Scheduler's
#     RestartCount is exhausted, the repetition trigger relaunches the
#     launcher.bat which no-ops if the emitter is still alive (singleton
#     guard in the .bat) or respawns it if not.
#   * -MultipleInstances IgnoreNew: never stack instances.
#
# Root cause of the 3-day-stale bug (2026-06-29T10:06 -> 2026-07-02T14:45):
# original install used ONLOGON-only + Interactive principal. After a reboot
# with no user login, the task never fired again. The launcher.bat + SYSTEM +
# ONSTART pattern fixes this permanently.
#
# Usage (run once on marsh@home as Administrator):
#   powershell -ExecutionPolicy Bypass -File `
#       C:\dev\hd-instrument\tools\orchestrator\install_remote_emitter_schtask.ps1

$taskName = "hd_remote_state_emitter"
$launcher = "C:\dev\hd-instrument\tools\remote_launchers\remote_state_emitter_launcher.bat"

if (-not (Test-Path $launcher)) {
    Write-Error "Launcher not found: $launcher (copy remote_state_emitter_launcher.bat there first)"
    exit 1
}

# Remove stale task if present
if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "Removed existing task: $taskName"
}

$action = New-ScheduledTaskAction -Execute $launcher

# Triggers: ONSTART (survives reboots with no login) + ONLOGON (belt-and-braces).
# Plus a 5-min repetition on a ONCE trigger so a killed emitter respawns
# even if Task Scheduler's RestartCount is exhausted. The launcher.bat
# singleton check keeps this idempotent (no-op if emitter already alive).
# RepetitionDuration must be a real TimeSpan (MaxValue rejected by Task
# Scheduler XML validator) — 365d is effectively "forever" for our purpose;
# ONSTART re-arms it after every reboot anyway.
$triggerBoot   = New-ScheduledTaskTrigger -AtStartup
$triggerLogon  = New-ScheduledTaskTrigger -AtLogOn
$triggerRepeat = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(2) `
    -RepetitionInterval (New-TimeSpan -Minutes 5) `
    -RepetitionDuration (New-TimeSpan -Days 365)

$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
    -RestartCount 10 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -RunOnlyIfNetworkAvailable:$false

# SYSTEM principal — same as hd_gpu_runner_0 / hd_cpu_runner_0. No user session
# needed. NetworkService can't SCP-authenticate; LocalSystem writes to
# C:\dev\hd-instrument\data\remote_state_cache.json fine (runners already do).
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask `
    -TaskName  $taskName `
    -Action    $action `
    -Trigger   @($triggerBoot, $triggerLogon, $triggerRepeat) `
    -Settings  $settings `
    -Principal $principal `
    -Description "hd-instrument remote state emitter - writes remote_state_cache.json every 30s. SYSTEM + ONSTART + ONLOGON + 5min repeat safeguard. testbed 2026-07-02."

Write-Host "Task '$taskName' registered."
Start-ScheduledTask -TaskName $taskName
Write-Host "Started task. Verify with: schtasks /Query /TN $taskName /V /FO LIST"
