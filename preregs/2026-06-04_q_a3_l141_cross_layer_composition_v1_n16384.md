# Prereg: q_a3_l141_cross_layer_composition_v1_n16384

## Anchor
q_a3_l141_cross_layer_composition_v1_n16384

## Priority
B (cycle 52 ladder continuation L=141 N=16384; PP-12/Q-A3 saturated 0.97, statistical confirmation of unbounded composition)

## Scientific question
Does cross-layer composition fidelity remain EXACT-1.0 at L=141 N=16384?
ECC theory predicts UNLIMITED depth when per-stage alpha = 100/16384 = 0.0061 << alpha_c=0.138.

## Pre-registered bands
HARD-PASS: all 141 level fidelities >= 0.9999 unanimous (5/5 seeds) AND l141_acc >= 0.5.
MIDDLE: any L_fid in [0.85, 0.9999) OR graceful degradation pattern.
HARD-FAIL: any L_fid < 0.85 OR l141_acc < 0.5.

## Formula self-tests (PROT-022)
1. Capacity: M_INNER=100, N=16384 -> alpha=0.0061 < alpha_c=0.138. [EXPECTED: True]
2. M_MID length == L_DEPTH - 2 == 139. [INPUT: L_DEPTH=141] [EXPECTED: len(M_MID)=139]
3. L=141 chain: 140-ctx Hadamard roundtrip recovers xi_L1. [EXPECTED: exact]

## N-suffix binding (PROT-018)
anchor _n16384; production N = 16384. Script constant N = 16384.

## Timeout estimate
PROT-019 floor applied: timeout_s = 21600.

## Smoke gate
--skip-smoke: no local CUDA. Structurally identical to EXACT ladder series (generated from gen_qa3_scripts.py, same template as L=137/L=101 HARD_PASS).

## Queue
overnight_queue (GPU required).
