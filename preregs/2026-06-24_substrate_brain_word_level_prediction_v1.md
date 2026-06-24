# Pre-registration: substrate_brain_word_level_prediction_v1

**Date:** 2026-06-24
**Anchor:** substrate_brain_word_level_prediction_v1
**Queue:** remote_cpu_queue
**N:** N_DIM=2048, **Seeds:** [7, 17, 23], **K:** [1, 5, 10] (PRIMARY arm = K=5)

## Scientific question

Does the substrate, measured at brain-natural WORD grain (V_word=4000 on text8 hold-out)
with K-word HRR context binding, beat the WORD-BIGRAM baseline -- the real "easy LM"
threshold? Prior 30+ char-level mechanisms this session may have been bounded by char-grain
baselines that are unnaturally strong vs brain's measured ~5Hz word-reading rate. This is
the FIRST word-grain probe; closes skepticism axes A2 (unigram baseline too weak) and A10
(text8 char corpus may be wrong test).

## Pre-registered bands

**HARD-PASS:**
- S_K5 top1 >= 1.30 * B2_word_bigram_top1 AND
- S_K5 BPW <= B2_word_bigram_BPW - 0.4 bits

**MIDDLE:** S_K5 top1 lift in [1.10x, 1.30x] over B2 OR S_K5 BPW margin in [B2-0.4, B2-0.1].

**HARD-FAIL:** S_K5 top1 <= B2_top1 OR S_K5 BPW >= B2_BPW (substrate doesn't beat bigram).

## Calibration rationale

Word-bigram is the real aliveness threshold for an LM. word-unigram is the trivial floor
(any frequency counter clears it). 1.30x top1 lift over bigram is a 30% relative
improvement -- a meaningful margin given text8 word-bigram on V=4000 typically scores top1
in the 0.18-0.25 range (so HP target is ~0.25-0.33 absolute top1). The 0.4-bit BPW margin
is calibrated against the substrate-as-LM fair-harness reference (BPC margin 0.3 was the
parent's HP bar; 0.4 bits at WORD grain is comparable since word-BPW units are larger
than char-BPC). 1.10x is the smallest practically meaningful lift (sub-0.10x lift is
statistical noise on 3 seeds + 10K test tokens). The 0.1-bit MIDDLE floor avoids
classifying noise-level wins as substantive.

## N-suffix section

Anchor name has NO _n<N> suffix (PROT-018 does not apply). The cell uses N_DIM=2048
(CPU-tractable for V=4000 logit matmul on remote_cpu_queue). The arm parameter is K
(context window), enumerated [1, 5, 10]; PRIMARY arm is K=5.

## Timeout estimate

Smoke ~ 4.5s at N_TRAIN=8000, V=400, N_DIM=512, K=[1,5,10], seeds=1.
FULL: N_TRAIN=200000 (25x), V=4000 (10x), N_DIM=2048 (4x), seeds=3.

Dominant cost is substrate-logits matmul O(n_query x N_DIM x V) per K per seed.
formula: ceil(1.5 * 4.5 * (200000/8000)**1.0 * (4000/400)**1.0 * (2048/512)**1.0 * (3/1)) = 40500s

This is much too generous (smoke included Python overhead). Empirically a V=4000,
N_DIM=2048, N_TRAIN=200K seeded run with 3 context-K values takes ~5-10 minutes on
remote_cpu (handoff cites "~10-15 min"). Add 50% safety margin -> 1800s (30 min).

timeout_s = 1800

## Smoke gate

- Synthetic Zipfian text 10K tokens, V_synth=400 (CLEAN data, not substrate state per
  feedback_smoke_clean_synthetic_data_not_substrate_state_USER_2026-06-23).
- Verify B2 word-bigram computes correctly (P_bi rows sum to 1, add-alpha backoff).
- Verify (T, lambda)-sweep selects degenerate (lam=0) when substrate signal is noise.
- Verify per-arm metrics (B1, B2, S_K1, S_K5, S_K10) present in metrics.json.
- Verify verdict classifier fires HP/MID/HF correctly on synthetic numbers (selftest).

## Honest scope reporting (Fix #28)

The cell metrics.json will include `honest_scope` with explicit `what_this_does_NOT_show`:
- V > 4000 not tested
- Learned encoder not tested (frozen char-trigram-meanpool only)
- Sequence > K=10 not tested
- Cross-corpus not tested (text8 only)
- Brain-compose stack not present (no PC top-down, no WM register, no DA-LR)

## Skunkworks tier hint

If HARD_PASS: candidate for chain-grade or measured-mechanism per Skunkworks tier review
(brain-grounded word-grain mechanism + canonical neural language stack alignment). Default
expectation per Fix #28: classify down (MEASURED_MECHANISM not chain-grade) unless
discriminator ratio justifies tier-up.
