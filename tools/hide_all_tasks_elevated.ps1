# Set Hidden=$true on all hd_* scheduled tasks (eliminates console popups).
# REQUIRES UAC: S4U tasks need admin to modify.
# Run from an elevated PowerShell window.

$tasks = @(
    'hd_blocker_ping',
    'hd_cpu_runner_local',
    'hd_dashboard',
    'hd_durability_cron',
    'hd_health_check',
    'hd_heartbeat_watchdog',
    'hd_metrics_sync',
    'hd_orch_daily_audit',
    'hd_orch_daily_research_drill',
    'hd_orch_scope_expansion',
    'hd_orchestrator_watchdog',
    'hd_session_watchdog'
)

foreach ($n in $tasks) {
    $t = Get-ScheduledTask -TaskName $n -ErrorAction SilentlyContinue
    if (-not $t) { Write-Host "  SKIP  $n (not found)" -ForegroundColor Yellow; continue }
    if ($t.Settings.Hidden) { Write-Host "  OK    $n (already Hidden)" -ForegroundColor Green; continue }
    try {
        $t.Settings.Hidden = $true
        Set-ScheduledTask -TaskName $n -Settings $t.Settings -ErrorAction Stop | Out-Null
        Write-Host "  SET   $n -> Hidden=True" -ForegroundColor Green
    } catch {
        Write-Host "  FAIL  $n -> $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Done. Trigger frequencies:" -ForegroundColor Cyan
Write-Host "  hd_health_check     every 15min"
Write-Host "  hd_metrics_sync     every 20min"
Write-Host "  hd_blocker_ping     every 30min"
Write-Host "  (others fire at logon or daily)"
