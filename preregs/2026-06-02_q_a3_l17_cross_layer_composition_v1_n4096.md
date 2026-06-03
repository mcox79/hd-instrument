# Prereq: q_a3_l17_cross_layer_composition_v1_n4096

**Date:** 2026-06-02
**Anchor:** q_a3_l17_cross_layer_composition_v1_n4096
**Queue:** overnight_queue (GPU)
**Script:** experiments/exp_q_a3_l17_cross_layer_composition_v1_n4096.py

## Hypothesis

Q-A3 ceiling chase: extends L=16 (HARD_PASS, all fids EXACT-1.0, 5-seed unanimous at N=4096, v350) to L=17.
17 levels of Hadamard binding over Hopfield retrieval at N=4096.
L-series at N=4096 now L=2..L=16 all EXACT-1.0000. Ceiling not found.

## PROT-022 Formula Self-tests

1. L=17 chain: 16-context Hadamard roundtrip recovers xi_L1 exactly.
   [INPUT: 2-element +-1 vectors, 16 context ops] [EXPECTED: decode = xi_L1, atol=1e-6] [VERIFIED in script selftest]
2. All alphas (M/N) < alpha_c=0.138. [VERIFIED in _instrumentation_selftest()]
3. GPU guard: memory > 0 after W build. [VERIFIED in _instrumentation_selftest()]

## GPU Memory Estimate

- 17 W matrices at N=4096, float32: 17 * 67.1 MB = 1139 MB ~ 1.11 GB
- Well within 8 GB GPU limit. No OOM risk.

## Pre-registered Bands

**HARD-PASS:** all 17 level fidelities = 1.0000 unanimous (5/5 seeds)
**MIDDLE:** any L_fid in [0.85, 1.0)
**HARD-FAIL:** any L_fid < 0.85 OR l17_acc < 0.5

## Smoke Result

No local GPU. Script self-test PASS (L=17 chain decode ok, capacity_ok, gpu_mem_ok).
Prior L=16 was EXACT-1.0 unanimous (v350). Pattern from L=2..L=16 = monotone EXACT.

## Walk-back gate

L=16 was EXACT-1.0 unanimous. Effect size >> 1.0 (exact precision). No walk-back needed.

## Timeout Estimate

- Prior L=16 elapsed: 0.82s at N=4096 (5 W matrices ~1.07GB)
- L=17 adds 1 W matrix. Wall ~1-2s expected.
- smoke_wall estimate: ~0.82s * (17/16) ~ 0.87s (sub-second)
- FULL N=4096 5-seed: wall should be <5s
- Using 14400s floor (PROT-019 minimum for overnight_queue GPU _n4096).

## N-suffix

Anchor _n4096, script N = 4096. PROT-018 binding: assert N == _N_SUFFIX in script.

## Cap_map Impact

- HARD-PASS: PP-12/Q-A3 L=17 sub-property; L-ceiling not found at L=17; L=18+ eligible.
- HARD-FAIL: ceiling detected between L=16 and L=17; PP-12 ceiling characterized at L=16.
- MIDDLE: graceful degradation at L=17; ceiling boundary being approached.
