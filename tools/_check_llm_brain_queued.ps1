$ErrorActionPreference = 'Stop'
Set-Location C:\dev\hd-instrument
$pat = 'charlm|_lm_|8channel|curriculum|_icl_|tier[0-9]|trained_mini|orchestrat|spectral_training|spectral_monitor|spectral_cumulant|anti_hebb|contrastive|counterfactual_rpe|data_attribution|multi_layer_observer|hebbian|krotov|climbing_fiber|dendritic|preloaded|pfc_attractor|deltanet|mini_lm'
$queues = @('overnight_queue','remote_cpu_queue')
foreach ($q in $queues) {
    $f = "data\$q\queue.json"
    $e = (Get-Content $f -Raw | ConvertFrom-Json).experiments
    $m = @($e | Where-Object { $_.name -match $pat })
    Write-Output "==== $q : $($m.Count) matches ===="
    $m | Sort-Object name | ForEach-Object { Write-Output ("  [" + $_.status + "] " + $_.name) }
}
