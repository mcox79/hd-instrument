---
priority: 4
review:
review_text:
---

# PROBLEM: the REPLACE verdict was proven on easy sentences -- the brain's hard regime (reversible non-canonical / filler-gap) is untested at power, and the parser that would handle it is too weak

**slug:** `the_relcl_parser_is_too_weak_for_filler_gap_role_assignment` - **opened:** 2026-08-25 by the strategy session (packaged from the `the_reading_extractor` solver's proposed follow-up)
**status:** OPEN - **evidence is first-hand in `the_reading_extractor` SOLVED.md, re-verified**

> **PRIORITY NOTE:** filed at `5` (stage-1 role assignment sits below the meaning/goal-bearing lines). But it
> is the honest hole under a REPLACE decision we already acted on, and it is a clean COMPONENT-MISSING result
> (oracle-parse 1.000 vs real-parse ~0.25 -> the parser is the bottleneck, not a ceiling). Re-rank if you judge
> closing that hole higher.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

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

## 1. THE PROBLEM IN PLAIN LANGUAGE

We just showed the elaborate "who did what to whom" reader loses to a dumb two-line rule (use word order;
flip it for "was X-ed"), and replaced it. But almost every sentence in that test was EASY -- the answer sits
right where word order puts it. The sentences that are hard *for a reason* -- where both things named could
plausibly have done the action AND the grammar is twisted ("the miner that the rock crushed", "it was the
acid that dissolved the metal"), the exact sentences the brain switches on its effortful parser for -- were
only **~600 out of 17,000**, and on those **nothing we tried worked** (two-line 0.60, elaborate 0.54, precise
0.57 -- all barely above a coin-flip-among-nouns). So we retired the elaborate reader on the strength of the
easy cases and never actually tested the case it was supposed to be for. Build a test that contains those hard
sentences at real power, and find out whether a brain-faithful incremental PARSER beats the two-line rule
there -- or whether the two-line rule is genuinely the ceiling for this pipeline stage.

## 2. WHY THIS ONE

It puts a real floor under the REPLACE decision we already made. Two outcomes, both valuable:
- **If nothing beats the two-line rule even on the hard regime** -> the two-line rule is the ceiling for
  stage-1 role assignment; stop investing here and redirect to stage 2 (meaning) with confidence, not on the
  strength of easy sentences only.
- **If a brain-faithful parser DOES beat it on reversible non-canonical items** -> that is what the elaborate
  reader *should* have been (a real syntactic parse, not an animacy-leaning perceptron), and the situation-model
  pipeline needs it for exactly the sentences plausibility cannot rescue.
The strong hint it is the SECOND: an ORACLE parse scores `1.000` on constructed reversibles while the real
`arc_parser` (UAS ~0.79) scores ~`0.25` -- a COMPONENT-MISSING result (the parser mis-resolves the antecedent),
not a ceiling.

## 3. HOW THE BRAIN DOES THIS (frame)

Canonical (active SVO) role assignment runs on a fast ventral/heuristic route (Bever's NVN; the two-line rule
copies it -- PINNED). Non-canonical, **semantically reversible** constructions -- reversible passives,
object-relative clauses, object-clefts, reversible datives -- recruit the **dorsal stream: posterior Broca's
BA44 + the arcuate fasciculus** (Friederici 2011/2017; Grodzinsky & Santi 2008), which processes syntactic
movement / filler-gap dependencies. Agrammatic damage there drops comprehension of reversible non-canonical
sentences to chance (Caramazza & Zurif 1976; Grodzinsky's Trace-Deletion Hypothesis 2000).
**PINNED:** reversibility is what forces syntax -- word order + voice is the only cue on reversible passives,
and a *structural parse* is the only cue on object-relatives/clefts (where even voice does not help).
**OUR-INVENTION-UNDER-TEST:** whatever parser is built to COPY that movement/filler-gap computation. Copy the
brain's OPERATION (effortful incremental parse resolving the filler-gap on reversible non-canonical clauses),
not another positional heuristic.

## 4. MEASURED vs INFERRED

MEASURED (`the_reading_extractor_may_not_beat_a_two_line_rule`, SOLVED, re-verified): on QA-SRL v2 patient
selection n=17,330, elaborate 0.751 loses to two-line 0.766 (CI-sep); precise-voice two-line 0.795 wins
overall. On the `noncanon_AND_reversible` cell **n=609**: TWO_LINE 0.601, PRECISE 0.571, ELABORATE 0.542,
POSITIONAL 0.000, TWIN 0.291 -- every arm near floor, cell under-powered. On constructed reversibles: the
FILLER-GAP mechanism with an ORACLE parse scores 1.000; with the real arc parser ~0.25 (net-negative overall
from canonical false-positives). The reversible stratum overall (n=1,897) is dominated by *canonical* actives
with two animate nouns (positional scores 0.86 there), so it does NOT isolate the brain's hard case.
INFERRED (open): whether a STRONGER brain-faithful incremental parser (filler-gap/movement) + a construction
gate beats the two-line rule CI-separated on a POWERED set of genuinely reversible non-canonical items.

## 5. ALREADY TRIED (do not re-run)

- The QA-SRL power comparison itself -- elaborate loses; precise-voice wins overall; ALL arms tie near
  0.55-0.60 on the hard cell. Do NOT re-run the aggregate comparison.
- The averaged-perceptron cue-integration (`thematic_role_labeler`) -- animacy-leaning, loses. A new positional
  variant is NOT the ask; a real PARSE is.
- An UNGATED filler-gap arm -- net-negative overall (canonical false-positives) -> the gate is required.
- Query `experiment_index.py query "relcl"`, `query "reversible"`, `query "parser"`, `query "movement"`; check
  `exp_arg_adjunct_role_eligibility_categorial_break050_v1` and `hdlab/arc_parser.py` before building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Read `notes/problems/the_reading_extractor_may_not_beat_a_two_line_rule/SOLVED.md` (Sections 2-3) +
  `data/exp_reader_vs_twoline_qasrl_power_v1/metrics.json`; confirm the n=609 hard-cell numbers and the
  oracle-1.000-vs-real-0.25 gap.
- Count how many QA-SRL items are genuine object-relative / object-cleft / reversible-dative. If it is a few
  hundred, QA-SRL alone cannot power this -> a constructed or supplemented reversible set is required (verify,
  do not assume).
- Confirm whether `hdlab/arc_parser.py` (UAS ~0.79) can resolve object-relative gaps at all -- a UAS-0.79
  parser may itself be the bottleneck (a component-missing result, not a ceiling). `hdlab/candidate_generator.py`
  has a `relcl_gap` rule already.

## 7. THE BAR

On a POWERED, held-out set (n well above 609) of genuinely **reversible non-canonical** role-assignment items
(both arguments animate AND the patient NOT in the canonical post-verb slot: object-relatives, object-clefts,
reversible passives), floor recomputed on that population = the precise-voice two-line rule: a brain-faithful
mechanism (an incremental syntactic parse resolving the filler-gap / movement, with a construction gate so it
does not fire on canonical clauses) must beat the two-line rule CI-separated over its UPPER bound, info-free
twin LOSING. The ORACLE-parse ceiling (1.000) shows the target is reachable; the deliverable is a REAL parser
that closes the oracle-vs-real gap on the hard regime.
HOW WE WOULD KNOW IT FAILED, AND THIS IS A FULL PASS: nothing beats the two-line rule on the hard regime even
with a strong parser -> the two-line rule is the ceiling for stage-1 role assignment, the REPLACE decision is
complete, stop investing here and redirect to stage 2.

## 8. FILES AND ENTRY POINTS

- `experiments/exp_reader_vs_twoline_qasrl_power_v1.py` -- the harness, strata, arms, bootstrap to reuse.
- `data/exp_reader_vs_twoline_qasrl_power_v1/metrics.json` + `_detail_sample.json` -- the hard-cell numbers and
  per-item picks.
- `hdlab/arc_parser.py`, `hdlab/candidate_generator.py` (`relcl_gap` rule already exists) -- the parse to build
  the filler-gap resolver on. Prove in `experiments/` + `verification/`; propose any hdlab change in `SOLVED.md`
  (strategy lands it, Q111). Do NOT write `hdlab/`.

## DO NOT QUOTE / DO NOT REDO

- Do NOT quote "the two-line rule beats the elaborate reader" as "the brain's syntactic parsing is unnecessary"
  -- that is shown only on the canonical-heavy regime; the reversible non-canonical regime is untested at power.
- Do NOT re-run the aggregate QA-SRL comparison; the open question is the HARD regime, at power, with a stronger parser.
