# Pre-registration: depth_sanity_check_v1_n4096

**Date:** 2026-05-30
**Anchor:** depth_sanity_check_v1_n4096
**Script:** experiments/exp_depth_sanity_check_v1_n4096.py
**Queue:** overnight_queue (GPU)
**PROT-018:** _n4096 binds N = 4096 (confirmed in script header).

## Question
Does Path D multi-hop accuracy maintain >= 0.85 across depths 75, 100, 150 at
production operating point N=4096, M=8192, K_paths=500, OR is there a depth
cliff between the previously-tested depths 50 and depth 150?

U1 tested depths [10, 20, 30, 50]; G7 tested depths [10, 20, 30, 50] at higher
M (24N-32N). Neither covers depth in [75, 150] at production M=8192.

## Setup
- N=4096 (BSC/Kerdock 4-coset codebook, 4N=16384 codewords).
- M=8192 facts (production operating point per user spec, M=2N).
- K_paths=500 candidate paths per query.
- Path D ONLY (state-propagation + Bayesian likelihood; no Path B/E).
- Depths: [75, 100, 150].
- 5 seeds: [7, 17, 23, 31, 41].
- 24 multi-hop queries per cell.
- 3 cells x 5 seeds = 15 cell-seeds.

## Pre-registered bands

- **HARD_PASS:** mean accuracy >= 0.85 at ALL 3 depths in >=3/5 seeds per depth
  (no cliff between depth 50 and depth 150).
- **HARD_FAIL:** any single depth has mean accuracy < 0.40 in >=3/5 seeds
  (cliff present; current depth envelope must be revised downward).
- **MIDDLE_BAND:** otherwise (partial: some depths pass, others sag in
  [0.40, 0.85) band; informative but not depth-cliff-confirmed either way).

## OOM check
- N=4096, M=8192, K_paths=500, depth=150 worst case:
  - keys+vals: 8192 * 4096 * 4 * 2 = 256 MiB
  - W (dense): 4096^2 * 4 = 64 MiB
  - codebook (4N): 16384 * 4096 * 4 = 256 MiB
  - Path D src/dst tensors: 500 * 150 * 4096 * 4 * 2 = ~2.4 GiB
- Peak ~3 GiB. OK on 8 GiB GPU.

## Smoke result (2026-05-30)
- N=1024, M=256, depths=[3, 5], K=40, 1 seed, 8 queries.
- d=3 acc=1.000 lat=0.01s; d=5 acc=1.000 lat=0.02s. Verdict: G13A_MIDDLE_BAND
  (1 seed cannot meet HP threshold of >=3/5; HP confirmed by 1/1 accuracy at HP band).
- smoke_wall_s = 0.09s for 2 cells.

## Timeout estimate
- smoke_wall_s = 0.09s (very fast on CPU at small scale).
- However, FULL is GPU with N=4096, M=8192, K_paths=500, depth up to 150 -
  the path-D per-query inner loop scales linearly with depth and K_paths.
- Effective scale ratio: N (4x) * K (12.5x) * depth_max (50x at depth 150 vs 3)
  * seeds (5x) * cells (3 depths) ~ 37500x.
- Even with 100x CPU-to-GPU speedup, FULL ~ 37500 * 0.09 / 100 = ~34s
  per query x 24 queries = ~13min per cell, 3 cells = ~40min total.
- Apply 1.5x safety + GPU launch overhead -> ~2h.
- **timeout = 14400 s (4 hours)**, formula
  ceil(1.5 * 0.09 * (4)^1.5 * (5) * (3 depths) * (depth_scale 50) * (K_scale 12.5))
  -> orders of magnitude calculation conservatism;
  bounded by role-contract maximum of 14400 (4 h).
  Long-run flag for status_log.

## Self-test
- `_instrumentation_selftest()` runs at module-scope import.
- N=1024 small scale and N=4096 4x scale.
- Asserts acc non-null, n_queries_valid > 0, latency_s > 0.

## Dependencies
- experiments/_multi_hop_mechanisms.py (build_shared, path_d_run) - exists.
- experiments/_relation_graph.py - exists.
- experiments/_metric_battery.py (via _multi_hop_mechanisms) - exists.
- experiments/_seed_checkpoint.py - exists.
