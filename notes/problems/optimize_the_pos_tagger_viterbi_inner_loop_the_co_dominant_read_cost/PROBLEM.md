---
priority: 8
review:
review_text:
---

# PROBLEM: with the arc parser now 3.5x faster (P8) and redundant tag passes de-duplicated (perf sweep #2), the POS tagger's per-call Viterbi is the CO-DOMINANT warm-read cost (~28% of a profiled read — `hdlab/perceptron.py._viterbi` + `hdlab/pos_tagger.py.pos_features`): every sentence is tagged by a structured-perceptron Viterbi that rebuilds sparse text features + dict weight lookups per token per tag-transition. Optimize the tagger's per-call feature assembly + Viterbi scoring (memoize/hoist the token-local features, batch the weight lookups) so a read is materially faster with BYTE-IDENTICAL tags on the same input — a GENERAL substrate speedup (every read pays the tagger), or a located negative naming the irreducible cost. This is the SAME memoization/hoist technique P8 used on the parser, but a DIFFERENT code path (dict-based structured perceptron, not the crc32 2^21 hashed vector) — a separate byte-identical fix, not a free ride; and it is DISTINCT from the already-SOLVED tagger CALIBRATION problem (that was accuracy, this is cost).

**slug:** `optimize_the_pos_tagger_viterbi_inner_loop_the_co_dominant_read_cost` — **opened:** 2026-09-04 by the strategy session, the explicit adjacent-component follow-on the owner-DONE `optimize_the_arc_parser_inner_loop_the_dominant_read_cost` (P8) named. **status:** OPEN. Strategy lands any hdlab wire (Q111, default-ON if byte-identical, witnessed). Glass-box, NO external LLM, NO new runtime dependency.

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26)
> **DO THE RIGHT THING, NOT THE CHEAP THING.** The mission is the most brain-faithful substrate. A located NEGATIVE is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed.

> ## 🧠 BRAIN-FOUNDATIONAL CHECKLIST (the owner's standing bar — work through IN ORDER; the solution is not done until every box holds)
> 1. **OPEN — how does the BRAIN do THIS?** Name the specific structure + computation and replicate that OPERATION as the FIRST move; mark each choice PINNED vs OUR-INVENTION. RESEARCH AGGRESSIVELY wherever you are unsure — do not build the tractable thing and cite neuroscience after.
> 2. **REUSE — does an existing organ already do what you need?** Check `tools/substrate_map.py` / `tools/reader_capabilities.py` / `hdlab/` FIRST; extend a matching organ rather than re-deriving it.
> 3. **GENERALIZE — does this need to generalize, and HOW does the brain generalize it?** Build for that (register / novelty / transfer), not for the single test.
> 4. **HIT A WALL? GO DEEPER, DON'T STOP.** Research-drill WHY. If the brain can do it, it IS possible and we can too, once we understand it. A located NEGATIVE counts only if the brain's ACTUAL mechanism, faithfully built, is what failed (fair test: can-fail, one-variable, real baseline).
> 5. **OPTIMIZE BY EXACT REPLICATION.** Evaluate aggressively, with great precision, EXACTLY how the brain does it, and replicate it exactly — copy the computation, SWEEP (never adopt) the parameters. No half-effort: the closer we are, the better we do.
> 6. **PERFORMANCE vs THE BRAIN.** How does our performance compare to a competent brain/reader on this task? WHERE ALONG THE CHAIN do we lose signal? What EXACTLY differs between our implementation and the brain's mechanism (an itemized mechanism-diff)?
> 7. **ADJACENT COMPONENTS.** Map the capabilities, limitations, opportunities, and brain-foundational status of the adjacent components — that seeds the next problems to address.
> 8. **COMPLETION BAR.** Is this a COMPLETE, EXCELLENT solved problem? Is it FULLY brain-foundational, conveying ALL the benefits of the brain function we replicate? If not, keep pushing toward a fully complete, exceptional solution.

## 1. THE PROBLEM IN PLAIN LANGUAGE
Reading a document runs a grammar tagger over every sentence to label each word's part of speech, and that tagger is now one of the two slowest steps in a read (the parser was the other, just made ~3.5x faster). The tagger is slow for the same reason the parser was: for every word, for every candidate label, it rebuilds a bag of small text features in plain Python and looks each one up in a big dictionary of weights — millions of tiny operations per document. The labels it produces are correct; the way it computes them is expensive. The job: make the SAME computation much faster (compute each word's features once, batch the weight lookups, hoist the hottest loops out of interpreted Python) so the tagger produces the EXACT SAME tags in a fraction of the time. Every read pays the tagger, so this speeds every benchmark and every reader-consuming organ.

## 2. WHY THIS ONE — it is the co-dominant, shared, always-paid cost now that the parser is fixed
P8's first-hand profile placed the POS tagger at ~28% of a warm read (`perceptron._viterbi` + `pos_tagger.pos_features`), now co-dominant with the (already-optimized) parser. The perf sweep #2 already cut the NUMBER of tag calls (321→111 on a 71-sentence read, ~1.05s saved) — this problem is the PER-CALL cost of each remaining Viterbi tag, a different axis. It is paid on EVERY read (the baseline board, every witness, every benchmark, every live consumer), so a byte-identical 1.5–3x tagger speedup compounds with P8 across the whole substrate. P8 explicitly named this as "the cleanest genuinely-NEW speed follow-on: high-value, low-risk, byte-identical."

## 3. HOW THE BRAIN DOES THIS (the opening move)
Lexical-category assignment is a graded, cue-based perceptual classification (the PINNED computational-level model, already validated — Kuperberg-Jaeger 2016; the structured perceptron / CRF posterior). This problem does NOT change the model or its feature TEMPLATE — the brain-foundational content is unchanged; the lever is purely the IMPLEMENTATION of the sparse feature scoring. PINNED: the tagging model + the feature template + the Viterbi decode. OUR-INVENTION (to optimize): the per-token feature-string assembly + the dict weight lookups + the per-transition Python loop. Mark PINNED vs OUR-INVENTION. (Measurement/speed is HYGIENE, not the mission — but the always-paid nature makes it a real force-multiplier, exactly as the parser fix was.)

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive — P8's first-hand profile 2026-09-04):** the POS tagger is ~28% of a warm read (`perceptron._viterbi` + `pos_tagger.pos_features`), co-dominant with the parser; it uses the SAME sparse-feature-scoring shape as the parser (build feature strings → dict weight lookup) but a DIFFERENT code path (dict-based structured perceptron, not the crc32 2^21 hashed vector). The perf sweep #2 already reduced tag CALLS to ~1.56x n_sentences (the redundancy axis is closed; this is the per-call cost).
- **INFERRED (you must measure):** how much of `pos_features`/`_viterbi` is removable by (a) precomputing each token's local features ONCE (they do not depend on the tag transition), (b) batching the weight lookups (gather over an integer-coded feature table, or a numpy score matrix) instead of per-token-per-tag dict-gets, (c) hoisting the transition scoring out of the Python inner loop; the byte-identical speedup factor on a warm read + the board; the residual irreducible cost + its named cause.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: `python tools/substrate_map.py`; read `hdlab/pos_tagger.py` IN FULL (`tag`, `pos_features`, the asset schema) and `hdlab/perceptron.py` (`_viterbi`, the weight structure); note P8's landed pattern in `hdlab/arc_parser.py` (`FeatCache`/`sentence_flat`/`sentence_scores` + the `np.add.reduceat` batched scoring, verified bit-identical) as the reference technique — but the tagger's weights are a DICT, not a 2^21 vector, so the mechanism transfers but the data structure does not.
- Profile first-hand: `cProfile` a warm `SituationReader().read()` on a LitBank doc and confirm the `_viterbi`/`pos_features` hotspot before changing anything.
- The BAR is byte-identity: capture the tags for a held-out sentence set BEFORE, and assert the optimized tagger reproduces them EXACTLY (tie-breaking included — a faster Viterbi that flips one argmax on a score tie is a regression).

## THE BAR (can-fail; byte-identical; real speedup)
PASS = a materially faster POS tagger (target: tagger per-call cost at least halved on a warm read; report the measured factor on a warm read AND the read-level delta) with PROVABLY BYTE-IDENTICAL tags on a held-out sentence set (a witness that asserts tag-sequence equality pre/post, at scale, on documents NOT used to tune), glass-box, NO new runtime dependency (no C-extension unless the owner approves) and NO LLM. A rigorous located NEGATIVE — the cost is irreducible in dependency-free Python, with the profile + the named bottleneck + the speedup ceiling — is a FULL PASS. Strategy lands the Q111 change (default-ON, byte-identical, the witness is the gate).

## ALREADY TRIED / DO NOT REDO
- The per-read tag MEMO (`_cached_tag`) + perf sweep #2 already removed REDUNDANT tag CALLS (321→111/read) — this problem is the PER-CALL Viterbi cost, a different axis. Do NOT re-file the call-count dedup.
- Do NOT change the tagger MODEL, its feature TEMPLATE, or the CALIBRATION (the SOLVED `upgrade_the_pos_tagger_to_a_calibrated_joint_decoded_posterior` was ACCURACY; this is byte-identical SPEED only — changing tags would fail the bar).
- Do NOT take a C-extension / external tagger dependency without owner approval (the glass-box + reproducibility invariant).
- The parser got this treatment already (P8, `hdlab/arc_parser.py`) — REUSE the technique (per-template id caches + batched `reduceat` scoring, byte-identity by construction), do not re-derive it; adapt it to the dict-weight structure.

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/`. REUSE + optimize `hdlab/pos_tagger.py` (`pos_features`, `tag`) + `hdlab/perceptron.py` (`_viterbi`, weights). Reference P8's landed `hdlab/arc_parser.py` fast path + `verification/test_arc_parser_fast_path_landing.py` for the byte-identity-witness pattern. Add a byte-identity witness (`verification/test_pos_tagger_speedup_byte_identical.py`). Strategy lands the Q111 change. No `BRAIN_FOUNDATIONAL_AUDIT.md` §2b fidelity change is warranted (output identical) — fold only a note if the mechanism map changes.

## DO NOT QUOTE
- Do NOT quote a speedup without the byte-identity proof at scale (a faster tagger that flips one tag is a regression, not a win — and tags feed the parser, so one flip can cascade).
- Do NOT quote the cProfile absolute seconds as the deployment cost (profiler overhead ~3-4x); quote the WARM unprofiled read + the read-level delta.
- Do NOT conflate this with the tagger CALIBRATION problem (SOLVED) — that changed the posterior for accuracy; this changes NOTHING about the output.
