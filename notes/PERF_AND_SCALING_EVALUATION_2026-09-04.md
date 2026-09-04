# SUBSTRATE PERF & SCALING EVALUATION (2026-09-04)

*Owner asked: scale? speed? parallelization? anything else? — answered from measurement (all figures warm,
2-thread, LitBank; cProfile used only for the RELATIVE hotspot map, which it inflates ~3-4x).*

## MEASURED STATE (after this session's speedups: parser 3.5x, tagger 4.5x, tag-calls 321→111)
| metric | value |
|---|---|
| warm read, FULL (all 11 dims) | **~3.6s/doc** (0.05s/sentence) |
| warm read, LEAN (`all_capabilities_off()`) | **0.685s/doc — 5.3x faster** |
| cold start (import + first-read asset loads) | ~16s (once per process) |
| 64-doc board | ~4 min · 10k-doc corpus ~10.5 hr/core FULL, ~2 hr/core LEAN |

**Per-dimension marginal cost (full − with-it-off):** bind_entity_states **+1.33s** (the single biggest),
track_affect +0.81s (drags in a redundant NLTK tagger), cm_agent +0.79s, cm_agent_struct +0.78s (a 2nd,
incremental parse), referent_per_np +0.74s, structural_patient +0.60s, track_goals +0.53s, track_belief +0.15s.
**The expensive dimensions are exactly the ones that PARSE — the parser is the shared cost.**

**Hotspot map:** #1 arc parser feature assembly (`sentence_flat` + **11.7M pure-Python dict.get/append/read**)
~35-50%; #2 entity-states/copular (shares the parse) ~34%; #3 affect (+ redundant NLTK tagger 2.75s); #4 POS
tagger viterbi ~7% (already optimized).

## ANSWERS
1. **Scale?** Reading scales linearly + leans + parallelizes fine. The real scaling design problem is the
   KNOWLEDGE STORES as the learner grows them (W / episodic / cortical) → must go **dense → sparse/indexed**
   (FHRR-compatible) — the standing fidelity-and-scale lever.
2. **How fast?** (a) **Lean ingest = 5.3x today** (no code). (b) The arc parser is the #1 cost — two levers:
   the numpy POS-feature gather (~1.2-1.4x, byte-identical, P8-named) and the **arc-eager O(n) swap (~8x +
   more accurate)**, blocked only by 19c register-brittleness = the filed register-general parser. (c) Route
   the redundant NLTK tagger through the fast path (~2.75s, byte-identical). (d) Warm-worker pool amortizes
   the ~16s cold start.
3. **Parallelization?** **Embarrassingly parallel ACROSS DOCUMENTS** (stateless, deterministic, cache reset
   per read) → process-parallel (GIL blocks threads for the pure-Python parser) scales ~linearly with cores +
   the remote box. **10k docs lean + 16-way ≈ 8 min, not 10 hr.** Intra-read is limited by the sequential
   accumulation (coref/timeline) — cross-doc is the clean axis.
4. **Anything else?** The redundant NLTK tagger; the ~16s cold start (warm-worker pool); a first-class lean
   "ingest profile"; the store sparse/indexed scaling; a per-dimension cost profile for tuning.

## FILED OPTIMIZATION PROBLEMS (from this evaluation)
- `lean_ingest_profile_and_parallel_corpus_read_harness_for_scale` (pri 8) — the 5.3x lean + cross-doc
  parallel harness; the enabling infra for the knowledge-foundation/learner corpus work.
- `route_the_redundant_nltk_perceptron_tagger_through_the_fast_hdlab_tagger` (pri 9) — byte-identical ~2.75s cut.
- `numpy_vectorize_the_arc_parser_pos_only_joint_features_p8_named_lever` (pri 10) — the P8-named byte-identical gather.
- (the arc-eager register-general parser — the bigger parser lever — is already filed as the who-did-what parser problem.)
