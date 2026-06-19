# Pre-registration: Wave 4.5 — Gradient W with frozen atoms

Date: 2026-05-18
Status: Pre-registered, queued (will launch after Wave 3 finishes)
Experiment file: [exp_wave45_gradient_w_frozen_atoms.py](../experiments/exp_wave45_gradient_w_frozen_atoms.py)

## Hypothesis (H)

Replacing the Hebbian delta-rule update on W with Adam-optimized gradient
updates (cross-entropy loss) lowers test bpc by at least 0.05 bpc 5-seed mean.

H operationalized: best gradient-trained variant (across LR sweep) is at
least 0.05 bpc lower than the BSC delta-rule baseline at the same N.

## Cited mechanism / paper

- Schlag, Irie, Schmidhuber 2021 ICML *Linear Transformers are Secretly
  Fast Weight Programmers* (arXiv 2102.11174). Theorem: linearized
  attention with delta-rule fast weights IS a fast-weight programmer
  trained by backprop on the slow network. The delta rule itself is just
  the chain rule unrolled. Backprop on the same W finds a different
  (lower-loss) optimum than the delta rule's least-squares solution.
- Yang et al. 2024 *Parallelizing Linear Transformers with the Delta Rule*
  (DeltaNet, arXiv 2406.06484). At scale, gradient-trained delta-rule
  fast weights match or beat parameter-matched transformers.
- Wave 8 backprop audit (2026-05-18) recommended this as the
  cheapest-lowest-risk-highest-leverage single addition.

## Operational definition

Identical architecture to BSC baseline (signed bundling, modReLU readout,
pool blend at α=0.3, β=8, N=4096 and N=8192, K=4), EXCEPT:

- W is a `torch.nn.Parameter` with `requires_grad=True`
- Training loss: cross-entropy on softmax-cleaned predictions
  `loss = -log P_W[target]` (mean across batch)
- Optimizer: `torch.optim.AdamW(lr ∈ {3e-3, 1e-2, 3e-2}, weight_decay=1e-4)`
- Atoms (byte and position): random fixed BSC ±1, NOT trainable
- Pool: same as before, written in epoch 1 only

All other hyperparams are matched to the delta-rule baseline.

**Faithfulness to Schlag 2021:** Schlag's setup uses backprop on a slow
network whose output produces the delta-rule fast-weight updates. Our setup
applies backprop DIRECTLY to W. This is a simpler test: "does gradient
descent on the same W find a better solution than the delta rule?"
Strictly weaker than Schlag's full architecture, but the cheapest way to
test the empirical claim.

## Falsification criterion (machine-readable)

**Support:** Best gradient variant 5-seed mean is ≥0.05 bpc below the
delta-rule BSC baseline at the same N. Specifically:
- At N=4096: gradient best ≤ 2.43 (vs delta baseline 2.4817)
- At N=8192: gradient best ≤ 2.38 (vs delta baseline 2.4344)

**Reject:** Gradient best is within ±0.02 bpc of delta baseline.
Delta rule is already near-optimal at our scale; bottleneck is
representational (atoms, depth, attention) not optimizational.

**Strong support:** Gradient best ≤ 2.30 at N=4096, which would put us
clearly past the tiny-transformer baseline (2.39).

## Pre-mortem (top 3 failure causes)

1. **LR sweep too narrow.** AdamW's optimal LR for this setup is unknown.
   Sweep {3e-3, 1e-2, 3e-2} is geometric over an order of magnitude; the
   true optimum could be 1e-3 or 1e-1. Mitigation: if all three are
   roughly similar, broaden to {1e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1}.

2. **Gradient explosion / numerical instability.** Cross-entropy on
   softmax of dot products can have extreme gradients early in training
   when W is near-zero. Mitigation: AdamW's normalization handles this in
   most cases; if W norm explodes, add gradient clipping at 1.0.

3. **Frozen atoms become the bottleneck.** If gradient gain is small,
   it confirms that representational learning (Wave 4.6 — learnable atom
   offsets) is the real path to closing the gap. The audit's predicted
   0.10-0.25 bpc gain assumes some headroom in W; if delta rule is
   already at the same local minimum, headroom is zero.

## Parameter-matched non-bio control

Two are built into this experiment:
1. **Delta-rule baseline run** for each N (matches our prior BSC results
   2.4817 / 2.4344). Direct A/B against gradient variant.
2. **||W||** is tracked per epoch. If gradient W converges to drastically
   different ||W||, that diagnoses whether they're finding different
   solutions geometrically.

## Expected wall time

- Delta-rule reference: ~25-100s per N (matches prior runs)
- Gradient sweep: 3 LRs × ~30-120s each per N = 90-360s per N
- Total: ~5-10 min for both Ns

Gradient computation adds maybe 1.5-2× per epoch vs the manual delta rule
(autograd overhead + AdamW state). Not bandwidth-bound.

## What this tells us about the bigger story

If gradient W wins by 0.10+: the delta rule is leaving real perplexity on
the table. The Schlag-Irie 2021 theorem is empirically vindicated for our
setup. Strongly motivates Wave 4.6 (learnable atoms) and Wave 6.5
(Schlag-Irie hybrid).

If gradient W loses or ties: the bottleneck is NOT in W optimization.
The delta rule already finds a near-optimal W given fixed random atoms.
Wave 4.6 (learnable atoms) becomes the next critical test — the gap is
representational, not optimizational.

Either outcome is informative and shapes Wave 4.6/6.5 design.
