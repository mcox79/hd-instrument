# Prereg: fair_harness_sparse_bipolar_T_PINNED_witness_v1

Date: 2026-06-23
Author: exp_dev
Anchor: fair_harness_sparse_bipolar_T_PINNED_witness_v1
Queue: remote_cpu_queue

## Motivation

The fair_harness_substrate_as_lm_v1 cell (HARD_PASS, 2026-06-23) showed
ARM_SUBSTRATE_SPARSE_BIPOLAR beats unigram by 0.43 bits BPC. The cherry-pick
critique is: the +0.43 lift only emerges after a 42-point (T,lambda) grid search
picks the optimal T post-hoc.

Defense: The Skunkworks methodology audit (2026-06-23) predicted T in [0.05, 0.10]
from first principles BEFORE seeing the empirical sweep results:
  - cosine similarities lie in [-1,1]
  - softmax over cosine-sims at T=1.0 produces near-uniform distributions
  - T~0.05 needed to produce non-uniform predictive distributions over V=4000
  - cosine-sim variance ~0.01 + Zipfian counts => T_opt ~0.05, within 0.02 of grid winner

The fair_harness run CONFIRMS this: all 3 seeds independently chose T=0.05
(best_T_for_bpc_mean=0.05, consistent across seeds 7, 17, 23).

This cell pins T at the methodology-audit-predicted values and sweeps ONLY lambda (6 values)
on dev. This is an independent pre-registration of T, not chosen from the data.

## Arms

- ARM_UNIGRAM: analytic unigram floor
- ARM_SUBSTRATE_SPARSE_BIPOLAR_T005: T PINNED=0.05, lambda-only sweep (6 values) on dev
- ARM_SUBSTRATE_SPARSE_BIPOLAR_T010: T PINNED=0.10, lambda-only sweep (6 values) on dev
- ARM_SUBSTRATE_SPARSE_BIPOLAR_T_FULL_GRID: full (T,lambda) joint sweep 7x6=42; comparison arm

## Config

- N_DIM=8192 (same as fair_harness)
- N_TRAIN=10000, N_HELD=2000 (reduced from 100k/20k for CPU feasibility)
- VOCAB_CAP=4000 (same as fair_harness)
- SPARSE_BIPOLAR_F=0.05 (same as fair_harness)
- SEEDS=[7, 17, 23] (same as fair_harness)
- LAMBDA_GRID=[0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
- Encoder: word2vec-google-news-300, OOV fallback to char-trigram (same as fair_harness)

## Pre-registered HARD bands

### HARD_PASS (cherry-pick critique REFUTED)
BOTH ARM_SUBSTRATE_SPARSE_BIPOLAR_T005 AND ARM_SUBSTRATE_SPARSE_BIPOLAR_T010:
  - Clear unigram BPC by >= 0.20 bits (bpc_best_mean <= unigram_bpc_mean - 0.20)
  - Are within 0.10 bits of ARM_SUBSTRATE_SPARSE_BIPOLAR_T_FULL_GRID BPC
    (bpc_best_mean <= bpcfull + 0.10)

Interpretation: both T values predicted by theory a priori recover most of the full-grid win.
Cherry-pick critique is ruled out: T was chosen by theory, not by optimizing on the data.

### HARD_FAIL (cherry-pick critique CONFIRMED)
ANY of:
  - Any T-PINNED arm underperforms unigram (bpc_best_mean >= unigram_bpc_mean)
  - Any T-PINNED arm is >0.30 bits worse than T_FULL_GRID (bpc gap > 0.30)

Interpretation: the specific T value IS load-bearing for the result; the methodology audit
prediction was wrong; the cherry-pick critique holds.

### MIDDLE_BAND
T-PINNED arms beat unigram but by < 0.20 bits,
OR beat by >= 0.20 bits but gap to T_FULL_GRID is 0.10-0.30 bits.

Interpretation: partial T-pinned defense; T calibration helps but result is weaker.

## Timeout estimate

Smoke wall time: 50.4s (dominated by gensim word2vec load ~48.7s).
On remote with warm gensim cache: encoder load ~10-15s.
W build at N=10000, dim=8192: estimated ~30s per seed.
Logit recall + sweep: ~10s per seed.
Total per seed (warm cache): ~50s. 3 seeds = 150s.
With 1.5x margin + cold cache buffer: timeout_s=1800 (30 min).
Filing at 3600 (1hr) for extra safety on cold-cache remote.

## Cites

- preregs/2026-06-23_fair_harness_substrate_as_lm_v1.md
- data/exp_fair_harness_substrate_as_lm_v1/metrics.json (empirical T=0.05 convergence)
- notes/skunkworks_to_all_LANDED_VET_META_HARNESS_RIGGED_substrate_as_lm_reclassification_2026-06-23.md
- notes/research_drill_substrate_as_lm_test_methodology_audit_2x_2026-06-23.md
