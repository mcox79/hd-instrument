# **I NEARLY REPORTED THAT MORE SENTENCES PER WORD MAKE IDENTIFICATION WORSE -- AND THAT IT CONFIRMED OUR "WRITE LESS" FINDING. HOLDING THE QUERIES FIXED SHOWS THE CURVE IS FLAT. THE POPULATION WAS MOVING, NOT THE DEPTH.**

**A result that agreed with something I already believed, on the first cut, and did not survive its
own control.**

---

## 1. WHAT THE FIRST SWEEP SHOWED, AND WHY IT WAS SEDUCTIVE

| sentences per word | hit@1 | delta |
|---|---|---|
| 5 | 0.1900 | |
| **10** | **0.2000** | +0.0100 |
| 20 | 0.1775 | **-0.0225** |
| 30 | 0.1600 | **-0.0175** |
| 41 | 0.1435 | **-0.0165** |

***A clean monotonic decline after 10.*** **And it pointed exactly where the plan already points:
*"THE ONE ACTIONABLE LEVER: WRITE LESS"*, *"crosstalk DOMINATES capacity"*.** *An independent
convergence on a different task and a different metric is a very attractive thing to report.*

## 2. 🔍 THE FIRST CONTROL I RAN -- AND IT CLEARED THE EFFECT

**Leave-one-out shrinks only the TARGET's profile: 4-of-5 at k=5, but 40-of-41 at k=41.** *A less
averaged profile can score a higher cosine against a single query, which would flatter the target
MOST at small k -- the exact shape of the decline.*

**Size-matched arm (one sentence dropped from EVERY lemma, so all 60 profiles are built from k-1):**
`0.1867 / 0.1983 / 0.1800 / 0.1633 / 0.1439`. ***Tracks the original within 0.0033 everywhere. NOT
the artifact.*** **At this point I had a controlled, replicated, theory-confirming result.**

## 3. 🔻 **THE SECOND CONTROL KILLED IT. THE QUERY SET WAS GROWING WITH THE DEPTH.**

***At k=5 only the first five sentences of each word are scored; at k=41, all forty-one.*** **So
every step ADDED HARDER QUERIES while also deepening the profiles, and the two travelled together.**

**Fixed-query version -- the SAME 300 queries at every depth, only profile depth varying:**

| profile depth | hit@1 (n=300 fixed) | delta |
|---|---|---|
| 5 | 0.1900 | |
| 10 | 0.2100 | +0.0200 |
| **20** | **0.2133** | +0.0033 |
| 30 | 0.1900 | -0.0233 |
| 41 | 0.1967 | +0.0067 |

> ### **THE DECLINE IS GONE. The curve RISES from 5 to 10 and is then FLAT within the noise of n=300 -- deltas of ±0.023 on 300 items are not distinguishable from each other.**

## 4. ✅ WHAT IS ACTUALLY TRUE HERE

1. ***MORE SENTENCES PER WORD DO NOT HURT.*** **The apparent harm was a moving population.**
2. **The only clear gain is `5 -> 10`.** *After that this measurement cannot tell 0.2133 from 0.1967.*
3. ***SO THE LIMIT IS NOT DATA PER WORD.*** **It saturates around ten sentences, and the live median
   word already gets about ten.** *Reading each word more would buy little on this task.*
4. 🚫 **THIS DOES NOT REPRODUCE "WRITE LESS", AND I WAS ABOUT TO SAY IT DID.**

⚠️ **LIMITS: no CI on the fixed-query points (n=300, 60 lemmas); "flat" means "not distinguishable at
this n", not "equal". Source-balanced lemmas only, which are not the average word. And this is
IDENTIFICATION, not meaning.**

## TLDR

I asked whether our system is held back by not reading each word often enough. **The first answer was
striking: the more sentences it saw of a word, the worse it got at recognising that word.** That
would have been a notable finding, and it agreed neatly with something we already believe — that this
system does better when it writes down less.

**Then I checked it properly, and it evaporated.**

The problem was that as I gave each word more sentences, I was also *testing on more sentences* —
including harder ones the smaller runs never saw. **Two things were changing at once, and I was
crediting the wrong one.**

**Holding the test fixed and varying only how much the system had read, the decline disappears
entirely.** Accuracy improves from five sentences to ten, and then stays flat.

**Which gives a genuinely useful answer to the original question: reading each word more than about
ten times buys us very little here — and our system already averages about ten.** So the thing
holding it back is not how often it sees each word.

**The part worth remembering: the wrong version of this result was the one that confirmed what I
already thought.** It survived the first control I designed. It took a second, different control to
kill it.

## QUESTIONS

None.

## NEXT STEPS

1. **Do not cite this as support for "write less".** *It is not, and the first cut of it was.*
2. **Do not propose "read each word more often" as a lever for identification** -- *saturates by ~10
   and the live median already gets ~10.*
3. *Method note: **the control that mattered was not the one I thought of first.** The size-matched
   arm cleared the effect and made it look solid; only fixing the query population killed it. **When
   a result agrees with a belief you already hold, one passing control is not enough.***
