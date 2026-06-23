# Prereg: clean_encoder_eval_harness_v1

**Date:** 2026-06-23
**Anchor:** `clean_encoder_eval_harness_v1`
**Author:** exp_dev
**Cell:** `experiments/exp_clean_encoder_eval_harness_v1.py`

## Why

USER 2026-06-23 caught that ALL encoder tests this session were contaminated
by char-trigram-shaped substrate state (W matrix carrying trigram bias across
arms; vocabulary/atom-IDs co-engineered with char_trigram orthography). Every
"encoder lever falsified" verdict was suspect because the test corpus and the
substrate state both shared trigram surface form.

This cell establishes a CLEAN harness for all future encoder tests. It does
NOT use substrate W, atoms, or any internal state. It evaluates ONLY the raw
encoder against EXTERNAL canonical word-similarity benchmarks (WordSim353 +
SimLex-999). Eliminates the contamination at the source by removing
substrate state from the loop entirely.

The chain-of-reasoning: an encoder that does NOT correlate with human
similarity judgement on canonical pairs (cat-dog, computer-keyboard) cannot
be the source of substrate semantic structure further downstream. This is
the necessary (not sufficient) precondition for any encoder-lever claim.

## Design

4 arms x 2 external benchmarks x 3 seeds (for projection variance).

Arms:
- `ARM_CHAR_TRIGRAM_HONEST` — current substrate's bag-of-char-trigrams at
  `N_DIM=4096`. NO name-leak: benchmark words are real English (cat, dog,
  book), not engineered atom IDs. The honest baseline.
- `ARM_WORD2VEC_300D` — Google `word2vec-google-news-300`. Projected 300d
  → 4096d via fixed per-seed Gaussian.
- `ARM_GLOVE_300D` — Stanford `glove-wiki-gigaword-300`. Same projection.
- `ARM_FASTTEXT_300D` — Facebook `fasttext-wiki-news-subwords-300`. Same
  projection. Handles OOV via char-ngram backoff (built into model).

Benchmarks (cached at `data/encoder_eval_benchmarks/`):
- WordSim353 (`combined.csv`, Finkelstein 2001): 353 pairs, 0-10 human
  similarity (mixes similarity + relatedness; canonical word-embedding eval).
- SimLex-999 (`SimLex-999.txt`, Hill 2015): 999 pairs, distinguishes pure
  similarity (cat-dog 9/10) from relatedness (cat-mouse 8/10 not similar).
  Substrate-product relevant because mechanism-family clustering needs
  similarity, not relatedness.

Metric: Spearman rank correlation between per-arm cosine similarity over
(w1, w2) pairs and human-rated score across all in-vocab pairs.

OOV handling: pairs where EITHER word is OOV under the arm are dropped from
the correlation for that arm. Report n_pairs_used per arm so coverage
differences are explicit (fastText covers most; word2vec/GloVe drop some).
char_trigram covers 100% by construction (any string trigrammable).

## Pre-reg bands

**Per-arm Spearman rho (mean across 3 seeds), per benchmark:**

Bands apply to the BEST-performing arm (the "best candidate" verdict):

- HARD_PASS (chain-grade-eligible encoder candidate):
  - ANY arm achieves rho >= 0.50 on WordSim353
  - AND that same arm achieves rho >= 0.40 on SimLex-999
- HARD_FAIL (test setup broken OR substrate-product fundamentally blocked):
  - ALL arms achieve rho < 0.25 on WordSim353
- MIDDLE_BAND: otherwise

**Expected priors (informational; not bands):**
- word2vec/GloVe/fastText on WordSim353: rho ~ 0.6-0.7 (canonical lit)
- word2vec/GloVe/fastText on SimLex-999: rho ~ 0.4-0.45 (harder benchmark)
- char_trigram on WordSim353: rho ~ 0.10-0.20 (orthographic noise floor)
- char_trigram on SimLex-999: rho ~ 0.05-0.15 (even lower; orthography
  unrelated to pure similarity)

If word2vec falls below rho ~ 0.40 on WordSim353, the test setup is wrong
(gensim model load failed, projection broken, lookup miscoded). This is the
sanity-test the cell uses to distinguish "encoder broken" from "benchmark
broken".

## Sanity self-test (--self-test)

T1-T4 unit-test the primitives, then:
- T5 planted-pair: on (("king","queen"),("king","potato")) all SEMANTIC arms
  must rank cosine(king,queen) > cosine(king,potato). char_trigram baseline
  may fail (orthography random vs. semantics).
- T6 projection determinism: same seed -> identical Gaussian P (regression
  guard).
- T7 verdict-shape: synthetic units exercise HARD_PASS, HARD_FAIL,
  MIDDLE_BAND paths.

## Implementation notes

- Pure numpy + gensim + scipy. Zero LLM at inference. Substrate-only-decode
  gate intact (decode = cosine on bipolar HD; no torch needed).
- DOES NOT touch substrate Store, atoms, or W matrix. Pure encoder quality
  test.
- ASCII-only, no unicode in source / output.
- Per-seed checkpointing via `experiments/_seed_checkpoint.py`.
- atexit synthesizer to recover metrics on timeout.
- Benchmark files pre-cached at `data/encoder_eval_benchmarks/` (committed
  with cell; no network at runtime). Cell falls back to download with same
  URLs if files missing.

## Routing

- Queue: `local_cpu_queue` (numpy-only; smoke + small enough for laptop;
  gensim models already cached locally at `data/gensim_cache/`).
- Timeout: 1800s (smoke <= 60s; full ~5-10min wall after model loads).
- Expected runtime: full ~5-10min (model loads dominate; correlation
  compute is sub-second).

## Cites
- `experiments/exp_encoder_word2vec_substrate_bind_v1.py` (sibling cell;
  same pretrained arm pattern, different metric; this cell uses external
  ground truth instead of substrate-internal cleanup/BPC).
- Mikolov 2013 word2vec / Pennington 2014 GloVe / Bojanowski 2017 fastText.
- Finkelstein 2001 WordSim353 / Hill 2015 SimLex-999.
- USER 2026-06-23 contamination diagnosis.
- USER 2026-06-22 NO-MiniLM-NO-BGE directive (only open-weights scientific
  encoders).
