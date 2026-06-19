# Prereg: q_a3_l58_cross_layer_composition_v1_n16384

**Date:** 2026-06-03
**Anchor:** q_a3_l58_cross_layer_composition_v1_n16384
**Script:** experiments/exp_q_a3_l58_cross_layer_composition_v1_n16384.py
**Queue:** overnight_queue (GPU)

## Hypothesis
Cross-layer composition fidelity remains EXACT-1.0 at L=58, N=16384 (39th rung in depth ladder).
Per ECC criterion: per-stage alpha < 0.0061 << alpha_c=0.138; depth UNLIMITED.

## Pre-registered bands (pre-registered before any run)
- **HARD-PASS**: all 58 level fidelities >= 0.9999 unanimous (5/5 seeds) AND l58_acc >= 0.5
- **MIDDLE**: any L_fid in [0.85, 0.9999) OR graceful degradation
- **HARD-FAIL**: any L_fid < 0.85 OR l58_acc < 0.5

## Smoke result (gate run 2026-06-03)
- Mode: smoke (N_active=512, 2 seeds)
- Verdict: HARD_PASS smoke (all 58 levels 1.0000, l58_acc=1.0000)
- Wall: ~0.18s per seed
- GPU memory: 0.011 GB peak

## Timeout estimate
- smoke_wall_s = 0.18, FULL_N/smoke_N = 16384/512 = 32, FULL_seeds/smoke_seeds = 5/2 = 2.5, scaling_exp = 1.5
- Prior L=57 elapsed ~35s (5-seed FULL). L=58 near-linear: ~37s.
- ceil(1.5 * 37 * 1) = 56s -> use PROT-019 safety floor: 21600s (queue default).

## N-suffix binding
PROT-018: _n16384 suffix -> N = 16384 in FULL config. Verified.

## Dependencies
None beyond existing experiments/_seed_checkpoint.py (verified present).
