# Prereg: substrate_neuromodulator_3axis_gated_compose_LM_v1

**Date**: 2026-06-23
**Anchor**: substrate_neuromodulator_3axis_gated_compose_LM_v1
**Queue**: overnight_queue (GPU; N_DIM=8192 satisfies Fix #22 routing rule)

## Hypothesis

Brain uses 3 ORTHOGONAL neurotransmitter dimensions (dopamine novelty / ACh attention /
serotonin state) to break single-dimension scaling envelopes. Substrate currently has ONE
modulator (cf-RPE delta = dopamine analog). Adding 2 orthogonal modulators composed
multiplicatively on the Hebbian write rule should break the scaling cap measured in
sparse_bipolar_substrate_lm_param_sweep_v1 (max_lift = +0.44 bits; envelope bounded).

## Empirical driver

sparse_bipolar_substrate_lm_param_sweep_v1 HARD_FAIL: N_TRAIN=1M ALL FAIL; N_DIM=16384
ALL FAIL; best: f=0.02 N=8192 bpc=7.295 (lift=+0.44 vs unigram=7.738). Scaling envelope
is bounded at this single operating point. Multi-modulator orthogonality is the primary
untested lever.

## Arms

- ARM_NO_MODULATOR: raw Hebbian W += outer(E[t+1], E[t]); control
- ARM_DOPAMINE_ONLY: cf-RPE delta rule; LR = f(prediction_error_norm); existing baseline
- ARM_DOPAMINE_PLUS_ACH: cf-RPE x ACh-attention gate
- ARM_TRIPLE_MOD_FULL: dopamine x ACh x serotonin-novelty gate

## Config

- N_DIM = 8192 (production; matching fair_harness baseline for fair envelope comparison)
- N_TRAIN = 100_000 (chain-grade regime)
- V = 4000 (fixed)
- f_sparse = 0.02 (best from param_sweep)
- seeds = [7, 17, 23]
- harness: joint (T, lambda) sweep; TEMP_GRID=[0.01-1.0], LAMBDA_GRID=[0.0-1.0]; 3 metrics (BPC + top-1 + MRR@10)

## PROT-018 N-suffix note

Anchor name has NO _n suffix. Production N = 8192. Rationale: matching fair_harness
baseline (N=8192, V=4000, N_TRAIN=100k) for direct envelope comparison. The N-suffix
would require anchor name `substrate_neuromodulator_3axis_gated_compose_LM_v1_n8192`
which was not specified by the task; PRODUCTION_N=8192 is explicitly stated in the script.

## Pre-registered bands (IMMUTABLE post-dispatch)

**Primary comparison: ARM_TRIPLE_MOD_FULL vs ARM_DOPAMINE_ONLY (delta = dopa_bpc - triple_bpc)**

- **HARD_PASS**: delta >= 0.10 bits BPC (triple beats dopamine by >= 0.10 bits; envelope broken)
- **MIDDLE_BAND**: delta in [0.03, 0.10] bits (modest additive; not chain-grade)
- **HARD_FAIL**: delta <= 0.03 bits (multi-modulator does NOT break envelope; cap is fundamental)
- **CHAIN_GRADE_ELIGIBLE BONUS**: if TRIPLE bpc_best_mean <= 7.2065 (fair_harness baseline 7.3065 - 0.10 bits)

## Calibration note

Prior empirical anchor exists: fair_harness DOPAMINE_ONLY achieves bpc ~7.31 (MIDDLE_BAND
per envelope). This is NOT a first-measurement calibration probe; bands are set relative to
the known baseline. Brain-existence-proof P_inherited=0.65; deflated 0.05-0.10 for
novel-synthesis -> P_deflated=0.55-0.60.

## Smoke result (gate passed)

- Smoke config: N=512, N_TRAIN=2000, V=300, seeds=[0]
- smoke_wall_s=28s
- ARM_DOPAMINE_ONLY bpc=5.523; ARM_TRIPLE_MOD_FULL bpc=5.314; delta=0.209 bits
- Verdict at smoke scale: HARD_PASS (delta=0.209 >= 0.10)
- Effect size is well above threshold (2.09x); no walk-back needed.
- Self-test: PASS (cf-RPE, ACh=0 for identical, serotonin=0 for familiar, sparse density correct)

## Timeout estimate

```
timeout_s = ceil(1.5 * smoke_wall_s * (FULL_N_TRAIN/smoke_N_TRAIN)^scaling_exp * (FULL_seeds/smoke_seeds))
          = ceil(1.5 * 28 * (100000/2000)^1.0 * (3/1))
          = ceil(1.5 * 28 * 50 * 3)
          = ceil(6300)
          = 6300s
```

scaling_exp=1.0 (linear; W build is O(N_TRAIN) at fixed N). FULL/smoke seed ratio=3.
6300s = 1.75h. Under 7200s ceiling; no strategy escalation needed.

## Fix #24 GPU compliance

Script imports torch.cuda; uses `.to('cuda')` / batched tensor matmul throughout.
Encoder hoisted outside arm+seed loop (Fix #24: load once, reuse).
N_DIM=8192 satisfies Fix #22 routing rule (N_DIM >= 8192 -> overnight_queue).
GPU util expected >= 50% during W build (E.T @ Delta is [dim x chunk] matmul).
