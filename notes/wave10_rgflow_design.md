# Wave 10: RG-flow hierarchical HDC — Design

Reference: substrate audit, 2026-05-18. The audit's verdict:
"This is the most directly relevant non-VSA idea for your 'depth without
backprop' question. Wilsonian fixed points = trained layers."

Citation: Berman & Klinger 2024 *Bayesian RG Flow in Neural Network
Field Theories* (arXiv:2405.17538). Maps NN depth to renormalization-
group scale.

## The RG-flow intuition

In statistical physics, the renormalization group describes how
physical theories change as you zoom out (coarse-grain). Each "scale"
corresponds to a different effective description. Wilsonian fixed
points are theories invariant under further coarse-graining.

Translated to NN: each layer is a coarse-graining operation, and
trained-to-completion layers approximate fixed points. **Depth =
scale**, and the key property is that each layer's update can be
local (only depending on its own input and its next-layer target),
not global like backprop.

## Wave 10 implementation strategy (3 phases)

### Phase A (this prototype): "Naive 2-layer Hebbian feedforward"

The simplest test: does adding a second Hebbian-trained layer help at
all? No backprop, no coarse-graining, no RG-formal training rule —
just two layers of delta-rule W stacked.

- Layer 0: standard combined+modReLU baseline. W_0 trained by delta
  rule on (ctx → byte target).
- Hidden: h = modReLU(W_0 @ ctx).
- Layer 1: W_1 trained by delta rule on (h → byte target).
- Combined prediction at test: alpha_layer · P_W1 + (1-alpha_layer) · P_W0
  + pool head.

Each layer is trained locally — Layer 1 sees Layer 0's frozen-during-
forward output, gradient does NOT flow through Layer 0.

This tests: **does naive 2-layer stacking with local Hebbian training
help at all?** If no, the RG-formal training rule (Phase B) is needed.
If yes, even the naive version delivers depth value.

Effort: ~1 day. Today's deliverable.

### Phase B: "Bayesian RG layer-wise training"

Per Berman/Klinger 2024:
- Each K_i (layer transition) is trained to maximize mutual information
  between layer-i features and layer-(i+1) features.
- MI estimator: closed-form Gaussian approximation
  I(X; Y) ≈ -0.5 · log det(Σ_X^{-1} Σ_XY Σ_Y^{-1} Σ_YX)
  Or use MINE-style neural MI estimator (overkill for prototype).
- W at each level still delta-rule trained on byte targets, but
  through the K_i-projected features.

Effort: ~1 week after Phase A is verified.

### Phase C: "True coarse-graining with reduced temporal resolution"

Per the actual RG analogy:
- Level 0: byte-level features at full temporal resolution
- Level 1: bigram-level features (every 2 byte positions merged)
- Level 2: 4-gram features
- Each level has its own W predicting its own coarse-grained target
- Combine predictions across levels

Effort: ~2 weeks. Requires defining coarse-grained targets cleanly.

## What we're testing per phase

| Phase | Tests | Expected payoff (vs single-layer BSC 2.4817) |
|---|---|---|
| A: naive 2-layer | Does stacking help at all? | 0.05-0.15 bpc improvement |
| B: Bayesian RG | Does formal RG training beat naive? | Additional 0.05-0.1 bpc |
| C: coarse-grained targets | Does multi-scale prediction help? | Highly uncertain (0.0-0.3) |

If Phase A delivers 0 bpc improvement, depth doesn't help at our scale
and Phase B/C are unlikely to either. Then Wave 10 → "depth is not the
bottleneck at N=4096 with 38KB data." Useful negative result.

If Phase A delivers 0.1+ bpc, push to Phase B.

## Falsification (Phase A)

Best 2-layer variant vs best single-layer baseline (BSC at 2.4817):
- Support if delta ≤ -0.05 (i.e., 2-layer ≤ 2.43)
- Reject if delta ≥ -0.02 (no meaningful improvement)
- Inconclusive in between
