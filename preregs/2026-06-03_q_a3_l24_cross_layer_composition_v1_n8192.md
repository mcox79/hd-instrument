# Prereg: q_a3_l24_cross_layer_composition_v1_n8192

**Date:** 2026-06-03
**Anchor:** q_a3_l24_cross_layer_composition_v1_n8192
**Script:** experiments/exp_q_a3_l24_cross_layer_composition_v1_n8192.py
**Queue:** overnight_queue (GPU)
**Cap_map row:** PP-12 / Q-A3 cross-layer composition

## Hypothesis

L=24 at N=8192 will produce all 24 level fidelities >= 0.9999 (EXACT-class), unanimous 5/5 seeds.
Prior evidence: N=8192 series {L=19, L=22, L=23} all EXACT-1.0000 (v354, v355, v358).
L=24 N=4096 HARD_PASS EXACT-1.0000 (v355).
Composition is N-independent through at least L=23 at both N-scales.

## Pre-registered bands

- **HARD-PASS:** all 24 level fidelities >= 0.9999 unanimous (5/5 seeds) AND l24_acc >= 0.5.
- **MIDDLE:** any L_fid in [0.85, 0.9999) OR graceful degradation.
- **HARD-FAIL:** any L_fid < 0.85 OR l24_acc < 0.5.

## Configuration

- N = 8192 (production; _n8192 suffix binding)
- L_DEPTH = 24
- SEEDS = [7, 17, 23, 31, 41] (5 seeds)
- M_INNER = 100, M schedules decreasing to M_OUTER=2
- NOISE_FRAC = 0.10

## PROT-018

Anchor _n8192; script N=8192. Verified: `grep "^N = " -> N = 8192`.

## PROT-021

run_mode=full, n_seeds=5. Seed checkpoints keyed with run_mode + L.

## Timeout estimate

Prior L=23 N=8192 elapsed ~4.31s FULL 5-seed GPU.
L=24 scales near-linearly with L (24/23 = 1.04x).
`ceil(1.5 * 4.31 * 1.04 * 1.0)` = ceil(6.72) = 300s (GPU queue overhead floor applies).

**timeout_s = 300**

## Formula self-tests (PROT-022)

1. L=24 chain: 23-ctx Hadamard roundtrip recovers xi_L1. [EXPECTED: decode = xi_L1 exactly]
2. All alphas < alpha_c=0.138 at N=8192. M_INNER=100 -> alpha=100/8192=0.0122 < 0.138.
3. GPU memory > 0 after W build.
4. Memory estimate: 24 * 8192 * 8192 * 4 / 1e9 = 6.442 GB < 7.5 GB.

## Dependency check

No upstream data dependencies. Script is self-contained.

## Ship rationale

Queue at 0 (overnight_queue + cpu_queue) after CYCLE 27 batch. Pipeline-pacing refill.
N-scale gap: L=23 N=8192 confirmed v358; L=24 N=8192 is the next cheapest gap closure.
GPU wall estimated < 10s; minimal cost.
