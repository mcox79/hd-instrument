# Idempotent + HARDENED language-pack downloader.
# Designed for autonomous scheduled-task execution; bounded retry budget;
# strong concurrent-run protection; self-cleanup on permanent failure.
#
# Failure modes hardened against:
#   - permanent URL failure (max 5 total run attempts; write FINAL_FAILURE; self-unregister)
#   - concurrent task instances (PID-and-age lock; max 1 running instance)
#   - disk space exhaustion (pre-check 2GB free)
#   - partial download (size threshold + cleanup)
#   - lock-file orphan (PID-dead detection + age clear)
#   - log file growth (rotate at 1MB)
#   - per-attempt hang (TimeoutSec 600 = 10 min)
#   - successful download but unregister fails (FINAL marker; idempotent)
#   - rate-limit by download host (jittered backoff)
# ASCII only.

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

$dir = "C:/dev/hd-instrument/data/language_packs"
$logPath = Join-Path $dir "download.log"
$lockPath = Join-Path $dir ".download.lock"
$attemptCounterPath = Join-Path $dir ".attempt_count"
$provPath = Join-Path $dir "PROVENANCE.md"
$finalFailurePath = Join-Path $dir "FINAL_FAILURE.md"
$taskName = "hd_lang_pack_download"
$MAX_TOTAL_RUNS = 5  # bounded retry budget across scheduled-task lifetime

if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
Set-Location $dir

function Write-Log($msg) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    try {
        # Log rotation: keep file under 1 MB
        if ((Test-Path $logPath) -and ((Get-Item $logPath).Length -gt 1MB)) {
            $rotated = $logPath + ".1"
            Move-Item $logPath $rotated -Force -ErrorAction SilentlyContinue
        }
        Add-Content -Path $logPath -Value "[$ts] PID=$PID $msg" -Encoding ASCII -ErrorAction SilentlyContinue
    } catch {}
}

function Try-Unregister-Self() {
    try {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
        Write-Log ("self-unregistered scheduled task: " + $taskName)
    } catch {
        Write-Log ("unregister attempt: " + $_.Exception.Message)
    }
}

# Early exit: already done (PROVENANCE present + no-op)
if (Test-Path $provPath) {
    Write-Log "PROVENANCE exists; previous success; unregister + exit"
    Try-Unregister-Self
    exit 0
}

# Early exit: previous final failure
if (Test-Path $finalFailurePath) {
    Write-Log "FINAL_FAILURE present from prior run; unregister + exit"
    Try-Unregister-Self
    exit 0
}

# STRONG LOCK: PID + age check
if (Test-Path $lockPath) {
    $lockContent = Get-Content $lockPath -Raw -ErrorAction SilentlyContinue
    $lockAge = ((Get-Date) - (Get-Item $lockPath).LastWriteTime).TotalMinutes
    $lockPid = 0
    if ($lockContent) {
        $parts = $lockContent.Trim().Split(":")
        if ($parts.Length -gt 0) { [int]::TryParse($parts[0], [ref]$lockPid) | Out-Null }
    }
    $still_running = $false
    if ($lockPid -gt 0) {
        $proc = Get-Process -Id $lockPid -ErrorAction SilentlyContinue
        if ($proc) { $still_running = $true }
    }
    if ($still_running -and $lockAge -lt 20) {
        Write-Log ("LOCKED by PID={0} age={1:N1}min; exit (concurrent run protection)" -f $lockPid, $lockAge)
        exit 0
    }
    Write-Log ("STALE lock PID={0} age={1:N1}min still_running={2}; clearing" -f $lockPid, $lockAge, $still_running)
    Remove-Item $lockPath -Force -ErrorAction SilentlyContinue
}

# BOUNDED RETRY BUDGET (across scheduled-task lifetime)
$attemptCount = 0
if (Test-Path $attemptCounterPath) {
    $rawCount = Get-Content $attemptCounterPath -Raw -ErrorAction SilentlyContinue
    if ($rawCount) { [int]::TryParse($rawCount.Trim(), [ref]$attemptCount) | Out-Null }
}
$attemptCount++
Set-Content -Path $attemptCounterPath -Value $attemptCount -Encoding ASCII

if ($attemptCount -gt $MAX_TOTAL_RUNS) {
    Write-Log ("BUDGET EXHAUSTED attempt={0} > MAX={1}; writing FINAL_FAILURE + self-unregister" -f $attemptCount, $MAX_TOTAL_RUNS)
    $ff_lines = @(
        "# Language-pack download FINAL_FAILURE",
        "",
        ("After {0} scheduled-task runs, not all initial packs landed." -f $MAX_TOTAL_RUNS),
        "See download.log for per-attempt details.",
        "Orchestrator (Custodian) should inspect manually + decide next action.",
        ""
    )
    Set-Content -Path $finalFailurePath -Value ($ff_lines -join "`n") -Encoding ASCII
    Try-Unregister-Self
    exit 0
}

Write-Log ("RUN START attempt={0}/{1}" -f $attemptCount, $MAX_TOTAL_RUNS)

# Acquire lock with PID
Set-Content -Path $lockPath -Value ("{0}:{1}" -f $PID, (Get-Date).ToString("o")) -ErrorAction SilentlyContinue

try {
    # Disk-space check (need at least 2 GB free for safety incl. future ConceptNet)
    $drive = (Get-Item $dir).PSDrive
    $free_gb = [math]::Round($drive.Free / 1GB, 2)
    if ($free_gb -lt 2.0) {
        Write-Log ("DISK LOW free={0}GB; exit (will retry next scheduled run)" -f $free_gb)
        exit 0
    }

    $packs = @(
        @{name="wn3.1.dict.tar.gz"; url="https://wordnetcode.princeton.edu/wn3.1.dict.tar.gz"; min_mb=10},
        @{name="text8.zip";          url="https://mattmahoney.net/dc/text8.zip";              min_mb=30},
        @{name="enwik8.zip";         url="https://mattmahoney.net/dc/enwik8.zip";             min_mb=30}
    )

    foreach ($p in $packs) {
        if (Test-Path $p.name) {
            $sz = (Get-Item $p.name).Length
            if ($sz -gt ($p.min_mb * 1MB)) {
                Write-Log ("SKIP {0} present {1} bytes" -f $p.name, $sz)
                continue
            }
            Write-Log ("REMOVE partial {0} {1} bytes" -f $p.name, $sz)
            Remove-Item $p.name -Force -ErrorAction SilentlyContinue
        }

        $success = $false
        # 3 attempts per pack per run; with bounded retry budget, max total = 5 runs * 3 attempts = 15 attempts
        for ($attempt = 1; $attempt -le 3 -and -not $success; $attempt++) {
            Write-Log ("DOWNLOAD {0} attempt {1}/3 (run {2}/{3})" -f $p.name, $attempt, $attemptCount, $MAX_TOTAL_RUNS)
            try {
                Invoke-WebRequest -Uri $p.url -OutFile $p.name -UseBasicParsing -TimeoutSec 600
                if (Test-Path $p.name) {
                    $sz = (Get-Item $p.name).Length
                    if ($sz -gt ($p.min_mb * 1MB)) {
                        Write-Log ("OK {0} {1} bytes" -f $p.name, $sz)
                        $success = $true
                    } else {
                        Write-Log ("UNDERSIZED {0} {1} bytes; remove + retry" -f $p.name, $sz)
                        Remove-Item $p.name -Force -ErrorAction SilentlyContinue
                    }
                }
            } catch {
                Write-Log ("FAIL {0} attempt {1}: {2}" -f $p.name, $attempt, $_.Exception.Message)
                if (Test-Path $p.name) { Remove-Item $p.name -Force -ErrorAction SilentlyContinue }
            }
            if (-not $success -and $attempt -lt 3) {
                $jitter = Get-Random -Minimum 5 -Maximum 30
                $backoff = (30 * $attempt) + $jitter
                Write-Log ("BACKOFF {0}s (jitter included) before next attempt" -f $backoff)
                Start-Sleep -Seconds $backoff
            }
        }
        if (-not $success) {
            Write-Log ("GIVEUP {0} after 3 attempts; will retry next scheduled run" -f $p.name)
        }
    }

    # Verify all packs present + size adequate
    $all_present = $true
    foreach ($p in $packs) {
        if (-not (Test-Path $p.name)) { $all_present = $false; continue }
        $sz = (Get-Item $p.name).Length
        if ($sz -le ($p.min_mb * 1MB)) { $all_present = $false }
    }

    if ($all_present) {
        Write-Log "ALL INITIAL PACKS PRESENT; writing PROVENANCE.md"
        $prov_lines = @(
            "# Language packs PROVENANCE",
            "",
            "Downloaded by Orchestrator (Custodian) per DECISION GO 2026-06-17",
            "(notes/research_to_orch_LANGUAGE_PACKS_GO_initial_3_2026-06-17.md).",
            "Trust tier: T2 EXTERNAL REFERENCE (per Skunkworks ruling); not T0-proven.",
            ""
        )
        foreach ($p in $packs) {
            $f = Get-Item $p.name
            $mb = [math]::Round($f.Length / 1MB, 2)
            $prov_lines += ""
            $prov_lines += ("## " + $p.name)
            $prov_lines += ("- URL: " + $p.url)
            $prov_lines += ("- Size: " + $f.Length + " bytes (" + $mb + " MB)")
            $prov_lines += ("- Downloaded: " + $f.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss"))
        }
        Set-Content -Path $provPath -Value ($prov_lines -join "`n") -Encoding ASCII
        Write-Log ("PROVENANCE.md written; " + $packs.Length + " packs catalogued")
        Try-Unregister-Self
    } else {
        Write-Log "NOT ALL PACKS PRESENT; scheduled task will retry"
    }

    Write-Log "RUN END"
} finally {
    if (Test-Path $lockPath) { Remove-Item $lockPath -Force -ErrorAction SilentlyContinue }
}
