# THE VALIDATED INSTRUMENT ALREADY SCORED OUR LIVE ENCODER -- **THE WORD ENCODING SITS AT RANDOM ON MEANING, AND THE CONCEPT ENCODING'S BIG SIGNAL IS ORTHOGRAPHIC**

**`exp_encoding_quality_instrument_v2`, landed 2026-08-15, 788 s. `INSTRUMENT_VALIDATED: 21/21
pre-registered gates passed.`** *Its predecessor v1 validated the instrument on 17/17 gates and
deliberately published NO number -- validate first, score second. That is the right order and it was
followed.*

**This is the cleanest measurement of our production encoder in the archive, and I had never opened
it.**

---

## 1. THE DESIGN INSIGHT, WHICH IS WORTH AS MUCH AS THE NUMBERS

**Two axes, reported separately and *deliberately not averaged*, each with its own note in the
metrics:**

| axis | the instrument's own note |
|---|---|
| **IDENTITY** (recoverability, sigma-half) | *"a RANDOM encoding is near-OPTIMAL on this axis by design; **scoring high here is NOT a win**"* |
| **STRUCTURE** (gold lifts, SimLex rho) | *"a RANDOM encoding must sit at lift ~1.0 / rho ~0.0 here; **any real lift IS the signal**"* |

**➡️ THAT IS WHY THEY MUST NOT BE AVERAGED: one axis is trivially maxed by noise.** *Averaging them
would let a random encoding launder its way to a respectable score -- which is the exact shape of
several artifacts caught tonight.*

## 2. 🔴 **THE LIVE WORD ENCODING IS AT RANDOM ON MEANING (d=256, the live dimension)**

| arm | SimLex rho | GOLD_ORTHO lift |
|---|---|---|
| **`P_LIVE_WORD`** | **-0.0019** | 0.987 |
| `A_RANDOM_IID` | -0.028 | 0.970 |
| `C_CONCEPT_SHUFFLED` (control) | -0.0092 | 1.021 |

**Our live word encoding is indistinguishable from a random encoding on the semantic axis.** *At
d=1024 it rises to rho 0.0747 against random 0.0119 -- better, still small, and **not the dimension
we run.***

## 3. ⚡ **THE CONCEPT ENCODING DOES CARRY REAL STRUCTURE -- AND THE BIG SIGNAL IS ORTHOGRAPHIC**

| arm (d=256) | SimLex rho | **GOLD_ORTHO lift** | FREQBAND | PLANTED |
|---|---|---|---|---|
| **`P_LIVE_CONCEPT`** | **0.1048** | **26.855** | 1.08 | 0.997 |
| **`C_CONCEPT_SHUFFLED`** | -0.0092 | **1.021** | 1.001 | 0.999 |

**THE SHUFFLED CONTROL COLLAPSES TO 1.021, SO THE 26.9x IS GENUINE SIGNAL, NOT A METRIC ARTIFACT.**
*That is the control doing its job, and it is what makes this readable at all.*

**➡️ THE CONCEPT ENCODING SHOWS A LARGE, CONTROL-VERIFIED LIFT ON THE *SPELLING* GOLD AND ONLY A
MODEST CORRELATION WITH HUMAN SIMILARITY JUDGEMENTS.**

**⚠️ WHAT I AM NOT SAYING: "26.9x more orthographic than semantic."** *A lift ratio and a rank
correlation are different units and cannot be divided. **No CI is reported for `simlex_rho` in this
structure**, so 0.1048 has no stated precision.* The defensible claim is the qualitative one: **a
large verified effect on spelling, a small one on meaning.**

## 4. WHY THIS MATTERS MORE THAN ANYTHING ELSE I FOUND TONIGHT

Every result tonight assumed the encoding carries meaning and asked what downstream organ fails to
use it. **This says the live word encoding carries essentially no meaning to begin with, at the
dimension we actually run.**

*It also gives the cleanest reading yet of why orthographic floors keep winning across this project:
`MEMORY.md` records `F_ORTHOGRAPHIC` as the binding floor in three cells. **If our concept encoding's
dominant verified structure is orthographic, an orthographic floor is not a nuisance baseline -- it
is a rival drawing on the same signal.***

**AND IT REFRAMES TONIGHT'S HAND-SCORES.** 3 MEANINGFUL of 100 blind is not obviously a *reading*
failure or an *extraction* failure. **It is consistent with a substrate whose word-level
representation has no semantic structure for anything downstream to read.**

## TLDR

I found a validated measuring instrument from the 15th that had already scored **our actual running
encoder**, and I had never opened it. It passed all 21 of its own checks, and its predecessor
deliberately published no numbers until the instrument itself was proven — the right order.

**Two findings.**

**Our word-level encoding carries essentially no meaning at the size we actually run.** Judged against
human ratings of word similarity it scores the same as random noise. At four times the size it does
slightly better, but that isn't the version in use.

**Our concept-level encoding does carry real structure — but the strong part is about spelling, not
meaning.** It shows a large effect on a spelling-based test, and only a weak relationship with human
judgements of meaning. **The experiment includes the right control** — scramble the concepts and the
spelling effect vanishes completely — so the effect is real, not a measurement quirk.

**Why this matters more than anything else I found:** everything else tonight assumed the system
stores meaning and asked which downstream part fails to use it. **This suggests the meaning may not
be there in the first place.** It also explains a pattern that's dogged this project — simple
spelling-based baselines keep beating our sophisticated methods. If our own representation is largely
spelling, then a spelling baseline isn't a cheap trick, **it's a competitor using the same signal.**

**One thing I'm careful not to claim:** the spelling number and the meaning number are in different
units and can't be divided into a ratio, and no precision is given for the meaning figure. The honest
version is "large verified effect on spelling, small one on meaning."

## QUESTIONS

None.

## NEXT STEPS

1. **This belongs in front of any plan that assumes the encoding carries meaning** -- which includes
   my own meaning-consumption proposal from earlier tonight.
2. **`P_LIVE_WORD` at d=1024 scores rho 0.0747 vs 0.0019 at d=256** -- the capacity question is live
   again on the axis that matters, and `ORGAN_MAP` STEP 2 already wants that switch flipped.
3. Ask the instrument's author for a CI on `simlex_rho`; without one the concept figure has no
   stated precision.
