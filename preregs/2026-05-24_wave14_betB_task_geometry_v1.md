# Prereg -- Bet B Direction 3: task-representation geometry as load-bearing variable

**Date**: 2026-05-24
**Routing source**: `notes/strategy_request_to_exp_dev_2026-05-24_5_new_directions.md` (Direction 3 -- HIGHEST LEVERAGE per user)
**Cap_map at filing**: v189 (commit 45fda61)
**Script**: `experiments/exp_wave14_betB_task_geometry_v1.py`
**Queue target**: overnight_queue (GPU; PPMI eigenvalues + multi-pair A->X training)
**Expected wall**: ~30-45 min full (5 task-pairs x 3 seeds; substrate width N=4096)
**Designed by**: exp_dev inline (orchestrator role per [[feedback-dispatch-wrappers-default]])

## What is being tested

Whether Bet B's 91-92% retention ceiling moves PREDICTABLY with task-pair spectral distance. Five task pairs span a range of A->X distance:

| Pair | corpus_X | Expected spectral distance | Hypothesis |
|---|---|---|---|
| B_shuffled | byte-shuffled A | LOW (preserves byte frequencies) | high retention |
| E_reversed | reversed A | LOW (similar marginals, different bigram graph) | high retention |
| C_python | Python source | MID (different byte distribution) | mid retention |
| D_random | uniform random bytes | HIGH (uniform marginal) | low retention |

Order in the regression spans 2-3 orders of magnitude in spectral KL.

## Spectral distance metric

KL divergence between top-256 eigenvalue histograms of corpus PPMI matrices (32 bins over union range). PPMI is symmetric so eigh is exact. PPMI matrix is 256x256 (byte-bigram); top 256 eigenvalues are the full spectrum.

Per [[feedback-verify-implementations]]: this is "KL on eigenvalue distributions" per the routing note. Bundle-distribution Wasserstein is OPTIONAL future work; this prereg ships KL only.

## Falsifier statements

- **HARD_PASS**: retention_A monotone-DECREASING in spectral distance AND r^2 of regression >= 0.60 across the 4-pair sweep. -> Substrate retention is geometry-bound; product story unlocked.
- **HARD_FAIL**: r^2 < 0.20 OR non-monotone. -> Retention not geometry-bound; "predict any task pair before training" story REJECTED.
- **MIDDLE**: 0.20 <= r^2 < 0.60 OR monotone with smaller lift; report and propose follow-up.

## Pre-registered config

- N_substrate = 4096; K (context) = 4; BETA = 8
- Seeds = [7, 17, 23] (3 seeds for compute budget)
- bytes_per_corpus = 200000; phase_a_epochs = 8; phase_x_epochs = 5
- EMA_alpha = 0.7
- replay_frac = 0.50 (matches base Kovacs)

## Rescue paths if HARD_FAIL (per [[feedback-rehabilitation-after-rejection]])

1. Try Wasserstein on bundle distributions instead of KL on eigenvalues (a different geometry metric).
2. Use BLEU-style n-gram divergence as the distance metric (rather than spectral).
3. Use a smaller distance window (B_shuffled vs E_reversed) to see if substrate distinguishes near-pairs.
4. Project PPMI via Kerdock codebook instead of BSC (test if codebook structure changes the geometry).
5. Use multi-seed within-pair variance as a discriminator (geometry-bound predicts low within-pair variance).
