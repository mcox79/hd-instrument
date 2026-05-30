# Prereg: gpu_acceleration_baseline_v1_n8192

Date: 2026-05-30
Anchor: gpu_acceleration_baseline_v1_n8192
Script: experiments/exp_gpu_acceleration_baseline_v1_n8192.py
N-suffix: _n8192 -> production-max N = 8192 (PROT-018)

## Question

Per (N in [2048, 4096, 8192], op in [store, query, edit, delete],
batch_size in [1, 16, 64, 256]): per-op wall-ns on GPU (`torch.cuda`) vs
CPU (`torch.cpu`). All 6 KF metrics on each device.

## Pre-registered bands

- **HARD_PASS**: mean query speedup at N=8192 >= 10x AND kf_max_delta <= 5%
  across all non-latency metrics (latency is the WHOLE point of the test, so
  excluded from the delta gate).
- **HARD_FAIL**: mean query speedup at N=8192 <= 2x OR kf_max_delta >= 10%
  (i.e., killer feature breaks on GPU).
- **MIDDLE_BAND**: otherwise.

## Sweep

3 N values * 5 seeds * 2 devices (CPU + GPU on runner). For each (N, seed,
device): store + query + edit + delete + 4 batch-size throughputs + 6-metric
battery.

## Timeout estimate

User specified 14400s. scaling_exp=1.5.

## Note

This anchor does NOT modify substrate code; it benchmarks the existing
`make_substrate` + `run_battery` pathways on the two devices.
