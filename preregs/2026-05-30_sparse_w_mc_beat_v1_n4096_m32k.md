# Pre-reg: sparse_w_mc_beat_v1_n4096_m32k

**Date:** 2026-05-30
**Anchor:** sparse_w_mc_beat_v1_n4096_m32k
**Script:** experiments/exp_sparse_w_mc_beat_v1_n4096_m32k.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** T1.3 (sparse-W envelope beyond standard M_c)

## Hypothesis

At N=4096, sparse-W retains usable retrieval AND non-trivial memory
characteristics across M in {8192, 16384, 24576, 32768} -- spanning the
estimated M_c band (16384-20480 from m_c_probe_v1_n4096).

## Pre-registered bands

| Outcome      | Condition                                                                  |
|--------------|----------------------------------------------------------------------------|
| HARD_PASS    | retention >= 0.95 AND mem_savings_ratio >= 2x at ALL 4 M points in >=3/5 seeds |
| HARD_FAIL    | retention drop >= 0.20 at any M >= 16384 in >=3/5 seeds                    |
| MIDDLE_BAND  | otherwise                                                                  |

mem_savings_ratio = dense_bytes / sparse_bytes = N^2 / (2*M*N) = N / (2*M).
At M=8192 N=4096: ratio = 0.25 (sparse LARGER than dense). HARD_PASS gate
intentionally near-impossible at these M values; this is a CHARACTERIZATION
ANCHOR and HARD_FAIL is the well-defined informative outcome.

## Calibration

No prior empirical anchor for sparse-W at M > N (M_c regime). HARD_FAIL
band set at +/- 20% retention loss (sub-threshold = sparse degrades past
M_c). Per [[feedback-envelope-expansion-fail-bands]].

## Self-test

`_instrumentation_selftest()`:
- N == 4096 (PROT-018).
- memory_bytes formulas verified.
- compute_verdict returns HARD_PASS / HARD_FAIL on synthetic cells.
- One CPU forward pass at N=1024, M=64 confirms sparse_retention,
  mem_savings_ratio, kf2_max_iso are non-null.

## Timeout estimate

smoke_wall_s ~ 0.2s at N_SMOKE=1024 M={64,256}. FULL N=4096, M up to 32768
scaling_exp=2.0 (matrix ops). 4 M x 5 seeds = 20 cells.
PROT-019 _n4096 floor 14400s. Budget: 21600s (6h) for safety at M=32768.
**timeout_s = 21600**

## Production config

N=4096, M_sweep=[8192, 16384, 24576, 32768], seeds=[7, 17, 23, 31, 41],
beta=8.0, n_probe=200.

## N-suffix binding

_n4096 -> production N = 4096. PROT-018 enforced via grep
`N\s*=\s*4096` in script.
