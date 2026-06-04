# Prereg: substrate_preloaded_icl_rung1_tinychar_v1

**Date:** 2026-06-04
**Routing:** Phase B rung-1 (overnight batch 2026-06-03, Section 3)
**Queue:** remote_cpu_queue
**Script:** experiments/exp_substrate_preloaded_icl_rung1_tinychar_v1.py

## Scientific Question

Does pre-loading K char-pair bindings into a substrate improve held-out char-pair completion accuracy versus no-substrate baseline?

## Design

- Substrate: N=256 bipolar, Hebbian-written with K (ctx, nxt) char-pair bindings (VSA bind = elem product)
- Conditions: K in [0, 10, 100, 1000]
- Eval: 2000 held-out char bigrams from wikitext2 validation
- Metric: top-1 accuracy (correct next-char prediction)
- 3 seeds per K condition

## N-suffix declaration (PROT-018)

No `_nN` suffix. PRODUCTION_N=256 declared. N is not a primary sweep axis.

## Pre-registered Bands

- **HARD-PASS:** K=100 or K=1000 beats K=0 by > 10% accuracy AND 3/3 seeds
- **MIDDLE:** 5-10% gain
- **HARD-FAIL:** K=100 and K=1000 both match or trail K=0

## Timeout estimate

Smoke: 0.05s total (4 cells, pure numpy)
FULL: 4 K-values x 3 seeds = 12 cells, N=256 vs N=64
`timeout_s = ceil(1.5 * 0.05 * (12/4) * (256/64)^1.0) = ceil(1.5 * 0.05 * 3 * 4) = ceil(0.9) -> 300s`
Conservative: **timeout_s = 600**

## Smoke Result (2026-06-04)

- HARD_FAIL at smoke (K=10 acc=1.25% vs K=0 acc=0.5%, gain=0.75%)
- Expected at tiny N=64, few eval pairs: bipolar retrieval at N=64 has very low SNR
- Instrumentation selftest PASSED (codebook shapes, joint self-retrieval cos=1.0, acc in [0,1])
- Wall: 0.05s smoke
