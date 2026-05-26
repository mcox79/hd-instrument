# Prereg — Sparse-coding codebook vs PPMI/random (A6/U3 field probe)

**Anchor**: `wave14_sparse_coding_ppmi_v1`
**Queue**: remote_cpu_queue (pure CPU; dictionary learning)
**Filed**: 2026-05-24 by exp_dev

## Hypothesis

Field probe per v195 8-new-fields delivery (SPARSE CODING). Sparse-coding
dictionary learned from byte-bigram cooc may outperform random bipolar and
PCA codebooks on binding-recall task.

## Pre-registered falsifiers (BEFORE FULL run)

- **HARD-PASS**: sparse-coded atoms outperform BOTH random AND PCA baselines
  by >=0.05 recall cosine across >=3 of 4 M values.
  -> A6/U3 row advanced; sparse-coding is a substrate-worthy codebook
  generator.
- **HARD-FAIL**: sparse-coded atoms within +/-0.01 of random OR worse on
  >=3 of 4 M values. -> sparse-coding rejected.
- **MIDDLE-BAND**: any intermediate.

## Parameters (exp_dev autonomy)

- N = 2048 FULL / 256 smoke
- M grid = {50, 100, 200, 400} FULL / {50, 100} smoke
- Seeds = {7, 17, 23} FULL
- N_sparse_atoms = 256
- L0 sparsity = 8
- Dict iters = 6

## ETA

Remote CPU FULL ~15-30 min.

## Smoke outcome

Smoke at N=256 single-seed: sparse atoms underperform random by 1-2 pct.
Small N hurts sparse coding more (the dict atoms are too sparse relative to
small N). FULL at N=2048 + 3 seeds is the test.
