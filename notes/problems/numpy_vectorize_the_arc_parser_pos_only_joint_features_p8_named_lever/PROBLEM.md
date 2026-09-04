---
priority: 10
review:
review_text:
---

# PROBLEM: even after the P8 fast path (3.5x, byte-identical), the arc parser's feature-ID assembly is STILL the single dominant warm-read cost (`sentence_flat` + ~11.7M pure-Python `dict.get`/`append` calls per read, profiled). P8 named the remaining byte-identical lever and left it unbuilt: the ~8 POS-ONLY joint features (which depend only on the small closed POS tagset, not open-vocabulary words) can be precomputed into an integer-coded POS×POS table and GATHERED with numpy — moving ~8 of the ~20 per-arc features out of the Python inner loop into a vectorized gather, estimated ~1.2–1.4x further, byte-identical. Build it: vectorize the POS-only joint features via a precomputed integer POS-feature table + numpy gather, keeping the word features in Python, with PROVABLY BYTE-IDENTICAL parse heads + labels + margins (the emission-matrix-level identity P8's witness pattern asserts) — or a located negative naming why the POS-only features cannot be cleanly separated + vectorized. NOTE: the BIGGER parser lever is the arc-EAGER O(n) swap (the filed `improve_the_parser_verb_argument_attachment_for_who_did_what` / register-general parser); this is the byte-identical micro-opt on the CURRENT arc-factored parser, complementary + independently shippable.

**slug:** `numpy_vectorize_the_arc_parser_pos_only_joint_features_p8_named_lever` — **opened:** 2026-09-04 by the strategy session (the P8-named further lever, surfaced again by the perf/scaling evaluation as the #1 remaining warm-read cost). **status:** OPEN. Strategy lands any hdlab wire (Q111, witnessed). Glass-box, byte-identical, NO new dependency, NO LLM. Optimization.

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26)
> **DO THE RIGHT THING, NOT THE CHEAP THING.** A located NEGATIVE is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed.

> ## 🧠 BRAIN-FOUNDATIONAL CHECKLIST (work through IN ORDER; not done until every box holds)
> 1. **OPEN — how does the BRAIN do THIS?** Name the structure + computation; PINNED vs OUR-INVENTION. RESEARCH where unsure.
> 2. **REUSE — does an existing organ already do it?** Check `hdlab/` FIRST.
> 3. **GENERALIZE — how does the brain generalize it?** Build for that.
> 4. **HIT A WALL? GO DEEPER.** A located NEGATIVE counts only if the brain's ACTUAL mechanism, faithfully built, failed.
> 5. **OPTIMIZE BY EXACT REPLICATION.** Copy the computation, SWEEP the parameters.
> 6. **PERFORMANCE vs THE BRAIN.** Where do we lose signal? The mechanism-diff.
> 7. **ADJACENT COMPONENTS.** Map the neighbours.
> 8. **COMPLETION BAR.** COMPLETE + EXCELLENT + full benefit?

## 1. THE PROBLEM IN PLAIN LANGUAGE
The grammar parser is still the slowest step. Most of its work is building millions of tiny text features in plain Python. Some of those features depend only on the small fixed set of part-of-speech tags (not on the actual words), so they can be computed once into a lookup table and fetched in fast batched math instead of one-at-a-time Python. The job: move those tag-only features to the fast batched path, produce the exact same parse, and shave more time off every read.

## 2. WHY THIS ONE — the #1 remaining always-paid warm-read cost, byte-identical
Profiled, the arc parser (`sentence_flat` + 11.7M dict ops) is ~35–50% of a warm read even after P8. This is the always-paid shared cost under every read + benchmark + the corpus ingest. P8 explicitly scoped this lever and estimated ~1.2–1.4x more, byte-identical — a clean, low-risk, unbuilt win.

## 3. HOW THE BRAIN DOES THIS (the opening move)
No mechanism change — pure implementation (P8's discipline). PINNED: the parse algorithm + the feature TEMPLATE are unchanged; OUR-INVENTION (to optimize): the integer POS-feature coding + the numpy gather for the POS-only features. Correctness = byte-identical (the same feature-id stream, same reduction — the emission-matrix identity, not just tag equality, per P8's Neumaier-sum lesson).

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive):** the arc parser is the #1 warm-read cost post-P8 (`sentence_flat` + 11.7M dict.get/append); ~8 of the ~20 per-arc features are POS-only (closed tagset); P8 estimated ~1.2–1.4x further from vectorizing them, byte-identical.
- **INFERRED (you must measure):** the exact speedup from the POS-feature-table gather, and BYTE-IDENTITY of heads + labels + margins at scale (P8's held-out witness pattern).

## VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: read `notes/problems/optimize_the_arc_parser_inner_loop.../SOLVED.md` (the fast path + the named POS-feature-gather lever + the Neumaier byte-identity lesson) IN FULL; read `hdlab/arc_parser.py` (`sentence_flat`/`sentence_scores`/`_parse_reference`, the ~20 features — identify the ~8 POS-only joint ones); read `verification/test_arc_parser_fast_path_landing.py` (the byte-identity witness to extend).
- Reproduce first-hand: the arc-parser share of a warm read + the current fast-path timing (the baseline to beat, byte-identical).

## THE BAR (byte-identical; real speedup)
PASS = the POS-only joint features vectorized via a precomputed integer POS-feature table + numpy gather (word features stay in Python), with PROVABLY BYTE-IDENTICAL parse heads + labels + margins on a held-out sentence set (emission-matrix-level identity, P8's witness pattern) and a measured further speedup on a warm read. NO new dependency (numpy only). A located NEGATIVE — the POS-only features cannot be cleanly separated/vectorized byte-identically (a named coupling), or the gather does not beat the current dict path — is a FULL PASS. Strategy lands the Q111 change (default-ON, the witness is the gate).

## ALREADY TRIED / DO NOT REDO
- The P8 fast path (per-template id cache + batched reduceat) is LANDED — this is the NEXT lever P8 named (vectorize the POS-only features), not re-deriving the fast path.
- The arc-EAGER swap is the BIGGER lever (filed separately) — this is the byte-identical micro-opt on the current parser; do not conflate.
- Do NOT touch the reduction (Neumaier byte-identity) or the word features — POS-only features only.

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/`. REUSE + optimize `hdlab/arc_parser.py` (`sentence_flat`); extend `verification/test_arc_parser_fast_path_landing.py`. Strategy lands the Q111 change. No §2b fidelity change (output identical).

## DO NOT QUOTE
- Do NOT quote a speedup without the byte-identity proof at scale (a faster parser that flips one head is a regression).
- Do NOT quote cProfile seconds as deployment cost — quote the warm unprofiled read.
