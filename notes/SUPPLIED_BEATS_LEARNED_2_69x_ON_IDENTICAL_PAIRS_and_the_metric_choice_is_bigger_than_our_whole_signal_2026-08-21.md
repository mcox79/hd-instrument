# **HANDED-OVER HUMAN RATINGS SCORE `0.2876` WHERE WHAT WE LEARNED SCORES `0.1071` -- `2.69x`, ON THE SAME 829 PAIRS WITH ONE SCORER. AND CHOOSING THE METRIC MOVES THE SUPPLIED ARM BY MORE THAN OUR ENTIRE LEARNED SIGNAL.**

> # 🚫 **FRAMING IS FIXED BY THE ORGAN'S OWN DOCSTRING AND I AM NOT FREE TO IMPROVE ON IT:**
> *"The Lancaster norms are HUMAN RATINGS... the substrate does not GROW this spoke, it is handed
> one. **That is SUPPLY, not learning, and no result from this organ may be reported as the substrate
> having learned perceptual structure.**"*
> **So this is a reason to USE the asset. It is NOT evidence that anything understands anything.**

---

## 1. WHY THIS NEEDED MEASURING AT ALL -- THE `2.7x` HAD NEVER BEEN MEASURED

**The archive records the norms at `rho 0.2701` and our live encoding at `0.1048`.** *Those are
**different cells on different pair sets**, and this project's standing bar says **no number crosses
populations or scorers**.* **So the ~2.7x gap everyone quotes was an INFERENCE from two numbers that
were never entitled to sit beside each other.** *This scores both at once, on the same pairs.*

## 2. THE RESULT

*829 SimLex pairs covered by BOTH the corpus and the norms -- the norms cost nothing in coverage
here, since SimLex vocabulary is common words. Null = 200 shuffles per arm.*

| arm | rho vs human | null p95 |
|---|---|---|
| **LEARNED** masked context `d=256` | 0.0944 | 0.0650 |
| **LEARNED** masked context `d=1024` | 0.1071 | 0.0631 |
| **SUPPLIED** norms12, cosine | 0.2176 | 0.0762 |
| **SUPPLIED** norms12, **euclid** | **0.2876** | 0.0729 |

> ### **`2.69x`. AND THE INFERRED FIGURE SURVIVES ITS FIRST HONEST TEST -- the archive's 2.7x was right, for the first time for the right reason.**

## 3. 🎯 **THE METRIC CHOICE IS WORTH MORE THAN EVERYTHING WE LEARNED**

**Euclid `0.2876` vs cosine `0.2176` = `+0.0700`.** *Our entire learned arm clears its own null by
`0.1071 - 0.0631 = 0.0440`.*

> ### **PICKING THE RIGHT DISTANCE ON A HANDED-OVER TABLE IS WORTH 1.6x OUR WHOLE LEARNED SIGNAL.**

**And I only swept because the organ's docstring told me to.** *It records that euclid separates
synonyms from siblings by `1.348` pooled SDs against cosine's `0.511`, that cosine wins on
concrete-versus-abstract by `22.8` to `3.2`, and that **the self-test which first asserted one was
better FAILED.** SimLex is dense in near pairs, which is exactly where euclid is documented to win --
so this result is a RETRODICTION of the organ's own stated mechanism, not a surprise.*

## 4. ⚠️ WHAT THIS DOES NOT SAY

1. **NOT that we learned anything.** *Fixed by the docstring above; the asset was handed over.*
2. **NOT that the learned arm is worthless** -- `0.1071` clears its null `0.0631`. *It is weak, not
   absent.*
3. **NOT a route to a better learner.** *Using a better supplied table does not make the reading loop
   better at reading; it changes what the loop is compared against.*
4. **NOT new coverage.** *The organ's own caveat stands: 60.4% token coverage overall. It cost
   nothing on THIS vocabulary and will cost on a general one.*

## TLDR

We have two sources of word meaning: **what the system worked out by reading, and a table of human
ratings we were given.** Everyone quotes the given table as about 2.7 times better — **but that
comparison had never actually been run.** The two numbers came from separate experiments on separate
word lists, which our own rules say cannot be compared.

**Run properly, on the same 829 word pairs at the same time: the given table scores 0.29 and our
learned version scores 0.11.** So 2.7 times was right, and now for a defensible reason.

**The part I did not expect:** simply choosing a better way to measure distance within that given
table is worth more than everything our system learned from reading. **Changing the distance measure
gains 0.07; our entire learned signal is worth 0.04 above chance.**

I only tested both because the component's own notes said to — and said that the first attempt to
declare a winner between them had failed.

**What this is not:** it is not evidence our system understands anything. The good numbers come from
a table of human judgements we were handed, and the component's own documentation forbids reporting
that as learning. **It is a reason to use the table well, not a claim about the substrate.**

## QUESTIONS

None.

## NEXT STEPS

1. **Quote the supplied/learned gap as `0.2876` vs `0.1071` on 829 shared pairs** -- not as the
   archive's two-cell inference.
2. **The live path should use EUCLID on the norms, not cosine, on near-pair work** -- *worth `+0.0700`
   here, and the plan separately records that the live scalar is crippled to two values by
   `GROUNDED_CAP=0.45` while the winning arm used RAW vectors.*
3. *Method note: **the metric sweep came from `tools/symbol_corrections.py` surfacing the organ's own
   docstring before I wrote a line.** Without it I would have picked cosine, the obvious default, and
   reported a number `0.07` too low.*
