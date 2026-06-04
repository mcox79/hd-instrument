# Prereg: phase05_v1_algorithm1_debug_pythia160m_v1

**Date:** 2026-06-04
**Routing:** Phase 0.5 rung-0 debug (change_request_phase05_v1_final_8gb_4060ti_2026-06-03.md)
**Queue:** overnight_queue (remote GPU; Pythia-160M needs transformer forward passes)
**Script:** experiments/exp_phase05_v1_algorithm1_debug_pythia160m_v1.py

## Scientific Question

Does Algorithm 1 (arXiv:2509.25045 Appendix B) run cleanly on Pythia-160M (12 layers)? Engineering correctness gate before any Llama compute cycles.

## Pipeline

1. Load Pythia-160M (12 layers, hidden=768, ~320MB)
2. Collect final-token residuals from layers 6-12 (latter half = 7 layers)
3. K-means (k=5) over 7 layer-residuals -> (5, 768) centroids
4. Sum-pool -> (768,) embedding
5. Sign() -> bipolar code {-1,+1}^768
6. Train tiny MLP probe (synthetic target) to verify convergence

## N-suffix declaration (PROT-018)

No `_nN` suffix. Substrate dim = Pythia hidden_dim = 768 (not a sweep variable). Production declared explicitly.

## Pre-registered Bands (IMPLEMENTATION CORRECTNESS GATE)

- **HARD-PASS:** pipeline runs cleanly (no NaN, no shape errors) AND bipolar balance |mean(xi)| < 0.7 AND embedding pairwise diversity > 0.1 AND probe converges (val_loss decreasing) across 3/3 seeds
- **MIDDLE:** pipeline runs but probe flat/noisy (implementation has subtle bugs, iterate at rung-0)
- **HARD-FAIL:** pipeline crashes OR NaN in embeddings OR zero-diversity codes

This is NOT a product claim gate; it is an engineering implementation correctness gate.

## Timeout estimate

Smoke: 4.6s (2 seeds, Pythia loaded, 20 epochs x 2 seeds)
FULL: 3 seeds, 80 epochs
`timeout_s = ceil(1.5 * 4.6 * (80/20) * (3/2)) = ceil(1.5 * 4.6 * 4 * 1.5) = ceil(41.4) -> 300s`
Conservative with GPU model load + document extraction overhead: **timeout_s = 3600**

## Smoke Result (2026-06-04)

- MIDDLE_BAND at smoke scale (2/2 seeds converged; HP requires 3/3; only 2 seeds in smoke)
- balance_mean=0.006 (well within HP threshold 0.7)
- diversity_mean=0.56 (well above HP threshold 0.1)
- pipeline_clean=True, nan_frac=0
- Model loading ~1s on CPU; GPU will be faster
- Instrumentation selftest PASSED (all 6 assertions)
- Wall: 4.6s smoke (CPU)
