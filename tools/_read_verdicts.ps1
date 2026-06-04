$ErrorActionPreference = 'SilentlyContinue'
Set-Location C:\dev\hd-instrument
$names = @(
  'q_a3_l400_cross_layer_composition_v1_n16384',
  'q_a3_l500_cross_layer_composition_v1_n16384',
  'q_a3_l700_cross_layer_composition_v1_n16384',
  'q_a3_l1000_cross_layer_composition_v1_n16384',
  'q_a3_l1500_cross_layer_composition_v1_n16384',
  'q_a3_l2000_cross_layer_composition_v1_n16384',
  'q_a3_l200_cross_layer_composition_v1_n8192',
  'q_a3_l300_cross_layer_composition_v1_n8192',
  'q_a3_l500_cross_layer_composition_v1_n8192',
  'q_a3_l1000_cross_layer_composition_v1_n8192',
  'pp58_scs_d_sweep_tau_actual_v1_n8192',
  'pp58_scs_d_sweep_tau050_calibrated_v1_n8192',
  'pp58_scs_tau_actual_d8_v1_n8192',
  'nhse_annulus_tau_sweep_gamma_v1_n8192'
)
foreach ($n in $names) {
  $f = "data\exp_$n\metrics.json"
  if (Test-Path $f) {
    $m = Get-Content $f -Raw | ConvertFrom-Json
    $msg = "$($m.verdict)"
    Write-Output "$n => $msg"
  } else {
    Write-Output "$n => NO_METRICS"
  }
}
Write-Output "---QUEUES---"
foreach ($q in @('overnight_queue','remote_cpu_queue')) {
  $e = (Get-Content "data\$q\queue.json" -Raw | ConvertFrom-Json).experiments
  $p = @($e | Where-Object { $_.status -eq 'pending' }).Count
  $r = @($e | Where-Object { $_.status -eq 'running' }).Count
  Write-Output "$q pending=$p running=$r"
}
