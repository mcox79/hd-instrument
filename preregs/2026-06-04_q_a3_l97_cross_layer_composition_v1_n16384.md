# Prereg: q_a3_l97_cross_layer_composition_v1_n16384

## Anchor
q_a3_l97_cross_layer_composition_v1_n16384

## Priority
A (cycle 45 all-night burst, ladder continuation L=97 N=16384, rung 78)

## Scientific question
Does cross-layer composition fidelity remain EXACT-1.0 at L=97 N=16384?
ECC theory predicts UNLIMITED depth when per-stage alpha = 100/16384 = 0.0061 << alpha_c=0.138.

## Pre-registered bands
HARD-PASS: all 97 level fidelities >= 0.9999 unanimous (5/5 seeds) AND l97_acc >= 0.5.
MIDDLE: any L_fid in [0.85, 0.9999) OR graceful degradation pattern.
HARD-FAIL: any L_fid < 0.85 OR l97_acc < 0.5.

## Formula self-tests (PROT-022)
1. L=97 Hadamard chain decode: [INPUT: 2-elem +-1 vectors, 96 context ops] [EXPECTED: decode = xi_L1 exactly]
2. Capacity: M_INNER=100, N=16384 -> alpha=0.0061 < alpha_c=0.138. [EXPECTED: True]
3. GPU memory > 0 after W build. [EXPECTED: allocated > 0]
4. M_MID length == L_DEPTH - 2 == 95. [INPUT: L_DEPTH=97] [EXPECTED: len(M_MID)=95]

## N-suffix binding (PROT-018)
anchor _n16384; production N = 16384. Script constant N = 16384.

## Timeout estimate
PROT-019 floor applied: timeout_s = 21600.

## Smoke gate
--skip-smoke: no local CUDA. Structurally identical to EXACT series L=20..L=96.

## Queue
overnight_queue (GPU required).
