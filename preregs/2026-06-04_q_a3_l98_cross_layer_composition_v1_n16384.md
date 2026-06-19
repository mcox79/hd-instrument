# Prereg: q_a3_l98_cross_layer_composition_v1_n16384

## Anchor
q_a3_l98_cross_layer_composition_v1_n16384

## Priority
B (cycle 45 all-night burst, ladder continuation L=98 N=16384, rung 79)

## Scientific question
Does cross-layer composition fidelity remain EXACT-1.0 at L=98 N=16384?
ECC theory predicts UNLIMITED depth when per-stage alpha = 100/16384 = 0.0061 << alpha_c=0.138.

## Pre-registered bands
HARD-PASS: all 98 level fidelities >= 0.9999 unanimous (5/5 seeds) AND l98_acc >= 0.5.
MIDDLE: any L_fid in [0.85, 0.9999) OR graceful degradation pattern.
HARD-FAIL: any L_fid < 0.85 OR l98_acc < 0.5.

## Formula self-tests (PROT-022)
1. Capacity: M_INNER=100, N=16384 -> alpha=0.0061 < alpha_c=0.138. [EXPECTED: True]
2. M_MID length == L_DEPTH - 2 == 96. [INPUT: L_DEPTH=98] [EXPECTED: len(M_MID)=96]

## N-suffix binding (PROT-018)
anchor _n16384; production N = 16384. Script constant N = 16384.

## Timeout estimate
PROT-019 floor applied: timeout_s = 21600.

## Smoke gate
--skip-smoke: no local CUDA. Structurally identical to EXACT series L=20..L=97.

## Queue
overnight_queue (GPU required).
