# ANGLE B CORRECTED: THE DEFINITIONAL HALF IS **HALF THE BANKED ROWS BUT ONLY A QUARTER OF THE WORDS** -- IT CANNOT SUPPLY THE PREDICTION FOR MOST OF THEM

> # ✅ SUPERSEDED THE SAME DAY -- **"UNRESOLVED" BELOW IS NOW "ANSWERED AGAINST"**
> This note left the filter open pending a quality test at low coverage. **That test was run.** On
> the 48 items where both routes fire, scored alone with no mixing: **definitional `-0.021`/item, CI
> `[-0.062, +0.000]` -- no signal at all**; distributional on the SAME items **`+0.188`, CI
> `[+0.042, +0.333]`**; paired **`-0.208`, CI `[-0.375, -0.042]`, SEPARATED.**
> **➡️ The filter should be INVERTED OR DROPPED, not marked unresolved.** Its three fallback options
> below are moot for the definitional-first framing; the open question is now only what F5 predicts
> FROM, and the distributional profiles are the only route measured to carry signal.
> The coverage finding below (24.6%) stands and is independent.
> `notes/THE_DEFINITIONS_CARRY_NO_ANOMALY_SIGNAL_...md`


**Testing the load-bearing claim I have repeated all session and never checked against a task.**
Angle B's design says *bind only the definitional half*, because hand-scoring puts it at **32%
MEANINGFUL** against **4%**. **That is a RUBRIC comparison, and a rubric is not an outcome.**

---

## 1. THE MEASUREMENT -- COVERAGE FIRST, BY DESIGN

7,535 simplewiki sentences read (465 item sentences excluded as leak control) yielded
**528 terms with a non-empty definition**.

| over 480 items | n | share |
|---|---|---|
| the **CORRECT** word has a definition | 118 | **24.6%** |
| the **INTRUDER** has a definition | 150 | 31.2% |
| **BOTH do -- the scorable items** | **48** | **10.0%** |

**HONEST VERDICT: NOT TESTABLE at this coverage. That is NOT a negative result.** With one item in
ten scorable, a low score would measure **coverage**, not meaning quality -- and reporting it as
*"the definitional half is worse"* would be precisely the confound the coverage check exists to
catch. *The script refuses to score rather than produce a number that would be misread.*

## 2. 🚨 **BUT THE COVERAGE FIGURE IS ITSELF THE ANSWER, AND IT CORRECTS MY DESIGN**

**Angle B assumed a clean split: use the 32% population, discard the 4% one.** The coverage number
says that split does not exist in the form the design needs.

**AND I CONFLATED TWO POPULATIONS TO GET THERE -- the same error I fixed in `STATUS.md` two turns
ago, in a different costume:**

| quantity | value | what it is a share OF |
|---|---|---|
| "212 of 402" | 53% | **provenance rows in one banking run** |
| definitional coverage of test words | **24.6%** | **the words that actually appear in arbitrary sentences** |

**Those are different denominators.** Being half the rows you happened to bank is not the same as
being available for half the words you meet. **The definitional route fires only on sentences
carrying a definitional pattern, so most words are never defined at all.**

## 3. WHAT THIS DOES TO THE DESIGN

**"Bind only the definitional half" leaves ~75% of encountered words with NO prediction**, and a
word with no prediction generates no error -- so F5 would be silent exactly where the substrate is
least informed. **The design needs a stated fallback, and there are only three options:**

1. **No prediction for uncovered words.** Honest, but the coherence monitor then covers a quarter of
   the text and cannot be the general mechanism the design claims.
2. **Fall back to the distributional profile** for uncovered words -- which reintroduces the 4%
   population the design explicitly excluded, and *the measured distributional arm scores +16.3 pp,
   so it is not worthless on this task even if its rubric score is poor.*
3. **Widen definitional coverage first** -- more patterns, more corpus, or a definition-seeking read.
   *That is a prerequisite, not a detail, and it was invisible until coverage was measured.*

**I cannot pick between these from evidence I have.** *(1) is a scope admission, (2) contradicts the
design's own stated reason for the split, and (3) is unbounded work.*

## 4. WHAT SURVIVES OF ANGLE B

**The architectural claim is untouched**: the banked meaning must supply the **PREDICTION** rather
than sit in the register, and the gap against observed context IS the error. **That is the pinned
half of F5 and this measurement says nothing against it.**

**What is corrected is the FILTER**, which was the design's second decision and which I stated as
settled: *"the filter is one field that already exists on every provenance row -- no new machinery."*
**True of the rows; false of the vocabulary.**

## TLDR

All session I have said the system's word meanings come in a good half and a bad half, and that the
fix is to use only the good half. I finally tested that, and the test says something I did not
expect.

**The good half is half of what the system wrote down, but only a quarter of the words it actually
meets.** Those sound like the same fact and they are not — the good half comes from sentences that
happen to contain a definition ("X is a kind of Y"), and most sentences do not. Across 480 test
items, only **one in ten** had a definition available for both words involved.

So the test could not be run, and I am reporting that as *"not testable"* rather than as a negative —
a bad score here would have been measuring how often definitions exist, not how good they are.

**But the coverage number is itself the answer to the design question.** "Use only the good half"
would leave three quarters of words with nothing to predict from, and the component I designed
produces its signal from prediction. It needs a stated fallback, and I laid out the three options
without choosing, because I do not have evidence to choose.

I also caught myself making the same mistake I fixed two days' worth of documents for: quoting a
share without checking **a share of what**. Half the rows written and a quarter of the words met are
different denominators.

## QUESTIONS

None -- the fallback choice needs evidence I do not have, and is recorded as an open design decision
rather than filed as a question, since it is not blocking anything today.

## NEXT STEPS

1. `tools/score_the_definitional_half_on_anomaly.py` refuses to score below 20% coverage; re-run it
   if coverage is widened.
2. Any future statement of the definitional/distributional split must name its DENOMINATOR.
3. F5's fallback for uncovered words is now an explicit open design decision.
