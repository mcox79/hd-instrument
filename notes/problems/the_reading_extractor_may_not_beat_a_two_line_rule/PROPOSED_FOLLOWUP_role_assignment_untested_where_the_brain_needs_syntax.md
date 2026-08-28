> ## ⚠️ UPDATE (solver, after pushing brain-foundational): THE "IS IT THE CEILING?" QUESTION IS NOW ANSWERED IN SOLVED.md.
> I DID test the brain-hard regime (SOLVED.md Sections 2-3): on reversible object-relatives/clefts the
> two-line rule collapses (0.001 synthetic / 0.080 real, below random) and the brain's FILLER-GAP
> mechanism recovers it (oracle 1.000; real parser +0.21 CI-separated). So the two-line rule is NOT the
> ceiling. **The residual open problem is NARROWER than this brief: BUILD A STRONGER RELATIVE-CLAUSE /
> FILLER-GAP PARSER (+ a construction gate).** The measured ceiling is oracle-parse 1.000 vs real-parse
> ~0.25; the arc parser (UAS 0.79) mis-resolves the antecedent, and an ungated filler-gap arm is
> net-negative overall (-0.107) from canonical false-positives. Re-title the filing accordingly, e.g.
> `the_relcl_parser_is_too_weak_for_filler_gap_role_assignment`. The section below is kept for the
> framing/citations; its BAR is superseded by the parser-build bar.

---

# PROPOSED FOLLOW-UP BRIEF (packaged by the solver; ranking + filing is the strategy session's to do)

**Why this lives here and not in a new numbered folder:** the concurrent strategy session is actively
re-ranking the problems tab (git log `bdb6a9041` "re-rank open queue", `881fede9a` filed the parent of
this very problem). Priority is cert-enforced-unique (`verification/test_problem_briefs_and_flags.py`),
so injecting a new priority mid-re-rank is the lost-update hazard the protocol forbids. This is the
complete brief, ready to lift into `notes/problems/<slug>/PROBLEM.md` with a priority when strategy
chooses. **Suggested slug:** `role_assignment_untested_where_the_brain_needs_syntax`.

**It exists because the REPLACE verdict I just filed has an honest hole**, and I would flag this hole on
anyone else's submission: I proved a *weak* elaborate reader loses to a two-line rule **on a benchmark
that barely contains the brain's hard case**, and where it does (n=609), *every* arm scores ~0.55-0.60.
"Two-line beats elaborate" is enough to retire the current machinery; it is NOT "the brain's real
computation is unnecessary." Those are different claims.

---

```
---
priority:            # STRATEGY TO SET (concurrent re-rank in progress; do not collide)
review:
review_text:
---
```

## 1. THE PROBLEM IN PLAIN LANGUAGE

We just showed the elaborate "who did what to whom" reader loses to a dumb two-line rule (use word
order; flip it for "was X-ed"). But almost every sentence in that test was easy -- the answer sits
right where word order puts it. The sentences that are hard *for a reason* -- where both things named
could plausibly have done the action AND the grammar is twisted ("the miner that the rock crushed",
"it was the acid that dissolved the metal"), the exact sentences the brain switches on its effortful
parser for -- were **~600 out of 17,000**, and on those **nothing we tried worked** (two-line 0.60,
elaborate 0.54, precise 0.57, all barely above a coin-flip-among-nouns). So we retired the elaborate
reader on the strength of the easy cases and never actually tested the case it was supposed to be for.
Build a test that contains those hard sentences at real power, and find out whether ANY mechanism --
especially a brain-faithful incremental parser -- beats the two-line rule there, or whether the
two-line rule is genuinely the ceiling for this pipeline stage.

## 2. WHY THIS ONE

It puts a real floor under the REPLACE decision. Two outcomes, both valuable:
- **If nothing beats the two-line rule even on the hard regime** -> the two-line rule is the ceiling
  for stage-1 role assignment; stop investing here, redirect to stage 2 (meaning) with confidence
  rather than on the strength of easy sentences only.
- **If a brain-faithful parser DOES beat it on reversible non-canonical items** -> that is what the
  elaborate reader *should* have been (a real syntactic parse, not an animacy-leaning perceptron), and
  it is a capability the situation-model pipeline needs for exactly the sentences plausibility can't
  rescue. Either way the "replace it" call stops resting on an untested regime.

## 3. HOW THE BRAIN DOES THIS (frame)

Canonical (active SVO) role assignment runs on a fast ventral/heuristic route (Bever's NVN; the
two-line rule copies it, PINNED). Non-canonical, **semantically reversible** constructions -- reversible
passives, object-relative clauses, object-clefts, reversible datives -- recruit the **dorsal stream:
posterior Broca's BA44 + the arcuate fasciculus** (Friederici 2011/2017; Grodzinsky & Santi 2008),
which processes syntactic movement / filler-gap dependencies. Agrammatic damage there drops
comprehension of reversible non-canonical sentences to chance (Caramazza & Zurif 1976; Grodzinsky's
Trace-Deletion Hypothesis 2000). **PINNED:** reversibility is what forces syntax; word order + voice is
the only cue on reversible passives, and a *structural parse* is the only cue on object-relatives/clefts
(where even voice does not help). **OUR-INVENTION-UNDER-TEST:** whatever parser is built to copy that
movement/filler-gap computation. The brief's job is to test the brain's OPERATION (effortful incremental
parse on reversible non-canonical clauses), not another positional heuristic.

## 4. MEASURED vs INFERRED

MEASURED (`the_reading_extractor_may_not_beat_a_two_line_rule`, SOLVED): on QA-SRL v2 patient selection
n=17,330, elaborate 0.751 loses to two-line 0.766 (CI-sep); precise-voice two-line 0.795 wins overall.
On the `noncanon_AND_reversible` cell **n=609**: TWO_LINE 0.601, PRECISE 0.571, ELABORATE 0.542,
POSITIONAL 0.000, TWIN 0.291 -- every arm near floor, and the cell is under-powered. The reversible
stratum overall (n=1,897) is dominated by *canonical* actives with two animate nouns (positional
scores 0.86 there), so it does NOT isolate the brain's hard case.
INFERRED (open): whether a brain-faithful incremental syntactic parser (filler-gap/movement) beats the
two-line rule CI-separated on a POWERED set of genuinely reversible non-canonical items.

## 5. ALREADY TRIED (do not re-run)

- The QA-SRL power comparison itself (this solver's cell) -- elaborate perceptron loses; precise-voice
  wins overall; ALL arms tie near 0.55-0.60 on the hard cell. Do NOT re-run the aggregate comparison.
- The averaged-perceptron cue-integration (`thematic_role_labeler`) -- animacy-leaning, loses. A new
  positional variant is not the ask; a real PARSE is.
- Query `experiment_index.py query "relcl"`, `query "reversible"`, `query "parser"`, `query "movement"`
  and check `exp_arg_adjunct_role_eligibility_categorial_break050_v1` (HARD_PASS_STRUCTURAL) and the
  arc_parser before building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Read `notes/problems/the_reading_extractor_may_not_beat_a_two_line_rule/SOLVED.md` + its
  `data/exp_reader_vs_twoline_qasrl_power_v1/metrics.json`; confirm the n=609 hard-cell numbers.
- Count how many QA-SRL items are genuine object-relative / object-cleft / reversible-dative -- if it is
  a few hundred, QA-SRL alone cannot power this and a constructed or supplemented set is required (the
  brief's "controlled-proxy" clause). Verify before assuming.
- Confirm the repo's `hdlab/arc_parser.py` (UAS ~0.79) can or cannot resolve object-relative gaps; a
  UAS-0.79 parser may itself be the bottleneck, which would be a *component-missing* result, not a
  ceiling.

## 7. THE BAR

On a POWERED, held-out set (n well above 609) of genuinely **reversible non-canonical** role-assignment
items (both arguments animate AND the patient is not in the canonical post-verb slot: object-relatives,
object-clefts, reversible passives), floor recomputed on that population = the precise-voice two-line
rule: a brain-faithful mechanism (an incremental syntactic parse resolving the filler-gap / movement)
must beat the two-line rule CI-separated over its upper bound, info-free twin LOSING. HOW WE WOULD KNOW
IT FAILED, AND THIS IS A FULL PASS: nothing beats the two-line rule on the hard regime either -> the
two-line rule is the ceiling for stage-1 role assignment and the REPLACE decision is complete; stop
investing here and redirect to stage 2.

## 8. FILES AND ENTRY POINTS

- `experiments/exp_reader_vs_twoline_qasrl_power_v1.py` -- the harness, strata, arms, bootstrap to reuse.
- `data/exp_reader_vs_twoline_qasrl_power_v1/metrics.json` + `_detail_sample.json` -- the hard-cell
  numbers and per-item picks.
- `hdlab/arc_parser.py`, `hdlab/candidate_generator.py` (relcl_gap rule already exists) -- the parse to
  build the filler-gap resolver on. Prove in `experiments/` + `verification/`; propose any hdlab change
  in SOLVED.md (strategy lands it, Q111). Do NOT write `hdlab/`.

## DO NOT QUOTE / DO NOT REDO

- Do NOT quote "the two-line rule beats the elaborate reader" as "the brain's syntactic parsing is
  unnecessary" -- that is shown only on the canonical-heavy regime; the reversible non-canonical regime
  is untested at power.
- Do NOT re-run the aggregate QA-SRL comparison; the open question is the HARD regime, at power.
