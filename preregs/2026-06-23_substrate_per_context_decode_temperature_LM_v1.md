# Prereg: substrate_per_context_decode_temperature_LM_v1

**Filed:** 2026-06-23
**Anchor:** substrate_per_context_decode_temperature_LM_v1
**Queue:** local_cpu_queue
**Script:** experiments/exp_substrate_per_context_decode_temperature_LM_v1.py

## Hypothesis

Global temperature calibration (fair_harness HARD_PASS: best T=0.05, BPC=7.3065) treats
all decode positions identically. Brain literature (Yu-Dayan 2005 ACh-mediated gain control;
locus coeruleus phasic-vs-tonic uncertainty-dependent gain) shows cortical neurons modulate
effective SNR based on task uncertainty. Per-context T modulated by query difficulty is
substrate-native phase-diagram navigation (USER phase-diagram action property).

P_inherited = 0.45 (Yu-Dayan 2005 at P=0.55 deflated 0.10 for substrate-native LM application).

## Design

- N_TRAIN=100k, N_HELD=20k, N_DIM=8192, VOCAB_CAP=4000, SPARSE_F=0.05
- 4 arms x 3 seeds (seeds=[7,17,23])
- T_LOW=0.02, T_HIGH=0.5, LAMBDA_PER_CONTEXT=0.3 (fixed at fair_harness best lambda)
- ARM_UNIGRAM: analytic floor
- ARM_GLOBAL_T: joint (T, lambda) sweep on dev (mirrors fair_harness); self-test bar: BPC within 0.05 of 7.3065
- ARM_PER_CONTEXT_T_ENTROPY: T_i = T_LOW + (T_HIGH-T_LOW)*(1-H_norm_i); T_base tuned on dev
- ARM_PER_CONTEXT_T_MARGIN: T_i = T_LOW + (T_HIGH-T_LOW)*margin_norm_i; T_base tuned on dev

## Pre-reg HARD bands

- **HARD_PASS**: ARM_PER_CONTEXT_T_ENTROPY OR ARM_PER_CONTEXT_T_MARGIN beats ARM_GLOBAL_T
  by >= +0.10 bits BPC AND cv < 0.05
- **CHAIN_GRADE_BONUS**: lift >= +0.20 bits AND final BPC < fair_harness chain-grade 7.3065
- **MIDDLE_BAND**: lift +0.03 to +0.10 bits (marginal)
- **HARD_FAIL**: lift <= +0.03 bits

Bands registered before any run. Thresholds are absolute BPC improvement values.

## Timeout estimate

Smoke: N_DIM=512, N_TRAIN=2000, 1 seed, CPU.
FULL: N_DIM=8192, N_TRAIN=100k, 3 seeds, CPU.
Scale ratio (N_DIM): 8192/512 = 16; matmul cost ~ O(N_DIM^2) for W build = 256x.
Scale ratio (N_TRAIN): 100k/2k = 50x for W build.
Scale ratio (seeds): 3/1 = 3x.
Combined W-build scaling: 50x * (8192/512)^2 = 50 * 256 = 12800x. RECALL: O(N_TRAIN * N_DIM) ~ 50x * 16x = 800x.
Smoke expected < 30s. Full: RECALL is the bottleneck at N=8192, n_test~10k positions, 300 recall batch ops.
Best estimate from structure: smoke_wall ~ 30s for 1 seed at smoke scale.
timeout_s = ceil(1.5 * 30 * 50 * 3) = ceil(6750) ~ 7200s (2 hours).
NOTE: W build at N_DIM=8192 is a 8192x8192 float32 matrix = 256MB; per-chunk outer product.
This is heavy for CPU. Recommend runner be healthy before dispatching.

## Gap source

substrate_mine_modulator_gain_experiments_inventory_2026-06-23.md row:
"Temperature-calibrate (global): MIDDLE_BAND only; per-context NEVER TESTED -- Top-1 untested gap"

## Cites

- data/exp_fair_harness_substrate_as_lm_v1/metrics.json (chain-grade baseline BPC=7.3065)
- notes/substrate_mine_modulator_gain_experiments_inventory_2026-06-23.md (gap source)
- Yu-Dayan 2005 (ACh gain control; brain P_inherited)
- USER phase-diagram action property (substrate acts at ANY position in phase diagram)
