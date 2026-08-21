# **REMOVE THE BOOK CONFOUND AND THE MASKED CONTEXT VECTOR DOES CARRY WORD-SPECIFIC SIGNAL: 0.1549 AGAINST A STRONGEST-FLOOR 0.0179, CI-SEPARATED. A POSITIVE, PROPERLY FLOORED.**

**The re-run my own previous note asked for and left undone. It resolves a question that was
UNRESOLVED rather than negative.**

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

## 1. THE TWO POPULATIONS SIDE BY SIDE

*Identical code, identical arms, identical scorer. The ONLY difference is which 60 lemmas.*

| | RANDOM sample | **SOURCE-BALANCED sample** |
|---|---|---|
| median largest-single-corpus share | 0.695 | **0.268** |
| lemmas >=90% from ONE corpus | 18 of 60 | **0 of 60** |
| chance | 0.0167 | 0.0167 |
| **SCRAMBLE floor** | -- | **0.0179** |
| **CORPUS-ONLY floor** | **0.0752** | **0.0179** |
| **MASKED (the real arm)** | 0.0972 | **0.1549** |
| MASKED - CORPUS_ONLY | +0.0220 | **+0.1370** |
| 95% CI | `[-0.0419, +0.0764]` | **`[+0.1085, +0.1626]`** |
| CI half-width | 0.0592 | **0.0270** |
| **separated?** | 🚫 **NO** | ✅ **YES** |
| lemmas favouring MASKED | 45 of 60 | **54 of 60** |

> ### ✅ **THE MANIPULATION WORKED, AND ITS OWN CONTROL PROVES IT: removing the confound drops the CORPUS-ONLY floor from `0.0752` to `0.0179` -- onto chance. A predictor knowing only the source text goes from useful to useless, which is exactly what it should do.**

## 2. **THE FLOOR THE RESULT IS ACTUALLY MEASURED AGAINST**

**Strongest floor ACTUALLY RUN = `max(chance 0.0167, SCRAMBLE 0.0179, CORPUS-ONLY 0.0179) = 0.0179`.**
**`MASKED = 0.1549` is `8.7x` that, with a CI excluding zero.**

**The SCRAMBLE arm is also the positive control on the harness**: each query keeps a REAL masked
vector but the word-to-context correspondence is destroyed, with dimensionality, profile sizes, tie
structure and the leave-one-out subtraction all untouched. **It lands at `0.0179`.** *An arm that
cannot produce a null cannot produce a result; this one can.*

## 3. ⚠️ **WHAT THIS IS NOT -- AND THE BIAS IS BY CONSTRUCTION, NOT AN ACCIDENT**

1. ***THE BALANCED SAMPLE IS THE 60 MOST SOURCE-SPREAD LEMMAS IN THE SHELF. THAT IS NOT THE AVERAGE
   WORD*** -- it is the subset appearing across many registers. **This answers "is there word signal
   once the confound is removed", NOT "how well does the arm do on our vocabulary".**
2. **THE TWO COLUMNS ARE DIFFERENT POPULATIONS.** *`0.0972 -> 0.1549` is NOT an improvement and must
   never be read as one.*
3. **`0.1549` IS STILL LOW IN ABSOLUTE TERMS** -- it picks the right word out of 60 about one time in
   six. **Separated from its floor is not the same as good.**
4. **This is an INTERNAL-REPRESENTATION question and is NOT scored against the standing task bar**
   (co-occurrence counting). *Nothing here says the substrate beats counting at anything.*

## TLDR

Earlier I found that our system's apparent ability to tell which word a sentence is about was mostly
explained by a cheat: **most words appear in only one of our books, so "which word" was largely
"which book".** That left the real question unanswered rather than answered — the test couldn't tell.

**So I re-ran it on words that appear evenly across many books**, where that cheat has nothing to
work with.

**The cheat collapses to guessing, exactly as it should** — a predictor knowing only the source book
drops from useful to useless. **And our system's own score goes up, to about one correct answer in
six out of sixty, which is roughly nine times the best cheat available and comfortably outside the
margin of error.**

**So the answer is yes: with the word deleted, what remains does carry real information about which
word it was.** That had been in genuine doubt.

**Three things I'm not claiming.** These are deliberately the most widely-read words, not typical
ones, so this shows the signal *exists* rather than how strong it is generally. The two runs are
different word sets, so the apparent rise from the earlier score is not an improvement. And one in
six is still weak — **beating the floor is not the same as being good.**

## QUESTIONS

None.

## NEXT STEPS

1. **The open item from the previous note is CLOSED.** *It asked for exactly this re-run.*
2. **Quote this as `0.1549 vs strongest-floor 0.0179, CI-separated, on a deliberately source-balanced
   sample`** -- never as a statement about the whole vocabulary.
3. *Method note: **the same measurement was uninterpretable and then decisive, and the only thing
   that changed was which items it ran on.** The confound was in the sample, not the mechanism.*
