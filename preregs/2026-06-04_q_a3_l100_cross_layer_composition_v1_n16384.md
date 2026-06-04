# Prereg: q_a3_l100_cross_layer_composition_v1_n16384 -- CENTURY RUNG

## Anchor
q_a3_l100_cross_layer_composition_v1_n16384

## Priority
C -- CENTURY RUNG (cycle 45 all-night burst, L=100 N=16384, rung 81, milestone)

## Scientific question
Does cross-layer composition fidelity remain EXACT-1.0 at L=100 N=16384?
This is the century rung: 100 sequential Hopfield layers at the largest tested N.
ECC theory predicts UNLIMITED depth when per-stage alpha = 100/16384 = 0.0061 << alpha_c=0.138.
Empirical confirmation at L=100 would be a strong product-level signal for the substrate.

## Pre-registered bands
HARD-PASS: all 100 level fidelities >= 0.9999 unanimous (5/5 seeds) AND l100_acc >= 0.5.
MIDDLE: any L_fid in [0.85, 0.9999) OR graceful degradation pattern.
HARD-FAIL: any L_fid < 0.85 OR l100_acc < 0.5.

## Formula self-tests (PROT-022)
1. Capacity: M_INNER=100, N=16384 -> alpha=0.0061 < alpha_c=0.138. [EXPECTED: True]
2. M_MID length == L_DEPTH - 2 == 98. [INPUT: L_DEPTH=100] [EXPECTED: len(M_MID)=98]
3. W on-demand: 16384*16384*4 = 1.07 GB -- within 8 GB GPU. [EXPECTED: True]

## N-suffix binding (PROT-018)
anchor _n16384; production N = 16384. Script constant N = 16384.

## Timeout estimate
PROT-019 floor applied: timeout_s = 21600.

## Smoke gate
--skip-smoke: no local CUDA. Structurally identical to EXACT series L=20..L=99.
Century rung significance: if HARD-PASS, confirms 100-layer ECC substrate at N=16384.

## Queue
overnight_queue (GPU required).
