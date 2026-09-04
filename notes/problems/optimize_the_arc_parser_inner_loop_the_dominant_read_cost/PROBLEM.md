---
priority: 8
review:
review_text:
---

# PROBLEM: the arc parser's inner feature-ID loop is the DOMINANT read cost (~73% of a warm read; `_arc_ids`/`_h` = ~55M Python genexpr calls/read, 179 parses/read), so every reading benchmark and every downstream organ pays it. Optimize the arc parser's per-transition feature computation (vectorize / precompute-and-hash the feature IDs / lift the hot genexprs out of Python) so a read is materially faster with BYTE-IDENTICAL parse heads + labels on the same input — a GENERAL substrate speedup (every consumer benefits), or a located negative naming the irreducible cost.

**slug:** `optimize_the_arc_parser_inner_loop_the_dominant_read_cost` — **opened:** 2026-09-04 by the strategy session from a first-hand cProfile of the reader (baseline board speed evaluation). **status:** OPEN. Strategy lands any hdlab wire (Q111). Glass-box, NO external LLM, BYTE-IDENTICAL output (this is an implementation speedup, NOT a model change).

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26)
> **DO THE RIGHT THING, NOT THE CHEAP THING.** This is a PERF/implementation problem: the parser's ALGORITHM is fixed (arc-standard, already PINNED) — the win is the IMPLEMENTATION of its feature-ID computation, with PROVABLY byte-identical output. A located negative (the cost is irreducible in pure Python; needs a C-extension we won't take) is a full pass with the number.
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
Reading a document is slow mostly because the grammar parser is slow, and the parser is slow because — for every possible attachment decision, for every sentence — it rebuilds a big bag of text features in plain Python (tens of millions of tiny operations per document). The rules it computes are correct; the way it computes them is expensive. The job: make the same computation much faster (vectorize it, precompute the feature identifiers once, or hoist the hottest loops out of interpreted Python) so the parser produces the EXACT SAME parse but in a fraction of the time. This is the single biggest lever on how long every benchmark and every reader-consuming organ takes.

## 2. WHY THIS ONE — it is the dominant, shared, always-paid cost
A first-hand cProfile of a warm `SituationReader.read()` (2026-09-04) shows `hdlab/arc_parser.py:parse` at ~73% of the read, dominated by `_arc_ids` (feature-ID assembly) and `_h` (hashing), ~55M Python-level calls/read across 179 parses. It is paid on EVERY read — the baseline board (~64 LitBank reads), every witness, every benchmark, every live consumer. A 2–4x parser speedup roughly halves the whole board and speeds every downstream organ. (The complementary shared-cache work already de-duplicated redundant parses/tags; this problem attacks the per-parse cost itself.)

## 3. HOW THE BRAIN DOES THIS (the opening move)
The parser's transition algorithm (arc-standard shift-reduce; Nivre 2004) is already the PINNED computational-level model — this problem does NOT change it. The brain-foundational content is unchanged; the lever is purely the IMPLEMENTATION of the feature scoring (the perceptron's sparse feature-ID lookup). PINNED: the parse algorithm + the feature TEMPLATE. OUR-INVENTION (to optimize): the feature-ID assembly + hashing + the per-transition Python loop. Mark PINNED vs OUR-INVENTION.

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive — first-hand cProfile 2026-09-04, doc 1023_bleak_house):** `arc_parser.parse` cumulative ~21s of a ~29s profiled read (~73%); `_arc_ids` ~18.8s / `_h` ~7.6s; 179 parses/read; ~55M primitive calls in the parser. Warm read (unprofiled) ~3.95s post shared-cache fix; the parser is the remaining bulk.
- **INFERRED (you must measure):** how much of the `_arc_ids`/`_h` cost is removable by (a) precomputing + caching feature IDs per (token, template) instead of re-hashing per transition, (b) vectorizing the per-transition feature scoring in numpy, or (c) memoizing token-local features across the O(2n) transitions of a sentence; the byte-identical speedup factor on a full read + the board; the residual irreducible cost + its cause.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: `python tools/substrate_map.py`; read `hdlab/arc_parser.py` IN FULL (`parse`, `_arc_ids`, `_h`, `_decode`, `_features`), and `hdlab/perceptron.py` (the shared sparse-feature scoring pattern the POS tagger uses too — a fix may generalize to both). Profile first-hand: `cProfile` a warm `SituationReader().read()` on a LitBank doc and confirm the `_arc_ids`/`_h` hotspot before changing anything.
- The BAR is byte-identity: capture the parse heads + labels for a set of sentences BEFORE, and assert the optimized parser reproduces them EXACTLY.

## THE BAR (can-fail; byte-identical; real speedup)
PASS = a materially faster arc parser (target: parse cost at least halved on a full read; report the measured factor on a warm read AND on the baseline board) with PROVABLY BYTE-IDENTICAL parse heads + labels on a held-out sentence set (a witness that asserts head/label equality pre/post), glass-box, NO new runtime dependency (no C-extension unless the owner approves) and NO LLM. A rigorous located NEGATIVE — the cost is irreducible in dependency-free Python, with the profile + the named bottleneck + the speedup ceiling — is a FULL PASS. Strategy lands the Q111 change.

## ALREADY TRIED / DO NOT REDO
- The per-read tag/parse MEMO (`_cached_tag`/`_cached_parse_heads`) + the arc-eager route + the entity-states shared-cache fix already removed REDUNDANT parses (179 was 179 unique-ish after de-dup; the earlier arm-A dedup took it 118->59 for the base path). This problem is the PER-PARSE inner cost, a different axis — do not re-file the memo.
- Do NOT change the parser MODEL or its feature TEMPLATE (that would change the output — this is byte-identical implementation only).
- Do NOT take a C-extension / external parser dependency without owner approval (the glass-box + reproducibility invariant).

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/`. REUSE + optimize `hdlab/arc_parser.py` (`_arc_ids`/`_h`/`parse`), possibly `hdlab/perceptron.py` (shared sparse-scoring). Add a byte-identity witness (`verification/test_arc_parser_speedup_byte_identical.py`). Strategy lands the Q111 change. Fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b if the mechanism map changes (it should not — output identical).

## DO NOT QUOTE
- Do NOT quote a speedup without the byte-identity proof (a faster parser that changes one head is a regression, not a win).
- Do NOT quote the cProfile absolute seconds as the deployment cost (profiler overhead ~3-4x); quote the WARM unprofiled read + the board delta.
