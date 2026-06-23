# Start the hd-instrument dashboard on 0.0.0.0:8765.
# Reachable via localhost AND Tailscale (http://frameworkmpc:8765).
# Ctrl+C to stop.

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
# Use the project main venv (has torch+numpy+all deps for substrate chat KGStore pickle.load).
# Previously used $ScriptDir\.venv which was missing torch+numpy and broke chat with
# "no substrate cache" (pickle.load raised ModuleNotFoundError silently). Fix 2026-06-22.
$RepoRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "project venv missing at $VenvPython" -ForegroundColor Red
    Write-Host "create it with:" -ForegroundColor Yellow
    Write-Host "  python -m venv `"$RepoRoot\.venv`""
    Write-Host "  & `"$VenvPython`" -m pip install -r `"$RepoRoot\requirements.txt`""
    exit 1
}

# Bind on all interfaces so Tailscale peers (and LAN) can reach the dashboard.
# 127.0.0.1 access is preserved automatically when binding 0.0.0.0.
$BindHost = "0.0.0.0"
$BindPort = 8765
$Url = "http://frameworkmpc:${BindPort}/"

Write-Host "hd-instrument dashboard -> $Url" -ForegroundColor Green
Write-Host "Also reachable at http://100.124.176.29:${BindPort}/ (Tailscale IP)" -ForegroundColor DarkGray
Write-Host "Ctrl+C to stop." -ForegroundColor DarkGray
Write-Host ""

& $VenvPython -m uvicorn server:app --app-dir $ScriptDir --host $BindHost --port $BindPort --log-level info
