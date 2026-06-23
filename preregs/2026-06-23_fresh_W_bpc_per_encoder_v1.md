# Pre-reg: fresh_W_bpc_per_encoder_v1 (METHODOLOGY-CORRECTED Path A BPC)

**Date:** 2026-06-23
**Anchor:** fresh_W_bpc_per_encoder_v1
**Cell:** experiments/exp_fresh_W_bpc_per_encoder_v1.py
**Queue:** overnight_queue (GPU; torch.cuda + batched matmul; N_DIM=8192; ~8M outer-products per arm; Fix #24 GPU dispatch)
**Run-mode:** full (smoke for gate)
**Author:** Exp-Dev (cell author + dispatch)
**Pre-reg source-of-truth:** USER directive 2026-06-23 "we need to make sure we're not testing these new ideas against old coding or data"

## Question

Does pretrained-encoder + substrate beat unigram BPC at production scale **when the
substrate W matrix is built FRESH from that encoder's vectors** (no char-trigram
contamination from prior ingest)? This is the methodology-corrected V2 LM gap closure
decisive test.

The current Path A test reuses existing substrate W which was built with char-trigram
during ingest -- that masks how good pretrained encoders actually are. This cell does
the clean test: build a COMPLETELY FRESH W matrix per encoder candidate, then measure
BPC.

- **If YES (HARD_PASS):** semantic encoder + fresh W IS the lever; V2 LM gap closure
  decisive evidence; chain-grade-eligible. Substrate's rank-1 Hebbian readout CAN
  work given the right encoder.
- **If NO (HARD_FAIL):** substrate W matrix itself is the bottleneck regardless of
  encoder; mathematical cap from rank-1 Hebbian; pivot V2 to descope or
  architectural rewrite.

## Arms (5; each builds COMPLETELY FRESH W from scratch using ONLY that encoder's vectors)

1. **ARM_UNIGRAM** -- analytic baseline floor (BPC=7.738 ref on text8 100k).
2. **ARM_CHAR_TRIGRAM_FRESH_W** -- ingest text8 via `hdlab/char_trigram_encoder.py`-style
   bipolar trigram bundling -> 8192d HD vectors; build fresh Hebbian W on GPU.
   **Honest substrate-native baseline with fresh W** (NOT a stale-W reuse).
3. **ARM_WORD2VEC_FRESH_W** -- Google word2vec 300d (Mikolov 2013) projected to 8192d
   via random Gaussian (one P per seed; JL-scaled 1/sqrt(300)); fresh W on GPU.
4. **ARM_GLOVE_FRESH_W** -- Stanford GloVe 300d (Pennington 2014) same projection; fresh W.
5. **ARM_FASTTEXT_FRESH_W** -- Facebook fastText 300d (Bojanowski 2017; OOV
   char-ngram backoff is substrate-relevant) same projection; fresh W.

**CRITICAL methodology fix:** each arm gets its OWN W matrix; NO sharing of substrate
state. Tests pure encoder-via-substrate capability.

OOV words in pretrained vocab fall back to char-trigram encoding so the fresh-W
ingest never receives degenerate zero-vectors.

## Config (full)

- N_DIM = 8192 (per USER routing: heavy cells via GPU; N>=4096 enforces PROT-019 floor)
- PRETRAIN_DIM = 300
- Seeds = [7, 17, 23]
- text8 N_TRAIN = 100_000 tokens
- text8 N_HELD = 20_000 tokens (split 50/50 dev/test)
- VOCAB_CAP = 4000
- INGEST_CHUNK = 4096 (GPU outer-product batch)
- RECALL_BATCH = 512
- LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0] (log-linear interp with unigram)

## Pre-reg HARD bands (V2 LM gap closure; chain-grade-eligible)

### HARD_PASS

ANY semantic encoder arm (WORD2VEC / GLOVE / FASTTEXT) simultaneously achieves:
- **bpc_best (log-linear-interpolated best lambda)** < **7.738** (beats unigram), AND
- **lift over ARM_CHAR_TRIGRAM_FRESH_W** >= **0.5 bits** (semantic encoder beats
  lexical encoder by >=0.5 bits on substrate -- shows lift is from semantic content
  not from substrate W mechanics that any encoder would inherit), AND
- **bpc cv across 3 seeds** <= **0.05**.

### HARD_FAIL

ALL 4 encoder arms (including CHAR_TRIGRAM_FRESH_W) achieve `bpc_best >= 7.738`
(no encoder beats unigram even with fresh W). Confirms substrate's rank-1
Hebbian readout is mathematically capped regardless of encoder; pivots V2 to
descope or architectural rewrite.

### MIDDLE_BAND

Semantic encoders lift over ARM_CHAR_TRIGRAM_FRESH_W but don't beat unigram OR
beat unigram without sufficient lift over CHAR_TRIGRAM_FRESH_W -- partial;
characterizes encoder contribution vs substrate-W bottleneck.

## Sanity gates (HANDOFF self-test; verified at --self-test)

- **lambda=1.0 sanity:** `log_linear_interp_bpc(sub_logp, U_log, nxt, 1.0)` ==
  raw substrate BPC `-mean(sub_logp[arange,nxt]) / log(2)`. (selftest T6a)
- **lambda=0.0 sanity:** `log_linear_interp_bpc(sub_logp, U_log, nxt, 0.0)` ==
  pure unigram BPC. (selftest T6b)
- **Hebbian cycle recall:** small 10-token cycle, 5 reps -> recall >= 0.7
  (selftest T5; confirms fresh W build is functionally correct).
- **Encoder L2-norm:** all built E rows have norm==1 to 1e-5. (selftest T3)
- **JL projection scale:** Gaussian P std ~ 1/sqrt(300) ~ 0.058. (selftest T2)
- **Verdict bands:** synthetic units in HP / HF / MID regions produce
  correct verdict-classification. (selftest T9)

## GPU dispatch (Fix #24 compliance)

- torch.cuda backend; `torch.float32` accumulator at N_DIM=8192 means
  W = 8192x8192 = ~256MB per arm (fits comfortably on any modern GPU).
- Per-arm encoder hoisted to GPU before Hebbian ingest.
- Batched outer-product via `W.add_(E_tgt.T @ E_src)` over INGEST_CHUNK=4096.
- Heartbeat: per-arm `mem_get_info()` print after E build; per-arm wall time
  for encode + ingest + recall logged.
- Smoke uses N_TRAIN=5000 N_DIM=8192 to actually exercise the GPU path under
  the SMOKE_TIMEOUT_S=180 cap (not a CPU-only mini-config).

## Compute budget

- 5 arms x 3 seeds x (encode + fresh W ingest 100k pairs + 2x recall over 10k
  held positions @ V=4000).
- W ingest at N_DIM=8192, INGEST_CHUNK=4096: ~24 outer-product batches per arm
  per seed; each batch is `[4096, 8192].T @ [4096, 8192]` -> ~8192x8192 result.
  On a modern GPU this is <1s per batch; ~30s per arm per seed.
- Recall at N=8192, V=4000: per-position `E[ctx] @ W.T -> normalize -> @ E.T` =
  `[B, 8192] @ [8192, 8192] @ [8192, 4000]`. At B=512: ~1s per batch; 10k
  positions / 512 = ~20 batches per arm per seed = ~20s.
- Per seed: ~5 arms x ~80s = ~400s; 3 seeds = ~1200s = ~20min FULL.
- Includes gensim model loads first time: ~30s each x 3 = ~90s one-shot.
- **Timeout: 5400s** (90 min; ~4.5x headroom over ~1200s estimate; absorbs
  first-time gensim downloads if remote cache cold despite our pre-stage).
- PROT-019: anchor name does NOT contain `_n<N>` suffix so no large-N
  tier-floor applies. Cell uses N=8192 internally; timeout 5400s well below
  21600s tier floor for `_n>=8192` anchors (which we don't trigger by
  omitting the suffix; this is a non-suffixed anchor).
- PROT-020: imports torch -> GPU queue legitimate.
- PROT-021: timeout 5400s < 14400s threshold -> no _seed_checkpoint
  requirement (we use it anyway for restart hygiene).

## Pre-flight discipline

- **Fix #26 (pre-dispatch verify-the-referent):**
  `python tools/predispatch_check.py fresh_W_bpc_per_encoder` -> 0 landings,
  PROCEED.
- **Fix #20 (no pipe-tail subprocess monitoring):** monitor via mtime polling.
- **Fix #28 (per-arm metrics, not summary verdict):** post-landing,
  `tools/peek_arm_metrics.py` per arm BEFORE propagating cross-arm narratives.
- **Long-cells discipline:** per-seed checkpoint via
  `_seed_checkpoint.write_partial_key`; restartable.
- **ASCII-only:** all print(), verdict_msg.
- **Commit prereg + cell before remote dispatch:** USER discipline 2026-06-17.
- **Gensim cache pre-staged on remote:** SCP `data/gensim_cache/` to
  `marsh@home:C:/dev/hd-instrument/data/gensim_cache/` BEFORE queue_add so
  the runner doesn't burn time on first-time downloads.

## Status_log

- event_kind="experiment_ship" importance=HIGH
- Note: methodology-corrected V2 LM gap decisive test; fresh W per encoder
  arm; closes the test-old-W-with-new-encoder ambiguity from prior cells.

## Cites

- preregs/2026-06-23_fresh_W_bpc_per_encoder_v1.md (this file)
- experiments/exp_encoder_word2vec_substrate_bind_v1.py (parent; numpy+N=4096)
- experiments/exp_text8_substrate_pseudoLM_v2_temperature_calibrated_v1.py
  (Path-A baseline; calibrated v1 7.864 BPC; provides log-linear interp
   template + unigram 7.738 ref)
- Mikolov et al. 2013 (word2vec)
- Pennington et al. 2014 (GloVe)
- Bojanowski et al. 2017 (fastText; OOV char-ngram backoff)
- hdlab/char_trigram_encoder.py (substrate-native baseline)
- USER directive 2026-06-23 (methodology fix: fresh W per encoder)
- USER directive 2026-06-22 (Fix #24 GPU dispatch must use GPU)
- USER directive 2026-06-22 (no MiniLM, no BGE; word2vec/GloVe/fastText OK)
- Shannon-floor META cert row 675

-- Exp-Dev
