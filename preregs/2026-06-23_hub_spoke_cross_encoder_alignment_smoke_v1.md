# Prereg: hub_spoke_cross_encoder_alignment_smoke_v1

**Date:** 2026-06-23
**Anchor:** `hub_spoke_cross_encoder_alignment_smoke_v1`
**Author:** exp_dev
**Cell:** `experiments/exp_hub_spoke_cross_encoder_alignment_smoke_v1.py`

## Why

Damasio convergence-divergence zone (CDZ) analog at word-only scope. USER
2026-06-23 explicitly approved this with caveat: "understanding that this will
only be applicable to words right. we'll need to test again when we understand
the encoding for other context islands."

Source: `notes/research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.md`
HEADLINE = hub-and-spoke federation. The HUB is a shared substrate HD subspace
that aligns outputs from multiple encoder spokes so the same concept produces
the same hub vector regardless of which spoke encoded it. Brain analog:
posterior medial cortex CDZ integrating V1/A1/S1 streams into unified concept
representations.

This cell tests the hub MECHANISM with word-only spokes (word2vec / GloVe /
FastText -- all from Path A which we validated as good word encoders via the
clean_encoder_eval_harness_v1 HARD_PASS). LATER cells will add atom-spoke +
entity-spoke + relation-spoke. The hub primitive itself is the substrate-native
operation being tested here.

## Design

4 hub-mechanism ARMs x 3 word-encoder spokes x V words x N_seeds:

- Reference vocab: words drawn from WordSim353 + SimLex-999, filtered to in-vocab
  on ALL 3 spokes. Capped at V=200 (smoke); V=30 in `--smoke` mode.
- 3 spokes: `w2v` (word2vec-google-news-300), `glove` (glove-wiki-gigaword-300),
  `ft` (fasttext-wiki-news-subwords-300). All cached at `data/gensim_cache/`.
- Each word w -> 3 spoke vectors (300d) -> hub representation at N_DIM=4096 per
  ARM.

**Arms (hub-mechanism candidates):**
- `ARM_NO_HUB_RAW` -- baseline; project each spoke's 300d to 4096d via fresh
  per-spoke random Gaussian; NO normalization, NO fusion. Expected to fail.
- `ARM_NO_HUB_PROJECT` -- same as RAW but L2-normalize per-spoke projection.
  Still no fusion across spokes. Expected to fail.
- `ARM_BIND_BUNDLE_HUB` -- substrate-native HRR-style multi-spoke integration.
  All spokes share a single Gaussian projection to 4096d (only difference =
  bind tag); sign-normalize projection to bipolar; bind each spoke's projection
  with its SPOKE_TAG bipolar tag (random per spoke, fixed per seed); bundle by
  sum; sign-normalize bundle to bipolar hub. Per-spoke readout = unbind(hub,
  SPOKE_TAG). The proposed primitive.
- `ARM_LEARNED_LINEAR_ALIGN` -- learned linear projection per-spoke (W_w2v,
  W_glove, W_ft) trained to minimize same-word cross-spoke squared distance and
  push apart diff-word cross-spoke distance. Initialized with shared Gaussian
  warm-start; SGD ~200 epochs (~30 in smoke). Backprop upper-bound baseline.

## Metric

Cross-encoder alignment discrimination ratio per arm:

    same_word_align = mean over w of cosine(hub_X[w], hub_Y[w])
                       averaged across all encoder-pairs (X,Y) in {w2v, glove, ft}
    diff_word_align = mean over (w, w') w!=w' of cosine(hub_X[w], hub_Y[w'])
                       averaged across all encoder-pairs
    discrimination  = same_word_align / max(|diff_word_align|, 1e-6)

For ARM_BIND_BUNDLE_HUB the per-spoke "hub readout" is `unbind(hub[w], SPOKE_TAG_X)`.
For ARM_LEARNED_LINEAR_ALIGN it is `W_X @ spoke_vec_X[w]` (L2-normed).
For ARM_NO_HUB_* it is `project_to_4096(spoke_vec_X[w])` per spoke (independent
projections; expected cross-spoke cosine ~0 = discrim ~1 on random JL projections).

## Pre-reg bands

**HARD_PASS (chain-grade-candidate for word-substrate hub primitive; later spoke
classes still need separate validation per USER caveat):**
- `ARM_BIND_BUNDLE_HUB` discrim_mean >= 3.0 AND
- `ARM_LEARNED_LINEAR_ALIGN` discrim_mean >= 5.0 AND
- both >= 2.0x `ARM_NO_HUB_RAW` discrim_mean

**HARD_FAIL (hub mechanism null even with backprop; word-encoder ensembles do
not fuse cleanly):**
- ALL 4 arms discrim_mean <= 1.5

**MIDDLE_BAND:** otherwise. Partial; one mechanism works but not the other.

**Expected priors (informational; not bands):**
- ARM_NO_HUB_RAW ~ 1.0-1.1 (independent JL projections of 300d -> 4096d; cross-
  spoke cosine of independent random projections is near 0; ratio of small same/
  small diff is unstable but near 1).
- ARM_NO_HUB_PROJECT ~ 1.0-1.2 (normalization can give same-word slightly above
  diff-word because per-spoke geometry of related-word vectors leaks through).
- ARM_BIND_BUNDLE_HUB ~ 2-5 if mechanism works; ~1 if bundle collapses to
  noise floor (signal-to-noise of 3-way bundle in bipolar HD).
- ARM_LEARNED_LINEAR_ALIGN ~ 5-20 if SGD converges (W_X learn aligned subspace);
  ~1 if optimization fails / instability.

## Sanity self-test (--self-test)

T1-T9 unit-test primitives (bipolar HV, sign_normalize, bind/unbind self-inverse,
spoke_tag determinism, Gaussian projection determinism + JL scale,
cross_encoder_discrim on identical hubs / random hubs, arm_bind_bundle_hub round
trip, arm_no_hub_raw low discrim).

T10 verdict-shape harness exercises HARD_PASS, HARD_FAIL, MIDDLE_BAND paths.

**Runtime identity check** (in run_unit): when all 3 spokes are IDENTICAL
(artificial; uses word2vec 3x), discrimination should be very high across ALL
arms (well above HP threshold). Reported as `sanity_identical_spokes` in
metrics; if BIND_BUNDLE shows weak discrim under identical spokes, the
implementation is broken (mechanism rejection NOT supported).

## Scope caveat (USER 2026-06-23)

**Word-only scope.** Whether the hub-and-spoke mechanism transfers to:
- atom-spokes (substrate atoms via their hd_vec field)
- entity-spokes (KG entities via their string + relations)
- relation-spokes (substrate relation types)

is a SEPARATE later cell, DEFERRED. The chain-grade-eligibility from a HARD_PASS
here applies ONLY to word substrate hub primitives. Non-word spokes require
their own validation cell before chain-grade onboarding.

## Implementation notes

- Pure numpy + gensim. Zero LLM at inference. Substrate-only decode (decode =
  cosine).
- DOES NOT touch substrate Store, atoms, or W matrix. Pure mechanism test on
  external pretrained encoders.
- ASCII-only, no unicode in source / output.
- Per-seed checkpointing via `experiments/_seed_checkpoint.py` (PROT-021
  config-mismatch guard with `run_config={N, run_mode}`).
- atexit synthesizer to recover metrics on timeout / signal.
- Benchmark files pre-cached at `data/encoder_eval_benchmarks/`; encoder models
  pre-cached at `data/gensim_cache/` (no network at runtime).

## Routing

- Queue: `local_cpu_queue` (numpy-only; gensim model cache already local;
  smoke+full bundled because cell wall <15min expected).
- Timeout: 1800s (smoke <= 60s; full V=200 x 3 seeds x 4 arms; SGD-arm dominant
  at ~200 epochs x 3 spokes x V matmul; expect ~3-8min full after model loads).

## Cites

- `experiments/exp_clean_encoder_eval_harness_v1.py` (sibling; validated the 3
  spokes as good word encoders -- HARD_PASS prerequisite for this hub test).
- `notes/research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.md`
  (source of hub-and-spoke federation proposal).
- Damasio 1989 (convergence-divergence zones, posterior medial cortex).
- Kanerva 2009 (HRR / VSA; bind+bundle primitive).
- USER 2026-06-23 hub-spoke word-only first cell approval (explicit caveat:
  "only be applicable to words right; we'll need to test again when we
  understand the encoding for other context islands").
