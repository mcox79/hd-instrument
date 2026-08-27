---
priority: 1
review:
review_text:
---

# PROBLEM: the reader finds a sentence's arguments with a BATCH dependency parser (parse the whole sentence, then read off structure) -- but the brain builds structure INCREMENTALLY and PREDICTIVELY, word by word, revising as it goes

**slug:** `the_argument_parser_is_batch_where_the_brain_is_incremental` - **opened:** 2026-08-27 by the strategy session
(the #1 remaining front-end fidelity gap the just-integrated `the_live_front_end_mislabels_who_did_what_to_whom`
proximity audit named: "the batch UD dependency parser vs the brain's incremental/predictive structure-building --
the highest-value front-end fidelity target").
**status:** OPEN - **the highest-value remaining front-end fidelity gap; the role ASSIGNER is converged, but the structure it runs on is a batch statistical parse the brain does not compute.**

> **PRIORITY NOTE (the call is the strategy session's):** filed at `1`. The front-end ROLE ASSIGNER converged
> (word-order-dominant cue competition, integrated). The remaining front-end fidelity gap is one level DOWN: the
> candidate-argument generator is a batch UD-EWT dependency parser, and "feed-forward where the brain is predictive"
> is the substrate's biggest architecture deviation (the predictive-reader session established it for semantics; this
> is its structural counterpart). It composes the already-integrated predictive reader (surprisal = the revision
> signal) + the relcl filler-gap resolver (the one place word order genuinely fails). Re-rank if the owner's
> next-steps direction supersedes.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant,
> and do not silently proceed without the denied step.**

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** -- the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau -- it is the FIRST thing you do. If you have
> not identified the brain's mechanism and attempted to build it, you have not started the real work,
> whatever else you have measured.
>
> **🚀 YOU ARE ENABLED -- AND EXPECTED -- TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> You are NOT boxed in -- not by this brief, not by the existing organs, not by the integration points you
> would tie into: if a MORE brain-foundational method conflicts with any of them, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful). Exploring
> the brain's true method is the work we most want from you; a bold, well-argued brain-faithful direction --
> even unfinished -- beats a tidy engineering result that never asked the question.
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several of your angles hit the
> SAME wall, that is strong evidence that NONE of them was the brain's mechanism -- the faithful method is
> probably DIFFERENT IN KIND, not another variation of what you already tried. A wall is a FIDELITY GAP TO
> BUILD ACROSS, never a ceiling. Hitting one is exactly the moment to LEAVE the family of methods you were
> sweeping and ask the biology again.
>
> **⛔ "CONVERGED" HAS A HIGH BAR, AND EXHAUSTING ENGINEERING VARIATIONS DOES NOT MEET IT.** Claim
> convergence ONLY when you have (a) identified how the brain actually performs this computation AND (b)
> replicated that operation as faithfully as you can and tested it, OR shown with a SPECIFIC reason why it
> cannot be replicated here. "I tried several combining / gating / scoring angles and they all plateaued at
> the same wall" is NOT converged -- it is tuning-limited, and it means the brain's mechanism is still
> UN-TRIED. That is a reason to explore harder, not to submit.
>
> **🔁 THE 30-MIN DEEPENING IS HOW YOU FORCE THIS -- IT IS NOT OPTIONAL BUSYWORK.** Run your own cron
> (`CronCreate "13,43 * * * *"`); each fire asks "how does the brain REALLY do this, one level deeper than
> my current mechanism?" -> implement -> test (can-fail, strongest real floor, info-free twin LOSING) ->
> iterate. Its whole purpose is to make you ask the brain question several more times than your own sense of
> "done" would. CANCEL it (`CronDelete`) and submit ONLY when the brain-mechanism bar above is met.
> Declining it because "my angles converged" is precisely the case it exists to catch.
>
> **A rigorous negative is a PASS -- but only if what failed was the brain's actual mechanism, faithfully
> built.** A negative on a family of convenient engineering methods is not a negative on the capability; it
> is a report that you have not yet found how the brain does it.
>
> **📖 REFERENCE THE BRAIN-FOUNDATIONAL AUDIT, AND HELP KEEP IT TRUE.** Before you start, read the entry for the
> system you are touching in `notes/BRAIN_FOUNDATIONAL_AUDIT.md` -- it gives the brain structure, whether the
> brain's equation is PINNED or something we are INVENTING, our current fidelity, and the known deviation, so you
> inherit that instead of re-deriving it. If your work shows a verdict there is WRONG, STALE, or INCOMPLETE, or you
> find a NEW deviation, put a short **AUDIT UPDATE** note in your submission -- the strategy session folds it into
> the audit at integration. The audit is a living, shared map and you help maintain it.

## 1. THE PROBLEM IN PLAIN LANGUAGE

To work out a sentence's structure -- which words are the arguments of which verb -- our reader runs a standard
computational-linguistics parser: it takes the WHOLE sentence and computes a full dependency tree, then reads the
arguments off it. The brain does not do this. You understand a sentence AS YOU READ IT, one word at a time: you build
a provisional structure, predict what is coming, and REVISE when a later word surprises you (that is why garden-path
sentences -- "the horse raced past the barn fell" -- briefly trip you up). Our batch parser has no notion of this: no
prediction, no left-to-right commitment, no revision. It is the "reacts instead of predicts" gap we already found in
the meaning system, now at the level of STRUCTURE.

This problem builds the brain's version: an INCREMENTAL, PREDICTIVE, left-to-right structure-builder that proposes the
verb's arguments as it reads, and test whether it supplies BETTER arguments to the (already-converged) role assigner
than the batch parser does -- especially on the sentences where incrementality matters.

## 2. WHY THIS ONE

- **It is the biggest remaining front-end fidelity gap.** The front-end role ASSIGNER is converged (word-order cue
  competition, integrated); the structure it runs on is the batch UD parser. The proximity audit ranked this the
  highest-value front-end target.
- **It composes what we just built.** The predictive reader supplies the SURPRISAL that should trigger revision; the
  relcl filler-gap resolver handles the object-relative cases where word order alone fails. This build ties them into
  the structural front-end.
- **The batch parser is measurably harmful in the exact place structure matters.** For filler-gap / reversible
  relatives the general arc parser scored BELOW an info-free twin (the relcl SOLVED); naive all-candidate wiring
  over-generates (9.96 candidates/clause). An incremental builder that commits + revises is the faithful fix.

## 3. HOW THE BRAIN DOES THIS (frame + discipline)

**PINNED:** sentence comprehension builds structure INCREMENTALLY, word-by-word, left-to-right, with PREDICTION and
bounded REVISION -- NOT a batch parse of the whole string. Evidence: anticipatory structure-building + garden-path
revision (Frazier & Rayner; the active-filler strategy, already built in relcl); GOOD-ENOUGH / underspecified parsing
(Ferreira 2003); the Now-or-Never bottleneck -- the brain must chunk-and-pass immediately because memory for the raw
input decays (Christiansen & Chater 2016); surprisal as the incremental processing-difficulty / revision signal
(Hale 2001; Levy 2008 noisy-channel). Neural: left-to-right predictive structure-building over temporal/inferior-frontal
cortex (eADM, Bornkessel-Schlesewsky; IFG/pSTS).

**OUR-INVENTION-UNDER-TEST (mark each; sweep don't adopt):** HOW to build incremental structure over our reps (an
incremental shift-reduce / left-corner parser? attachment-by-prediction? a chunk-and-pass buffer?); the REVISION trigger
(surprisal from the predictive reader? a garden-path reanalysis?); the granularity of "good-enough" (how underspecified
is acceptable). COPY the OPERATION (incremental, predictive, revisable argument-structure building); SWEEP the params.
Do NOT reproduce a Universal-Dependencies tree -- that is the convenient tool, not the brain's representation.

**Corpus-age note (MIND IT):** test on modern prose (QA-SRL) where the batch parser is trained, AND on
garden-path/reversible constructions; hold corpus era fixed across arms.

## 4. MEASURED vs INFERRED

**MEASURED (integrated this session):** `hdlab/candidate_generator.py` is a batch UD-EWT-trained statistical POS tagger
+ arc parser (the proximity audit, `the_live_front_end...`). For filler-gap / reversible role assignment the general arc
parser is MEASURABLY HARMFUL (below an info-free twin -- the relcl SOLVED); naive all-candidate wiring over-generates
(9.96 candidates/clause, `the_live_front_end...`). The predictive reader supplies a validated per-word SURPRISAL signal
(landed `hdlab/predictive_reader.py`); the relcl filler-gap resolver handles reversible relatives (integrated).

**INFERRED / OPEN (this problem, decisive either way):**
- Whether an INCREMENTAL, PREDICTIVE, left-to-right structure-builder (with surprisal-triggered revision) supplies
  BETTER candidate arguments to the converged role assigner than the batch UD parse -- on real reading, and especially
  on garden-path / reversible constructions where incrementality is the point.
- Whether "good-enough"/underspecified incremental structure suffices for role assignment (vs a full parse).

## 5. ALREADY TRIED / DO NOT RE-RUN

- Do NOT reproduce a Universal-Dependencies dependency tree -- that is the batch convenience being replaced; the brain's
  representation is incremental provisional structure, not a UD graph.
- Do NOT rebuild the role ASSIGNER -- it is converged and integrated (word-order-dominant cue competition); this is the
  STRUCTURE that feeds it.
- Compose, do NOT duplicate: the predictive reader (`hdlab/predictive_reader.py`, surprisal = the revision signal), the
  relcl filler-gap resolver (reversible relatives), the N400 monitor (event boundaries).
- Query `experiment_index.py query "incremental"`, `query "parser"`, `query "garden"`, `query "surprisal"`, and read
  `hdlab/candidate_generator.py` + the relcl + predictive-reader SOLVEDs BEFORE building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Read `hdlab/candidate_generator.py` (the batch parser to beat) and where the live reader calls it; confirm how to
  swap in an incremental builder behind a flag (identical downstream, only the argument-source changes).
- Reproduce the batch parser's candidate-argument quality (over-generation rate; filler-gap harm) so you trust the
  baseline you are beating.
- Pick a population with garden-path / reversible / non-canonical structure (where incrementality matters) AND a modern
  general slice; recompute every floor on each.

## 7. THE BAR

Build an incremental, predictive, revisable structure-builder and feed its candidate arguments to the converged role
assigner. On a real reading population, floors recomputed on it:

- **The incremental builder must beat the BATCH UD parser (`candidate_generator`) at candidate-argument identification /
  downstream role assignment, CI-separated over its UPPER bound, with an info-free twin (shuffled attachment / random
  revision) LOSING CI-separated.** Report CI half-width + null p95. Attribute the gain to INCREMENTALITY (ablate the
  revision / prediction). Test where it should matter (garden-path, reversible relatives) AND on a general slice.
- **DECISIVE EITHER WAY:**
  - The incremental builder beats the batch parse -> the structural front-end should be incremental/predictive; propose
    the hdlab wiring (strategy lands it), composing the predictive reader (surprisal) + relcl.
  - A faithfully-built incremental parser does NOT beat the batch parse on argument identification -> a rigorous negative
    (the batch parse is an adequate stand-in for THIS job at this scale), with the residual localized (e.g. only the
    garden-path/reversible tail needs it) -- as valuable as the win. State the incremental mechanism you built and why
    it is the brain's.

## 8. FILES AND ENTRY POINTS

- `hdlab/candidate_generator.py` (the batch UD parser to replace), the live reader's call site
  (`hdlab/situation_reader.py` / `reading_grounding_loop.py`), `hdlab/predictive_reader.py` (surprisal = revision
  signal), the relcl filler-gap resolver (from `the_relcl_parser...` SOLVED), `hdlab/n400_coherence_monitor.py`.
- Prove in `experiments/` + `verification/`; propose the hdlab WIRING diff in `SOLVED.md` (strategy lands it, Q111).
  **Do NOT write `hdlab/`.**

## DO NOT QUOTE / DO NOT REDO

- Do NOT rebuild the role assigner (converged) or reproduce a UD tree (the batch convenience being replaced).
- Do NOT score only on canonical prose -- test where incrementality matters (garden-path / reversible), hold era fixed.
- No number crosses populations/scorers -- recompute every floor on the live population.
