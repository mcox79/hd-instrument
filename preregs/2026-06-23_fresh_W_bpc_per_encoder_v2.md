# Pre-reg: fresh_W_bpc_per_encoder_v2 (re-dispatch of methodology-corrected Path A BPC)

**Date:** 2026-06-23
**Anchor:** fresh_W_bpc_per_encoder_v2
**Cell:** experiments/exp_fresh_W_bpc_per_encoder_v2.py
**Queue:** overnight_queue (remote GPU; torch.cuda + batched matmul; N_DIM=8192; ~8M outer-products per arm; Fix #24)
**Run-mode:** full (smoke for gate)
**Author:** Exp-Dev (cell author + dispatch)
**Pre-reg source-of-truth:** USER directive 2026-06-23 (re-dispatch authorization after gensim install on remote .venv)

## Why v2 (re-dispatch of v1 under fresh ship_name)

v1 was dispatched to overnight_queue. On remote run, ARM_CHAR_TRIGRAM_FRESH_W
executed cleanly to BPC 7.74 (which equals the unigram floor 7.738 -- substrate
signal is no stronger than unigram for the lexical baseline arm). BUT the three
pretrained encoder arms (ARM_WORD2VEC_FRESH_W / ARM_GLOVE_FRESH_W /
ARM_FASTTEXT_FRESH_W) all hit ENCODER LOAD FAIL because remote
`C:/dev/hd-instrument/.venv` did not have gensim installed. The HARD_PASS bar
requires a pretrained encoder arm to clear BPC<7.738 AND lift>=0.5 bits over
CHAR_TRIGRAM_FRESH_W -- impossible to evaluate when the encoder cells never
ran. v1 therefore left the decisive V2 LM gap closure question undetermined.

USER 2026-06-23 authorized installing gensim-4.4.0 + smart_open-7.6.1 into the
remote .venv. Gensim cache at `marsh@home:C:/dev/hd-instrument/data/gensim_cache/`:
- fasttext-wiki-news-subwords-300 fully present
- glove-wiki-gigaword-300 fully present
- word2vec-google-news-300 re-SCP'd in parallel (or gensim will re-download
  from cached mirror if not complete before this cell runs)

v2 is **the same cell as v1** (no code changes vs v1; same 5-arm config /
N_DIM=8192 / V=4000 / N_TRAIN=100k / N_HELD=20k / seeds=[7,17,23] /
LAMBDA_GRID=[0.0,0.1,0.3,0.5,0.7,1.0] / fresh W per arm) re-dispatched under
a fresh ship_name so the queue accepts it and all 4 encoder arms actually
execute. Restores the decisive test.

## Question (unchanged from v1)

Does pretrained-encoder + substrate beat unigram BPC at production scale **when the
substrate W matrix is built FRESH from that encoder's vectors** (no char-trigram
contamination from prior ingest)?

- **HARD_PASS:** semantic encoder + fresh W IS the lever; V2 LM gap closure
  decisive evidence; chain-grade-eligible. Substrate's rank-1 Hebbian readout CAN
  work given the right encoder.
- **HARD_FAIL:** substrate W matrix itself is the bottleneck regardless of
  encoder; mathematical cap from rank-1 Hebbian; pivot V2 to descope or
  architectural rewrite. v1's CHAR_TRIGRAM_FRESH_W=7.74 result is a partial
  data-point in favor of HARD_FAIL pending the pretrained encoder arms.

## Arms (unchanged from v1; all 4 encoder arms expected to run on v2)

1. **ARM_UNIGRAM** -- analytic baseline floor (BPC=7.738 ref on text8 100k).
2. **ARM_CHAR_TRIGRAM_FRESH_W** -- substrate-native bipolar trigram bundling.
3. **ARM_WORD2VEC_FRESH_W** -- Mikolov 2013 word2vec-google-news-300 + JL projection 300->8192.
4. **ARM_GLOVE_FRESH_W** -- Pennington 2014 glove-wiki-gigaword-300 + JL projection.
5. **ARM_FASTTEXT_FRESH_W** -- Bojanowski 2017 fasttext-wiki-news-subwords-300 + JL projection.

## Pre-reg HARD bands (unchanged from v1; V2 LM gap closure; chain-grade-eligible)

### HARD_PASS
ANY of {WORD2VEC, GLOVE, FASTTEXT}_FRESH_W simultaneously achieves:
- `bpc_best` (log-linear interp best lambda) < **7.738** (beats unigram), AND
- lift over ARM_CHAR_TRIGRAM_FRESH_W >= **0.5 bits**, AND
- bpc cv across 3 seeds <= **0.05**.

### HARD_FAIL
ALL 4 encoder arms (incl. CHAR_TRIGRAM_FRESH_W) >= **7.738**. Substrate
rank-1 Hebbian readout mathematically capped regardless of encoder.

### MIDDLE_BAND
Some lift over CHAR_TRIGRAM_FRESH_W but not both bars cleared.

## Sanity gates (HANDOFF self-test; same as v1)

T1-T10 identical to v1 -- bipolar trigram + JL projection scale +
build_E_char_trigram shape + Hebbian W shape + cycle recall acc>=0.7 +
log-linear endpoints (lambda=1 raw, lambda=0 unigram) + unigram analytic +
mock-KV gensim pipeline + verdict bands HP/HF/MID + LLM-counter=0.

## GPU dispatch (Fix #24 compliance; unchanged from v1)

- torch.cuda backend; W = 8192x8192 fp32 = ~256MB per arm
- INGEST_CHUNK=4096, RECALL_BATCH=512, batched outer-products / recall
- Per-arm `mem_get_info()` heartbeat + wall-time logging
- Smoke at N_TRAIN=2000 N_DIM=8192 exercises GPU path under SMOKE_TIMEOUT_S=180

## Compute budget (unchanged; remote GPU FULL)

- 5 arms x 3 seeds; ingest ~30s + recall ~20s per arm-seed = ~80s
- Per seed: ~5 arms x ~80s = ~400s; 3 seeds = ~1200s = ~20min
- Gensim model loads first time: ~30s each x 3 = ~90s (or cache hit ~5s each)
- **Timeout: 5400s** (90 min; ~4.5x headroom over ~1200s estimate; absorbs
  any first-time gensim model load if cache cold or word2vec re-download)

## Pre-flight discipline (this v2 ship)

- **Fix #26 (pre-dispatch verify-the-referent):** ran
  `python tools/predispatch_check.py fresh_W_bpc_per_encoder` -> 0 matching
  landings, 0 atoms; PROCEED.
- **Fix #20 (no pipe-tail subprocess monitoring):** monitor via mtime polling
  on `data/exp_fresh_W_bpc_per_encoder_v2/metrics.json`.
- **Fix #28 (per-arm metrics):** post-landing run
  `python tools/peek_arm_metrics.py exp_fresh_W_bpc_per_encoder_v2` to read
  per-arm BPC before propagating cross-arm narratives.
- **Long-cells discipline:** per-seed checkpoint via `_seed_checkpoint`.
- **ASCII-only:** all print() + verdict_msg.
- **Commit prereg + cell before remote dispatch:** USER discipline 2026-06-17.

## Status_log

- event_kind="experiment_ship" importance=HIGH
- Note: re-dispatch of methodology-corrected V2 LM gap decisive test under v2
  ship_name; v1 was blocked by missing gensim on remote .venv (now installed).
  Same cell as v1 (no code changes); restores all 4 encoder arms.

## Cites

- preregs/2026-06-23_fresh_W_bpc_per_encoder_v2.md (this file)
- preregs/2026-06-23_fresh_W_bpc_per_encoder_v1.md (parent prereg; same bands)
- experiments/exp_fresh_W_bpc_per_encoder_v1.py (parent cell)
- experiments/exp_fresh_W_bpc_per_encoder_v2.py (this cell; copy of v1 + renamed anchor/config)
- USER directive 2026-06-23 (gensim install authorization + re-dispatch)
- USER directive 2026-06-23 (methodology fix: fresh W per encoder)
- USER directive 2026-06-22 (Fix #24 GPU dispatch must use GPU)
- Mikolov 2013 (word2vec) / Pennington 2014 (GloVe) / Bojanowski 2017 (fastText)

-- Exp-Dev
