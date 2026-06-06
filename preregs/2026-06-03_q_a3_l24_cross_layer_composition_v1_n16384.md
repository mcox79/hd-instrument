# Prereg: q_a3_l24_cross_layer_composition_v1_n16384

**Date:** 2026-06-03
**Anchor:** q_a3_l24_cross_layer_composition_v1_n16384
**Script:** experiments/exp_q_a3_l24_cross_layer_composition_v1_n16384.py
**Queue:** overnight_queue (GPU)
**Cap_map row:** PP-12 / Q-A3 cross-layer composition

## Hypothesis

L=24 at N=16384 will produce all 24 level fidelities >= 0.9999 (EXACT-class), unanimous 5/5 seeds.
Prior evidence: N=16384 series {L=20, L=21, L=22, L=23} all EXACT-1.0000 (v360 cycle).
N=8192: L=24 HARD_PASS EXACT-1.0000.
Composition is N-independent through at least L=23 at N=16384.

## Pre-registered bands

- **HARD-PASS:** all 24 level fidelities >= 0.9999 unanimous (5/5 seeds) AND l24_acc >= 0.5.
- **MIDDLE:** any L_fid in [0.85, 0.9999) OR graceful degradation.
- **HARD-FAIL:** any L_fid < 0.85 OR l24_acc < 0.5.

## Configuration

- N = 16384 (production; _n16384 suffix binding)
- L_DEPTH = 24
- SEEDS = [7, 17, 23, 31, 41] (5 seeds)
- M_INNER = 100, on-demand W build to manage GPU memory
- NOISE_FRAC = 0.10

## PROT-018

Anchor _n16384; script N=16384. Verified: `grep "^N = " -> N = 16384`.

## PROT-021

run_mode=full, n_seeds=5. Seed checkpoints keyed with run_mode + L.

## Timeout estimate

Prior L=23 N=16384 elapsed ~300s FULL 5-seed GPU.
L=24 scales near-linearly with L (24/23 = 1.04x).
`ceil(1.5 * 300 * 1.04 * 1.0)` = ceil(468) = 600s.

**timeout_s = 600**

## Formula self-tests (PROT-022)

1. L=24 chain: 23-ctx Hadamard roundtrip recovers xi_L1. [EXPECTED: decode = xi_L1 exactly]
2. All alphas < alpha_c=0.138 at N=16384. M_INNER=100 -> alpha=100/16384=0.0061 < 0.138.
3. GPU memory > 0 after W build.
4. W on-demand peak: 16384^2 * 4 / 1e9 < 1.2 GB.

## Dependency check

No upstream data dependencies. Script is self-contained.

## Ship rationale

RESUME: script existed but queue_add failed mid-cycle due to API ConnectionRefused.
N=16384 depth ladder L=24; extends confirmed EXACT streak to 5th rung at N=16384.
GPU wall estimated < 10 min; minimal cost.
