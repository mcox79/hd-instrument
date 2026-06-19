# Pre-registration: path_d_k1_phase_boundary_cross_m_v1_n4096

Date: 2026-06-01
Anchor: path_d_k1_phase_boundary_cross_m_v1_n4096
Queue: remote_cpu_queue (CPU)

## Hypothesis

v1 probe found k1_mean=0.022 at M=16N (6.7x random). This cross-M sweep locates
the substrate-physics phase boundary: at what M does K=1 signal cross from
"graceful degradation >random" to "random-chance"?
Research P3 predicted ceiling at M ~ 100N-300N; this measures the M-axis empirically.

## Configuration

- N = 4096 (PROT-018 binding)
- M_grid = [2N=8192, 4N=16384, 8N=32768, 16N=65536, 32N=131072]
  (64N=262144 dropped: 512 GB codebook exceeds RAM)
- depth = 5
- K_paths grid: {10, 100} (via path_d_run); path_b_run for K=1 effective
- k_random_keys = 100 per (seed, M) cell
- 5 seeds: [7, 17, 23, 42, 99]
- Device: cpu (PROT-022)

## Primary metric

path_b_top1_acc = fraction of random starts where Path B (no candidate pool) walk
arrives at correct codebook atom after depth=5 steps (top-1 NN in codebook).
This IS the K=1 phase boundary probe; path_d_run(K=1) is degenerate.

## Pre-registered bands

Per-M cell:
  HP: path_b_top1_acc > 0.10 (substantive)
  HF: path_b_top1_acc < 0.002 (random-chance floor)
  MIDDLE: path_b_top1_acc in [0.002, 0.10]

Overall cross-M verdict:
  HARD-PASS: path_b_top1_acc >= 0.005 at M=16N (corroborates v1 MIDDLE_BAND 0.022)
             AND clear decay trend with increasing M.
  HARD-FAIL: path_b_top1_acc < 0.005 at M=2N (no K=1 signal at any M).
  MIDDLE-BAND: M-axis characterized; boundary identified at specific M*.

Calibration note: v1 measured 0.022 at M=16N. M=16N corroboration window: [0.011, 0.044] (2x).

## OOM check

Worst case M=32N=131072: codebook = 131072 x 4096 float32 = 2 GB.
Remote CPU RAM = 64 GB. Peak ~2.1 GB. OK.

## Timeout estimate

v1 elapsed ~30-60s/seed at M=16N. M=32N is 2x. 25 cells total.
Estimated 60s x 25 x 1.5 = 2250s -> 2700s. PROT-019 floor: 14400s.
timeout_s = 14400.

## N-suffix binding

_n4096: production N = 4096. Script assert N_FULL == 4096.
