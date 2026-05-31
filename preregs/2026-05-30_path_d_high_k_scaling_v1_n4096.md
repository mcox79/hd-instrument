# Pre-registration: G2 path_d_high_k_scaling_v1_n4096

Date: 2026-05-30
Anchor: path_d_high_k_scaling_v1_n4096
Queue: overnight_queue
Script: experiments/exp_path_d_high_k_scaling_v1_n4096.py
N-suffix: _n4096 (PROT-018) — production N = 4096

## Question

Holding `M=8192`, `depth=5`, `N=4096 BSC`, does Path D maintain `accuracy
>= 0.95` at `K_paths in {1500, 2000, 3000, 5000}` AND does `log(latency)`
regress linearly on `log(K)` with slope <= 1.1?

## Production config (PROT-018)

- N_FULL = 4096
- M_FIXED = 8192 (within validated envelope per v289)
- DEPTH_FIXED = 5 (production-typical)
- K_GRID_FULL = [1500, 2000, 3000, 5000]
- SEEDS_FULL = [7, 17, 23, 31, 41]  (5 seeds)
- N_STARTS = 16
- 4 K x 5 seeds = 20 cell-seeds
- PER-CELL CHECKPOINT (PROT-021)

## Pre-registered bands

- **HP**:
  - mean `accuracy >= 0.95` at K_max=5000 in `>=3/5 seeds`
  - log-log latency slope `<= 1.1` (linear with small headroom)
- **HF**:
  - mean `accuracy < 0.70` at ANY K (mean across seeds), OR
  - log-log latency slope `>= 1.5` (super-linear)
- **MB**: otherwise

Scaling slope = OLS of `log(mean_lat_s)` on `log(K)` across the 4 K values
(mean over seeds at each K).

## Smoke result

- smoke N=1024 M=256 K_grid=[20,50,100] 1 seed
- accuracy = 1.000 at all 3 K
- latency: 24/44/61 ms (slope = 0.58 sub-linear)
- Verdict at smoke: G2_MIDDLE_BAND (only 1 seed; pass needs 3/5 — gate
  works as designed).
- Effect size: accuracy ceiling = 1.0 with no variance; HP gate at FULL
  is conditional on K=5000 holding.

## Calibration / walk-back

- Smoke effect size on slope is strong (0.58 << 1.1). FULL keeps 5 seeds
  at K up to 5000 with no walk-back doubling needed.
- The accuracy ceiling at smaller K is uninformative for K=5000 prediction;
  FULL run is the actual test.

## OOM check

N=4096 M=8192 K_max=5000 depth=5. Codebook=256 MiB, W=64 MiB,
K*depth indices = 25k longs = 200 kB. Peak ~400 MiB. Under 6 GiB.

## Timeout estimate

- smoke_wall_s = 0.22s for 3 smoke cell-seeds; ~0.07s per cell-seed
- scaling: N=4x, M(256->8192)=32x but only affects substrate build (not
  per-cell hot loop), K_max(100->5000)=50x, seeds(1->5)=5x;
  effective scaling_exp = 1.5
- Per-cell-seed at FULL ~ 30-60s (K=5000 dominant; depth=5 fixed)
- Total: 60s * 20 = 1200s. With margin 3600s.
- TIMEOUT = 14400s (4-hour cap; gives full headroom for tail cases).

## Outcome routing

- **HP**: K-scaling confirmed linear up to K=5000. Production Path D
  envelope extended to K=5000. Next: K=10000 scaling probe (Batch 2 if
  applicable).
- **HF**: K-scaling breaks at high K. Need batched-K execution strategy
  or candidate-pruning before posterior-max. Route to Strategy for
  rescue design.
- **MB**: K=5000 doesn't quite hit HP-95 in 3/5 seeds; characterize
  effective production K-ceiling.
