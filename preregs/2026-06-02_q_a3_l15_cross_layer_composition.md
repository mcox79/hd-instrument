# Prereg: q_a3_l15_cross_layer_composition_v1_n4096

**Date:** 2026-06-02
**Anchor:** q_a3_l15_cross_layer_composition_v1_n4096
**Queue:** overnight_queue
**N:** 4096, **Seeds:** 5 (7, 17, 23, 31, 41)

## Hypothesis
Q-A3 cross-layer hierarchical composition maintains EXACT-1.0 fidelity at L=15 (15 Hopfield levels, Hadamard-bound). Ceiling chase from L=14 HARD_PASS (cycle 16, all fids = 1.0000, 5-seed unanimous).

## Pre-registered Bands
- **HARD-PASS:** all 15 level fidelities >= 0.9999 (EXACT-1.0 unanimous, 5/5 seeds)
- **MIDDLE:** any L_fid in [0.85, 1.0)
- **HARD-FAIL:** any L_fid < 0.85 OR l15_acc < 0.5
- **Calibration:** L1-L14 all EXACT-1.0 through L=14. Hadamard binding is algebraically exact when alpha << alpha_c; all 15 levels are well sub-capacity (M_inner/N=100/4096=0.024 << 0.138). HP bands unchanged from prior L cycles.

## N-suffix
PROT-018: production N=4096 matches anchor suffix _n4096.

## Timeout estimate
- Smoke N=512, seeds=2; FULL N=4096, seeds=5, scaling_exp=2.0 (15 W matrices, each N^2 matmul)
- Formula: ceil(1.5 * smoke_wall_s * (4096/512)^2.0 * (5/2))
- = ceil(1.5 * smoke_wall_s * 64 * 2.5) = ceil(240 * smoke_wall_s)
- Estimated smoke ~15s => timeout = ceil(240*15) = 3600s
- Actual timeout set per ship_anchor.py formula from measured smoke wall.
