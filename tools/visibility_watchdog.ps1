# Visibility watchdog: independent of Claude. Runs from Windows Task Scheduler
# every 20 min. Checks data\local_dashboard_snapshot.json for freshness and
# monitor health, writes an alert file if degraded, clears it when healthy.
#
# Output:
#   data\log\visibility_watchdog.log   - one line per run, append-only
#   data\log\visibility_watchdog_alert.md - present only when alert is active

$ErrorActionPreference = 'Continue'
$root = 'D:\AI\hd-instrument'
$snapshot = Join-Path $root 'data\local_dashboard_snapshot.json'
$alert = Join-Path $root 'data\log\visibility_watchdog_alert.md'
$log = Join-Path $root 'data\log\visibility_watchdog.log'
$logDir = Split-Path $log -Parent
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Force -Path $logDir | Out-Null }

function Write-WatchdogLog($msg) {
    $line = "[$(Get-Date -Format 'yyyy-MM-ddTHH:mm:ss')] $msg"
    Add-Content -Path $log -Value $line -Encoding utf8
}

$problems = New-Object System.Collections.Generic.List[string]

if (-not (Test-Path $snapshot)) {
    $problems.Add("snapshot file missing at $snapshot - monitor never ran or path moved")
} else {
    try {
        $raw = Get-Content $snapshot -Raw -Encoding utf8
        $d = $raw | ConvertFrom-Json
        $ts = [datetime]::Parse($d.ts)
        $age_s = [int]((Get-Date) - $ts).TotalSeconds
        if ($age_s -gt 90) {
            $problems.Add("snapshot ts is ${age_s}s old (>90s) - monitor process likely dead")
        }
        if ($d.PSObject.Properties.Name -contains 'monitor_health' -and $d.monitor_health -ne $null) {
            $h = $d.monitor_health
            if ($h.PSObject.Properties.Name -contains 'stale_for_s' -and $h.stale_for_s -ne $null) {
                $stale_s = [int]$h.stale_for_s
                if ($stale_s -gt 300) {
                    $problems.Add("monitor_health.stale_for_s = ${stale_s}s (>300s) - SSH or remote workstation degraded")
                }
            }
            if ($h.PSObject.Properties.Name -contains 'status' -and $h.status -ne $null -and $h.status -ne 'ok') {
                $err = if ($h.last_error) { "$($h.last_error.type): $($h.last_error.msg)" } else { '(none)' }
                $problems.Add("monitor_health.status=$($h.status) last_error=$err")
            }
        }
    } catch {
        $problems.Add("snapshot parse error: $($_.Exception.Message)")
    }
}

if ($problems.Count -gt 0) {
    $body = @"
# Visibility watchdog alert
Generated: $(Get-Date -Format 'yyyy-MM-ddTHH:mm:ss')

$($problems -join "`r`n")

Relaunch command (run from D:\AI\hd-instrument):
``````powershell
`$cwd = 'D:\AI\hd-instrument'
`$py = Join-Path `$cwd '.venv\Scripts\pythonw.exe'
Start-Process -FilePath `$py -ArgumentList 'tools\local_dashboard_monitor.py' -WorkingDirectory `$cwd -RedirectStandardError (Join-Path `$cwd 'data\log\local_dashboard_monitor.err.log') -WindowStyle Hidden -PassThru
``````
"@
    Set-Content -Path $alert -Value $body -Encoding utf8
    Write-WatchdogLog ("ALERT: " + ($problems -join '; '))
} else {
    if (Test-Path $alert) { Remove-Item $alert -Force }
    Write-WatchdogLog "ok"
}
