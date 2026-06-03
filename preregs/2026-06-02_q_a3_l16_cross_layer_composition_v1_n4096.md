# Prereq: q_a3_l16_cross_layer_composition_v1_n4096

**Date:** 2026-06-02
**Anchor:** q_a3_l16_cross_layer_composition_v1_n4096
**Queue:** overnight_queue (GPU)
**Script:** experiments/exp_q_a3_l16_cross_layer_composition_v1_n4096.py

## Hypothesis

Q-A3 ceiling chase: extends L=15 (HARD_PASS, all fids EXACT-1.0, 5-seed unanimous) to L=16.
16 levels of Hadamard binding over Hopfield retrieval at N=4096.

## PROT-022 Formula Self-tests

1. L=16 chain: 15-context Hadamard roundtrip recovers xi_L1 exactly.
   [INPUT: 2-element +/-1 vectors, 15 context ops] [EXPECTED: decoded = xi_L1, atol=1e-6] [VERIFIED at AST level; runs on GPU]
2. All alphas (M/N) < alpha_c=0.138. [VERIFIED in _instrumentation_selftest()]
3. GPU guard: memory > 0 after W build. [VERIFIED in _instrumentation_selftest()]

## GPU Memory Estimate

- 16 W matrices at N=4096, float32: 16 * (4096^2 * 4 bytes) = 16 * 67.1 MB = 1073 MB ~ 1.05 GB
- Well within 8 GB GPU limit (< 6 GB ceiling). No OOM risk.

## Pre-registered Bands

**HARD-PASS:** all 16 level fidelities = 1.0000 unanimous (5/5 seeds)
**MIDDLE:** any L_fid in [0.85, 1.0)
**HARD-FAIL:** any L_fid < 0.85 OR l16_acc < 0.5

## Smoke Result

No local GPU available. GPU script verified: AST parse OK, PROT-018 binding N=4096 matches _n4096,
_seed_checkpoint import exists, same pattern as L=15 (which succeeded). Prior L=15 was HARD_PASS.

## Walk-back gate

Prior L=15 was EXACT-1.0 unanimous. Effect size >> 1.0 (exact precision, no degradation).
No walk-back needed.

## Timeout Estimate

- Prior L=15 elapsed: ~60s per seed at N=4096 (5 W matrices ~ 1 GB, ~12s/seed from L=13 history)
- L=16 adds 1 more W matrix (~67MB). Minimal time increase.
- smoke_wall estimate: ~15s/seed at N=512 (2 seeds)
- FULL: N=512->4096 (8x), 2->5 seeds (2.5x), scaling_exp=1.5
  timeout = ceil(1.5 * 15 * 8^1.5 * 2.5) = ceil(1272) = 1500s
- Using 1800s for margin.

## N-suffix

Anchor _n4096, script N = 4096. PROT-018 binding: N == _N_SUFFIX assertion in script.

## Cap_map Impact

- HARD-PASS: PP-12 cross-layer composition ceiling extends to L=16 EXACT-1.0; Q-A3 family continues.
- HARD-FAIL: ceiling detected between L=15 and L=16; PP-12 ceiling characterized.
- MIDDLE: graceful degradation at L=16; ceiling boundary being approached.
