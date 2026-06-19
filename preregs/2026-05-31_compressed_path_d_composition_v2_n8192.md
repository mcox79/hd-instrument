# Pre-registration: compressed_path_d_composition_v2_n8192

**Date**: 2026-05-31
**Anchor**: compressed_path_d_composition_v2_n8192
**Queue**: overnight_queue (GPU)
**Script**: experiments/exp_compressed_path_d_composition_v2_n8192.py
**PROT-018**: _n8192 binds N = 8192.
**PROT-019**: timeout_s = 14400 (floor).
**PROT-021**: per-cell checkpointing (seed x M).
**PROT-022**: N=8192 is NOT a valid Kerdock dimension (requires 2^(2t));
  script uses explicit BSC bipolar codebook. Never calls make_substrate().

## Context

v1 (compressed_path_d_composition_v1_n4096) landed CPD_HARD_PASS: c_quant/bits8
preserves Path D depth=5 accuracy at N=4096, M in {8192, 32768} (cap_map v303,
"c_quant/bits8 x Path D" Validated 0.65-0.80 sub-row under PP-2).

Cross-N to N=8192 closes whether the composition holds beyond N=4096.

## Configuration

- N = 8192, **BSC bipolar codebook** (PROT-022: not Kerdock -- N=8192 invalid)
- M_grid: [16384 = 2N, 65536 = 8N] (same M/N ratios as v1)
- depth = 5, K_paths = 100, n_starts = 100
- Seeds: [7, 17, 23, 31, 41] (5 seeds)
- 2 arms per cell: (i) baseline W, (ii) c_quant/bits8 W

## Pre-registered thresholds

| Band | Condition |
|---|---|
| HARD-PASS | acc_compressed >= 0.95 on BOTH M values in 4/5+ seeds. Composition N-robust. |
| HARD-FAIL | acc_compressed < 0.70 in majority of cells. Compression breaks Path D at N=8192. |
| MIDDLE-BAND | acc_compressed 0.70-0.95 OR passes 2N but fails 8N. Marginal; deployment caveat needed. |

## Outcome plans

**IF HARD-PASS**: PP-2 x Path D composition row extends from N=4096 to N=4096+8192.
Strong cross-N validation for production deployment narrative.

**IF MIDDLE-BAND (8N fails, 2N passes)**: composition is M/N-ratio sensitive.
The 8N over-capacity regime introduces compression noise that Path D cannot overcome.
File: cap_map caveat "c_quant/bits8 x Path D limited to M <= 4N at N=8192."

**IF HARD-FAIL**: quantization error grows with N in a way that breaks Path D
probability-domain disambiguation at N=8192. File upstream-push to Strategy:
c_quant/bits8 may require bit-width scaling with N (e.g., bits=10 at N=8192).

## BSC vs Kerdock note

N=8192 = 2^13. Kerdock 4-coset codebook requires N = 2^(2t) with t in {5,6,7}:
valid values are {1024, 4096, 16384} only. BSC bipolar codebook is used instead.
BSC has equivalent capacity properties for random-query retrieval experiments.
This is the correct substrate at N=8192; Kerdock is invalid here.

## Timeout estimate

v1 at N=4096 CPU: ~30s/seed/M. This runs on GPU at N=8192.
GPU at 2x N: estimated ~20s/seed/M (GPU much faster than CPU).
10 cells x 20s = 200s. Safety: ceil(1.5 * 200) = 300s.
PROT-019 floor dominates. **timeout_s = 14400**.

## N-suffix

PROT-018 binding: N_FULL = 8192 in script. Production config matches _n8192 suffix.
