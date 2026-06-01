# Pre-registration: tcft_fresh_erase_v4

**Date**: 2026-05-27
**Anchor**: tcft_fresh_erase_v4
**Script**: experiments/exp_tcft_fresh_erase_v4.py
**Queue**: remote_cpu_queue
**Parent**: tcft_fresh_erase_v3 (MIDDLE_BAND; smoke only ran at N=512 1 seed)

## Hypothesis

TCFT variance reduction (var_ratio < 0.10) confirmed at N=4096 in >= 3/5 seeds.

## Pre-registered bands

- HARD-PASS: var_ratio < 0.10 in >= 3/5 seeds at N=4096
- HARD-FAIL: var_ratio >= 1.0 in ALL 5 seeds
- MIDDLE-BAND: 1-2/5 seeds only, or [0.10, 1.0) in all 5

Calibration probe: no prior N=4096 empirical anchor. Bands widened +-50%.

## Timeout estimate

smoke_wall_s = 0.12s, smoke_N = 512, FULL_N = 4096, FULL_seeds = 5, scaling_exp = 1.5.
Note: smoke elapsed includes fixed overhead. Use analog: v2 N=1024 5 seeds ~120s.
timeout_s = ceil(1.5 * 120 * (4096/1024)^1.5 * (5/5)) = ceil(1.5 * 120 * 8) = 1440 -> 2700s.
