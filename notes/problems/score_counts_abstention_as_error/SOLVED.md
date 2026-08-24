---
problem: score_counts_abstention_as_error
status: SOLVED
bar: "The cell's scorer agrees with its own engine, and every number that moves is reported both ways."
result: "OOV-36 (n=36), live congruence_with_lexicon_fallback. Coverage-weighted accuracy (abstain==error, the gated number) = 0.3056 = 11/36, UNCHANGED by the fix. Selective accuracy when committing = 0.5789 = 11/19 under the engine convention (NONE+AMBIGUOUS abstain) vs 0.5000 = 11/22 under the narrow convention (only NONE abstains); both_conventions().agree = False. 3-way split: 11 correct / 8 wrong / 17 abstained (14 NONE + 3 AMBIGUOUS)."
floor: "The one number that moves is selective accuracy; its fair floor is the committed-subset majority class = 0.7368 = 14/19, which 0.5789 does NOT clear (this is an instrument fix, not a rescue). The gated coverage-weighted primary 0.3056 remains below the full-population majority floor 0.6389 -> verdict stays HARD_FAIL. Negative-control baseline (empty overlay) 0.3889, byte-identical before/after."
controls: "POSITIVE: the 3 AMBIGUOUS items (befriend/come/find) carried correct:False (scored wrong) in the landed record; after the fix they are abstentions and move committed-subset accuracy 0.5000->0.5789, and removing exactly those 3 makes the two conventions AGREE (they are the entire disagreement). NEGATIVE: empty-overlay baseline re-derived live has zero AMBIGUOUS and coverage-weighted accuracy byte-identical to the landed 0.3889. STABILITY: predictions reproduce 36/36 live from the saved overlay (not a JSON replay). ENGINE-COUPLING (positive, not an absence check): NONE and AMBIGUOUS are both members of hdlab.goal_typing._LEVIN_ABSTAIN, and the guard ABSTAIN_MAJORITY matches it."
files_changed: "experiments/exp_consequence_learning_loop_oov_outcome_verb_valence_v1.py (_score is now abstention-aware via tools/score_with_abstention.py; additive metrics fields; gates untouched); verification/test_oov_cell_scores_abstention_as_abstention.py (new scaffold-free witness); notes/problems/score_counts_abstention_as_error/SOLVED.md"
reverify: ".venv/Scripts/python.exe verification/test_oov_cell_scores_abstention_as_abstention.py"
---

## TLDR (plain language)

The one number this experiment is graded on treated the system saying **"I can't tell"** as if it had
given a **wrong answer**. I made it stop doing that. The system's own engine has always counted
"I can't tell" as *declining to answer*, not as an error; the scoring code in this one cell was the
only place that disagreed, and it disagreed by accident.

The fix does **not** make the score look better, and I checked that carefully -- the headline number is
byte-for-byte the same. What it fixes is that the instrument was **misdescribing** what the system
does: it was reporting "wrong 69% of the time" when the truth is "**wrong 22% of the time, and honestly
unsure 47% of the time.**" A system that knows when it doesn't know is behaving *well* in a way the old
scorer erased.

I also found the problem is bigger than the brief said. The brief named **3** "I can't tell" answers.
The disk has **17** of them (3 of one kind, 14 of another) -- and the old scorer counted all 17 as
wrong. The brief only noticed the 3 because those 3 are the ones where the *choice of how to count*
changes a number.

## What I built

- **The fix (in my lane -- `experiments/`).** `_score` in the goal-bearing cell no longer does
  `ok = (pred == gold)`. It now classifies each item **correct / wrong / abstained** using the repo
  guard `tools/score_with_abstention.py` (self-test 6/6), and records **both scoring conventions** plus
  the `.agree` flag, additively. The gated `primary_accuracy` is left exactly as it was.
- **A scaffold-free witness** (`verification/test_oov_cell_scores_abstention_as_abstention.py`) that
  exercises the edited cell **live** on the already-learned overlay -- it re-learns nothing, re-derives
  the 36 predictions from the saved overlay, and writes nothing to the landed directory. Passes all
  checks.

**I did not re-run the cell.** Editing the source is mine; regenerating the landed
`data/.../metrics.json` is a re-land, which per board Q111 is the strategy session's, and re-running in
place would re-date the landed record (the documented `harness_cannot_recompute` hazard). The witness
proves the corrected numbers from the existing overlay instead.

## What I measured (OOV-36, n=36, live `congruence_with_lexicon_fallback`)

| quantity | value | note |
|---|---|---|
| coverage-weighted accuracy (abstain==error) -- **the gated number** | **0.3056 = 11/36** | **UNCHANGED**; verdict stays HARD_FAIL vs floor 0.6389 |
| 3-way split | **11 correct / 8 wrong / 17 abstained** | old scorer reported this as 11 correct / 25 "not correct" |
| abstentions | **17 = 14 NONE + 3 AMBIGUOUS** | all reason `abstain_fallback_to_lexicon` |
| coverage (fraction committed) | 0.5278 = 19/36 | |
| selective accuracy when committing -- **engine convention** (NONE+AMBIGUOUS abstain) | **0.5789 = 11/19** | the number that moves |
| selective accuracy when committing -- narrow convention (only NONE abstains) | 0.5000 = 11/22 | AMBIGUOUS counted as error |
| `both_conventions().agree` | **False** | the 3 AMBIGUOUS are the entire disagreement |
| baseline, empty overlay (negative control) | 0.3889, **0 AMBIGUOUS**, agree=True | byte-identical before/after |

**Why the gated number cannot move:** coverage-weighted accuracy is `correct / n`. Whether a
non-correct item is labelled "wrong" or "abstained" does not change `correct` and does not change `n`,
so the value is invariant to the relabel. That is exactly why the brief is right that this is not a
rescue -- and it is also why no gate threshold can move. Every gate in the cell reads coverage-weighted
quantities (`primary_accuracy`, `learnable_subset_accuracy`), so all gates are untouched. **I changed
no band.**

## The disk outranked the brief: the defect is 17, not 3

The brief's MEASURED section says the defect "fires 3 times" (the 3 AMBIGUOUS). The disk shows the cell
had **no abstention handling at all**, so it also scored the **14 NONE** predictions as wrong. `NONE`
is an abstention in the readout's own set -- `hdlab.goal_typing._LEVIN_ABSTAIN = ('NA','NONE',
'AMBIGUOUS')`, which the readout branches on at `goal_typing.py:2200,2214` -- and in **both** of the
guard's convention sets. I confirmed this by **reading the abstain set and seeing NONE in it** (a
positive control), not by failing to find NONE committed. The brief named only the 3 AMBIGUOUS because
AMBIGUOUS is the token on which the majority and narrow conventions *differ*; NONE abstains under both,
so it never trips `.agree`. Both are the same event on the disk: `abstain_fallback_to_lexicon`.

This does not contradict the brief's conclusion -- it strengthens it. The instrument was mislabelling
**17** withheld answers as errors, not 3.

## Brain-foundational framing (the *why*, marked for what is pinned vs ours)

The organ is an **evidence-accumulation cascade with an opt-out branch**: structural congruence ->
referent recurrence -> grounded result-class -> request/response -> flat lexicon -> Levin backoff, and
it **abstains** (returns NONE/AMBIGUOUS) when no tier crosses threshold. Scoring an abstention
identically to a confident wrong answer collapses the two things a decision system must keep separate:

- a **commission error** -- committed to MET when the truth is UNMET (confidently wrong), and
- an **abstention** -- declined to commit under insufficient/conflicting evidence (knows it doesn't
  know).

**PINNED by evidence:** withholding a decision under uncertainty is a distinct neural act, not a failed
commitment -- the opt-out response has a direct correlate in evidence-accumulation-to-bound circuits
(Kiani & Shadlen 2009, LIP "sure-target" opt-out under low accumulated evidence), gated by a
metacognitive criterion (signal-detection theory: a response carries both a decision axis *and* a
criterion; abstention = evidence never crossed criterion). **OUR-INVENTION-UNDER-TEST:** the specific
mapping of *this* cascade's NONE (no tier fired) and AMBIGUOUS (tiers conflicted) onto that
metacognitive-bound picture is our interpretation, not a measured correspondence.

The correct instrument for such a system is the **risk-coverage decomposition** of selective prediction
(El-Yaniv & Wiener 2010): report **coverage** (how often it commits) and **selective accuracy**
(accuracy when it commits) as a *pair*, because a system trades one for the other -- the same
speed/accuracy/abstention trade the brain runs. `AbstentionScore` already **is** that summary
(`abstention_rate`, `precision_when_committing`, `accuracy_abstain_counts_wrong`); wiring the cell to it
restores the cell's ability to *see* the abstention behavior that is the entire point of an
evidence-cascade with opt-out. Here that behavior is: **commits on 53% of items, and is 58% accurate
when it does** -- invisible under the single "31%" the old scorer produced.

## What I did NOT establish

- **Nothing about capability.** Selective accuracy 0.5789 does **not** clear its fair floor -- the
  committed-subset majority class is 0.7368 (14 of the 19 committed items are gold MET). The system is
  still worse-than-majority *even when it chooses to answer*. This is an instrument correction; it says
  nothing good or bad about the mechanism's competence.
- **Whether the abstention rate itself is well-calibrated.** I report coverage and selective accuracy;
  I did not test whether the items it abstains on are genuinely the harder ones (a calibration/AUARC
  analysis). That is a real next question, not something this fix answers.
- **I did not re-land.** The corrected `metrics.json` will only exist after the strategy session
  re-runs the cell; the witness stands in for that until then.

## What I would withdraw first if it turned out to be wrong

The **"17, not 3"** claim rests on `NONE` being a true abstention rather than a committed "predicts
neither." If someone shows the goal-bearing task *intends* `NONE` to mean "the system asserts neither
outcome applies" (a commitment), then only the 3 AMBIGUOUS are abstentions and the narrow convention
(0.5000) is the engine-faithful one. I judged `NONE` an abstention because the readout's own
`_LEVIN_ABSTAIN` set, the engine's teacher (`consequence_learning_loop.py:233`, `b == "NONE"` treated
as silent), and all five other consumers agree it is -- but that is the load-bearing assumption, so it
is the first thing to check.

## Hand-back: what changes, and what does NOT need to change in `hdlab/`

- **`hdlab/` needs no change.** The engine was already correct; only the cell's scorer disagreed with
  it. This is the cleanest possible version of the defect -- the source of truth never moved.
- **The landed change is in `experiments/` (my lane) and is additive + gate-safe.** To re-land: run the
  cell to refresh `data/exp_consequence_learning_loop_oov_outcome_verb_valence_v1/metrics.json`. The
  new fields are `abstained_pred_count`, `abstention` (both conventions), and `baseline_abstention`;
  `primary_accuracy`, the gates, and the `HARD_FAIL` verdict are unchanged.
- **One tripwire is weaker than the brief implies.** The brief says the guard's self-test "FAILS the
  day the OOV-36 acquires an AMBIGUOUS." It does not: `score_with_abstention.py` self-test item 4 uses a
  **hard-coded fixture** (`["NONE"]*20 + ["MET"]*9 + ["UNMET"]*7`), which cannot see the live
  population, so it still passes 6/6 today even though the live population now has 3 AMBIGUOUS. The live
  tripwire is instead the new witness, which reads the landed predictions. Worth reconciling, but not
  mine to edit (`tools/`).

## TLDR / Questions / Next steps

**TLDR.** The scorer for this experiment used to count "I can't tell" as a wrong answer. Its own engine
never did. I fixed the scorer to match, and the fix deliberately does not change the headline number --
it changes what the number *means*, and it now also reports "how often it answers" and "how accurate it
is when it answers." The real problem turned out to be 17 hidden "I can't tell" answers, not the 3 the
brief flagged.

**Questions.** None blocking. (One worth a ruling at integration: is `NONE` an abstention or a
commitment? Every signal on the disk says abstention; I scored it that way.)

**Next steps (for the strategy session, not me).** (1) Re-run the cell to refresh the landed
`metrics.json` with the additive fields. (2) Consider replacing the guard's hard-coded fixture with a
read of the live landed predictions so the tripwire actually fires. (3) If abstention behavior becomes
interesting, add a calibration check (are the abstained items the harder ones?) -- that is the question
this fix makes askable.

---

## INTEGRATED_BY_STRATEGY -- 2026-08-24

Re-verified, 18 checks pass, every number recomputed live from the saved overlay. Review EXCELLENT. The scorer now agrees with the engine's own abstain set (_LEVIN_ABSTAIN = NA/NONE/AMBIGUOUS), and the witness checks that coupling directly.

Recorded as integrated on the strength of what it did NOT do: the gated number is byte-identical at 0.3056, so HARD_FAIL stands, and the one number that moves (selective accuracy 0.5000 -> 0.5789) still does not clear its own committed-subset floor of 0.7368. A scorer fix that improved the headline would have been the easiest possible way to launder a failure.

CARRIED FORWARD AS A STANDING CHECK: any scorer that treats abstention as error punishes the system for the behaviour the refuse-gate brief is separately trying to build. The other scorers have not been checked for the same defect.

*Appended by the strategy session, which owns integration (board Q111). Solver text unchanged.*
