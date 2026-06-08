# Persistent start of backend + cloudflared on runner.
# Writes logs to C:\Users\marsh\ so we can poll them externally.

$ErrorActionPreference = "Stop"
$BackendLog = "C:\Users\marsh\backend.log"
$CFLog = "C:\Users\marsh\cloudflared.log"
$BackendPid = "C:\Users\marsh\backend.pid"
$CFPid = "C:\Users\marsh\cloudflared.pid"

# Kill any previous instances first (clean state)
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object {
    try { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue } catch {}
}
Get-Process cloudflared -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

# Clear stale logs
Remove-Item $BackendLog, $CFLog -ErrorAction SilentlyContinue

# Start the FastAPI backend detached
$be = Start-Process `
    -FilePath "C:\dev\hd-instrument\.venv-demo\Scripts\python.exe" `
    -ArgumentList @("-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000") `
    -WorkingDirectory "C:\dev\hd-instrument" `
    -RedirectStandardOutput $BackendLog `
    -RedirectStandardError "$BackendLog.err" `
    -WindowStyle Hidden -PassThru
$be.Id | Out-File -Encoding ascii $BackendPid
Write-Host "backend PID: $($be.Id)"

# Give backend 5 seconds to boot
Start-Sleep -Seconds 5

# Start cloudflared with the trycloudflare quick mode (no auth required)
$cf = Start-Process `
    -FilePath "C:\Program Files (x86)\cloudflared\cloudflared.exe" `
    -ArgumentList @("tunnel", "--url", "http://localhost:8000") `
    -RedirectStandardOutput $CFLog `
    -RedirectStandardError "$CFLog.err" `
    -WindowStyle Hidden -PassThru
$cf.Id | Out-File -Encoding ascii $CFPid
Write-Host "cloudflared PID: $($cf.Id)"

# Wait for cloudflared to print its URL (typically 5-15 sec)
Write-Host "Waiting up to 30s for cloudflared to provision URL..."
$publicUrl = $null
$start = Get-Date
while (((Get-Date) - $start).TotalSeconds -lt 30) {
    Start-Sleep -Seconds 2
    foreach ($logPath in @($CFLog, "$CFLog.err")) {
        if (Test-Path $logPath) {
            $content = Get-Content $logPath -Raw -ErrorAction SilentlyContinue
            if ($content -match "https://[a-z0-9-]+\.trycloudflare\.com") {
                $publicUrl = $matches[0]
                break
            }
        }
    }
    if ($publicUrl) { break }
}

Write-Host "=== STATUS ==="
if ($publicUrl) {
    Write-Host "PUBLIC URL: $publicUrl"
    "PUBLIC_URL=$publicUrl" | Out-File -Encoding ascii C:\Users\marsh\public_url.txt
} else {
    Write-Host "PUBLIC URL: (not yet provisioned; check cloudflared.log)"
}
Write-Host "backend.log tail:"
Get-Content $BackendLog -Tail 5 -ErrorAction SilentlyContinue
Write-Host "cloudflared.log tail:"
Get-Content $CFLog -Tail 8 -ErrorAction SilentlyContinue
if (Test-Path "$CFLog.err") {
    Write-Host "cloudflared.err tail:"
    Get-Content "$CFLog.err" -Tail 8 -ErrorAction SilentlyContinue
}
