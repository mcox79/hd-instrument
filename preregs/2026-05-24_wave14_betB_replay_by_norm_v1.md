# Prereg -- Bet B Direction 2: Replay-by-bundle-norm weighted vs uniform

**Date**: 2026-05-24
**Routing source**: `notes/strategy_request_to_exp_dev_2026-05-24_5_new_directions.md` (Direction 2 -- MEDIUM; cheap addition; potential gap-closer)
**Cap_map at filing**: v189 (commit 45fda61)
**Script**: `experiments/exp_wave14_betB_replay_by_norm_v1.py`
**Queue target**: overnight_queue (GPU; 2 modes x 5 seeds A->B->C)
**Expected wall**: ~30-45 min full (2 modes x 5 seeds x 3-phase pipeline)
**Designed by**: exp_dev inline

## What is being tested

Substrate-specific replay scheme: weight Phase A replay samples by their bundle-norm (||ctx||_2 in W-space). High-norm bundles are in dense regions of the substrate's representational space, hypothesized to be the "vulnerable" memories that catastrophic forgetting hits hardest. Compare against uniform random replay (current Bet B Kovacs mechanism).

## Two modes

- **uniform**: existing replay (samples drawn uniformly from pool)
- **norm_weighted**: samples drawn with probability proportional to ||ctx||_2 over the active replay pool (computed once per Phase since pool is appended only during Phase A)

## Falsifier statements

- **HARD_PASS**: norm_weighted retention_A >= 0.91 AND within +0.02 or better of uniform. -> Replay-by-vulnerability validated; substrate-novel replay scheme is at least neutral, potentially gap-closer.
- **HARD_FAIL**: norm_weighted retention_A falls more than 0.02 below uniform across the A->B->C pipeline. -> Bundle-norm NOT the load-bearing weighting axis; replay-composition theory rejected for this metric.
- **MIDDLE**: norm_weighted within +/-0.02 of uniform; report.

NOTE: Original routing note framed HARD_PASS as "closes 7pp gap from 73% baseline to 80%". This was written before v188 LONGER_PHASEA confirmed compound is ALREADY at 91-92%. Re-framing per [[feedback-no-smoke]] before the run, not after: HARD_PASS is "matches-or-beats uniform at >= 0.91 retention_A".

## Pre-registered config

- N = 4096; K = 4; BETA = 8
- Seeds = [7, 17, 23, 31, 41] (5 seeds)
- bytes_per_corpus = 200000; phase_a_epochs = 8; phase_b/c_epochs = 5
- EMA_alpha = 0.7; replay_frac = 0.50 (FIXED -- not a sweep here)

## Rescue paths if HARD_FAIL per [[feedback-rehabilitation-after-rejection]]

1. Inverse-norm weighting (sample LOW-norm bundles preferentially -- maybe substrate-novel "edge bundle" hypothesis).
2. W-distance weighting (sample replay pool by distance to current W's eigenvectors).
3. Gradient-norm weighting (sample by ||dW|| from each context).
4. Hybrid uniform+norm_weighted at 50/50 mix.
5. Norm-weighting only DURING PHASE B (not Phase C) -- test if the load-bearing point is Phase B intrusion not Phase C overwrite.
