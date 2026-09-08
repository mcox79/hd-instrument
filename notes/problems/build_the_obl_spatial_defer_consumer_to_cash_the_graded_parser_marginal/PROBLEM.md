---
priority: 5
slug: build_the_obl_spatial_defer_consumer_to_cash_the_graded_parser_marginal
status: CANDIDATE
review:
review_text:
---

# PROBLEM: the globally-normalized graded parser proved its RAW oblique-attachment marginal (AUC 0.782) BEATS the whole landed obl calibrator (0.736) and lifts obl SELECTIVE accuracy 0.758 -> 0.902 (+0.048, the biggest single parser win, 6x the patient gain) -- but there is NO live consumer that DEFERS on an unreliable oblique/locative attachment, so the win is dormant; build the brain-faithful defer consumer (the spatial/where-is reader abstains or down-weights when the obl marginal is low) and prove the live spatial/locative dimension lifts CI-separated on modern gold with the info-free twin LOSING, then flip per no-more-default-off.

**slug:** `build_the_obl_spatial_defer_consumer_to_cash_the_graded_parser_marginal` -- **opened:** 2026-09-07 by the
strategy session. The graded parser (`hdlab/graded_parser.py`, Matrix-Tree edge marginals) is landed and its obl-attachment
marginal is exposed (`parse_confidence.obl_reliability_marginal`), MEASURED net-positive, but the CONT-19 integration left
the flip "deferred to strategy" because there is no live obl consumer to cash it. This is a BUILD (a defer/abstain consumer),
REUSE of a landed marginal -- the biggest unrealized parser lever on the board.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**
>
> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** -- the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau -- it is the FIRST thing you do.
>
> **YOU ARE ENABLED -- AND EXPECTED -- TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> If a MORE brain-foundational method conflicts with this brief or the existing organs, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful).
>
> **A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several angles hit the SAME wall,
> the faithful method is probably DIFFERENT IN KIND. A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
>
> **"CONVERGED" HAS A HIGH BAR.** Claim it ONLY when you have (a) identified how the brain performs this
> computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC
> reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
>
> **THE 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`) -- RUN THIS CHECKLIST EACH FIRE AND ACT ON IT
> (owner 2026-08-28; this is how you keep pushing without being told):**
> (1) DO THE RIGHT THING, not the cheap one -- and if there is high-value ADJACENT info we can gather that raises
> fidelity OR PROVES THE POINT (a control, a distance/robustness curve, an ablation, a second gold), GO GET IT.
> (2) What is LEFT that rationally fits THIS problem? Enumerate + do it. If ADJACENT components bottleneck it, MAP
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps -- AND
> EVALUATE each for BRAIN-FOUNDATIONAL FIDELITY + OPTIMIZATION POTENTIAL (is it the brain's actual mechanism or an
> OUR-INVENTION placeholder? a higher-fidelity / higher-yield version worth building?) -- that evaluation seeds the next problem.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill -- do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across -- never a ceiling.
> Each fire: implement -> test (can-fail, strongest real floor, info-free twin LOSING) -> iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS -- but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch; inherit its PINNED/INVENTED verdicts;
> put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale or any new deviation.
>
> ## BRAIN-FOUNDATIONAL CHECKLIST (the owner's standing bar -- work through IN ORDER; the solution is not done until every box holds)
> 1. **OPEN -- how does the BRAIN do THIS?** Name the specific structure + computation and replicate that OPERATION as the FIRST move; mark each choice PINNED vs OUR-INVENTION. RESEARCH AGGRESSIVELY wherever you are unsure -- do not build the tractable thing and cite neuroscience after.
> 2. **REUSE -- does an existing organ already do what you need?** Check `tools/substrate_map.py` / `tools/reader_capabilities.py` / `hdlab/` FIRST; extend a matching organ rather than re-deriving it.
> 3. **GENERALIZE -- does this need to generalize, and HOW does the brain generalize it?** Build for that (register / novelty / transfer), not for the single test.
> 4. **HIT A WALL? GO DEEPER, DON'T STOP.** Research-drill WHY. If the brain can do it, it IS possible and we can too, once we understand it. A located NEGATIVE counts only if the brain's ACTUAL mechanism, faithfully built, is what failed (fair test: can-fail, one-variable, real baseline).
> 5. **OPTIMIZE BY EXACT REPLICATION.** Evaluate aggressively, with great precision, EXACTLY how the brain does it, and replicate it exactly -- copy the computation, SWEEP (never adopt) the parameters. No half-effort: the closer we are, the better we do.
> 6. **PERFORMANCE vs THE BRAIN.** How does our performance compare to a competent brain/reader on this task? WHERE ALONG THE CHAIN do we lose signal? What EXACTLY differs between our implementation and the brain's mechanism (an itemized mechanism-diff)?
> 7. **ADJACENT COMPONENTS.** Map the capabilities, limitations, opportunities, and brain-foundational status of the adjacent components -- that seeds the next problems to address.
> 8. **COMPLETION BAR.** Is this a COMPLETE, EXCELLENT solved problem? Is it FULLY brain-foundational, conveying ALL the benefits of the brain function we replicate? If not, keep pushing toward a fully complete, exceptional solution.
>
> **(PHASE DIAGRAM -- the substrate is not locked to one regime.)** The substrate's operating point -- store DENSITY vs SPARSITY, dimensionality, binding regime, capacity, decay/gain, indexed-vs-superposed organization -- is FREE to change at ANY time, PER ORGAN. These are parameters to SWEEP, never fixed constraints. A wall "at this configuration" is a cue to MOVE the operating point on the phase diagram BEFORE ever calling it a ceiling.
>
> **(FULL-STACK UPSTREAM -- prototype THIS component AND its upstream, to EXCEL and EXCEED.)** Fully prototype THIS component AND the upstream brain-foundational component it depends on (and ALL the way upstream if the chain is deeper), and SHOW the capability can EXCEL and EXCEED -- make it happen. Then: (a) CONFIRM no other downstream consumer of the upstream optimization REGRESSES; (b) CONFIRM whether those other consumers should be REVISITED to be more brain-foundational, now making use of the newly-optimized upstream capabilities; (c) make SURE, VIA RESEARCH, that what you implement upstream is genuinely brain-foundational. **THE ONLY WAY YOU OVERCOME THIS WALL IS FOR EVERY COMPONENT -- YOU AND UPSTREAM -- TO BE BRAIN-FOUNDATIONAL.** Any wall you encounter must be FULLY RESEARCHED: the brain does it, so we can too -- and to do so we must UNDERSTAND it fully.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When a sentence says "she put the cup on the table by the window", the reader has to attach "on the table" and "by the
window" to the right thing -- a job the parser is often unsure about. We built a parser that can now say HOW SURE it is
about each such attachment (a real confidence number, not a guess), and proved that when it's unsure and the reader BACKS
OFF instead of committing, the spatial answers get much better (from ~76 right in 100 to ~90). But nothing in the reader
currently listens to that confidence for spatial attachments. This job builds the piece that listens: the spatial reader
abstains or down-weights exactly when the parser is unsure, cashing the biggest single parser improvement we have.

## 2. WHY THIS ONE
It is the biggest MEASURED-but-unrealized parser lever (obl selective 0.758 -> 0.902, +0.048 AUC -- 6x the who-did-what
patient gain), it is REUSE of an already-landed marginal (no new parser research), and it directly serves the shared
EXTRACTION wall the reasoners bottleneck on (spatial extraction is edge-recall-bound). It also builds the brain's actual
confidence-gated commitment mechanism (retrieval/attachment under uncertainty), which the substrate wants everywhere.

## 3. HOW THE BRAIN DOES THIS
PINNED (computational-level). Sentence processing is incremental and PROBABILISTIC: PP/oblique attachment is resolved by
graded competition, and commitment is confidence-gated -- under low confidence the parser DELAYS/keeps alternatives alive
rather than committing to a wrong attachment (surprisal / good-enough processing; Hale; Levy noisy-channel; the same
speed-accuracy tradeoff McElree describes for retrieval). The graded parser's edge MARGINAL (a posterior over all trees,
Matrix-Tree) IS that confidence signal. The consumer should DEFER (abstain / down-weight the locative edge) when the
marginal is low, exactly as the brain withholds commitment under ambiguity -- NOT force a single attachment.

## 4. MEASURED vs INFERRED
- **MEASURED (CONT-19, first-hand at integration):** the RAW obl-attachment marginal AUC 0.782 BEATS the whole landed obl
  logistic calibrator 0.736; deferring the obl pick on low marginal lifts obl SELECTIVE accuracy 0.758 -> 0.902 (+0.048,
  the biggest parser win); the shuffled-marginal twin is FLAT; the marginal is additive (heads byte-identical).
- **INFERRED (this problem must MEASURE):** that a LIVE spatial/locative consumer (the where-is / RCC8 reader) built to
  defer on the low-marginal obl edges lifts the live SPATIAL dimension CI-separated on modern gold -- the selective-accuracy
  number is on the parser's own obl instrument; the end-to-end spatial reader lift through the live path is unproven and is
  the deliverable. The operating point (defer threshold on the marginal) must be tuned, not adopted.

## 5. ALREADY TRIED / DO NOT RE-RUN (the disk outranks this brief)
- **The obl marginal itself is already landed** (`parse_confidence.obl_reliability_marginal`) and the logistic calibrator was
  DROPPED in its favor -- do NOT rebuild the calibrator or re-derive the marginal; consume it.
- **Deferring the PATIENT pick (who-did-what) via the marginal: only +0.0065** and costs a second parse -- that is a DIFFERENT,
  smaller lever (default-off, filed elsewhere). This problem is the OBL/spatial consumer, the 6x-larger lever.
- **Do NOT flip `decode="exact"` as the fix here** -- that is a separate parser flip (the 8-consumer no-regress check); the obl
  marginal is available under the current default decode.
- The 2nd-best tree does NOT raise absolute patient accuracy (scorer-feature bound) -- do not chase it here.

## 6. VERIFY BEFORE YOU START
1. Understand the organs: `python tools/substrate_map.py`, skim `hdlab/graded_parser.py` (the Matrix-Tree marginals),
   `hdlab/parse_confidence.py` (`obl_reliability_marginal` -- the landed signal), `hdlab/arc_parser.py` (`ParseResult.marginals`,
   the `want_marginals` opt-in), and the live spatial/locative reader (`hdlab/` where-is / locative-PP path; `tools/reader_capabilities.py`).
2. Read IN FULL the parser SOLVED: `notes/problems/replace_the_greedy_arc_eager_with_a_globally_normalized_graded_parser_with_marginals/SOLVED.md`
   (the marginal, the obl selective 0.902 result, the flip-decision deferral) and the space SOLVED
   `.../space_where_is_is_extraction_recall_bound_add_lazy_locative_pp_bridging/SOLVED.md`.
3. Confirm on disk: the obl marginal is exposed and the spatial dimension's live floor + scorer (the board's spatial/where-is arm).

## 7. THE BAR
PASSES only with ALL of:
1. A brain-faithful DEFER/abstain consumer built on the obl marginal (the spatial/locative reader down-weights or abstains on
   low-marginal obl attachments), wired opt-in (default off, byte-identical), strategy owns the hdlab land (Q111); solver
   builds + measures in `experiments/`.
2. The LIVE spatial/locative dimension beats its CURRENT live input CI-separated on MODERN gold, doc-level paired-bootstrap CI.
3. The info-free twin (shuffled marginal, or defer on a random edge subset of equal size) LOSES CI-separated.
4. No regress on other parse consumers (who-did-what, temporal, etc.).
5. Per no-more-default-off: if net-positive, propose the flip ON with the tuned defer threshold; else state the measured reason.
A rigorous NEGATIVE is a full pass (e.g. "the live spatial reader is extraction-recall-bound upstream of attachment, so
attachment-confidence deferral cannot move it -- located, with the recall number").

## 8. FILES AND ENTRY POINTS
- The marginal: `hdlab/parse_confidence.py::obl_reliability_marginal`; `hdlab/graded_parser.py` (Matrix-Tree edge marginals); `hdlab/arc_parser.py` (`ParseResult.marginals`, `want_marginals`).
- The consumer: the live spatial/locative reader (`hdlab/` where-is / locative-PP bridging; find via `tools/reader_capabilities.py`), + `hdlab/situation_reader.py` for the wire.
- The measurement: the board's spatial/where-is arm (`experiments/exp_situation_model_qa_modern_v1.py`) + the parser's obl selective harness in the parser SOLVED's cells.
- Corpus: modern gold (GUM / the spatial modern gold used by the space SOLVED). NOT 19c (owner 2026-09-06).

## DO NOT QUOTE / DO NOT REDO
- 0.758 -> 0.902 is the parser's own obl SELECTIVE-accuracy instrument -- do NOT quote it as the live spatial-dimension number until re-measured through the live reader; that IS this problem.
- Do NOT rebuild the obl logistic calibrator (dropped) or re-derive the marginal (landed) -- consume the landed signal.
- Do NOT force a single attachment where the brain defers -- the whole point is confidence-gated abstention.

**TLDR (plain English):** Our parser can now say how confident it is about tricky "attach this phrase to that thing"
decisions, and we proved that when it holds back on the unsure ones, spatial understanding jumps a lot. But the reader
doesn't yet listen to that confidence for spatial phrases. This job builds the listener -- the spatial reader backs off
exactly when the parser is unsure -- and proves the spatial answers improve for real when the whole reader runs. It's the
biggest unused parser improvement we have, and it teaches the substrate the brain's "don't commit when unsure" habit.

**QUESTIONS:** none blocking. One scope note: if the live spatial reader turns out to be limited by how many spatial
relations it EXTRACTS (recall) rather than how it ATTACHES them, the honest finding is that attachment-confidence can't move
it and the recall extractor is the real lever -- report that with the number (it seeds the spatial-extraction problem, pri 2).

**NEXT STEPS:** run VERIFY BEFORE YOU START; build the defer consumer + measure the live spatial lift + twin + no-regress in
`experiments/`; sweep the defer threshold; propose the flip. Strategy lands the hdlab edit and, if net-positive, flips it on with a board arm.
