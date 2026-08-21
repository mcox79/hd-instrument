# T4b -- **THE "22x REFUSAL ASYMMETRY" WAS 93% ALREADY ON DISK BEFORE A SINGLE SENTENCE WAS READ**

**The claim being checked was mine**, filed tonight as a negative worth drilling:

> *"v1 (4322 anchors) refused 525 times; v2 (1415 anchors) refused 11,930, 98.7% of them
> `TAUTOLOGY_NO_ANCHOR`. A quality-filtered foundation refusing **22x** more often is either the most
> informative thing in that run or a second bug."*

**IT IS NEITHER. `state.refusals` IS A PERSISTED LIST THAT TRAVELS WITH THE FOUNDATION** -- not a
counter that starts at zero when reading begins.

## THE MEASUREMENT: LOAD EACH FOUNDATION, READ NOTHING, COUNT

*No read means no possible contribution from reading, so the number is unambiguous.*

| foundation | anchors | **refusals AT LOAD** | reported after read | **actually from the read** |
|---|---|---|---|---|
| `reading_grounding_v1` | 4,322 | **0** | 525 | **525** |
| `reading_grounding_v2_qualityfix` | 1,415 | **11,122** | 11,930 | **808** |

**➡️ 11,122 OF 11,930 -- 93.2% -- EXISTED BEFORE THE READ STARTED.**
**The real ratio is 808 vs 525 = 1.54x, in the expected direction (fewer anchors -> more
`TAUTOLOGY_NO_ANCHOR`) and entirely unremarkable.** *A 22x headline was a 1.5x effect wearing an
accumulated total.*

## ⚠️ AND A SECOND PROBLEM THE SAME CHECK EXPOSED: **THE TWO FOUNDATIONS ARE NOT COMPARABLE ON THIS FIELD AT ALL**

`v1` carries **ZERO** refusals at load despite holding 4,322 anchors. Either it never refused
during its own construction -- implausible -- or **its save did not persist the refusal log.**
**So `refusals` means different things in the two files, and any cross-foundation comparison of it
is comparing two different quantities.** *The delta-from-read comparison above is still valid,
because each arm is measured against its own baseline; the RAW TOTALS never were.*

## 🔁 THE PATTERN, FOURTH TIME TONIGHT

**Every one of tonight's four withdrawn claims is the same error in a different costume: A QUANTITY
THAT PRE-DATED THE INTERVENTION, ATTRIBUTED TO THE INTERVENTION.**

| claim | what was actually being measured |
|---|---|
| foraging "loses on every outcome" | which arm read the register the probe was written in |
| "the leak is refuted, so the finding is stronger" | one refuted confound, with a second one live |
| "this cell lost its data" | a 4 MB file my scanner could not open |
| **"22x refusal asymmetry"** | **a refusal log saved with the foundation months earlier** |

**THE CHEAP TEST THAT CATCHES ALL FOUR IS THE SAME ONE: MEASURE THE BASELINE BEFORE THE
INTERVENTION, EVEN WHEN IT OBVIOUSLY MUST BE ZERO.** *It is one line. It is cheaper than the
reasoning required to convince yourself it must be zero, and unlike that reasoning it cannot be
wrong.* **The repo already says this, for held-out overlap.** It generalises to every accumulated
field.

## TLDR

I flagged something tonight that looked dramatic: one version of the system refused to learn **22
times more often** than the other, which would have been either a big clue or a serious bug.

**It was neither.** The refusal tally is saved *inside* the knowledge file and carried forward — so
I was reading a total accumulated over that file's whole history and attributing it to the few
minutes of reading I'd just done. **93% of those refusals were already sitting on disk before the
test began.** The real difference is about one and a half times, which is exactly what you'd expect
from the smaller of two knowledge bases, and is not interesting.

The check took one line: load the file, read nothing, count.

**That's the fourth time tonight I've made the same mistake in a different disguise** — measuring
something that was already there and crediting it to what I just did. The fix is the same every
time: **check the starting value before you start, even when it's obvious it must be zero.**

One genuine problem did fall out: the two knowledge files don't record this the same way — one
appears not to save its refusal log at all — so their raw totals were never comparable in the first
place.

## QUESTIONS

None.

## NEXT STEPS

1. **The 22x is withdrawn; nothing further is owed to it.**
2. Worth confirming whether `reading_grounding_v1` genuinely persists no refusal log — if so, any
   note comparing raw refusal totals across foundations needs the same correction.
