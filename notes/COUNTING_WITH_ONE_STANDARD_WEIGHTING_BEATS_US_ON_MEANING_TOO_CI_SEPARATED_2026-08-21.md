# **WORD-COUNTING WITH ONE LINE OF STANDARD TERM WEIGHTING SCORES `0.1835` WHERE WE SCORE `0.1071`. `+0.0764`, CI `[+0.0263, +0.1278]`, EXCLUDES ZERO. THE PROJECT'S STANDING NEGATIVE NOW REPRODUCES ON MEANING, WHICH IS A DIFFERENT TASK FROM WHERE IT WAS FOUND.**

**All night I floored my measurements against shuffles and chance. This is the floor the project
actually recognises, and I had not run it.**

---

## 1. THE LADDER, ALL ON THE SAME 829 PAIRS

| arm | rho vs human |
|---|---|
| co-occurrence counting, **raw** | 0.0885 |
| **OURS -- masked context, `d=1024`** | **0.1071** |
| **co-occurrence counting, `+idf`** | **0.1835** |
| supplied norms12, euclid | 0.2876 |

***`IDF-COUNTING MINUS OURS = +0.0764`, 95% CI `[+0.0263, +0.1278]`, half-width `0.0508`, EXCLUDES
ZERO.***

## 2. 🎯 WHAT IT MEANS, IN BOTH DIRECTIONS

✅ **WE DO BEAT RAW COUNTING** -- `0.1071` vs `0.0885`. *The reading loop is not doing nothing.*

🔻 **AND WE LOSE TO COUNTING PLUS ONE STANDARD WEIGHTING, CI-SEPARATED.** *Inverse document
frequency is a single multiplicative term, textbook since the 1970s, and it takes counting from
BELOW us to comfortably ABOVE us.*

> ### **THE RAW -> IDF STEP IS WORTH `+0.0950`. OUR ENTIRE LEARNED SIGNAL CLEARS ITS OWN NULL BY `~0.0440`. ONE STANDARD WEIGHTING IS WORTH MORE THAN TWICE EVERYTHING THE SUBSTRATE LEARNED.**

## 3. 🔁 **AND THIS IS THE SECOND TIME TONIGHT THAT SHAPE APPEARED**

| the standard choice | its value | our learned contribution |
|---|---|---|
| euclid instead of cosine on the supplied norms | **+0.0700** | `0.0440` over null |
| idf instead of raw counts | **+0.0950** | `0.0440` over null |

***TWICE, A ROUTINE METHODOLOGICAL CHOICE OUTWEIGHED THE SUBSTRATE'S WHOLE CONTRIBUTION.*** *That is
not an argument against the substrate; it is a statement about where the remaining headroom is
cheapest, and about how carefully rivals must be built before any comparison means anything.*

## 4. ✅ WHY THIS MATTERS BEYOND THE NUMBER

**The project's standing position -- `SUBSTRATE - COUNTING = -0.142`, CI-separated, "measurably
BEHIND counting" -- was measured on the WORD-RECALL task.** ***This reproduces it on a MEANING
benchmark, with a different scorer and a different population. A negative that survives a change of
task is a much stronger negative.***

## 5. ⚠️ LIMITS

1. **The idf rival is built from the SAME 41 sentences per word**, so it is a fair rival, but its
   document-frequency statistic comes from only 854 words' contexts. *A larger corpus would likely
   help it further, not us.*
2. **`0.1835` is not good either.** *Both are far below the supplied norms at `0.2876`.*
3. **No CI on the raw-vs-idf step itself**, only on idf-vs-ours.

## TLDR

All night I have been checking our system against scrambled data and against pure chance. **I had not
checked it against the obvious rival: just counting which words appear near which.**

**Plain counting scores 0.089 where we score 0.107 — so we are ahead of it.** That is the good news
and it is real.

**Then I added one standard adjustment to the counting** — the decades-old trick of paying less
attention to words that appear everywhere — **and counting jumps to 0.184, comfortably ahead of us,
by a margin large enough to be outside the error bars.**

**One line of ordinary technique is worth more than twice everything our system learned from
reading.** And this is the second time tonight that has happened: earlier, simply choosing a better
distance measure on a table of human ratings was worth more than our whole learned contribution.

**Why it matters beyond the number:** we already knew our system trails plain counting, but we knew it
on a *different* test. **Finding the same thing on a test of meaning, with a different scoring method,
makes that a much more solid conclusion** — it is not an artifact of one benchmark.

## QUESTIONS

None.

## NEXT STEPS

1. **Any future claim on this benchmark must clear IDF-WEIGHTED counting at `0.1835`**, not raw
   counting at `0.0885` and not a shuffle. *I had been using the weak floor.*
2. **The standing "behind counting" position is now CROSS-TASK.** *Quote it as reproduced on meaning,
   not only on word recall.*
3. *Method note: **the strongest floor is usually the rival someone would actually build, not the
   degenerate one.** Raw counting flattered us by `+0.0186`; the honest version beat us by `+0.0764`.*
