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

## 2b. 🔴 **CORRECTION TO §2, AND IT MATTERS: THE WORD ENCODER IS RANDOM *BY CONSTRUCTION*, NOT BY FAILURE**

**I wrote §2 as if a deficiency had been discovered. It has not.** The cell's
`production_encoder_identification` block names the live word encoder exactly:

> **`"INLINED in hdlab/grounding_acquisition_loop.context_vector and exposed as
> hdlab/reading_grounding_loop.symbol_vector: sha256(w)[:8] -> seed -> default_rng(seed).choice([-1,+1], d)"`**

**THE LIVE WORD CODE IS A HASH-SEEDED RANDOM DRAW. It cannot correlate with meaning -- not "does
not", CANNOT.** `rho = -0.0019` is not a finding about our encoder's quality; **it is the
mathematically necessary value, and its appearance confirms the instrument is measuring the right
object.**

**AND THAT IS ORTHODOX VSA, NOT A DEFECT.** *Atomic symbols are random by design; meaning is supposed
to live in what gets BUNDLED, which is the concept level.* **So "the meaning may not be there in the
first place", as I put it, is WRONG at the word level -- it was never meant to be there.**

*How the cell proves the arm really is the live path, rather than asserting it:*
**`byte_equality_vs_live_context_vector_masked: "200/200"`** -- 200 samples byte-identical to the live
function -- and the identification method is stated as *"RUNTIME: imported the two live entry points
and diffed `sys.modules`; then reconciled to `capability_registry.jsonl`. **Never the reverse, and
never from grep.**"* **That is the exact discipline `CLAUDE.md` demands, executed.**

**🔎 AND ONE MORE THING IN THAT BLOCK, WHICH BELONGS BESIDE TONIGHT'S ISLANDING WORK:**
> *"12 encoder-named candidates, **0 on the live path**... every encoder-named registry row is
> `WIRED_BUT_NOT_PIPELINE_REACHABLE`; **NO registry row names the live word encoder at all**."*

**Twelve built encoders, none reached, and the thing actually running is unregistered.**

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

**I initially misread the first one and have corrected it.** I reported the word-level result as a
*discovered weakness*. It isn't: the code that represents a word is **deliberately a random pattern
derived from its spelling hash** — that's the standard design in this family of systems, where words
are meant to be arbitrary tags and meaning is supposed to live in what accumulates around them.
**Scoring zero there is the mathematically required answer, and getting it is evidence the instrument
is pointed at the right thing.**

**So the real finding is the second one**, and it's narrower but sharper: **the level that IS supposed
to carry meaning carries a lot of spelling and a little meaning.**

That still explains a pattern that's dogged this project — simple spelling-based baselines keep
beating our sophisticated methods. If the structure our representation actually captures is largely
spelling, **a spelling baseline isn't a cheap trick, it's a competitor drawing on the same signal.**

**One more thing worth flagging:** twelve different encoders have been built, **none of them is on
the live path**, and the one actually running **isn't recorded in our capability list at all.**

**One thing I'm careful not to claim:** the spelling number and the meaning number are in different
units and can't be divided into a ratio, and no precision is given for the meaning figure. The honest
version is "large verified effect on spelling, small one on meaning."

## QUESTIONS

None.

## NEXT STEPS

1. **This belongs in front of any plan that assumes the encoding carries meaning** -- which includes
   my own meaning-consumption proposal from earlier tonight.
2. ~~`P_LIVE_WORD` at d=1024 scores rho 0.0747 vs 0.0019 at d=256 -- the capacity question is live
   again.~~ 🔴 **WITHDRAWN, WRONG ON BOTH COUNTS.**
   **(a) `P_LIVE_CONCEPT` WAS NEVER MEASURED AT d=1024** -- the d=1024 arm list has no such entry, so
   **this cell says NOTHING about concept-encoder capacity.**
   **(b) The arm I quoted is `P_LIVE_WORD`, which is the sha256-seeded RANDOM draw**, so its rho
   moving `-0.0019 -> 0.0747` is **noise in a quantity that cannot learn.** *And the tell was sitting
   in the same table: `A_RANDOM_IID` moves the SAME WAY over the same jump, `-0.028 -> 0.0119`.
   **Two independent random arms rising together is a property of the dimension and the 322-pair
   sample, not of anything learning.***
   *I made this error in the message reporting the finding, one turn after correcting a different
   misreading of the same cell. The guard that catches it is the one this file already praises: **ask
   what a random arm does under the same change.** It was in the table and I did not look.*
3. Ask the instrument's author for a CI on `simlex_rho`; without one the concept figure has no
   stated precision.
