# THE DEFINITIONS CARRY **NO ANOMALY SIGNAL AT ALL** -- AND MY GLUE IS EXONERATED

**The measurement I named in advance as the one that would separate two explanations.** It was run,
and it cleared the explanation that would have protected my own design.

**Scored ALONE on the 48 items where BOTH routes fire -- no mixing, no z-score, nothing of mine
between the arms:**

| arm | discrimination per item | 95% CI |
|---|---|---|
| **DEFINITIONAL** | **-0.021** | **[-0.062, +0.000]** -- indistinguishable from zero, certainly not positive |
| **DISTRIBUTIONAL**, same 48 items | **+0.188** | **[+0.042, +0.333]** -- real signal |
| **PAIRED, DEFINITIONAL - DISTRIBUTIONAL** | **-0.208** | **[-0.375, -0.042] -- SEPARATED** |

---

## 1. ✅ **THE ALTERNATIVE EXPLANATION IS RULED OUT, AND IT WAS THE ONE THAT WOULD HAVE LET ME OFF**

The hybrid run left two readings open. **The one that survives is the one against my design.**

| reading | verdict |
|---|---|
| my per-sentence z-score mixes two scales badly | **EXONERATED** -- removed entirely here, and the gap remains |
| the definitions genuinely predict context worse | **THIS ONE.** They carry no signal at all where they fire |

*Writing that caution down was right. Going and settling it was the point of writing it down --
a caution is a debt, not a shelter.*

## 2. 🚨 **WHAT IS ACTUALLY ESTABLISHED, STATED NARROWLY**

> **The extracted definitions carry NO measurable anomaly signal on this task**, on the items where
> they exist, while the accumulated distributional profiles carry real signal on **those same items**.

**AND THE NARROWNESS MATTERS -- THIS IS NOT "THE DEFINITIONS ARE BAD".** A correct definition need
not share vocabulary with an arbitrary sentence the word appears in. *"A bottle is a container used
to carry liquids"* tells you what a bottle IS and predicts almost nothing about a sentence
mentioning bottles at a picnic. **The hand-score rubric and this task are measuring genuinely
different properties, and the definitions may still be the right content for a different consumer --
a lookup, a question-answerer, an inference step -- just not for a prediction-error monitor.**

## 3. **WHAT IT SETTLES FOR ANGLE B**

**Angle B's filter is now ANSWERED, and answered against the design.** *"Bind only the definitional
half"* would **remove** the signal and keep the half that has none. Both of its supports have failed
for two independent reasons:

1. **Coverage** -- definitions exist for only **24.6%** of encountered words.
2. **Quality on the task** -- where they do exist, they carry **no anomaly signal**.

**➡️ THE FILTER SHOULD BE INVERTED OR DROPPED, NOT MARKED UNRESOLVED.** *That is a stronger statement
than the previous note's "unresolved", and it is warranted because the discriminating measurement has
now been run.*

**THE ARCHITECTURAL CLAIM IS STILL UNTOUCHED**: the meaning must supply the PREDICTION and the gap
against observed context is the error. **What has died is my claim about WHICH stored meanings should
do the predicting** -- and on this evidence it is the ones I called the bad half.

## 4. THE HONEST LIMITS

- **n=48**, which is the coverage meeting a paired requirement, not a design flaw. The CI is reported
  and the separation survives it.
- **One task.** Anomaly detection is not comprehension.
- **The distributional arm still does not clear the counting bar** (+16.3 pp against +44.2). *Winning
  this comparison is not winning.*

## TLDR

Last turn I found that using the "better" word meanings made the system worse, and I flagged one
alternative explanation: the way I combined the two kinds might be the broken part rather than the
meanings.

**I ran the test that separates those, and it cleared me and convicted the meanings.** On the small
set of words where both kinds exist, scored separately with none of my combining logic involved, the
hand-picked "good" meanings detect **nothing at all** — while the cruder automatic ones detect
something real on the very same words.

**So the good-looking meanings are not merely worse at this job. They are useless at it.**

The important qualifier: that does **not** mean they are bad definitions. *"A bottle is a container
for liquids"* is a fine definition and tells you almost nothing about a sentence where someone brings
bottles to a picnic. The two things I was measuring — is this a good definition, does this predict
what appears nearby — are genuinely different, and I had been treating one as evidence for the other.

What this kills is my confident claim about **which** stored meanings should drive the system's
expectations. On this evidence it is the ones I had been calling the bad half. What survives
untouched is the underlying idea that meanings should generate expectations at all.

And the sober note: the winning side here still loses badly to plain word-counting. Winning this
comparison is not winning.

## QUESTIONS

None.

## NEXT STEPS

1. Angle B's filter is ANSWERED against the design -- invert or drop, do not mark unresolved.
2. The definitions may still suit a different consumer; nothing here tests that.
3. `tools/definitional_vs_distributional_on_covered_items.py` is the instrument.
