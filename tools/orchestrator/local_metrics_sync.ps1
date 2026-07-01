# Hardened recurring metrics-sync puller (LAPTOP side).
# Pulls new data/<exp>/metrics.json + results.json + provenance.json + verdict.json + recent_verdicts.json
# from remote marsh@home -> local. Method B (tar-pipe; ~30MB compressed).
#
# Hardening (per USER autonomous-remote pattern):
#   - PID-and-age lock; max 1 instance
#   - SSH failures handled gracefully; just exit + retry next scheduled run
#   - Idempotent merge: existing local files PRESERVED; only new files copied
#   - Disk-space pre-check
#   - Log rotation at 1MB
#   - Coverage-gap alert: writes data/.coverage_gap flag if delta > 0 for N consecutive runs
#   - No retry budget cap (this is a RECURRING infra task, not one-shot)
#   - Bounded execution time per run (10min hard kill via task settings)
# ASCII only.

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

$repo = "D:/AI/hd-instrument"
$dataDir = Join-Path $repo "data"
$stateDir = Join-Path $dataDir ".metrics_sync"
$lockPath = Join-Path $stateDir ".lock"
$logPath = Join-Path $stateDir "sync.log"
$statusPath = Join-Path $stateDir "status.json"
$gapAlertPath = Join-Path $dataDir ".coverage_gap"
$stagingDir = Join-Path $repo "data_remote_pull_staging"
$tarballPath = Join-Path $repo "data_remote_pull.tar"
# Use the VERSION-CONTROLLED repo copy (reconciled to the remote via git), NOT a home-dir copy
# that drifts. The repo copy carries the 2026-06-19 25MB size-cap fix (the home copy lacked it ->
# 3.9GB tar -> SCP hang). Repo-tracked => future fixes propagate by commit+push, no remote-host write.
$remoteScript = "C:/dev/hd-instrument/tools/orchestrator/remote_metrics_tar.py"
$remoteTarball = "/users/marsh/metrics_pull.tar"

# Coverage gap alert threshold: N consecutive runs with delta > 0
$GAP_ALERT_RUNS = 3

if (-not (Test-Path $stateDir)) { New-Item -ItemType Directory -Path $stateDir -Force | Out-Null }

function Write-Log($msg) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    try {
        if ((Test-Path $logPath) -and ((Get-Item $logPath).Length -gt 1MB)) {
            Move-Item $logPath ($logPath + ".1") -Force -ErrorAction SilentlyContinue
        }
        Add-Content -Path $logPath -Value "[$ts] PID=$PID $msg" -Encoding ASCII -ErrorAction SilentlyContinue
    } catch {}
}

function Cleanup-Staging() {
    if (Test-Path $stagingDir) { Remove-Item $stagingDir -Recurse -Force -ErrorAction SilentlyContinue }
    if (Test-Path $tarballPath) { Remove-Item $tarballPath -Force -ErrorAction SilentlyContinue }
}

# Bounded-execution wrapper for SSH/SCP calls (2026-07-01 phantom-FULL fix).
# `-o ConnectTimeout=N` only bounds the TCP connect; once ssh is connected and
# the remote powershell hangs (auth-agent, ExecutionPolicy prompt, network
# drop mid-payload, etc.), ssh will wait indefinitely. Result: the scheduled
# task's ssh child persists as a SYSTEM-owned process the user cannot kill,
# and the .lock stays "held" until the age>=12min bypass kicks in. Meanwhile
# every sync-cycle firing produces a new hung ssh, and 10+ hours of remote
# metrics never sync back -> Director framings become phantom-FULL because
# local metrics.json is stale from an earlier smoke run.
#
# Fix: wrap ssh/scp in Start-Job + Wait-Job -Timeout. If the wall-timeout
# fires, Stop-Job forcibly kills the invocation chain. Returns @{ok, stdout, exit_code}.
function Invoke-BoundedSsh {
    param(
        [Parameter(Mandatory=$true)][string]$Command,
        [int]$TimeoutSeconds = 60,
        [string]$Label = "ssh"
    )
    $job = Start-Job -ScriptBlock {
        param($cmd)
        $out = & ssh -o ConnectTimeout=15 -o BatchMode=yes -o ServerAliveInterval=10 -o ServerAliveCountMax=3 marsh@home $cmd 2>&1
        @{ stdout = ($out | Out-String); exit_code = $LASTEXITCODE }
    } -ArgumentList $Command
    $finished = Wait-Job -Job $job -Timeout $TimeoutSeconds
    if (-not $finished) {
        Write-Log ("BOUNDED_SSH TIMEOUT label={0} timeout={1}s command={2}" -f $Label, $TimeoutSeconds, ($Command.Substring(0, [math]::Min(80, $Command.Length))))
        Stop-Job -Job $job -ErrorAction SilentlyContinue
        Remove-Job -Job $job -Force -ErrorAction SilentlyContinue
        return @{ ok = $false; stdout = ""; exit_code = -1; timed_out = $true }
    }
    $result = Receive-Job -Job $job
    Remove-Job -Job $job -Force -ErrorAction SilentlyContinue
    return @{ ok = ($result.exit_code -eq 0); stdout = $result.stdout; exit_code = $result.exit_code; timed_out = $false }
}

function Invoke-BoundedScp {
    param(
        [Parameter(Mandatory=$true)][string]$SourceSpec,
        [Parameter(Mandatory=$true)][string]$DestPath,
        [int]$TimeoutSeconds = 180,
        [string]$Label = "scp"
    )
    $job = Start-Job -ScriptBlock {
        param($src, $dst)
        $out = & scp -o ConnectTimeout=15 -o BatchMode=yes -o ServerAliveInterval=10 -o ServerAliveCountMax=3 $src $dst 2>&1
        @{ stdout = ($out | Out-String); exit_code = $LASTEXITCODE }
    } -ArgumentList $SourceSpec, $DestPath
    $finished = Wait-Job -Job $job -Timeout $TimeoutSeconds
    if (-not $finished) {
        Write-Log ("BOUNDED_SCP TIMEOUT label={0} timeout={1}s src={2}" -f $Label, $TimeoutSeconds, $SourceSpec)
        Stop-Job -Job $job -ErrorAction SilentlyContinue
        Remove-Job -Job $job -Force -ErrorAction SilentlyContinue
        return @{ ok = $false; stdout = ""; exit_code = -1; timed_out = $true }
    }
    $result = Receive-Job -Job $job
    Remove-Job -Job $job -Force -ErrorAction SilentlyContinue
    return @{ ok = ($result.exit_code -eq 0); stdout = $result.stdout; exit_code = $result.exit_code; timed_out = $false }
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

    # Disk space pre-check
    $drive = (Get-Item $repo).PSDrive
    $freeGB = [math]::Round($drive.Free / 1GB, 2)
    if ($freeGB -lt 5.0) {
        Write-Log ("DISK LOW free={0}GB exit" -f $freeGB)
        exit 0
    }

    Set-Location $repo

    # Step 1: ask remote to count its load-bearing files (cheap one-liner).
    # Bounded to 60s to survive remote-side hangs (2026-07-01 phantom-FULL fix;
    # was raw ssh, which hung 10+ hours holding the sync lock).
    $remoteCount = 0
    $countResult = Invoke-BoundedSsh -Command "powershell -NoProfile -Command `"(Get-ChildItem -Path 'C:/dev/hd-instrument/data' -Recurse -Filter metrics.json).Count`"" -TimeoutSeconds 60 -Label "count-probe"
    if ($countResult.ok -and $countResult.stdout) {
        [int]::TryParse($countResult.stdout.Trim(), [ref]$remoteCount) | Out-Null
    }
    if ($remoteCount -le 0) {
        if ($countResult.timed_out) { Write-Log "SSH count probe TIMED OUT (60s); will retry next run" }
        else { Write-Log "SSH count probe failed; will retry next run" }
        exit 0
    }

    # Step 2: count local
    $localCount = (Get-ChildItem -Path $dataDir -Recurse -Filter metrics.json -ErrorAction SilentlyContinue).Count
    Write-Log ("COUNT remote={0} local={1} delta={2}" -f $remoteCount, $localCount, ($remoteCount - $localCount))

    # Persistent gap-alert state
    $persistentGap = 0
    if (Test-Path $statusPath) {
        try {
            $prev = Get-Content $statusPath -Raw | ConvertFrom-Json
            if ($prev.persistent_gap_runs) { $persistentGap = [int]$prev.persistent_gap_runs }
        } catch {}
    }

    $delta = $remoteCount - $localCount
    # Gap-alert (preserved for the remote-has-more case; informational)
    if ($delta -gt 0) {
        $persistentGap += 1
        Write-Log ("GAP delta={0} persistent={1}/{2}" -f $delta, $persistentGap, $GAP_ALERT_RUNS)

        if ($persistentGap -ge $GAP_ALERT_RUNS) {
            $alertContent = @(
                "# COVERAGE GAP ALERT",
                "",
                ("Remote (marsh@home) has {0} metrics.json files; local has {1}; delta = {2}" -f $remoteCount, $localCount, $delta),
                ("Persistent gap detected over {0} consecutive sync runs." -f $persistentGap),
                "",
                "Sync attempted but did not close gap. Possible causes:",
                "- SSH transient drops preventing tarball transfer",
                "- Remote files inaccessible (permission / lock)",
                "- Disk space",
                "",
                ("Investigate via tools/orchestrator/local_metrics_sync.ps1 logs at " + $logPath)
            )
            Set-Content -Path $gapAlertPath -Value ($alertContent -join "`n") -Encoding ASCII
        }
    } else {
        Write-Log ("DELTA={0} (count-equal-or-local-more; pull runs anyway per file-set diff fix 2026-06-18)" -f $delta)
    }

    # ALWAYS run the pull pipeline (FIX 2026-06-18: Skunkworks AFFIRMED the
    # delta-gating was the corpus-completeness ROOT -- when local-old > remote-new,
    # delta went NEGATIVE and the tar pull silently skipped, so new remote results
    # never synced. The per-file merge step at ~line 187 already performs file-set
    # diff [if-exists-skip / else-copy], so unconditional pull is safe; the
    # LOAD_BEARING tarball filter keeps it ~30MB per cycle).
    # RE-ENABLED 2026-06-19 (Orchestrator): the MERGE was briefly disabled because the remote tar
    # BALLOONED to ~3.9GB (bge-index .npz caches + huge results.json, no size cap) -> the SCP hung
    # >10min -> task hard-kill -> the run DIED before the GIT PUSH (which is AFTER the merge) ->
    # origin fell 60+ behind. ROOT FIX: remote_metrics_tar.py now has a 25MB per-file cap (the
    # repo copy, pointed-to above) -> tar ~108MB -> SCP-able. Merge re-enabled. (Further hardening
    # TODO: ssh-runtime-timeout + push-before-merge so a future pull-hang can NEVER block the push.)
    if ($true) {
        # Step 3: trigger remote tar build (bounded 300s — remote tar takes ~60-120s typically)
        $tarResult = Invoke-BoundedSsh -Command "python $remoteScript" -TimeoutSeconds 300 -Label "tar-build"
        if (-not $tarResult.ok) {
            if ($tarResult.timed_out) { Write-Log "remote tar build TIMED OUT (300s); will retry next run" }
            else { Write-Log "remote tar build failed; will retry next run" }
            exit 0
        }

        # Step 4: SCP tarball back (bounded 300s — ~124MB / typical 10-30s over LAN)
        Cleanup-Staging
        $scpResult = Invoke-BoundedScp -SourceSpec ("marsh@home:" + $remoteTarball) -DestPath $tarballPath -TimeoutSeconds 300 -Label "tar-pull"
        if (-not $scpResult.ok -or -not (Test-Path $tarballPath)) {
            if ($scpResult.timed_out) { Write-Log "SCP tarball back TIMED OUT (300s); will retry next run" }
            else { Write-Log "SCP tarball back failed; will retry next run" }
            Cleanup-Staging
            exit 0
        }

        # Step 5: extract + merge
        New-Item -ItemType Directory -Path $stagingDir -Force | Out-Null
        try {
            & tar -xf $tarballPath -C $stagingDir 2>$null
        } catch {
            Write-Log ("tar extract threw: " + $_.Exception.Message)
            Cleanup-Staging
            exit 0
        }

        # MERGE: mtime-newer-wins (2026-06-30 fix — preserve-existing rule blocked fresh
        # remote metrics 2x today: 17:43 UTC Orchestrator "hallucination" + 18:33 UTC Cell C v2
        # sync miss. Skunkworks caught both via SCP side-pull. Root cause: this merge step
        # used `if (Test-Path $target) { skip }` which skipped any existing local file
        # without checking remote mtime. Fix: overwrite when remote is newer.
        $copied = 0
        $skipped = 0
        $overwritten = 0
        $stagingData = Join-Path $stagingDir "data"
        if (Test-Path $stagingData) {
            Get-ChildItem -Path $stagingData -Recurse -File | ForEach-Object {
                $relPath = $_.FullName.Substring($stagingData.Length).TrimStart('\','/')
                $target = Join-Path $dataDir $relPath
                if (Test-Path $target) {
                    $localItem = Get-Item $target
                    if ($_.LastWriteTimeUtc -gt $localItem.LastWriteTimeUtc) {
                        Copy-Item $_.FullName $target -Force
                        $overwritten += 1
                    } else {
                        $skipped += 1
                    }
                } else {
                    $targetDir = Split-Path $target -Parent
                    if (-not (Test-Path $targetDir)) { New-Item -ItemType Directory -Path $targetDir -Force | Out-Null }
                    Copy-Item $_.FullName $target -Force
                    $copied += 1
                }
            }
        }
        Write-Log ("MERGE copied={0} overwritten={1} skipped={2}" -f $copied, $overwritten, $skipped)
        Cleanup-Staging

        # Re-count after merge
        $localCountPost = (Get-ChildItem -Path $dataDir -Recurse -Filter metrics.json -ErrorAction SilentlyContinue).Count
        if ($localCountPost -ge $remoteCount) {
            $persistentGap = 0
            if (Test-Path $gapAlertPath) { Remove-Item $gapAlertPath -Force -ErrorAction SilentlyContinue }
            Write-Log ("GAP CLOSED local={0} remote={1}" -f $localCountPost, $remoteCount)
        } else {
            Write-Log ("GAP NOT CLOSED local={0} remote={1} delta={2}" -f $localCountPost, $remoteCount, ($remoteCount - $localCountPost))
        }
        $localCount = $localCountPost
    }
    # Note: persistentGap is reset inside the GAP CLOSED branch (line ~196 above)
    # when the local post-pull count >= remote count; the previous else-branch
    # (delta <= 0 -> skip pull + clear persistent) was the corpus-completeness
    # bug and is removed.

    # ===== GIT PUSH STEP (per USER directive via Skunkworks 15:19) =====
    # Off-machine backup; LAST step of cadence after sync.
    # Conditions (per Skunkworks): NON-INTERACTIVE + fail-fast + NEVER force +
    # measured-low-bandwidth + freshness-monitor + ordering-last + idempotent.
    $gitStatus = @{
        push_ran = $false
        push_ok = $null
        ahead_before = 0
        ahead_after = $null
        pack_bytes = $null
        error = $null
    }
    $backupAlertPath = Join-Path $dataDir ".backup_stale_alert"
    $persistentPushFail = 0
    if (Test-Path $statusPath) {
        try {
            $prev = Get-Content $statusPath -Raw | ConvertFrom-Json
            if ($prev.persistent_push_fail_runs) { $persistentPushFail = [int]$prev.persistent_push_fail_runs }
        } catch {}
    }

    try {
        Set-Location $repo
        $env:GIT_TERMINAL_PROMPT = "0"

        # Auto-stage notes/ (per Skunkworks 18:29 ratify: closes durability gap
        # for untracked-notes-not-on-git; staging restricted to notes/ scope to
        # avoid accidental data/ or other subtree commits per Skunkworks cert-
        # conditions; never force; clear commit message)
        $untrackedNotes = & git ls-files notes/ --others --exclude-standard 2>$null | Where-Object { $_ }
        $modifiedNotes = & git diff --name-only -- notes/ 2>$null | Where-Object { $_ }
        if ($untrackedNotes -or $modifiedNotes) {
            & git add notes/ 2>$null | Out-Null
            $staged = & git diff --cached --name-only -- notes/ 2>$null | Where-Object { $_ }
            if ($staged) {
                $stagedCount = ($staged | Measure-Object).Count
                & git commit -m ("hd_metrics_sync auto-stage: {0} notes/" -f $stagedCount) 2>$null | Out-Null
                Write-Log ("GIT auto-staged {0} notes" -f $stagedCount)
            }
        }

        & git fetch origin main 2>$null | Out-Null
        # PULL-BEFORE-PUSH (staleness-sweep root fix 2026-06-19): integrate origin/main BEFORE pushing.
        # Was push-only -> when behind origin (e.g. remote-consumer commits) the push rejects non-ff and the
        # laptop/origin divergence accumulates SILENTLY. Rebase local onto origin first; abort-on-conflict (never
        # auto-resolve atoms.jsonl) and flag for a manual reconcile.
        $behind = & git rev-list --count HEAD..origin/main 2>$null
        if ($behind -and [int]$behind -gt 0) {
            Write-Log ("GIT behind origin by {0}; rebasing (pull-before-push) before push" -f $behind)
            & git rebase origin/main 2>&1 | Out-Null
            if ($LASTEXITCODE -ne 0) {
                & git rebase --abort 2>$null | Out-Null
                Write-Log "GIT REBASE CONFLICT -> aborted; manual reconcile needed (push skipped this cycle)"
                $gitStatus.rebase_conflict = $true
            } else {
                Write-Log ("GIT rebased onto origin/main (was behind {0}); now fast-forwardable" -f $behind)
            }
        }
        $aheadBefore = & git rev-list --count origin/main..HEAD 2>$null
        if ($aheadBefore) { $gitStatus.ahead_before = [int]$aheadBefore } else { $gitStatus.ahead_before = 0 }
        Write-Log ("GIT ahead_before={0}" -f $gitStatus.ahead_before)

        if ($gitStatus.ahead_before -eq 0) {
            Write-Log "GIT no commits to push; skip"
        } else {
            # Measure pack size (warn if > 50 MB)
            $packBytes = 0
            try {
                $packOut = & git rev-list --objects origin/main..HEAD 2>$null | git pack-objects --stdout 2>$null | Out-String
                if ($packOut) { $packBytes = $packOut.Length }
            } catch {}
            $gitStatus.pack_bytes = $packBytes
            if ($packBytes -gt 52428800) {
                Write-Log ("GIT LARGE PACK {0} bytes (>50MB); pushing anyway + flagging" -f $packBytes)
            }

            # PRE-PUSH STORE-LOAD GATE (incident 2026-06-19 prevention): NEVER push an unloadable Store
            # to origin. The concept-partition NULL-corruption reached origin+remote via push before this
            # gate existed. Only gate when the push actually includes data/substrate_index changes (the
            # risky case); notes-only pushes skip it (no cost, no transient-fail). Fail-CLOSED (skip push)
            # if PartitionedStore().all_atoms() throws; fail-OPEN if the .venv python is unavailable.
            $storeLoadOk = $true
            $storeChanged = & git diff --name-only origin/main..HEAD -- data/substrate_index/ 2>$null | Where-Object { $_ }
            if ($storeChanged) {
                $venvPy = Join-Path $repo ".venv/Scripts/python.exe"
                if (Test-Path $venvPy) {
                    $gateCode = "import sys; r=r'$repo'; sys.path.insert(0,r); from backend.substrate_index.partition import PartitionedStore; sum(1 for _ in PartitionedStore(r+'/data/substrate_index').all_atoms()); print('STORE_LOAD_OK')"
                    $gateOut = & $venvPy -c $gateCode 2>&1 | Out-String
                    if ($gateOut -notmatch 'STORE_LOAD_OK') { $storeLoadOk = $false; $gitStatus.store_load_error = $gateOut.Trim() }
                } else {
                    Write-Log "STORE-LOAD GATE: .venv python not found; gate skipped (fail-open, notes-safe)"
                }
            }

            # Fast-forward push only (NEVER force) -- gated by the Store-LOAD check above
            $gitStatus.push_ran = $true
            if (-not $storeLoadOk) {
                $gitStatus.push_ran = $false
                $gitStatus.store_load_gate_failed = $true
                Write-Log "!! STORE-LOAD GATE FAILED: push includes data/substrate_index changes that do NOT load (PartitionedStore threw) -> PUSH SKIPPED this cycle; a corrupt/unloadable Store will NOT propagate to origin. Manual investigation needed (see store_load_error in status)."
            } else {
                $pushOut = & git push origin "HEAD:main" 2>&1
                if ($LASTEXITCODE -eq 0) {
                    $gitStatus.push_ok = $true
                    $aheadAfter = & git rev-list --count origin/main..HEAD 2>$null
                    if ($aheadAfter) { $gitStatus.ahead_after = [int]$aheadAfter } else { $gitStatus.ahead_after = 0 }
                    Write-Log ("GIT PUSH OK ahead_after={0}" -f $gitStatus.ahead_after)
                    $persistentPushFail = 0
                    if (Test-Path $backupAlertPath) { Remove-Item $backupAlertPath -Force -ErrorAction SilentlyContinue }
                } else {
                    $gitStatus.push_ok = $false
                    $gitStatus.error = ($pushOut | Out-String).Trim()
                    Write-Log ("GIT PUSH FAIL: " + $gitStatus.error.Substring(0, [math]::Min(200, $gitStatus.error.Length)))
                    $persistentPushFail += 1
                    # On non-ff rejection: do NOT --force; log + flag
                    if ($gitStatus.error -match "non-fast-forward|rejected") {
                        Write-Log "GIT NON-FF rejection; not forcing; alert raised"
                    }
                }
            }
        }
    } catch {
        $gitStatus.error = $_.Exception.Message
        Write-Log ("GIT step threw: " + $gitStatus.error)
        $persistentPushFail += 1
    }

    # Backup-stale alert if persistent failure or sustained ahead-count
    if ($persistentPushFail -ge 3 -or ($gitStatus.ahead_after -gt 5 -and $persistentPushFail -gt 0)) {
        $alertLines = @(
            "# BACKUP STALE ALERT",
            "",
            ("Push failures: {0} consecutive runs" -f $persistentPushFail),
            ("Last error: {0}" -f $gitStatus.error),
            ("Ahead after last push attempt: {0}" -f $gitStatus.ahead_after),
            "",
            "GitHub off-machine backup not staying current.",
            ("See sync.log: " + $logPath)
        )
        Set-Content -Path $backupAlertPath -Value ($alertLines -join "`n") -Encoding ASCII
    }

    # Write status
    $status = @{
        last_run_utc = (Get-Date).ToUniversalTime().ToString("o")
        remote_count = $remoteCount
        local_count = $localCount
        delta = $remoteCount - $localCount
        persistent_gap_runs = $persistentGap
        last_push_utc = if ($gitStatus.push_ran) { (Get-Date).ToUniversalTime().ToString("o") } else { $null }
        git_push_ok = $gitStatus.push_ok
        commits_pushed = $gitStatus.ahead_before
        ahead_after = $gitStatus.ahead_after
        pack_bytes = $gitStatus.pack_bytes
        persistent_push_fail_runs = $persistentPushFail
    } | ConvertTo-Json
    Set-Content -Path $statusPath -Value $status -Encoding ASCII

    Write-Log "RUN END"
} finally {
    if (Test-Path $lockPath) { Remove-Item $lockPath -Force -ErrorAction SilentlyContinue }
}
