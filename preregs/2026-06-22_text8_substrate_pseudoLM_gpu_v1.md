# Pre-registration: text8_substrate_pseudoLM_gpu_v1

**Date:** 2026-06-22
**Anchor:** text8_substrate_pseudoLM_gpu_v1
**Queue:** overnight_queue (GPU)
**N_DIM:** 16384, **N_TRAIN:** 5,000,000, **N_HELD:** 100,000, **VOCAB_CAP:** 20000, **Seeds:** [7, 17, 23]

## Scientific question

Can the substrate, at LLM-class N_DIM (16384) and on a real natural-language corpus (text8, 5M
training tokens), act as a pseudo-LM via pure Hebbian-bind word-NEXT_TOKEN binding and match or
beat the word-bigram bar (~3.84 BPC on text8 per L2 MVP frontier)? Composes the
substrate_as_llm_scaling capacity finding (1M facts at N=16384 perfect recall via Hebbian) with
B2 TinyStories pseudo-LM mechanism (Hebbian-bind word-NEXT_TOKEN pairs).

## Mechanism (4 arms; Fix #16 discriminator)

1. **SUBSTRATE_LM_HEBBIAN** -- char-trigram word encoder E [V, dim] unit-normed; single
   NEXT_TOKEN relation Hebbian-bind: W = sum_t outer(E[idx[t+1]], E[idx[t]]) on GPU via batched
   matmul. Per-eval: pred_vec = E[ctx] @ W.T ; pred_vec /= ||pred_vec|| ; logits = pred_vec @ E.T
   ; probs = softmax(logits / 0.1) ; argmax + log p(true).
2. **UNIGRAM_BASELINE** -- argmax unigram (CAN-FAIL floor).
3. **WORD_BIGRAM_BASELINE** -- sparse Laplace-smoothed bigram (HARD bar). dict-of-dicts for
   V=20k tractability (dense V*V at V=20k float64 = 3.2GB; sparse stores ~few-million observed pairs).
4. **SUBSTRATE_HEBBIAN_BIGRAM_BACKOFF** -- substrate prediction when sub_p_argmax >= 0.05
   (substrate-confident); else fall back to bigram. Composition arm: predicts MAYBE substrate
   adds value above bigram even if not alone.

## Pre-registered bands

**HARD-PASS** (any of the following AND cv <= 0.10 AND n_llm_calls == 0):
- ppl(SUBSTRATE) <= ppl(BIGRAM) AND acc(SUBSTRATE) >= acc(BIGRAM) -- substrate matches bigram
  via pure Hebbian-bind (L2 MVP frontier achievement);
- ppl(BACKOFF) < min(ppl(SUBSTRATE), ppl(BIGRAM)) -- HYBRID composition lift demonstrated.

**MIDDLE-BAND:** substrate beats unigram floor but doesn't match bigram and no composition lift
(existing L2 state; still informative as substrate-Hebbian-LM cap measurement at this scale).

**HARD-FAIL:**
- ppl(SUBSTRATE) >= ppl(UNIGRAM) -- substrate fails to even improve over unigram floor;
- OR n_llm_calls > 0 -- substrate-only-decode gate violated.

## Calibration rationale

- text8 unigram BPC ~6.33 (per N1 v3.1 reference; uniform-ish over top-V words).
- text8 word-bigram BPC ~3.84 (L2 MVP frontier; smoothed bigram with same vocab cap).
- Prior B2 TinyStories cell at smoke scale (V_DIM=1024, 12k tokens, V=2000) HARD_FAILED
  (substrate ppl > unigram ppl). This cell tests whether scaling N_DIM 16x (1024 -> 16384) +
  corpus 400x (12k -> 5M tokens) lets the substrate hit the L2 frontier.
- cv <= 0.10 reflects 3-seed variance tolerance for natural-corpus cells (looser than
  cv <= 0.05 used for synthetic-capacity cells like substrate_as_llm_scaling).
- BACKOFF_THRESH = 0.05 chosen so substrate dominates on confident high-prob tokens (head of
  predictive distribution) and bigram absorbs the long-tail / unseen-context cases. If substrate
  has wide flat probs (low confidence everywhere), the cell defers to bigram.

## N-suffix section

Anchor has NO _n<N> suffix because this is a substrate-as-LM cell with multiple N-bearing
parameters (N_DIM=16384 + N_TRAIN=5M). PROT-018 does not apply. (Compare anchor pattern to
substrate_as_llm_scaling_million_facts_v1 which also omits _n suffix.)

## Timeout estimate

Smoke (N_DIM=4096, N_TRAIN=100k, VOCAB_CAP=4000, 1 seed) wall estimate:
- Encoder build:  ~1-3s (build_encoder_gpu over 4000 words at dim=4096)
- Hebbian ingest: ~3-10s (chunked outer-products over ~100k token pairs at chunk=8192)
- Substrate recall: ~1-3s (batched matmul over ~5000 eval positions)
- Bigram + unigram + backoff: ~5s (sparse-dict Python loop over 5000 positions)
- Total smoke wall: ~10-30s

FULL (N_DIM=16384, N_TRAIN=5M, VOCAB_CAP=20k, 3 seeds) extrapolation:
- Encoder build per seed: 20k * 4x trigrams ~ ~5s
- Hebbian ingest per seed: 5M / 32k = 156 chunks * (32k chunk -> outer-product at 16384 dim).
  Each chunk = 2 mm-batched matmuls + accumulate = roughly 32k * 16384^2 * 2 FLOPs = ~17 TFLOPs
  per chunk -> ~5-15s per chunk on a consumer GPU; total ~13-40 min per seed.
- Substrate recall per seed: 100k eval / 2048 batch = ~50 batches * (2048 * 16384^2 + 2048 * 20k * 16384) FLOPs.
  Roughly ~3-10 min per seed.
- Bigram per seed (sparse-dict Python loop over 100k eval positions): ~30-60s.
- Total per seed: ~20-60 min (high variance based on GPU specifics).
- 3 seeds: ~60-180 min wall.

formula: ceil(1.5 * 30 * (16384/4096)^1.5 * (5_000_000/100_000)^1.0 * (3/1)) heavily overestimates
because the per-chunk wall is dominated by GPU throughput (matmul TFLOPS) not by N_DIM^1.5
scaling -- batched outer-product scales linearly in chunk_size and quadratically in N_DIM.
Practical extrapolation: 30s * (16x N_DIM^2 / 4x) * (50x N_TRAIN) * 3 seeds = 30s * 4 * 50 * 3
= 18000s -- but this assumes GPU saturates; in practice ~half that.

**timeout_s = 7200 (2h)**

If full wall exceeds 7200s, the atexit / SIGTERM handlers will synthesize metrics.json from
per-seed partials so completed seeds aren't wasted. PROT-021 not triggered (timeout < 14400s).

## GPU mandate (Fix #24)

- N_DIM=16384 + 5M token-pair ingest = matmul-heavy at GPU-class scale.
- All substrate compute on torch.cuda (encoder load, W ingest, recall matmul).
- Smoke must verify nvidia-smi GPU util >= 50% steady-state during ingest phase.
  (The prior substrate_as_llm_scaling cell ran at 0% util -- Fix #24 violation. This cell
  uses larger INGEST_CHUNK + RECALL_BATCH to keep the GPU fed; periodic torch.cuda.synchronize
  to surface the actual work.)

## Compose with

- substrate_as_llm_scaling_million_facts_v1 (storage chain at LLM-class N): if HARD_PASS,
  storage-at-scale + LM-decoder-at-scale together = first chain-grade evidence at REAL LANGUAGE
  CORPUS scale of substrate-as-LLM-substitute mechanism.
- B2 TinyStories pseudo-LM (mechanism): same Hebbian-bind formula, scaled UP to GPU class +
  real corpus.

## Substrate-only-decode gate

n_llm_calls == 0 enforced at exit (_LLM_CALL_COUNTER asserted). Encoder is char-trigram (HD vector
hash). No LLM forward calls at inference; substrate-only at every stage.

## Honest scope

What this DOES test: the substrate's ability to act as a pseudo-LM via single-NEXT_TOKEN
Hebbian-bind, on natural-language text at GPU-class N_DIM, against unigram + bigram baselines.
What this does NOT test: longer-context (k>1) bindings (a HARD_PASS at k=1 establishes the
floor; future cells can sweep k); transformer-class LM benchmarks (this is a Path A pseudo-LM,
not a competitor to TinyStories transformers).
