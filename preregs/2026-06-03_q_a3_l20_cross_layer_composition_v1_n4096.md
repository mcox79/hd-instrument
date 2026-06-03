# Pre-registration: Q-A3 L=20 cross-layer composition ceiling chase

**Date:** 2026-06-03
**Anchor:** `q_a3_l20_cross_layer_composition_v1_n4096`
**Queue:** overnight_queue
**Trigger:** Q-A3 L=19 HARD_PASS (all 19 levels EXACT-1.0 unanimous 5-seed). Ceiling not reached.
**Priority:** PP-12 cross-layer composition ceiling characterization.

## Capability question

Does substrate PP-12 cross-layer hierarchical composition continue EXACT-1.0 fidelity at L=20
(extending from L=19 unanimous HARD_PASS)?

## Prior results

| Anchor | L | verdict | fidelity |
|---|---|---|---|
| q_a3_l19 | 19 | HARD_PASS | all EXACT-1.0 5-seed unanimous |
| q_a3_l18 | 18 | HARD_PASS | all EXACT-1.0 |
| ... | ... | HARD_PASS | all EXACT-1.0 |

Pattern: L=1 through L=19 all HARD_PASS EXACT-1.0 at N=4096. Ceiling not yet found.

## Pre-registered bands

### HARD-PASS
All 20 level fidelities >= 0.9999 (EXACT-1.0) unanimous (5/5 seeds) AND l20_acc >= 0.5.

### MIDDLE
Any L_fid in [0.85, 1.0) OR graceful degradation of inner levels.

### HARD-FAIL
Any L_fid < 0.85 OR l20_acc < 0.5. Ceiling found at L=20.

## Formula self-tests (PROT-022)

1. L=20 chain: 20-step Hadamard roundtrip recovers xi_L1.
   [INPUT: 2-element +-1 vectors, 19 context ops] [EXPECTED: decode = xi_L1 exactly]
2. All alphas < alpha_c=0.138 at production N=4096.
   M_INNER=100 -> alpha=0.0244; M_OUTER=2 -> alpha=0.000488. All < 0.138.

## Smoke result

N_ACTIVE=512, 2 seeds, wall=0.22s:
HARD_PASS: all 20 levels EXACT-1.0 unanimous. Instrumentation verified.

## Timeout estimate

Prior L=19 smoke: ~0.22s at N=512. FULL at N=4096 (8x linear scale, 5/2 seeds):
timeout = ceil(1.5 * 0.22 * 8^1.0 * 2.5) = ceil(6.6) = 300s.
Conservative: 600s (GPU startup + W-build overhead at N=4096).

## Memory estimate

20 W matrices * (4096^2 * 4 bytes) = 20 * 67 MB = 1340 MB. Well within 8.6 GB GPU.
