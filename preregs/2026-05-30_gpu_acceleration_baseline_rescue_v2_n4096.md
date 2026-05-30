# Prereg: gpu_acceleration_baseline_rescue_v2_n4096

Date: 2026-05-30
Anchor: gpu_acceleration_baseline_rescue_v2_n4096
Script: experiments/exp_gpu_acceleration_baseline_rescue_v2_n4096.py
N-suffix: _n4096 -> production N = 4096 (top of reduced sweep)

## Question

v1 was anchored `_n8192` and ran 20s without producing metrics.json
(NO_METRICS instrumentation failure per cap_map v283). v2 REDUCES scope:

- N sweep [2048, 4096] only (drop 8192)
- 3 seeds (down from 5)
- Per-op timing for store/query/edit ONLY (drop batched + delete + KF
  battery from rescue scope)
- Per-op try/except with explicit error reporting

Anchor suffix `_n4096` matches reduced top-N (PROT-018-clean).

## Pre-registered bands

- **HARD_PASS**: mean `query_speedup` at N=4096 >= 5x AND all 3 ops
  (store/query/edit) succeed on cuda in 3/3 seeds.
- **HARD_FAIL**: mean `query_speedup` at N=4096 <= 2x OR any op fails
  on cuda in 2+/3 seeds.
- **MIDDLE_BAND**: otherwise.

HP threshold RELAXED from v1's 10x to 5x because v2 drops the largest
N=8192 (which was the most GPU-favorable).

## Sweep

- N values: [2048, 4096]
- Seeds: 3 ([7, 17, 23])
- Devices: [cpu, cuda]
- Total cells: 2 * 3 * 2 = 12

## Timeout estimate

14400s (4h). 12 cells * ~30s = 360s; ample.

## N-suffix

`_n4096` binds top-of-sweep N=4096. Smoke runs at N=1024.

## Note

v1 anchor name was `_n8192`; v2 is reduced-scope so anchor uses `_n4096`
to honor PROT-018 binding (production N is now 4096 max).
