# Pre-registration: path_b_subcapacity_characterization_v1_n4096

**Date:** 2026-05-30
**Anchor:** path_b_subcapacity_characterization_v1_n4096
**Test:** T5 (Test 24 of user-routed batch)
**Queue:** overnight_queue (GPU)
**Script:** experiments/exp_path_b_subcapacity_characterization_v1_n4096.py

## Hypothesis

Path B (continuous-output propagation) works at sub-capacity (M well below
N/4). The Pattern B LLM integration regime operates at M in [50, 500].
We characterize Path B specifically at this regime against Path D, with
attention to the continuous-representation advantage: geometric interpolation
between facts (cosine similarity of the continuous Path B response with
the expected output vector).

If Path B achieves >=0.90 accuracy AND beats Path D in latency AND yields
geometric-cos >=0.85 at ALL (M, depth) cells in the Pattern B regime, Path B
earns the killer-feature classification for LLM integration.

## Config

- N = 4096 (PROT-018 _n4096 binding).
- BSC substrate.
- M sweep = [50, 100, 200, 500].
- depth sweep = [3, 5, 8].
- K_paths = 100 (for the Path D comparison).
- 5 seeds = [7, 17, 23, 31, 41].
- 24 path-starts per seed.
- Total cells: 4 M-points * 3 depths * 5 seeds = 60 cell-seeds.

### Path B continuous

q_{d+1} = q_d @ W.T (NO argmax between hops).
Final argmax over codebook similarity at the end.

### Path D comparison

Standard path_d_run at same (M, depth, K). Latency measured per-cell.

### Geometric interpolation metric

For each path-start with valid target:
  q = codebook[start]; for d hops: q = q @ W.T
  cos = (q . target_vec) / (||q|| * ||target_vec||)
mean over path-starts in cell.

## Pre-registered bands

**HARD_PASS:** For ALL (M, depth) cell-groups (M <= 500 is in Pattern B
regime by construction since the sweep is bounded at 500):
- >= 3/5 seeds have acc_b >= 0.90
- AND >= 3/5 seeds have lat_b < lat_d
- AND >= 3/5 seeds have geom_cos_b >= 0.85.

**HARD_FAIL:** Any cell-group triggers >= 3/5 seeds for:
- acc_b < 0.70, OR
- lat_b > lat_d.

**MIDDLE_BAND:** all other outcomes.

## Self-tests

- N_FULL == 4096 (PROT-018).
- measure_geometric_interpolation returns cos in [-1, 1].
- path_b_run + path_d_run callable without TypeError (smoke verified).
- compute_verdict returns T5_HARD_PASS / T5_HARD_FAIL / T5_MIDDLE_BAND /
  T5_INCONCLUSIVE only.
- smoke produces acc_b=1.000 acc_d=1.000 geom_cos=0.948 (M=50, depth=2)
  and geom_cos=0.812 (M=200, depth=2) at N=1024.

## OOM check

- N=4096, M=500: keys+vals 4 MiB; W 64 MiB; CB 805 MiB. Total ~900 MiB.
- 60 cells run sequentially; per-cell peak <1 GB.
- Well within 6 GB GPU ceiling.

## Smoke result

- N_smoke=1024, M_sweep=[50, 200], depths=[3], K=20, n_paths=8, 1 seed.
- smoke_wall_s ~ 0.2s.
- M=50, d=3: acc_b=1.000, acc_d=1.000, geom_cos=0.948, lat_b<lat_d=True.
- M=200, d=3: acc_b=1.000, acc_d=1.000, geom_cos=0.812, lat_b<lat_d=True.
- All metrics non-null; instrumentation self-test PASSes; one cell shows
  geom_cos below 0.85 at M=200 (single-seed) — indicates that at higher
  M within Pattern B regime, geometric quality degrades.

## Walk-back gate

Smoke at M=200 produced geom_cos=0.812, slightly below the HP threshold
of 0.85 — borderline. However: (a) this is a single seed at smaller N,
(b) the geom_cos at M=50 is 0.948 (well above), suggesting genuine M-
dependence. The full sweep at N=4096 with 5 seeds covers this directly.

Per the walk-back gate guidance, d (Cohen's d at smoke) is not directly
computable from a single-seed reading. The full 5-seed sweep across
4 M-points * 3 depths = 12 cell-groups gives 60 measurements — power-
adequate; not doubling sample size.

## Timeout estimate

- smoke_wall_s = 0.2s at 2 cells = 0.1s/cell at N=1024.
- FULL: 4x N, 8x M (max M_full / smoke avg), 1.7x depth, 24/8=3x
  n_paths, 5x K_paths, 5 seeds, 4*3=12 cells/seed = 60 cells.
- Per-cell scaling factor (FULL/smoke): 4*8*1.7*3*5 = ~816; with
  scaling_exp=1.5 -> ~78x per-cell vs smoke.
- 60 cells * 0.1s * 78 = 468s. Apply 2x safety -> ~936s.
- Conservative budget for 60-cell sweep with N=4096 substrate per cell:
  timeout_s = 14400 (user task spec).

**timeout_s = 14400** (user task spec).
