# Prereg: substrate_trained_mini_lm_rung1_tinychar_v1

**Date:** 2026-06-04
**Routing:** Phase B rung-1 (overnight batch 2026-06-03, Section 3)
**Queue:** remote_cpu_queue
**Script:** experiments/exp_substrate_trained_mini_lm_rung1_tinychar_v1.py

## Scientific Question

Can a 2-layer char-LM be trained ENTIRELY via substrate operations (no gradient descent) and achieve BPC well below uniform on held-out text?

## Design

- Model: SubstrateCharLM (testbed.substrate_lm.char_lm), 2 layers, N=512, alpha_max=0.05
- Corpus: synthetic/wikitext2 char-level; 100k train chars, 20k val chars
- Substrate primitives: outer-product Hopfield write + anti-Hebbian + stacked composition
- Defensive: alpha_max=0.05 = 5% activity regime
- 3 seeds

## N-suffix declaration (PROT-018)

No `_nN` suffix. Production N = 512. Substrate dimensionality is not the load-bearing axis for this experiment (alpha budget is).

## Pre-registered Bands

- **HARD-PASS:** val BPC <= 2.5 nats AND no watchlist triggers AND 3/3 seeds
- **MIDDLE:** BPC 2.5-3.5 OR 2/3 seeds OR 1 watchlist trigger
- **HARD-FAIL:** BPC > 3.5 OR primitive collapse OR multiple watchlist triggers

Note: uniform baseline log2(~60 chars) ~ 5.9 nats. HP target 2.5 = ~42% of uniform.

## Watchlist triggers

- BPC_PLATEAU: val BPC std < 0.01 over last 5 snapshots
- W_NORM_GROWTH_LAYER_K: max_abs_eig > 3 * N per layer
- BPC_NEAR_CHANCE: val BPC > 0.95 * uniform

## Timeout estimate

Smoke: N=128, 2 seeds, 0.2s total
FULL: N=512, 3 seeds, scaling_exp=2.0 (outer-product matrix ops)
`timeout_s = ceil(1.5 * 0.1 * (512/128)^2 * (3/2)) = ceil(3.6) -> 600s`
Conservative: **timeout_s = 1800** (6x safety; outer-product at N=512 is the bottleneck per alpha_cap stopping early; production alpha-max will hit cap at ~26 writes * 4 layers = ~104 writes, 4x more than smoke).

## Smoke Result (2026-06-04)

- HARD_FAIL at smoke scale (N=128, alpha_max=0.05 -> only 7 writes before cap)
- This is expected: alpha budget at N=128 caps at 7 patterns before meaningful learning
- At N=512: 26 patterns per layer available; more meaningful learning expected
- Instrumentation selftest PASSED (n_pairs>0, bpc finite, plateau detection correct)
- Wall: 0.2s smoke
