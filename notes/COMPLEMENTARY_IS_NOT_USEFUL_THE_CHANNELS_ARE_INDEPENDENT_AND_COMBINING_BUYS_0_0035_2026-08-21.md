# **THE TWO CHANNELS ARE NEARLY INDEPENDENT (`rho 0.0901`) AND COMBINING THEM BUYS `+0.0035`. LOW CORRELATION IS NECESSARY FOR A COMBINATION TO HELP AND IT IS NOT SUFFICIENT.**

**`ORGAN_MAP` marks the hub-spoke combination rule UNPINNED and OUR-INVENTION-BEING-TESTED. Before
inventing one, this tests the precondition: do the channels carry complementary information, and does
combining them actually pay?**

---

## 1. THE TWO CHANNELS ON 829 IDENTICAL PAIRS

| channel | rho vs human |
|---|---|
| **LEARNED** -- masked context, `d=1024` | **+0.1071** |
| **SUPPLIED** -- norms12, euclid | **+0.2876** |

**CORRELATION BETWEEN THEM: `+0.0901`.** ***They are very nearly independent. By the usual argument
that is exactly the condition under which combining should help.***

## 2. 🔻 AND COMBINING BUYS ALMOST NOTHING

*z-scored, swept over the weight on the supplied channel:*

| weight on SUPPLIED | 0.00 | 0.25 | 0.50 | 0.70 | 0.80 | **0.90** | 1.00 |
|---|---|---|---|---|---|---|---|
| combined rho | 0.1071 | 0.1923 | 0.2608 | 0.2859 | 0.2894 | **0.2911** | 0.2876 |

***BEST `w=0.90`, rho `+0.2911`, against supplied-alone `+0.2876`. GAIN `+0.0035`.***

**Earlier tonight the same kind of paired comparison on this benchmark carried a CI half-width of
`~0.043`. `+0.0035` is an order of magnitude inside that.** *No CI was computed for this specific
difference and none is needed to see it is noise.*

> ### **THE OPTIMUM PUTS 90% OF THE WEIGHT ON THE HANDED-OVER TABLE AND 10% ON EVERYTHING THE SUBSTRATE LEARNED.**

## 3. 🎯 **WHY -- AND IT IS THE USEFUL PART**

***Independence is not the whole condition. A second channel helps in proportion to how much SIGNAL
it has, not just how UNCORRELATED it is.*** **At `rho 0.1071` against a null p95 of `~0.063`, the
learned channel has so little to contribute that adding it to a channel nearly three times stronger
moves nothing, however independent it is.**

**COMPLEMENTARY IS NOT THE SAME AS USEFUL.** *I would have predicted the opposite from the
correlation alone, and that is exactly why the precondition was worth measuring before inventing a
combination rule to exploit it.*

## 4. WHAT THIS SETTLES AND WHAT IT DOES NOT

| | |
|---|---|
| **build a hub-spoke combination rule NEXT** | 🚫 **NOT the move.** *There is nothing to combine yet.* |
| the channels are redundant | 🚫 **NO** -- `rho 0.0901`, they are nearly independent |
| a combination will NEVER help | ⚠️ **NOT CLAIMED.** *It will help when the learned channel is worth combining. This measures today's strengths, not the mechanism's ceiling.* |
| the right target | ✅ **MAKE THE LEARNED CHANNEL STRONGER.** *Combination is downstream of that and cheap to revisit.* |

## TLDR

We have two sources of word meaning: one the system learned by reading, one handed to us as human
ratings. **I checked whether using them together beats using the better one alone.**

**First the encouraging part:** the two barely agree with each other — they are almost completely
independent. Normally that is exactly when combining two sources pays off, because each knows
something the other does not.

**It does not pay off here.** The best possible blend is better than the good source alone by an
amount far too small to be real, and the blend that works best puts **ninety percent of its weight on
the handed-over table and ten percent on everything the system learned by reading.**

**The reason is worth keeping:** a second opinion helps in proportion to *how much it knows*, not
just *how different it is*. Ours is different, and it knows too little for that difference to matter.

**So building a clever scheme for combining them is not the next thing to do** — there is nothing yet
to combine. **The thing to fix is the weak channel.** Once it is worth listening to, this is a cheap
measurement to repeat.

## QUESTIONS

None.

## NEXT STEPS

1. **Do not build a hub-spoke combination rule as the next step.** *Best blend gains `+0.0035` where
   the noise floor on this comparison is `~0.043`.*
2. **Keep the finding that the channels are INDEPENDENT** (`rho 0.0901`) -- *that is the good news
   and it survives; it means the combination becomes worth doing the moment the learned side improves.*
3. *Method note: **near-zero correlation made me expect a gain, and the measurement said no.** The
   precondition for a mechanism is cheaper to test than the mechanism.*
