# **ON THE ITEMS WHERE A GOAL IS RECOGNIZED AND THE CASCADE COMMITS, IT IS RIGHT `10 OF 19`. EXACT BINOMIAL vs A COIN FLIP: `p = 1.0000`.**

**This retires the recommendation I made one turn ago.** *I wrote: "the repair is upstream -- make the
cascade FIRE, not make the guess better." **Routing more items into a coin flip does not help**, and the
arithmetic that shows it uses numbers I had already printed.*

---

## 1. THE ROOT OF THE `44%` ABSTENTION IS GOAL RECOGNITION

*All four tiers require `find_desired_state` to find an antecedent goal. Measured on the fall-through
items: **`T1 NA`x15, `T2 NA`x16, `T3 NA`x16, `T4 NA`x16** -- the cascade does not partially fire, it goes
silent together.*

| | decided structurally | fell through |
|---|---|---|
| **goal recognized** | **19** | 6 |
| **NO goal recognized** | 1 | **10** |

**Goal recognition is a near-perfect gate: `76.0%` of goal-recognized items get decided, versus `9.1%`
without one. Overall recognition on the bank is `25/36` = `69.4%`.**

## 2. 🔻 **AND FIXING IT WOULD NOT CLEAR THE FLOOR, BECAUSE OF WHAT THE OTHER COLUMN SAYS**

| | |
|---|---|
| **CEILING** -- all 10 no-goal items become correct | `24/36` = `0.6667` ✅ *clears* |
| **REALISTIC** -- they route into the cascade at the rate the cascade actually achieves | 🔻 **`19.3/36` = `0.5351`** -- **BELOW THE `0.6389` FLOOR** |

**To clear the floor by routing alone, those 10 items would have to be answered at `90.0%`. The cascade
manages `52.6%` on its own turf.**

> # 🔑 **A CEILING ASSUMES PERFECTION. THE MEASURED CONDITIONAL ACCURACY IS THE HONEST MULTIPLIER, AND IT WAS SITTING IN THE ADJACENT CELL OF MY OWN TABLE.**

## 3. **THE NUMBER UNDERNEATH EVERYTHING**

| | |
|---|---|
| cascade accuracy **when a goal is found AND it commits** | **`10/19` = `0.5263`** |
| 95% Wilson CI | `[0.3171, 0.7267]` |
| **exact binomial vs `0.5`, two-sided** | 🔻 **`p = 1.0000`** |

> ## **FOUR TIERS -- verb-class windowing, referent recurrence, grounded result class, request/response -- EACH ITS OWN DOCUMENTED BUILD, AND ON THE ITEMS IT WAS DESIGNED FOR IT CANNOT BE SHOWN TO BEAT GUESSING.**

⚠️ **AND THE DISCIPLINE APPLIES TO ME TOO: `n=19` IS SMALL. THIS IS *"NEVER DEMONSTRATED TO
DISCRIMINATE"*, NOT *"PROVEN EQUAL TO CHANCE"*.** *Underpowered is not negative -- that is this
project's most-repeated error and I am not committing it in the note that finds it.*

## 4. WHAT THIS REORDERS

| lever | ceiling | verdict |
|---|---|---|
| **cascade accuracy** (19 items, 9 wrong) | `0.7222` | ✅ **the only lever that is not conditional on another one** |
| goal recognition (10 items, 7 wrong) | `0.6667` ceiling / **`0.5351` realistic** | 🔻 *only pays AFTER the cascade discriminates* |
| both | `0.9167` | -- |
| `referent_mismatch` (the documented bug) | `0.6111` | 🔻 *cannot clear alone, established last turn* |

**The two levers are NOT substitutes and NOT independent: coverage without discrimination buys
nothing.** *That is the whole content of this note.*

## 5. ⚠️ LIMITS

1. **n=36 overall, n=19 for the headline.** Everything here is small-n; the ORDERING is what I trust,
   not the values.
2. **One eval bank.** These are properties of this cascade ON THIS BANK -- which is also the bank every
   decision on this line has been made from, all session.
3. **The realistic projection assumes newly-routed items behave like currently-routed ones.** They may
   be systematically easier or harder; I have not shown they are comparable.
4. **I have not diagnosed WHY the cascade is at chance** -- only that it is. *Naming is not diagnosing;
   three times today I have been wrong doing that.*

## TLDR

The system judges whether a story's goal came out well using four purpose-built checks in sequence.
Yesterday I found it goes silent on 44% of the test and said the fix was to make it speak up more often.

**Today I checked what it does when it does speak.** On the 19 questions where it recognises a goal and
commits to an answer, **it gets 10 right — the same as flipping a coin.** The statistical test comparing
it to a coin flip comes back as identical, exactly 1.0.

**So my advice last turn was wrong.** Making it answer more questions just sends more questions to a
coin flip. I worked out what fixing the silence would actually buy, using the machine's own measured hit
rate rather than assuming the fixed version would be perfect: **it lands around 54 out of 100, still
short of the 64 we have to beat.** For silence-fixing alone to work, those questions would have to be
answered 90% correctly by a mechanism that manages 53%.

**Being fair to it:** 19 questions is a small test. This does not prove the machinery is worthless — it
proves it **has never been shown to work**, which is a different and more fixable statement.

**But the ordering is now clear.** Getting it to answer more is worthless until it can answer better.
Everything I investigated today — which action gets the credit, how verbs are spotted, the negative
vocabulary, the silence — sits downstream of a judgement that has never been demonstrated to be better
than a guess.

## QUESTIONS

None.

## NEXT STEPS

1. 🎯 **Diagnose WHY the cascade is at chance on its 19 committed items** -- it is the only unconditional
   lever left on this line. *Start by splitting those 19 by which tier committed and in which direction
   it erred; `same_class_same_referent` alone holds 9 of them with 2 wrong, so the errors are
   concentrated elsewhere and that is where to look.*
2. 🚫 **Do not build goal recognition, do not repair `referent_mismatch`.** *Both are real defects; both
   are conditional on a discriminator that has not been shown to work.*
3. *Method note: **the correcting number was in the cell next to the one I quoted.** Last turn's table
   had `goal/decided n=19 wrong=9` in it, and I reported the ceiling from a different row without
   multiplying the two together.*
