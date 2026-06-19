# Prereg: q_a3_l59_cross_layer_composition_v1_n16384

**Date:** 2026-06-03
**Anchor:** q_a3_l59_cross_layer_composition_v1_n16384
**Script:** experiments/exp_q_a3_l59_cross_layer_composition_v1_n16384.py
**Queue:** overnight_queue (GPU)

## Hypothesis
Cross-layer composition fidelity remains EXACT-1.0 at L=59, N=16384 (40th rung in depth ladder).
Per ECC criterion: per-stage alpha < 0.0061 << alpha_c=0.138; depth UNLIMITED.

## Pre-registered bands (pre-registered before any run)
- **HARD-PASS**: all 59 level fidelities >= 0.9999 unanimous (5/5 seeds) AND l59_acc >= 0.5
- **MIDDLE**: any L_fid in [0.85, 0.9999) OR graceful degradation
- **HARD-FAIL**: any L_fid < 0.85 OR l59_acc < 0.5

## Smoke result (gate run 2026-06-03)
- Mode: smoke (N_active=512, 2 seeds)
- Verdict: HARD_PASS smoke (all 59 levels 1.0000, l59_acc=1.0000)
- Wall: ~0.20s per seed
- GPU memory: 0.011 GB peak

## Timeout estimate
- Prior L=57 elapsed ~35s (5-seed FULL). L=59 near-linear: ~39s.
- ceil(1.5 * 39 * 1) = 59s -> use PROT-019 safety floor: 21600s.

## N-suffix binding
PROT-018: _n16384 suffix -> N = 16384 in FULL config. Verified.

## Dependencies
None beyond existing experiments/_seed_checkpoint.py (verified present).
