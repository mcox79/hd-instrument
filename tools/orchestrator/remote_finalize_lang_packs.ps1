# One-shot manual finalize: verify the 3 packs are valid + write PROVENANCE.md.
# Run once on remote after the hd_lang_pack_download self-unregistered with
# FINAL_FAILURE due to an over-aggressive min_mb threshold (false negative).
# ASCII only.

$ErrorActionPreference = "Continue"
$dir = "C:/dev/hd-instrument/data/language_packs"
Set-Location $dir

$packs = @(
    @{name="wn3.1.dict.tar.gz"; url="https://wordnetcode.princeton.edu/wn3.1.dict.tar.gz"; min_bytes=10000000},   # ~10 MB
    @{name="text8.zip";          url="https://mattmahoney.net/dc/text8.zip";              min_bytes=30000000},   # ~28.6 MB
    @{name="enwik8.zip";         url="https://mattmahoney.net/dc/enwik8.zip";             min_bytes=30000000}    # ~28.6 MB
)

$ok = $true
foreach ($p in $packs) {
    if (-not (Test-Path $p.name)) {
        Write-Output ("MISSING " + $p.name)
        $ok = $false
        continue
    }
    $sz = (Get-Item $p.name).Length
    if ($sz -lt $p.min_bytes) {
        Write-Output ("UNDERSIZED " + $p.name + " " + $sz + " bytes")
        $ok = $false
    } else {
        Write-Output ("OK " + $p.name + " " + $sz + " bytes")
    }
}

if (-not $ok) {
    Write-Output "NOT ALL PACKS VALID; do not write PROVENANCE"
    exit 1
}

# Clean up FINAL_FAILURE artifacts from over-aggressive threshold
if (Test-Path "FINAL_FAILURE.md") { Remove-Item "FINAL_FAILURE.md" -Force }
if (Test-Path ".attempt_count")   { Remove-Item ".attempt_count" -Force }

# Write PROVENANCE.md
$prov_lines = @(
    "# Language packs PROVENANCE",
    "",
    "Downloaded by Orchestrator (Custodian) per DECISION GO 2026-06-17",
    "(notes/research_to_orch_LANGUAGE_PACKS_GO_initial_3_2026-06-17.md).",
    "Trust tier: T2 EXTERNAL REFERENCE (per Skunkworks ruling); not T0-proven.",
    "",
    "Manually finalized after hd_lang_pack_download false-alarm self-unregister",
    "(over-aggressive min_mb threshold deleted valid completed files).",
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
Set-Content -Path "PROVENANCE.md" -Value ($prov_lines -join "`n") -Encoding ASCII
Write-Output "PROVENANCE.md written"
