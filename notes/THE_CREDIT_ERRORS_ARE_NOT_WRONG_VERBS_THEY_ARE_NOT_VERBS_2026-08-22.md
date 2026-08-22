# **THE CREDIT-ASSIGNMENT ERRORS ARE NOT WRONG VERBS AND NOT WRONG ROLES. `73%` OF THEM ARE NOT VERBS AT ALL -- MANGLED STEMS AND NOUNS. NO ROLE SYSTEM FIXES THAT.**

**I asked whether the errors were wrong-role or wrong-verb. The answer is neither, and it is upstream of
both.**

---

## 1. THE MEASUREMENT

*The sharpened-credit cell SAVED ITS POPULATION -- `attribution_precision_*` carries the actual lemma
lists. Classified against WordNet:*

| | `loaded_lemmas` **(correctly credited)** | `light_lemmas` **(the errors)** |
|---|---|---|
| **not a word at all** | **`0 / 113` (0%)** | 🔻 **`90 / 173` (52%)** |
| **noun, no verb sense** | **`0 / 113` (0%)** | 🔻 **`37 / 173` (21%)** |
| has a verb sense | ✅ **`113 / 113` (100%)** | `46 / 173` (27%) |

**NON-WORDS:** `admir, alway, anyth, asham, babi, behav, cal, capaciou, caus, confid, continu`
**NOUNS:** `ad, amusement, boy, chang, explanation, fr, friend, guest, heart, lesson, lover`

> ### ✅ **AND THE CORRECTLY-CREDITED SET IS `100%` REAL VERBS -- A CLEAN INTERNAL CONTROL. IF MY WORDNET CHECK WERE THE BROKEN THING, IT WOULD SHOW GARBAGE ON BOTH SIDES. IT SHOWS IT ON EXACTLY ONE.**

## 2. 🔑 **SO THE DOMINANT ERROR IS A MORPHOLOGY DEFECT, NOT A SEMANTIC ONE**

***`_is_verblike` is a "Section 7 morphological heuristic". It is admitting broken stems and plain
nouns, and those get credited with the window's consequence.***

**A role system -- frame-based or otherwise -- assigns roles to VERBS. It has nothing to say about
`capaciou` or `boy`.** *So the prescribed situation-model upgrade, which I scoped last turn as "a real
upgrade on the role half", **would not touch roughly three quarters of the error types**.*

## 3. 🔻 **AND SHARPENING DID NOT CHANGE THE MIX**

| | non-words | nouns | verbs |
|---|---|---|---|
| OLD | **52%** | 21% | 27% |
| NEW *(clause-anchored + selectionally weighted)* | **47%** | 21% | 32% |

***It cut volume threefold (`958 -> 338` exposures) and left the ERROR COMPOSITION essentially
intact.*** **That is why precision moved only `0.4676 -> 0.4941`: the sharpening was aimed at which
clause a verb sits in, while most of the errors were never verbs.**

## 4. ⚠️ **THE LIMIT THAT BOUNDS THE HEADLINE -- TYPES vs TOKENS**

***The `52 / 21 / 27` split is over LEMMA TYPES. The precision `0.4676` is over EXPOSURES (`958`).***
**I cannot convert one into the other without per-lemma exposure counts, which are not saved.**

**SO: "73% of the error TYPES are not verbs" is measured. "73% of the erroneous CREDIT is not verbs" is
NOT** -- *a few real light verbs could dominate the token count.* ⚠️ **I will not project a repaired
precision from these proportions, and any number that did would be mixing types and tokens.**

## 5. ⚠️ OTHER LIMITS

1. **WordNet is the arbiter of "is a word".** *A rare-but-real verb absent from WordNet counts as
   garbage here; the non-word list is visibly stemmer output, so this is unlikely to explain 52%.*
2. **READ from `metrics.json`, not reproduced.**
3. **Nothing is fixed.** *This locates the defect and does not repair it.*

## TLDR

I asked whether the system attaches consequences to the wrong verb, or gets the roles wrong. **It is
neither. About three quarters of the mistakes are not verbs at all.**

The list of things being wrongly credited reads: `admir`, `alway`, `asham`, `babi`, `behav`,
`capaciou` — **broken word-fragments from a crude stemmer** — and `boy`, `friend`, `amusement`,
`explanation` — **ordinary nouns**. Meanwhile every single correctly-credited item is a genuine verb,
which tells me my own check is sound: if it were broken, both lists would look like rubbish.

**This matters for what I recommended last turn.** I scoped the prescribed build as a real improvement
because it assigns roles by grammar rather than word order. **But a role system only has opinions about
verbs.** It has nothing to say about `capaciou`. So it would leave most of these mistakes untouched.

**It also explains why the earlier fix barely moved.** Sharpening which clause a verb belongs to cut the
volume by two thirds and left the *mixture* of mistakes unchanged — because the mistakes were never
about clauses.

**One thing I am deliberately not claiming:** I counted distinct words, not occurrences. A handful of
common wrong verbs could still account for most of the actual mis-credits, and the data to check that
was not saved. So I am not putting a number on how much a repair would gain.

## QUESTIONS

None.

## NEXT STEPS

1. ⭐ **THE CHEAPEST HIGH-VALUE FIX IN THIS THREAD IS NOW A MORPHOLOGY GATE, NOT A ROLE SYSTEM** *--
   reject candidates with no WordNet verb sense before crediting them.* ⚠️ *Must be tested, not assumed:
   it would also reject rare real verbs, and the type/token caveat means the gain is unquantified.*
2. **Re-scope the prescribed build honestly** *-- it remains a real role upgrade, but it is not the
   dominant error and I should stop implying it would fix this.*
3. *Method note: **the cell saved its population, and that is the only reason this was answerable from
   disk.** Four turns ago I recorded a cell that did NOT save its population as costing exactly this
   kind of re-analysis.*
