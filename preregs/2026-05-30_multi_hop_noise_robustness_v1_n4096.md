# Prereg: multi_hop_noise_robustness_v1_n4096

**Date:** 2026-05-30
**Anchor:** multi_hop_noise_robustness_v1_n4096
**Script:** experiments/exp_multi_hop_noise_robustness_v1_n4096.py
**Queue:** overnight_queue
**Timeout:** 14400s

## Why this anchor

Production data has noise: transcription errors in stored facts, query-side
uncertainty. Determines which mechanism (B/D/E) handles real-world noise best
-- critical for Pattern B integration where stored facts may have source
uncertainty.

This is the natural complement to R1 (which characterizes mechanism behavior
across (M, depth) at clean storage) and R4 (which characterizes path E's
latency envelope). R5 holds (M, depth) fixed at production-realistic values
and sweeps NOISE.

## Noise model

- Stored facts noise: each key vector and value vector gets `sigma * N(0, 1)`
  Gaussian noise per coordinate at storage time. W is rebuilt from these noisy
  vectors. Codebook is left clean (it's the readout target).
- Query noise: each query start vector gets the same Gaussian noise at retrieval.
- sigma applies to BOTH storage AND query (worst-case symmetric noise).

## Sweep grid

- N = 4096 (PROT-018 _n4096 binding).
- M = 2048 (production regime, well below M_c).
- depth = 5 (canonical multi-hop).
- K_paths = 100 (production-realistic).
- 3 paths: {B, D, E}.
- sigma grid: {0.00, 0.05, 0.10, 0.20, 0.40}.
- Seeds: {7, 17, 23, 31, 41}.
- Per-cell-seed checkpoint.
- Cells: 3 paths x 5 sigmas x 5 seeds = 75 cell-seeds.

## Pre-registered bands

- **HARD_PASS (HP)** = at least one path maintains accuracy >= 0.65 at sigma=0.20
  AND degrades gracefully (max |acc[i+1] - acc[i]| < 0.30 across adjacent sigma
  levels) in >= 3/5 seeds. Reading: "this path is production-viable under noise."
- **HARD_FAIL (HF)** = ALL paths drop below 0.30 accuracy at sigma=0.10 (mean
  over seeds). Reading: "mechanisms brittle to small noise."
- **MIDDLE_BAND (MB)** = otherwise.

## Outcome plan

| Verdict | Action |
|---|---|
| HARD_PASS | Identified path is the production default; document the noise envelope. |
| HARD_FAIL | Production deployment requires a denoising preprocessor; surface upstream to Strategy. |
| MIDDLE_BAND | Identify which sigma is the breaking point per path; use as deployment constraint. |

## Closed-form self-tests in the script

- `compute_verdict(fake_hp)` -> HARD_PASS when B's acc curve is smooth and
  >= 0.65 at sigma=0.20 in all 5 seeds.
- `compute_verdict(fake_hf)` -> HARD_FAIL when all paths drop to 0.10 at sigma=0.10.

## Timeout estimate

smoke_wall_s = 0.4s (N=1024, M=512, 2 sigmas, 1 seed, 3 paths).
FULL: N 1024->4096 (16x for N^2; matmul); depth 3->5 (1.6x); M 512->2048 (4x storage);
K 20->100 (5x for D); seeds 1->5 (5x); sigmas 2->5 (2.5x).
Per-cell-seed at FULL ~10-30s.
75 cell-seeds total. Average ~20s -> 1500s expected. User pre-spec'd 14400s.

**Timeout: 14400s** (per user spec).

## PROT-018 _n4096 binding

`N = 4096` is a module-level constant. Verified.

## Dependency check

- experiments/_metric_battery.py -- exists
- experiments/_relation_graph.py -- exists
- experiments/_seed_checkpoint.py -- exists
- No upstream data files required.
