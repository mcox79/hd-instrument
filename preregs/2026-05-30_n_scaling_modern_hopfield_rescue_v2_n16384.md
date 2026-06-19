# Prereg: n_scaling_modern_hopfield_rescue_v2_n16384

Date: 2026-05-30
Anchor: n_scaling_modern_hopfield_rescue_v2_n16384
Script: experiments/exp_n_scaling_modern_hopfield_rescue_v2_n16384.py
N-suffix: _n16384 -> production N = 16384 (PROT-018 binding)

## Question

v1 ran 116s and produced no completed seeds (instrumentation failure per
cap_map v283). Likely OOM at large M values. v2 REDUCES the M sweep
(drops 4N, 8N, 16N), uses 3 seeds with per-cell graceful failure, and
adds explicit memory logging.

At N=16384, what is `max_M_at_95_recall`?

## Pre-registered bands

- **HARD_PASS**: `max_M_at_95_recall > N = 16384`
  (exponential bend appears at or below 2N; the relaxed HP from v1's
  "> 2N" threshold, since v2 caps the sweep at 2N=32768).
- **HARD_FAIL**: `max_M_at_95_recall in [0.8*N/4, 1.2*N/4] = [3277, 4915]`
  (linear extends; outer-product ceiling).
- **MIDDLE_BAND**: otherwise.

## Sweep

- N=16384
- M cells: [N/8, N/4, N/2, N, 2N] = [2048, 4096, 8192, 16384, 32768] (5)
- Seeds: 3 ([7, 17, 23])

REDUCED from v1 (dropped 4N, 8N, 16N to avoid OOM).

## Timeout estimate

User-authorized 86400s (24h) for battery-class N=16384 sweep. Per cell:
~30-60s. 15 cells = ~600-900s; the long timeout absorbs cell-failure
restarts and any per-cell stalls.

## Memory footprint at top M=2N=32768

- Keys: 32768 * 16384 * 4 = 2.1GB
- CB: 49152 * 16384 * 4 = 3.2GB
- W: 16384 * 16384 * 4 = 1.07GB
- Peak ~6.4GB. Within 8GB; tight, hence graceful fail.

## N-suffix

`_n16384` binds production N = 16384. Smoke runs at N=1024.
queue_add.py exit-6 validator checks `N = 16384` literal in script.
