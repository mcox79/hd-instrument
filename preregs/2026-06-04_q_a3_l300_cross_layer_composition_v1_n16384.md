# Prereg: q_a3_l300_cross_layer_composition_v1_n16384

## Anchor
q_a3_l300_cross_layer_composition_v1_n16384

## Priority
A (cycle 54: extreme-depth probe)

## Scientific question
Does cross-layer composition fidelity remain EXACT-1.0 at L=300 N=16384?
ECC theory predicts UNLIMITED depth when per-stage alpha = 100/16384 = 0.0061 << alpha_c=0.138.

## Pre-registered bands
HARD-PASS: all 300 level fidelities >= 0.9999 unanimous (5/5 seeds) AND l300_acc >= 0.5.
MIDDLE: any L_fid in [0.85, 0.9999) OR graceful degradation pattern.
HARD-FAIL: any L_fid < 0.85 OR l300_acc < 0.5.

## Formula self-tests (PROT-022)
1. Capacity: M_INNER=100, N=16384 -> alpha=0.0061 < alpha_c=0.138. [EXPECTED: True]
2. M_MID length == L_DEPTH - 2 == 298. [INPUT: L_DEPTH=300] [EXPECTED: len(M_MID)=298]
3. L=300 chain: 299-ctx Hadamard roundtrip recovers xi_L1. [EXPECTED: exact]

## EXTREME-DEPTH note (cycle 54)
L=300 is 100 rungs past cycle-53 probe L=200 and ~150 past frontier L=150. Maps the extreme-depth
regime (L=200/300). Smoke-at-low-N satisfied by remote --self-test (299-ctx Hadamard chain decode +
capacity asserts). Full run N=16384 5-seed. Note: L=200 (cycle 53) verdict still in flight; L=300 is
an additional extreme-depth datapoint, not contingent on L=200.

## N-suffix binding (PROT-018)
anchor _n16384; production N = 16384. Script constant N = 16384.

## Timeout estimate
PROT-019 floor applied: timeout_s = 21600.

## Smoke gate
--skip-smoke: no local CUDA. Remote --self-test gates chain decode + capacity. gen_qa3_scripts.py template (same as L=137/L=101 HARD_PASS).

## Queue
overnight_queue (GPU required).
