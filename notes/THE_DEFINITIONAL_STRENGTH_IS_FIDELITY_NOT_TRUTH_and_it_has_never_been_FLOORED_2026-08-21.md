# **THE DEFINITIONAL PATH'S MEASURED STRENGTH IS *FIDELITY TO THE SENTENCE*, NOT TRUTH -- AND IT HAS NEVER BEEN SCORED AGAINST A FLOOR**

**Tonight I repeatedly called the definitional half "the one exception worth pressing" -- the only
part of the substrate's output with a repeatable quality signal. Reading the cell that actually
hand-scored it tempers that considerably, and the cell says so itself.**

---

## 1. THE NUMBER, AND EXACTLY WHAT IT MEASURES

`exp_definitional_predicate_v62`, hand-scored 2026-08-20, n=50 of 221:

| | |
|---|---|
| **result** | **48 correct / 2 incorrect -> precision 0.96** |
| **question scored** | ***"IS THE EXTRACTED TRIPLE FAITHFUL TO ITS SOURCE SENTENCE?"*** |
| verdict | *"HANDSCORE ANSWERED, POSITIVE: 96% of extracted predicate triples are faithful to their source sentence."* |

## 2. 🚨 **AND ITS OWN `scope_limits` FIELD DISARMS THE TWO READINGS I WAS ABOUT TO MAKE**

> **"SINGLE ARM. No control, no floor. This is a PRECISION figure, not a floor-cleared comparison,
> and CANNOT CLEAR THE PROJECT MEASUREMENT BAR."**

> **"THIS SCORES FIDELITY-TO-SENTENCE, NOT TRUTH.** Row 30 (`nitrification -> nitrite`) is faithful
> to a sentence that is **itself chemically backwards**; it was scored [correct]."

**➡️ 96% FAITHFUL IS NOT 96% TRUE. The extractor can perfectly extract a false statement, and on this
sample it demonstrably did.** *An extractor reading a textbook that contains an error will reproduce
the error with full marks.*

**➡️ AND THERE IS NO FLOOR.** *Every other quality claim tonight was judged against a control that
fired. **This one has none at all**, so "96%" cannot be compared with any of them.*

## 3. THE FAILURE MODE IS NOT NOISE -- WHICH IS THE GOOD NEWS

> *"BOTH errors are the same shape: **the wrong verb picked out of a complex clause** (a downstream
> participle, or a gerund complement). **Not random noise.**"*

**Two errors, one mechanism, and it is a parsing failure rather than a semantic one.** *That is a
fixable class, and the v6 -> v6.1 -> v6.2 chain is exactly a record of fixing named defects: v6.1's
summary is "fix the five hand-scored defects in the predicate extractor", and v6.2 fixed four more
(slot type, term sanity, main verb, main-clause argument).*

## 4. ⚠️ AND A BOOKKEEPING TRAP I NEARLY FELL INTO

**`v6` and `v61` have `SCORING_SHEET.txt` files with ZERO filled verdicts, and their metrics still
read `STRUCTURAL_PASS_PENDING_HANDSCORE`.** *I was about to record them as unscored work.*
**They are not: `v62`'s own note records "the cell note records the v6.1 hand-score as 40/2/8".**
**The scoring was done and written somewhere other than the sheet or the verdict field** -- the same
shape as `B3_RESOLVED.md`, where a completed blind hand-score sat unread behind a `PENDING` verdict.

**➡️ A `PENDING` VERDICT IN THIS REPO IS NOT EVIDENCE THAT THE WORK IS PENDING.** *Three instances
found tonight. **Check the sidecars and the cell notes before believing the verdict field.***

## 5. WHAT THIS DOES TO "THE DEFINITIONAL HALF IS THE EXCEPTION"

**IT SURVIVES, NARROWED:**
- **STANDS:** the definitional half hand-scores several times better than the distributional half on
  MEANINGFUL, across three independent samples (32%/4%, 48%/4%, 28%/6%).
- **NEW AND NARROWER:** its extraction is **96% faithful to source sentences** -- *a precision figure,
  single-arm, no floor, and about FIDELITY not TRUTH.*
- **➡️ THE HONEST COMPOSITE: THE DEFINITIONAL PATH FAITHFULLY EXTRACTS WHAT THE TEXT SAYS. WHETHER
  WHAT THE TEXT SAYS IS TRUE, AND WHETHER THIS BEATS ANY BASELINE, ARE BOTH UNMEASURED.**

## TLDR

I kept calling the definition-reading half of the system "the part that works." Reading the experiment
that actually graded it makes that more precise, and less flattering than I'd implied.

**It scores 96%** — but on a specific question: *does the extracted fact match the sentence it came
from?* **Not: is the fact true.** The experiment says so plainly, and gives an example where the
system faithfully extracted a statement from a textbook sentence that is **chemically backwards**, and
was marked correct for doing so. **A perfect extractor reading a wrong sentence produces a wrong fact
with full marks.**

**And it has no comparison.** Every other quality claim tonight was measured against something —
random, shuffled, a counting baseline. This one was measured against nothing, and the experiment
itself states it "cannot clear the project measurement bar."

**The good news is real though:** its two errors are the *same* error — grabbing the wrong verb out of
a complicated sentence. That's a grammar problem, not a comprehension problem, and it's the kind of
thing that gets fixed. The version history is literally a list of such fixes.

**One trap worth flagging:** two of these experiments look unfinished — they have blank grading sheets
and their status still says "awaiting grading." **They were graded; the results were written somewhere
else.** That's the third time tonight something marked "pending" was actually done. **In this project,
a status field saying "pending" is not evidence that anything is pending.**

## QUESTIONS

None.

## NEXT STEPS

1. **The definitional claim should now be stated as two separate things** -- better MEANINGFUL rates
   than the distributional half (three samples), and 96% fidelity-to-sentence (one sample, no floor).
   *Never as one number.*
2. **A floor for the fidelity figure is cheap and missing** -- even a shuffled-sentence control would
   make 96% interpretable.
3. **Do not trust `PENDING` verdict fields.** *Three-for-three tonight.*
