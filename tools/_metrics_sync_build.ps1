# Skunkworks remote sync build (runs ON marsh@home). Copies all data/*/metrics.json into a
# clean staging tree preserving <exp>/metrics.json, then tars it. I/O only; no compute.
$ErrorActionPreference = 'Stop'
$src   = 'C:\dev\hd-instrument\data'
$stage = 'C:\dev\hd-instrument\_metrics_sync_stage'
$tar   = 'C:\dev\hd-instrument\_metrics_sync.tar'
if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Force -Path $stage | Out-Null
$files = Get-ChildItem $src -Recurse -Filter metrics.json -ErrorAction SilentlyContinue
foreach ($f in $files) {
    $rel = $f.FullName.Substring($src.Length + 1)
    $dst = Join-Path $stage $rel
    New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
    Copy-Item -LiteralPath $f.FullName -Destination $dst -Force
}
if (Test-Path $tar) { Remove-Item $tar -Force }
tar -cf $tar -C $stage .
$mb = (Get-Item $tar).Length / 1MB
"STAGED {0} metrics.json files; tar {1:N2} MB at {2}" -f $files.Count, $mb, $tar
