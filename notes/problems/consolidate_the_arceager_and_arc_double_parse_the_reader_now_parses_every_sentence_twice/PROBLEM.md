---
priority: 7
review:
review_text:
---

# PROBLEM: since `parser_arceager` was flipped DEFAULT-ON (2026-09-05), the live reader parses every sentence TWICE per read — the base arc-factored parser (`_frontend_parser`/`_cached_parse_heads`) still runs for the shared front-end (the arc-labeler, PP/space router, copular reader) while the arc-eager parser (`_ae_parse`, `hdlab/arceager_parser`) runs for the who-did-what role heads. Both outputs are consumed (not dead code), but two full dependency parses per sentence is a real, newly-introduced read-time cost. Consolidate to ONE parse per sentence with BYTE-IDENTICAL reader output on every consumed dimension — either route the front-end consumers through the arc-eager heads (if they suffice), or route the role heads through the base parser under the labeled readout (measure which parser each head-consumer actually needs), or share one parse both can read — a GENERAL substrate speedup, or a located negative naming exactly which consumer requires which parser's heads and why one parse cannot serve both.

**slug:** `consolidate_the_arceager_and_arc_double_parse_the_reader_now_parses_every_sentence_twice` — **opened:** 2026-09-05 by the strategy session (an at-land efficiency finding from the parser integration: flipping `parser_arceager` default-on introduced a second per-read parse). **status:** OPEN. Strategy lands any hdlab wire (Q111). Glass-box, NO external LLM, BYTE-IDENTICAL reader output on every consumed dim (this is an efficiency consolidation, NOT a model change). Pairs with `add_the_arc_labeler_fast_scoring_path...` (pri 5) — the same read-cost surface.

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
The reader now runs two different grammar-parsers on every sentence — the old one for most jobs and a stronger one just for "who did what" — because we recently switched the stronger one on. Running two full parses per sentence is slower than it needs to be. The brain parses a sentence once. The job: get back to one parse per sentence without changing a single answer the reader gives.

## 2. WHY THIS ONE — a self-inflicted read-cost with a byte-identity safety net
The double-parse was introduced deliberately (the labeled readout made arc-eager register-safe, a real who-did-what win), but nobody has measured whether the two head-consumers genuinely need different parsers. Parsing is one of the two dominant read costs; halving it (or proving it can't be halved) is a clean, general speedup with a hard correctness bar (byte-identical consumed output). It pairs with the arc-labeler fast-path (pri 5) as the read-cost surface, and the answer also informs whether the base arc parser is now vestigial for the role path.

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED: the brain builds ONE incremental syntactic analysis per sentence (a single unification/attachment pass — Hagoort MUC; Vosse-Kempen), and every downstream reader (role binding, PP attachment, predication) reads off that ONE structure. Two parallel full parses is an OUR-INVENTION artifact of wiring, not a brain property. REUSE (do NOT re-derive): `hdlab/arc_parser.py` (the base arc-factored parser, already fast-pathed), `hdlab/arceager_parser.py` (the role-head parser), `hdlab/arc_labeler.py`, `hdlab/situation_reader._frontend_parser`/`_cached_parse_heads`/`_read_events_wired` (the two parse call-sites).

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive):** `parser_arceager` is default-on and register-safe under the labeled readout (+0.006 modern / +0.0045 19c, board-neutral 0.0 on all 6 dims); the base arc parser feeds the shared front-end (labeler + PP/space + copular); the arc-eager parser feeds the wired role heads. The arc parser is already fast-pathed (FeatCache/CRC ids).
- **INFERRED (you must measure):** which head-consumer requires which parser's heads (enumerate every consumer of `_cached_parse_heads` vs `_ae_parse`); whether ONE parse can serve both with byte-identical consumed output; the read-time saved by dropping the redundant parse; if not collapsible, the named consumer + reason.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `hdlab/situation_reader.py` `_frontend_parser` / `_cached_parse_heads` / `_read_events_wired` (the two parse sites) + the `parser_arceager` §2b entry in `notes/BRAIN_FOUNDATIONAL_AUDIT.md`.
- Reproduce first-hand: instrument a warm read and count parse calls per sentence (expect 2 when `parser_arceager=True`); enumerate every consumer of each parse's heads.

## THE BAR (byte-identical; a real read-time cut)
PASS = one parse per sentence on the live read path with BYTE-IDENTICAL reader output on every consumed dimension (coref/events[agent+patient]/temporal/causal/location/belief/state + who-did-what arms) and a MEASURED read-time cut, on a held-out doc set. A rigorous located NEGATIVE — one parse cannot serve both consumers, with the named consumer + the exact head-difference that forces two parses (e.g. the arc-labeler is trained on the arc parser's head distribution and its labels diverge on arc-eager heads) — is a FULL PASS (then document why the double-parse stands and close the efficiency question). Report the read-time delta + byte-identity proof; keep the slow two-parse path as a self-checkable reference until the single-parse output is proven bit-identical.

## ALREADY TRIED / DO NOT REDO
- Do NOT change `parser_arceager`'s default or the labeled readout — the who-did-what win is landed and board-neutral; this is purely about not parsing twice.
- Do NOT chase parser ACCURACY here (head accuracy is head-independent for who-did-what — three register-general head-parsing negatives on disk); this is an efficiency consolidation with a byte-identity bar.
- The arc parser inner loop is already fast-pathed (`optimize_the_arc_parser_inner_loop...`, integrated) — do not re-optimize it; the lever here is running ONE parse, not a faster parse.

## FILES AND ENTRY POINTS
Investigate + build in `experiments/` + `verification/`; the wire (if collapsible) is in `hdlab/situation_reader.py` (the two parse sites). REUSE `hdlab/arc_parser.py`, `hdlab/arceager_parser.py`, `hdlab/arc_labeler.py`. Strategy lands the Q111 wire; fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b. Pairs with `add_the_arc_labeler_fast_scoring_path_the_dominant_remaining_read_cost` (pri 5).

## DO NOT QUOTE
- Do NOT quote a read-time cut without byte-identical consumed output on a held-out doc set.
- Do NOT quote a "one parse is enough" claim without enumerating EVERY head-consumer and proving each is byte-identical on the shared heads.
- NO external LLM (the invariant).
