$qpath = "C:/dev/hd-instrument/data/overnight_queue/queue.json"
$tmppath = "C:/dev/hd-instrument/data/overnight_queue/queue.json.tmp"

$raw = Get-Content $qpath -Raw -Encoding UTF8
$q = ConvertFrom-Json $raw

$updates = @{
    "axis3_triplepoint_v2_n4096"   = 7200
    "t3_susceptibility_v1_n4096"   = 21600
    "c1_kf_battery_phase_v1_n4096" = 86400
    "m1_boundary_fine_v1_n4096"    = 28800
    "c3_tcft_phase_v1_n4096"       = 86400
}

$changed = 0
for ($i = 0; $i -lt $q.experiments.Count; $i++) {
    $name = $q.experiments[$i].name
    if ($updates.ContainsKey($name)) {
        $old = $q.experiments[$i].timeout_s
        $q.experiments[$i].timeout_s = $updates[$name]
        Write-Host "UPDATED: $name  old=$old  new=$($updates[$name])"
        $changed++
    }
}

if ($changed -eq 0) {
    Write-Host "WARN: no matching entries found - check names"
    exit 1
}

$out = ConvertTo-Json $q -Depth 20
[System.IO.File]::WriteAllText($tmppath, $out, [System.Text.Encoding]::UTF8)
Move-Item -Force $tmppath $qpath
Write-Host "ATOMIC_WRITE_COMPLETE: $changed entries updated"

$q2 = Get-Content $qpath -Raw | ConvertFrom-Json
foreach ($e in $q2.experiments) {
    if ($updates.ContainsKey($e.name)) {
        Write-Host "VERIFY: $($e.name) status=$($e.status) timeout_s=$($e.timeout_s)"
    }
}
