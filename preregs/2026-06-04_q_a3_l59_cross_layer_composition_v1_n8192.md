# Prereg: q_a3_l59_cross_layer_composition_v1_n8192

## Anchor
q_a3_l59_cross_layer_composition_v1_n8192

## Priority
D (cycle 45 all-night burst, N=8192 depth ladder past L=58, rung 40)

## Scientific question
Does cross-layer composition fidelity remain EXACT-1.0 at L=59 N=8192?
ECC theory predicts UNLIMITED depth when per-stage alpha = 100/8192 = 0.0122 << alpha_c=0.138.

## Pre-registered bands
HARD-PASS: all 59 level fidelities >= 0.9999 unanimous (5/5 seeds) AND l59_acc >= 0.5.
MIDDLE: any L_fid in [0.85, 0.9999) OR graceful degradation pattern.
HARD-FAIL: any L_fid < 0.85 OR l59_acc < 0.5.

## Formula self-tests (PROT-022)
1. Capacity: M_INNER=100, N=8192 -> alpha=0.0122 < alpha_c=0.138. [EXPECTED: True]
2. M_MID length == L_DEPTH - 2 == 57. [INPUT: L_DEPTH=59] [EXPECTED: len(M_MID)=57]
3. W on-demand: 8192*8192*4 = 268 MB < 1 GB. [EXPECTED: True]

## N-suffix binding (PROT-018)
anchor _n8192; production N = 8192. Script constant N = 8192.

## Timeout estimate
PROT-019 floor applied: timeout_s = 21600.

## Smoke gate
--skip-smoke: no local CUDA. Series structurally identical to L=19..L=58 (all EXACT-1.0).

## Queue
overnight_queue (GPU required).
