# Pre-registration: DeltaNet-style update variants

Date: 2026-05-18
Status: Pre-registered, not yet run
Experiment file: [exp_deltanet_variants_charlm.py](../experiments/exp_deltanet_variants_charlm.py)

## Hypothesis (H)

Our current best (combined+modReLU, 2.4994 bpc) uses a **softmax-cleaned delta
rule**: error = target_atom − softmax(modReLU(W ctx)) @ codebook. The literature
points to two natural alternatives:

- **DeltaNet (Yang et al. 2024)**: raw-vector error `target_atom − W ctx`, no
  softmax cleanup, no modReLU. This is the literal DeltaNet update.
- **Pure Hebbian** (no error subtraction): `dW = target ⊗ ctx`. The simplest
  associative rule, included as a control to confirm the delta rule is doing work.

Sub-hypothesis: the softmax cleanup + modReLU each contribute independent gain.
The 2x2 ablation (cleanup yes/no × modReLU yes/no) will tell us which dominates.

## Cited mechanism / paper

- Yang et al. *Parallelizing Linear Transformers with the Delta Rule*,
  arXiv 2406.06484 (DeltaNet, 2024). Update: W ← W(I − k kᵀ) + v kᵀ, which
  expands to W += (v − W k) kᵀ. This is a fully-replacing delta rule with
  explicit erase of the old value at key k.
- Schlag-Irie-Schmidhuber 2021 *Linear Transformers are Secretly Fast Weight
  Programmers* (ICML): the underlying delta-rule fast-weight formulation.

## Operational definition (Carnap)

Five variants, all sharing baseline architecture (N=4096, K=4, pool 1024,
α=0.3, decay=1e-4, β=8, modReLU b=0.5 where applied):

| Variant | Update equation |
|---|---|
| `baseline_cleaned` | dW = (target − softmax(β·sim(byte_atoms, modReLU(W ctx))) @ byte_atoms) ⊗ ctx̄ / N |
| `raw_delta` | dW = (target − W ctx) ⊗ ctx̄ / N |
| `raw_delta_with_modrelu` | dW = (target − modReLU(W ctx)) ⊗ ctx̄ / N |
| `pure_hebbian` | dW = target ⊗ ctx̄ / N |
| `cleaned_no_modrelu` | dW = (target − softmax(β·sim(byte_atoms, W ctx)) @ byte_atoms) ⊗ ctx̄ / N |

All variants: W ← (1 − decay) W + α dW.

**Faithfulness to DeltaNet:** `raw_delta` matches DeltaNet's update form for a
single-key step. DeltaNet's full algorithm runs in parallel over the sequence;
we run online over batches. The mechanism (raw-error outer-product update with
implicit erase via subtraction of W k) matches; the parallel scan does not.

## Falsification criterion (machine-readable)

This experiment tests **three sub-hypotheses** with separate criteria:

**H1: DeltaNet-style raw error beats cleaned error.**
- Support if `raw_delta` 5-seed mean ≤ 2.485 (≥ 0.014 better, ≥ 2× FP noise).
- Reject if `raw_delta` 5-seed mean ≥ 2.515 OR `baseline_cleaned` is best by ≥ 0.014.
- Weak/inconclusive otherwise.

**H2: modReLU dominates the gain (vs cleanup).**
- Support if `baseline_cleaned` − `cleaned_no_modrelu` > `baseline_cleaned` − `raw_delta_with_modrelu`.
- Operationalized: if removing modReLU hurts more than removing cleanup, H2 supported.

**H3: Pure Hebbian (no delta) is materially worse than delta-rule variants.**
- Support if `pure_hebbian` 5-seed mean ≥ 2.7 (a clear gap from ~2.5).
- Reject if `pure_hebbian` 5-seed mean ≤ 2.55 (delta rule was overrated).
  We will be SURPRISED if H3 is rejected — pre-commit to noting this prominently
  in the tracker.

Single-seed exploratory pass first; 5-seed promotion only for any variant
within ±0.01 of the best single-seed result.

## Pre-mortem (top 3 failure causes)

1. **Raw error blows up W norm without cleanup.** Without the codebook projection,
   the error `target − W ctx` has unbounded magnitude when W is wrong; this could
   cause runaway W growth. Need to monitor ||W|| each epoch.
2. **modReLU acts as implicit regularizer, not signal-enhancer.** If removing
   modReLU at test time hurts, but adding it during training to raw-delta doesn't
   help, modReLU is doing regularization not sparse-coding.
3. **The softmax cleanup hides everything because the codebook is small.** With
   only 256 byte atoms, the softmax projection has very limited freedom — it
   essentially picks the closest codebook entry. This may mean the "cleanup
   advantage" we measured is small and inconsistent across seeds.

## Parameter-matched non-biological control

Already built-in: `pure_hebbian` is the simplest mechanism and serves as the
"no learning signal" control. If pure-Hebbian matches delta-rule variants, the
"delta rule helps" story is unsupported in our regime.

Also pre-committed: ||W|| Frobenius is logged per epoch for all variants. If
`raw_delta` wins but ||W|| explodes, the win is a regularization artifact.

## Expected wall time

5 variants × 15 epochs × ~50s/epoch at N=4096 ≈ 60 min total single-seed.
5-seed promotion (best variant) ≈ 12 min. Total: ~75 min.
