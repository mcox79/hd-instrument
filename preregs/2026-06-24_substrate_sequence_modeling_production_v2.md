# 2026-06-24 substrate_sequence_modeling_production_v2

## Anchor
`substrate_sequence_modeling_production_v2`

## Status
- Prereg authored 2026-06-24 (exp_dev)
- Queue: `remote_cpu_queue` (numpy CPU; ~25-30 min estimated wall on remote)
- Timeout: 3600s (1h safety)
- Cell: `experiments/exp_substrate_sequence_modeling_production_v2.py`

## Why v2 (v1 HARD_FAIL post-mortem)

v1 landed HARD_FAIL with `bpc_word_bigram=9.011 > unigram=8.239`. Root cause:
**BIGRAM_ALPHA = 0.1** at V=4000 places pseudocount 0.1 in every cell of
`counts[V, V]`, so per-row smoothing-mass = V * alpha = **400** while typical
real bigram counts per source row = N_TRAIN/V = **10**. Real-signal weight in
`P(w | prev)` = 10/(10+400) = **2.4%** -> word-bigram baseline collapsed
toward uniform-over-V (which is HIGHER bpc than unigram, since unigram
exploits frequency-rank). The substrate-arm metrics in v1 were honest
(substrate logits independent of the bigram count table), so v1 smoke at
V=200 still showed K16+cfRPE beating word-bigram by 0.37 bits. The full-V
verdict reversal was a baseline-calibration bug, not a substrate failure.

## v2 fix

**One-line change**: `BIGRAM_ALPHA = 0.1 -> 0.001`.

New smoothing-mass = V * alpha = **4**, real-signal weight = 10/(10+4) =
**71%**. Word-bigram baseline now operates as intended.

Additional housekeeping:
- BIGRAM_BPC_MIN widened: 6.30 -> 5.30 (alpha=0.001 yields LOWER bigram
  bpc than alpha=0.1; the 6.30 lower bound is no longer the natural floor).
- New formula self-test T1b: arithmetic check that alpha=0.001 yields
  >25x prob and >4 bits improvement on the planted V=4000 N_row=10 c=10
  regime (verifies the fix magnitude matches the v1-bug magnitude).
- WHAT_THIS_DOES_NOT_SHOW clause appended to every verdict_msg path
  (HARD_PASS / HARD_FAIL / MIDDLE_BAND) per Fix #30 / verdict_lint.
- `preflight_spec.yaml` filed at `data/exp_substrate_sequence_modeling_production_v2/`
  (Fix #29 5-section gate; preflight_check PASS).

## Arms (5; SAME as v1; substrate logic byte-identical)

1. **ARM_UNIGRAM** -- analytic word-unigram floor (alpha=0.1). Reference ~7.74.
2. **ARM_WORD_BIGRAM** -- add-alpha=**0.001** word-bigram conditional. Real-LM
   baseline (expected [5.30, 6.90] word-BPC; hard-cap 7.40 for "broken").
3. **ARM_CONTEXT_FREE_SUBSTRATE** -- rank-1 Hebbian W on word2vec-projected
   encoder; mirrors fair_harness ARM_SUBSTRATE_WORD2VEC_DENSE. Sanity rail
   `bpc_best in [7.21, 7.41]` (within +/-0.10 of landed 7.3065).
4. **ARM_SEQUENCE_BIND_K8** -- c3 SequenceMatrix S over K=8 lookback words.
5. **ARM_SEQUENCE_BIND_K16_CFRPE** -- K=16 + cf-RPE delta-rule online; eta=0.05.

## Config (PRODUCTION CPU; SAME as v1)

- V=4000 vocab, N_TRAIN=40_000 text8 tokens, N_HELD=8_000
- N_DIM=8192, seeds=[7, 17, 23]
- Encoder: word2vec-google-news-300 (gensim loader; char-trigram OOV fallback)
- K_SHORT=8, K_LONG=16, LOCK_IN_FREQ_STEP=31, CFRPE_ETA=0.05
- **BIGRAM_ALPHA=0.001** (was 0.1; THIS is the v2 fix)
- Joint (T, lambda) sweep on dev half: TEMP_GRID [0.01..1.0], LAMBDA_GRID [0..1]
- Substrate-only-decode: zero LLM forward calls at inference
- numpy-only on CPU; no torch device dependency

## Reported metrics per arm

Per Fix #28 (per-arm metrics, NOT verdict_msg framing): each arm reports
`bpc_best_mean`, `bpc_best_cv`, `top1_acc_mean`, `mrr_at_10_mean`,
`raw_bpc_at_T1_L1`, `best_T_for_bpc`, `best_lambda_for_bpc` in
`metrics.json` `detail.by_arm_agg`.

## Pre-reg HARD bands

### Sanity rail (full only; smoke deferred at V=200)
ARM_CONTEXT_FREE_SUBSTRATE `bpc_best_mean` within +/-0.10 of 7.3065.

### Word-bigram calibration (full only; v2)
`ARM_WORD_BIGRAM bpc_best_mean <= 7.40` (hard-cap; expected [5.30, 6.90]).
Above hard-cap -> baseline broken; cannot evaluate HP.

### HARD_PASS (substrate sequence-modeling clears real-LM baseline)
- `ARM_SEQUENCE_BIND_K16_CFRPE bpc_best_mean <= ARM_WORD_BIGRAM bpc_best_mean - 0.10`
- AND `cv` across seeds for K16+cfRPE `<= 0.05`
- AND `zero_llm_calls_at_inference == True`
- AND sanity rail satisfied
- AND bigram calibration satisfied

### CHAIN_GRADE_BONUS
`ARM_SEQUENCE_BIND_K16_CFRPE bpc_best_mean <= ARM_WORD_BIGRAM bpc_best_mean - 0.30`

### MIDDLE_BAND
`ARM_SEQUENCE_BIND_K16_CFRPE bpc_best_mean` beats word-bigram by < 0.10 bits, OR
ARM_SEQUENCE_BIND_K8 beats word-bigram but K16+cfRPE does not.

### HARD_FAIL
- K16+cfRPE does NOT beat word-bigram (`delta <= 0`), OR
- Substrate-only-decode gate violated, OR
- Sanity rail violated, OR
- Word-bigram baseline broken (`bpc > 7.40`).

## Discriminating regime

5-arm contrast IS the discriminator:
- If all substrate arms collapse within 0.05 -> sequence-binding NULL.
- If K8 == CONTEXT_FREE -> sequence binding alone is null; cf-RPE may rescue.
- If K16+cfRPE clears word-bigram -> mechanism load-bearing.

## Formula self-tests (run on every invocation; v2 adds T1b)

T1: word-bigram row-stochastic under add-alpha smoothing.
**T1b (new in v2)**: at V=4000 c=10 N_row=10 regime, alpha=0.001 yields
   >25x prob and >4 bits/token vs alpha=0.1 (arithmetic check matching
   the v1-bug magnitude). Also: monotonic on small-V planted toy.
T2: HRR bind shape-preserved + non-trivial norm.
T3: SequenceMatrix bind_pair round-trip.
T4: cf-RPE delta-rule does not increase ||true - pred||_2.
T5: K=8 context vector norm > 0.01.
T6: bpc_from_logp reproduces unigram BPC at lambda=0.
T7: Verdict bands classify HP / CG / MID / HF / sanity-fail correctly.
T8: `_LLM_CALL_COUNTER[0] == 0`.

## Smoke results (2026-06-24)

V=200 N_TRAIN=1500 N_HELD=300 N_DIM=256 single-seed=0:

| Arm | bpc_best | top1_acc | mrr@10 | raw_bpc_T1L1 |
|---|---|---|---|---|
| ARM_UNIGRAM | 4.752 | 0.4494 | 0.5044 | -- |
| ARM_WORD_BIGRAM | 5.476 | 0.4382 | 0.5336 | -- |
| ARM_CONTEXT_FREE_SUBSTRATE | 4.503 | 0.4494 | 0.5035 | 7.190 |
| ARM_SEQUENCE_BIND_K8 | 4.572 | 0.4494 | 0.5067 | 7.206 |
| ARM_SEQUENCE_BIND_K16_CFRPE | 4.570 | 0.4494 | 0.5067 | 7.210 |

Verdict at smoke: HARD_PASS_CHAIN_GRADE_BONUS (delta K16 vs bigram = +0.906
bits). Smoke confirms harness + 5 arms + verdict logic execute end-to-end;
top1 identical across arms is a small-N saturation artifact at V=200 (89
test positions; not a regression). Smoke v1 showed the SAME identical top1
pattern -- this is an inherent property of the V=200 smoke regime, not a
v2 bug.

The v2 fix CANNOT be smoke-validated for the bigram-calibration regime --
at V=200 alpha*V = 20 vs N/V = 7.5 (smoothing-mass still dominates but
weakly); the v1 bug only manifests strongly at V=4000 (alpha*V = 400 vs
N/V = 10). Hence the formula self-test T1b is the load-bearing v2-fix
validation, not the smoke run.

## Smoke gate disposition

- `_selftest()` PASS (all T1, T1b, T2-T8)
- End-to-end smoke EXECUTES (no errors; metrics.json + per-seed partial written)
- `tools/preflight_check.py data/exp_substrate_sequence_modeling_production_v2` PASS
- `tools/verdict_lint.py data/exp_substrate_sequence_modeling_production_v2_smoke/metrics.json` PASS

## Cites

- `experiments/exp_substrate_sequence_modeling_production_v1.py` (v1; HARD_FAIL)
- `preregs/2026-06-24_substrate_sequence_modeling_production_v1.md` (v1 prereg)
- `experiments/exp_fair_harness_substrate_as_lm_v1.py` (parent harness; CF sanity)
- `experiments/exp_c3_compressed_sequence_replay_v1.py` (c3 primitive)
- `experiments/exp_g1b_capacity_sweep_v1.py` (g1b generation)
- `hdlab/sequence_memory.py` (SequenceMatrix primitive)
- USER_2026-06-24_sequence_modelling_we_could_get_very_good
- USER_2026-06-22_Fix24 (zero-LLM at inference)
- META_2026-06-22_no-Hebbian-window (offline-pass vs online software-arch)

## Stakes (USER directive)

v1 smoke showed substrate K16+cfRPE BEAT word-bigram by 0.37 bits at small
scale. If v2 reproduces at full V=4000 (with corrected bigram calibration),
**substrate-as-LM clears the word-bigram threshold -- first cell to do so**.
This would land the first chain-grade-eligible substrate-as-LM result on
text8 word-level with a real-LM baseline (not the rank-1 W floor of the
fair-harness landed 7.31).
