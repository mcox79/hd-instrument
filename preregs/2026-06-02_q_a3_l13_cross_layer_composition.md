# Pre-registration: q_a3_l13_cross_layer_composition_v1_n4096

**Date:** 2026-06-02
**Anchor:** q_a3_l13_cross_layer_composition_v1_n4096
**Queue:** overnight_queue
**N:** 4096, **Seeds:** 5, **L-depth:** 13

## Scientific question
Does cross-layer composition remain at exact fidelity 1.0000 at L=13? All L through L=12 have shown 1.0000. Find degradation onset.

## Pre-registered bands

**HARD-PASS:**
- All 13 level fidelities >= 0.9999 (unanimous 5/5 seeds)
- l13_acc >= 0.5

**MIDDLE:** any L_fid in [0.85, 1.0).

**HARD-FAIL:** any L_fid < 0.85 OR l13_acc < 0.5.

## Calibration rationale
All prior L showed EXACT-1.0. Mechanism: each Hadamard binding is invertible iff W_k is in basin. At low alphas (M_k/N << 0.138 at each level) the retrieval is perfect. Degradation only expected when some W_k's alpha approaches critical. L=13's tightest level uses M=2/4096 = 0.00049 << 0.138 -- so HP expected. Bands set per prior L pattern.

## N-suffix section
Anchor _n4096; production N = 4096; scripts enforce N = _N_SUFFIX = 4096.

## Timeout estimate
L=12 smoke ~ 15s at N=512 smoke (L=13 is slightly more). FULL: N=4096, seeds=5.
formula: ceil(1.5 * 18 * (4096/512)^1.5 * (5/2)) = ceil(1.5 * 18 * 22.6 * 2.5) = ceil(1525) = 1800
timeout_s = 1800
