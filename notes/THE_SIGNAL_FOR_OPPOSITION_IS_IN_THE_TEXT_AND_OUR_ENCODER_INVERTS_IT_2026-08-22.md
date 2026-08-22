# **YES -- TEXT DOES SEPARATE OPPOSITES FROM SYNONYMS. "X AND/OR Y" FIRES `35x` MORE FOR ANTONYMS THAN FOR RANDOM PAIRS. AND OUR ENCODER CONVERTS THAT SIGNAL INTO ITS OPPOSITE.**

**This closes the fork opened an hour ago: the verb failure is NOT "reading cannot do it". The signal
is there, in our own corpus, and we destroy it by construction.**
*`tools/do_antonyms_cooccur_v3_random_control.py`.*

> **CONFIG:** *28 corpora, **286,069 sentences** (the FULL shelf, not the 41-per-word sample -- pair
> co-occurrence is rare and power was the whole risk), 801 of 827 SimVerb verbs covered, **SimVerb's
> own relation labels**, all arms **FREQUENCY-MATCHED to the antonym pairs' bins**.*

---

## 1. ⚠️ **THIS INSTRUMENT REFUSED TO REPORT TWICE BEFORE IT WORKED. BOTH REFUSALS WERE CORRECT.**

| version | what fired | the fault, which was mine |
|---|---|---|
| **v1** | positive control | **THE STATISTIC.** *PMI with a `0.5` smoothing floor manufactured high scores for rare pairs that never co-occur -- and **54% of the baseline never co-occurs**.* |
| **v2** | positive control | **THE CONTROL ITSELF.** *It demanded SimVerb's `NONE` pairs co-occur least. `NONE` means **no WordNet relation**, not topically unassociated -- `drive/park`, `cook/serve` have no lexical relation and co-occur constantly. **I was demanding something false.*** |
| **v3** | -- | **PASSES**, against the negative control that was missing all along: **RANDOM pairs** from the same vocabulary, gold pairs excluded. |

## 2. ✅ THE RESULT -- ALL ARMS FREQUENCY-MATCHED

| relation | n | %never co-occur | mean shared sentences | **cond. "X and/or Y"** |
|---|---|---|---|---|
| **ANTONYMS** | 105 | **13.3%** | **18.87** | **`0.0782`** |
| COHYPONYMS | 98 | 21.4% | 8.90 | `0.0356` |
| SYNONYMS | 105 | 19.0% | 12.38 | `0.0269` |
| NONE | 105 | 33.3% | 12.06 | `0.0221` |
| HYPER/HYPONYMS | 105 | 22.9% | 12.51 | `0.0068` |
| **RANDOM** *(negative control)* | 103 | **47.6%** | **8.64** | **`0.0022`** ✅ lowest |

> ### **ANTONYMS LEAD ON EVERY STATISTIC. THE COORDINATION FRAME IS `2.91x` SYNONYMS AND `34.82x` RANDOM.**

*`COND-COORD` is coordination hits **divided by** co-occurrences, so a frequent pair gets more chances
at the numerator AND the denominator. **It is not a frequency effect wearing a hat.***

## 3. 🎯 **THE MECHANISM, AS A CHAIN WHERE EVERY LINK IS MEASURED**

1. **Antonyms co-occur, and announce themselves in an explicit frame** -- `0.0782` vs `0.0022` random.
   *(this note)*
2. **Our encoder builds SECOND-ORDER profiles and DELETES the target word** (`context_vector_masked`).
   *So when `buy` and `sell` share a sentence, each one's context profile is enriched by the other's
   surroundings.* ***CO-OCCURRENCE IS CONVERTED INTO SIMILARITY.***
3. **Therefore antonyms should be our CLOSEST pairs -- and measured, they are:** `cos 0.2062`, above
   synonyms `0.1727` and above unrelated `0.1591`. *(measured tonight)*
4. **Therefore verb similarity cannot clear chance -- and measured, it is `0.0000`** on 2,651 pairs.

> # 🔑 **THE SIGNAL THAT MARKS TWO WORDS AS OPPOSITE IS THE SAME EVENT OUR ENCODER READS AS EVIDENCE THEY ARE ALIKE. NOT A MISSING FEATURE -- AN INVERTED ONE.**

## 4. 🧠 BRAIN NOTE, AND IT CUTS AGAINST A CONVENIENT READING

*`hdlab/lexical_similarity.py` cites Cox et al. 2024: ventral anterior temporal similarity tracks
**feature-norm overlap, NOT co-occurrence**.* **So co-occurrence is NOT the brain's similarity
signal -- and this result does not claim it is.** *The claim is narrower and survives that: **first-order
co-occurrence is a cheap, available, text-derived DETECTOR OF OPPOSITION**, a different job from
computing graded similarity.* ⚠️ *Whether the brain uses it for that job is UNPINNED here and I am not
asserting it.*

## 5. ⚠️ LIMITS -- **AND THE FIRST ONE MATTERS MOST**

1. 🔻 **IT DOES NOT UNIQUELY IDENTIFY ANTONYMS.** *COHYPONYMS sit second at `0.0356` -- "cats and dogs"
   fires the same frame. **Antonyms lead cohyponyms by only `2.20x`** against `2.91x` for synonyms and
   `34.82x` for random. **This detects "coordinated pair", and opposition is a SUBSET of that.***
2. **SPARSE: only `7.8%` of antonym co-occurrences are an explicit frame.** *High precision, low
   recall -- it would fire on a minority of pairs.*
3. **NOTHING HERE SHOWS THAT USING THIS SIGNAL FIXES ANYTHING.** *No arm was built. The claim is that
   the information EXISTS and is DISCARDED, not that exploiting it works.*
4. **n=105 antonym pairs**, verbs only, one corpus, one language.
5. **A pattern-matched frame** (`\ba\w*\s+(?:and|or)\s+b\w*\b`), not a parsed coordination.

## TLDR

An hour ago I confirmed that our system treats opposites as the *most similar* words there are, which
explains why it scores nothing on verbs. **The open question was whether that is fixable by reading at
all, or whether opposites are simply invisible in text.**

**They are not invisible.** Opposites give themselves away by appearing *together*: "buy and sell",
"rise and fall". Measured on our own reading material, with everything matched for how common the
words are, opposite pairs turn up in an explicit "X and Y" phrase **thirty-five times more often than
random pairs** and about **three times more often than synonyms**.

**And here is the uncomfortable part.** Our system reads two words appearing in the same sentence as
*evidence they mean the same thing* — because it learns a word from its surroundings, and two words in
one sentence share surroundings. **So the exact event that marks a pair as opposite is the event we
count as proof they are alike.** It is not a missing ingredient; it is one we have pointed backwards.

**Two honest limits.** The signal says "these two words get mentioned together", which also covers
things like *cats and dogs* — so it flags opposites without being specific to them. And it only fires
on a small share of cases: reliable when it speaks, quiet most of the time.

**And I should say how this was measured, because the instrument refused to report twice before it
worked.** The first attempt used a broken statistic. The second used a broken *check* — I had demanded
that unrelated word pairs co-occur least, but the benchmark's "unrelated" only means no dictionary
relationship, and pairs like *drive* and *park* have none while appearing together constantly. Both
refusals were the safety catch doing its job on my own mistakes.

## QUESTIONS

None.

## NEXT STEPS

1. **The buildable move is now specific: a co-occurrence-aware term that SUBTRACTS rather than adds.**
   *Two words sharing a sentence should count AGAINST identity, not for it. That is one arm and it is
   testable against the verb `0.0000`.* ⚠️ *It would need to beat `counting+idf 0.0689`, not a shuffle.*
2. **Sharpen the detector against cohyponyms** *(limit 1)* -- *the frame alone does not separate
   `buy/sell` from `cats/dogs`, and a fix that treats both as opposed would be worse than nothing.*
3. *Method note: **the two refusals cost two runs and saved a false result twice.** The v2 lesson is
   the transferable one -- **a control can encode an assumption that is simply untrue**, and mine did.*
