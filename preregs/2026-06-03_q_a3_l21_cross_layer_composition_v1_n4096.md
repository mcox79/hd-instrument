# Pre-registration: Q-A3 L=21 cross-layer composition ceiling chase

**Date:** 2026-06-03
**Anchor:** `q_a3_l21_cross_layer_composition_v1_n4096`
**Queue:** overnight_queue
**Trigger:** Q-A3 L=19 HARD_PASS (all 19 levels EXACT-1.0); L=20 expected HARD_PASS from smoke.
**Priority:** PP-12 cross-layer composition ceiling characterization; ceiling still not found.

## Capability question

Does substrate PP-12 cross-layer hierarchical composition continue EXACT-1.0 fidelity at L=21?
Shipped in parallel with L=20 to keep ceiling chase efficient.

## Prior results

All L=1..19 HARD_PASS EXACT-1.0 at N=4096. L=20 smoke HARD_PASS. Ceiling not reached.

## Pre-registered bands

### HARD-PASS
All 21 level fidelities >= 0.9999 (EXACT-1.0) unanimous (5/5 seeds) AND l21_acc >= 0.5.

### MIDDLE
Any L_fid in [0.85, 1.0) OR graceful degradation of inner levels.

### HARD-FAIL
Any L_fid < 0.85 OR l21_acc < 0.5. Ceiling found at L=21.

## Formula self-tests (PROT-022)

1. L=21 chain: 21-step Hadamard roundtrip recovers xi_L1.
   [INPUT: 2-element +-1 vectors, 20 context ops] [EXPECTED: decode = xi_L1 exactly]
2. All alphas < alpha_c=0.138 at production N=4096. M_INNER=100 -> alpha=0.0244; M_OUTER=2 -> alpha=0.000488.

## Smoke result

N_ACTIVE=512, 2 seeds, wall=0.23s:
HARD_PASS: all 21 levels EXACT-1.0 unanimous. Instrumentation verified.

## Timeout estimate

Prior L=19 smoke: ~0.22s at N=512. FULL at N=4096 (8x scale, 5/2 seeds):
timeout = ceil(1.5 * 0.23 * 8^1.0 * 2.5) = ceil(6.9) = 300s.
Conservative: 600s (GPU startup + W-build overhead).

## Memory estimate

21 W matrices * 67 MB = 1407 MB. Fits in 8.6 GB GPU.
