# Prereg: q_a3_l30_cross_layer_composition_v1_n4096

**Date:** 2026-06-03
**Anchor:** q_a3_l30_cross_layer_composition_v1_n4096
**Script:** experiments/exp_q_a3_l30_cross_layer_composition_v1_n4096.py
**Queue:** overnight_queue (GPU)
**Cap_map row:** PP-12 / Q-A3 cross-layer composition

## Hypothesis

L=30 at N=4096 will produce all 30 level fidelities >= 0.9999 (EXACT), unanimous 5/5 seeds.
Prior evidence: L=2..L=29 all EXACT-1.0000 at N=4096 (15 consecutive L-extensions; v358).
This is the 16th extension in the ceiling chase.

## Pre-registered bands

- **HARD-PASS:** all 30 level fidelities >= 0.9999 unanimous (5/5 seeds) AND l30_acc >= 0.5.
- **MIDDLE:** any L_fid in [0.85, 0.9999) OR graceful degradation.
- **HARD-FAIL:** any L_fid < 0.85 OR l30_acc < 0.5.

## Configuration

- N = 4096 (production; _n4096 suffix binding)
- L_DEPTH = 30
- SEEDS = [7, 17, 23, 31, 41] (5 seeds)
- M_INNER = 100, M schedules decreasing to M_OUTER=2
- NOISE_FRAC = 0.10

## PROT-018

Anchor _n4096; script N=4096. Verified: `grep "^N = " -> N = 4096`.

## PROT-021

run_mode=full, n_seeds=5. Seed checkpoints keyed with run_mode + L.

## Timeout estimate

Prior L=29 elapsed ~2.04s FULL 5-seed GPU.
L=30 scales near-linearly with L (30/29 = 1.034x).
`ceil(1.5 * 2.04 * 1.034 * 1.0)` = ceil(3.16) = 300s (GPU queue overhead floor applies).

**timeout_s = 300**

## Formula self-tests (PROT-022)

1. L=30 chain: 29-ctx Hadamard roundtrip recovers xi_L1. [EXPECTED: decode = xi_L1 exactly]
2. All alphas < alpha_c=0.138 at N=4096. M_INNER=100 -> alpha=100/4096=0.0244 < 0.138.
3. GPU memory > 0 after W build.
4. Memory estimate: 30 * 4096 * 4096 * 4 / 1e9 = 2.013 GB < 2.2 GB.

## Dependency check

No upstream data dependencies. Script is self-contained.

## Ship rationale

Queue at 0 after CYCLE 27 batch. Pipeline-pacing refill.
16th L-extension ceiling chase; ceiling not found at L=29; L=30 is cheapest next test.
GPU wall estimated < 5s; minimal cost.
