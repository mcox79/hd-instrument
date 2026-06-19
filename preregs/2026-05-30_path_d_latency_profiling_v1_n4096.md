# Pre-registration: G1 path_d_latency_profiling_v1_n4096

Date: 2026-05-30
Anchor: path_d_latency_profiling_v1_n4096
Queue: overnight_queue
Script: experiments/exp_path_d_latency_profiling_v1_n4096.py
N-suffix: _n4096 (PROT-018) — production N = 4096

## Question

Across `M in {2048, 8192, 16384}` x `depth in {3, 5, 10, 15}` x
`K_paths in {100, 500, 1000}` at N=4096 BSC, what operation dominates
Path D wall_s in each cell? Is the dominance pattern stable across
seeds and within `(M, K)` families across depth?

## Production config (PROT-018)

- N_FULL = 4096
- M_GRID_FULL = [2048, 8192, 16384]
- DEPTH_GRID_FULL = [3, 5, 10, 15]
- K_GRID_FULL = [100, 500, 1000]
- SEEDS_FULL = [7, 17, 23, 31, 41]  (5 seeds)
- N_STARTS = 16 starts per cell
- 3 x 4 x 3 x 5 = 180 cell-seeds (36 unique cells)
- PER-CELL CHECKPOINT (PROT-021)

## Instrumentation

Per-operation timing via `TimingTrace` (from `_multi_hop_mechanisms`):
- `time_enumerate_paths`         (decoy path sampling)
- `time_likelihood_query_per_hop`(per-hop substrate W-query + sim)
- `time_bayesian_update`         (log-posterior accumulation)
- `time_posterior_max`           (final argmax)

Memory tracking:
- `mem_cpu_peak_mib` via `tracemalloc`
- `mem_cuda_delta_mib` via `torch.cuda.max_memory_allocated` delta

Per-cell `dominant_op` = op whose `total_ns` > 50% of summed wall.

## Pre-registered bands

- **HP**: `dom_fraction >= 0.80` (>=80% of cells have a >50% dominant op)
  AND mean within-family `mode_frac >= 0.60`
  (same dominant op across same M/K family along depth axis)
- **HF**:
  - `mean_seed_disagree >= 0.50` (seeds disagree on dominant op in >=50%
    of (M, depth, K) cells), OR
  - `res_violation_frac >= 0.50` (per-op times below measurement
    resolution: max-op-total < 10x min-per-op-call in >=50% of cells)
- **MB**: otherwise

## Smoke result

- M_grid=[512,1024] depth_grid=[3,5] K_grid=[20,50] N=1024 1 seed
- 8/8 cells reported `time_likelihood_query_per_hop` dominant
  (frac 0.72-0.82)
- Verdict: `G1_HARD_PASS` at smoke (`dom_frac=1.0`, `family_mode=1.0`,
  `seed_disagree=0`)
- Effect size at smoke: d ~ large (uniform dominant op call across
  all cells) -> FULL n=180 is sufficient power.

## Calibration / walk-back

- Smoke effect size is strong (uniform dominance). FULL stays at 180
  cell-seeds (no walk-back doubling required).
- Verdict band gating is NOT a calibration probe (it gates instrumentation
  consistency, not a theoretical effect). Standard bands apply.

## OOM check

N=4096 M=16384 -> codebook C=16384 x 4096 fp32 = 256 MiB; W=64 MiB; K=1000
path enum = ~4 MiB. Peak ~350 MiB. Under 6 GiB GPU headroom.

## Timeout estimate

- `smoke_wall_s` = 0.66s (8 smoke cells); per-cell smoke ~ 0.08s
- scaling: N (1024->4096) = 4x; depth (max 5->15) = 3x; K (max 50->1000) = 20x;
  cells (8->36) = 4.5x; seeds (1->5) = 5x; scaling_exp = 1.5
- Conservative per-cell-seed estimate: 0.08 * 4 * 3 * 20 * 1.5 = ~30s
- Total: 30s * 180 = 5400s. With margin and depth-15 K-1000 cells (heaviest
  tail) doubling: ~9000s.
- TIMEOUT = 21600s (6 hours; per user spec for Batch 1 #1 safety).
  Note flagged for For You status_log: >7200s long run.

## Outcome routing

- **HP**: identifies concrete dominant op per (M, K) family. Unblocks
  Testbed Test 10 (posterior-max optimization) and any per-op refactor
  work. Path D engineering target locked.
- **HF**: instrumentation noise dominates -> back to Strategy with
  finer-resolution timer plan or per-op call-batching strategy.
- **MB**: differential dominance (e.g. likelihood-dominated at small K,
  posterior-max-dominated at large K) -> Pattern B integration uses
  regime-aware optimization plan.
