# Pre-registration: GHRR permutation-binding variants

Date: 2026-05-18
Status: Pre-registered, queued (after DeltaNet + BSC)
Experiment file: [exp_ghrr_charlm.py](../experiments/exp_ghrr_charlm.py)

## Hypothesis (H)

A non-commutative binding operation — implemented as per-position random
permutation applied to position (or byte) atoms — improves test bpc at
N=4096 on our 38KB byte-level corpus.

H is operationalized as: best non-baseline variant 5-seed mean ≤ 2.485
(≥ 0.014 better than baseline, ≥ 2× FP-noise floor).

## Cited mechanism / paper

- Alam, Raff, Holt et al. *Generalized Holographic Reduced Representations*,
  arXiv 2405.09689 (May 2024). Proposes extending HRR with non-commutative
  binding operations.
- Kanerva 1996 *Binary Spatter Codes* — original VSA paper that discusses
  permutation as a binding primitive.
- Kleyko et al. 2022 *Survey on HD Computing Part I* — survey of VSA
  binding operations including permutation-based.

**Faithfulness note:** Alam-Raff propose a more elaborate non-commutative
binding via learned mixing matrices. We test the **simpler
permutation-binding variant first** as a low-effort sanity check; this is
a related, simpler form of non-commutative binding, but does NOT fully
replicate the GHRR formalism. If permutation-binding helps, we follow up
with the full GHRR machinery; if it doesn't, GHRR's specific mixing-matrix
mechanism might still help but at higher implementation cost.

## Operational definition

For each k ∈ {0, K-1}, generate a fixed random permutation perm_k of
indices [0..N-1] using SEED+k as the RNG seed. Binding becomes:

- `baseline_no_perm`: `byte_atom * pos_atom[k]` (current FHRR)
- `pos_permuted`: `byte_atom * pos_atom[k][perm_k]`
- `byte_permuted`: `byte_atom[perm_k] * pos_atom[k]`
- `both_permuted`: `byte_atom[byte_perm_k] * pos_atom[k][pos_perm_k]`
  (different perms for byte and pos paths)

All other architecture, hyperparams, and seeds are identical to the
combined+modReLU baseline (2.4994).

## Falsification criterion (machine-readable)

H supported if best non-baseline variant 5-seed mean ≤ 2.485.

H rejected if all non-baseline variants have 5-seed mean ≥ 2.495
(within ±0.005 of baseline). Permutation-binding does not help at our
operating point.

Direction-of-effect informs follow-up:
- If `pos_permuted` helps but `byte_permuted` doesn't: position structure
  benefits from non-commutative encoding. Position encoding is the bottleneck.
- If `byte_permuted` helps but `pos_permuted` doesn't: byte identity
  benefits from non-commutative encoding. Vocabulary encoding is the bottleneck.
- If `both_permuted` helps more than either alone: independent permutations
  on each path compose constructively.

## Pre-mortem (top 3 failure causes)

1. **Position structure is already adequately captured by per-position pos
   atoms.** Random pos atoms per k already differ; adding a permutation on
   top may not add information. If H rejected for this reason, GHRR's full
   mixing-matrix mechanism is unlikely to help either at our K=4.
2. **Permutation breaks unbinding.** With non-commutative binding, recovery
   of byte from `bind(byte, pos)` via `bind(pos.conj(), .)` no longer
   works directly. Our system doesn't unbind (W learns implicit unbinding),
   so this may not matter — but check that pool retrieval quality doesn't
   crash.
3. **K=4 is too small to see sequence-order benefits.** Frady-Kanerva-Sommer
   found grid-cell binding shines at K=20-100, not K=4. The same may hold
   for non-commutative binding. Mitigation: if rejected, retry at K=8 or K=16.

## Parameter-matched non-bio control

`baseline_no_perm` IS the matched control. Same atoms, same hyperparams,
same seed — only the binding operation differs.

## Expected wall time

4 variants × 15 epochs × ~3.5s/epoch at N=4096 ≈ ~3.5 minutes total.

## What this measurement tells us

If permutation-binding helps: weak evidence that non-commutativity matters
at our scale. Justifies follow-up at K=8/16 and full GHRR machinery.

If permutation-binding doesn't help: weak evidence that the FHRR position
code is doing what's needed at K=4. Substrate experiments (BSC) become
the higher-EV direction.

Either way, this is cheap to run and closes the GHRR question for our
current operating point.
