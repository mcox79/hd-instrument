# WITHDRAWN: **THE FLOOR DOES NOT CONFIRM MY HAND-SCORES** -- AND THE FAULT IS THAT I KEPT A CONCLUSION AFTER FIXING THE INPUT IT CAME FROM

**The claim, from today's F5-bar commit, listed as one of three "independent confirmations that the
item set is sound":**

> *"Co-occurrence surprisal separates the 102 hand-scored CLEAN items from the 17 hand-scored WEAK
> ones, so an independent machine measure agrees with the human pass about which items have an
> anomaly to find."*

**MEASURED PROPERLY (`tools/test_floor_separates_handscored_item_classes.py`):**

| | |
|---|---|
| CLEAN | n=101, median **4.00**, mean 5.25 |
| WEAK | n=17, median **5.00**, mean 5.79 |
| difference | **+0.54, 95% CI [-1.34, +2.60]** |
| Mann-Whitney | **p = 0.535** |

**IT DOES NOT SEPARATE.** The direction is right -- WEAK items do rank worse -- but **17 items
cannot resolve a gap that size.**

---

## THE TWO FAULTS, AND THE FIRST IS THE TRANSFERABLE ONE

### 1. 🚨 **I KEPT A CONCLUSION AFTER FIXING THE INPUT THAT PRODUCED IT**

The separation I quoted was **2.5 vs 4.0** -- and that came from the run **with the corpus leak in
it**, before I excluded the 120 item sentences. I found the leak, fixed it, correctly re-reported
the headline number it changed (rank 2.50 -> 4.00)... **and carried the CLEAN-vs-WEAK conclusion
across unchanged, because it still sounded right.** Post-fix the same comparison reads 4.0 vs 5.0
and does not survive a CI.

**➡️ FIXING AN INPUT INVALIDATES EVERY NUMBER DOWNSTREAM OF IT -- INCLUDING THE ONES THAT STILL LOOK
CORRECT.** *The leak fix was careful work; the failure was treating it as affecting only the number
I was looking at when I found it. There is no version of "partially recompute after a data fix".*

### 2. **I READ AN UNDERPOWERED POSITIVE AS A CONFIRMATION**

This is the exact mirror of the most expensive recorded error here -- *reading an underpowered NULL
as a capability statement, three times in one night.* **A median gap with no CI is not a finding in
EITHER direction.** I applied the CI discipline rigorously to the F5 bar in the same session and
skipped it entirely for the supporting claim, because the supporting claim was agreeing with me.

## WHAT SURVIVES

**WITHDRAWN, NOT REFUTED.** An underpowered test is not evidence that the hand-scores disagree with
the floor -- it is evidence the question was not asked with enough items. *To ask it properly would
need far more than 17 WEAK items, which means building more sets and hand-scoring them.*

**The other two confirmations from that commit are unaffected and stand:**

1. **FREQUENCY's delta is +0.00 / +0.50 / +0.75 / +0.50 across four independently-built sets** --
   the direct evidence that the frequency matching worked.
2. **POSITION, LENGTH and CONSTANT read EXACTLY +0.00** -- no positional artifact, no length
   artifact, no query-blind winner. **That one is exact arithmetic, not a statistic**, so no power
   question arises.

**And the F5 bar itself is untouched**: `+2.00 / +2.25 / +2.00 / +2.00`, `REPLICATED`, 1.1x spread.
That number was measured post-leak-fix and re-derived on four sets.

## 📌 A SECOND, SEPARATE FINDING FROM THE SAME ATTEMPT

**The reason I went looking was to test Angle B's corollary** -- that accumulated prediction error
could grade banked facts without a human -- against the several hundred facts hand-scored on
2026-08-20. **It cannot be done: those hand-scores were persisted as TALLIES, not as labelled rows.**
Five `_handscore_verdict_*.json` files hold counts, percentages and a handful of illustrative
examples; **not one carries a term-by-term label.**

**➡️ A HAND-SCORE PERSISTED AS A COUNT ANSWERS THE QUESTION THAT PROMPTED IT AND NOTHING ELSE.** The
expensive part is the human judgement per row; the tally is a lossy summary of it, and it throws
away every future use -- validating a gold-free quality estimate, error analysis, or re-scoring
under a revised rubric. *Today's `anomaly_set_..._v8_handscores.json` already does this right, with
a per-item verdict and reason; that is the pattern to keep.*

## TLDR

I checked one of my own claims from earlier today and it did not survive.

I had said that plain word-counting agrees with my hand-marking about which test sentences are good
— presented as independent evidence the test set is sound. **Measured properly, it does not: the
gap could easily be zero, and there are only 17 sentences in the smaller group.**

**The interesting part is how the error got in.** Earlier I found that the counting method had
secretly read the sentences it was being tested on, and I fixed it and correctly updated the
headline number. **But I carried this side-claim across unchanged, because it still sounded right.**
Its number came from the broken version. **Fixing an input invalidates everything downstream of it,
including the parts that still look fine.**

I also applied the "show me the error bar" rule strictly to the main result that same hour, and
skipped it for this one — because this one was agreeing with me.

Two of the three supporting checks stand, including the important one (the frequency matching
demonstrably works). The main number the whole exercise produced is unaffected.

**Separately:** I went looking in order to test whether the system could grade its own output
without a human. It can't be tested yet, because the several hundred judgements made yesterday were
saved as *totals* rather than as marks against each item. The expensive part was the judging; the
total throws it away.

## QUESTIONS

None.

## NEXT STEPS

1. **Hand-scores persist PER-ITEM from now on** -- today's anomaly-set file is the pattern.
2. The CLEAN-vs-WEAK question stays open and underpowered; it needs more WEAK items, not a re-read
   of the same 17.
3. F5 remains the substantive item, bar measured and replicated, blocked only on cell-authoring.
