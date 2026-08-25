# Install hd_capability_registry_audit as a Windows scheduled task.
# Runs tools/capability_registry_audit.py daily: computes integration_status (wired vs
# islanded) per data/capability_registry.jsonl row from the live import graph, flags
# undecided chain-grade capability_family rows (cross-ref substrate_capabilities_view.json)
# and stale VET_PENDING gate decisions. Writes data/capability_registry_reports/*.json.
#
# NOTE (testbed 2026-07-28): this is the SECONDARY/belt durability anchor. The PRIMARY
# anchor is the CLAUDE.md process-rule hook (land-time gate + session-start read of
# capability_registry.jsonl) -- this session discovered that 11 of 14 hd_* scheduled
# tasks were SILENTLY mass-disabled 2026-07-16/17 for ~12 days with zero alarm (see
# testbed audit report). A cron-only nag inherits that exact fragility (nothing checks
# whether the CHECKER itself got disabled). Register this for the redundancy, but do
# not treat it as sufficient on its own.

$ErrorActionPreference = "Stop"

$taskName = "hd_capability_registry_audit"
$pythonExe = "C:/AI/hd-instrument/.venv/Scripts/python.exe"
$scriptPath = "C:/AI/hd-instrument/tools/capability_registry_audit.py"

if (-not (Test-Path $scriptPath)) { Write-Error ("capability_registry_audit.py not at " + $scriptPath); exit 1 }
if (-not (Test-Path $pythonExe)) { Write-Error ("venv python not at " + $pythonExe); exit 1 }

try { Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue } catch {}

$action = New-ScheduledTaskAction `
    -Execute $pythonExe `
    -Argument ("`"" + $scriptPath + "`"") `
    -WorkingDirectory "C:/AI/hd-instrument"

$dailyTrigger = New-ScheduledTaskTrigger -Daily -At 5:15AM

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
    -Trigger $dailyTrigger `
    -Settings $settings `
    -Principal $principal | Out-Null

Write-Output ("REGISTERED " + $taskName)
Write-Output "Cadence: daily 05:15 (StartWhenAvailable)"
Write-Output "Secondary anchor only -- primary durability = CLAUDE.md process-rule (land-time gate + session-start read)."
