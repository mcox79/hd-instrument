# Wave 10A RG-flow Phase A failure — research synthesis

Returned 2026-05-19. Unbiased deep research on the closed Wave 10A
negative (naive 2-layer Hebbian feedforward monotonically hurts bpc).

## Bottom line

**Naive 2-layer Hebbian is dead, and the literature predicts this dead.**
What's NOT dead:
- The RULE choice (delta-on-same-target) was the kill, not depth
- The SCALE was wrong (K=4 has no hierarchy for RG to coarse-grain)
- Phase B as written is underspecified (cites Berman-Klinger, but
  actionable algorithm is Koch-Janusz/Lenggenhager 2018-2020)

## Literature consensus

Stacking Hebbian layers with a purely local delta rule on the same
global target **almost never works**. Depth-2 only adds value with
ONE of:

| Method | Local rule | What makes depth-2 work |
|---|---|---|
| Krotov-Hopfield 2019 (PNAS) | Anti-Hebbian WTA | Hidden = unsupervised competition; classifier on top sees labels |
| SoftHebb (Journé 2022) | Soft-WTA + anti-Hebbian | Each layer is Bayesian WTA on its own output, no target propagation |
| Whittington-Bogacz 2017 | Local Hebbian on error neurons | Error neurons carry prediction-residual; approximates backprop |
| Difference target prop (Lee+Bengio 2014) | Local layer update toward target | Separate inverse net generates per-layer targets |
| Greedy layer-wise pretrain (Bengio 2007) | Per-layer reconstruction | Each layer is autoencoder, signal is "reconstruct your input" |

**Our config (delta-rule-on-modReLU'd-output-toward-same-target) was
the worst possible.** Every working method either (a) replaces the
layer-2 objective, (b) supplies a per-layer target, or (c) trains
layer-2 to reconstruct layer-1.

## Why alpha=1.0 gave 3.92 bpc (unigram floor)

Three compounding issues:
1. **Semi-positive collapse** — modReLU bias=0.5 zeros half coords;
   Layer 1's input is sparse non-negative low-rank
2. **Target mismatch** — Layer 1's input is in Layer 0's output space;
   predicts via similarity to byte_atoms (original input basis)
3. **No anti-Hebbian / no competition** — all W_1 rows collapse to
   dominant target direction (most frequent byte)

Result is consistent with predicting the unigram distribution.

## Berman-Klinger 2024 actually

Their paper is NOT a learning algorithm — it's a duality between
Bayesian RG and NN field theory parameter-space flow. The actionable
form of RG-flow Hebbian is **Koch-Janusz/Lenggenhager 2018-2020**
(mutual-information real-space RG): train K_i to maximize
I(layer_i features ; layer_{i+1} features) conditional on target
relevance. Structurally identical to a **deep information bottleneck**,
not delta-rule-on-target.

## Five rescues (each <1h GPU)

1. **Krotov-WTA Layer 1** (highest-prior). Train W_1 unsupervised
   with soft-WTA + negative update on non-winners; Layer 1 as features
   for small readout. ~30 min.
2. **Reconstruction-target Layer 1** (Bengio autoencoder pretrain).
   Layer 1 predicts ctx from h via reconstruction loss. ~45 min.
3. **Predictive-coding Layer 1** (Whittington-Bogacz). W_1 on
   (h, target − Wh) error neurons. ~1h.
4. **Linear (no modReLU) Layer 1**. Sanity check: is failure
   rank/nonlinearity or rule? ~20 min.
5. **Koch-Janusz MI surrogate**. Train W_1 to maximize Gaussian-MI
   proxy. ~1h.

**Cheap combined ablation**: #4 + #1 (linear + WTA) in one experiment.
If best ≤ 2.46 bpc: depth is salvageable, warrants Phase B build.
If ≥ 2.48 bpc: declare 2-layer Hebbian at K=4/N=4096 dead and pivot
Wave 10 directly to Phase C with coarse-grained targets at K≥16.

## K=4 scale-separation issue

Byte context at K=4 is information-thin (~32 effective bits, 256
target alphabet). Layer 0 at N=4096 already over-parameterizes. No
hierarchy of scales for RG to traverse — which is exactly what RG
needs. Krotov/SoftHebb depth gains appear at K≥CIFAR-tile (thousands
of context bits).

**Honest read**: at K=4 with N=4096, depth is **theoretically
unmotivated**. A real test of RG-flow Hebbian needs K≥16 with
bigram/4-gram coarse targets.

## Sources

- [Krotov-Hopfield Unsupervised hidden units PNAS 2019](https://www.pnas.org/doi/10.1073/pnas.1820458116)
- [Journé SoftHebb ICLR 2023 (arXiv:2209.11883)](https://arxiv.org/abs/2209.11883)
- [Whittington-Bogacz predictive coding local Hebbian Neural Comp 2017](https://www.semanticscholar.org/paper/An-Approximation-of-the-Error-Backpropagation-in-a-Whittington-Bogacz/c124a6aec4b1833e4e86092e20a782183349d57e)
- [Lee-Bengio difference target propagation (arXiv:1412.7525)](https://arxiv.org/abs/1412.7525)
- [Bengio greedy layer-wise pretraining NeurIPS 2006](https://www.iro.umontreal.ca/~lisa/pointeurs/BengioNips2006All.pdf)
- [Howard-Klinger Bayesian RG NN field theories 2024](https://arxiv.org/abs/2405.17538)
- [Koch-Janusz-Ringel mutual-info RG Nature Phys 2018](https://arxiv.org/abs/1809.09632)
- [Lenggenhager optimal RG transformation PRX 2020](https://doi.org/10.1103/PhysRevX.10.011037)
- [Krotov-Hopfield Large Associative Memory NeurIPS 2020](https://ar5iv.labs.arxiv.org/html/2008.06996)
