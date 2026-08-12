# wake_stopped_claude_sessions.ps1
# USER-opt-in mechanism for automatically waking stopped Claude Code sessions
# in VSCode windows by sending keyboard input via Windows API.
#
# Concept:
#   1. Enumerate all Code.exe windows (VSCode parent windows)
#   2. For each, find the Claude Code session in that window via the
#      claude.exe child process's --resume <UUID> arg
#   3. Read fleet staleness from data/fleet_status_NOW.md (Testbed-maintained)
#   4. For each stale role: focus the matching VSCode window + SendKeys
#      "continue<Enter>" — wakes the Claude session by submitting a prompt
#
# RISKS (READ BEFORE ENABLING):
#   - SendKeys could inject input MID-TASK if a session is actually working
#     (rare — usually idle when stale >30min, but possible)
#   - Window title detection is fragile (workspace path determines match)
#   - Requires VSCode windows to remain open (won't help closed sessions)
#   - Bringing windows to foreground steals focus from whatever USER is doing
#
# Run manually first to verify behavior:
#   powershell.exe -ExecutionPolicy Bypass -File tools/wake_stopped_claude_sessions.ps1 -DryRun
#
# Then enable as scheduled task (every 30min while USER away):
#   powershell.exe -ExecutionPolicy Bypass -File tools/register_wake_task_elevated.ps1
#
# DISABLE: schtasks /Change /TN hd_wake_stopped_sessions /DISABLE
#
# Author: Testbed (Integrator), USER-authorized 2026-06-21 absence

[CmdletBinding()]
param(
    [switch]$DryRun,
    [int]$StaleThresholdMin = 30,
    [string]$WakePrompt = "continue work"
)

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll", CharSet = CharSet.Auto)]
    public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder lpString, int nMaxCount);
    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();
    public const int SW_RESTORE = 9;
}
"@

# Step 1: enumerate all claude.exe processes + extract --resume UUID and parent Code.exe window
$claudeProcs = Get-CimInstance Win32_Process -Filter "Name='claude.exe'"
$sessionMap = @{}  # session_uuid -> @{ pid, parent_pid, code_window_title }
foreach ($p in $claudeProcs) {
    $cmd = $p.CommandLine
    if (-not $cmd) { continue }
    $m = [regex]::Match($cmd, '--resume\s+([a-f0-9-]{36})')
    if (-not $m.Success) { continue }
    $uuid = $m.Groups[1].Value
    $parentPid = $p.ParentProcessId
    # Walk up parent chain to find Code.exe
    $cur = $parentPid
    $codeWinTitle = $null
    for ($i = 0; $i -lt 5; $i++) {
        $parent = Get-CimInstance Win32_Process -Filter "ProcessId=$cur" -ErrorAction SilentlyContinue
        if (-not $parent) { break }
        if ($parent.Name -eq "Code.exe") {
            # Get the window title for this Code.exe process
            try {
                $proc = Get-Process -Id $cur -ErrorAction SilentlyContinue
                if ($proc -and $proc.MainWindowTitle) {
                    $codeWinTitle = $proc.MainWindowTitle
                }
            } catch {}
            break
        }
        $cur = $parent.ParentProcessId
    }
    $sessionMap[$uuid] = @{
        Pid = $p.ProcessId
        ParentPid = $parentPid
        CodeWindowTitle = $codeWinTitle
    }
}

Write-Host "Found $($sessionMap.Count) Claude Code sessions:"
foreach ($uuid in $sessionMap.Keys) {
    $s = $sessionMap[$uuid]
    Write-Host "  uuid=$uuid pid=$($s.Pid) code_title='$($s.CodeWindowTitle)'"
}

# Step 2: read fleet status to determine which roles are stale
$statusPath = "D:\AI\hd-instrument\data\fleet_status_NOW.md"
if (-not (Test-Path $statusPath)) {
    Write-Host "FAIL: $statusPath missing — cannot determine stale sessions" -ForegroundColor Red
    exit 1
}
$statusRaw = Get-Content $statusPath -Raw

# Parse stale roles from fleet_status_NOW.md (pattern: "**Nm STALE**")
$staleRoles = @()
foreach ($line in $statusRaw -split "`n") {
    if ($line -match "^\s*-\s+(\w+):\s+\*\*~?(\d+)m\s+STALE\*\*") {
        $role = $matches[1]
        $ageM = [int]$matches[2]
        if ($ageM -ge $StaleThresholdMin) {
            $staleRoles += @{ Role = $role; AgeM = $ageM }
        }
    }
}
Write-Host ""
Write-Host "Stale roles (>=$StaleThresholdMin min):"
foreach ($r in $staleRoles) {
    Write-Host "  $($r.Role): $($r.AgeM)m"
}

if ($staleRoles.Count -eq 0) {
    Write-Host "Nothing to wake."
    exit 0
}

# Step 3: for each stale role, find the matching session by window title
# (Heuristic: VSCode window title typically contains workspace folder name
# which differs per session; for hd-instrument they're all the same project
# so we'd need a more reliable mapping. For now: log mapping problem.)
#
# Practical approach: USER assigns session UUID to each role via a config file
# data/session_local/role_uuid_map.json. If absent, just list available
# sessions and let USER pick.

$roleMapPath = "D:\AI\hd-instrument\data\session_local\role_uuid_map.json"
if (-not (Test-Path $roleMapPath)) {
    Write-Host ""
    Write-Host "ROLE-UUID MAP MISSING at $roleMapPath" -ForegroundColor Yellow
    Write-Host "Create it with content like:"
    Write-Host '  {'
    Write-Host '    "research":    "<uuid-for-research-window>",'
    Write-Host '    "exp_dev":     "<uuid-for-exp_dev-window>",'
    Write-Host '    "skunkworks":  "<uuid-for-skunkworks-window>",'
    Write-Host '    "orchestrator":"<uuid-for-orchestrator-window>",'
    Write-Host '    "testbed":     "<uuid-for-testbed-window>"'
    Write-Host '  }'
    Write-Host ""
    Write-Host "Find UUIDs in this script's enumeration output (above)."
    exit 1
}

$roleMap = Get-Content $roleMapPath -Raw | ConvertFrom-Json

# Step 4: send wake to each stale role
foreach ($r in $staleRoles) {
    $role = $r.Role
    $uuid = $roleMap.$role
    if (-not $uuid) {
        Write-Host "SKIP $role : no UUID mapping" -ForegroundColor Yellow
        continue
    }
    $session = $sessionMap[$uuid]
    if (-not $session) {
        Write-Host "SKIP $role : session $uuid not running (window closed?)" -ForegroundColor Yellow
        continue
    }
    Write-Host ""
    Write-Host "WAKE $role (uuid=$uuid pid=$($session.Pid))" -ForegroundColor Cyan
    if ($DryRun) {
        Write-Host "  [DryRun] would focus window + SendKeys '$WakePrompt{Enter}'"
        continue
    }
    # Get window handle from process
    try {
        $proc = Get-Process -Id $session.ParentPid -ErrorAction Stop
        $hWnd = $proc.MainWindowHandle
        if ($hWnd -eq [IntPtr]::Zero) {
            Write-Host "  FAIL: no main window handle (minimized?)" -ForegroundColor Red
            continue
        }
        [Win32]::ShowWindow($hWnd, [Win32]::SW_RESTORE) | Out-Null
        Start-Sleep -Milliseconds 200
        [Win32]::SetForegroundWindow($hWnd) | Out-Null
        Start-Sleep -Milliseconds 500
        [System.Windows.Forms.SendKeys]::SendWait("$WakePrompt{ENTER}")
        Write-Host "  SENT '$WakePrompt' + Enter"
    } catch {
        Write-Host "  FAIL: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Done. Re-run periodically (scheduled task or manual)."
