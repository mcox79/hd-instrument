# **THE LIMIT IS THE REPRESENTATION, NOT THE READING. `256 -> 1024` BUYS `+0.0622` HIT@1, CI `[+0.0443, +0.0797]`, 48 OF 60 LEMMAS -- AND THE SCRAMBLE FLOOR STAYS AT CHANCE AT EVERY DIMENSION.**

**Two sweeps, one conclusion. More sentences per word does nothing past ten. More DIMENSIONS keeps
paying, and is still paying at 2048.**

> **RUN CONFIG: `GRADED_COMPARATOR=True` (shipped default), source-balanced lemmas over all 28
> corpora sampled round-robin, 60 lemmas x 41 sentences, leave-one-out, chance `0.0167` at every `d`
> by construction.**

---

## 1. THE SWEEP, WITH ITS FLOOR RECOMPUTED AT EVERY POINT

| `d` | hit@1 | **SCRAMBLE floor** | margin |
|---|---|---|---|
| 128 | 0.1061 | 0.0138 | +0.0923 |
| **256** *(what ships)* | **0.1435** | 0.0130 | +0.1305 |
| 512 | 0.1776 | 0.0187 | +0.1589 |
| **1024** *(what D1 proposes)* | **0.2057** | 0.0211 | +0.1846 |
| 2048 | **0.2268** | 0.0138 | **+0.2130** |

> ### ✅ **THE FLOOR IS RECOMPUTED AT EVERY `d` AND STAYS AT CHANCE (0.0130-0.0211). So the rise is not the metric inflating with dimension -- which is the one way this sweep could have fooled itself.**

**THE DECISION-RELEVANT PAIR, WITH AN INTERVAL:**
***`d=1024` MINUS `d=256` = `+0.0622`, 95% CI `[+0.0443, +0.0797]`, half-width `0.0177`, improved on
48 of 60 lemmas, CI EXCLUDES ZERO.***

## 2. 🎯 WHY THIS MATTERS FOR A DECISION ALREADY ON THE BOARD

**`notes/PLAN.md` D1 asks whether to raise the live path from 256 to 1024.** *Its evidence was
**"16x the dimensions bought +0.0843 at probe scale"** -- a different task, a different scale, and
`ORGAN_MAP` separately records that **`P_LIVE_CONCEPT` was only ever run at `d=256`, so NO CAPACITY
CLAIM IS AVAILABLE there.*** **This is `4x` the dimensions buying `+0.0622` on a task with a
recomputed floor and a CI. It is a second, independent measurement of the same lever.**

**And it answers the question the previous sweep raised.** *That one showed identification saturates
by about ten sentences per word -- and the live median word already gets about ten.* **So the binding
constraint is NOT how much we read. It is how much room the representation has.**

## 3. ⚠️ WHAT THIS IS NOT

1. **NOT a meaning result.** *This is IDENTIFICATION -- which word is this sentence about. Tonight
   also established that identification is largely a LOOKUP.* **Nothing here says meaning improves.**
2. **NOT the average word.** *Source-balanced lemmas, chosen for spread across the 28 corpora.*
3. **NOT free.** *`d` multiplies every stored profile. Owner answer to Q65 was **"do whatever is
   ideal"**, and the standing caution on D1 is to do it only with no concurrent session and a backup
   of the persisted stores -- because it rewrites every anchor store.*
4. **NOT saturated.** *It is still climbing at 2048 (`+0.0211` over 1024), so 1024 is not obviously
   the right stopping point -- this measurement does not find the knee.*

## TLDR

Our system recognises the right word about one time in seven. **I checked two possible reasons: it
hasn't read enough, or it hasn't got enough room to store what it read.**

**Reading more is not the answer** — that saturates after about ten sentences per word, and we
already average about ten.

**Room is the answer.** Quadrupling the size of the internal representation takes it from about one
in seven to about one in five, and it's still improving when I double it again. **The improvement is
solidly outside the margin of error and holds for 48 of the 60 words tested.**

**The check that makes this believable:** at every size I also ran a deliberately scrambled version,
where the link between words and their contexts is destroyed. **That stays at pure guesswork at every
size** — so the improvement is real capacity, not the measurement getting easier as things get
bigger.

**What I'm not claiming:** this is about recognising *which* word, not about understanding what it
means, and those came apart earlier tonight. It also isn't free — making the representation bigger
rewrites everything we've stored, which is why the standing advice is to do it with a backup and
nothing else running.

## QUESTIONS

None new. *This is evidence for a decision already recorded as D1, whose owner answer was "do
whatever is ideal".*

## NEXT STEPS

1. **D1 (`256 -> 1024`) now has a second, independent, floored measurement behind it** --
   `+0.0622 [+0.0443, +0.0797]` on identification.
2. **It is still climbing at 2048, so the knee is not where the plan assumes.** *If it is worth
   raising at all, the target may not be 1024.*
3. *Method note: **recomputing the scramble floor at every point is what makes this readable.** A
   rising curve alone would not have distinguished real capacity from a metric that inflates with
   dimension.*
