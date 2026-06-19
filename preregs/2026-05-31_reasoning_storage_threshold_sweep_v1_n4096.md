# Pre-registration: reasoning_storage_threshold_sweep_v1_n4096

Date: 2026-05-31
Anchor: reasoning_storage_threshold_sweep_v1_n4096
Script: experiments/exp_reasoning_storage_threshold_sweep_v1_n4096.py
Queue: remote_cpu_queue
PROT-018: _n4096 binds N = 4096

## Context

Drill A from 2x synthesis predicted spectral collapse at ~32N/3 ~ 44K shared-modus-ponens
chains at N=4096. This anchor verifies the threshold empirically by sweeping
#chains-sharing-the-same-rule-codeword and measuring W spectral structure.

## Scientific question

At what #-of-shared-rule-code chains does the W matrix show spectral dominance
(sigma_1/sigma_2 >> 1)? Does the empirical threshold match the theoretical ~44K?

## Configuration

- N = 4096 (PROT-018 binding)
- All stored steps share same rule codeword (worst-case shared structure)
- k_step_i = r_modus * k1_i * k2_i (k1, k2 random BSC per step)
- Sweep #chains: [100, 1000, 10000, 44000, 100000]
- Each chain contributes CHAIN_DEPTH=4 steps
- 3 seeds: [7, 17, 23]
- SVD: top-50 singular values via svd_lowrank
- Device: CPU (remote_cpu_queue)

## N-suffix

`_n4096` -> production N = 4096 (PROT-018 binding).

## Pre-registered bands

Collapse criterion: sigma_1/sigma_2 > 3.0 (empirically calibrated; random BSC
outer-product W has sigma_1/sigma_2 ~ 1.0-1.02 at all tested M, N values).

- HARD-PASS: sigma_1/sigma_2 < 3.0 for ALL sweep points <= 44K.
             (No spectral collapse below the theoretical 32N/3 threshold.)
- HARD-FAIL: spectral collapse (sigma_1/sigma_2 >= 3.0) at #chains <= 10K.
             (Threshold is 4x lower than drill A prediction.)
- MIDDLE-BAND: collapse in range (10K, 44K] -- lower than predicted, not 4x.
- NOTE: If collapse is only at #chains > 44K, that also constitutes HARD-PASS
  (consistent with 32N/3 theoretical prediction).

## Formula self-tests

1. 32N/3 at N=4096: 32*4096/3 = 43690 (spec rounds to 44K). Self-tested in script.
2. For random BSC W: sigma_1/sigma_2 ~ 1.0. Self-tested at N=128 in selftest().
3. Collapse criterion: sigma_1/sigma_2 > 3.0 (constant, not N-dependent).

## Timeout estimate

- Smoke wall: 0.26s (N=512, 1 seed, sweep=[50,200,500])
- FULL N=4096 vs smoke N=512: W build scales ~N^2.7.
  At n_chains=100K, M=400K: W build estimated ~134s (N=4096 extrapolation).
  5 sweep points x 3 seeds: 5 * 3 * 134s / 5 (avg over sweep) ~ 402s.
  Actually n_chains=100K is the expensive point; others are faster.
  Total estimate: ~200-400s. With 1.5x safety: ~600s.
- PROT-019 floor: 14400s.
- timeout_s = 14400

## Dependencies

- BSC codebook construction: self-contained.
- _seed_checkpoint.py: present.
- No external data files.

## Walk-back assessment

Smoke sigma_1/sigma_2 ratio ~ 1.0-1.02 at all smoke scale points. No collapse.
Effect size: N/A (ratio is the primary metric; no d-measure applies here).
Walk-back not triggered (the metric is a ratio threshold, not an effect size).
Expected FULL run result: HARD-PASS (no collapse) given that k_step = r_modus * k_rand
is still random BSC from a k1×k2 pool of 200×20=4000 combinations. The 32N/3
prediction may be overly pessimistic for this corpus design.
