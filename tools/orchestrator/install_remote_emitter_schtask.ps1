# Install Windows scheduled task on marsh@home that runs remote_state_emitter.py.
#
# The emitter runs its own while-True loop, so we only need ONE trigger: ONLOGON.
# Task Scheduler restarts it (RestartCount=10) if it crashes, and the ONLOGON
# trigger fires again automatically after a reboot — so the bridge self-heals on
# both local crashes and system reboots without any manual intervention.
#
# Run this script ONCE on marsh@home (not on the local machine).
# Usage:
#   powershell -ExecutionPolicy Bypass -File C:\dev\hd-instrument\tools\orchestrator\install_remote_emitter_schtask.ps1

$taskName   = "hd_remote_state_emitter"
$python     = "C:\dev\hd-instrument\.venv\Scripts\pythonw.exe"
$script     = "C:\dev\hd-instrument\tools\orchestrator\remote_state_emitter.py"

# Remove stale task if it exists
if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "Removed existing task: $taskName"
}

# ONLOGON trigger: fires once per logon session.  The emitter's while-True loop
# keeps it running indefinitely.  RestartCount handles crashes between logons.
$action  = New-ScheduledTaskAction -Execute $python -Argument $script
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
    -RestartCount 10 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false

# Interactive logon principal (same user who owns the SSH keys and venv).
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest

Register-ScheduledTask `
    -TaskName  $taskName `
    -Action    $action `
    -Trigger   $trigger `
    -Settings  $settings `
    -Principal $principal `
    -Description "hd-instrument remote state emitter - writes remote_state_cache.json every 30s; auto-starts on logon"

Write-Host "Task '$taskName' registered. Starting now..."
Start-ScheduledTask -TaskName $taskName
Write-Host ("Done. Verify with: schtasks /Query /TN " + $taskName + " /V /FO LIST")
