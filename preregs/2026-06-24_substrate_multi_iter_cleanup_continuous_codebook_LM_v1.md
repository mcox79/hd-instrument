# Prereg: substrate_multi_iter_cleanup_continuous_codebook_LM_v1

Filed: 2026-06-24 (pre-run; A2 substrate-mining drill; reverses-or-confirms v1 wrong-closure).

## Hypothesis

v1 (substrate_multi_iteration_cleanup_LM_v1, HARD_FAIL 2026-06-23) reported
bpc_1iter == bpc_3iter == bpc_10iter == 7.3753 to 4 decimals. The sign-step Hopfield
update `sign(W @ q)` is IDEMPOTENT on sign-binarized char-trigram states: it reaches
a fixed point in one iteration, so iterations 1, 3, 10 produce identical logits and
identical BPC. v1 was a PRIMITIVE x ENCODER confound, not a clean test.

Meanwhile modern_hopfield_n_sweep_v1 is chain-grade at N=4096 M/N=0.30 with 100%
accuracy (CERT row 100): a CONTINUOUS-codebook softmax-based update transfers
iterations meaningfully.

Does multi-iter cleanup transfer to the LM regime when the encoder is CONTINUOUS
(word2vec dense L2-normalized, projected to N_DIM=8192) AND the cleanup primitive
is MODERN-HOPFIELD softmax (NOT sign)?

P_deflated = 0.40 (uncertain; modern-Hopfield is brain-grounded + chain-grade at
primitive level, but LM regime may have different ceiling than associative-recall;
also Skunkworks-cautious by-construction-saturation possibility).

## Arms

All 4 arms run on the same text8 split with the same seeds.

- **ARM_BASELINE_NO_CLEANUP_SIGN_BINARIZED**: char-trigram sign-binarized encoder
  + sign(W @ q) at n_iter=0 (no cleanup). Sanity-rail: should reproduce v1's
  ARM_BASELINE_NO_CLEANUP bpc ~ 7.226 +- 0.05.
- **ARM_SINGLE_STEP_CONTINUOUS_CODEBOOK**: word2vec-300d -> N_DIM=8192 Gaussian-
  projected L2-normalized codebook + modern-Hopfield softmax 1-step cleanup. New
  baseline for the continuous regime.
- **ARM_MULTI_ITER_3_CONTINUOUS_CODEBOOK**: same encoder + codebook; 3 iterations
  of modern-Hopfield softmax cleanup.
- **ARM_MULTI_ITER_10_CONTINUOUS_CODEBOOK**: same encoder + codebook; 10 iterations
  of modern-Hopfield softmax cleanup.

Cleanup primitive (continuous):
```
  s_{k+1} = softmax(beta * (s_k @ codebook.T)) @ codebook
  s_{k+1} = l2_normalize(s_{k+1})
```
beta = 8.0 (matches modern_hopfield_n_sweep_v1).

## Pre-registered bands (DO NOT ADJUST after seeing data)

Primary comparison = lift_3_vs_1 = bpc_c1 - bpc_c3 (POSITIVE means multi-iter HELPS).

- **HARD_PASS**: lift_3_vs_1 >= 0.05 bits AND cv_c3 <= 0.05. The v1 wrong-closure is
  REVERSED -- multi-iter cleanup DOES transfer to LM regime when encoder + primitive
  are continuous.
- **MIDDLE_BAND**: lift_3_vs_1 in [0.02, 0.05). Partial reversal; multi-iter helps
  marginally but not at HARD_PASS threshold.
- **HARD_FAIL**: lift_3_vs_1 < 0.02 (or negative). v1 wrong-closure CONFIRMED at
  primitive level: multi-iter cleanup does NOT transfer to LM regardless of encoder
  or cleanup primitive. The Tier-3 multi-iter hypothesis remains rejected for LM.
- **SANITY_RAIL_FLAG**: ARM_BASELINE_NO_CLEANUP_SIGN_BINARIZED bpc must be within
  +-0.05 of v1 reference 7.226. Outside tolerance -> PROVENANCE_FLAG annotation
  (does NOT alter verdict band; reported for cert-chain audit).

## Config

- N_DIM = 8192 (PRODUCTION; PROT-018: no _nN suffix; N stated here + in script)
- N_TRAIN = 100,000 text8 tokens; N_HELD = 20,000; VOCAB_CAP = 4000
- SEEDS = [7, 17, 23] (3 seeds, full run)
- W2V_MODEL = "word2vec-google-news-300" (cached at data/gensim_cache/)
- MH_BETA = 8.0; SPARSITY_F = 0.05; AMPLITUDE_SCALE = 1/sqrt(0.05) ~ 4.47

## Timeout estimate

Smoke (N_DIM=512, N_TRAIN=2000, 1 seed, 4 arms): includes word2vec cache load
(~2-5s if cached locally), trigram encoder, Hebbian W build (smallest), 4 logit
sweeps. Estimated 60-120s.

Full extrapolation:
  - encoder cost: V * trigram-loop + V * w2v-lookup -> linear in V; dominated by
    Gaussian projection (300d * 8192d = 2.5M ops per word; V=4000 -> 10G ops; ~5s)
  - W build: O(N_TRAIN * N_DIM^2 / INGEST_CHUNK) chunked; at N_DIM=8192 this is
    the dominant CPU cost. v1 measured ~150s at N_DIM=8192 per seed for one W.
    Two W builds (sign + continuous) per seed -> ~300s/seed for W.
  - Recall: 4 arms x N_HELD=20000 / RECALL_BATCH=512 = 40 batches per arm.
    Per batch: W @ src (8192x8192 @ 512x8192) + cleanup-iters x codebook matmul
    (512x8192 @ V=4000x8192 -> 16M ops; ~1s). 10-iter arm = 10x. Per arm ~10-30s.
    Per seed = ~100-150s recall.
  - Per seed total: ~400-500s = ~7-9 min.
  - 3 seeds: ~25-30 min.

Add 1.5x safety margin + overhead: **timeout = 3600s (1h)**.

Per PROT-019: anchor has no _nN suffix; tier floors do not apply.
Per PROT-021: 3600s < 14400s; checkpoint-import not strictly required, but cell
imports _seed_checkpoint anyway (per-seed resumability).

## Queue routing

remote_cpu_queue (pure numpy + gensim; no torch; matmul-dominated but bounded;
total wall < 1h). Per Fix #22, N_DIM=8192 is fixed (not swept), arms are
sequential, cell tests STRUCTURAL primitive choice not capacity, so GPU
parallelism gains are minimal. CPU route accepted.

## What this does NOT show

1. Whether multi-iter helps with OTHER continuous encoders (GloVe / fastText).
2. Whether beta=8.0 is optimal for LM regime (lifted from primitive-cell).
3. Whether the result generalizes beyond word-bigram BPC at V=4000 / N_DIM=8192.
4. Whether ARM_BASELINE_NO_CLEANUP_SIGN_BINARIZED reproducing v1 ref proves
   reproduction-fidelity (it's same setup, but cell-author + commit-hash may
   have subtle differences); the sanity-rail is a check, not a chain-grade claim.

## Sanity-rail provenance

v1 reference (data/exp_substrate_multi_iteration_cleanup_LM_v1/metrics.json):
- ARM_BASELINE_NO_CLEANUP bpc_mean = 7.2268 (3 seeds, N_DIM=8192, N_TRAIN=100k,
  VOCAB_CAP=4000, sign-binarized char-trigram, AMPLITUDE_SCALE=4.47).
- ARM_SINGLE_STEP / 3_ITER / 10_ITER all = 7.3753 (identical -- the wart).
- ARM_UNIGRAM = 7.6838.

If new ARM_BASELINE_NO_CLEANUP_SIGN_BINARIZED comes in at 7.22 +- 0.05 -> sanity-rail
PASS (v1 reproduces; cell-author drift is bounded).
If outside tolerance -> PROVENANCE_FLAG raised but verdict still issued on the
continuous-codebook primary comparison.
