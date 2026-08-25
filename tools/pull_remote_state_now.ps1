# Manual one-call pull of remote_state_cache.json from marsh@home -> local.
# Mirrors heartbeat_watchdog.pull_remote_state_cache but runs synchronously and
# VALIDATES that the pulled payload is fresh + real before replacing the local file.
# Use when the heartbeat_watchdog daemon is dead and the observability cache
# (queue / runner / GPU / verdict state read by tools/inflight_monitor.py) has
# gone stale. Read-only on the remote side; only writes the local cache file.
# ASCII only.
$ErrorActionPreference = "Continue"
$repo = "C:/AI/hd-instrument"
$dst  = Join-Path $repo "data/remote_state_cache.json"
$tmp  = "$dst.pull.tmp"
$src  = "marsh@home:C:/dev/hd-instrument/data/remote_state_cache.json"

# scp -O legacy mode (popup-fix; avoids remote SFTP-subsystem conhost).
& scp -O -o ConnectTimeout=8 -o BatchMode=yes -o StrictHostKeyChecking=no $src $tmp 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $tmp)) {
    Write-Host "PULL FAILED (scp exit=$LASTEXITCODE); local cache unchanged"
    if (Test-Path $tmp) { Remove-Item $tmp -Force }
    exit 1
}

# Validate: parseable JSON with a snapshot_ts fresher than 5 min.
$py = Join-Path $repo ".venv/Scripts/python.exe"
$check = & $py -c @"
import json,sys,datetime
d=json.load(open(r'$tmp',encoding='utf-8'))
ts=d.get('snapshot_ts_utc') or d.get('snapshot_ts')
dt=datetime.datetime.fromisoformat(str(ts).replace('Z','+00:00'))
if dt.tzinfo is None: dt=dt.replace(tzinfo=datetime.timezone.utc)
age=(datetime.datetime.now(datetime.timezone.utc)-dt).total_seconds()
print('%s|%.0f' % (ts, age))
sys.exit(0 if age <= 300 else 2)
"@
$rc = $LASTEXITCODE
if ($rc -ne 0) {
    Write-Host "PULL REJECTED: payload not fresh/valid ($check); local cache unchanged"
    Remove-Item $tmp -Force
    exit 1
}
Move-Item $tmp $dst -Force
Write-Host "PULL OK: snapshot_ts|age_s = $check -> data/remote_state_cache.json refreshed"
exit 0
