# Prereg: q_a3_l42_cross_layer_composition_v1_n16384

**Date:** 2026-06-03
**Cycle:** v363 refill
**Queue:** overnight_queue (GPU)
**Script:** experiments/exp_q_a3_l42_cross_layer_composition_v1_n16384.py

## Scientific question

Does cross-layer composition fidelity remain EXACT-1.0 at L=42 N=16384?

## Context

N=4096: L=2..L=35 all EXACT-1.0000.
N=16384: L=20..L=38 all HARD_PASS. L=39/40/41 in v363 batch.
L=42 is the 23rd rung in the N=16384 ladder.

## Pre-registered bands

HARD-PASS: all 42 level fidelities >= 0.9999 unanimous (5/5 seeds) AND l42_acc >= 0.5.
MIDDLE: any L_fid in [0.85, 0.9999) OR graceful degradation.
HARD-FAIL: any L_fid < 0.85 OR l42_acc < 0.5.

## Formula self-tests (PROT-022)

1. L=42 chain: 41-ctx Hadamard roundtrip recovers xi_L1.
   [INPUT: 2-element +-1 vectors, 41 context ops] [EXPECTED: decode = xi_L1 exactly]
2. M_INNER=100, N=16384 -> alpha=0.0061 < alpha_c=0.138. PASS.
3. GPU memory > 0.
4. on-demand W = 1.073 GB < 1.2 GB per-layer gate.

## N-suffix binding (PROT-018)

Anchor name _n16384; production N = 16384. Verified.

## PROT-021 checkpoint keying

Seed checkpoints keyed with run_mode + L. Smoke N=512 isolates from full N=16384.

## Timeout estimate

Prior L=36 ~75s total. L=42 scales linearly. Estimate ~95s total.
timeout_s = ceil(1.5 * 95) = 143s -> PROT-019 floor 21600s.
Timeout filed: 21600s.
