# **THE 36-ITEM BANK EVERY CONSEQUENCE-LEARNING RESULT RESTS ON HAS A LENGTH CONFOUND: `MET` PASSAGES ARE `+20.7%` LONGER (`p = 0.0027`), AND A RULER SCORES `0.8056` ON IT.**

**Found by the floor battery built an hour earlier, which is exactly what it was built to find.**

---

## 1. THE CONFOUND

| | n | mean chars | median |
|---|---|---|---|
| **MET** | 23 | **410.9** | 406.0 |
| **UNMET** | 13 | **340.3** | 339.0 |
| **difference** | | **`+70.6` chars = `+20.7%`** | |

**Permutation test, 20,000 shuffles: `p = 0.0027`.**

**AND IT IS NOT ONE CORPUS.** *MET is longer than UNMET in EVERY source where both classes appear:*

| corpus | MET | UNMET |
|---|---|---|
| little_women | 465.3 (n=7) | 388.3 (n=3) |
| wizard_of_oz | 405.5 (n=4) | 293.0 (n=1) |
| race | 453.0 (n=1) | 383.0 (n=2) |
| onestop | 401.3 (n=3) | 386.0 (n=1) |
| anne_of_green_gables | 348.0 (n=4) | 328.0 (n=5) |
| tom_sawyer | 372.0 (n=3) | 174.0 (n=1) |

## 2. 🔻 WHAT IT COSTS

**`text_length_chars` alone scores `0.8056` on this bank** -- *tied with the negation counter and above
the `0.6389` majority floor, with a margin of `+0.0556` over its own permutation null.*

> # **A RULER BEATS THE MAJORITY FLOOR ON THIS BANK. ANY ORGAN SCORED HERE COULD EXPLOIT PASSAGE LENGTH WITHOUT READING A WORD, AND NOTHING IN THE HARNESS WOULD NOTICE.**

## 3. 🔑 **AND THE ORGAN UNDER TEST IS NOT EVEN EXPLOITING IT**

**The four-tier cascade scores `0.4722` -- below a ruler, below a negation counter, below the majority
floor, and below all 12 trivial baselines the battery runs.**

*That is worth stating precisely because it CUTS AGAINST the obvious worry: the confound is not
inflating our result. It is available and unused.* **The organ is not cheating; it is failing to use
signal that a ruler picks up.**

## 4. ⚠️ IS THIS A FLAW IN THE BANK, OR A PROPERTY OF THE TASK?

**Plausibly the second, and I cannot separate them here.** *Narrating a goal that WAS achieved requires
describing the fulfilling event; a goal that was NOT achieved can be a short refusal -- the bank's own
`"I wanted to save him." / "But I couldn't."` is 6 words.* **If unfulfilled outcomes are genuinely
briefer in prose, the confound is a fact about narrative, not an annotation error.**

**Either way the consequence is the same: it must be reported beside any number from this bank**, and a
length-matched control is now required before any result here can be called comprehension.

## 5. LIMITS

1. **n=36, and 13 UNMET.** *The per-corpus table has cells of n=1; only the pooled figure and its
   permutation test carry weight.*
2. **CHARACTERS, not tokens or clauses.** *A different length measure might behave differently.*
3. **I have NOT re-scored anything with length matched** -- *this identifies the confound; it does not
   quantify how much of any past result it explains.*
4. **Cause unestablished** -- *narrative property vs sampling artifact, see section 4.*

## TLDR

Every result on this line -- the wall at 47 out of 100, the credit-assignment work, the channel
analysis -- is measured on the same 36 test passages. **Those passages have a giveaway in them: the
ones where the character got what they wanted are about 21% longer, and that difference is far too
consistent to be chance.**

**So a program that ignores the words entirely and just measures how long the passage is scores 81 out
of 100** -- better than the "always guess yes" baseline of 64, and better than our purpose-built
machinery.

**The reassuring half:** our machinery is *not* secretly exploiting this. It scores 47, below the ruler
and below every other trivial trick. It isn't cheating — it's failing to pick up signal that a ruler
picks up.

**It may not even be a flaw.** Describing a wish that came true takes narration; a wish that didn't can
be one line — *"But I couldn't."* If that's how stories work, the length difference is a fact about
prose rather than a mistake in the test set. **Either way it has to be stated next to any number from
this bank**, and any future claim of comprehension here needs a length-matched comparison first.

## QUESTIONS

None — Q106 (the 150-item scoring sheet) remains the only open one, and this is a sixth reason the
36-item bank is too small and too quirky to carry the line.

## NEXT STEPS

1. ⚠️ **Report the length confound beside any result from this bank.** *Recorded here; the bank is
   `goal_bearing_modern_eval_v1`.*
2. 🎯 **Any future comprehension claim on this bank needs a LENGTH-MATCHED control** -- *pair items of
   similar length across classes, or regress length out, before the number means anything.*
3. *Method note: **the tool found this within an hour of being built, on the first real bank I pointed
   it at.** The floor battery exists because the negation counter was found by accident; this is the
   first thing it caught that nobody was looking for.*
