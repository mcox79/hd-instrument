# 2026-06-24 substrate_sequence_modeling_production_v1

## Anchor
`substrate_sequence_modeling_production_v1`

## Status
- Prereg authored 2026-06-24 (exp_dev)
- Queue: `remote_cpu_queue` OR `local_cpu_queue` (CPU; numpy-only)
- Timeout: 3600s (1h safety; full estimated 25-30 min wall on remote CPU)
- Estimated wall: ~25-30 min CPU full (3 seeds * 5 arms * 40k tokens)

## Cell
`experiments/exp_substrate_sequence_modeling_production_v1.py`

## Why now (USER directive 2026-06-24)

USER: "sequence modelling - I think we could get very good here too."

The substrate has TWO chain-grade sequence primitives:
- **c3 sequence-binding** (cert atom 586): SequenceMatrix `S` Hebbian-binds
  ordered pairs; HARD_PASS at every depth [1,3,5,7,10] on K=20 N_DIM=4096.
- **g1b autoregressive generation** (cert atom 587): generation primitive ships.

But these are PRIMITIVES, not production-scale LM evaluation. The honest test
is: can substrate sequence-binding + cf-RPE online learning, on the established
text8 word-level harness, beat a real-LM baseline (word-bigram)?

## Honest re-cast (Step 0)

Task brief cited "char_bigram ~6.5 BPC" as the real-LM baseline. The established
LM harness in this repo (fair_harness_substrate_as_lm_v1) operates at **word-
level** on text8 with UNIGRAM_BPC_REF=7.738 word-BPC and landed substrate fair-
harness bpc_best ~7.31 word-BPC. To preserve apples-to-apples with that landed
substrate measurement and to test USER intent honestly ("substrate beats real-LM
baseline"), this cell uses **word-level** evaluation with **word-bigram add-
alpha** as the real-LM baseline. Word-bigram with add-alpha=0.1 on text8 word-
level should land in [6.30, 6.90] word-BPC -- a real LM that beats unigram by
~1-1.4 bits with order information; the comparable real-LM threshold at word-
level.

## Arms (5)

1. **ARM_UNIGRAM** -- analytic word-unigram floor (alpha=0.1). Reference ~7.74.
2. **ARM_WORD_BIGRAM** -- add-alpha=0.1 word-bigram conditional. Real-LM
   baseline (expected ~6.3-6.9 word-BPC; hard-cap 7.40 for "broken").
3. **ARM_CONTEXT_FREE_SUBSTRATE** -- rank-1 Hebbian W on word2vec-projected
   encoder; mirrors fair_harness ARM_SUBSTRATE_WORD2VEC_DENSE. Sanity rail
   `bpc_best in [7.21, 7.41]` (within +/-0.10 of landed 7.3065).
4. **ARM_SEQUENCE_BIND_K8** -- c3 `SequenceMatrix S` over K=8 lookback words;
   k_ctx_t = sum_{i=1..K} HRR(E[w_{t-i}], P_i). S += outer(E[w_t], k_ctx_t).
   Predict: pred = S @ k_ctx; logits = cos(pred, E).
5. **ARM_SEQUENCE_BIND_K16_CFRPE** -- K=16 + cf-RPE delta-rule online: at each
   eval position, after scoring with current S, apply
   `S += eta * outer(E[w_t] - pred, k_ctx_t)`. Eta=0.05.

## Config (PRODUCTION CPU)

- V=4000 vocab, N_TRAIN=40_000 text8 tokens, N_HELD=8_000
- N_DIM=8192, seeds=[7, 17, 23]
- Encoder: word2vec-google-news-300 (defensive gensim loader; char-trigram fallback for OOV / smoke)
- K_SHORT=8, K_LONG=16, LOCK_IN_FREQ_STEP=31, CFRPE_ETA=0.05, BIGRAM_ALPHA=0.1
- Joint (T, lambda) sweep on dev half: TEMP_GRID [0.01..1.0], LAMBDA_GRID [0..1]
- Substrate-only-decode: zero LLM forward calls at inference; encoder is static
  open-weight word2vec lookup (no LLM)
- numpy-only on CPU; no torch device dependency

## Reported metrics per arm

- `bpc_best` (at best joint (T*, lambda*) on dev; reported on test)
- `top1_acc`
- `mrr_at_10`
- `best_T_for_bpc`, `best_lambda_for_bpc`
- `raw_bpc_at_T1_L1` (sanity / DEGEN check)

## Pre-reg HARD bands

### Sanity rail (smoke + full)
ARM_CONTEXT_FREE_SUBSTRATE `bpc_best_mean` within +/-0.10 of 7.3065 (i.e.
`[7.21, 7.41]`). Outside this band -> harness mis-spec; cannot interpret
sequence arms.

### Word-bigram calibration (full)
`ARM_WORD_BIGRAM bpc_best_mean <= 7.40` (hard-cap; expected [6.30, 6.90]).
Above hard-cap -> baseline broken; cannot evaluate HP.

### HARD_PASS (substrate sequence-modeling clears real-LM baseline)
- `ARM_SEQUENCE_BIND_K16_CFRPE bpc_best_mean <= ARM_WORD_BIGRAM bpc_best_mean - 0.10`
- AND `cv` across seeds for K16+cfRPE `<= 0.05`
- AND `zero_llm_calls_at_inference == True`
- AND sanity rail satisfied
- AND bigram calibration satisfied

### CHAIN_GRADE_BONUS
`ARM_SEQUENCE_BIND_K16_CFRPE bpc_best_mean <= ARM_WORD_BIGRAM bpc_best_mean - 0.30`
(substrate sequence-modeling DECISIVELY beats word-bigram).

### MIDDLE_BAND
`ARM_SEQUENCE_BIND_K16_CFRPE bpc_best_mean` beats word-bigram by < 0.10 bits, OR
ARM_SEQUENCE_BIND_K8 beats word-bigram but K16+cfRPE does not.

### HARD_FAIL
- K16+cfRPE does NOT beat word-bigram (`delta <= 0`), OR
- Substrate-only-decode gate violated (`n_llm > 0`), OR
- Sanity rail violated, OR
- Word-bigram baseline broken (`bpc > 7.40`).

## Discriminating regime (Fix #16)

The 5-arm contrast IS the discriminator:
- All substrate arms collapse to each other within 0.05 -> sequence-binding
  mechanism is NULL (honest negative).
- ARM_SEQUENCE_BIND_K8 ~= ARM_CONTEXT_FREE_SUBSTRATE -> sequence binding alone
  doesn't help; cf-RPE may still rescue.
- ARM_SEQUENCE_BIND_K16_CFRPE clears word-bigram -> mechanism load-bearing.

## Formula self-tests

T1: word-bigram row-stochastic under add-alpha smoothing.
T2: HRR bind shape-preserved + non-trivial norm.
T3: SequenceMatrix bind_pair(a,b) -> predict_next(a) has higher cosine to b
    than to a random vector c.
T4: cf-RPE delta-rule with positive eta does not increase ||true - pred||_2.
T5: K=8 context vector is non-zero with norm > 0.01.
T6: bpc_from_logp on planted exactly reproduces unigram BPC at lambda=0.
T7: Verdict bands HP / CG / MID / HF / sanity-fail classify correctly on
    planted arm-data.
T8: `_LLM_CALL_COUNTER[0] == 0` after self-test.

## Honest scope

- Word-level text8; not char-level (USER framing's "char_bigram" is preserved as
  intent -- a real-LM baseline -- but instantiated at word-level for apples-to-
  apples with the established harness; documented in cell docstring).
- CPU-only numpy implementation; matmul-heavy arms (rank-1 W and sequence
  S = N_DIM x N_DIM = 8192 x 8192 ~ 256MB; ingest chunks 2048).
- cf-RPE online update is per-position (online); eta=0.05; no hyperparam sweep.
- Encoder is shared across substrate arms (apples-to-apples; only the binding
  layer differs).
- Sanity rail is the CAN-fail gate: if it fails, mechanism arms are not
  interpretable.

## Cites

- `experiments/exp_fair_harness_substrate_as_lm_v1.py` (parent harness)
- `experiments/exp_c3_compressed_sequence_replay_v1.py` (c3 primitive)
- `experiments/exp_g1b_capacity_sweep_v1.py` (g1b generation)
- `hdlab/sequence_memory.py` (SequenceMatrix primitive)
- USER_2026-06-24_sequence_modelling_we_could_get_very_good
- USER_2026-06-22_Fix24 (zero-LLM at inference)
- META_2026-06-22_no-Hebbian-window (offline-pass vs online software-arch)
