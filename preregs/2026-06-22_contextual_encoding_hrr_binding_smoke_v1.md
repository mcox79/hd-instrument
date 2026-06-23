# Pre-registration: contextual_encoding_hrr_binding_smoke_v1

**Date:** 2026-06-22
**Anchor:** contextual_encoding_hrr_binding_smoke_v1
**Queue:** local_cpu_queue
**N:** 4096, **Seeds:** [7, 17, 23], **ARMS:** 4 (STATIC_WORD2VEC, BIND_RECENT_5, BIND_SENTENCE, BIND_WEIGHTED_PHASE)

## Scientific question
Does substrate-native context-conditional encoding via HRR-binding
( word_in_context[t] = bind(word2vec[w_t], context_vec[t]) ) give substrate
polysemy disambiguation that static encoding (Path A word2vec; one vector per
word) cannot? Brain analog: hippocampus CA3 pattern separation + dentate gyrus
sense-tagging by context. Substrate-native: a polysemous word (apple, bank,
bass, ...) carries its disambiguating sense via element-wise bind with a
context bundle of recent / sentence-level / position-weighted words.

## Pre-registered bands

**HARD-PASS (context-binding works; chain-grade-eligible substrate primitive for polysemy):**
- ANY bind-arm mean WSD accuracy across seeds >= 0.70
- AND lift over ARM_STATIC_WORD2VEC mean >= 0.25 (absolute)
- AND cv across seeds for the winning arm <= 0.30 (stability)

**MIDDLE:** Some bind-arm beats STATIC by >= 0.10 absolute but fails to clear 0.70 OR cv > 0.30.

**HARD-FAIL (context-binding does not disambiguate; substrate-only conversational context is structurally hard):**
- ALL bind-arms WSD accuracy <= ARM_STATIC_WORD2VEC + 0.05 absolute

## Calibration rationale
- Static word2vec on a polysemous WSD task is expected near chance because one
  vector per word cannot encode sense; on a synthetic dataset where the WRONG
  sense centroid is genuinely WRONG, STATIC should land around 0.20-0.40
  (closer to whichever sense centroid happens to be similar to the static
  pooled embedding, but no discriminative context information).
- 0.70 is the substrate-product threshold for a polysemy primitive (covers
  3-out-of-5 senses correctly on average; > 2x random for 5-way).
- 0.25 absolute lift requirement guards against the binding arms hitting 0.70
  by coincidence on a dataset where STATIC happens to also score 0.65.
- The HARD-FAIL band catches the "binding adds noise but no signal" outcome,
  which would falsify the substrate-native polysemy mechanism and route the
  arc to a different lever (sense-induction, learned context, etc.).

## N-suffix section
Anchor has no `_n<N>` suffix; PROT-018 / PROT-019 / PROT-021 do not apply
(smoke cell; production N=4096 is set in source as a config constant; smoke
runs full N=4096 on a tiny 150-pair dataset, projected so wall is bounded).

## Timeout estimate
This anchor is a smoke cell by name; the queued FULL run is itself bounded.
Estimated wall: 4 arms x 3 seeds x ~30s/seed (word2vec load is cached + ~150
pairs at N=4096 + ~30 sense-centroid argmaxes) = ~6 minutes total.
Smoke (single seed, V_DATA=30 pairs): ~30 seconds.
formula: ceil(1.5 * 30 * 1.0 * (3/1)) = ~135s -> rounded up to 600s for safety.
timeout_s = 600

## Mechanism design (informative)
- Synthetic 30-polysemous-words x 5-sense-contexts = 150 (word, context) pairs.
- Each context is a short sentence (5-10 words) hand-written so the
  disambiguating sense is unambiguous to a human reader.
- Sense centroids are computed by averaging the bind-encoded vectors of the
  4 other contexts for the SAME (word, sense); held-out context is the query;
  evaluation = cosine to gold-sense centroid > cosine to any wrong-sense centroid.
- bind operator: element-wise product on sign-quantized bipolar vectors
  (substrate-native HRR binding analog; involutive: bind(bind(a,b),b) = a).
- bundle operator: mean + L2-normalize.
- Sanity self-test (endpoint): on a monosemous word with one meaning, all arms
  should achieve 100% accuracy (only one sense; trivially correct).

## Cites
- experiments/exp_encoder_word2vec_substrate_bind_v1.py (encoder loader pattern)
- experiments/exp_polysemy_context_bound_cpu_v1.py (concept-bind precedent)
- hdlab/char_trigram_encoder.py (substrate primitive)
- USER 2026-06-22: top-tier substrate-only-product enabler; hippocampus/CA3 brain analog
- Pre-existing word2vec-google-news-300 in data/gensim_cache/
