# Pre-registration: wave14n_decoder_bound (modern Hopfield capacity)

Date: 2026-05-20
Status: Pre-registered, gated
Experiment: [exp_wave14n_decoder_bound.py](../experiments/exp_wave14n_decoder_bound.py)

## Why

This is the highest-leverage capacity experiment in the synthesis. Three
research agents converged: our substrate is in the AGS Hopfield regime
(alpha_c=0.153 measured today). Hu 2023 (arXiv:2309.12673) proved that
swapping softmax retrieval for alpha-entmax gives **exp(N) capacity** with
provably tighter retrieval-error bound than dense Hopfield.

If true for our substrate, this is a 50x+ capacity multiplier with a single
decoder swap. That's the central product differentiator: same byte budget,
order-of-magnitude more stored facts.

## Hypothesis (H)

Sparsemax (alpha-entmax with alpha=2) gives K* at least 2x that of softmax
at N=4096, beta=1.0, 10% query corruption.

## Kill criterion

If sparsemax K*/softmax K* < 1.2, the predicted Hu 2023 capacity gain does
NOT materialize in our substrate regime, and the decoder swap is not the
central path forward. We then lean on alternatives (sparsity in coding,
structured codebooks, multi-bundle architecture).

## Cited mechanism

- Ramsauer 2020 arXiv:2008.02217 "Hopfield Networks Is All You Need" — modern
  Hopfield with softmax = transformer attention; exp(N) capacity in dense
  case for separated patterns
- Hu 2023 arXiv:2309.12673 "On Sparse Modern Hopfield" — alpha-entmax retrieval,
  tighter retrieval-error scaling
- Martins & Astudillo 2016 arXiv:1602.02068 — sparsemax closed-form projection
  onto simplex (alpha=2 entmax)

## Operational definition

Modern Hopfield retrieval:
- Stored: K random +/-1 patterns Xi in R^{K x N}
- Query: pattern_i with 10% bits flipped
- Scores: s = (Xi @ q) / sqrt(N)
- Weights: w = decoder(beta * s) where decoder in {softmax, sparsemax}
- Retrieved: r = w @ Xi
- Success: argmax over (Xi @ r) == i

K-grid: {100, 300, 600, 1000, 1500, 2200, 3000, 4500, 6500, 10000}
N=4096, beta=1.0, flip_frac=0.10
3 seeds, 30 trials per (K, seed)

K* per decoder via linear interp at recovery=0.5.
alpha_c = K* / N.

## Expected runtime

Smoke (N=512, K in {50,150,500}, 1 seed, 10 trials): ~10 sec.
Full (N=4096, K up to 10000, 3 seeds, 30 trials): ~2h on GPU.

## Verdict labels

- `SPARSEMAX_WINS`: ratio >= 2x (matches Hu 2023)
- `SPARSEMAX_WINS_BIG`: softmax never crossed 0.5 in grid
- `SPARSEMAX_MARGINAL`: ratio in [1.2, 2.0)
- `TIE`: ratio in [0.8, 1.2]
- `SOFTMAX_WINS`: ratio < 0.8 (contradicts theory)
- `ANOMALOUS`: only one decoder crossed 0.5
- `INCONCLUSIVE`: neither did

## What product decision this enables

WINS (>= 2x): Central product story. "Our memory tier supports 10,000+ facts
in 4096-bit byte budget via sparse Hopfield retrieval. Same physical footprint
as a vector DB shard, 10x the addressable memory."

MARGINAL: Real but smaller gain. Combine with sparsity in coding (Tsodyks-
Feigelman log(1/f)) and structured codebooks (Welch bound 2x) for compound
effect.

TIE/SOFTMAX_WINS: Decoder swap is not the lever; lean on other rescue paths
(sparse coding, structured codes, alternative architectures).
