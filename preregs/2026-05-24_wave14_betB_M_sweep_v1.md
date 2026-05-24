# Prereg -- Bet B Direction 1: Sample-complexity / storage-capacity M-sweep

**Date**: 2026-05-24
**Routing source**: `notes/strategy_request_to_exp_dev_2026-05-24_5_new_directions.md` (Direction 1 -- HIGH leverage; single most informative for Bet B closure)
**Cap_map at filing**: v189 (commit 45fda61)
**Script**: `experiments/exp_wave14_betB_M_sweep_v1.py`
**Queue target**: overnight_queue (GPU; M=16384 cell dominates compute)
**Expected wall**: ~60-90 min full (5 M-points x 3 seeds; M=16384 alone is ~30 min)
**Designed by**: exp_dev inline

## What is being tested

Whether Bet B's 91-92% retention ceiling is capacity-bound (rises with substrate width M) or interference-bound (plateaus). Per [[feedback-verify-implementations]]: M = substrate width N (dimensionality of BSC code and W matrix). Pool size left at base default POOL_SIZE=1024.

## Pre-registered M-sweep

M (substrate width N) sweep: [1024, 2048, 4096, 8192, 16384]
- 0.25x baseline -- below the regime where compound mechanism was characterized
- 0.5x baseline
- 1x baseline (current Bet B operating point; retention_A ~ 0.91-0.92)
- 2x baseline -- key data point per routing note "2x-4x current M"
- 4x baseline -- key data point per routing note

## Falsifier statements

- **HARD_PASS_CAPACITY_BOUND**: retention_A monotone-increasing in M across the sweep AND retention_A(M_max) - retention_A(M_min) >= 0.10 (10pp lift). -> Substrate retention is capacity-bound; product story unlocked.
- **HARD_FAIL_INTERFERENCE_BOUND**: retention_A plateaus across M-sweep within +/-0.03 (3pp band). -> Substrate retention is interference-bound; 91-92% IS the substrate; accept-ceiling product framing per cycle 188 user framing.
- **MIDDLE_BAND**: any intermediate scaling; report bands.

## Adjacent theory verdict (per `notes/research_5_directions_math_drill_2026-05-24.md` Drill 1)

PAC-Bayes bound for outer-product Hebbian with sequential tasks is M-INDEPENDENT. If the empirical M-sweep is interference-bound (HARD_FAIL), the bound is CONFIRMED; if capacity-bound (HARD_PASS), the bound is too loose and a refined Hebbian-specific PAC-Bayes form is needed. This empirical IS the discriminator.

## Pre-registered config

- N (substrate width) -- THE swept variable
- K (context) = 4; BETA = 8
- Seeds = [7, 17, 23] (3 seeds; M=16384 is compute-heavy)
- bytes_per_corpus = 200000; phase_a_epochs = 8; phase_b/c_epochs = 5
- EMA_alpha = 0.7; replay_frac = 0.50 (matches base Kovacs)

## Rescue paths if HARD_FAIL (interference-bound) per [[feedback-rehabilitation-after-rejection]]

1. Pool size sweep at fixed M (separate POOL_SIZE axis from substrate-width axis).
2. K (context length) sweep at fixed M (test if context-length is the load-bearing capacity axis).
3. Vocabulary sweep (test if larger vocab interacts with M).
4. Mixed-precision FP16 at M=32768 (memory-bound; would reveal if FP32-at-M=16384 is the bottleneck).
5. Per-task substrates at varying M (test if structural-separation axis interacts with capacity).
