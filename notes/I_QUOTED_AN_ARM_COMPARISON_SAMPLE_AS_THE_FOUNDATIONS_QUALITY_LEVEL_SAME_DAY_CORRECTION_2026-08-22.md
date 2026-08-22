# **I PUT `3 MEANINGFUL / 19 RELATED / 78 NOISE` INTO `STATUS.md` THIS MORNING AS "THE GROUNDING ANSWER". THOSE 100 ROWS WERE BUILT TO COMPARE TWO ARMS, NOT TO MEASURE THE FOUNDATION. CORRECTED THE SAME DAY.**

**The number is not wrong. The population I attached it to was.**

---

## 1. HOW IT SURFACED

*Running the newly-wired proxy across the foundations produced three pass rates that did not sit
together:*

| population | n | **proxy pass rate** |
|---|---|---|
| `reading_grounding_v1_full` | 1,216 | **`0.5683`** CI `[0.5402, 0.5958]` |
| `reading_grounding_v2q_full` | 634 | **`0.5016`** CI `[0.4628, 0.5404]` |
| 🔻 **the 100 hand-scored rows** | 100 | 🔻 **`0.3200`** |

**The CIs do not overlap.** *The hand-scored set is materially harder than either full foundation, by
the proxy's own measure.*

## 2. 🔑 WHY -- AND IT IS BY DESIGN, NOT BY ACCIDENT

**The blind sample is `50 / 50` across two ARMS (`PBV_BASE`, `PBV_F1F3`) and skews to the hardest
segment (`adv_new` 42 of 100, `int_cont` 21, `ele_cont` 18, `bio_new` 17, `bootstrap` 2).**

***It was constructed to measure the DIFFERENCE BETWEEN TWO ARMS.*** *The cell says so itself -- its
discriminator is `MEANINGFUL(PBV_F1F3) - MEANINGFUL(PBV_BASE)`, a DELTA. **A 50/50 arm-balanced draw is
the right design for a delta and the wrong design for a level.***

> # **THE CELL DID EVERYTHING RIGHT. I READ ITS OUTPUT AS ANSWERING A QUESTION IT WAS NOT ASKED.**

## 3. WHAT I CORRECT AND WHAT SURVIVES

| statement | status |
|---|---|
| `3 / 19 / 78` on those 100 rows | ✅ **stands, for its own population** |
| the arm delta `BASE - F1F3 = -0.020`, CI spanning zero | ✅ **stands -- this is what the sample was FOR** |
| 🔻 *"the loop's output is 78% noise"* as a FOUNDATION-WIDE claim | 🔻 **WITHDRAWN -- I wrote that into `STATUS.md` this morning** |
| the foundation-wide meaningful fraction | 🔻 **UNMEASURED** |
| the loop reliably accumulates (`scramble_ratio 0.077`) | ✅ **untouched** |

**`STATUS.md` corrected in place, because it is injected every session and an uncorrected headline
there propagates into every future context.**

## 4. ⚠️ AND THE OBVIOUS INFERENCE IS *NOT* AVAILABLE

**"The foundation passes the proxy at 0.50-0.57 and the hard sample at 0.32, so the foundation must be
better than 22% meaningful."** 🔻 **NO.** *Converting a pass rate into a meaningful-fraction requires
hit rates measured ON THAT POPULATION, and yesterday's note showed that exact inversion giving `74%`
against a measured `22%` -- a `3.4x` error. **The same trap, one day apart, and it is still shut.***

**What can be said: the hand-scored population is not representative. What cannot: what the
representative number is.**

## 5. LIMITS

1. **The proxy is a rough instrument** -- `0.591` recall, one validation, 100 rows. *"Materially
   harder by the proxy's measure" is a statement about the proxy as much as about the population.*
2. **I have not verified segment composition of the FOUNDATIONS**, only of the sample. *The comparison
   is pass-rate to pass-rate, not like-for-like on segment mix.*
3. **One scorer, once.**

## TLDR

This morning I wrote into our main status document that the system's learned facts are "3% meaningful,
78% noise", calling it the grounding answer. **The measurement is real. I attached it to the wrong
thing.**

Those 100 facts weren't a random sample of what the system knows. They were **deliberately picked half
from one experimental setup and half from another, weighted toward the hardest material**, because that
experiment's job was to compare the two setups against each other. That's the right way to measure a
*difference* and the wrong way to measure a *level*.

**I noticed because the new quality filter disagreed with itself across populations**: it passes about
half the facts in the actual stored foundations, but only a third of the hand-scored batch. Those
ranges don't overlap, which means the batch is harder than the bulk.

**So what I should have said:** the hand-scored figures are correct for the batch they came from, and
**we do not know the meaningful fraction of the foundation as a whole.**

**And the tempting follow-up is still off-limits:** "the foundation passes more often, so it must be
better than 22%." That's the same inversion that gave me 74% against a measured 22% yesterday. Knowing
a filter's pass rate on a new population tells you nothing about quality there until someone hand-scores
some of it.

**Which is, once again, the same missing thing.**

## QUESTIONS

None — Q105 open; this is the sixth distinct thing a representative hand-scored sample would settle.

## NEXT STEPS

1. 🎯 **A REPRESENTATIVE blind sample -- drawn at random from a foundation, not balanced across arms --
   is what measures the level.** *Every quality claim this week has failed for want of it.*
2. ⚠️ **Any future citation of `3/19/78` must carry "on an arm-balanced sample weighted to hard
   segments".** *Recorded in `STATUS.md` in place.*
3. *Method note: **the correction came from a tool disagreeing with itself across populations**, not
   from re-reading the note. **Running one instrument over several populations is a cheap way to find
   out that one of them is not what you thought.***
