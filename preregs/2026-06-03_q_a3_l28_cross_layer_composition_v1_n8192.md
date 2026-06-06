# Prereg: q_a3_l28_cross_layer_composition_v1_n8192

**Date:** 2026-06-03
**Anchor:** q_a3_l28_cross_layer_composition_v1_n8192
**Script:** experiments/exp_q_a3_l28_cross_layer_composition_v1_n8192.py
**Queue:** overnight_queue (GPU)
**Cap_map row:** PP-12 / Q-A3 cross-layer composition

## Context

N=8192 series: L=19, L=22..L=27 = 7 rungs all EXACT-1.0000 (v367 recent L=27 completed).
L=28 is the 8th rung in the N=8192 depth ladder.

## Hypothesis

Cross-layer composition fidelity remains EXACT-1.0000 at L=28 N=8192 (5-seed, full).
Theory: EXACT-1.0 algebraic property is N-independent through at least L=28 (established for N=4096 and N=16384 at L=28+).

## Pre-registered bands

- **HARD-PASS:** all 28 level fidelities >= 0.9999 unanimous (5/5 seeds) AND l28_acc >= 0.5.
- **MIDDLE:** any L_fid in [0.85, 0.9999) OR graceful degradation.
- **HARD-FAIL:** any L_fid < 0.85 OR l28_acc < 0.5.

## Formula self-tests (PROT-022)

1. L=28 chain: 27-ctx Hadamard roundtrip recovers xi_L1.
   [INPUT: 2-element +-1 vectors, 27 context ops] [EXPECTED: decode = xi_L1 exactly]
2. Capacity check: M_INNER=100, N=8192 -> alpha=0.0122 < alpha_c=0.138.
3. GPU memory > 0 (remote runner).
4. M_MID length = 26 entries for L2..L27 + M_OUTER L28 = 28 total = L_DEPTH. (Script assertion.)

## PROT-018

Anchor _n8192; N=8192 in production config. Script grep: `N = 8192`. Binding confirmed.

## PROT-021

run_mode=full, n_seeds=5. Seed checkpoints keyed with run_mode + L.

## Timeout estimate

L=27 N=8192 elapsed ~2.84s (5-seed full). L=28 near-linear.
ceil(1.5 * 3 * (28/27) * 1.0) = ceil(4.67) = 300s.
**timeout_s = 300**

## Ship rationale

PP-12/Q-A3 N=8192 cross-N gap extension; 8th N=8192 rung; 2-N cross-N at L=28 {N=4096+N=8192}.
N=8192 series bridges gap toward N=16384 frontier (currently L=47). No upstream dependencies.
Script structurally identical to L=27 N=8192 with L+1 increment.
