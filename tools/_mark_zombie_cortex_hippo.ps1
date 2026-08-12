$qfile = 'C:/dev/hd-instrument/data/remote_cpu_queue/queue.json'
$j = Get-Content $qfile -Raw | ConvertFrom-Json
foreach ($e in $j.experiments) {
  if ($e.name -eq 'cortex_hippo_handoff_FULL_seed_7' -and $e.status -eq 'running') {
    $e.status = 'orphaned_timeout'
    $e | Add-Member -NotePropertyName ended_at -NotePropertyValue ((Get-Date -Format 'yyyy-MM-ddTHH:mm:ss')) -Force
    $e | Add-Member -NotePropertyName zombie_reason -NotePropertyValue 'past 9000s timeout deadline by 1h45m; marked by orchestrator 2026-06-28T16:33Z' -Force
    Write-Output ('MARKED: ' + $e.name)
  }
}
$out = $j | ConvertTo-Json -Depth 50
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($qfile, $out, $utf8NoBom)
Write-Output 'WROTE'
