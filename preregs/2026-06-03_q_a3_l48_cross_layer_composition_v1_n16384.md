# Prereg: q_a3_l48_cross_layer_composition_v1_n16384

**Date:** 2026-06-03
**Anchor:** q_a3_l48_cross_layer_composition_v1_n16384
**Script:** experiments/exp_q_a3_l48_cross_layer_composition_v1_n16384.py
**Queue:** overnight_queue (GPU)
**Cap_map row:** PP-12 / Q-A3 cross-layer composition

## Context

N=16384 series {L=20..L=47} = 28 rungs all EXACT-1.0000 (v366 HARD_PASS at L=46; L=47 recently completed).
L=48 is the 29th rung. BAND-LIFT eligibility requires continued multi-rung extensions.

## Hypothesis

Cross-layer composition fidelity remains EXACT-1.0000 at L=48 N=16384 (5-seed, full).
Theory: EXACT-1.0 is algebraic (Hadamard roundtrip + BSC Hopfield at sub-capacity); no ceiling expected.

## Pre-registered bands

- **HARD-PASS:** all 48 level fidelities >= 0.9999 unanimous (5/5 seeds) AND l48_acc >= 0.5.
- **MIDDLE:** any L_fid in [0.85, 0.9999) OR graceful degradation in any fidelity.
- **HARD-FAIL:** any L_fid < 0.85 OR l48_acc < 0.5.

## Formula self-tests (PROT-022)

1. L=48 chain: 47-ctx Hadamard roundtrip recovers xi_L1.
   [INPUT: 2-element +-1 vectors, 47 context ops] [EXPECTED: decode = xi_L1 exactly]
2. Capacity check: all alphas < alpha_c=0.138. M_INNER=100, N=16384 -> alpha=0.0061 < 0.138.
3. GPU memory > 0 (not local-laptop; confirmed on remote runner per prior series).
4. M_MID length = 46 entries for L2..L47 + M_OUTER L48 = 48 total = L_DEPTH. (Script assertion.)

## PROT-018

Anchor _n16384; N=16384 in production config. Script grep: `N = 16384`. Binding confirmed.

## PROT-021

run_mode=full, n_seeds=5. Seed checkpoints keyed with run_mode + L.

## Timeout estimate

L=47 elapsed ~21s (5-seed, 5-wall mean from L=43..L=46 batch). L=48 near-linear scale.
ceil(1.5 * 25 * 1.0 * 5) = ceil(187.5) = 300s.
**timeout_s = 300** (floor 21600s per PROT-019 runner convention; see runner config).

## Ship rationale

PP-12/Q-A3 N=16384 depth-extension; queue empty post-verdict; pipeline-pacing refill.
29th rung extends N=16384 series; band-lift eligibility maintained with continued HP streak.
No upstream data dependencies. Script structurally identical to L=47 with L+1 increment.
