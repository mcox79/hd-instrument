# Prereg: q_a3_l152_cross_layer_composition_v1_n16384

## Anchor
q_a3_l152_cross_layer_composition_v1_n16384

## Priority
B (cycle 54 ladder continuation past actual frontier)

## Scientific question
Does cross-layer composition fidelity remain EXACT-1.0 at L=152 N=16384?
ECC theory predicts UNLIMITED depth when per-stage alpha = 100/16384 = 0.0061 << alpha_c=0.138.

## Pre-registered bands
HARD-PASS: all 152 level fidelities >= 0.9999 unanimous (5/5 seeds) AND l152_acc >= 0.5.
MIDDLE: any L_fid in [0.85, 0.9999) OR graceful degradation pattern.
HARD-FAIL: any L_fid < 0.85 OR l152_acc < 0.5.

## Formula self-tests (PROT-022)
1. Capacity: M_INNER=100, N=16384 -> alpha=0.0061 < alpha_c=0.138. [EXPECTED: True]
2. M_MID length == L_DEPTH - 2 == 150. [INPUT: L_DEPTH=152] [EXPECTED: len(M_MID)=150]
3. L=152 chain: 151-ctx Hadamard roundtrip recovers xi_L1. [EXPECTED: exact]

## N-suffix binding (PROT-018)
anchor _n16384; production N = 16384. Script constant N = 16384.

## Timeout estimate
PROT-019 floor applied: timeout_s = 21600.

## Smoke gate
--skip-smoke: no local CUDA. Remote --self-test gates chain decode + capacity. gen_qa3_scripts.py template (same as L=137/L=101 HARD_PASS).

## Queue
overnight_queue (GPU required).
