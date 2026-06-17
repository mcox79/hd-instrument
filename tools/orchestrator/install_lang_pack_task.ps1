# Install hd_lang_pack_download as a Windows scheduled task that runs
# every 5 minutes until self-unregistered (download script removes the
# task when all packs are present + PROVENANCE.md written).

$ErrorActionPreference = "Stop"

$taskName = "hd_lang_pack_download"
$scriptPath = "C:/Users/marsh/lang_dl.ps1"

# Uninstall any existing instance
try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
} catch {}

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$scriptPath`""
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddSeconds(15) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Hours 24)
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 15) `
    -MultipleInstances IgnoreNew

$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal | Out-Null

Write-Output ("REGISTERED " + $taskName)
Write-Output "Runs every 5 minutes for up to 24 hours; self-unregisters when all packs present + PROVENANCE.md written"
