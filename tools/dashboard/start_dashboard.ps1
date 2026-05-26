# Start the hd-instrument dashboard on 0.0.0.0:8765.
# Reachable via localhost AND Tailscale (http://frameworkmpc:8765).
# Ctrl+C to stop.

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$VenvPython = Join-Path $ScriptDir ".venv\Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "venv missing at $VenvPython" -ForegroundColor Red
    Write-Host "create it with:" -ForegroundColor Yellow
    Write-Host "  python -m venv `"$ScriptDir\.venv`""
    Write-Host "  & `"$VenvPython`" -m pip install -r `"$ScriptDir\requirements.txt`""
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
