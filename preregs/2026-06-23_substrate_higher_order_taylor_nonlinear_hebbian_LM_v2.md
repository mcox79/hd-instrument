# PRE-REG: substrate_higher_order_taylor_nonlinear_hebbian_LM_v2

**Date:** 2026-06-23
**Author:** exp_dev (cell author; sub-agent)
**Cell:** `experiments/exp_substrate_higher_order_taylor_nonlinear_hebbian_LM_v2.py`
**Anchor:** `substrate_higher_order_taylor_nonlinear_hebbian_LM_v2`
**Queue routing:** overnight_queue (GPU; N_DIM=8192 >= Fix #22 threshold)
**Parent prereg:** `preregs/2026-06-23_substrate_higher_order_taylor_nonlinear_hebbian_LM_v1.md`
**VET diagnosis:** `notes/skunkworks_to_all_BATCH_VET_4_recent_negatives_2026-06-23.md` (TARGET 4)
**P_inherited:** 0.45 (same as v1; RESCUE not a new hypothesis)

## Rescue rationale

v1 was IMPLEMENTATION_BUG (CALIBRATION_COLLAPSE_LAMBDA_ZERO):
- v1 LAMBDA_GRID=[0.0, 0.1, 0.3, 0.5, 0.7, 1.0] skipped fair_harness optimal lambda~0.033
- All 5 arms collapsed to best_lambda=0.0 (pure unigram), bpc=7.7378 across ALL arms
- raw_bpc_at_T1_L1 showed real per-arm separation (n1=11.70, n5=11.77) confirming W matrices non-degenerate
- Only fix: expand grid to bracket 0.033

## Fix (v2 -- minimal change)

**LAMBDA_GRID expanded to {0.0, 0.01, 0.02, 0.033, 0.05, 0.1, 0.2, 0.5, 1.0}**
which brackets fair_harness optimal lambda~0.033.
No other mechanism changes vs v1.

Added diagnostics (v2):
- calibration_collapse field per arm (best_lambda=0.0 flag)
- ARM_n1 best_lambda and best_T reported in arm_summary
- Verdict includes CALIBRATION_GRID_TOO_COARSE branch if all arms still collapse

## Hypothesis (unchanged from v1)

Ocker-Buice 2021 (arxiv:2106.15685): nonlinear Hebbian plasticity with
f_n(x)_i = x_i * |x_i|^(n-1) converges to n-th order tensor eigenvectors.
Can this forward-only mechanism lift BPC above the rank-1 Hebbian ceiling?

## Architecture (unchanged from v1)

Five arms sweep polynomial order n in {1,2,3,4,5}:
- ARM_n1: n=1 standard rank-1 Hebbian (should reproduce fair_harness word2vec_dense ~7.72 BPC)
- ARM_n2: quadratic nonlinear Hebbian
- ARM_n3: cubic
- ARM_n4: quartic (Krotov dense-memory regime; target arm for HARD_PASS criterion)
- ARM_n5: quintic

Encoder: DENSE word2vec-projected L2-normalized (NOT sparse-bipolar; required for Ocker-Buice).
Verdict uses LIFT vs ARM_n1 (within-cell rank-1 baseline), not absolute BPC.

## Config (unchanged from v1)

- N_DIM = 8192 (matches fair_harness baseline scale)
- N_TRAIN = 100,000 (text8)
- N_HELD = 20,000
- VOCAB_CAP = 4000
- SEEDS = [7, 17, 23]
- T_GRID: [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
- LAMBDA_GRID (v2): [0.0, 0.01, 0.02, 0.033, 0.05, 0.1, 0.2, 0.5, 1.0]

## Pre-registered HARD bands (same as v1; registered before smoke)

**HARD_PASS (all of):**
- ARM_n4 BPC lift >= +0.30 bits vs ARM_n1 (higher-order storage independently breaks envelope)
- cv across 3 seeds < 0.05 (stable signal)
- ARM_n1 BPC < unigram BPC - 0.05 (rank-1 baseline shows substrate signal)
- zero_llm_calls_at_inference = True

**CHAIN_GRADE_BONUS:**
- ARM_n4 BPC lift >= +0.50 bits (Krotov dense capacity visible at substrate scale)

**MIDDLE_BAND:**
- ARM_n4 BPC lift +0.10 to +0.30 bits (partial mechanism; route to v3 with larger n or iteration)

**HARD_FAIL (any of):**
- ARM_n4 BPC lift <= +0.10 bits (forward-only nonlinear Hebbian insufficient at LM scale)
- ARM_n>=3 collapses to unigram (BPC >= unigram - 0.05)
- ARM_n1 READOUT_DEGEN and calibration grid confirmed sufficient (lambda > 0.0 available but n1 still near unigram)
- cv >= 0.05 at ARM_n4 (mechanism unstable across seeds)
- all_collapse=True after expanded grid (CALIBRATION_GRID_TOO_COARSE branch)

**MANDATORY sanity gate:**
- ARM_n1 best_lambda must be > 0.0 (if still 0.0 with expanded grid: CALIBRATION_GRID_TOO_COARSE)
- ARM_n1 BPC should be ~7.3-7.8 range (word2vec dense at N_DIM=8192)
- If ARM_n1 BPC in range but all higher arms collapse: genuine HARD_FAIL on mechanism

## Timeout estimate

- v1 per-seed wall: ~205-238s per seed (from v1 metrics.json elapsed_s_seed values)
- v2 grid is 9 lambdas x 7 temps = 63 grid points vs v1's 6x7=42; compute overhead ~50% more on joint_sweep
- joint_sweep is CPU-bound (numpy); GPU work (W build + recall) dominates; 50% grid overhead is negligible
- Estimate: ceil(1.5 * 238 * 1 * 3) = ceil(1071) -> 1200s (same as v1)
- Scaling exp: 1.0 (linear in seeds; FULL_N same as smoke-to-full reference)
- timeout_s = 1200

## N-suffix note

Anchor name has no `_n<NUMBER>` suffix. Production N_DIM=8192 (full mode).
No PROT-018 binding applies.

## Honest scope

- Forward-only only (no backprop, no iterative refinement at test time)
- Dense word2vec encoder (static, pre-trained; not substrate-native embedding)
- n=1 arm targets fair_harness ARM_SUBSTRATE_WORD2VEC_DENSE (~7.72 BPC), NOT sparse_bipolar (7.3065)
- HARD_PASS threshold is lift over ARM_n1 within this cell, NOT over fair_harness sparse_bipolar
- This is a RESCUE of v1's calibration-collapse bug -- no new mechanism variations

## Cites

- Ocker-Buice 2021 arxiv:2106.15685
- Krotov-Hopfield 2016 NeurIPS
- preregs/2026-06-23_substrate_higher_order_taylor_nonlinear_hebbian_LM_v1.md (parent)
- notes/skunkworks_to_all_BATCH_VET_4_recent_negatives_2026-06-23.md (VET diagnosis TARGET 4)
- data/exp_fair_harness_substrate_as_lm_v1/metrics.json (baseline reference)
- data/exp_substrate_higher_order_taylor_nonlinear_hebbian_LM_v1/metrics.json (v1 collapse evidence)
