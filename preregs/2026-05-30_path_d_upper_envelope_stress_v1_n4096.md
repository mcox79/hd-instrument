# Pre-reg: path_d_upper_envelope_stress_v1_n4096

**Date:** 2026-05-30
**Anchor:** path_d_upper_envelope_stress_v1_n4096 (U1, v289 follow-on)
**Script:** experiments/exp_path_d_upper_envelope_stress_v1_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** v289 cap_map Path D production-default ceiling characterization.

## Context

Path D was selected as the production-default 6-axis robust multi-hop
mechanism in v289 cap_map. R1 (stress_at_breaking) showed Path D unanimous
1.000 through M=24576 depth=20 K=500 -- but did not identify a breaking
ceiling. This anchor pushes past R1's envelope: M up to 4x larger and depth
up to 2.5x deeper, to find the actual production limit.

## Hypothesis

Path D will either:
  (a) hold accuracy >=0.85 across all tested cells (need a v2 with harder
      cells) -- the production envelope extends past this test, OR
  (b) break clearly at one or more (M, depth) cells, identifying a
      production ceiling.

## Pre-registered bands

| Outcome      | Condition                                                                |
|--------------|--------------------------------------------------------------------------|
| HARD_PASS    | mean accuracy >=0.85 across ALL 20 (M, depth) cells (over 5 seeds)        |
| HARD_FAIL    | mean accuracy <0.30 at >=50% of cells (>=10 of 20)                         |
| MIDDLE_BAND  | otherwise (differential breaking pattern, informative)                   |

## Sweep grid

- M ∈ {16384, 24576, 32768, 49152, 65536} (R1 max was 24576)
- depth ∈ {10, 20, 30, 50} (R1 max was 20)
- K_paths fixed at 500 (per R1 baseline; K-scaling already characterized by Q3+S2)
- 5 seeds = {7, 17, 23, 31, 41}
- Total: 5 x 4 x 5 = 100 cell-seeds, per-cell-seed checkpoint (PROT-021)

## Self-test (instrumentation)

- `_instrumentation_selftest()` runs at module load:
  - N == 4096 (PROT-018)
  - HP verdict gate: synthesized acc=0.90 across all cells -> HARD_PASS
  - HF verdict gate: synthesized acc=0.10 at >=50% cells -> HARD_FAIL
  - MIDDLE_BAND verdict gate: synthesized one-cell failure -> MIDDLE_BAND
  - Live `measure_cell()` smoke on CPU, N=1024 M=512 depth=3 K=20 produces
    a non-null accuracy in [0,1] and n_eval > 0 (filter survives)

## OOM check

- N=4096, M=65536: M_eff = min(M, C=4N) = 16384 (capped at codebook size).
- Storage: codebook 256 MiB, W 64 MiB, per-call path lists ~2 MiB.
- Peak ~400 MiB on GPU. Well under 6 GiB headroom on 8 GiB runner.

## Timeout estimate

- Smoke wall ~60s estimated at module-load instrumentation.
- FULL: 100 cell-seeds. depth=50 dominates inner Path D loop over B starts
  x K=500 candidates x depth=50 dst computations.
- Estimate ~50s/cell-seed = 5000s; with substrate build overhead and
  worst-case depth=50 super-linear scaling, budget 21600s per user spec.

## Production config

- N=4096, K_paths=500, N_starts=16, beta=4.0
- M_grid, depth_grid, seeds as above.

## N-suffix binding

`_n4096` -> production N = 4096 (PROT-018). `N_FULL = 4096` asserted at
import time; pre-ship gate `grep -E "(N\s*=|n\s*=)\s*4096"` matches `N = 4096`
on line ~84.
