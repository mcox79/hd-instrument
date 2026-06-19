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

    # Disk-space pre-check (need at least 2 GB)
    $drive = (Get-Item $repo).PSDrive
    $freeGB = [math]::Round($drive.Free / 1GB, 2)
    if ($freeGB -lt 2.0) {
        Write-Log ("DISK LOW free={0}GB exit" -f $freeGB)
        exit 0
    }

    # Step 1: git reconcile -- HARDENED to push remote-side commits to
    # origin FIRST (Testbed-committed-on-remote pattern; if we just reset
    # those commits get backed up and never make it to origin -> infinite
    # divergence loop). New flow:
    #   1. fetch origin
    #   2. if HEAD == origin/main: nothing
    #   3. if HEAD ahead-only of origin/main: try fast-forward push HEAD up
    #   4. if HEAD behind-only: reset (no local commits to lose)
    #   5. if diverged (both): try push HEAD up; if push rejects, preserve
    #      + reset (current behavior)
    try {
        $env:GIT_TERMINAL_PROMPT = "0"
        $localHead = & git rev-parse HEAD 2>$null
        & git fetch origin main 2>$null | Out-Null
        $originHead = & git rev-parse origin/main 2>$null

        if ($localHead -eq $originHead) {
            Write-Log "GIT already at origin/main"
        } else {
            $ahead = & git rev-list --count origin/main..HEAD 2>$null
            $behind = & git rev-list --count HEAD..origin/main 2>$null
            $aheadCount = if ($ahead) { [int]$ahead } else { 0 }
            $behindCount = if ($behind) { [int]$behind } else { 0 }
            Write-Log ("GIT divergence ahead={0} behind={1}" -f $aheadCount, $behindCount)

            if ($aheadCount -gt 0) {
                # Try to push remote's local commits to origin BEFORE any reset.
                # This preserves Testbed-style work + closes the divergence loop.
                & git push origin "HEAD:main" 2>&1 | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    Write-Log ("GIT pushed {0} local commit(s) to origin/main" -f $aheadCount)
                    # If behindCount was also > 0, we'll be ff'd by the push if remote allows
                    # (it won't; remote requires --force on divergence). In that case the push
                    # would have failed; fall through to reset path below.
                    & git fetch origin main 2>$null | Out-Null
                    $newOrigin = & git rev-parse origin/main 2>$null
                    $newHead = & git rev-parse HEAD 2>$null
                    if ($newHead -ne $newOrigin) {
                        # Still diverged after push (likely because origin moved
                        # while we were pushing; try ff merge)
                        & git merge --ff-only origin/main 2>&1 | Out-Null
                    }
                } else {
                    # Push rejected (true divergence: remote ahead + behind)
                    # Fall back to preserve + reset
                    $ts = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
                    $backup = "backup_consumer_$ts"
                    & git branch $backup HEAD 2>$null | Out-Null
                    Write-Log ("GIT push rejected; preserved $aheadCount commit(s) on $backup")
                    & git reset --hard origin/main 2>$null | Out-Null
                    Write-Log ("GIT reset to origin/main $originHead")
                }
            } else {
                # Behind only; just ff
                & git merge --ff-only origin/main 2>&1 | Out-Null
                Write-Log ("GIT ff'd $behindCount commit(s) from origin/main")
            }
        }
    } catch {
        Write-Log ("GIT reconcile failed: " + $_.Exception.Message)
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
            $cmdArgs = @(
                $queueAddPy,
                $queue,
                $name,
                $script,
                "--prereg", $prereg,
                "--timeout", $timeout
            )
            if ($skipSmoke) { $cmdArgs += "--skip-smoke" }

            $env:HDLAB_QUEUE_ADD_ON_REMOTE = "1"
            $out = & $pythonExe $cmdArgs 2>&1 | Out-String
            $exit = $LASTEXITCODE

            if ($exit -eq 0) {
                Write-Log ("OK {0}: queued {1}" -f $m.Name, $name)
                # git rm + commit + push so origin/main doesn't restore the manifest
                # on next reset (otherwise manifest re-processes every cycle)
                $relPath = "data/dispatch_requests/" + $m.Name
                & git rm $relPath 2>$null | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    & git commit -m ("dispatch-consumer: processed " + $m.Name) 2>$null | Out-Null
                    & git push origin "HEAD:main" 2>$null | Out-Null
                    Write-Log ("GIT rm + push for " + $m.Name)
                }
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
