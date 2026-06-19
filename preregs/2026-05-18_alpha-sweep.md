# Pre-registration: α (pool blend) sweep — rehabilitation from Titans rejection

Date: 2026-05-18
Status: Pre-registered, ready to launch
Experiment file: [exp_alpha_sweep_charlm.py](../experiments/exp_alpha_sweep_charlm.py)

## Hypothesis (H)

The pool retrieval head contributes materially to test bpc at α=0.3 (the
current best). This rehabilitation experiment measures pool importance
directly by sweeping α ∈ {0.0, 0.1, 0.3, 0.5, 0.7, 1.0}.

H is operationalized as: `bpc(α=0.0) − bpc(α=0.3) ≥ 0.05`. That is, removing
the pool entirely degrades test bpc by ≥0.05 bits.

## Cited mechanism / paper

This is a measurement experiment, not a mechanism test. No specific paper
predicts the exact value. Related lit:
- Schlag-Irie-Schmidhuber 2021 *Linear Transformers are Secretly Fast Weight
  Programmers* (ICML) — fast weights as memory blended with slow weights.
- Irie/Gershman 2025 *Blending Complementary Memory Systems*.
- Our prior measurement: pool top-1 = 0.437, W top-1 = 0.605. Pool alone is
  worse than W alone; the question is whether blending the two helps.

## Operational definition

For each α ∈ {0.0, 0.1, 0.3, 0.5, 0.7, 1.0}, train the standard
combined+modReLU baseline (15 epochs, N=4096, all other hyperparams fixed
to current best). At test time:
```
P = α · P_pool + (1 − α) · P_W
```
where P_pool is the softmax-weighted-by-similarity-and-label retrieval
distribution and P_W is the modReLU+softmax W readout distribution.

α=0.0 = W readout only (no pool contribution)
α=1.0 = pool only (no W readout)

## Falsification criterion (machine-readable)

H supported if `bpc(α=0.0) ≥ 2.55` (i.e., removing pool hurts ≥ 0.05 bpc
vs the 2.4994 baseline).

H rejected if `bpc(α=0.0) ≤ 2.51` (i.e., removing pool changes bpc by ≤
0.011, within noise floor). If this happens, the pool is barely
contributing; pool-mechanism work has low ceiling and Titans-style
rehabilitation candidates are deprioritized.

Inconclusive if `2.51 < bpc(α=0.0) < 2.55`.

## Pre-mortem (top 3 failure causes if rejection)

1. **W readout alone is already near-optimal at this scale.** modReLU + 15
   epochs + decay may saturate the W capacity, leaving little for the pool
   to add. Would mean: the pool is a redundant ensemble member, not a
   complementary information source.
2. **The pool's contribution is exclusively to rare bytes**, which are too
   few in the test set to move bpc materially. Would mean: pool retrieval
   shows up in per-byte bpc histogram but not in the aggregate.
3. **α=0.3 was tuned without comparison to α=0.0.** The baseline may have
   converged on α=0.3 by accident of an earlier choice, not because it's
   optimal. Would mean: even an α-tuned variant won't help much.

## Parameter-matched non-bio control

α=0.0 IS the no-pool control. α=1.0 is the pool-only control.
This experiment is itself the control suite for any future pool-mechanism work.

## Expected wall time

6 α values × ~55s each at N=4096 ≈ 6 minutes total single-seed.

## What this measurement tells us about Titans

If α=0.0 ≈ baseline (H rejected): the Titans rejection was over-interpreted.
The gate didn't fail because of common-byte filtering — it failed because
the pool itself is barely contributing. No amount of pool-mechanism work
will help much. Move on to substrate experiments (BSC) instead.

If α=0.0 is much worse than baseline (H supported): the pool IS doing real
work. The Titans rejection IS about gate design, and rehabilitation
candidates (inverted gate, larger pool, gradient-norm surprise) are
genuinely worth running. Also: the optimal α might not be 0.3 — could be
higher.
