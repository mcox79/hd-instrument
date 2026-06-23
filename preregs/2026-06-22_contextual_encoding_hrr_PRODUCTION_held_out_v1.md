# Pre-registration: contextual_encoding_hrr_PRODUCTION_held_out_v1

**Date:** 2026-06-22
**Anchor:** contextual_encoding_hrr_PRODUCTION_held_out_v1
**Queue:** local_cpu_queue
**N:** 4096, **Seeds:** [7, 17, 23], **ARMS:** 4 (STATIC_WORD2VEC, BIND_RECENT_5, BIND_SENTENCE, BIND_WEIGHTED_PHASE)

## Scientific question

Does substrate-native context-conditional encoding via HRR-binding GENERALIZE
to **held-out contexts**? I.e., when the query context and gold-centroid
contexts are GENUINELY DIFFERENT sentences for the same sense, does the bind
mechanism still disambiguate polysemy?

This is the production upgrade of `contextual_encoding_hrr_binding_smoke_v1`
which landed HARD_PASS with bind-arm accs 0.99-1.00 but was flagged
**by-construction-saturation** by Skunkworks: the smoke query sentence and
gold-centroid were encoded from the SAME context bundle, so trivial cosine
self-identity (with 10% dropout) drove the result. The smoke does NOT
test what we actually care about: whether the bind primitive encodes
sense-level information that transfers across new sentences.

## Pre-registered bands

**HARD-PASS (substrate-native HRR-binding for polysemy GENERALIZES to held-out
contexts; chain-grade-eligible contextual-encoding primitive at production):**
- ARM_BIND_RECENT_5 mean WSD accuracy on LEAVE-ONE-OUT held-out contexts >= 0.70
- AND lift over ARM_STATIC_WORD2VEC mean >= 0.30 (absolute)

**MIDDLE:** Partial generalization. At least one bind arm beats STATIC by
> 0.05 but ARM_BIND_RECENT_5 fails to clear (acc >= 0.70 AND lift >= 0.30).

**HARD-FAIL (context-binding does NOT generalize to new contexts; the smoke
0.99 result was by-construction-saturation; mechanism null at production):**
- ALL bind-arms WSD accuracy <= ARM_STATIC_WORD2VEC + 0.05 absolute on held-out

## Calibration rationale
- 5-way classification: random baseline = 0.20.
- STATIC on held-out should land near 0.20-0.40 (one vector per word; no
  discriminative sense information; centroids collapse to identical bundles
  across senses; ties broken by argmax index = uninformative).
- 0.70 = substrate-product threshold for a polysemy primitive (covers
  3-out-of-5 senses correctly on average; > 3x random for 5-way).
- 0.30 absolute lift requirement is the strict held-out-generalization bar:
  rules out coincidental hits where STATIC happens to score 0.50-0.65 by
  fortune of which sense centroid happens to align with the pooled vector.
- The HARD-FAIL band catches the "binding generalization fails entirely"
  outcome which falsifies the substrate-native polysemy mechanism at
  production regime and routes the arc to a different lever (sense-induction
  primitive, learned-context-tag mechanism, or explicit memory-lookup).

## Key design difference from smoke

| Aspect | Smoke (flagged) | PRODUCTION (this cell) |
|---|---|---|
| Tuples | 30 words x 5 senses x 1 sentence | 50 words x 5 senses x **4 distinct contexts** = 1000 |
| Query | sentence_i for (w, s_i) | context_j for (w, s_i, c_j) |
| Gold centroid | same sentence_i (with 10% dropout) | mean of OTHER 3 contexts (j' != j) for (w, s_i) |
| Generalization required | none (self-identity) | TRUE (sense transfers across distinct contexts) |
| Sanity check | monosemous trivial 100% | same-context branch reproduces smoke 0.99-1.00 |

This is true leave-one-out cross-validation: the query's own context vector
is NEVER part of the gold-centroid it is compared against.

## N-suffix section
Anchor has no `_n<N>` suffix; PROT-018 / PROT-019 / PROT-021 do not apply
(production N=4096 is set in source as constant; bounded by 1000-tuple
dataset and 3-seed runs).

## Timeout estimate

Each seed: 4 arms x 1000 tuples x 5-centroid argmax x N=4096 vector ops.
Per tuple: ~5 N=4096 cosine ops + 1 encode = ~5e4 flops; per arm ~5e7 flops.
Per seed (4 arms x 1000 tuples): a few minutes including word2vec lookup.
Total wall for 3 seeds: ~10-15 minutes (well under any timeout).

formula: ceil(1.5 * 600s * 1.0 * (3/1)) = 2700s. Set --timeout 3600 for safety
(also accommodates word2vec first-load cache miss if needed).

## Mechanism design
- Synthetic 50-polysemous-word x 5-sense x 4-context dataset = 1000 tuples.
- Each context is a hand-written sentence (5-10 words) so the disambiguating
  sense is unambiguous to a human reader.
- 4 distinct contexts per sense: written so each conveys the same sense but
  shares minimal vocabulary; this ensures the context bundle generalizes by
  sense-level features, not by lexical overlap.
- bind operator: element-wise product on sign-quantized bipolar vectors
  (substrate-native HRR binding analog; involutive).
- bundle operator: mean + L2-normalize + sign-quantize.
- Same-context sanity branch: for each (w, s, c) re-runs the smoke-style
  query=centroid identity check; should reproduce 0.99-1.00.

## Cites
- experiments/exp_contextual_encoding_hrr_binding_smoke_v1.py (smoke; flagged)
- preregs/2026-06-22_contextual_encoding_hrr_binding_smoke_v1.md (smoke prereg)
- Skunkworks by-construction-saturation tiering (META atom 2026-06-22)
- USER 2026-06-22 strategic direction: substrate-native primitives must
  generalize across held-out evaluation; not by-construction-saturation
- Pre-existing word2vec-google-news-300 in data/gensim_cache/
