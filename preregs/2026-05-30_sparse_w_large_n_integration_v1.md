# Pre-registration: sparse_w_large_n_integration_v1

**Date:** 2026-05-30
**Anchor:** sparse_w_large_n_integration_v1
**Script:** experiments/exp_sparse_w_large_n_integration_v1.py
**Queue:** remote_cpu_queue (CPU, marsh@home)

## N-suffix
No `_n<N>` suffix because the experiment spans N=4096 (footprint sweep) +
N=8192 (validation runs) + projection to N=16384. Per PROT-018 rule 3 the
script asserts the explicit N values at module top:
`assert N_FOOTPRINT == 4096`, `assert N_VALIDATION == 8192`,
`assert N_PROJECT == 16384`.

## Question
Does sparse-W compose with large-N (N=16384 projection target) to deliver
on-device-deployable memory footprints (sparse-W cost <= 25% of dense W at
N=16384 at a typical operating M=2048), while preserving the four killer
features (KF-1 hallucination detection, KF-2 edit isolation, retention,
audit-cert chain) at the empirically-grounded validation N=8192?

## Setup
- Footprint sweep: N=4096, M in [128, 512, 2048, 8192]. Records both
  empirical (built substrate) and theoretical footprint bytes.
- Validation: N=8192 (BSC codebook because N=8192 has odd log2; Kerdock
  4-coset requires N in {1024, 4096, 16384}), M in [512, 2048, 8192],
  3 seeds.
- Projection: log-linear fit on N=4096 footprint cells to confirm sparse
  slope ~ 1.0 (theoretical). Project sparse cost at N=16384 across M
  sweep [1024, 2048, 4096, 8192]. Evaluate on-device deployability at
  M=2048 anchor (theory: ratio = 2 * 2048 * 16384 / 16384^2 = 0.25).

## Pre-registered bands

- **HARD_PASS:** sparse-W at N=8192 preserves all killer features in ALL 3
  seeds at all M (retention >= 0.90, KF-2 max_iso <= 0.05,
  KF-1 above_thresh_frac < 0.05) AND empirical projection slope in
  [0.95, 1.05] (theoretical 1.0) AND projected N=16384 footprint at
  M=2048 <= 25% of dense N=16384 (= 1024 MiB).
- **HARD_FAIL:** sparse-W loses any killer feature at N=8192 in >= 2/3 seeds
  at any M OR projection slope outside [0.95, 1.05] (composition unstable).
- **MIDDLE_BAND:** otherwise (slope ok but KF degraded in 1/3 seeds; or KF
  ok but projection invalid).

## Calibration note
This is a calibration probe for the sparse-W + large-N composition. The
sparse-W footprint formula (2 * M * N * 4) is theoretically exact for
float32; the empirical step verifies the codebook builder doesn't introduce
hidden allocation. The "deployable" threshold of 25% is from user spec
(consistent with 4x savings from sparse + 16x dense capacity = on-device
viable). The slope band ±5% is tight because the underlying formula is
analytic; any deviation > 5% indicates a code path or measurement issue.

## OOM check
- All work on CPU (remote_cpu_queue). No GPU memory pressure.
- Largest allocation: N=8192 BSC codebook = 8192*8192*4 = 256 MiB per cell.
- Plus W (dense) = 256 MiB. Peak ~ 700 MiB. CPU RAM has plenty.

## Smoke result (2026-05-30)
- N_fp=1024, N_val=1024 (smoke), M_fp=[32, 128], M_val=[32, 128], 1 seed.
- fp N=1024 M=32: sparse/dense = 0.0625 (theory: 2*32/1024=0.0625) MATCH.
- fp N=1024 M=128: sparse/dense = 0.2500 (theory: 2*128/1024=0.25) MATCH.
- kf N=1024 M=32: ret=1.000 iso=0.000 kf1=0.000 PASS.
- kf N=1024 M=128: ret=1.000 iso=0.000 kf1=0.000 PASS.
- projection slope=1.0 deployable=True.
- Verdict: C8_HARD_PASS at smoke.
- smoke_wall_s = 0.15s.

## Timeout estimate
- Smoke: 0.15s for tiny config.
- FULL: 4 M values for footprint at N=4096 (~1s each) + 9 KF cells at
  N=8192 (build 256MB codebook + 3 metrics; ~30-90s each on CPU).
  Total ~15 min compute, much higher with worst-case M=8192 OOM-adjacent.
- **timeout = 21600 s (6 h)** for headroom + remote-CPU possibly running
  at BELOWNORMAL priority. Long-run flag for status_log.
- Formula: ceil(1.5 * 0.15 * 4 * 9 * 100) = 810s base; inflated for
  large-N CPU work and BELOWNORMAL throttling.

## Self-test
- `_instrumentation_selftest()` at module scope.
- Footprint formula self-test:
  - sparse(N=4096, M=2048, 4-byte) = 2*2048*4096*4 = 67108864 (= 64 MiB).
  - dense(N=4096, 4-byte) = 4096^2 * 4 = 67108864 (= 64 MiB).
  - dense(N=16384) = 16384^2 * 4 = 1073741824 (= 1024 MiB).
  - sparse(N=16384, M=8192) = 2*8192*16384*4 = 1073741824 (= 1024 MiB; saturation).
  - sparse(N=16384, M=2048) = 2*2048*16384*4 = 268435456 (= 256 MiB; ratio 0.25).
- Empirical footprint matches theory within 64 bytes.
- KF metrics non-null and non-NaN at smoke scale.
- Projection slope = 1.0 at smoke (perfect for analytic formula).

## Dependencies
- experiments/_metric_battery.py (make_substrate, metric_retention,
  metric_max_iso, metric_above_thresh_frac) - exists.
- experiments/_seed_checkpoint.py - exists.
- Built-in BSC codebook fallback for N=8192 (script-local `make_bsc_substrate`).
