# Pre-registration: substrate_brain_word_level_prediction_v2_production_config

**Date:** 2026-06-24
**Anchor:** substrate_brain_word_level_prediction_v2_production_config
**Queue:** overnight_queue (GPU; Fix #24 torch.cuda)
**N_DIM:** 8192 (PRODUCTION), **Seeds:** [7, 17, 23], **K:** [1, 5, 10] (PRIMARY arm = K=5)

## Scientific question

v1 (char-trigram-meanpool encoder + N_DIM=2048) HARD_FAILed at word-grain: S_K5 top1=0.201
vs B2 word-bigram 0.243 (lift 0.83x; under bigram by 0.54 BPW). Critically, ALL substrate
arms (S_K1/S_K5/S_K10) in v1 collapsed to IDENTICAL metrics matching B1 word-unigram,
because the joint sweep selected lambda_star=0.0 (i.e. "substrate logits useless, ignore
them entirely; use unigram alone"). top1_raw was ~0.02 (essentially random).

The v1 substrate had no signal -- the char-trigram-meanpool encoder + N_DIM=2048 produced
embeddings that contained no useful word-context information. This is config-degraded, not
a word-grain failure.

**This rescue tests:** does substrate at PRODUCTION config (word2vec encoder + N_DIM=8192
+ sparse-bipolar f=0.05) beat word-bigram at word grain?

- **HARD_PASS**: word-grain reframe is valid; substrate has a real LM path.
- **HARD_FAIL at production**: word-grain isn't the issue; the LM gap is deeper. Drill what.
- **MIDDLE_BAND**: config matters but bigram still wins; need richer architecture.

Closes skepticism axes A2 (unigram baseline too weak) + A10 (text8 char corpus may be
wrong test) + A14 (config-degraded harness gave a false negative).

## Pre-registered bands (UNCHANGED from v1; rescue tests config not bands)

**HARD-PASS:**
- S_K5 top1 >= 1.30 * B2_word_bigram_top1 AND
- S_K5 BPW <= B2_word_bigram_BPW - 0.4 bits

**MIDDLE:** S_K5 top1 lift in [1.10x, 1.30x] over B2 OR S_K5 BPW margin in [B2-0.4, B2-0.1].

**HARD-FAIL:** S_K5 top1 <= B2_top1 OR S_K5 BPW >= B2_BPW.

## Calibration rationale

Same as v1: word-bigram is THE aliveness threshold for any LM (unigram is the trivial
floor). 1.30x top1 lift over bigram is meaningful given V=4000 word-bigram on text8
typically scores top1 0.18-0.25. 0.4-bit BPW margin matches the substrate-as-LM
fair-harness HP bar (0.3 BPC -> 0.4 BPW since word units are larger).

## Critical config changes vs v1

| Field | v1 | v2 (this rescue) |
| --- | --- | --- |
| Encoder | char-trigram-meanpool | word2vec-google-news-300 -> Gaussian proj -> sparse-bipolar |
| N_DIM | 2048 | **8192** (production) |
| Sparse-bipolar f | not used (dense) | **0.05** (VSA primitive) |
| LAMBDA_GRID | [0.0, 0.3, 0.5, 0.7] | **[0.1, 0.3, 0.5, 0.7]** (excludes 0.0; META C7) |
| Device | CPU (numpy) | **CUDA (torch)** (Fix #24) |
| Substrate floor | top1_raw ~ 0.02 | expected > 0.05 if signal present |

The lambda_star=0.0 collapse in v1 means a future v3 must NEVER admit lambda=0.0 to the
sweep when the question is "does substrate beat baseline" -- lambda=0.0 lets the sweep
trivially recover the baseline by zero-weighting the substrate. v2 LAMBDA_GRID excludes
0.0 (META C7 discipline).

## N-suffix section

Anchor name has NO _n<N> suffix (PROT-018 does not apply: the rescue intent is the cell's
production-config focus, not the N value itself). The cell uses N_DIM=8192 explicitly in
the FULL config block. Selftest verifies LAMBDA_GRID does not contain 0.0.

## Timeout estimate

Smoke target: <180s on laptop CPU (char-trigram fallback; no gensim).
FULL on GPU: N_DIM=8192 (16x v1) + sparse-bipolar topk + torch.cuda matmul + 3 seeds.

Dominant cost is substrate-logits matmul O(n_query * N_DIM * V) per K per seed on GPU:
- ~16x v1 (2048 -> 8192) but on GPU (~50-100x speedup on matmul)
- Net per-seed estimate: ~6-12 min on RTX-class GPU
- 3 seeds: ~25-40 min total

Add safety margin for word2vec load (~2 min) + sparse-bipolar topk (~1 min/seed):
- timeout_s = 5400 (1.5 h)

PROT-021 threshold is 14400s (4h); we are well under so checkpoint is not mandatory but
the cell DOES adopt _seed_checkpoint anyway (good hygiene).

## Smoke gate

- Synthetic Zipfian text 10K tokens, V_synth=400 (CLEAN data, not substrate state per
  feedback_smoke_clean_synthetic_data_not_substrate_state_USER_2026-06-23).
- Smoke uses char-trigram fallback (no gensim) so smoke runs on laptop CPU without
  word2vec installed.
- Sparse-bipolar primitive selftest: verify exactly k=round(f*dim) non-zero entries per row,
  all +/-1.
- LAMBDA_GRID-excludes-zero selftest (META C7): fail if 0.0 is in LAMBDA_GRID.
- Verify B2 word-bigram normalization + verdict classifier HP/MID/HF fire correctly.
- Per-arm metrics (B1, B2, S_K1, S_K5, S_K10) present in metrics.json.

Smoke is intentionally NOT a discriminator (synthetic Zipfian, char-trigram encoder, tiny
config). Smoke proves the harness runs end-to-end; production GPU run is the discriminator.

## GPU utilization gate (Fix #24)

The cell records `gpu_mem_used_gb_peak` per seed. On the FULL GPU run, expected peak
should be in the 4-12 GB range (sparse-bipolar f=0.05 of N_DIM=8192 V=4000 + HRR keys).
If gpu_mem_used_gb_peak < 0.5 GB for full run -> Fix #24 violation flag (cell is on CPU
despite GPU queue).

## Honest scope reporting (Fix #28)

The cell metrics.json includes `honest_scope` with `what_this_does_NOT_show`:
- V > 4000 not tested
- Encoder learning not tested (word2vec frozen + Gaussian projection; no backprop)
- Sequence > K=10 not tested
- Cross-corpus not tested (text8 only)
- Brain-compose stack not present
- `v1_comparison` explicitly lists v1 config + v2 changes

Per-arm metrics in per_seed[*].{arm_name}.{bpw,top1,top1_raw,T_star,lambda_star};
DO NOT read verdict_msg for cross-arm framing (Fix #28).

## Skunkworks tier hint

If HARD_PASS at production: candidate for chain-grade or measured-mechanism per Skunkworks
tier review (word-grain LM with production encoder). Default expectation per Fix #28:
classify down (MEASURED_MECHANISM not chain-grade) unless discriminator ratio (e.g. lift
ratio across K=1,5,10) justifies tier-up.

If HARD_FAIL at production: definitive negative on "config-confound rescues word-grain
substrate"; routes to Research for the next drill (e.g. backprop encoder, attractor
cleanup, deeper HRR composition).
