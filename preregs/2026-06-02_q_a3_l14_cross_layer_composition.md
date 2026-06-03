# Pre-registration: q_a3_l14_cross_layer_composition_v1_n4096

**Date:** 2026-06-02
**Anchor:** q_a3_l14_cross_layer_composition_v1_n4096
**Queue:** overnight_queue
**N:** 4096, **Seeds:** 5, **L-depth:** 14

## Scientific question
Does cross-layer composition remain at exact fidelity 1.0000 at L=14? Cycle-15 L=13 HARD_PASS with all fidelities EXACT-1.0000. Pushing to L=14 to find degradation onset.

## Pre-registered bands

**HARD-PASS:**
- All 14 level fidelities >= 0.9999 (unanimous 5/5 seeds)
- l14_acc >= 0.5

**MIDDLE:** any L_fid in [0.85, 1.0).

**HARD-FAIL:** any L_fid < 0.85 OR l14_acc < 0.5.

## Calibration rationale
All L=2..L=13 showed EXACT-1.0 fidelity at N=4096 (13 confirmed sub-properties). Mechanism: each Hadamard binding is invertible when W_k is in basin. At L=14 M_outer=2 (minimum floor per geometric-decay scheme); alpha at each level remains << 0.138. HP unchanged from prior L series.

## N-suffix section
Anchor _n4096; production N = 4096; scripts enforce N = _N_SUFFIX = 4096.

## Timing estimate
Reference: q_a3_l12_cross_layer_composition elapsed=0.59s at N=4096 5-seed; L=13 was ~0.64s. L=14 adds one more level. Formula: ceil(1.5 * 0.64 * 1.08 * 1.0) = ceil(1.04) = 300s minimum.
Smoke skipped (GPU-only; no local GPU; timing from bridge reference).
timeout_s = 300
