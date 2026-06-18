# hd_dispatch_consumer: remote-pull dispatch pattern.
# Runs on REMOTE every 60s as scheduled task. Pulls dispatch_requests/
# manifests from git + processes them via local queue_add.py.
#
# Pattern (industry standard for flaky-link orchestration):
#   1. Local (laptop) writes data/dispatch_requests/<name>.json + commits + pushes
#   2. Remote scheduled task: git pull + process new manifests
#   3. Each manifest = queue_add.py args; run, mark processed (move to processed/)
#   4. No live SSH from laptop required for dispatch
#
# Hardening (per USER directive + lessons from prior tasks):
#   - PID-and-age lock (no CPU pile-up)
#   - Bounded execution per run (10 min ExecutionTimeLimit)
#   - MultipleInstances IgnoreNew via task settings
#   - git pull failure-tolerant; exit + retry next run
#   - Per-manifest try/catch: one failure doesn't block others
#   - Idempotent: already-processed manifests skipped (moved to processed/)
#   - Log rotation at 1MB
#   - No retry budget cap (recurring infra)
#
# ASCII only.

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

$repo = "C:/dev/hd-instrument"
$dataDir = Join-Path $repo "data"
$stateDir = Join-Path $dataDir ".dispatch_consumer"
$lockPath = Join-Path $stateDir ".lock"
$logPath = Join-Path $stateDir "consumer.log"
$statusPath = Join-Path $stateDir "status.json"
$requestsDir = Join-Path $dataDir "dispatch_requests"
$processedDir = Join-Path $requestsDir "processed"
$failedDir = Join-Path $requestsDir "failed"

foreach ($d in @($stateDir, $requestsDir, $processedDir, $failedDir)) {
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
}

function Write-Log($msg) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    try {
        if ((Test-Path $logPath) -and ((Get-Item $logPath).Length -gt 1MB)) {
            Move-Item $logPath ($logPath + ".1") -Force -ErrorAction SilentlyContinue
        }
        Add-Content -Path $logPath -Value "[$ts] PID=$PID $msg" -Encoding ASCII -ErrorAction SilentlyContinue
    } catch {}
}

# Strong lock (PID + age)
if (Test-Path $lockPath) {
    $content = Get-Content $lockPath -Raw -ErrorAction SilentlyContinue
    $age = ((Get-Date) - (Get-Item $lockPath).LastWriteTime).TotalMinutes
    $lockPid = 0
    if ($content) {
        $parts = $content.Trim().Split(":")
        if ($parts.Length -gt 0) { [int]::TryParse($parts[0], [ref]$lockPid) | Out-Null }
    }
    $alive = $false
    if ($lockPid -gt 0) {
        try {
            if (Get-Process -Id $lockPid -ErrorAction SilentlyContinue) { $alive = $true }
        } catch {}
    }
    if ($alive -and $age -lt 12) {
        Write-Log ("LOCKED PID={0} age={1:N1}min exit" -f $lockPid, $age)
        exit 0
    }
    Write-Log ("STALE lock PID={0} age={1:N1}min alive={2} clearing" -f $lockPid, $age, $alive)
    Remove-Item $lockPath -Force -ErrorAction SilentlyContinue
}
Set-Content -Path $lockPath -Value ("{0}:{1}" -f $PID, (Get-Date).ToString("o")) -ErrorAction SilentlyContinue

try {
    Write-Log "RUN START"
    Set-Location $repo

    # Step 1: git pull (fast-forward only; resilient)
    try {
        $env:GIT_TERMINAL_PROMPT = "0"
        & git fetch origin main 2>$null | Out-Null
        & git merge --ff-only origin/main 2>&1 | Out-Null
        Write-Log "GIT pulled"
    } catch {
        Write-Log ("GIT pull failed: " + $_.Exception.Message)
    }

    # Step 2: scan dispatch_requests/*.json
    $manifests = Get-ChildItem -Path $requestsDir -Filter "*.json" -File -ErrorAction SilentlyContinue
    $processed = 0
    $failed = 0
    foreach ($m in $manifests) {
        try {
            $manifest = Get-Content $m.FullName -Raw | ConvertFrom-Json

            # Required fields
            $queue = $manifest.queue
            $name = $manifest.name
            $script = $manifest.script
            $prereg = $manifest.prereg
            $timeout = if ($manifest.timeout_s) { [int]$manifest.timeout_s } else { 3600 }
            $skipSmoke = if ($manifest.skip_smoke) { $true } else { $false }

            if (-not $queue -or -not $name -or -not $script -or -not $prereg) {
                Write-Log ("MANIFEST INVALID {0}: missing required fields" -f $m.Name)
                Move-Item $m.FullName (Join-Path $failedDir $m.Name) -Force -ErrorAction SilentlyContinue
                $failed += 1
                continue
            }

            Write-Log ("PROCESS {0} queue={1} name={2}" -f $m.Name, $queue, $name)

            # Build queue_add.py invocation
            $pythonExe = Join-Path $repo ".venv/Scripts/python.exe"
            $queueAddPy = Join-Path $repo "tools/queue_add.py"
            $args = @(
                $queueAddPy,
                $queue,
                $name,
                $script,
                "--prereg", $prereg,
                "--timeout", $timeout
            )
            if ($skipSmoke) { $args += "--skip-smoke" }

            $env:HDLAB_QUEUE_ADD_ON_REMOTE = "1"
            $out = & $pythonExe $args 2>&1 | Out-String
            $exit = $LASTEXITCODE

            if ($exit -eq 0) {
                Write-Log ("OK {0}: queued {1}" -f $m.Name, $name)
                Move-Item $m.FullName (Join-Path $processedDir $m.Name) -Force -ErrorAction SilentlyContinue
                $processed += 1
            } else {
                Write-Log ("FAIL {0}: queue_add exit={1} -- {2}" -f $m.Name, $exit, $out.Substring(0, [math]::Min(200, $out.Length)))
                Move-Item $m.FullName (Join-Path $failedDir $m.Name) -Force -ErrorAction SilentlyContinue
                $failed += 1
            }
        } catch {
            Write-Log ("THROW {0}: {1}" -f $m.Name, $_.Exception.Message)
            try { Move-Item $m.FullName (Join-Path $failedDir $m.Name) -Force -ErrorAction SilentlyContinue } catch {}
            $failed += 1
        }
    }

    # Step 3: status
    $status = @{
        last_run_utc = (Get-Date).ToUniversalTime().ToString("o")
        manifests_seen = $manifests.Count
        processed = $processed
        failed = $failed
    } | ConvertTo-Json
    Set-Content -Path $statusPath -Value $status -Encoding ASCII

    Write-Log ("RUN END seen={0} processed={1} failed={2}" -f $manifests.Count, $processed, $failed)
} finally {
    if (Test-Path $lockPath) { Remove-Item $lockPath -Force -ErrorAction SilentlyContinue }
}
