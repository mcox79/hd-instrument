# **FIVE CONSUMERS OF THIS ORGAN TREAT `AMBIGUOUS` AS AN ABSTENTION. THE ONE THAT PRODUCES THE LANDED NUMBER TREATS IT AS A WRONG ANSWER -- BY OMISSION.**

**Found because I made the same mistake myself this morning and went looking for where the
convention was written down.** Guard: `tools/score_with_abstention.py` (`--self-test`, 6/6).

---

## 1. THE ENUMERATION (grep `AMBIGUOUS` across the consumers of `congruence_*`)

| treats `AMBIGUOUS` as | where |
|---|---|
| **ABSTENTION** (5) | `verify_levin_lastresort_backoff.py:51` · `exp_verbclass_backoff_coverage_v1.py:214` · `exp_verbclass_backoff_coverage_v2.py:73` · `verify_request_response_typing.py:200` · **`hdlab/consequence_learning_loop.py:219,235`** -- *the engine itself, in words: "AMBIGUOUS -> abstain"* |
| 🔻 **WRONG ANSWER** (1) | **`exp_consequence_learning_loop_oov_outcome_verb_valence_v1.py`** -- its `_score` does `ok = (pred == gold)` and **never mentions `AMBIGUOUS` anywhere in the file** |

> # **THE DISSENTER IS THE CELL WHOSE NUMBER THE ENTIRE LINE IS GRADED ON, IT DISAGREES WITH ITS OWN `hdlab` ENGINE, AND IT DISAGREES BY ACCIDENT RATHER THAN BY DECISION.**

## 2. ✅ IT HAS NOT BITTEN, AND THAT IS MEASURED, NOT ASSUMED

**The OOV-36 population returns `UNMET 7 / NONE 20 / MET 9` -- ZERO `AMBIGUOUS`.** *So the landed
`primary_accuracy` is **not** wrong today.* 🔻 **It is one prediction away from being wrong, and it
WOULD be wrong on the in-lexicon 8, where 2 of 8 come back `AMBIGUOUS`.**

*This is a LATENT measurement defect with a positive control already available -- which is the only
reason it is worth writing down rather than fixing silently.*

## 3. 🔻 AND IT REFINES MY OWN RETRACTION FROM EARLIER TODAY

*I retracted "abstention `0/8`, `p=0.0049`" on the grounds that **"the repo convention governs"**.
That was too clean.* **The accurate statement is that the repo holds BOTH conventions, in adjacent
files, on the same organ and the same bank -- and the one I used is the one the LANDED CELL uses.**

➡️ **SO THE HONEST VERDICT IS NOT "I USED THE WRONG ONE". IT IS THAT THE ABSTENTION CLAIM IS
CONVENTION-DEPENDENT AND THEREFORE NOT QUOTABLE EITHER WAY.** ✅ *The claim that SURVIVES is the one
that is convention-free: **accuracy is `4/8` under both readings** -- supplying the word does not buy
the answer.*

## 4. THE GUARD, AND WHY IT IS A FUNCTION RATHER THAN A RULE

`tools/score_with_abstention.py` returns an `AbstentionScore` carrying its own convention.
**There is no call signature that yields a bare accuracy**, and `both_conventions()` sets `.agree`
-- when False, no figure from that population may be quoted without naming the convention.

*Self-tested on the REAL failure (abstained 2 vs 0, flagged), on the claim that SURVIVED it
(accuracy identical, so the guard must not imply otherwise), on a **negative control** (a clean
population must NOT be flagged, or the guard cries wolf), and on the landed OOV-36 shape -- **that
last assertion fails if the population ever acquires an `AMBIGUOUS`**, which is precisely when the
cell's omission stops being latent.*

**This is standing discipline 13 -- REPORT TIE CONVENTIONS BOTH WAYS -- in a new costume: there the
ambiguous case was a TIE in a ranking, here it is a THIRD OUTCOME in a classification.** *The repo
already escalated the ranking version into `rank_with_ties.py` after the prose rule was violated
twice in one day. **A caution written as prose gets violated; a control written as code catches
something. This is the sixth instance and the prose version did not save me either.***

---

## TLDR

The machine can give three answers: yes, no, and "I can't tell". Most of the code treats "I can't
tell" as declining to answer. The one piece of code that produces our official score treats it as a
wrong answer instead -- not deliberately, it just never considered the third case.

Right now this costs nothing, because that third answer happens not to come up in the 36 questions
the official score is measured on. It does come up elsewhere, so the error is sitting there waiting.
I've added a scorer that refuses to report a number without saying which of the two readings it
used, and it refuses quietly when both readings agree, so it won't become noise.

## QUESTIONS

None. Q106 and Q107 remain with the owner and neither blocks this.

## NEXT STEPS

1. ⚠️ **Fix `_score` in the landed cell to abstain on `AMBIGUOUS`, matching its own engine.**
   *It changes NO current number (measured: zero `AMBIGUOUS` in the OOV 36), so it is a safe edit
   -- but it edits `experiments/*.py`, which this repo routes to `hdi_exp_dev` rather than the main
   thread.* **NOT done here.**
2. **Use `score_with_abstention.both_conventions()` for any future figure off this organ**, rather
   than re-deciding the convention each time.
3. 🔎 **The same question is worth asking of the other three-outcome scorers in the repo** -- this
   was found by hand on one organ, and nothing systematically checks it.
