# **COUNTING NEGATION WORDS IN THE FINAL SENTENCE SCORES `0.8056`. THE FOUR-TIER STRUCTURAL CASCADE SCORES `0.4722`. THIS IS A NEW FLOOR, NOT A PROPOSAL.**

**The measurement bar says a gate is a margin over the strongest floor ACTUALLY RUN. Nobody had run this
one. The whole line has been measuring itself against `0.6389` when a one-line regex reaches `0.8056`.**

---

## 1. WHERE THE IDEA CAME FROM -- THE STRUCTURE OF THE EVIDENCE, NOT A GUESS

*Established over the previous notes: the ONE branch that beats its base rate (`same_class_same_referent`,
`7/9` = `77.8%`) is the only one requiring **POSITIVE EVIDENCE** -- the goal action happened, to the goal
person. **Every branch that fires on ABSENCE** -- `referent_mismatch` (could not bind), `opposed_class`
(different verb class) -- **runs at `4/11` = `36.4%`, worse than silence.***

➡️ **So: does POSITIVE evidence for a NEGATIVE outcome exist in the text at all?** *If a reader knows the
wish failed, something in the passage must say so.*

## 2. ✅ IT DOES, AND IT IS SHARPLY LOCALISED

| window | accuracy | permutation null p95 | | MET / UNMET mean cues |
|---|---|---|---|---|
| **final sentence** | ✅ **`0.8056`** | `0.6944` | **CLEARS** | **`0.04` / `0.69`** |
| last 2 sentences | ✅ `0.7778` | `0.6944` | **CLEARS** | `0.13` / `0.85` |
| last 3 | `0.6944` | `0.6944` | inside null | `0.26` / `0.85` |
| last 4 | `0.7222` | `0.7222` | inside null | `0.48` / `1.00` |
| whole passage | `0.7222` | `0.7222` | inside null | `0.65` / `1.31` |

**The decay is MONOTONE in window size**, which is what a genuinely localised signal looks like -- *the
negation has to be in the sentence that resolves the goal. A knife-edge fit would not degrade in order.*

> # **`0.8056` vs the majority floor `0.6389` vs the four-tier cascade `0.4722`.**

**The rule is: `no|not|never|n't|cannot|refuse|fail|won't|can't|hasn't|...` -- count them in the last
sentence; one or more means the goal failed.**

## 3. 🚫 **THIS IS NOT A FIX AND MUST NOT BE SHIPPED AS ONE**

**It is a LEXICAL CUE DETECTOR. It does not read, model a goal, or track a referent.** *It is the same
"word-counting beats the substrate" pattern this project has hit repeatedly -- and the standing
discipline is that such a result RAISES THE BAR rather than becoming the mechanism.*

| what it establishes | what it does not |
|---|---|
| ✅ positive evidence for `UNMET` **is present** in the text | 🚫 that counting it is comprehension |
| ✅ it is **localised in the resolving sentence** | 🚫 that it generalises past 36 items |
| ✅ **the cascade is not merely below the majority floor -- it is `0.33` below a one-line regex** | 🚫 that the cascade should be replaced by it |

> ## **THE POINT IS THE GAP: A MECHANISM THAT MODELS GOALS, REFERENTS AND VERB CLASSES IS BEATEN BY `re.findall` ON THE LAST SENTENCE. THAT IS THE MEASUREMENT THE LINE HAS BEEN MISSING.**

## 4. ⚠️ LIMITS -- **AND ONE OF THEM IS A REAL WEAKNESS IN THIS TEST**

1. 🔻 **THE NULL COVERS THRESHOLD SELECTION BUT NOT FEATURE OR WINDOW SELECTION.** *Best-`t` is
   recomputed inside every permutation, so that part is honest. **But I chose "negation cues" and "final
   sentence" AFTER reading the failing passages**, where I had seen `"No," she said coldly`,
   `"hasn't relented"`, `"I shall never have courage"`. **That is selection on the test set and the null
   does not price it.*** *The monotone decay is reassuring but is not a substitute for a held-out bank.*
2. **n=36, 13 of them UNMET.** The whole separation rests on 13 items.
3. **Negation is not the same as failure.** *`"I never was whipped in school"` appears in a gold-MET
   item; the cue will misfire on negated non-outcomes, and at this n I cannot characterise that.*
4. **This says nothing about the OTHER direction** -- it does not detect goal SATISFACTION, which is what
   the working `MET` branch already does at `77.8%`.

## TLDR

The system decides whether a character's wish came true. It gets 47 out of 100. Simply always answering
"yes it came true" gets 64.

**I tried counting negative words — "no", "not", "never", "failed" — in the last sentence of each story.
That gets 81 out of 100.**

A single line of pattern-matching, with no understanding of the story, no idea who anyone is and no model
of what anyone wanted, **beats the purpose-built four-part reasoning machine by more than thirty points.**

**This is not something to ship.** It doesn't understand anything; it would be fooled by any negative
sentence that isn't about the outcome, and one of our own test stories contains exactly that trap. **The
value is that it sets a bar.** The project's rule is that a result only counts if it beats the best
simple trick anyone has actually tried — and nobody had tried this one. So every past comparison on this
task has been against too low a bar.

**It also confirms the thing worth knowing:** the evidence for "the wish failed" *is* sitting in the
text, in the final sentence, in plain words. **The machinery isn't missing information. It is failing to
use information that is right there.**

**One honest weakness:** I picked "negative words" and "last sentence" after reading the stories the
system got wrong, where I'd noticed exactly those words. My statistics correct for picking the best
cut-off, but not for picking the feature. On a fresh set of stories this number would probably be lower.

## QUESTIONS

None.

## NEXT STEPS

1. 🎯 **Add this as a standing FLOOR for the line** *-- alongside majority and scramble. Any future
   consequence-learning result must clear `0.8056`, not `0.6389`.* **Every verdict on this line was
   graded against a floor that was too low.**
2. **The honest version needs a held-out bank** *-- which is the same `n=36` constraint that has bound
   every question this week. This is now the third independent reason to enlarge it.*
3. 🚫 **Do not replace the cascade with the regex.** *Record it as a floor and let it do the job floors
   do: make weak mechanisms visibly weak.*
