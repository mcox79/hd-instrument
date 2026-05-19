# MIR-loses-to-random — research agent synthesis

Returned 2026-05-19. Deep unbiased survey on why our MIR result lost
to random replay by 0.02 bpc.

## TL;DR

**Our result is non-informative about MIR-the-mechanism.** We were 4
axes off from Aljundi's published regime. The clean falsifier is the
canonical recipe — deterministic top-K, re-score every batch, ~10-20%
replay, single-pass Phase B.

## What we tested vs canonical MIR

| Aspect | Aljundi 2019 canonical | Our first MIR | Risk |
|---|---|---|---|
| Selection | deterministic top-K | top-4K-then-random | **HIGH** — diluted signal 4x |
| Re-scoring | every batch | every 5 batches (cached) | **MEDIUM** — staleness |
| Replay ratio | 1:1 (small B=10) | 32:64 = 50% | **HIGH** — over-saturation |
| Training schedule | single-pass stream | 15-epoch cycling | **HIGH** — regime mismatch |
| Virtual update | single SGD step, actual lr | rank-1 delta update | LOW (mathematically equivalent) |
| Loss | cross-entropy on logits | byte-LM cross-entropy via cosine softmax | MEDIUM |

## Where MIR wins in literature (Aljundi 2019 NeurIPS)

| Benchmark | ER (reservoir random) | ER-MIR | Δ |
|---|---|---|---|
| Split MNIST | 86.8% | 87.4% | +0.6% |
| Permuted MNIST | 80.1% | 80.4% | +0.3% |
| Split CIFAR-10 (M=100) | 41.3% | 47.6% | **+6.3%** |
| Split CIFAR-10 (M=20) | 27.5% | 29.8% | +2.3% |

Big wins (+6.3%) appear on ResNet-18 + CIFAR-10 + single-pass.
Small wins (<1%) on MNIST. **Our 0.02 bpc gap is well within MNIST-scale
noise.**

## When MIR fails in literature

- **Buzzega DER++ 2020:** reservoir random + logit distillation beats
  prioritization-only on Seq-CIFAR-10/Tiny-ImageNet
- **Chaudhry tiny-memory 2019:** uniform-random ER beats GEM, A-GEM,
  EWC, iCaRL at 1 example/class
- **Mai OCL survey 2021:** MIR wins on *larger-scale*; iCaRL wins at
  small memory; GDumb wins at medium
- **CLOPS 2020 (physio):** MIR doesn't dominate outside vision
- **Bricken SDM 2023:** sparse substrates need no prioritization
  baseline random replay saturates

Pattern: MIR wins scale with (a) network capacity / non-linearity,
(b) single-pass severity, (c) dataset scale.

## Substrate-specific mechanisms for our failure

- **Rank-1 delta-rule** — scores barely move under virtual update
  (~1/N = 0.0002 per coord); top-K is mostly tie-breaks
- **BSC ±1 geometry** — "interference neighborhood" is Hamming-bounded;
  MIR concentrates replay on already-correct entries (anti-pattern)
- **Pool 1024 vs typical 200-500** — uniform sampling hits diverse
  modes; marginal value of top-K decreases
- **50% replay** — over-saturation; MIR's marginal interference signal
  doesn't matter when 1/3 of every gradient is buffer-derived
- **15 epochs cycling** — biggest mismatch. Every sample seen ~7×;
  per-step interference signal averages over cycle. MIR's mechanism
  vanishes.

## Five rescues, ordered by information value

1. **Pure deterministic top-K** (drop top-4K-random subsample) -
   only change that restores canonical recipe. **HIGHEST INFORMATION.**
2. **Re-score every batch** (cached freq = 1 instead of 5)
3. **Single-pass Phase B** (1 epoch instead of 15 cycling) - biggest
   regime restoration
4. **Lower replay fraction** (10-20% instead of 50%)
5. **Combined MIR+random hybrid** — cheapest hedge

**Minimal faithful re-test:** #1 ∧ #2 ∧ #3 simultaneously. That is
the literature-faithful canonical MIR. If THAT loses to random, the
substrate is the issue.

## Honest bottom line

**The replay-prioritization door is NOT closed** for this substrate.
The evidence for closing it is weaker than the R7 verdict text claims.

What we actually showed: soft-MIR + stale cache + 50% replay + 15
epochs cycling, fails to beat random by 0.02 bpc.

What the literature predicts MIR should beat random on: deterministic
top-K, re-scored every batch, ~10-20% replay, single-pass, high-capacity
non-linear model with smooth gradient geometry.

We are 4 axes off. The 0.02 bpc gap is uninformative.

**Genuinely closed:** static prioritization (concept tags). R7+F1
settled that. Dynamic priority has one clean falsifier remaining
(rescue #1+2+3, ~1h GPU), and until that runs, claiming the door is
closed is overextending Buzzega/Chaudhry "tiny-memory random wins"
to a multi-epoch substrate where neither paper tested.

## Sources

- [Aljundi MIR 2019 arXiv:1908.04742](https://arxiv.org/abs/1908.04742)
- [MIR codebase optimass GitHub](https://github.com/optimass/Maximally_Interfered_Retrieval)
- [Chaudhry tiny-memory ER 2019](https://arxiv.org/abs/1902.10486)
- [Buzzega DER++ 2020](https://arxiv.org/abs/2004.07211)
- [Aljundi GSS 2019 NeurIPS](https://proceedings.neurips.cc/paper/2019/file/e562cd9c0768d5464b64cf61da7fc6bb-Paper.pdf)
- [Mai OCL empirical survey 2021](https://arxiv.org/abs/2101.10423)
- [Bricken SDM CL 2023](https://arxiv.org/abs/2303.11934)
- [Hebbian descent unified view](https://direct.mit.edu/neco/article/36/9/1669/124060/Hebbian-Descent-A-Unified-View-on-Log-Likelihood)
