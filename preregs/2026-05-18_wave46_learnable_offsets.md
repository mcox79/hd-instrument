# Pre-registration: Wave 4.6 — Gradient W + learnable atom offsets

Date: 2026-05-18
Status: Pre-registered, queued after Wave 4.5
Experiment file: [exp_wave46_learnable_offsets.py](../experiments/exp_wave46_learnable_offsets.py)

## Hypothesis (H)

Adding learnable per-byte offsets to the random BSC atoms (atom_v =
sign_STE(random_v + Δ_v)) closes additional perplexity beyond Wave 4.5
(gradient W with frozen atoms). Specifically: best Δ-regularization variant
beats Wave 4.5's best variant by ≥ 0.03 bpc.

Compositional hypothesis: gradient W (Wave 4.5) addresses the
"optimizational" gap; learnable offsets (Wave 4.6) address the
"representational" gap on top.

## Cited mechanism / paper

- Imani et al. *Hyperdimensional computing with holographic and adaptive
  encoder* (Frontiers in AI, 2024) — canonical reference for learnable HDC
  atoms in classification; 1-3% accuracy gains over fixed-random encoders.
- Yeung, Zou, Imani 2024 *Generalized Holographic Reduced Representations*
  (arXiv 2405.09689) — extends adaptive encoder to non-commutative binding.
- THDC: Training Hyperdimensional Computing Models with Backpropagation
  (arXiv 2602.00116, Jan 2026) — full end-to-end backprop on HDC.
- Liu et al. 2023 ICCV *ReSTE: Rectified Straight Through Estimator*
  (arXiv 2308.06689) — STE recipe for sign() in binary networks.

## Operational definition

Identical to Wave 4.5 except:

- byte_atoms = sign_STE(random_byte + Δ_byte), where Δ_byte is a learnable
  (VOCAB_SIZE, N) Parameter init to zero
- pos_atoms = sign_STE(random_pos + Δ_pos), similar (K, N)
- sign_STE: forward sign(x); backward clipped identity (gradient passes
  through where |x| ≤ 1, blocked elsewhere) — ReSTE recipe
- Optimizer: AdamW with two parameter groups: W (weight_decay=1e-4) and
  atom offsets (weight_decay ∈ {1e-2, 1e-3, 1e-4} — the controlled sweep)
- Atoms reconstructed every forward pass with current Δ

Higher Δ weight decay → atoms stay closer to random (HDC-like).
Lower Δ weight decay → atoms drift freely (more transformer-like).

The sweep characterizes the tradeoff.

## Falsification criterion (machine-readable)

**Support:** Best Δ-wd variant 5-seed mean is ≥0.03 bpc below Wave 4.5
best 5-seed mean.

**Reject:** All Δ-wd variants are within ±0.02 bpc of Wave 4.5 best.
The "fixed atoms cost perplexity" hypothesis is empirically false at our
scale.

**Strong support:** Δ-wd=1e-4 (least regularization) beats Wave 4.5 by
≥0.10 bpc AND ||Δ|| has grown substantially (>0.5 × ||random||). Atoms
have meaningfully shifted to learn structure.

## Pre-mortem (top 3 failure causes)

1. **STE gradient mismatch is too lossy.** sign_STE's gradient is clipped
   identity; this is a known approximation that hurts at low LR. If
   atoms don't move (||Δ|| stays small), it's likely the STE is
   blocking too many gradients. Mitigation: try ReSTE's `x^(1/k)`
   shaping if identity-STE doesn't work.

2. **Adam destabilizes the substrate.** Learning atoms via Adam can
   produce momentum-driven oscillations. The L2 regularizer on Δ
   should pin it but might not be strong enough. Mitigation: try SGD
   with weight decay instead.

3. **38KB is too little data to learn good atoms.** Random atoms work
   precisely because we don't have enough data to do better than random.
   If H rejected, the constraint isn't "fixed atoms are wrong" — it's
   "we don't have enough data to learn atoms at this corpus size." Wave
   2a (1MB corpus) becomes critical: re-run Wave 4.6 at larger scale.

## Parameter-matched non-bio control

Built-in: the Δ=0 case IS Wave 4.5 (gradient W with frozen atoms).
Comparing best-Δ-wd variant to Wave 4.5 IS the controlled A/B test.

Also tracked: ||Δ|| Frobenius norm per epoch. Tells us if atoms moved
materially. If Δ stays near zero across all variants, the offsets didn't
help and the constraint isn't binding.

## Expected wall time

3 weight-decay variants × ~60-180s each at N=4096 ≈ 5-10 min total.
Gradient computation with learnable atoms adds maybe 1.5-2× overhead vs
Wave 4.5 due to autograd through STE.

## Decision tree

| Outcome | Next step |
|---|---|
| Strong support (≥0.10 over 4.5) | Run at N=8192. Run with larger corpus (Wave 2a). |
| Weak support (0.03-0.10) | Promote to 5-seed. Combine with Wave 6.5 (Schlag-Irie hybrid). |
| Reject (within ±0.02) | Atoms aren't the bottleneck at this scale. Push to depth (Wave 5/6). |
| Negative (atoms hurt) | STE problem. Try alternative gradient estimators. |

## Connection to the bigger story

If Wave 4.5 wins by 0.1 + Wave 4.6 wins another 0.05, combined 0.15 below
BSC delta-rule baseline puts us at 2.33 bpc — below the tiny-transformer
baseline (2.39) at the same N. That's a real headline result.

If both win minimally, the bottleneck is structural (depth, attention),
and we redirect to Wave 5+ for depth.

If neither wins, the delta rule + fixed atoms is near-optimal at our
scale and the perplexity floor is data-bound (Wave 2a critical).
