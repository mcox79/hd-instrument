---
problem: eval_bank_too_small
status: SOLVED
bar: (1) >=120 scorable items (~3x the current 36); (2) text_length_chars AND the negation counter sit at their OWN permutation nulls via tools/floor_battery.py, not merely below the majority floor; (3) gold fixed by textual entailment BEFORE any organ output is consulted, and the scored population saved; (4) fairness reported honestly incl. how many items defeat all four positional baselines simultaneously.
result: experiments/data/goal_bearing_modern_eval_v2.jsonl = 166 items, 124 scorable (outcome_in_lexicon False), 3.4x the current 36. Scorer tools/floor_battery.py on the 124 scorable (n=124, majority floor 0.605 "always UNMET"): text_length_chars 0.613 vs its own null p95 0.653 (clears_own_null FALSE); negation_cue_last_sentence 0.613 vs 0.637 (FALSE); negation_cue_whole_text 0.613 vs 0.629 (FALSE); text_length_words 0.613 vs 0.653 (FALSE) -- BOTH documented cheats are DEAD. Same result on the full 166 (all_watched_at_their_null True). For contrast the two cheats were reproduced on v1's 36 first: text_length_chars 0.8056 and negation_cue_last_sentence 0.8056.
floor: strongest trivial baseline that still CLEARS its own null on the scored subset = NONE of the length/negation cheat family (the family that scored 0.8056 on v1); the majority floor is 0.605. Diff-in-means permutation (stricter than floor_battery's fitted threshold): length p=0.988, negation-in-last p=0.844 -- both features independent of the label.
controls: (a) floor_battery full 12-baseline battery run on BOTH the 124 scorable and the full 166; (b) verbatim-substring gate against the cited source, dropped 3 items (coverage<0.80/0.65) -- kills hallucinated/paraphrased gold; (c) roster structural gate, dropped 9 (goal-owner token absent from trimmed text); (d) source-overlap dedup, dropped 13; (e) length+negation diff-in-means permutation nulls; (f) positional-baseline fairness floors (recency 0.657 / first_mention 0.759 / nearest_subject 0.355 / majority 0.699 on the full bank), with 9/166 (7/124) items defeating all four simultaneously. Every control reports how many items it removed.
files_changed: experiments/data/goal_bearing_modern_eval_v2.jsonl, experiments/data/goal_bearing_modern_eval_v2_baselines.json, experiments/goal_bearing_eval_v2_miner.py, experiments/goal_bearing_eval_v2_shortlist.py, experiments/goal_bearing_eval_v2_assemble.py, experiments/goal_bearing_eval_v2_seed_v1.py, experiments/goal_bearing_eval_v2_finalize.py, verification/goal_bearing_eval_v2_gates.py
reverify: cd d:/AI/hd-instrument && .venv/Scripts/python.exe experiments/goal_bearing_eval_v2_finalize.py
---

## What was built

A new goal-outcome eval bank, `goal_bearing_modern_eval_v2.jsonl` (**166 items, 124 scorable**),
constructed so the two documented cheats do not work on it, with gold fixed by textual entailment
before any organ output was consulted.

- **Pipeline (all in `experiments/` + `verification/`, reproducible):** deterministic verbatim miner
  over the corpora -> stratified shortlist -> parallel Opus annotation (entailment-only, organ
  forbidden) -> machine gates (verbatim substring, roster, dedup) -> matched-stratum curation +
  greedy diff-in-means prune -> fairness baselines. The bank text is guaranteed real: a
  verbatim-substring gate re-checks every item against its cited source and drops anything an
  annotator paraphrased or hallucinated (3 dropped).
- **Sources:** Little Women, Anne of Green Gables, Tom Sawyer, Wizard of Oz, **Sherlock Holmes**
  (added as a fresh high-yield third-person narrative source), plus the 28 surviving items of the
  original v1 bank (independently gold-fixed in the 2026-08-06 four-surveyor build, so
  non-contaminating). Alice in Wonderland excluded per the brief.
- **The anti-cheat design (the real difficulty):** both cheats are the same fact -- failures get
  narrated tersely and with negation, successes at length and affirmatively. The fix was to
  over-source the two rare quadrants (**success worded with a negative**; **failure worded
  affirmatively/at length**) and then curate so length and negation are statistically independent of
  the label. On v1 the negation rate was 0.04 (met) vs 0.54 (unmet); on v2 it is 0.41 vs 0.45, and
  the length distributions are indistinguishable (permutation p=0.988).
- **Competency structure (brain-anchored design):** trap_type is recorded per item -- 94 natural,
  45 recency_trap, 27 distractor_between -- so the bank can be scored as a diagnostic of the
  sub-competencies a reader actually uses (finding the goal-owner under a recency distractor, etc.),
  not just a flat pass/fail. Difficulty: 31 easy / 100 medium / 35 hard.

## What was measured

- **Both cheats dead**, on the scored subset AND the full bank (floor_battery), and under the
  stricter diff-in-means permutation test. This is the headline the original bank never achieved.
- **Fairness, reported honestly as the original did:** first_mention (0.759) and majority (0.699)
  stay high because in narrative prose the goal-owner is usually also the protagonist (introduced
  first, named most) -- a structural property of the text, not a construction bug, identical in
  character to v1's finding. nearest_subject sits low (0.355). **9 items defeat all four positional
  baselines simultaneously** (v1 had 5), the unambiguous-capability subset.
- **Population saved:** `scored_population_ids` (all 124) is written into the baselines file, so any
  future re-score is free.

## Brain-faithfulness (the honest framing)

This deliverable is an **instrument, not a brain mechanism**, and deliberately so -- a test built out
of the mechanism it grades is worthless (contamination). Its brain-anchoring is in *what* it tests:
it forces the scored system onto the situation-model route (represent the goal, integrate the events,
judge congruence) by making the surface shortcuts -- length, negation, position -- uninformative.
The owner explicitly authorized carrying this through to the brain-foundational MECHANISM as a full
solution (see `OWNER_AUTH.md`); that is Phase B, gated on this bank being frozen first.

## What was NOT established

- **The two cheats are gone, but the bank is not "fully fair."** Like v1, positional priors
  (first_mention/majority) remain strong on the full set; only 9/166 defeat all four. A capability
  claim on this bank should headline the 9-item all-fair subset and the trap subsets, not the full
  number (brief failure-mode (c): a fully-fair-by-construction bank risks not resembling real prose;
  I did not force that trade-off, I reported it).
- **Class balance skewed to UNMET (101/65).** Killing the length cheat required dropping
  preferentially long (MET) items, leaving a 0.605 UNMET majority floor. Reported, not hidden; v1 was
  the mirror image (0.64 MET).
- **I did not run the goal-typing organ against this bank.** By construction (contamination rule):
  gold was fixed by entailment only. The single-word `verb_lexical_similarity.in_lexicon` check (to
  define the scored subset) and the positional-OWNER resolver (fairness floors) are lexicon
  membership / structural floors, NOT the outcome-valence organ's per-item predictions.

## What I would withdraw first if wrong

The gold labels on the ~10 hardest items flagged `difficulty: hard` by annotators (cross-entity
recency traps, inferential outcomes). They were fixed by single-annotator entailment with a written
justification and passed the machine gates, but were not double-annotated. If any v2 result turned
surprising, re-adjudicating those first is the cheapest check. (The cheat-defeat and fairness numbers
do not depend on any single item -- they are population properties.)

## Next step (authorized, out of this slug's frozen scope)

Phase B: diagnose why the ALREADY-BUILT goal-outcome organ HARD_FAILs (`PHASE_B_PRIOR_WORK.md` --
the mechanism exists; do not rebuild it) and fix the binding sub-component brain-foundationally,
evaluated against this now-frozen bank, proven in `experiments/` for the strategy session to land.


---

## INTEGRATED_BY_STRATEGY -- 2026-08-22, re-verified independently before acceptance

**ACCEPTED. I verified the ARTIFACT rather than re-running the submitted pipeline**, deliberately: a
re-run shares whatever bug the pipeline has, so it can confirm a number without confirming a fact.

| claim | independently recomputed | verdict |
|---|---|---|
| 166 items | `166` | MATCH |
| 124 scorable (`outcome_in_lexicon False`) | `124` | MATCH |
| majority floor `0.605` | `0.605` (`unmet 75` / `met 49`) | MATCH |
| length independent of the label | permutation `p = 0.984` (solver: `0.988`) | CONFIRMED |
| negation independent of the label | permutation `p = 0.564` (solver: `0.844`) | **CONFIRMED, NUMBER DIFFERS** |

**THE NEGATION p DOES NOT REPRODUCE EXACTLY (`0.564` vs `0.844`) and I am recording that rather than
smoothing it.** Almost certainly a different last-sentence extraction and cue set. **Both readings
are far from significance, so the CONCLUSION -- negation does not separate the labels on v2 -- is
unaffected.** *Do not quote `0.844` as reproduced; quote the conclusion.*

> ### ✅ **THE POSITIVE CONTROL IS WHAT MAKES THIS VERIFICATION MEAN ANYTHING.**
> "No separation on v2" is worthless unless the same instrument can SEE the cheat where it is known
> to live. **Run on v1's 36: `met = 410.9` chars vs `unmet = 340.3`, diff `+70.6`, permutation
> `p = 0.0027`.** ➡️ **The instrument detects it on v1 and finds nothing on v2.**
> 🔑 **AND `+70.6` / `p = 0.0027` REPRODUCES, TO THE DIGIT, A MEASUREMENT I TOOK INDEPENDENTLY ON v1
> DAYS BEFORE THIS BRIEF EXISTED.** *Two authors, two implementations, same number -- which is worth
> more than either of us checking our own work.*

**ONE DESIGN PROPERTY WORTH NAMING, WHICH THE SUBMISSION DOES NOT CLAIM: THE MAJORITY CLASS
FLIPPED.** v1 was `23 met / 13 unmet` (64% MET); v2 is `49 met / 75 unmet` (60.5% UNMET). **The old
bank's majority floor was "always say MET" -- the exact answer the organ systematically fails to
give, so it could never clear its own floor. That coincidence is gone.**

### WHAT THIS UNBLOCKS, AND ONE THING IT DOES NOT

- ✅ **The 36-item bank is no longer the binding constraint on this line.** `124` scorable at `3.4x`
  is enough to separate margins that `n=36` could not.
- ✅ **I was DISQUALIFIED from building this** -- I had read the per-item predictions, so gold I
  authored would violate *did the test items exist before the mechanism did?* **A solver who had not
  read them is the correct author, and the split worked as designed here.**
- 🚫 **IT DOES NOT MAKE ANY PRIOR RESULT ON v1 WRONG.** Numbers measured on the 36 remain numbers
  about the 36. **They may not be quoted as v2 numbers, and v1/v2 results may not be compared
  directly** -- different populations, different majority class, no number crosses.
