# revive_cpu_runner_via_schtasks.ps1
# SCPed to marsh@home and invoked via SSH to register + start cpu_runner_0
# under Windows Task Scheduler (survives SSH disconnect; parented to svchost,
# not the SSH session).
#
# Includes -X utf8 flag so PYTHONIOENCODING=utf-8 is active in the runner
# process, preventing cp1252 crashes in scripts that emit non-ASCII chars.

$taskName  = "hd_cpu_runner_0"
$queueDir  = "C:\dev\hd-instrument\data\remote_cpu_queue"
$runnerId  = "cpu_runner_0"
$logFile   = "C:\dev\hd-instrument\data\logs\cpu_runner_0.log"
$launcher  = "C:\dev\hd-instrument\cpu_runner_0_launcher.bat"

# /TR must be <= 261 chars. Use a launcher batch file as the target.
# The batch file has the full command with -X utf8 and log redirect.
$tr = "`"$launcher`""

Write-Output "=== hd_cpu_runner_0 revival via Task Scheduler ==="
Write-Output "Task name : $taskName"
Write-Output "Command   : $tr"
Write-Output ""

# Ensure log directory exists
$logDir = Split-Path $logFile
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
    Write-Output "Created log dir: $logDir"
}

# Delete any stale task with the same name (ignore errors if it does not exist)
# Use cmd /c to suppress non-zero exit without triggering PS native error handling
cmd /c "schtasks /Delete /TN $taskName /F" | Out-Null

# Register the task: ONCE trigger at 00:00 is a dummy trigger.
# /Run below fires it immediately.
# /RU SYSTEM runs under the SYSTEM account (no interactive session needed).
# /RL HIGHEST gives the task elevated privilege.
# NOTE: /RU SYSTEM is required; "Interactive only" tasks cannot be /Run via SSH.
$createResult = schtasks /Create /TN $taskName /TR $tr /SC ONCE /ST 00:00 /F /RL HIGHEST /RU SYSTEM 2>&1
Write-Output "schtasks /Create: $createResult"

if ($LASTEXITCODE -ne 0) {
    Write-Output "ERROR: schtasks /Create failed (exit $LASTEXITCODE). Aborting."
    exit 1
}

# Run the task immediately
$runResult = schtasks /Run /TN $taskName 2>&1
Write-Output "schtasks /Run   : $runResult"

if ($LASTEXITCODE -ne 0) {
    Write-Output "ERROR: schtasks /Run failed (exit $LASTEXITCODE)."
    exit 1
}

# Brief pause so the task scheduler actually starts the process
Start-Sleep -Seconds 4

# Verify: query the task status
Write-Output ""
Write-Output "=== Task status ==="
schtasks /Query /TN $taskName /FO LIST 2>&1

# Verify: confirm python.exe is in Services session (session 0 = schtasks-launched)
Write-Output ""
Write-Output "=== python.exe processes (Services session = Task Scheduler) ==="
tasklist /fi "imagename eq python.exe" /fo csv

# Show current heartbeat file if it exists
$hbFile = "$queueDir\heartbeat.$runnerId.json"
Write-Output ""
Write-Output "=== Heartbeat file ==="
if (Test-Path $hbFile) {
    Get-Content $hbFile
} else {
    Write-Output "(not yet written - runner may still be initializing)"
}

Write-Output ""
Write-Output "=== Done. To manage the task: ==="
Write-Output "  Stop : schtasks /End    /TN $taskName"
Write-Output "  Start: schtasks /Run    /TN $taskName"
Write-Output "  Del  : schtasks /Delete /TN $taskName /F"
Write-Output "  Query: schtasks /Query  /TN $taskName /FO LIST"
