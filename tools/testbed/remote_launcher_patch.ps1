$ErrorActionPreference = 'Stop'

$files = @(
    'C:\dev\hd-instrument\tools\orchestrator\cpu_runner_0_launcher.bat',
    'C:\dev\hd-instrument\tools\orchestrator\gpu_runner_0_launcher.bat'
)

foreach ($f in $files) {
    if (-not (Test-Path $f)) {
        Write-Output "MISSING: $f"
        continue
    }
    $content = Get-Content $f -Raw
    $original = $content
    # Replace .venv\Scripts\python.exe with pythonw.exe (handles both forward and back slashes)
    $patched = $content -replace [regex]::Escape('\.venv\Scripts\python.exe'), '\.venv\Scripts\pythonw.exe'
    $patched = $patched -replace [regex]::Escape('/.venv/Scripts/python.exe'), '/.venv/Scripts/pythonw.exe'
    if ($patched -ne $original) {
        # Backup
        Copy-Item $f "$f.popup_backup_$(Get-Date -Format 'yyyyMMddHHmmss')"
        Set-Content -Path $f -Value $patched -Encoding ASCII -NoNewline
        Write-Output "PATCHED: $f"
    } else {
        Write-Output "NOCHANGE: $f"
    }
}

Write-Output ""
Write-Output "=== verify ==="
foreach ($f in $files) {
    Write-Output "--- $f ---"
    Get-Content $f
    Write-Output ""
}
