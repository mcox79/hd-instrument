---
review: EXCELLENT
review_text: Reverified first-hand test_affect_reroute_hdlab_tagger.py 6/6 (pre-land byte-identity vs NLTK) + a new pure-hdlab landing witness test_affect_reroute_landing.py (VALENCED byte-identity vs the NLTK reference 0 flips/1124; NLTK-free read; skip-valence byte-identical ternary). LANDED: hdlab/situation_reader._assign_affect tags via the shared _load_frontend UD-EWT tagger (one category system) instead of the second NLTK averaged-perceptron tagger; hdlab/context_grounded_valence.score_item gains need_valence (default True = byte-identical) so the affect wire skips the 2 discarded torch matmuls/event. ~0.37s/read off the affect path (NLTK 195->0 calls). Valenced output (HARM/HELP) byte-identical (0/8947); the inert None<->NA provenance bit differs ~9% (0 consumers branch on it -- a full-pass located-negative sub-finding). Witness's C4 is a stale pre-land NLTK-tokenizer control (becomes the ~9% tagger-divergence measure post-land; SOLVED said 5/5 post-land) -- superseded by the clean landing witness. Follow-on filed: the arc-labeler fast-path (~10x the affect tagger; _FastLabelPlan built + witnessed, ready). §2b folded. INTEGRATED 2026-09-05.
---

# PROBLEM: a warm read spends ~2.75s (profiled, 627 calls) in NLTK's averaged-perceptron tagger (`nltk/tag/perceptron.py`) — a SECOND, slower, redundant POS tagger reached from the affect/valence path (`track_affect` is +0.807s of the read; the NLTK tagger is a large part of it). The substrate already has a fast, calibrated, byte-identical hdlab POS tagger (`hdlab/pos_tagger.py`, ~4.5x faster after the P8-follow-on landing) + a shared per-read tag cache (`_cached_tag`). Route the affect/valence tagging through the hdlab fast tagger + the shared cache (the same move as perf sweep #2) so the read drops the redundant NLTK tagger with BYTE-IDENTICAL affect/valence output — or a located negative naming why the NLTK tags cannot be reproduced by the hdlab tagger (a genuine tagset/behaviour difference).

**slug:** `route_the_redundant_nltk_perceptron_tagger_through_the_fast_hdlab_tagger` — **opened:** 2026-09-04 by the strategy session (the perf/scaling evaluation found the redundant NLTK tagger in the affect path). **status:** OPEN. Strategy lands any hdlab wire (Q111, witnessed). Glass-box, byte-identical, NO external LLM. Optimization.

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26)
> **DO THE RIGHT THING, NOT THE CHEAP THING.** A located NEGATIVE is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed.

> ## 🧠 BRAIN-FOUNDATIONAL CHECKLIST (work through IN ORDER; not done until every box holds)
> 1. **OPEN — how does the BRAIN do THIS?** Name the structure + computation; mark PINNED vs OUR-INVENTION. RESEARCH where unsure.
> 2. **REUSE — does an existing organ already do it?** Check `tools/substrate_map.py` / `hdlab/` FIRST.
> 3. **GENERALIZE — how does the brain generalize it?** Build for that.
> 4. **HIT A WALL? GO DEEPER.** A located NEGATIVE counts only if the brain's ACTUAL mechanism, faithfully built, failed.
> 5. **OPTIMIZE BY EXACT REPLICATION.** Copy the computation, SWEEP the parameters.
> 6. **PERFORMANCE vs THE BRAIN.** Where do we lose signal? The mechanism-diff.
> 7. **ADJACENT COMPONENTS.** Map the neighbours — seeds the next problems.
> 8. **COMPLETION BAR.** COMPLETE + EXCELLENT + conveys the full benefit?

## 1. THE PROBLEM IN PLAIN LANGUAGE
The reader accidentally runs two different part-of-speech taggers: our fast one everywhere, and a slower off-the-shelf one buried in the emotion-analysis path. They do the same job. The fix: make the emotion path use the fast one (and the tags we already computed for the sentence), producing identical results with the slow tagger removed.

## 2. WHY THIS ONE — a clean, byte-identical ~2.75s/read cut, no capability change
The affect dimension (default-on) drags in NLTK's tagger; the substrate's own tagger is faster, cached, and already the reader's front end. This is pure waste — a shared, always-paid cost with zero capability tradeoff. Same pattern as the landed perf sweep #2 (private taggers → the shared cache).

## 3. HOW THE BRAIN DOES THIS (the opening move)
No new mechanism — one lexical-category system, not two. PINNED: the tagger model is unchanged (the hdlab fast tagger already IS the reader's category inference); OUR-INVENTION: only the routing. Correctness = byte-identical affect/valence output (if the two taggers disagree on some tokens, the affect output may differ — that is the thing to measure + resolve, either by mapping the tagset or documenting the residual).

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive):** ~2.75s/read in `nltk/tag/perceptron.py` (627 calls, warm read profile); `track_affect` marginal cost +0.807s; the hdlab tagger is landed + ~4.5x faster + cached.
- **INFERRED (you must measure):** whether the hdlab tagger (+ `_cached_tag`) reproduces the NLTK tags the affect path needs BYTE-IDENTICALLY on the affect output (feel/valence), and the read-time saved; any tagset/behaviour residual + its cause.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: find the NLTK tagger call site (grep the affect/valence path — `hdlab/affect_register.py`, `hdlab/context_grounded_valence.py`, `hdlab/psych_verb_frames.py` — for `nltk`/`pos_tag`); read `hdlab/pos_tagger.py` (the fast tagger) + `situation_reader._cached_tag`; profile a warm read first-hand to confirm the NLTK hotspot.
- Reproduce first-hand: the affect output (feel/valence) on a doc, then re-route + assert byte-identical.

## THE BAR (byte-identical; real speedup)
PASS = the affect/valence path tags via the hdlab fast tagger + the shared cache, with BYTE-IDENTICAL affect output (feel-category + valence) on a held-out doc set and the NLTK tagger no longer called, with the measured read-time cut. A located NEGATIVE — the hdlab tagger cannot reproduce the NLTK tags the affect path relies on (a named tagset/behaviour difference) — is a FULL PASS (then the NLTK dependency is documented, not silently kept). Strategy lands the Q111 change.

## ALREADY TRIED / DO NOT REDO
- Perf sweep #2 already unified the reader's OTHER private taggers through `_cached_tag` — REUSE that pattern; this is the affect-path NLTK tagger it did not cover.
- Do NOT change the affect OUTPUT — byte-identical is the bar.

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/`. REUSE `hdlab/pos_tagger.py`, `situation_reader._cached_tag`, the affect path (`hdlab/affect_register.py` + wherever the NLTK tagger enters). Add a byte-identity witness (affect output NLTK-route vs hdlab-route). Strategy lands the Q111 change.

## DO NOT QUOTE
- Do NOT quote the speedup without the byte-identity proof on the affect output.
- Do NOT keep the NLTK tagger silently if it cannot be reproduced — document the residual.
