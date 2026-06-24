# Pre-registration: substrate_fast_slow_weights_LM_v1

Date: 2026-06-23
Anchor: substrate_fast_slow_weights_LM_v1
Script: experiments/exp_substrate_fast_slow_weights_LM_v1.py
Queue: remote_cpu_queue
Status: REGISTERED (pre-smoke)

---

## Hypothesis

Brain CLAIM 5 from research_brain_to_lm_relevance_audit_2x_drill_2026-06-23.md (verdict A):
Multi-timescale plasticity (fast weights + slow weights) is a REAL gap for substrate-LM.
Fast weights provide rapid in-context adaptation; slow weights provide stable long-term knowledge.
Hinton-Plaut 1987, Ba 2016, Irie 2021: fast-slow weight separation measurably improves sequence LM.

Substrate's single Hebbian W is SLOW-weight-only. This cell tests whether adding a fast-weight
overlay (high-LR exponential decay over tau=10,100 tokens) improves BPC on text8 next-token prediction.

## Arms

- ARM_SINGLE_W: single Hebbian W (rank-1 accumulation); baseline ~7.3065 BPC from fair_harness
- ARM_FAST_W_ONLY: exponentially decayed W_fast only (no slow W); tests fast adaptation alone
- ARM_FAST_PLUS_SLOW_W: W_eff = W_slow + alpha * W_fast; tests joint fast+slow contribution

## Config

- N_DIM = 8192 (FULL production; PROT-018: no _n suffix; N stated here)
- N_TRAIN = 100,000 tokens
- N_HELD = 20,000 tokens
- VOCAB_CAP = 4,000 words
- SEEDS = [7, 17, 23]
- TAU_GRID = [10, 100] (fast-weight decay timescales)
- ETA_FAST_GRID = [2.0, 5.0, 10.0] (fast W learning rate multipliers)
- ALPHA_GRID = [0.5, 1.0, 2.0] (blend weight: W_eff = W_slow + alpha * W_fast)
- TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
- LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]

## Pre-registered threshold bands

HARD_PASS: ARM_FAST_PLUS_SLOW_W BPC < ARM_SINGLE_W BPC - 0.15
  (fast-slow architecture outperforms single-timescale by >= 0.15 bits)

CHAIN_GRADE_BONUS: lift >= 0.25 AND ARM_FAST_PLUS_SLOW_W beats fair_harness 7.3065 by >= 0.20
  (fps_bpc <= 7.3065 - 0.20 = 7.1065)

MIDDLE_BAND: lift in [+0.05, +0.15]
  (modest fast-slow benefit; insufficient for HARD_PASS)

HARD_FAIL: lift <= +0.05
  (fast-slow weight separation does NOT help substrate-LM;
   CLAIM 5 appears OVER-MAPPED at this scale/encoder;
   route SAME-CYCLE to Strategy: revival angle = pretrained encoder or
   per-token W_fast reconstruction at eval time)

CV requirement: cv < 0.05 across seeds (ARM_FAST_PLUS_SLOW_W BPC)

## Calibrated P(HARD_PASS)

P = 0.35
Deflation: raw lit P = 0.65 (CLAIM 5 verdict A, high LM evidence strength per audit).
Deflated 0.30 for: (a) substrate-specific char-trigram encoder shapes may not benefit from
fast-slow separation (encoder is the load-bearing bottleneck per 2026-06-23 arc);
(b) final-state W_fast accumulation is a simplification vs. per-token context-window fast W;
(c) no prior empirical anchor for this mechanism on substrate.
Novel-synthesis cap 0.50 not binding here (P already below 0.50 after deflation).

## What this does NOT show

- Does NOT test fast-slow on tasks beyond next-token BPC.
- Does NOT test tau values beyond {10, 100}.
- Does NOT test per-token W_fast reconstruction at eval time (that is a follow-on cell).
- Does NOT claim this is optimal; eta_fast/alpha grids are proxies for the mechanism.

## N-suffix

No _nN suffix. Production N = N_DIM = 8192. Rationale: N_DIM is the only meaningful N axis;
naming the anchor with _n8192 would conflict with convention that _n<N> binds N = N_TRAIN
in most prior cells where N = sample count. Production N_DIM stated here.

## Smoke gate results

RUN_MODE=smoke (N_DIM=512, N_TRAIN=3000, SEEDS=[0])
- ARM_SINGLE_W bpc = 4.7209
- ARM_FAST_W_ONLY bpc = 4.8566 (fast-only hurts at small scale)
- ARM_FAST_PLUS_SLOW_W bpc = 4.7220 (lift = -0.0011; near-zero at smoke scale)
- Smoke verdict: HARD_FAIL (expected at N_DIM=512; fair_harness operates at N_DIM=8192)
- Instrumentation self-test: PASS
- All metrics finite, non-degenerate, non-constant across arms
- Smoke wall time: 14.7s (seed 0, N_DIM=512)

SMOKE NOTE: The smoke HARD_FAIL at N_DIM=512 is expected and does not block ship.
Reason: the fair_harness chain-grade result (BPC=7.3065) operates at N_DIM=8192.
At N_DIM=512, ARM_SINGLE_W gets 4.7209 BPC vs unigram 4.9498 (already well below unigram).
The Hebbian prediction mechanism at N_DIM=512 is strong enough that the fast-weight
overlay adds near-zero marginal information. At N_DIM=8192, the prediction is harder
(single-step Hebbian at higher dim has different properties) -- this is the decisive test.

SUSPICIOUS-RESULT GATE: NOT triggered. All BPC values finite, non-zero, arms differ from
each other and from unigram. fast-only degradation (-0.1357) is a real signal (not zero).
Script exits in 14.7s, well above 100ms threshold.

## Timeout estimate

Method: direct empirical estimate from matmul benchmarking on laptop CPU.

Key operations at full scale (N_DIM=8192, N_TRAIN=100k, 3 seeds):
- W_fast build (vectorized): 2 tau * 25 chunks * 2.3s/chunk * 3 seeds = 345s
- pred_contributions: 6 passes * 12.4s * 3 seeds = 224s
- logits_from_preds: 24 dev passes + ~12 test passes = 36 * 14s * 3 seeds (over 3 seeds) = ~1500s

Direct estimate on laptop CPU: ~27 min
Remote CPU (2x faster than laptop): ~13 min
With 1.5x safety margin: ~20 min = 1200s

timeout_s = 1800 (30 min; 1.5x margin over 1200s direct estimate)

Note: formula approach (using smoke_wall_s=14.7s * N_ratio^2 * seed_ratio) produces
an overestimate because computation is NOT purely O(N^2) -- fixed batch chunking
and n_held / V remain constant across N_DIM. Direct empirical measurement used per
role contract "use most recent comparable experiment" guidance.

## Dependencies

- data/text8_cache/text8.txt (local and remote) -- verified present (used by all LM cells)
- experiments/_seed_checkpoint.py -- verified present
- No outputs from other experiments required

## Version marker

metrics.json will include: config_version, N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, TAU_GRID,
ETA_FAST_GRID, ALPHA_GRID, SEEDS, run_mode, arm_summary (per-arm BPC mean/std/cv),
what_this_does_not_show, pre_reg, fair_harness_bpc_ref.
