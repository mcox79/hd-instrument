---
priority: 8
review:
review_text:
---

# PROBLEM: the parser is the DOMINANT signal leak in the whole front-end (loses ~21% of heads even given perfect POS tags; its head-errors cost the labeler 3× what the tagger's do), and the ONE clear, tractable, brain-foundational fidelity gap is its REPRESENTATION: it scores attachments over SPARSE HASHED SYMBOLIC features where the brain (and neural SOTA) use DISTRIBUTED CONTEXTUAL representations. Feed the parser the substrate's OWN distributed meaning vectors (glass-box, NO LLM) to close the measured −0.083 accuracy gap — the biggest upstream accuracy multiplier.

**slug:** `distributed_contextual_representations_into_the_parser_the_tractable_accuracy_fidelity_gap` — **opened:** 2026-09-05 by the strategy session (the arc-labeler submission's whole-chain signal-loss ladder ranked this the #1 tractable brain-foundational parser fix). **status:** OPEN. Glass-box, NO external LLM. Strategy lands the Q111 wire.

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26)
> **DO THE RIGHT THING, NOT THE CHEAP THING.** Iterate to the OPTIMAL brain-foundational solution; do NOT submit the first thing that clears. The OPENING MOVE is "how does the BRAIN actually do this?" — name the structure/circuit + replicate the OPERATION. A located NEGATIVE is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed. Run a 30-min deepening cron; cancel + submit only when the brain-mechanism bar is met AND nothing more of value remains.

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
Before the reader can say who-did-what, where, or what-is-what, it has to figure out how the words in a sentence connect (which noun goes with which verb). That step gets about one connection in five wrong, and those errors ripple into everything downstream. It's wrong partly because it "sees" each word as an isolated symbol (a hashed string), not as a MEANING that carries what it typically attaches to. Give the parser the reader's own meaning vectors so it can attach "poured the tea into the CUP" using what a cup is — the way the brain does.

## 2. WHY THIS ONE — the parser is the dominant leak, and this is the ONE tractable fidelity gap
The arc-labeler submission's oracle-substitution ladder measured the whole front-end: the labeler is the strongest link (5.8% intrinsic loss); the DOMINANT leak is the PARSER (loses ~21% of heads even with gold tags; its head-errors cost the labeler 3× the tagger's). The ladder then ranked the fixes by (measured loss × brain-fidelity): the top TRACTABLE, clearly-brain-foundational one is **distributed representations** — "our parser uses SPARSE HASHED SYMBOLIC features; the brain (and SOTA) use DISTRIBUTED CONTEXTUAL representations; the brain-faithful fix = feed the parser the substrate's OWN distributed meaning vectors (present but unused by the parser) — glass-box, NO LLM. The most tractable clearly-brain-foundational upgrade" (SOTA→ours gap −0.083). PP-attachment (the canonical meaning-sensitive decision) is measured to rise 0.587→0.639 with typed grounding, still climbing toward the ~0.84 ideal. The parser is upstream of who-did-what, state, space, and goals — one accuracy gain here lifts many dims.

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED: the brain parses with DISTRIBUTED, graded lexical-semantic representations integrated into a constraint-satisfaction attachment decision (MacDonald 1994 lexicalist; Hale/Levy surprisal; the meaning of the head + dependent conditions the attachment — Pado/Resnik selectional preference; Klein&Manning 2003: it is the CLASS/subcategorization level, not word-pair memorization, that carries — bilexical is worth little). Our arc-eager/arc-factored scorers use crc32-hashed symbolic feature strings — no meaning generalization. REUSE (do NOT re-derive): the parser scoring in `hdlab/arceager_parser.py` (`parse_with_conf`) / `hdlab/arc_parser.py`; the distributed meaning vectors already on the shelf — `hdlab/meaning_foundation` (curated sense signatures) + the distributional meaning channel; the WHITENING fix (the raw vectors are collinear cos 0.92 — contrast-normalize before use, as the arc-labeler exploration measured). The move: add a TYPED (head grammatical-function) selectional-preference feature computed from distributed vectors into the attachment score — a CLASS-level cue, not a word-pair lookup.

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive):** parser UAS ≈ 0.79 (live) / 0.842 (gold POS) — the dominant chain leak; SOTA→ours −0.083 = the representation gap; PP-attachment 0.587→0.639 with a typed grounding lexicon, monotonic, info-free (shuffled-prep) twin collapses to 0.512; the generic TOPICAL hub does NOT help (must be syntactically TYPED head+function); raw meaning vectors are collinear (cos 0.92) and need whitening; the CLASS/subcat level is the lever, not bilexical word-pairs.
- **INFERRED (you must measure):** whether a whitened, TYPED distributed selectional-preference feature added to the arc-eager attachment score lifts held-out UAS (and the meaning-sensitive relations `obl`/`nmod`/PP-attachment) CI-separated with a shuffled-meaning/scrambled-prototype info-free twin LOSING, on BOTH modern UD-EWT AND 19c LitBank (register-general — a modern-only gain that regresses 19c is a FAIL); and whether it propagates to a live board dim (who-did-what / state / space). The right feature weight (sweep).

## VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: understand ALL parser organs (`python tools/substrate_map.py`) + read IN FULL: the arc-labeler submission `add_the_arc_labeler_fast_scoring_path...` sections D-O (the whole-chain signal-loss ladder + the ranked fixes + the whiten root-cause) and `improve_the_parser_verb_argument_attachment...` (the PP-attachment 0.587→0.639 grounding result + the register-OOD warning: a modern-trained parser LOSES on 19c). Read `hdlab/arceager_parser.py`, `hdlab/arc_parser.py`, `hdlab/meaning_foundation.py`.
- Reproduce first-hand: the parser UAS on UD-EWT + 19c; the PP-attachment grounding lift; the whitening requirement.

## THE BAR (can-fail; CI-separated; the info-free twin must lose)
PASS = a whitened, syntactically-TYPED distributed selectional-preference feature in the arc-eager attachment score that lifts held-out UAS (and the meaning-sensitive `obl`/PP relations) CI-separated over the current parser, with a shuffled-meaning info-free twin LOSING, on BOTH modern AND 19c (register-general, no 19c regression), landed through the LIVE reader — and NO-regress on any board dim, ideally a CI-separated lift on one (who-did-what/state/space). Report CI half-width + null p95; recompute floors per population. A rigorous located NEGATIVE — a faithful distributed selectional feature cannot close the gap glass-box (with the exact reason, e.g. the class-typing coverage bound), is a FULL PASS.

## ALREADY TRIED / DO NOT REDO
- Do NOT re-run the located negatives: raw (un-whitened) distributed meaning ties its scrambled control; lexical/bilexical WORD-PAIR PMI HURTS (the grain is CLASS-level, not word-pair); the generic topical hub does NOT help PP-attachment (must be syntactically typed); beam/revision on the greedy model, a delexicalized parser (−8 UAS in-domain), and a modern-trained SOTA swap (loses on 19c) are all located negatives on disk.
- Do NOT re-solve parse EFFICIENCY — the double-parse CONSOLIDATION (single arc-eager) is already landed; this is ACCURACY (better heads over the same single parse).

## COORDINATION (does NOT conflict with the in-flight substrate streamlining)
SEQUENCE this AFTER the double-parse consolidation (now landed): arc-eager is the SOLE read-path parser, so target `hdlab/arceager_parser` — prototype against it in `experiments/`; strategy lands the Q111 wire after the consolidation settles. This is ACCURACY (attachment features), ORTHOGONAL to the consolidation's EFFICIENCY (which parse). Its COMPLEMENT is the ROLE side of the non-canonical wall (`grounded_meaning_role_cue_for_non_canonical...`): this problem makes the parser ATTACH `obl:agent`; that one ASSIGNS the role given the parse — cross-reference, do NOT duplicate. Uses the SAME `meaning_foundation` vectors as the meaning-wire / the role cue, but as a PARSER ATTACHMENT feature (a distinct consumer). No live-code overlap with the pass.

## FILES AND ENTRY POINTS
Prototype + measure in `experiments/` + `verification/`; the wire is `hdlab/arceager_parser.py` (the attachment score) — REUSE `hdlab/meaning_foundation.py` + the distributional channel + the whitening. Strategy lands the Q111 wire; fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b (RUNG-2 SOTA→ours representation gap).

## DO NOT QUOTE
- Do NOT quote a UAS gain without the shuffled-meaning info-free twin LOSING + BOTH-register no-regression (a modern-only gain that regresses 19c is a FAIL).
- Do NOT quote a bilexical/word-pair result — the lever is the CLASS/subcategorization level.
- NO external LLM (the invariant); the distributed reps are the substrate's own glass-box meaning vectors, whitened.
