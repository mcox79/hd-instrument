# PRE-REG: substrate_higher_order_taylor_nonlinear_hebbian_LM_v1

**Date:** 2026-06-23
**Author:** exp_dev (cell author; sub-agent)
**Cell:** `experiments/exp_substrate_higher_order_taylor_nonlinear_hebbian_LM_v1.py`
**Anchor:** `substrate_higher_order_taylor_nonlinear_hebbian_LM_v1`
**Queue routing:** overnight_queue (GPU; N_DIM=8192 >= Fix #22 threshold)
**Parent research:** `notes/research_rank1_hebbian_brain_escape_mechanisms_2026-06-23.md`
**Hand-off:** `notes/exp_dev_handoff_research_rank1_hebbian_brain_escape_mechanisms_2026-06-23.md`
**P_inherited:** 0.45 (Ocker-Buice brain-grounded forward-only; deflated from P=0.55 for substrate-native LM-scale application per research note)

## Hypothesis

Ocker-Buice 2021 (arxiv:2106.15685) proves that nonlinear Hebbian plasticity with
polynomial nonlinearity f_n(x)_i = x_i * |x_i|^(n-1) applied to L2-normalized
input vectors converges to n-th order tensor eigenvectors of input correlations.
This is the same decomposition Krotov-Hopfield 2016 dense associative memory uses.

At LM scale with word2vec-projected dense encodings, can this forward-only mechanism
(no backprop) lift BPC above the rank-1 Hebbian ceiling (ARM_n1 baseline) by
accumulating meaningful higher-order correlations in the W matrix?

## Architecture

Five arms sweep polynomial order n in {1,2,3,4,5}:
- ARM_n1: n=1 standard rank-1 Hebbian (fair_harness word2vec baseline ~7.72 BPC)
- ARM_n2: quadratic nonlinear Hebbian
- ARM_n3: cubic
- ARM_n4: quartic (Krotov dense-memory regime; target arm for HARD_PASS criterion)
- ARM_n5: quintic

Encoder: DENSE word2vec-projected L2-normalized (NOT sparse-bipolar).
Reason: Ocker-Buice requires |x_i| ~ 1/sqrt(N); sparse-bipolar |x_i| ~ 1/sqrt(k)
causes n-th power to collapse for k<<N at n>=2.

Verdict uses LIFT vs ARM_n1 (within-cell rank-1 baseline), not absolute BPC.

## Config

- N_DIM = 8192 (matches fair_harness baseline scale)
- N_TRAIN = 100,000 (text8)
- N_HELD = 20,000
- VOCAB_CAP = 4000
- SEEDS = [7, 17, 23]
- Joint (T, lambda) sweep: T in [0.01,0.02,0.05,0.1,0.2,0.5,1.0], lambda in [0.0,0.1,0.3,0.5,0.7,1.0]
- Same evaluation protocol as fair_harness: BPC + top-1 + MRR@10

## Pre-registered HARD bands (registered before smoke, before queuing)

**HARD_PASS (all of):**
- ARM_n4 BPC lift >= +0.30 bits vs ARM_n1 (higher-order storage independently breaks envelope)
- cv across 3 seeds < 0.05 (stable signal)
- ARM_n1 BPC < unigram BPC - 0.05 (rank-1 baseline reproduces expected word2vec signal)
- zero_llm_calls_at_inference = True

**CHAIN_GRADE_BONUS:**
- ARM_n4 BPC lift >= +0.50 bits (Krotov dense capacity visible at substrate scale)

**MIDDLE_BAND:**
- ARM_n4 BPC lift +0.10 to +0.30 bits across n (partial mechanism; route to v2 with larger n or iterative cleanup)

**HARD_FAIL (any of):**
- ARM_n4 BPC lift <= +0.10 bits (forward-only nonlinear Hebbian insufficient at LM scale)
- ARM_n>=3 collapses to unigram (BPC >= unigram - 0.05) (higher-order interactions degenerate)
- ARM_n1 READOUT_DEGEN (rank-1 baseline fails: pipeline broken)
- cv >= 0.05 at ARM_n4 (mechanism unstable across seeds)

## Falsifiable predictions

| Prediction | HARD_PASS | HARD_FAIL |
|---|---|---|
| n-th order nonlinearity accumulates n-th order correlations | n4 lift >= +0.30 | n4 lift <= +0.10 |
| Monotonic improvement possible | n4 <= n3 <= n2 <= n1 (lower BPC) | ordering inverts (n4 > n3 > n2 > n1) |
| Mechanism scale-stable | cv < 0.05 | cv >= 0.05 |

## Timeout estimate

- Smoke wall: ~0.4s (N_DIM=512, N_TRAIN=2000, 1 seed, Gaussian CPU fallback)
- Fair_harness per-seed per-arm GPU elapsed: ~42s (from metrics.json)
- 5 arms * 42s/arm * 3 seeds = 630s
- Formula: ceil(1.5 * 42 * 5 * 3) = ceil(945) -> 1200s
- timeout_s = 1200
- Note: this is sub-2hr; within normal GPU slot limits.

## Honest scope

- Forward-only only (no backprop, no iterative refinement at test time)
- Dense word2vec encoder (static, pre-trained; not substrate-native embedding)
- n=1 arm does NOT reproduce fair_harness sparse_bipolar (7.3065); it reproduces
  fair_harness word2vec_dense (~7.72). The HARD_PASS threshold is lift over n=1 arm
  within this cell, NOT over fair_harness sparse_bipolar.
- If HARD_FAIL: Ocker-Buice forward-only is insufficient at LM scale with static
  word2vec; a substrate-native iterative cleanup mechanism may be needed (CERT 588
  refuse-gate cleanup as CA3-equivalent is the next candidate).

## N-suffix note

Anchor name has no `_n<NUMBER>` suffix. Production N_DIM=8192 (full mode).
No PROT-018 binding applies.

## Cites

- Ocker-Buice 2021 arxiv:2106.15685
- Krotov-Hopfield 2016 NeurIPS
- notes/research_rank1_hebbian_brain_escape_mechanisms_2026-06-23.md
- notes/exp_dev_handoff_research_rank1_hebbian_brain_escape_mechanisms_2026-06-23.md
- data/exp_fair_harness_substrate_as_lm_v1/metrics.json (baseline ARM_SUBSTRATE_SPARSE_BIPOLAR BPC=7.3065)
- notes/exp_dev_att1_v2_krotov_pre_reg_2026-06-23.md (parallel Krotov drill at att1 scale)
