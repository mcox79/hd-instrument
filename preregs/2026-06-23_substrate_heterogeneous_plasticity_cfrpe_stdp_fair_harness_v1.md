# Prereg: substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1

**Date:** 2026-06-23
**Anchor:** substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1
**Queue:** overnight_queue (GPU)
**Script:** experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py

## Hypothesis

Heterogeneity IS the lever for LM improvement at production scale (N_DIM=8192, text8 100k).
Source evidence:
- cert row 473: cf-RPE x STDP HETEROGENEOUS HARD_PASS chain-grade at N=512 (super_seeds=5/5)
- substrate_mine Axis A: heterogeneous pairing superadditive; homogeneous Hebbian compose MIDDLE_BAND
- 3-axis neuromod cell: READOUT_DEGENERATE at production (homogeneous Hebbian gating fails)
This cell directly tests: does the N=512 heterogeneous-compose advantage survive scale to N=8192?

## Arms

1. ARM_UNIGRAM -- analytic baseline (BPC + top-1 + MRR)
2. ARM_HEBBIAN_ONLY -- one-pass rank-1 symmetric Hebbian; reproduces 7.3065 fair_harness baseline
3. ARM_CFRPE_ONLY -- cf-RPE delta rule alone (task-supervised axis); tests single-rule hypothesis
4. ARM_CFRPE_STDP_HETEROGENEOUS -- cf-RPE task-axis + STDP temporal-axis heterogeneous compose; load-bearing arm

## Configuration

- N_DIM = 8192 (production scale)
- N_TRAIN = 100,000 (text8)
- N_HELD = 20,000
- VOCAB_CAP = 4000
- SPARSE_BIPOLAR_F = 0.05 (same as fair_harness chain-grade baseline)
- CFRPE_LR = 0.5
- STDP_WEIGHT = 0.5
- N_STEPS = 1000 (iterative stochastic updates for CFRPE/HETERO arms)
- SEEDS = [7, 17, 23]
- Encoder: word2vec-google-news-300 projected + sparse-bipolar (same as chain-grade fair_harness baseline)
- Joint (T, lambda) sweep: TEMP_GRID=[0.01..1.0] x LAMBDA_GRID=[0.0..1.0]; dev-pick, test-eval
- Three metrics per arm: BPC + top-1 + MRR@10

## Pre-Registered HARD Bands

**Primary metric: BPC lift = ARM_HEBBIAN_ONLY BPC - ARM_CFRPE_STDP_HETEROGENEOUS BPC (positive = better)**

- **HARD_PASS:** lift >= 0.10 bits
  Heterogeneous plasticity adds REAL lift over Hebbian chain-grade baseline at production scale.
  Confirms: heterogeneity is the lever, not an N=512 artifact.

- **CHAIN_GRADE_BONUS:** HARD_PASS AND lift >= 0.20 bits
  Confirms substrate-mine hypothesis at production; breaks the 0.44 bits sparse_bipolar envelope cap.

- **MIDDLE_BAND:** lift in [0.03, 0.10) bits
  Heterogeneity helps but does not break envelope; partial signal.

- **HARD_FAIL:** lift <= 0.03 bits OR ARM_CFRPE_STDP_HETEROGENEOUS collapses to unigram (READOUT_DEGENERATE)
  Heterogeneous rule compose also degenerate at scale; mechanism doesn't transfer.

**cv constraint:** cv < 0.05 across seeds for ARM_CFRPE_STDP_HETEROGENEOUS (mandatory for cert-grade)

**READOUT_DEGENERATE gate:** raw_bpc_at_T1_L1 within +/-0.5 of log2(V) for ARM_CFRPE_STDP_HETEROGENEOUS
AND lift <= 0.03 -> READOUT_DEGENERATE (same as 3-axis cell pattern).

## Probability Estimate (deflated from N=512 chain-grade)

P(HARD_PASS) = 0.50-0.55
- P_inherited from cert row 473 (5/5 super_seeds at N=512) would be ~0.80
- P_deflated: envelope-cap precedent (sparse_bipolar capped at 0.44 bits at N=8192) + 3-axis cell READOUT_DEGENERATE at production + iterative stochastic updates may not converge same way at scale
- Genuine uncertainty; run warranted

## Smoke Result (pre-ship gate)

Smoke run: N_DIM=512 N_TRAIN=2000 SEEDS=[0] -- laptop CPU (no CUDA available on laptop).

Results (from metrics.json):
- ARM_UNIGRAM: bpc=5.523
- ARM_HEBBIAN_ONLY: bpc=5.178
- ARM_CFRPE_ONLY: bpc=4.773
- ARM_CFRPE_STDP_HETEROGENEOUS: bpc=5.024
- lift (hetero vs hebbian): 0.154 bits (above 0.10 HARD_PASS threshold)
- verdict: HARD_PASS (smoke scale)
- elapsed_s: 35.7s

Fix #28 honest_scope note: at smoke scale, ARM_CFRPE_ONLY (bpc=4.773) outperforms ARM_CFRPE_STDP_HETEROGENEOUS (5.024). The lift I pre-registered is vs ARM_HEBBIAN_ONLY, not vs ARM_CFRPE_ONLY. At production scale, STDP may add or subtract from CFRPE. This is exactly what the cell tests.

Smoke effect size: lift=0.154 vs HARD_PASS bar=0.10; ratio=1.54x. Effect size borderline (1.54x > 1.2x walkback threshold). Sample size adequate (3 seeds at FULL). No walk-back required.

## Timeout Estimate

```
smoke_wall_s = 35.7  (laptop CPU; no GPU)
FULL / smoke ratio: N_DIM 16x, N_STEPS 12.5x, seeds 3x
GPU speedup vs laptop CPU: ~50x (conservative; actual may be higher for matmul)
raw = 35.7 * 16^2 * 12.5 * 3 / 50 = 6854s
margin = 1.5 * 6854 = 10281s
rounded to nearest 300 = 10500s (2.9h)
```

timeout_s = 10500

Flag: run expected ~2.9h. Within 4h limit. Flag for user visibility.

## N-suffix note

Anchor name has no `_n<N>` suffix. Production N_DIM = 8192. No PROT-018 binding required.
(Per role contract: "If the anchor name lacks `_n<N>` suffix, explicitly state production N")

## GPU note (Fix #24)

Script imports torch.cuda; all arms use GPU tensor ops. ARM_CFRPE_ONLY and ARM_CFRPE_STDP_HETEROGENEOUS
use iterative stochastic updates with batched matmul (Ctx @ W^T + outer product). ARM_HEBBIAN_ONLY
uses chunked E_tgt.T @ E_src. Encoder hoisted outside arm loop per Fix #24.
GPU util expected >= 50% for iterative arms.
