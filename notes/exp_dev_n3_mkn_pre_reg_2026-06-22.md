# PRE-REG: n3_mkn_smoothing_v1 (Path B sub-area b, #1 revival angle of n3 SimVQ HONEST_NEGATIVE)

**Date:** 2026-06-22
**Author:** exp_dev (cell author)
**Cell:** `experiments/exp_n3_mkn_smoothing_v1.py`
**Anchor:** `n3_mkn_smoothing_v1`
**Queue:** `remote_cpu_queue` (pythia residuals + token_ids live on marsh@home)

## Motivation
- Skunkworks n3 SimVQ LANDED_VET commit `4c086a9f` (2026-06-22): SimVQ MVP HONEST_NEGATIVE; PCA projection HURT ceiling_bpc at every PD. Sub-area (a) ruled out for the MVP form.
- Decode-side bottleneck DIAGNOSIS stands: substrate_bpc - ceiling_bpc ~ 2.9 bits at every PD across N2/N3.
- Research drill (`notes/research_decode_side_lm_improvements_substrate_native_2026-06-22.md`) sub-area (b) = Modified Kneser-Ney smoothing. Calibrated P(>=0.10 bits gain) ~ 0.55 (highest among smoothing options). Mechanism: MKN absolute discounting + continuation-probability lower-order distribution reduces over-confidence in sparse-concept low-count predictions.

## Cell design
- Fixed (V_C=1024, N_DIM=16384, K=1, F_SPARSE=0.006) -- matches N2 best config.
- Identity VQ (no projection) -- n3 SimVQ HN ruled out projection.
- Two-arm sweep (decode-time only): ARM A = Jelinek-Mercer (anchor; reproduces N2 4.959); ARM B = Modified Kneser-Ney (Chen-Goodman 1998; absolute discount + continuation prob).
- Same VQ, same C, same D-store, same train counts across both arms; only `batched_token_logprob` differs.
- ceiling_bpc identical between arms (sanity invariant; asserted in T7 selftest).
- 3 seeds {7, 17, 23}.

## MKN implementation
- D = n_1 / (n_1 + 2 * n_2) (optimal discount per Chen-Goodman); clipped to [0.1, 0.99].
- P_MKN(t|c) = max(n_ct - D, 0) / count_c + gamma(c) * P_cont(t).
- gamma(c) = (D / count_c) * n1plus_c_dot[c] (per-concept normalizer).
- P_cont(t) proportional to n1plus_dot_t (# distinct concepts containing t), NOT raw frequency.
- Fallback for never-observed concept: use P_cont directly. Numerical fallback for any zero-sum row: uniform.

## Pre-registered bands (user task spec 2026-06-22; pre-reg-direction-must-match-intent per n3 SimVQ catch)
**HARD_PASS (chain-grade, ALL of):**
- MKN substrate_bpc <= 4.86 (>= 0.10 bits drop from JM anchor 4.959)
- cv across seeds <= 0.05 for MKN arm
- ARM A (JM) reproduces N2's 4.959 within 0.05 bits (ANCHOR-OK)
- NOT saturated (alpha < 1.0)
- substrate-only-decode (zero LLM calls at inference -- enforced + asserted)

**MIDDLE_BAND:**
- MKN improves substrate_bpc by 0.03-0.10 bits vs JM

**HARD_FAIL (ANY of):**
- MKN improvement < 0.03 bits (mechanism doesn't reduce within-concept entropy materially)
- MKN substrate_bpc WORSE than JM (any wrong-direction delta = HARD_FAIL per pre-reg-direction-must-match-intent; n3 SimVQ catch)
- ARM A anchor mismatch (>0.05 bits from N2 4.959)
- substrate-only gate violated (LLM forward calls > 0)

## Pre-flight discipline (Section 7a + Director Fix 3 + Skunkworks n3 disciplines)
1. **--self-test PASSES on .venv:** 11/11 selftests green. Validated locally 2026-06-22.
2. **REQUIRED_FIELDS metrics:** verdict, verdict_msg, elapsed_s, summary, per_seed[].per_unit[].{substrate_bpc, ceiling_bpc, cv at verdict-time, zero_llm_calls_at_inference, mkn_D}.
3. **Per-seed runtime measurement:** to be measured by running ONE seed at full scale on remote before dispatching the full 3-seed run. Reports below.
4. **Zero-D-overlap fallback** in `batched_token_logprob_jm` (mirrors n3 SimVQ pattern); MKN has its own zero-concept/zero-row fallback. Both validated in T4+T6 selftests.
5. **pre-reg-direction-must-match-intent verdict() pattern:** wrong-direction delta (MKN worse than JM) = HARD_FAIL, NOT MIDDLE_BAND.
6. **Substrate-only-decode gate:** zero `model(`/`forward(`/`generate(`/`AutoModel` at inference; pythia at ingest only. MKN is pure-Python count-based -- naturally substrate-only. T8 selftest asserts `_LLM_CALL_COUNTER == 0`.
7. **CONFIG_VERSION:** captures `SMOOTH=jm-mkn,V_C=1024,N_DIM=16384,K=1,f=0.0060,LAM=0.10,MKN_D=optimal-clip[0.10,0.99],MAX_DOCS=100000,SEEDS=7-17-23,SPLIT=0.8`. Invalidates checkpoints if changed (PROT-021 guard).
8. **Checkpoint:** imports `_seed_checkpoint`; per-seed partial write + resume.

## Sanity invariant (T7 selftest, additional discipline)
ceiling_bpc IDENTICAL between JM and MKN arms (same VQ + same train counts; only decode differs). If ceiling_bpc diverges in the run, the harness is broken.

## Anchor reproduction check (the load-bearing baseline)
ARM A (JM) substrate_bpc at full scale (3 seeds, V_C=1024, N_DIM=16384, K=1) should be within 0.05 bits of N2's 4.959. Anchor mismatch -> HARD_FAIL (cannot interpret MKN delta without valid baseline).
