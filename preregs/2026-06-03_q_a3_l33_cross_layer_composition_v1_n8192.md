# Prereg: q_a3_l33_cross_layer_composition_v1_n8192

**Date:** 2026-06-03
**Anchor:** q_a3_l33_cross_layer_composition_v1_n8192
**Script:** experiments/exp_q_a3_l33_cross_layer_composition_v1_n8192.py
**Queue:** overnight_queue (GPU)

## Hypothesis
Cross-layer composition fidelity remains EXACT-1.0 at L=33, N=8192 (13th rung in N=8192 ladder).
Establishes 2-N cross-N {N=4096+N=8192} at L=33 (N=4096 already passed L=33).

## Pre-registered bands (pre-registered before any run)
- **HARD-PASS**: all 33 level fidelities >= 0.9999 unanimous (5/5 seeds) AND l33_acc >= 0.5
- **MIDDLE**: any L_fid in [0.85, 0.9999) OR graceful degradation
- **HARD-FAIL**: any L_fid < 0.85 OR l33_acc < 0.5

## Smoke result (gate run 2026-06-03)
- Mode: smoke (N_active=512, 2 seeds)
- Verdict: HARD_PASS smoke (all 33 levels 1.0000, l33_acc=1.0000)
- Wall: ~0.13s per seed
- GPU memory: 0.011 GB peak

## Timeout estimate
- Prior L=32 N=8192 elapsed ~5s (5-seed FULL). L=33 near-linear: ~6s.
- ceil(1.5 * 6 * 1) = 9s -> use PROT-019 safety floor: 21600s.

## N-suffix binding
PROT-018: _n8192 suffix -> N = 8192 in FULL config. Verified.

## Dependencies
None beyond existing experiments/_seed_checkpoint.py (verified present).
