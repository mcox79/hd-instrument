---
priority: 5
review:
review_text:
---

# PROBLEM: the arc labeler is the single biggest remaining read-time lever — `hdlab/arc_labeler.py::ArcLabeler._predict_label` (default-on via entity-states / `bind_entity_states`) scores each arc by summing `w.get(f + "~" + lab)` over the arc's 25 features for EVERY one of 36 labels — ~900 string-concat dict lookups per arc, ~75k `_score` calls per read, ~10× the affect tagger and the dominant remaining cost the tagger-routing SOLVED note localized. The reader's POS tagger and arc parser already replaced this EXACT naive pattern with a byte-identical fast plan (`_FastEmissionPlan` / `FeatCache`); the labeler never got it. The analogous `_FastLabelPlan` is already BUILT and WITNESSED (`experiments/exp_arc_labeler_fastpath_v1.py` + `verification/test_arc_labeler_fastpath.py`, 3/3): precompute `feat -> [(label_idx, weight)]` by splitting each weight key on the LAST `~`, accumulate present weights into per-label lanes in FEATURE order, argmax in LABEL order → identical float sums + identical tie-break. Land it into `hdlab/arc_labeler.py`, built lazily in `label()` (mirroring `PosTagger._ensure_fast`), so inference uses the fast path while training stays on the reference; prove BYTE-IDENTICAL labels + a measured read-time cut on a held-out doc set, keeping the stock scoring body as a self-checkable reference. This is a byte-identical SPEEDUP, not a model change.

**slug:** `add_the_arc_labeler_fast_scoring_path_the_dominant_remaining_read_cost` — **opened:** 2026-09-05 by the strategy session, the explicit follow-on the tagger-routing SOLVED note named (§(I) localized the labeler naive scoring loop as the single biggest remaining read-time lever, and the same fast-path technique already landed for the POS tagger + arc parser). **status:** OPEN. Strategy lands the Q111 wire. Glass-box, NO external LLM; byte-identical inference.

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26)
> **DO THE RIGHT THING, NOT THE CHEAP THING.** A located NEGATIVE is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed.

> ## 🧠 BRAIN-FOUNDATIONAL CHECKLIST (work through IN ORDER; not done until every box holds)
> 1. **OPEN — how does the BRAIN do THIS?** Name the structure + computation; PINNED vs OUR-INVENTION. RESEARCH where unsure.
> 2. **REUSE — does an existing organ already do it?** Check `tools/substrate_map.py` / `hdlab/` FIRST.
> 3. **GENERALIZE — how does the brain generalize it?** Build for that.
> 4. **HIT A WALL? GO DEEPER.** A located NEGATIVE counts only if the brain's ACTUAL mechanism, faithfully built, failed.
> 5. **OPTIMIZE BY EXACT REPLICATION.** Copy the computation, SWEEP the parameters.
> 6. **PERFORMANCE vs THE BRAIN.** Where do we lose signal? The mechanism-diff.
> 7. **ADJACENT COMPONENTS.** Map the neighbours — seeds the next problems.
> 8. **COMPLETION BAR.** COMPLETE + EXCELLENT + conveys the full benefit?

## 1. THE PROBLEM IN PLAIN LANGUAGE
Every time the reader parses a sentence it labels each grammatical link (subject, object, and so on). The current code does this the slow way: for each link it loops over all 36 possible labels and, for each, adds up 25 feature-weights by building a text key and looking it up — about 900 dictionary lookups per link, tens of thousands per page. The reader's word-tagger and its parser were already sped up years ago with a trick that gives the exact same answer far faster; the labeler was simply never given that trick. The job is to bolt the same already-built, already-tested fast method onto the labeler so it produces the identical labels but runs much faster. This is a speed fix that must not change a single output.

## 2. WHY THIS ONE — it is the dominant remaining read-time cost, and the fix is already built and witnessed
The tagger-routing SOLVED note measured the labeler scoring loop as the biggest remaining read-time lever, roughly ten times the affect tagger it just fixed. The fast plan already exists and passes its witness (3/3), and it is the SAME technique that already landed byte-identical for the POS tagger and the arc parser — this is landing a proven optimization onto the one hot path that still lacks it, not inventing anything. Cheap, high-leverage, zero behavioural risk when byte-identity is enforced.

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive):** the mechanism + witness exist — `_FastLabelPlan` in `experiments/exp_arc_labeler_fastpath_v1.py` and `verification/test_arc_labeler_fastpath.py` pass 3/3, matching the labeler's reference scoring byte-for-byte on the witness set; the labeler is the ~10× dominant remaining read cost (tagger-routing SOLVED §(I)).
- **INFERRED (you must measure):** the landed read-time cut and byte-identity of the fast path against the reference body on a held-out doc set (not just the witness fixtures).

## VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: read `notes/problems/route_the_redundant_nltk_perceptron_tagger_through_the_fast_hdlab_tagger/SOLVED.md` §(I) (RESOLVED — the arc-labeler naive scoring loop) IN FULL; run `verification/test_arc_labeler_fastpath.py` and confirm 3/3.
- Read how the byte-identity-reference pattern already landed: `hdlab/pos_tagger.py` `_FastEmissionPlan` / `PosTagger._ensure_fast` and `hdlab/arc_parser.py` `FeatCache` — mirror the lazy-build + reference-kept-for-self-check shape exactly.
- Reproduce first-hand: build `_FastLabelPlan` from a loaded `ArcLabeler` and confirm it reproduces `_predict_label` byte-identically on a real doc before landing.

## THE BAR (can-fail; byte-identical inference; measured cut)
PASS = `_FastLabelPlan` landed into `hdlab/arc_labeler.py`, built lazily in `label()` (mirroring `PosTagger._ensure_fast`); inference uses the fast path, training stays on the reference; labels are BYTE-IDENTICAL to the stock `_predict_label` on a held-out doc set (not just witness fixtures), with a measured read-time cut reported; the stock scoring body is retained as a self-checkable reference. A rigorous located NEGATIVE — the labeler cannot be fast-pathed byte-identically (with the named reason, e.g. a tie-break or float-accumulation-order divergence the split-on-last-`~` plan cannot reproduce) — is a FULL PASS. Strategy lands the Q111 wire.

## ALREADY TRIED / DO NOT REDO
- Do NOT rebuild the plan — `_FastLabelPlan` already exists in `experiments/exp_arc_labeler_fastpath_v1.py` and passes its witness; REUSE it.
- Do NOT touch the training path — inference-only fast path; training stays on the reference scorer.
- This is the SAME technique as the landed POS-tagger `_FastEmissionPlan` and arc-parser `FeatCache` fast paths — do not re-derive the approach, mirror it.

## FILES AND ENTRY POINTS
Land in `hdlab/arc_labeler.py` (`label()` lazy-build, `_predict_label` reference kept). REUSE `experiments/exp_arc_labeler_fastpath_v1.py` + `verification/test_arc_labeler_fastpath.py`. Study `hdlab/pos_tagger.py` (`_FastEmissionPlan` / `_ensure_fast`) + `hdlab/arc_parser.py` (`FeatCache`) for the landed byte-identity-reference pattern. Strategy lands the Q111 wire.

## DO NOT QUOTE
- Do NOT quote a speedup without byte-identical labels demonstrated on a held-out doc set (witness fixtures alone are not enough).
- Do NOT quote a read-time cut as a comprehension change — this is a pure speedup, identical outputs.
- Do NOT use an external LLM (the invariant).
