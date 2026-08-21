# **A PREDICTOR THAT KNOWS ONLY WHICH BOOK A SENTENCE CAME FROM SCORES 0.0752. THE MASKED ARM SCORES 0.0972 AND DOES NOT SEPARATE FROM IT. "5.8x CHANCE" WAS THE WRONG FLOOR.**

**I measured `MASKED hit@1 = 0.0972` against chance `0.0167` an hour ago. Before anyone quotes that
as word-specific signal, this is the floor it should have been measured against.**

> **RUN CONFIGURATION, stated because it is part of the measurement: `GRADED_COMPARATOR=True` (the shipped default), `CTX_D=256`, `HD_GRADED_COMPARATOR` unset. *`context_vector_masked` takes `graded=None` meaning 'follow the module switch' (DEFAULT CHANGED 2026-08-14), so these numbers inherit it -- and a number from one switch state may not be compared with one from the other. Found by running `tools/symbol_corrections.py context_vector_masked` over my own night's citations.*

> # **CORRECTED THE SAME NIGHT -- THIS NOTE'S SAMPLE WAS 9 OF 28 CORPORA, TAKEN ALPHABETICALLY.**
> **My loader filled a 60,000-sentence quota in `readable_names()` order and stopped. That took
> `alice, anne, arc, breadth_v1, graded_readers*, litbank, little_women, mcguffey_graded` -- almost
> entirely NOVELS AND SCHOOL READERS -- and silently excluded ALL SIX TEXTBOOKS, `simplewiki`,
> `onestop`, `race`, `wiqa` and `social_iqa`. THE REAL SHELF IS 28 READABLE CORPORA, 286,069 usable
> sentences.** *A cap is a sampling decision, and taking it in name order is a bias.*
>
> **RE-RUN ROUND-ROBIN ACROSS ALL 28, everything else identical:**
>
> | | this note (9 corpora, alphabetical) | **CORRECTED (28, round-robin)** |
> |---|---|---|
> | median largest-corpus share, balanced arm | 0.268 | **0.098** |
> | CORPUS-ONLY floor, balanced | 0.0179 | **0.0000** |
> | MASKED, balanced | 0.1549 | **0.1435** |
> | **MASKED - CORPUS_ONLY, RANDOM sample** | **+0.0220, CI `[-0.0419,+0.0764]` NOT separated** | **+0.1163, CI `[+0.0520,+0.1760]` SEPARATED** |
> | MASKED / CORPUS-ONLY, RANDOM | 0.0972 / 0.0752 | **0.2809 / 0.1646** |
>
> ***THE CORRECTION RUNS AGAINST MY OWN EARLIER CONCLUSION: on a properly sampled shelf the masked
> arm SEPARATES from source-identity for TYPICAL words too, which this note reported as NOT
> separated. I under-claimed because of a biased sample.*** **The balanced result is unchanged in
> substance and its control is now perfect: with words spread over 28 sources, a predictor knowing
> only the source scores EXACTLY 0.0000.**
> `THE_SHELF_IS_28_CORPORA_NOT_9_...`

---

## 1. WHY THIS FLOOR AND NOT CHANCE

*The corpus mix spans Alice in Wonderland, ARC, Little Women, McGuffey readers and six more.* **A
lemma's sentences are NOT drawn uniformly from it:*

| largest-single-corpus share per lemma | |
|---|---|
| median | **0.695** |
| mean | 0.709 |
| lemmas drawn **>=90% from ONE corpus** | **18 of 60** |

***So "which word is this sentence about" is answerable in large part by "which book is this
sentence from".*** **That is topic and register, not word meaning** -- and this project withdrew a
foraging headline on exactly this fault the same day, a **7.6x register bias sitting under a 1.2x
effect.**

## 2. THE RESULT

| arm | hit@1 |
|---|---|
| chance | 0.0167 |
| **CORPUS-ONLY** -- knows ONLY the source text, nothing else | **0.0752** |
| **MASKED** -- the real arm | **0.0972** |

**`MASKED - CORPUS_ONLY = +0.0220`, 95% CI **`[-0.0419, +0.0764]`**, half-width `0.0592`,
bootstrapped over the 60 LEMMAS (the clustering unit -- queries inside a lemma share its sentences
and its source mix, so resampling queries would understate the width).**

> ### 🚫 **THE CI SPANS ZERO. THIS RUN CANNOT TELL THE MASKED ARM APART FROM KNOWING WHICH BOOK THE SENTENCE CAME FROM.**

*45 of 60 lemmas favour the masked arm, so the direction is not nothing -- but the per-lemma spread
is nearly three times the effect.*

## 3. 🔻 **AND THE TOOL I WROTE TO ENFORCE THIS RULE BROKE IT ON ITS FIRST RUN**

**Its concluding line read `masked > corpus_only` and printed *"so it carries something the source
tag does not"* -- while its OWN bootstrap, four lines above, printed `[-0.0419, +0.0764]`.**

> ### **READING A POINT ESTIMATE AS A FINDING WHILE THE INTERVAL SPANS ZERO IS THE EXACT ERROR "A WIDTH IS NOT AN EFFECT" EXISTS TO STOP -- AND I SHIPPED IT INSIDE THE CONTROL WRITTEN TO ENFORCE IT.**

**Fixed: the verdict is now gated on the CI, and the not-separated branch prints the floor's own
score so the reader cannot miss what the arm is competing with.**

## 4. WHAT THIS CHANGES

| | |
|---|---|
| *"MASKED 0.0972 vs chance 0.0167 = 5.8x"* | 🚫 **DO NOT QUOTE. Chance is the weakest available floor; the strongest one reaches 0.0752 and is not separable.** |
| *"the masked context vector carries weak word-specific signal"* | ⚠️ **UNSUPPORTED BY THIS RUN.** *Not refuted either -- 45 of 60 lean the right way. It is UNRESOLVED at this n.* |
| the two-jobs finding | ✅ **UNTOUCHED.** *It rests on the MASKED-vs-TARGET_ONLY contrast, and TARGET_ONLY at 0.9687 clears any of these floors by a mile.* |

## TLDR

An hour ago I measured how well our system recognises which word a sentence is about when the word
itself is hidden. It scored about six times better than guessing, **which sounds like it knows
something.**

**So I checked what a cheat would score.** I built a predictor that knows nothing except **which book
each sentence came from** — no words at all. **It scores almost as well.**

The reason is that our reading material is a pile of separate books, and most words show up mainly in
one of them. **Two-thirds of the words we tested draw most of their sentences from a single book, and
a third draw nearly all of them from one.** So "which word is this about" can be largely answered by
"which book is this from" — **which is about topic, not meaning.**

**Measured properly, our system's lead over that cheat is too small to call**, given how much it
varies from word to word. It leans the right way for 45 of 60 words, so this isn't proof it knows
nothing — **it means this test can't tell, and the six-times-better figure should not be repeated.**

**The part I'm least comfortable with:** the tool I wrote to enforce exactly this discipline
**announced a positive result on its first run**, reading the raw difference while its own
uncertainty range — printed four lines above — clearly included zero. I fixed it to check the range
before drawing any conclusion.

**None of this touches the main finding from earlier**, which rests on a gap so large that no floor
here comes close to it.

## QUESTIONS

None.

## NEXT STEPS

1. **Stop quoting `0.0972 vs chance`.** *Quote it against the source-text floor of `0.0752`, or not
   at all.*
2. **The right fix for the confound is a corpus-balanced lemma sample** -- select lemmas whose
   sentences are spread across sources. *That is a re-run, not a re-analysis, and it is not done.*
3. *Method note: **the floor took twenty minutes and changed the reading of a number I had published
   an hour earlier.** Chance is almost never the strongest floor available.*
