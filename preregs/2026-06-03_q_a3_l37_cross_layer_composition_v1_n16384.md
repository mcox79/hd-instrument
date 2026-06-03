# Prereg: q_a3_l37_cross_layer_composition_v1_n16384

**Date:** 2026-06-03
**Cycle:** v363 refill
**Queue:** overnight_queue (GPU)
**Script:** experiments/exp_q_a3_l37_cross_layer_composition_v1_n16384.py

## Scientific question

Does cross-layer composition fidelity remain EXACT-1.0 at L=37 N=16384?

## Context

N=4096: L=2..L=35 all EXACT-1.0000 (21 consecutive rungs, no ceiling found).
N=16384: L=20..L=36 all HARD_PASS (18 confirmed rungs, most recent L=36 in v362 refill-2).
L=37 is the 18th rung in the N=16384 ladder, continuing beyond L=36.

## Pre-registered bands

HARD-PASS: all 37 level fidelities >= 0.9999 unanimous (5/5 seeds) AND l37_acc >= 0.5.
MIDDLE: any L_fid in [0.85, 0.9999) OR graceful degradation.
HARD-FAIL: any L_fid < 0.85 OR l37_acc < 0.5.

Rationale: these are the same bands applied to L=20..L=36, all of which HARD_PASSed.
Continuation of an unbroken streak does not require band revision.

## Formula self-tests (PROT-022)

1. L=37 chain: 36-ctx Hadamard roundtrip recovers xi_L1.
   [INPUT: 2-element +-1 vectors, 36 context ops] [EXPECTED: decode = xi_L1 exactly]
2. All alphas < alpha_c=0.138 at N=16384. M_INNER=100 -> alpha=0.0061.
   [INPUT: M_INNER=100, N=16384, alpha_c=0.138] [EXPECTED: 0.0061 < 0.138]
3. GPU memory > 0 after W build.
4. Memory estimate: on-demand W = 16384*16384*4/1e9 = 1.073 GB per layer (single at a time).
   [INPUT: N=16384, dtype=float32] [EXPECTED: 1.073 GB < 1.2 GB per-layer gate]

## N-suffix binding (PROT-018)

Anchor name contains _n16384; production N = 16384. Verified by grep.

## PROT-021 checkpoint keying

Seed checkpoints keyed with run_mode + L. Smoke at N_smoke=512 will not contaminate full run at N=16384.

## Timeout estimate

Prior L=36 run: wall_s ~15s per seed (5 seeds ~75s total).
L=37 scales linearly with L (one more layer). Estimate ~15s per seed.
timeout_s = ceil(1.5 * 75 * 1.0) = ceil(112.5) = 113s -> floor 14400s (PROT-019 minimum).
Timeout filed: 14400s.
