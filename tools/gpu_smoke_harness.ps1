# GPU smoke harness for Fix #24 verification.
# Runs a cell with --smoke and concurrent nvidia-smi sampling.
# Reports gpu_util_p50 + smoke exit code so caller can gate dispatch.
#
# Usage:
#   pwsh tools/gpu_smoke_harness.ps1 -Script <path> -Anchor <name> -TimeoutSec <int>
#
# Output (last line; parse-friendly):
#   GPU_SMOKE_RESULT exit=<n> util_p50=<int> util_max=<int> samples=<n> elapsed_s=<f>

param(
    [Parameter(Mandatory=$true)] [string]$Script,
    [Parameter(Mandatory=$true)] [string]$Anchor,
    [int]$TimeoutSec = 600
)

$ErrorActionPreference = 'Continue'
$repo = "C:\dev\hd-instrument"
$python = Join-Path $repo ".venv\Scripts\python.exe"
$logFile = Join-Path $repo "data\_gpusmoke_$Anchor.log"
$csvFile = Join-Path $repo "data\_gpusmoke_$Anchor.csv"

# Clear prior outputs.
if (Test-Path $logFile) { Remove-Item $logFile -Force }
if (Test-Path $csvFile) { Remove-Item $csvFile -Force }

# Launch nvidia-smi sampler in background (1s interval).
$sampler = Start-Process -FilePath "nvidia-smi" `
    -ArgumentList "--query-gpu=utilization.gpu,memory.used", "--format=csv,noheader,nounits", "-l", "1" `
    -RedirectStandardOutput $csvFile `
    -NoNewWindow `
    -PassThru

Start-Sleep -Milliseconds 500  # give sampler time to start

# Run the smoke synchronously with timeout.
$env:HDLAB_EXP_NAME = "${Anchor}_gpusmoke"
$env:HDLAB_RUN_MODE = "smoke"

$sw = [System.Diagnostics.Stopwatch]::StartNew()
$smoke = Start-Process -FilePath $python `
    -ArgumentList "$repo\$Script", "--smoke" `
    -WorkingDirectory $repo `
    -RedirectStandardOutput $logFile `
    -RedirectStandardError "$logFile.err" `
    -NoNewWindow `
    -PassThru

$exited = $smoke.WaitForExit($TimeoutSec * 1000)
$sw.Stop()
$elapsed = [math]::Round($sw.Elapsed.TotalSeconds, 1)

if (-not $exited) {
    try { Stop-Process -Id $smoke.Id -Force -ErrorAction SilentlyContinue } catch {}
    $exitCode = -1
} else {
    $exitCode = $smoke.ExitCode
}

# Stop the sampler.
try { Stop-Process -Id $sampler.Id -Force -ErrorAction SilentlyContinue } catch {}
Start-Sleep -Milliseconds 200  # let final samples flush

# Parse util samples.
$util = @()
if (Test-Path $csvFile) {
    foreach ($line in Get-Content $csvFile) {
        $parts = $line.Split(',')
        if ($parts.Length -ge 1) {
            $u = $parts[0].Trim()
            if ($u -match '^\d+$') {
                $util += [int]$u
            }
        }
    }
}

if ($util.Count -eq 0) {
    Write-Output "GPU_SMOKE_RESULT exit=$exitCode util_p50=-1 util_max=-1 samples=0 elapsed_s=$elapsed"
    exit 1
}

$sorted = $util | Sort-Object
$p50 = $sorted[[int]($sorted.Count / 2)]
$max = ($util | Measure-Object -Maximum).Maximum

Write-Output "GPU_SMOKE_RESULT exit=$exitCode util_p50=$p50 util_max=$max samples=$($util.Count) elapsed_s=$elapsed"
