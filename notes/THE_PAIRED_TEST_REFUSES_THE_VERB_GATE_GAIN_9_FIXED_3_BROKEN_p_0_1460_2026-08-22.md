# **THE PAIRED TEST REFUSES IT. `9` FIXED, `3` BROKEN, McNEMAR EXACT `p = 0.1460`. THE `0.4722 -> 0.6389` GAIN IS NOT SUPPORTED.**

**I said last turn that `0.6389` was "a point estimate with no admissible test behind it" and that the
fix was to persist per-item predictions. I did that. The admissible test now exists, and it says no.**

---

## 1. THE PLUMBING FIX WAS ONE LINE, AND THE DATA ALREADY EXISTED

`_score` computed a per-item `details` list -- `id`, `gold`, `pred`, `reason`, `correct` -- **on every
run since the cell was written, and `_aggregate` threw it away.** Now persisted as
`per_item_predictions`. *A few KB. It was the difference between an answerable and an unanswerable
question.*

## 2. ✅ BOTH ARMS REPRODUCED, THEN THE PAIRED TEST RAN

*Same 36 items, same gold (**0 gold mismatches between arms** -- checked, because a pairing is invalid
without it).*

| | |
|---|---|
| both arms correct | 14 |
| **TAGGER FIXED** (wrong -> right) | **9** |
| **TAGGER BROKE** (right -> wrong) | **3** |
| neither correct | 10 |
| **discordant pairs** | **12** |
| **McNemar exact, two-sided** | 🔻 **`p = 0.1460`** |

> # 🔻 **NOT SEPARATED. AND THE CORRECT TEST IS *WEAKER* THAN THE WRONG ONE I DECLINED TO USE -- the unpaired approximation read `p ~ 0.033`.**

**That is the whole reason the paired test mattered.** *The unpaired number would have been reported as
a significant gain. It is not one, because the intervention CHURNS: it does not just add correct
answers, it also destroys three that were already right.*

| | |
|---|---|
| **fixed** | `give`, `encore`, `find`, `give`, `buy`, `go`, `come`, `whip`, `drink` |
| 🔻 **broken** | `turn`, `befriend`, `have` |

## 3. 🔑 WHAT SURVIVES, AND WHAT I WITHDRAW

✅ **SURVIVES: the intervention CHANGES DECISIONS. `12` of `36` items flipped.** *That claim was the
genuinely new thing versus the `lemma_verb` repair, which took gold verb-inflection `53.50% -> 99.03%`
and moved the wall by NOTHING (four identical decimals). Changing which tokens are candidates does
reach the outcome; changing what they are called does not.*

🔻 **WITHDRAWN: that the change is an IMPROVEMENT.** *Last turn I wrote "this changes DECISIONS where
the repair changed only LABELS" immediately beside the `0.4722 -> 0.6389` figure. **The first half is
measured and stands. The second half is not supported and I am not going to let the two travel
together**, which is exactly how the caveat gets lost.*

**AND THE PRE-REGISTERED GATE NEVER MOVED: `0.6389` IS the majority floor, `primary <= floor -> chance`,
`HARD_FAIL` in both arms.** *A result that needs a non-pre-registered test to look good is not a
result.*

## 4. ⚠️ LIMITS

1. **n=36, 12 discordant.** `p=0.1460` is *"not supported"*, **NOT** *"proven absent"* -- at this n the
   study cannot resolve a real effect of this size either way. **UNDERPOWERED IS NOT NEGATIVE**, and
   reading it as negative would be this project's most-repeated error for the fifth time.
2. **One config, deterministic cell.** No cross-seed replication available.
3. **9-versus-3 is a real asymmetry** and would reach significance at a larger n *if the ratio held*.
   That is a reason to enlarge the eval bank, not to quote `0.6389`.

## TLDR

Last turn the system's score on this task went from about 47 out of 100 to about 64 out of 100 after I
connected a proper grammar tool. **I refused to call it a win because the right statistical test
couldn't be run** — the experiment had never recorded which individual questions it got right.

**I made it record that. The right test now runs, and it does not back up the improvement.**

The reason is that the change is **messy rather than purely helpful**: it fixes nine questions and
breaks three that were previously right. Once you account for the fact that these are the *same*
questions before and after — which is what the proper test does — nine-versus-three out of 36 is well
within luck.

**What does survive is the interesting part.** Twelve of the 36 answers *changed*. A very similar repair
earlier this month changed nothing at all. So this kind of fix does reach the system's actual
decisions — **we just have no evidence yet that it reaches them in a good direction.**

**And a caution about the caution:** 36 questions is too few to settle this either way. "Not supported"
is not "disproved." The nine-to-three split would matter at a larger scale — so the useful next move is
a bigger test set, not another attempt to rescue this number.

## QUESTIONS

None.

## NEXT STEPS

1. **The eval bank is 36 items and is now the binding constraint on this whole line.** *Every result
   here — the wall, the gate swap, the sharpened-credit HARD_FAIL — is being decided by 36 questions.
   Enlarging it is worth more than any further mechanism change.*
2. **`per_item_predictions` now ships by default** *(landed run: `0.4722`, key metrics identical to the
   pre-edit landed values, so the field is additive)*. **Every future re-analysis of this cell is now
   free.**
3. *Method note: **the wrong test said `p = 0.033`, the right test said `p = 0.146`, and I had already
   written down that the wrong one was wrong before I saw either number.** Declaring which test counts
   BEFORE running it is what made this safe.*
