# C7 Path D CPU Latency Profiling v1 at N=4096

## Anchor
path_d_cpu_latency_profiling_v1_n4096

## Queue
remote_cpu_queue

## Script
experiments/exp_path_d_cpu_latency_profiling_v1_n4096.py

## Scientific question
CPU baseline for Path D latency profiling. Composes with G12 (GPU memory
profiling). Validates profiling methodology on CPU. Is the dominant op
identified per M-point AND per-op CV <0.20 (clean baseline)?

## Pre-registered bands
- HARD_PASS: dominant op identified per M-point AND per-op CV < 0.20.
- HARD_FAIL: noise dominates (CV >= 0.50 across most measurements).
- MIDDLE_BAND: otherwise.

## Config
- N = 4096 (PROT-018 _n4096)
- M sweep [50, 100, 200, 500] (Pattern B operating points)
- depth = 5, K_paths = 100, N_STARTS = 16
- N_REPEAT = 10 per (M, seed) cell
- beta_D = 4.0
- Seeds: [7, 17, 23, 31, 41]

## Self-test
- Verdict gates HP/HF/MB exercised
- CV self-check
- Live CPU smoke at N=1024 M=50 with reduced n_repeat

## Timeout estimate
- smoke wall ~3s
- 5 seeds * 4 M-points * 10 repeats; Path D ~5s/call at full config
- scaling_exp = 1.0; estimate = ceil(1.5 * 3 * 4 * 5 * 4 * 10 / 3) ~ 1200s
- timeout_s = 14400 (user spec).

## Importance
HIGH - composition baseline for G12; CPU/GPU latency baseline for production
SLA pricing.
