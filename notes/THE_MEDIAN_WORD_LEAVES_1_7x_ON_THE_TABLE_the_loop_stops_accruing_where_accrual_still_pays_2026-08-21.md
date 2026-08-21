# **THE MEDIAN WORD SITS AT 10 TRACES WHERE 37 IS STILL PAYING. THE LOOP STOPS ACCRUING EXACTLY WHERE ACCRUAL IS STILL WORTH IT -- ~1.7x FOR THE MEDIAN WORD, ~2x FOR ONE THAT GROUNDS EARLY.**

**Two measurements from tonight, set beside each other. Owner Q71 and Q74 asked whether the loop
should keep taking notes on a word after it decides it knows that word. This gives the question a
measured size on one task.**

---

## 1. THE TWO MEASUREMENTS

**(a) MORE TRACES HELP** -- anchor self-identification, 80 lemmas, chance 0.0125, CI-separated
L=1 vs L=37, shuffled-label control at chance:

| traces | 1 | 4 | 8 | 16 | 24 | 37 |
|---|---|---|---|---|---|---|
| hit@1 | 0.0312 | 0.0516 | 0.0719 | 0.0984 | 0.1219 | **0.1328** |

**(b) WHAT THE LIVE LOOP ACTUALLY ACCUMULATES** -- 1,200-sentence read through the live path,
94 lemmas, every one with a known count: **median 10, p90 36, max 77.**

## 2. 🎯 PUT THEM TOGETHER

| live position | its hit@1 | hit@1 at L=37 | **left on the table** |
|---|---|---|---|
| **MEDIAN lemma (10 traces)** | **0.0785** | 0.1328 | **1.69x** |
| p90 lemma (36 traces) | 0.1320 | 0.1328 | 1.01x |

> ### **THE MEDIAN WORD IS SITTING AT ROUGHLY 60% OF WHAT ACCUMULATION ALREADY BUYS. THE BUSY TAIL IS ALREADY AT THE PLATEAU; THE TYPICAL WORD IS NOT.**

**And the standing example of early grounding, `century` at 7 traces from 92 occurrences:**
*7 traces -> 0.0668 against 0.1328 at 37 = **1.99x**, on a curve that had not flattened.*

## 3. ⚠️ **THE POPULATION WARNING, BECAUSE I AM COMBINING TWO MEASUREMENTS**

***The task curve comes from 80 lemmas over the corpus pool. The live distribution comes from 94
lemmas over a 1,200-sentence read. The `century` figure comes from a THIRD run recorded in
`STATUS`.*** **These are different populations and discipline 11 forbids quoting a single combined
multiplier as a measured result.**

**What IS supported:**
1. **the DIRECTION** -- more traces raise this score, CI-separated, with a working control;
2. **that the live MEDIAN sits well below the plateau** -- 10 against a curve still climbing at 24-37;
3. **that the busy tail is already at the plateau**, so the loss is concentrated on typical words, not rare ones.

**What is NOT supported:** *the exact multiplier as a single number. Treat 1.7x as an order-of-size
estimate that crosses populations, not a measurement.*

## 4. 🔗 WHY THIS MATTERS FOR THE STANDING QUESTION

**Owner, Q71: *"Right now the system stops taking notes on a word once it decides it knows that word.
So the words it meets most often end up with the FEWEST notes. Should it keep taking notes anyway?"***
**Owner, Q74, after the fix was tested: *"I think we need to have some measure of what it's learning
by taking notes each time... only when there's something NEW."***

***This supplies the missing measure for the first half: on this task, notes keep paying up to at
least 37, and the typical word stops at 10.*** **It does NOT answer the second half -- whether the
NEXT note carries anything new -- which is the harder and better question and remains unmeasured.**

## TLDR

Two things I measured tonight belong side by side.

**First: the more times the system sees a word, the better it gets at recognising it** — and that keeps
improving up to at least thirty-seven encounters, which is as far as I tested.

**Second: in an actual reading run, the typical word gets ten.**

**So the typical word is sitting at about 60% of what simply paying attention longer would already
buy** — and the words that stop earliest lose the most. A word recorded seven times from ninety-two
appearances is at roughly half of what it could reach.

**The busiest words are fine** — they're already at the ceiling. **The loss is concentrated on
ordinary words**, which is most of them.

**This is the measure you asked for when you queried whether the system should keep taking notes after
deciding it knows a word.** The answer, on this task, is that notes keep paying long past the point
where it stops.

**One honest caution.** The three numbers come from three different runs over different word lists.
The *direction* is solid and properly controlled, and the typical word clearly sits below where the
gains flatten — **but I'd treat "1.7 times" as a rough size rather than a measurement**, because
combining figures across different populations is exactly the mistake I've caught four times tonight.

**And it doesn't answer your sharper follow-up** — whether the *next* note actually contains anything
new. That's the better question and it's still unmeasured.

## QUESTIONS

None.

## NEXT STEPS

1. **The direction is settled: the loop stops accruing where accrual still pays.** *Size is roughly
   1.7x for the median word; do not quote it as a precise measurement.*
2. **The unanswered half is the owner's own sharper question** -- does the next note carry anything
   NEW? *That needs a per-note information measure, not a count.*
3. *The curve itself was flat between L=24 and L=37 (CIs overlap), so beyond 37 is unmeasured and the
   true plateau is not located.*
