# Prereg: q_a3_l38_cross_layer_composition_v1_n16384

**Date:** 2026-06-03
**Cycle:** v363 refill
**Queue:** overnight_queue (GPU)
**Script:** experiments/exp_q_a3_l38_cross_layer_composition_v1_n16384.py

## Scientific question

Does cross-layer composition fidelity remain EXACT-1.0 at L=38 N=16384?

## Context

N=4096: L=2..L=35 all EXACT-1.0000 (21 consecutive rungs).
N=16384: L=20..L=36 all HARD_PASS. L=37 in current v363 batch.
L=38 is the 19th rung in the N=16384 ladder.

## Pre-registered bands

HARD-PASS: all 38 level fidelities >= 0.9999 unanimous (5/5 seeds) AND l38_acc >= 0.5.
MIDDLE: any L_fid in [0.85, 0.9999) OR graceful degradation.
HARD-FAIL: any L_fid < 0.85 OR l38_acc < 0.5.

## Formula self-tests (PROT-022)

1. L=38 chain: 37-ctx Hadamard roundtrip recovers xi_L1.
   [INPUT: 2-element +-1 vectors, 37 context ops] [EXPECTED: decode = xi_L1 exactly]
2. All alphas < alpha_c=0.138. M_INNER=100, N=16384 -> alpha=0.0061 < 0.138. PASS.
3. GPU memory > 0 after W build.
4. on-demand W = 1.073 GB < 1.2 GB per-layer gate.

## N-suffix binding (PROT-018)

Anchor name _n16384; production N = 16384. Verified.

## PROT-021 checkpoint keying

Seed checkpoints keyed with run_mode + L. Smoke N=512 will not contaminate full N=16384.

## Timeout estimate

Prior L=36 wall ~75s total (5 seeds). L=38 scales linearly. Estimate ~80s total.
timeout_s = ceil(1.5 * 80) = 120s -> PROT-019 minimum 14400s.
Timeout filed: 14400s.
