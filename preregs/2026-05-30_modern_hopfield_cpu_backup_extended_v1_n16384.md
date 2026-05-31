# C1 Modern Hopfield CPU Backup Extended v1 at N=16384

## Anchor
modern_hopfield_cpu_backup_extended_v1_n16384

## Queue
remote_cpu_queue

## Script
experiments/exp_modern_hopfield_cpu_backup_extended_v1_n16384.py

## Scientific question
T3 confirmed max_M >= N at N=16384 CPU but the sweep stopped at M=N. C1
extends to 2N, 4N on CPU as insurance + ceiling-identification.

## Pre-registered bands
- HARD_PASS: max_M_at_95_recall >= 2N (= 32768) on >= 2/3 seeds.
- HARD_FAIL: max_M_at_95_recall = N on >= 2/3 seeds.
- MIDDLE_BAND: otherwise.

## Config
- N = 16384 (PROT-018 _n16384)
- M sweep [N, 2N, 4N] = [16384, 32768, 65536]
- Codebook: BSC, C = max(M_sweep) = 65536
- Seeds: [7, 17, 23]
- N_PROBE = 100 per M-cell
- RECALL_THRESHOLD = 0.95

## OOM check
- W = 16384*16384 float32 = 1 GiB on CPU (RAM)
- Codebook 65536 x 16384 float32 = 4 GiB
- Sim (65536 x 100) float32 = 25 MiB
- Peak ~6 GiB on CPU (RAM). Remote desktop has 16+ GiB.

## Self-test
- N_FULL == 16384
- M_SWEEP_FULL == [16384, 32768, 65536]
- Verdict gates exercised
- Live CPU smoke at N=1024 with M_SWEEP_SMOKE = [512, 1024]

## Timeout estimate
- smoke wall ~5s
- 3 seeds * 3 M-cells; max M = 4N = 65536; CPU matrix work at this size is slow
- scaling_exp = 2.0; estimate = ceil(1.5 * 5 * 16^2 * 3) = 5760s
- timeout_s = 86400 (24h budget per user spec; CPU patient construction).

## Importance
HIGH - extends T3 cap_map row; CPU insurance for G5/G6.
