# **I TOLD THE OWNER WE HAD READ NINE BOOKS. WE HAVE TWENTY-EIGHT SOURCES AND 286,069 SENTENCES. A 60,000-SENTENCE CAP TAKEN IN ALPHABETICAL ORDER PRODUCED THE WHOLE CLAIM, AND I WITHDREW THE BOARD QUESTION WITHIN THE HOUR.**

**The correction runs AGAINST my own earlier conclusion in one place and FOR it in another. Both
directions are below.**

---

## 1. THE DEFECT, IN ONE LINE

*My loader filled a 60,000-sentence quota in `readable_names()` order and stopped.*

**That took the first NINE corpora ALPHABETICALLY** -- `alice_in_wonderland, anne_of_green_gables,
arc, breadth_v1, graded_readers_grade1, graded_readers_graded, litbank_coref_conll, little_women,
mcguffey_graded` -- **almost entirely novels and school readers.** *It silently excluded **all six
textbooks** (anatomy, biology, microbiology, psychology, chemistry, concepts-biology), `simplewiki`,
`onestop`, `race`, `wiqa`, `social_iqa` and `worldtree`.*

> ### **A CAP IS A SAMPLING DECISION. TAKING IT IN NAME ORDER IS A BIAS, AND NOTHING IN THE SCRIPT OR ITS OUTPUT SAID SO.**

## 2. WHAT THE SHELF ACTUALLY IS

| | I said | **actual** |
|---|---|---|
| readable corpora | 9 | **28** |
| usable sentences | 60,000 | **286,069** |
| lemmas with >=41 sentences | 3,030 | **7,568** |
| median largest-single-corpus share | 0.695 | **0.488** |
| lemmas >=90% in ONE corpus | ~30% | **12.6%** |
| SimLex pairs BOTH words balanced | **40** | **111** |
| SimLex pairs both covered | 533 | **829** |

## 3. 🔻 **AND IT REVERSES ONE OF MY OWN CONCLUSIONS -- IN THE DIRECTION OF UNDER-CLAIMING**

*Re-run round-robin across all 28, everything else byte-identical:*

| | 9 corpora, alphabetical | **28, round-robin** |
|---|---|---|
| **RANDOM sample: MASKED - CORPUS_ONLY** | **+0.0220, CI `[-0.0419,+0.0764]` -- NOT separated** | **+0.1163, CI `[+0.0520,+0.1760]` -- SEPARATED** |
| RANDOM: MASKED / CORPUS-ONLY | 0.0972 / 0.0752 | **0.2809 / 0.1646** |
| BALANCED: MASKED | 0.1549 | **0.1435** |
| BALANCED: CORPUS-ONLY floor | 0.0179 | **0.0000** |
| BALANCED: median largest-corpus share | 0.268 | **0.098** |
| SCRAMBLE floor | 0.0179 | **0.0167** *(= chance exactly)* |

***I PUBLISHED "NOT SEPARATED FROM SOURCE-TEXT IDENTITY" FOR TYPICAL WORDS. ON A PROPERLY SAMPLED
SHELF IT IS SEPARATED.*** **My biased sample made me UNDER-claim, which is the less common direction
and no better.**

✅ **AND THE BALANCED RESULT IS UNCHANGED IN SUBSTANCE, WITH A NOW-PERFECT CONTROL:** with words
spread over 28 sources, a predictor knowing only the source scores **exactly `0.0000`**, and the
scramble floor lands on chance to four decimals.

## 4. WHAT IT COST, AND WHAT I DID ABOUT IT

**I filed board Q103 asking the owner to consider a broader reading list, on the strength of "nine
books" and "only 40 usable pairs". BOTH NUMBERS WERE MINE, NOT THE PROJECT'S.** *I withdrew it
within the hour, from disk, before it was answered -- a question resting on a wrong number is worse
than no question.*

**THE FIX IS IN THE CODE, NOT THIS NOTE:** both diagnostics now sample **ROUND-ROBIN across every
readable corpus** and print `shelf: N corpora, M sentences sampled ROUND-ROBIN` as their first line,
so the sampling is visible in every future run rather than assumed.

## TLDR

I told you our reading material was nine books and that this was blocking us from testing whether the
system understands meaning. **That was wrong, and it was my own error.**

My script grabbed the first sixty thousand sentences it found, **taking sources in alphabetical
order** — which handed it Alice in Wonderland, Anne of Green Gables and a pile of school readers, and
quietly skipped all six textbooks, Wikipedia, the news reader and everything else. **We have
twenty-eight sources and nearly three hundred thousand usable sentences.**

**I had already asked you to consider changing the reading list on the strength of that mistake. I
withdrew the question within the hour, before you saw it.**

**Re-running properly changes one of my conclusions, and not in the flattering direction — it
reverses a negative I published.** I had said that for ordinary words, our system couldn't be told
apart from a cheat that only knows which book a sentence came from. **On a proper sample it clearly
can be.** I had understated our own result because of my bad sample.

**The main positive from earlier survives and its control is now perfect:** when words are spread
across all twenty-eight sources, the "which book" cheat scores exactly zero, and our system still
works.

**The fix is in the code rather than in this note** — both tools now spread their sampling across
every source and announce what they sampled, every run.

## QUESTIONS

None. *Q103 is withdrawn; Q102 is unaffected and still open.*

## NEXT STEPS

1. **Re-read any tonight number that came from the 60k slice** -- the three affected notes now carry
   correction banners with the round-robin figures beside the old ones.
2. **`CORPUS-ONLY 0.1646` on the full-shelf RANDOM sample is still substantial** -- source identity
   remains a real confound for typical words even across 28 sources, so the floor stays mandatory.
3. *Method note: **the tell was noticing that `readable_names()` returned 28 while my own output
   named 9.** Two numbers from the same object, side by side, one line apart.*
