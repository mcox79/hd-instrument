# **THE OPEN-VOCABULARY COST IS THREE WORDS -- `arm`, `hand`, `leg` -- WHERE THE REAL LOOKUP GIVES THE *MORE CORRECT* ANSWER AND SCORES *WORSE*. AND THAT DIRECTLY INDICTS THE FIX I PROPOSED AN HOUR AGO.**

> # 🔻 **RETRACTED THE SAME NIGHT. `arm` SCORES CORRECTLY -- `he broke her arm` RETURNS `BLOCK_HIGH`, THE GOLD ANSWER.**
> **THE FAULT: I compared `v2.lookup_animacy` against the real lookup, and THE CLOSED ARM DOES NOT CONSUME `lookup_animacy`** -- it consumes `object_event_class` (`GOAL_OBJECT`/`ADVERSARIAL`/`ANIMATE_HARMABLE`), a different type system. *The real causes are a `gclass_narrow == "UNK"` guard that switches the harm route OFF for `beat`/`attack`, and animacy being unable to express `ADVERSARIAL` so `enemy` reads `abstract`.*
> `I_RETRACT_THE_THREE_WORD_FINDING_...`

**I was about to ship a change that would plausibly regress the very subsets I was trying to improve.**

---

## 1. THE WHOLE COST IS THREE WORDS

*Closed lexicon (`v2.lookup_animacy` -- the arm scoring `1.000`) vs the REAL lookup (the arm scoring
`0.833`/`0.750`), on every word in each subset.* ✅ **Positive control: both agree on
`woman`/`dog`/`rock`/`table`.**

| subset | n words | disagreements |
|---|---|---|
| **B** | 11 | **1** -- `arm` |
| **Bgen** | 7 | **2** -- `hand`, `leg` |
| Bopen | 12 | 0 |
| Bgap | 6 | 0 |

| word | **CLOSED** *(scores 1.000)* | **REAL** *(scores worse)* |
|---|---|---|
| `arm`, `hand`, `leg` | `inanimate` / `object` | `animate` / `body_part` |

## 2. 🔑 **AND THE ITEMS SHOW THE REAL LOOKUP IS THE ONE THAT IS RIGHT**

```
"he broke  her arm"   -> gold HARM
"he crushed her leg"  -> gold HARM
"he smashed her hand" -> gold HARM
```

***Possessive, unambiguous, genuine body-part harm. `her arm` IS an animate body part. The CLOSED
lexicon calls it an inanimate object -- and the closed lexicon is the arm that scores `1.000`.***

> # 🔻 **THE MORE CORRECT LEXICAL JUDGEMENT MAKES THE PIPELINE WORSE. THE DOWNSTREAM LOGIC IS CALIBRATED ON THE COARSER, WRONGER READING.**

**An INTEGRATION defect, not a coverage hole.** *Improving a component's accuracy degraded the system,
which is the clearest sign that its consumer was fitted to the component's error.*

## 3. 🔻 **THE PART THAT MATTERS MOST: THIS INDICTS MY OWN PROPOSED FIX**

*An hour ago I proposed, demonstrated and recorded a "principled replacement for the body-part
whitelist": WordNet's `body_part` hypernym at the top sense returning **`animate` / `body_part`** for
all body parts. I showed it changes exactly `ankle`/`elbow`/`knee` and touches no control.*

***`animate`/`body_part` IS THE EXACT VALUE CURRENTLY COSTING ACCURACY ON `arm`, `hand`, `leg`.***
**My fix makes MORE words take the value that already loses points -- plausibly repairing `Bgap` while
REGRESSING `B` and `Bgen`, the subsets I was trying to protect.**

⚠️ **AND MY COMPONENT DEMONSTRATION COULD NOT HAVE CAUGHT IT.** *It compared the lookup against itself
-- "changes exactly 3 words, touches no control" -- which is true and useless here, because the damage
is downstream of a value the lookup already returned for other words.* **A component test that never
asks what the CONSUMER does with the value cannot see a consumer calibrated on the old error.**

## 4. ⚠️ WHAT IS AND IS NOT ESTABLISHED

| | |
|---|---|
| the 3 disagreeing words are `arm`, `hand`, `leg` | ✅ **measured**, positive-controlled |
| the closed lexicon calls them inanimate objects | ✅ **measured** |
| **`Bgen`'s errors are EXACTLY accounted for** | ✅ *2 disagreeing words; 8 items at `0.750` = 2 wrong* |
| 🔻 **`B`'s are NOT** | *12 items at `0.833` = **2** wrong, but only **1** disagreeing word. **One error has another cause I have not found.*** |
| that the disagreement CAUSES the errors | 🔻 **NOT PROVEN** *-- I have not run the arms with the value swapped. Strong association, plausible mechanism, correlational evidence.* |
| that my fix would regress B/Bgen | 🔻 **NOT PROVEN -- but the burden is now on the fix.** |

## TLDR

I traced why the system does worse on realistic vocabulary. **It comes down to three words: arm, hand
and leg.**

The test sentences are *"he broke her arm"*, *"he crushed her leg"*, *"he smashed her hand"* — plainly
about hurting a person. **The version that scores perfectly treats an arm as an inanimate object, which
is wrong. The version that correctly calls it part of a living body scores worse.**

**Making the component more accurate made the system less accurate**, which almost always means the
rest of the pipeline had quietly been built around the original mistake.

**And this lands squarely on the fix I proposed an hour ago.** I wanted the dictionary to label body
parts as "part of a living thing" — precisely the label currently losing points on these three words.
**My change would have repaired one small group and broken a larger one.**

**My own test could not have caught it.** I checked that the change touched only the words I intended —
true, and beside the point. The harm happens further down, in code that had adapted to the old answer.
**Checking a part in isolation cannot reveal that something else was relying on it being wrong.**

**I am not claiming this is proven.** I have not re-run with the values swapped, and one error still has
no explanation. But the burden has moved onto my proposal, and it should not ship on what I had.

## QUESTIONS

None.

## NEXT STEPS

1. 🔻 **DO NOT SHIP THE BODY-PART FIX ON THE EVIDENCE I HAD.** *It must now be tested on B and Bgen, not
   only on Bgap.*
2. **Find the second `B` error** *-- unexplained by any lookup disagreement.*
3. ⭐ **The bigger question: WHICH OTHER DOWNSTREAM LOGIC IS CALIBRATED ON A COMPONENT'S ERRORS?** *This
   surfaced only because a more accurate input made things worse.*
4. *Method note: **the component test and the consumer disagreed, and I trusted the component test.**
   "Changes exactly what I intended" is not evidence of improvement.*
