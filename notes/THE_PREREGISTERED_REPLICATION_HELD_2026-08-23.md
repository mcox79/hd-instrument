# THE PRE-REGISTERED REPLICATION HELD

**2026-08-23, strategy session.** I flagged a `17/18 = 0.9444` cell as post-hoc, said it needed
re-testing on a population fixed in advance, wrote the pre-registration, **committed it before the
numbers existed** (`notes/PREREG_replication_of_the_18_item_cell_2026-08-23.md`, commit `9d09f9945`),
and ran it once.

**VERDICT: REPRODUCED**, under the rule written down beforehand.

---

## 1. THE RESULT

Same question, **84-word anchor instead of 52** -- which changes every neighbourhood, so the
in-range sets, the margins, the commit decisions and therefore the cell membership are all freshly
determined.

| pre-specified cell | n | accuracy | original run |
|---|---|---|---|
| **1. weighted-only, SURVIVES the rounding** | `19` | **`0.8421`** (16/19) | `0.9444` (17/18) |
| 2. weighted-only, DISCARDED | `62` | `0.5806` | `0.6491` |
| 3. overlap, SURVIVES | `279` | `0.6595` | `0.6327` |
| 4. overlap, DISCARDED | `15` | `0.6667` | `0.5000` |

**THE PRE-SPECIFIED CONTRAST:** `0.8421 - 0.5806 = +0.2615`, CI95 `[+0.0509, +0.4635]` --
**EXCLUDES ZERO.**

**AND THE INTERACTION IS EXACTLY WHERE IT SHOULD BE:** in the overlap group, surviving the rounding
is worth `-0.0072`, CI95 `[-0.2466, +0.2394]` -- **crosses zero, i.e. nothing.**

🔑 **So the effect is confined to the group it was claimed for.** Confidence is worthless among
items both vote types reach, and worth a quarter of accuracy among items only the weighted vote
reaches. **A guard that fired everywhere would have been a red flag; this one fires in one place and
is silent in the other.**

---

## 2. WHAT REPLICATED AND WHAT SHRANK

✅ **The pattern replicated:** survivors beat discards inside the weighted-only group, by a margin
whose interval excludes zero.

🔻 **The effect shrank, exactly as a post-hoc cell should.** `0.9444` -> `0.8421`. **That is
regression to the mean and it is the expected behaviour of a number selected for looking good.**
*Had it come back at `0.94` again I would trust it less, not more.*

⚠️ **`n = 19`. The CI runs from `+0.05` to `+0.46`** -- the effect is real at this rule and its SIZE
is barely constrained. **Do not quote `+0.2615` as a magnitude.**

---

## 3. THE LIMIT I WROTE DOWN BEFORE I COULD BE TEMPTED TO OMIT IT

**THE ITEM POOL OVERLAPS THE ORIGINAL.** This is a replication under a different mechanism
configuration, **not an independent sample**. A fresh gold set would be stronger; the disk
enumeration found exactly one valence lexicon, so it does not exist here.

*That limitation was in the pre-registration, not discovered while writing this up -- which is the
only reason it can be believed.*

---

## 4. WHAT THIS CHANGES

| claim | status |
|---|---|
| the rounding discards a fifth of decisions | ✅ stands |
| *"no measured basis for preferring the ones it keeps"* | 🔻 **stays WITHDRAWN** -- and now there is a pre-registered basis, in one subgroup |
| confidence does not predict correctness (aggregate) | ✅ stands, and the interaction it averages over is now **confirmed rather than suspected** |
| similarity carries answerability, not valence | ✅ stands |

🚫 **STILL NOT PROPOSING A CHANGE TO THE ROUNDING.** The rounding is now shown to be doing something
useful in one corner. **That is an argument for leaving it alone, not for tuning it**, and n=19 is
not a basis for touching a shipped constant either way.

---

## TLDR

Last stretch I found something that looked great — 17 right out of 18 — and immediately said not to
trust it, because I had found it by slicing the same data many ways and something was bound to look
great eventually.

So I wrote down in advance exactly what I would test, which four groups I would look at, what
counted as success, and what I would not be allowed to do afterwards. I committed that, then ran it
once with a different set of hand-labelled starting words.

**It held.** The pattern is the same: in the group where the system's cleverest step is doing the
work, the answers it keeps are much better than the answers it throws away — and in the group where
that step adds nothing, keeping or throwing makes no difference at all. That second half matters as
much as the first: an effect that showed up everywhere would suggest I was measuring an artefact.

The number came down from 17-in-18 to 16-in-19. **That drop is the expected and reassuring outcome**
— a result found by looking around usually shrinks when retested. If it had come back just as
strong, I would trust it less.

Still only 19 items, and the test reuses much of the same vocabulary. I said both of those things
before running, which is the only reason they are worth anything now.

## QUESTIONS

None.

## NEXT STEPS

1. **Nothing here justifies changing the shipped rounding**, and the replication argues for leaving
   it alone rather than tuning it.
2. A genuinely independent test needs a second valence lexicon; the disk has one.
3. The polarity thread closes here. Every remaining question needs a population this evaluation
   cannot supply.
