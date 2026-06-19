# Prereg: q_a3_l95_cross_layer_composition_v1_n16384

## Anchor
q_a3_l95_cross_layer_composition_v1_n16384

## Priority
A (cycle 45 all-night burst, ladder continuation L=95 N=16384, rung 76)

## Scientific question
Does cross-layer composition fidelity remain EXACT-1.0 at L=95 N=16384?
ECC theory predicts UNLIMITED depth when per-stage alpha = 100/16384 = 0.0061 << alpha_c=0.138.

## Pre-registered bands
HARD-PASS: all 95 level fidelities >= 0.9999 unanimous (5/5 seeds) AND l95_acc >= 0.5.
MIDDLE: any L_fid in [0.85, 0.9999) OR graceful degradation pattern.
HARD-FAIL: any L_fid < 0.85 OR l95_acc < 0.5.

## Formula self-tests (PROT-022)
1. L=95 Hadamard chain decode: [INPUT: 2-elem +-1 vectors, 94 context ops] [EXPECTED: decode = xi_L1 exactly]
2. Capacity: M_INNER=100, N=16384 -> alpha=0.0061 < alpha_c=0.138. [EXPECTED: True]
3. GPU memory > 0 after W build. [EXPECTED: allocated > 0]
4. M_MID length == L_DEPTH - 2 == 93. [INPUT: L_DEPTH=95] [EXPECTED: len(M_MID)=93]

## N-suffix binding (PROT-018)
anchor _n16384; production N = 16384. Script constant N = 16384.

## Timeout estimate
Prior L=94 elapsed ~45s (5-seed, N=16384). L=95 near-linear in L.
Formula: ceil(1.5 * 50 * 1.0 * 1) = 75s. PROT-019 floor applied: timeout_s = 21600.

## Smoke gate
--skip-smoke: no local CUDA. Series structurally identical to L=20..L=94 (all EXACT-1.0).
Prior smoke: l94 PASS. Validated via _instrumentation_selftest + assert M_MID length.

## Queue
overnight_queue (GPU required).
