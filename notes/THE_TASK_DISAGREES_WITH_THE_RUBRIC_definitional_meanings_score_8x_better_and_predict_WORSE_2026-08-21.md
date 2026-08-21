# THE TASK DISAGREES WITH THE RUBRIC: THE DEFINITIONAL MEANINGS SCORE **8x BETTER BY HAND** AND **PREDICT WORSE**

> # ✅ RESOLVED SAME DAY -- **THE ALTERNATIVE EXPLANATION IS RULED OUT. IT IS THE DEFINITIONS.**
> This note left two readings open and named the test that separates them. It was run.
> **On the 48 items where BOTH routes fire, scored ALONE with no mixing and no z-score:**
> **DEFINITIONAL `-0.021` per item, CI `[-0.062, +0.000]`** -- indistinguishable from zero and
> certainly not positive. **DISTRIBUTIONAL on the SAME items `+0.188`, CI `[+0.042, +0.333]`.**
> **PAIRED `-0.208`, CI `[-0.375, -0.042]` -- SEPARATED.**
> **➡️ My per-sentence z-score is EXONERATED; the loss is attributable to the definitions.** The
> caution below was the right thing to write and the right thing to then go and settle.
> `notes/THE_DEFINITIONS_CARRY_NO_ANOMALY_SIGNAL_...md`

**Pre-committed reading, written before the run.** Three outcomes were named in advance; **the third
fired.**

| arm -- paired anomalous-vs-original hit@1, 4 sets | per set | median |
|---|---|---|
| **DISTRIBUTIONAL** (accumulated profiles) | +12.5, +11.8, +20.8, +20.2 | **+16.3 pp** |
| **HYBRID** (definition where available, profile otherwise) | -0.8, +1.7, +13.3, +8.4 | **+5.0 pp** |

> **PAIRED, same items: HYBRID - DISTRIBUTIONAL = -0.107 per item, 95% CI [-0.144, -0.069].
> SEPARATED.**

**Substituting the extracted definition where one exists makes the system MEASURABLY WORSE than
using the accumulated profile everywhere.**

---

## 1. 🚨 **THIS IS THE STANDING RULE FIRING ON MY OWN DESIGN**

*"A statistic the mechanism optimises may DIAGNOSE, it may never DECIDE."*

The definitional half scores **32% MEANINGFUL against 4%** -- eight times better -- on a hand-score
rubric. **I used that rubric to justify a design decision (bind only the definitional half) and the
task now disagrees with it.** *The rubric asks "is this a good definition". The task asks "does this
predict the context". Those are different questions and I had been treating one as evidence for the
other all session.*

## 2. ⚠️ **THE ALTERNATIVE EXPLANATION, WHICH I CANNOT YET RULE OUT AND WILL NOT BURY**

**The hybrid's scale-mixing is MY invention and could be the defect rather than the definitions.**
A cosine over PPMI counts and a cosine over bundled bipolar codes have different spreads, so the
hybrid z-scores the definitional route within each sentence before choosing. **That z-scoring is not
brain-derived, not validated, and sits exactly where the damage would show.**

**Two readings remain open and they have different consequences:**

| reading | consequence |
|---|---|
| the definitions genuinely predict context worse | a finding about the EXTRACTOR, and Angle B's filter is wrong |
| my per-sentence z-score mixes the two scales badly | a finding about MY GLUE, and the question is still open |

**The clean discriminator is definitional-only scored against distributional-only on the SAME 48
covered items** -- no mixing, no z-score. *n=48 is small and it would need a CI, but it isolates the
one thing this run cannot separate.* **That is the next measurement, and until it is run the honest
statement is that the HYBRID is worse, not that the DEFINITIONS are.**

## 3. WHAT IS ESTABLISHED REGARDLESS

1. **`+16.3 pp` for the plain distributional arm survives** -- re-measured here identically
   (+12.5/+11.8/+20.8/+20.2), which is an incidental reproducibility check that passed.
2. **The hybrid, as designed, should not be built.** Whatever the cause, the arm that Angle B's
   filter implies is worse than doing nothing special.
3. **Coverage bounds everything here**: definitions exist for **24.6%** of the words, so neither a
   win nor a loss could have been large.

## 4. WHAT THIS DOES TO ANGLE B

**The architectural claim is STILL untouched** -- the meaning must supply the PREDICTION, and the
gap against observed context is the error. **Both filters proposed for it have now failed a check:**
the definitional filter covers only a quarter of words (previous note), and substituting it where it
does fire scores worse (this one).

**➡️ ANGLE B'S FILTER IS UNRESOLVED AND SHOULD BE STATED AS SUCH IN EVERY BRIEF.** *I stated it as
settled -- "the filter is one field that already exists on every provenance row, no new machinery"
-- and it has now been wrong twice for two different reasons.*

## TLDR

The system writes down word meanings two ways, and I have said all session that one way is eight
times better — that number comes from reading a sample by hand and judging them.

**I finally checked whether the better-judged meanings actually work better, and they do not.** Using
them where available made the system **measurably worse** at spotting an odd word than simply using
the cruder meanings everywhere. The comparison was run on identical sentences and the gap is solid.

**That is the rule this project already has, catching me:** a score the system was tuned toward can
tell you where to look, but it must never decide anything. "Is this a good definition" and "does this
help predict what comes next" turn out to be different questions, and I was using answers to the
first as evidence about the second.

**One honest caution I am not burying:** the way I combined the two kinds of meaning is my own
invention, and it could be the thing that is broken rather than the definitions. Distinguishing those
needs one more measurement on the smaller set of words where both exist. Until then the fair
statement is *"my combination is worse"*, not *"definitions are worse"*.

What survives: the core idea that a word's meaning should generate an expectation is untouched. What
is now twice-broken is my confident claim about **which** meanings to use — and I had called that
part settled.

## QUESTIONS

None.

## NEXT STEPS

1. **Definitional-only vs distributional-only on the 48 covered items**, with a CI -- the one test
   that separates "the definitions are worse" from "my glue is worse".
2. Every brief stating Angle B's filter must mark it UNRESOLVED.
